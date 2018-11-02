#!/usr/bin/env python3
""" Main interface """

from random import randint
from src.chain import Chain


def main():
    """Main function"""
    chain = Chain("corpus/test.txt")
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
