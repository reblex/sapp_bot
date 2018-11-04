#!/usr/bin/env python3
""" Main interface """

from random import randint

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

        # Capitalize first letter in word after punctuation.
        for idx in range(len(chain.values) - 1):
            if len(chain.values[idx]) > 0:
                if chain.values[idx][-1] in [".", "!", "?"]:
                    chain.values[idx+1] = chain.values[idx+1].title()

        # TODO: Disallow multiple numbers in a row. (multiple words only containing numbers)

        # Remove conjunction if present at end of sentence.
        if chain.values[-1] in CONJUNCTIONS:
            chain.values = chain.values[:-1]



        # Join the words into a string.
        sentence = ' '.join(chain.values)


        # Append random punctuation if missing.
        punctuations = [".", "!", "?"]
        if sentence[-1] not in punctuations:
            sentence += punctuations[randint(0, len(punctuations) - 1)]


        # Print the resulting sentence.
        print(sentence + "\n")


if __name__ == "__main__":
    main()
