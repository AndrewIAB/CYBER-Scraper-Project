import http.client

# Need this to avoid getting blocked by websites
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.100 Safari/537.36'}

def decode_url(url):
    url = url.replace('\\', '/')

    https_idx = url.find("https://")
    http_idx = url.find("http://")
    if https_idx != -1:
        url = url[https_idx + len("https://"):]
    elif http_idx != -1:
        url = url[http_idx + len("http://"):]

    slash_idx = url.find('/')
    dir = '/'
    if slash_idx != -1:
        dir = url[slash_idx:]
        url = url[:slash_idx]
    
    return (https_idx != -1), url, dir

class Client:
    def create_connection(self, url: str, port=None):
        if \
            type(self.connection) is http.client.HTTPConnection or\
            type(self.connection) is http.client.HTTPSConnection:
            self.connection.close()

        is_https, host, _ = decode_url(url)
        self.host = host

        if is_https:
            self.connection = http.client.HTTPSConnection(host, port)
        else:
            self.connection = http.client.HTTPConnection(host, port)
    
    def __init__(self, url: str, port=None):
        self.connection = None
        self.create_connection(url, port)

    def close(self):
        self.connection.close()

    def get(self, path):
        self.connection.request("GET", path, headers=headers)
        response = self.connection.getresponse()

        print(path, response.status, response.reason)

        if response.status == 301:
            location = response.getheader("Location")
            print("Relocated to", location)

            self.create_connection(location)
            self.connection.request("GET", path, headers=headers)
            response = self.connection.getresponse();

            print(response.status, response.reason)
        
        return response.read()

if __name__ == "__main__":
    c = Client("https://en.wikipedia.org")
    code = c.get("/wiki/Lists_of_abbreviations")

    with open("index.html", 'w') as file:
        file.write(code.decode('ascii', 'ignore'))

    c.close()
    