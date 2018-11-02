#!/usr/bin/env python3
""" Main interface """

from src.chain import Chain
from src.wiki_scraper import WikiScraper
from random import randint
from src.chain import Chain


def main():
    """Main function"""
    # Scrape Minervawikin
    # ws = WikiScraper()
    # ws.set_page_list()
    # ws.build_corpus()

    chain = Chain("corpus")
    chain.build_model()
    chain.generate(20)

    # Join the words into a string.
    sentance = ' '.join(chain.values)

    # Append random punctuation if missing.
    punctuations = [".", "!", "?"]
    if sentance[-1] not in punctuations:
        sentance += punctuations[randint(0, len(punctuations) - 1)]

    # Print the resulting sentance.
    print(sentance)


if __name__ == "__main__":
    main()
