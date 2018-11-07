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

        self.NUM_GENERATORS = 3
        self.generators = list()
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
        for i in range(self.NUM_GENERATORS):
            self.generators.append(self.create_model_generator(i + 2))

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

        for generator in self.generators:
            model = self.expand_model(model, generator)

        if save:
            if not os.path.exists("models"):
                os.makedirs("models")
            with open("models/markov_dict.txt", "w") as file:
                for key, value in model.items():
                    file.write('%s:%s\n' % (key, value))

        return model


    def expand_model(self, model, corpus_generator):
        """Expand the markov model with multi or single keys."""
        expanded_model = model
        for string in corpus_generator:
            multi = ' '.join(string)
            key = ' '.join(multi.split(' ')[:-1])
            value = multi.split(' ')[-1]

            # If the key exists, put value in that key, or just add to count if value exists.
            # If key doesn't exist, append it.
            if key in expanded_model.keys():
                if value in expanded_model[key].keys():
                    expanded_model[key][value] += 1
                else:
                    expanded_model[key][value] = 1
            else:
                expanded_model[key] = {value: 1}

        return expanded_model


    def create_model_generator(self, words_in_key):
        """Yield a generator object from corpus with key-value single_key"""
        for sub_list in self.corpus:
            for i in range(len(sub_list) - words_in_key):
                yield [sub_list[i+x] for x in range(words_in_key)]


    def walk(self):
        """
        Pick the next step at random
        Each key appearance rate is turned into a probability.
        Then a random key is selected at random, based on probability.
        """
        key_to_check = self.values[-1] # If no multikey is chosen, just use last word.
        chance = None

        for i in range(self.NUM_GENERATORS, 1, -1):
            # If there are too few words to check for 'i' number of keys, skip.
            if len(self.values) < self.NUM_GENERATORS:
                continue

            # Base 80% chance to pick multi-key, for now.
            if randint(1, 100) > 20:
                multi = ' '.join(self.values)
                # print(i, multi)
                start_key_pos = len(self.values) - i
                key = ' '.join(multi.split(' ')[start_key_pos:])

                if key in self.model:
                    if len(self.model[tripple_word].keys()) > 3:
                        chance = 90
                    elif len(self.model[tripple_word].keys()) > 1:
                        chance = 85
                    else:
                        chance = 25

                    cmp_val = 100 - chance
                    if randint(1, 100) > cmp_val:
                        key_to_check = key
                        break

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
