#!/usr/bin/env python3
""" Sentence generator using markov self.chain """

import re
import os
from random import randint

class Sentence():
    """Sentence generator"""

    def __init__(self, chain, max_characters, filters=None):
        self.chain = chain  # Initialized Markov self.chain object.
        self.words = None
        self.string = ""
        self.max_characters = max_characters
        self.max_word_occurrence = 6    # TODO: should be per sentence, not whole chain. (split on ".!?")
        if filters is not None:
            self.filters = filters  # Applied in order listed.
        else:
            # Alwas in this order!
            self.filters = ["trailing_conjunction",
                            "trailing_commas",
                            # "punctuation_whitespace",
                            "punctuation_capitalization",
                            "random_trailing_punctuation",
                            "capitalize_names"]

        with open('conjunctions.txt', 'r') as file:
            self.conjunctions = file.read().split("\n")


    def generate(self, first_word=None):
        """Generate senctances until one is deemed worthy.."""
        too_many_word_occurences = True
        while too_many_word_occurences:
            completed = False
            while not completed:
                try:
                    # print("Generating a tweet of max", self.max_characters, "characters...")
                    self.chain.generate(self.max_characters, first_word)
                    completed = True
                except BaseException as exception:
                    print("Error in sentence.generate", str(exception))

            too_many_word_occurences = False

            # print(' '.join(self.chain.values))
            for word in self.chain.values:
                count_occurrences = self.chain.values.count(word)
                if count_occurrences > self.max_word_occurrence:
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
            'random_trailing_punctuation': self._random_trailing_punctuation,
            'capitalize_names': self._capitalize_names
        }

        # Call functions based on filter name.
        for current_filter in self.filters:
            filter_functions[current_filter]()


    def _trailing_conjunction(self):
        """Remove conjunction if present at end of sentence."""
        last_word = re.sub(r"[\-\,\.\?\!\(\)\"\“\”\:\'\[\]]", '', self.words[-1])
        b = last_word in self.conjunctions
        while last_word in self.conjunctions:
            del self.words[-1]
            last_word = re.sub(r"[\-\,\.\?\!\(\)\"\“\”\:\'\[\]]", '', self.words[-1])

        self.string = ' '.join(self.words)

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

    def _capitalize_names(self):
        """Capitalize names anywhere in sentence."""
        if os.path.isfile("config/saved_users.txt"):
            names = list()
            with open('config/saved_users.txt', 'r') as file:
                names = file.read().split("\n")

            words = self.string.split()

            for i in range(len(words) - 1):
                if words[i] in names:
                    words[i] = words[i].title()

            self.string = ' '.join(words)
