#!/usr/bin/env python3
""" Main interface """

from random import randint
import re

from src.chain import Chain
from src.wiki_scraper import WikiScraper
from src.sentence import Sentence


def main():
    """Main function"""
    # Scrape Minervawikin
    # ws = WikiScraper()
    # ws.set_page_list()
    # ws.build_corpus()

    chain = Chain("corpus")
    chain.build_model()

    for _ in range(5):
        sentence = Sentence(chain, randint(120, 260))
        sentence.generate()

        # Print the resulting sentence.
        print(str(sentence) + "\n")

if __name__ == "__main__":
    main()
