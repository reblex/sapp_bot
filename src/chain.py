#!/usr/bin/env python3
""" Markov chain """

import os
import numpy as np


class Chain():
    """Markov Chain Generator"""
    def __init__(self, corpus_path, model=None):
        self.corpus_path = corpus_path
        self.corpus_pairs = None
        self.corpus = None    # Splitted words
        self.model = None
        self.values = None

    def build_model(self):
        """Build a new Model from Corpus"""
        # Load corpus
        txt = ""
        if os.path.isdir(self.corpus_path):
            for (dirpath, _, filenames) in os.walk(self.corpus_path):
                for filename in filenames:
                    with open(os.path.join(dirpath, filename)) as f:
                        txt += f.read()
        else:
            with open(self.corpus_path, encoding='utf8') as f:
                txt = f.read()

        self.corpus = list()

        for word in txt.split():
            word = word.lower()
            word = word.strip(',.?!()"“”:')

            self.corpus.append(word)

        # Yield a generator object from corpus
        self.corpus_pairs = self.make_pairs()

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
            self.values.append(self.walk(self.model[self.values[-1]]))

        self.values[0] = self.values[0].title()

    def instantiate_model(self, save=True):
        """Build the model"""
        # Fill dictionary with word pairs, appending to already existing keys.
        model = {}
        for word_1, word_2 in self.corpus_pairs:
            if word_1 in model.keys():
                if word_2 in model[word_1].keys():
                    model[word_1][word_2] += 1
                else:
                    model[word_1][word_2] = 1
            else:
                model[word_1] = {word_2: 1}

        if save:
            if not os.path.exists("models"):
                os.makedirs("models")
            with open("models/markov_dict.txt", "w") as file:
                for key, value in model.items():
                    file.write('%s:%s\n' % (key, value))

        return model

    def make_pairs(self):
        """Yielding a generator object from corpus"""
        for i in range(len(self.corpus)-1):
            yield (self.corpus[i], self.corpus[i+1])

    def walk(self, chain):
        """
        Pick the next step at random
        Each key appearance count is turned into a probability.
        Then a random key is selected at random, based on probability.
        """
        keys = list(chain.keys())

        # Calculate the normalizer, using: (1 / (sum of values))
        normalizer = 1 / float(sum(chain.values()))

        # Multiply each value by the normalizer
        probabilities = [x * normalizer for x in chain.values()]

        step = np.random.choice(keys, 1, p=probabilities)[0]

        return step
