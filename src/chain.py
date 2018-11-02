#!/usr/bin/env python3

import numpy as np


class Chain(object):
    """Markov Chain Generator"""
    def __init__(self, corpus_path, model=None):
        self.corpus_path = corpus_path
        self.corpus = None    # Splitted words
        self.model = None
        self.values = None


    def build_model(self, save=True):
        """Build a new Model from Corpus"""
        # Load corpus
        txt = open(self.corpus_path, encoding='utf8').read()
        self.corpus = txt.split()

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

        while first_word.islower(): # TODO: better handling of first capital? Maybe.
            first_word = np.random.choice(self.corpus)
        self.values = [first_word]

        for i in range(steps):
            self.values.append(self.walk(self.model[self.values[-1]]))






    def instantiate_model(self, save=True):
        """Build the model"""
        # Fill dictionary with word pairs, appending to already existing keys.
        # TODO: Move more occuring words to the left
        model = {}
        for word_1, word_2 in self.corpus_pairs:
            if word_1 in model.keys():
                if word_2 in model[word_1].keys():
                    model[word_1][word_2] += 1
                else:
                    model[word_1][word_2] = 1
            else:
                model[word_1] = {word_2: 1}

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
