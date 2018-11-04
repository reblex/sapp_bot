#!/usr/bin/env python3
""" Main interface """

from random import randint
import re

from src.chain import Chain
from src.wiki_scraper import WikiScraper
from src.chain import Chain


def main():
    """Main function"""
    # Scrape Minervawikin
    # ws = WikiScraper()
    # ws.set_page_list()
    # ws.build_corpus()

    chain = Chain("corpus", "whiplash")
    chain.build_model()

    MAX_WORD_OCCURRENCE = 2

    with open('conjunctions.txt', 'r') as f:
        CONJUNCTIONS = f.read().split("\n")

    for i in range(5):

        # Generate senctances until one is deemed worthy..
        too_many_word_occurences = True
        while too_many_word_occurences: # TODO: also check for too many punctuations.

            # TODO: Generate random character max, up to twitter max.
            # chain.generate(279) # 1 lower than max to allow for punctuation.
            chain.generate(randint(120, 260))
            too_many_word_occurences = False

            for word in chain.values:
                count_occurrences = chain.values.count(word)
                if count_occurrences > MAX_WORD_OCCURRENCE:
                    too_many_word_occurences = True
                    break


        # Remove conjunction if present at end of sentence.
        if chain.values[-1] in CONJUNCTIONS:
            chain.values = chain.values[:-1]

        # Join the words into a string.
        sentence = ' '.join(chain.values)

        # Remove trailing comma, if present.
        if sentence[-1] == ",":
            sentence = sentence[:-2]

        # Make sure punctuations (That are followed by words) are followed by space.
        sentence = re.sub('(?<=[.,!?()])([\w\d])(?! )', r'\0 \1', sentence).strip()

        # Capitalize first letter of word after punctuation.
        words = sentence.split()
        for idx in range(len(words) - 1):
            if len(words[idx]) > 0:
                if any(punct in words[idx] for punct in [".", "!", "?"]):
                    words[idx+1] = words[idx+1].title()
        sentence = ' '.join(words)

        # Append random punctuation if missing (at end).
        punctuations = [".", "!", "?"]
        if sentence[-1] not in punctuations:
            sentence += punctuations[randint(0, len(punctuations) - 1)]


        # Print the resulting sentence.
        print(sentence + "\n")


if __name__ == "__main__":
    main()
