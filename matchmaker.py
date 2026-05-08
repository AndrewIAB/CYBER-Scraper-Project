"""
Game state:
-----------
Current article
Article list
Theme
Match score

"""

from tkinter import Tk, ttk
import tkinter as tk
from time import sleep
from random import choice
from json import JSONDecoder

import wikipedia
from Scrapenator import Client

from random import random

def compare_elems(t1, t2):
    w1 = {}

    for w in t1:
        if w in w1:
            w1[w] += 1
        else:
            w1[w] = 1
    
    occur = 0
    total = 0

    for w in t2:
        # weigh words by length so words like "in" or "a" dont pollute the output
        weight = len(w)
        if w in w1:
            occur += weight
        total += weight

    print(occur)
    print(total)

    return occur / total

class Game:
    def __init__(self, sim_min, sim_max):
        self.client = Client("https://en.wikipedia.org/")
        
        self.a1 = None
        self.a2 = None

        self.sim_range = (sim_min, sim_max)

        self.min_similarity = 0
        self.similarity = 0

        self.correct_guesses = 0
        self.total_guesses = 0
    
    # Scrape article 1
    def get_t1(self):
        g_a1 = self.client.get(self.a1[1]).decode("ascii", "ignore")
        self.t1 = wikipedia.get_article_body(g_a1)
    # Scrape article 2
    def get_t2(self):
        g_a2 = self.client.get(self.a2[1]).decode("ascii", "ignore")
        self.t2 = wikipedia.get_article_body(g_a2)

    def new_round(self):
        self.links = wikipedia.gen_wiki_links(self.client, wikipedia.wiki_lists, 5, 0.001)
        shuffle(self.links)
        self.links = self.links[:10]
        self.a1 = self.links.pop()
        self.a2 = self.links.pop()
        self.min_similarity = random() * (self.sim_range[1] - self.sim_range[0]) + self.sim_range[0]

        self.get_t1()
        self.get_t2()

        self.update_similarity()
    
    def cmd_skip(self):
        if len(self.links) == 0:
            self.wrong()
        else:
            self.a2 = self.links.pop()
            self.get_t2()
            self.update_similarity()
    
    def cmd_good(self):
        if self.similarity >= self.min_similarity:
            self.correct()
        else:
            self.wrong()
    
    def cmd_bad(self):
        if self.similarity >= self.min_similarity:
            self.wrong()
        else:
            self.correct()

    def update_similarity(self):
        self.similarity = compare_elems(self.t1, self.t2)

    def wrong(self):
        self.total_guesses += 1
        self.new_round()
    
    def correct(self):
        self.total_guesses += 1
        self.correct_guesses += 1
        self.new_round()
    
    def percent_correct(self):
        if self.total_guesses == 0:
            return 100
        return self.correct_guesses / self.total_guesses * 100

from random import shuffle

if __name__ == "__main__":
    game = Game(.2, .6)

    shuffle(wikipedia.wiki_lists)
    links = wikipedia.gen_wiki_links(game.client, wikipedia.wiki_lists, 1, 0.9)

    l1 = choice(links)
    l2 = choice(links)

    print(l1[0], "-->", game.client.host+l1[1])
    print(l2[0], "-->", game.client.host+l2[1])

    a1 = game.client.get(l1[1]).decode("ascii", "ignore")
    t1 = wikipedia.get_article_body(a1)

    a2 = game.client.get(l2[1]).decode("ascii", "ignore")
    t2 = wikipedia.get_article_body(a2)

    print(compare_elems(t1, t2))