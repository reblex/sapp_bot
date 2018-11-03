#!/usr/bin/env python3
""" Markov chain """

import os
import re
import numpy as np
from random import randint


class Chain():
    """Markov Chain Generator"""
    def __init__(self, corpus_path, model=None):
        self.corpus_path = corpus_path
        self.blacklist = "blacklist.txt"
        self.corpus_pairs = None
        self.corpus_tripples = None
        self.corpus_quads = None
        self.corpus = None    # Splitted words
        self.model = None
        self.values = None

    def build_model(self):
        """Build a new Model from Corpus"""
        # Load corpus
        txt = ""
        blacklist = list() # Ignore blacklisted corpus files
        if os.path.isfile(self.blacklist):
            with open(self.blacklist, encoding='utf8') as f:
                blacklist = f.read().split("\n")

        if os.path.isdir(self.corpus_path):
            for (dirpath, _, filenames) in os.walk(self.corpus_path):
                for filename in filenames:
                    if filename in blacklist:
                        continue
                    with open(os.path.join(dirpath, filename)) as f:
                        txt += f.read()
        else:
            with open(self.corpus_path, encoding='utf8') as f:
                txt = f.read()

        self.corpus = list()

        for word in txt.split():
            word = word.lower()
            word = re.sub(r"[\,\.\?\!\(\)\"\“\”\:\[\]]", '', word)

            self.corpus.append(word)

        # Yield a generator object from corpus
        self.corpus_pairs = self.make_pairs()
        self.corpus_tripples = self.make_tripples()
        self.corpus_quads = self.make_quads()

        self.model = self.instantiate_model()

    def load_model(self, file):
        """Load a Model from File"""
        # 1. load model from file
        # 2. instantiate_model()
        pass

    def generate(self, steps):
        """Generate Markov Chain based on Model"""
        # Pick a random capitalized first word.
        first_word = np.random.choice(self.corpus)

        self.values = [first_word]

        for _ in range(steps):
            # TODO: If there are too few words possible, maybe pick another
            # random word.
            # print(self.model[self.values[-1]])
            self.values.append(self.walk())

        self.values[0] = self.values[0].title()

    def instantiate_model(self, save=True):
        """Build the model"""
        model = {}

        # Fill dictionary with word pairs, appending to already existing keys.
        for word_1, word_2 in self.corpus_pairs:
            if word_1 in model.keys():
                if word_2 in model[word_1].keys():
                    model[word_1][word_2] += 1
                else:
                    model[word_1][word_2] = 1
            else:
                model[word_1] = {word_2: 1}

        # Fill dictionary with word tripples, using two words as key.
        for word_1, word_2, word_3 in self.corpus_tripples:
            pair = word_1 + " " + word_2

            if pair in model.keys():
                if word_3 in model[pair].keys():
                    model[pair][word_3] += 1
                else:
                    model[pair][word_3] = 1
            else:
                model[pair] = {word_3: 1}

        # Fill dictionary with word quads, using three words as key.
        for word_1, word_2, word_3, word_4 in self.corpus_quads:
            pair = word_1 + " " + word_2 + " " + word_3

            if pair in model.keys():
                if word_4 in model[pair].keys():
                    model[pair][word_4] += 1
                else:
                    model[pair][word_4] = 1
            else:
                model[pair] = {word_4: 1}

        if save:
            if not os.path.exists("models"):
                os.makedirs("models")
            with open("models/markov_dict.txt", "w") as file:
                for key, value in model.items():
                    file.write('%s:%s\n' % (key, value))

        return model

    def make_pairs(self):
        """Yielding a generator object from corpus, with paired words"""
        for i in range(len(self.corpus)-1):
            yield (self.corpus[i], self.corpus[i+1])

    def make_tripples(self):
        """Yielding a generator object from corpus, with three paired words"""
        for i in range(len(self.corpus)-2):
            yield (self.corpus[i], self.corpus[i+1], self.corpus[i+2])

    def make_quads(self):
        """Yielding a generator object from corpus, with four paired words"""
        for i in range(len(self.corpus)-3):
            yield (self.corpus[i], self.corpus[i+1], self.corpus[i+2], self.corpus[i+3])

    def walk(self):
        """
        Pick the next step at random
        Each key appearance rate is turned into a probability.
        Then a random key is selected at random, based on probability.
        """

        last_word = self.values[-1]
        key_to_check = last_word

        if len(self.values) >= 3:
            second_last_word = self.values[-2]
            third_last_word = self.values[-3]
            tripple_word = third_last_word + " " + second_last_word + " " + last_word
            if tripple_word in self.model:
                # print(self.model[tripple_word])
                # Default rand_max: 10 gives 30% chance of picking double word value
                # If double word has more than one value, increase chance to pick a double word value.
                rand_max = 10
                if len(self.model[tripple_word].keys()) > 3:
                    rand_max = 25
                elif len(self.model[tripple_word].keys()) > 1:
                    rand_max = 15

                if randint(1, rand_max) > 7:
                    key_to_check = tripple_word

        elif len(self.values) >= 2:
            second_last_word = self.values[-2]
            double_word = second_last_word + " " + last_word
            if double_word in self.model:
                # print(self.model[double_word])
                # Default rand_max: 10 gives 30% chance of picking double word value
                # If double word has more than one value, increase chance to pick a double word value.
                rand_max = 10
                if len(self.model[double_word].keys()) > 3:
                    rand_max = 25
                elif len(self.model[double_word].keys()) > 1:
                    rand_max = 15

                if randint(1, rand_max) > 7:
                    key_to_check = double_word

        chain = self.model[key_to_check]

        keys = list(chain.keys())

        # Calculate the normalizer, using: (1 / (sum of values))
        normalizer = 1 / float(sum(chain.values()))

        # Multiply each value by the normalizer
        probabilities = [x * normalizer for x in chain.values()]

        # TODO: Check if there is a greater match in double word keys.
        # Reduced chance of picking multiple tripples, quads...

        # TODO: Larger chance to pick word that has many values

        step = np.random.choice(keys, 1, p=probabilities)[0]
        # print("word:", step)

        return step
