#!/usr/bin/env python3
""" Wiki Scraper """

import sys
import json
import os
import re
import time
import requests
import progressbar
from datetime import datetime, timedelta

import src.base as base


class WikiScraper():
    """Web Scraper for minervawikin.nu"""
    def __init__(self):
        self.base_url = "https://minervawikin.nu"
        self.pages = list()
        self.blacklist_file = "blacklist.txt"
        self.blacklist = list()
        self.corpus_folder = "corpus"
        self.corpus_path = "corpus"
        self.word_blacklist = list()
        if os.path.isfile("word_blacklist.txt"):
            with open("word_blacklist.txt", encoding='utf8') as f:
                self.word_blacklist = f.read().split("\n")

        if os.path.isfile(self.blacklist_file):
            with open(self.blacklist_file, encoding='utf8') as f:
                self.blacklist = f.read().split("\n")


    def build_corpus(self):
        """Build corpus files"""
        # TODO: Find out why some words have  spaces in them (start of sentence)
        i = 0

        bar = progressbar.ProgressBar(maxval=len(self.pages), term_width=50, \
        widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        bar.start()
        for page_title in self.pages:
            url = self.base_url + "/wiki/" + page_title
            res = self.get_url(url)
            bar.update(i+1)

            regex = r"<p>(.*?)<\/p>"

            content = re.findall(regex, res.text, re.DOTALL)
            content_text = ""
            if content:
                for j in range(len(content)):
                    content_text += content[j]

                content = ''.join(content_text)
            else:
                content = ""

            # Remove HTML tags
            # clean = re.compile('<.*?>')
            content = re.sub('<.*?>', '', content)
            content = re.sub("</p", '', content)

            # Remove web links
            content = re.sub(r'http\S+', '', content)

            # Remove multiple whitespace?
            content = re.sub(r'\s{2,}', ' ', content).strip()

            # Remove blacklisted words
            for word in self.word_blacklist:
                content = re.sub(word, '', content)

            # Fix "&" tokens
            content = re.sub('&amp;', '&', content)

            if not os.path.exists(self.corpus_path):
                os.makedirs(self.corpus_path)

            # Strip slashes from page_title and set as file_name.
            # Then build file_path.
            file_name = re.sub(r"[\/]", '_', page_title)
            file_path = self.corpus_path + "/" + file_name + ".txt"

            with open(file_path, "w") as file:
                file.write(content)

            if i % 5 == 0:
                time.sleep(0.8)
            i += 1

        bar.finish()

    def update_all_pages(self):
        """Get list of pages available on the wiki"""
        self.pages = list()
        end_of_categories = False
        continue_param = ""

        while not end_of_categories:
            url = self.base_url + "/api.php?action=query&list=allpages&aplimit=500&format=json" + continue_param
            res = self.get_url(url)
            # TODO: Check for None result.

            json_data = json.loads(res.text)
            for page in json_data["query"]["allpages"]:
                # Skip blacklisted pages
                if page["title"] not in self.blacklist:
                    self.pages.append(page["title"])

            if "continue" in json_data:
                continue_param = "&apfrom=" + json_data["continue"]["apcontinue"]
            else:
                end_of_categories = True

        self.build_corpus()

    def update_recent_changes(self):
        """Update pages that have been edited/created yesterday"""
        self.pages = list()
        end_of_updates = False
        continue_param = ""

        while not end_of_updates:
            url = self.base_url + "/api.php?action=query&list=recentchanges&rcprop=title|timestamp&rclimit=50&format=json" + continue_param
            res = self.get_url(url)
            # TODO: Check for None result.
            json_data = res.json()
            post_day = None
            yesterday = datetime.today() - timedelta(1)
            yesterday = yesterday.day

            for page in json_data["query"]["recentchanges"]:
                # Skip blacklisted pages
                if page["title"] not in self.blacklist:
                    self.pages.append(page["title"])

                post_day = datetime.strptime(page["timestamp"][:10], '%Y-%m-%d').day
                if post_day == yesterday and page["title"] not in self.pages:
                    self.pages.append(page["title"])

            if post_day == yesterday:
                continue_param = "&rcstart=" + json_data["continue"]["rccontinue"][:14]
            else:
                end_of_updates = True

        self.build_corpus()

    def get_url(self, url):
        """General GET request"""
        res = None

        try:
            res = requests.get(url, headers={'User-Agent': 'knutte-bot'})

        except KeyboardInterrupt:
            base.prompt_print("The program was manually interrupted, bye!")
            sys.exit(0)

        except BaseException as e:
            message = "Exception in get_html: " + str(e)
            base.prompt_print(message)

        if res is not None:
            # TODO: Send notification on 404. Site down? other codes?
            if res.status_code != 200:
                res = None

        return res
