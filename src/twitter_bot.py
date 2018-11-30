#!/usr/bin/env python3
""" Twitter Bot """

from random import randint
import time
import json
import sys
import schedule
from twython import Twython

from src.chain import Chain
from src.wiki_scraper import WikiScraper
from src.sentence import Sentence
import src.base as base

# TODO: Read "Desired Subject" from file and set first_word in chain.

class TwitterBot():
    """Bot for posting on Twitter"""
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = None
        self._configure()

        schedule.every().day.at(self.config["update_corpus_time"]).do(self._update_corpus)
        schedule.every().sunday.at(self.config["update_users_time"]).do(self._update_users)
        schedule.every().day.at(self.config["post_time"]).do(self._post)


    def run(self):
        """Main loop"""
        base.prompt_print("Bot started.")
        while True:
            try:
                schedule.run_pending()
            except BaseException as exception:
                base.prompt_print("Error in twitter_bot.run run_pending: " + str(exception))

            try:
                time.sleep(1)
            except KeyboardInterrupt:
                print("Manually shut down. Bye!")
                sys.exit(0)


    def _post(self):
        """Post a generated sentence to Twitter."""
        # Instantiate and generate the Markov chain.
        base.prompt_print("Posting to Twitter...")
        completed = False
        while not completed:
            try:
                chain = Chain("corpus")
                chain.build_model()
                completed = True
            except:
                raise


        # Instantiate and generate a sentence.
        completed = False
        while not completed:
            try:
                sentence = Sentence(chain, randint(180, 260))
                sentence.generate()
                completed = True
            except:
                raise

        # Get twitter authentication.
        APP_KEY = self.config['twitter_auth_key']
        APP_SECRET = self.config['twitter_auth_secret']
        OAUTH_TOKEN = self.config['twitter_oauth_token']
        OAUTH_TOKEN_SECRET = self.config['twitter_oauth_token_secret']

        # Instantiate Twython object and post to Twitter.
        completed = False
        while not completed:
            try:
                twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
                twitter.update_status(status=str(sentence))
                completed = True
            except:
                raise

        base.prompt_print("Succesfully posted to Twitter!")


    def _update_corpus(self, all_pages=False):
        """Update Minervawiki-corpus"""
        ws = WikiScraper()
        if all_pages:
            completed = False
            while not completed:
                try:
                    base.prompt_print("Updating corpus from all pages...")
                    ws.update_all_pages()
                    completed = True
                except:
                    raise
        else:
            completed = False
            while not completed:
                try:
                    base.prompt_print("Updating corpus from latest edits...")
                    ws.update_recent_changes()
                    completed = True
                except:
                    raise

        base.prompt_print("Finished updating corpus!")

    def _update_users(self):
        """Update Minervawiki users"""
        ws = WikiScraper()
        completed = False
        while not completed:
            try:
                base.prompt_print("Updating users...")
                ws.update_users()
                completed = True
            except:
                raise

        base.prompt_print("Finished updating users!")


    def _configure(self):
        """Read configurations from file"""
        with open(self.config_file) as file:
            self.config = json.load(file)
