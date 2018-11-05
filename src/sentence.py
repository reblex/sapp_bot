#!/usr/bin/env python3
""" Sentence generator using markov self.chain """

import re
from random import randint

class Sentence():
    """Sentence generator"""

    def __init__(self, chain, max_characters, filters=None):
        self.chain = chain  # Initialized Markov self.chain object.
        self.words = None
        self.string = ""
        self.max_characters = max_characters
        self.MAX_WORD_OCCURRENCE = 2
        if filters != None:
            self.filters = filters  # Applied in order listed.
        else:
            self.filters = ["trailing_conjunction",
                            "trailing_commas",
                            "punctuation_whitespace",
                            "punctuation_capitalization",
                            "random_trailing_punctuation"]

        with open('conjunctions.txt', 'r') as f:
            self.CONJUNCTIONS = f.read().split("\n")


    def generate(self):
        """Generate senctances until one is deemed worthy.."""
        too_many_word_occurences = True
        while too_many_word_occurences:
            try:
                self.chain.generate(self.max_characters)
            except Exception as e:
                continue

            too_many_word_occurences = False

            for word in self.chain.values:
                count_occurrences = self.chain.values.count(word)
                if count_occurrences > self.MAX_WORD_OCCURRENCE:
                    too_many_word_occurences = True
                    break

        self.words = self.chain.values
        self.string = ' '.join(self.words)
        self._apply_filters()

    def __str__(self):
        """Printable"""
        return self.string

    def _apply_filters(self):
        """Apply selected filters"""
        filter_functions = {
            'trailing_conjunction': self._trailing_conjunction,
            'trailing_commas': self._trailing_commas,
            'punctuation_whitespace': self._punctuation_whitespace,
            'punctuation_capitalization': self._punctuation_capitalization,
            'random_trailing_punctuation': self._random_trailing_punctuation
        }

        # Call functions based on filter name.
        for filter in self.filters:
            filter_functions[filter]()


    def _trailing_conjunction(self):
        """Remove conjunction if present at end of sentence."""
        if self.words[-1] in self.CONJUNCTIONS:
            self.words = self.words[:-1]

    def _trailing_commas(self):
        """Remove trailing comma, if present."""
        if self.string[-1] == ",":
            self.string = self.string[:-2]

    def _punctuation_whitespace(self):
        """Make sure punctuations (That are followed by words) are followed by space."""
        self.string = re.sub('(?<=[.,!?()])([\w\d])(?! )', r'\0 \1', self.string).strip()

    def _punctuation_capitalization(self):
        """Capitalize first letter of word after punctuation."""
        words = self.string.split()
        for idx in range(len(words) - 1):
            if len(words[idx]) > 0:
                if any(punct in words[idx] for punct in [".", "!", "?"]):
                    words[idx+1] = words[idx+1].title()
        self.string = ' '.join(words)

    def _random_trailing_punctuation(self):
        """Append random punctuation if missing (at end)."""
        punctuations = [".", ".", ".", "!", "?"]
        if self.string[-1] not in punctuations:
            self.string += punctuations[randint(0, len(punctuations) - 1)]