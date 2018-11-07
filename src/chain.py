#!/usr/bin/env python3
""" Markov chain """

import os
import re
import sys
import numpy as np
from random import randint


class Chain():
    """Markov Chain Generator"""
    def __init__(self, corpus_path, model=None):
        self.corpus_path = corpus_path
        self.word_blacklist = list()
        if os.path.isfile("word_blacklist.txt"):
            with open("word_blacklist.txt", encoding='utf8') as f:
                word_blacklist = f.read().split("\n")

        self.corpus_pairs = None
        self.corpus_tripples = None
        self.corpus_quads = None
        self.corpus = list()    # Splitted words
        self.model = None
        self.values = None

        # TODO: Make newline not continue as sentence? Names get combined together.

    def build_model(self):
        """Build a new Model from Corpus"""
        if os.path.isdir(self.corpus_path):
            for (dirpath, _, filenames) in os.walk(self.corpus_path):
                for filename in filenames:
                    with open(os.path.join(dirpath, filename)) as f:
                        txt = f.read()

                    # For each paragraph in the loaded file, filter the words
                    # and add as lists in corpus.
                    for paragraph in txt.split('\n'):
                        self.corpus.append(self.filter_words(paragraph))
        else:
            with open(self.corpus_path, encoding='utf8') as f:
                txt = f.read()
                for paragraph in txt.split('\n'):
                    self.corpus.append(self.filter_words(paragraph))


        # Yield generator objects from corpus.
        self.corpus_pairs = self.make_pairs()
        self.corpus_tripples = self.make_tripples()
        self.corpus_quads = self.make_quads()


        self.model = self.instantiate_model()

    def filter_words(self, text):
        """Return list of accepted and filtered words from a string."""
        paragraph_words = list()
        punct_only_word = "^[\-\,\.\/?\!\\\/\;\:\"\(\)]+$"

        for word in text.split():
            if word not in self.word_blacklist and re.match(punct_only_word, word) == None:
                word = word.lower()
                # word = re.sub(r"[\-\,\.\?\!\(\)\"\“\”\:\'\[\]]", '', word)
                word = re.sub(r"[\-\(\)\"\“\”\:\;\'\[\]]", '', word)
                word = re.sub(r"[\/]", ' ', word)

                paragraph_words.append(word)

        return paragraph_words


    def load_model(self, file):
        """Load a Model from File"""
        # 1. load model from file
        # 2. instantiate_model()
        pass

    def generate(self, num_chars, fw=None):
        """Generate Markov Chain based on Model"""
        # Pick a random capitalized first word.
        word = np.random.choice(list(self.model.keys()), 1)[0]
        first_word = word.split(' ')[0]

        if fw != None:
            first_word = fw
        else:
            # 90% chance to pick another random word if chosen words key only has two or less values.
            while len(self.model[first_word].values()) <= 2 and randint(1, 100) > 10:
                try:
                    word = np.random.choice(list(self.model.keys()), 1)[0]
                    first_word = word.split(' ')[0]
                except Exception as e:
                    pass # TODO: Handle this.

        self.values = [first_word]

        # Pick a second word that is part of a multi-key, if possible.
        multi_key_search = '^' + first_word + '\s(.+?(?:\s.+?)*)'
        multi_keys = list()

        for key in list(self.model.keys()):
            if re.match(multi_key_search, key):

                multi_keys.append(key)

        if len(multi_keys) > 0:
            multi_key = np.random.choice(multi_keys, 1)[0]
            word = ''.join(multi_key.split(' ')[1])
            self.values.append(word)


        # While there are characters left, keep chosing new words.
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
        for sub_list in self.corpus:
            for i in range(len(sub_list)-1):
                yield (sub_list[i], sub_list[i+1])

    def make_tripples(self):
        """Yielding a generator object from corpus, with three paired words"""
        for sub_list in self.corpus:
            for i in range(len(sub_list)-2):
                yield (sub_list[i], sub_list[i+1], sub_list[i+2])

    def make_quads(self):
        """Yielding a generator object from corpus, with four paired words"""
        for sub_list in self.corpus:
            for i in range(len(sub_list)-3):
                yield (sub_list[i], sub_list[i+1], sub_list[i+2], sub_list[i+3])

    def walk(self):
        """
        Pick the next step at random
        Each key appearance rate is turned into a probability.
        Then a random key is selected at random, based on probability.
        """

        last_word = self.values[-1]
        key_to_check = last_word
        multi_key_selected = False

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
                    chance = 90
                elif len(self.model[tripple_word].keys()) > 1:
                    chance = 85
                else:
                    chance = 45

                cmp_val = 100 - chance
                if randint(1, 100) > cmp_val:
                    key_to_check = tripple_word
                    multi_key_selected = False
                    # print("selecting tripple key:", tripple_word)

        if not multi_key_selected:
            if len(self.values) >= 2 and randint(1, 100) > 10: # Else 90% chance to try double key.
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
                        multi_key_selected = False
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
