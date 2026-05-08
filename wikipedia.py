from Scrapenator import Client
import urllib.parse

from time import sleep
from random import random

def get_surrounding_button(text: str, idx: int):
    idx_l = text[:idx].rfind("<a")
    spliced = text[idx_l:]
    idx_r = spliced.find("</a>")
    
    button_text = spliced[:idx_r]

    button_name = button_text[button_text.find(">")+1:]
    
    button_href = button_text[button_text.find("href=\"") + len("href=\""):]
    button_href = button_href[:button_href.find('"')]

    return button_name, button_href

def get_name_by_href(href):
    text = href[len("/wiki/"):]
    return urllib.parse.unquote(text, encoding="ascii", errors="ignore").replace("_", " ")

def get_wiki_lists(client: Client):
    html_data = bytes.decode(client.get('/wiki/Wikipedia:Contents/Lists'), encoding="ascii", errors="ignore")

    lists = [
        ("Wikipedia:Contents/Lists", "https://en.wikipedia.org/wiki/Wikipedia:Contents/Lists")
    ]

    html_data = html_data[html_data.find('<div class="contentsPage__heading" id="General_reference">'):]

    while True:
        idx_plural = html_data.find("Lists_of")
        idx_base = html_data.find("List_of")
        idx = -1
        if idx_plural == -1 or idx_base < idx_plural and idx_base != -1:
            idx = idx_base
        if idx_base == -1 or idx_plural < idx_base and idx_plural != -1:
            idx = idx_plural

        if idx == -1:
            break

        bttn_text, bttn_href = get_surrounding_button(html_data, idx)
        bttn_href = "https:" + bttn_href
        html_data = html_data[idx + len(bttn_text):]

        lists.append((get_name_by_href(bttn_href), bttn_href))

    return lists

def get_wiki_links(client, urlhref):
    html_data = bytes.decode(client.get(urlhref[urlhref.find("/wiki/"):]), encoding="ascii", errors="ignore")
    html_data = html_data[html_data.find("<body"):]

    lists = []
    
    while True:
        idx = html_data.find("/wiki/")
        if idx == -1:
            break

        bttn_text, bttn_href = get_surrounding_button(html_data, idx)
        html_data = html_data[idx + len(bttn_href):]

        if bttn_href == "":
            html_data = html_data[idx + len("/wiki/"):]
            continue
        
        html_data = html_data[idx + len(bttn_href):]

        # Filter links for only 'articles'
        if \
                bttn_href[0:len('/wiki/')] == '/wiki/' and\
                bttn_href.find("/wiki/File:") == -1 and\
                bttn_href.find("/wiki/Wikipedia:") == -1 and\
                bttn_href.find("/wiki/Special:") == -1:
            lists.append((get_name_by_href(bttn_href), bttn_href))

    return lists

def gen_wiki_links(client, wiki_lists, max_queries, query_chance, read_modulos = 25, read_timeout = 2.5):
    wiki_links = {}
    idx = 0

    while idx < max_queries:
        for list_link in wiki_lists:
            if idx >= max_queries:
                break

            if query_chance < 1 and random() > query_chance:
                continue

            wl = get_wiki_links(client, list_link[1])
            for l in wl:
                wiki_links[l] = 0
            
            idx += 1
            if idx % read_modulos == 0:
                print(idx)
                sleep(read_timeout)

    wl_keys = list(wiki_links.keys())

    return wl_keys

def write_wiki_links(wiki_links):
    with open("links.json", 'w') as file:
        file.write("{\"links\":[\n")
        for l in wiki_links:
            file.write(f"[\"{l[0].replace("\"", '\\"')}\", \"{l[1]}\"]" + (",\n" if l is not wiki_links[-1] else ''))
        file.write("\n]}")

def decode_element(idx: int, webpage: str, strings: str):
    in_tag = True
    in_end_tag = False

    t = ""
    s = ""

    while idx < len(webpage):
        c_curr = webpage[idx]
        c_next = '' if idx + 1 >= len(webpage) else webpage[idx + 1]

        # wait until out of end tag and break
        if in_end_tag:
            idx += 1
            if c_curr == '>':
                break
            continue
        
        # wait until out of tag
        if in_tag:
            idx += 1
            t += c_curr
            if c_curr == '>':
                t = t.replace('\t', ' ').replace('\n', ' ')[1:-1].split(' ')[0]
                in_tag = False
            continue

        if c_curr == '<':
            if webpage[idx + 1:idx + 1 + len("script")] == "script":
                idx = webpage.find("</script>", idx)
                if idx == -1:
                    idx = len(webpage) - 1
                continue
            if c_next == '/':
                in_end_tag = True
                idx += 1
            else:
                s = s.strip()
                strings.append((t, s))
                s = ""
                idx = decode_element(idx, webpage, strings)
            
            continue

        s += c_curr
        
        idx += 1
    
    s = s.strip()
    if len(s) > 0:
        strings.append((t, s))

    return idx

def get_words(string: str):
    words = []
    wbuf = ""

    string = urllib.parse.unquote(string, encoding="utf-8", errors="ignore")

    for c in string:
        if c.isspace():
            if len(wbuf) > 0:
                words.append(wbuf)
            wbuf = ""
            continue

        if c.isalpha():
            if len(wbuf) == 0 or wbuf[-1].isalpha():
                wbuf += c
            else:
                words.append(wbuf)
                wbuf = ""
        elif c.isnumeric():
            if len(wbuf) == 0 or wbuf[-1].isnumeric():
                wbuf += c
            else:
                words.append(wbuf)
                wbuf = ""
        else:
            if len(wbuf) == 0 or not wbuf[-1].isalnum():
                wbuf += c
            else:
                words.append(wbuf)
                wbuf = ""
    
    if len(wbuf) > 0:
        words.append(wbuf)

    return words

def get_article_body(webpage:str):
    idx = webpage.find("<body")
    idx = webpage.find("From Wikipedia, the free encyclopedia", idx)
    idx = webpage.find(">", idx) + 1
    webpage = webpage[idx: webpage.find("</body>")]
    webpage = webpage[:webpage.find("<h2 id=\"References\">References</h2>")]
    webpage = webpage[:webpage.find("<h2 id=\"See_also\">See also</h2>")]
    idx = 0

    strings = []
    while idx < len(webpage):
        c_curr = webpage[idx]
        
        if c_curr == '<':
            idx = decode_element(idx, webpage, strings)

        idx += 1

    words = []

    for i in strings:
        if i[0] in ('script', 'footer', 'button', 'noscript', 'style') or len(i[1]) == 0:
            continue
        words += get_words(i[1])

    return words

wiki_lists = get_wiki_lists(Client("https://en.wikipedia.org"))

if __name__ == "__main__":
    client = Client('https://en.wikipedia.org')

    links = gen_wiki_links(client, wiki_lists, 5, 0.001)
    write_wiki_links(links)

    l = links[int(random() * (len(links) - 1)) + 1][1]
    print(l)
    b = client.get(l)
    with open("index.html", 'w') as file:
        file.write(b.decode("ascii", "ignore"))
        get_article_body(b.decode("ascii", "ignore"))

    client.close()