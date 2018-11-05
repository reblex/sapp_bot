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
        self.word_blacklist = "word_blacklist.txt"
        self.corpus_pairs = None
        self.corpus_tripples = None
        self.corpus_quads = None
        self.corpus = None    # Splitted words
        self.model = None
        self.values = None

        # TODO: Make newline not continue as sentence? Names get combined together.

    def build_model(self):
        """Build a new Model from Corpus"""
        # Load corpus
        txt = ""
        blacklist = list() # Ignore blacklisted corpus files
        if os.path.isfile(self.blacklist):
            with open(self.blacklist, encoding='utf8') as f:
                blacklist = f.read().split("\n")

        word_blacklist = list() # Ignore word_blacklisted corpus files
        if os.path.isfile(self.word_blacklist):
            with open(self.word_blacklist, encoding='utf8') as f:
                word_blacklist = f.read().split("\n")

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

        puncts = ["-", ",", ".", "?", "!", "\\", "/", ";", ":"]

        for word in txt.split():
            if word not in word_blacklist and word not in puncts:
                word = word.lower()
                # word = re.sub(r"[\-\,\.\?\!\(\)\"\“\”\:\'\[\]]", '', word)
                word = re.sub(r"[\(\)\"\“\”\:\;\'\[\]]", '', word)
                word = re.sub(r"[\/]", ' ', word)
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

    def generate(self, num_chars, fw=None):
        """Generate Markov Chain based on Model"""
        # Pick a random capitalized first word.
        first_word = np.random.choice(self.corpus)

        if fw != None:
            first_word = fw
        else:
            # 70% chance to pick another random word if chosen words key only has two or less values.
            if len(self.model[first_word].values()) <= 2 and randint(1, 100) > 30:
                try:
                    first_word = np.random.choice(list(self.model.keys()), 1)[0]
                except Exception as e:
                    pass # TODO: Handle this.

        self.values = [first_word]

        character_capped = False
        while not character_capped:
            # TODO: If there are too few words possible, maybe pick another
            # random word.
            value = self.walk()
            chars = len(' '.join(self.values) + " " + value)
            # print(chars)

            # 60% chance to pick another random word if chosen words key only has one value.
            if len(self.model[value].values()) == 1 and randint(1, 100) > 40:
                try:
                    value = np.random.choice(list(self.model.keys()), 1)[0]
                except Exception as e:
                    pass # TODO: Handle this.

            if chars > num_chars:
                character_capped = True
            else:
                self.values.append(value)


        # TODO: move grammar stuff out of chain.

        # Remove leading sentence whitespace, if present
        if len(self.values[0]) > 0: # No idea why this would be zero, but it works.
            if self.values[0][0] == " ":
                self.values[0] = self.values[0][1:]

        #Capitalize first character in first word.
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

        chance = None  # Chance in percentage to pick double/tripple/quad key

        # TODO: Make it possible to randomly start building towards a tripple
        # key while sentence is still less than 3 words.

        if len(self.values) >= 3 and randint(1, 100) > 20: # 80% chance to try tripple key.
            second_last_word = self.values[-2]
            third_last_word = self.values[-3]
            tripple_word = third_last_word + " " + second_last_word + " " + last_word
            if tripple_word in self.model:
                # print(self.model[tripple_word])

                if len(self.model[tripple_word].keys()) > 3:
                    chance = 85
                elif len(self.model[tripple_word].keys()) > 1:
                    chance = 80
                else:
                    chance = 50

                cmp_val = 100 - chance
                if randint(1, 100) > cmp_val:
                    key_to_check = tripple_word
                    # print("selecting tripple key:", tripple_word)

        elif len(self.values) >= 2 and randint(1, 100) > 10: # Else 90% chance to try double key.
            second_last_word = self.values[-2]
            double_word = second_last_word + " " + last_word
            if double_word in self.model:
                # print(self.model[double_word])

                if len(self.model[double_word].keys()) > 3:
                    chance = 95
                elif len(self.model[double_word].keys()) > 1:
                    chance = 90
                else:
                    chance = 70

                cmp_val = 100 - chance
                if randint(1, 100) >= cmp_val:
                    key_to_check = double_word
                    # print("selecting double key:", double_word)

        chain = self.model[key_to_check]

        keys = list(chain.keys())

        # Calculate the normalizer, using: (1 / (sum of values))
        normalizer = 1 / float(sum(chain.values()))

        # Multiply each value by the normalizer
        probabilities = [x * normalizer for x in chain.values()]

        step = np.random.choice(keys, 1, p=probabilities)[0]

        # Dont pick two numbers in a row.
        if self.values[-1].isdigit() and len(self.model[step]) > 1:
            while step.isdigit():
                # Small chance to just pick a random (non digit) word instead.
                if passrandint(1, 100) > 99:
                    step = np.random.choice(list(self.model.keys()), 1)[0]
                else:
                    step = np.random.choice(keys, 1, p=probabilities)[0]

        # print("word selected:", step)

        return step
