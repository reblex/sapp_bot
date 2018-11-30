#!/usr/bin/env python3
""" Markov chain """

import os
import re
from random import randint
import numpy as np


class Chain():
    """Markov Chain Generator"""
    def __init__(self, corpus_path, debug=False):
        self.corpus_path = corpus_path
        self.complexity = 10
        self.debug = debug
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
        for i in range(self.complexity):
            self.generators.append(self.create_model_generator(i + 2))

        self.model = self.instantiate_model()

    def filter_words(self, text):
        """Return list of accepted and filtered words from a string."""
        paragraph_words = list()
        punct_only_word = "^[\~\-\,\.\/?\!\\\/\;\:\"\(\)]+$"

        for word in text.split():
            if re.match(punct_only_word, word) is None:
                word = word.lower()
                # word = re.sub(r"[\-\,\.\?\!\(\)\"\“\”\:\'\[\]]", '', word)
                word = re.sub(r"[\(\)\"\“\”\:\;\'\[\]]", '', word)
                word = re.sub(r"[\-]([\w\d]+?)[\-]", r'\0', word)
                word = re.sub(r"[\/]", ' ', word)

                paragraph_words.append(word)

        return paragraph_words


    def load_model(self, file):
        """Load a Model from File"""
        # 1. load model from file
        # 2. instantiate_model()
        pass

    def pick_multi_continue(self, first_word):
        """Pick a random word that is part of multikey, beginning with first_word."""
        multi_key_search = '^' + first_word + '\s(.+?(?:\s.+?)*)'
        multi_keys = list()
        word = None

        for key in list(self.model.keys()):
            if re.match(multi_key_search, key):
                multi_keys.append(key)

        if len(multi_keys) > 0:
            multi_key = np.random.choice(multi_keys, 1)[0]
            word = ''.join(multi_key.split(' ')[-1])

        return word

    def generate(self, max_chars, fw=None):
        """Generate Markov Chain based on Model"""
        # Pick a random capitalized first word.
        word = np.random.choice(list(self.model.keys()), 1)[0]
        first_word = word.split(' ')[0]

        if fw is None:
            first = ""
        else:
            first = fw

        if first != "" and first.lower() in self.model.keys():
            first_word = first

        elif os.path.isfile("config/saved_users.txt") and randint(1, 100) > 50:
            users = list()

            with open('config/saved_users.txt', 'r') as file:
                users = file.read().split("\n")

            if len(users) > 0:
                while first == "" or first.lower() not in self.model.keys():
                    first = np.random.choice(users, 1)[0]

                first_word = first

        else:
            # 90% chance to pick another random word if chosen words key only has 3 or less values.
            while len(self.model[first_word].values()) <= 3 and randint(1, 100) > 10:
                try:
                    word = np.random.choice(list(self.model.keys()), 1)[0]
                    first_word = word.split(' ')[0]
                except Exception as e:
                    print("Error in chain.generate:", str(e))
                    pass # TODO: Handle this.

        if self.debug:
            print("First word:", first_word)

        self.values = [first_word]
        second_word = None

        try:
            second_word = self.pick_multi_continue(first_word)
            self.values.append(second_word)
            if self.debug:
                print("Second word:", second_word)
        except BaseException as exception:
            print(str(exception))

        if second_word is not None:
            try:
                third_word = self.pick_multi_continue(first_word + " " + second_word)
                if third_word is not None:
                    self.values.append(third_word)
                    if self.debug:
                        print("Third word:", third_word)
            except BaseException as exception:
                print(str(exception))


        # While there are characters left, keep chosing new words.
        character_capped = False
        while not character_capped:
            value = self.walk()

            # Pick a random word if it is after punctuation.
            if any(punct in self.values[-1] for punct in [".", "!", "?"]):
                while len(self.model[value].values()) <= 2 and randint(1, 100) > 10:
                    try:
                        value = np.random.choice(list(self.model.keys()), 1)[0]
                        first_word = value.split(' ')[0]
                    except BaseException as exception:
                        print("Error in chain.generate loop:", str(exception))
                        # TODO: Handle this better

            # After punctuation and first word after, try to pick multi_key word.
            if len(self.values) > 2:
                if any(punct in self.values[-2][-1] for punct in [".", "!", "?"]):
                    value = self.pick_multi_continue(self.values[-1])

            # TODO: fix this mess....
            # # 40% chance to pick another random word if chosen words key only has one value.
            # # TODO: crashes without try/catch if value is not in base of self.model..
            # try:
            #     if len(list(self.model[value].keys())) == 1 and randint(1, 100) > 60:
            #         try:
            #             print("trying")
            #             value = np.random.choice(list(self.model.keys()), 1)[0]
            #         except Exception as e:
            #             print("Error:", str(e))
            #             pass # TODO: Handle this.
            # except Exception as e:
            #     pass



            chars = len(' '.join(self.values) + " " + value)
            # print(chars)

            if chars > max_chars:
                character_capped = True
            else:
                self.values.append(value.split()[-1])

            # Try to end sentence on an already punctuated word.
            if chars > max_chars - 70 and any(punct in self.values[-1] for punct in [".", "!", "?"]):
                if self.debug:
                    print("Ending on punctuated word:", self.values[-1])
                character_capped = True


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

    @staticmethod
    def expand_model(model, corpus_generator):
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
        multi_picked = False
        chance = None
        denied_multi = ''
        denying_multi = False

        for i in range(self.complexity, 1, -1):
            # If there are too few words to check for 'i' number of keys, skip.
            if len(self.values) < i:
                continue

            # 90% base chance to pick multi-key.
            base_chance = 90

            # Lower chance to pick higher complexity keys.
            chance = round(base_chance - (i * 3))

            # Minimum chance of 60%
            if chance < 60:
                chance = 60

            multi = ' '.join(self.values[-i:])
            if randint(1, 100) < chance and (multi != denied_multi or not denying_multi):
                if multi in self.model:
                    # print("key<", multi, "> is in model.")
                    if len(list(self.model[multi].keys())) > 3:
                        # print("90%")
                        chance = 90
                    elif len(list(self.model[multi].keys())) > 1:
                        # print("85%")
                        chance = 80
                    elif len(list(self.model[multi].keys())) == 1 and list(self.model[multi].keys())[0] == self.values[-1]:
                        # print("0%")
                        chance = 0
                    else:
                        # print("45%")
                        chance = 30

                    if randint(1, 100) < chance:
                        key_to_check = multi
                        multi_picked = True
                        if self.debug:
                            print("Picking multi-key(" + str(i) + "):", key_to_check, "> ", end="")
                        break

            elif not denying_multi and randint(1, 100) > 78:
                denying_multi = True
                denied_multi = ' '.join(multi.split()[1:])
                if self.debug:
                    print("Denying multi with:", denied_multi)
            else:
                denied_multi = ' '.join(multi.split()[1:])


        # TODO: Better handling of keys not being in base of model
        try:
            chain = self.model[key_to_check]
        except:
            # Just return a completely random key if key_to_check is not in base of model.
            return np.random.choice(list(self.model.keys()))

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
                if randint(1, 100) > 99:
                    step = np.random.choice(list(self.model.keys()), 1)[0]
                else:
                    step = np.random.choice(keys, 1, p=probabilities)[0]

        if self.debug:
            if not multi_picked:
                print("Picking single-key:", step)
            else:
                print(step)

        return step
