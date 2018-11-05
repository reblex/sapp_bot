#!/usr/bin/env python3
""" Wiki Scraper """

import sys
import json
import os
import re
import time
import requests
from datetime import datetime, timedelta

import src.base as base


class WikiScraper():
    """Web Scraper for minervawikin.nu"""
    def __init__(self):
        self.base_url = "https://minervawikin.nu"
        self.pages = list()
        self.corpus_folder = "corpus"
        self.corpus_path = "corpus"

    def build_corpus(self):
        """Build corpus files"""
        # TODO: Find out why some words have  spaces in them (start of sentence)

        i = 0
        for page_title in self.pages:
            base.prompt_print("Fetching page: " + page_title)
            url = self.base_url + "/wiki/" + page_title
            res = self.get_url(url)

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

    def set_page_list(self):
        """Get list of pages available on the wiki"""
        end_of_categories = False
        continue_param = ""

        while not end_of_categories:
            url = self.base_url + "/api.php?action=query&list=allpages&aplimit=500&format=json" + continue_param
            res = self.get_url(url)
            # TODO: Check for None result.

            json_data = json.loads(res.text)
            for page in json_data["query"]["allpages"]:
                self.pages.append(page["title"])

            if "continue" in json_data:
                continue_param = "&apfrom=" + json_data["continue"]["apcontinue"]
            else:
                end_of_categories = True

    def update_recent_changes(self):
        """Update pages that have been edited/created yesterday"""
        end_of_updates = False
        continue_param = ""

        while not end_of_updates:
            self.pages = list()
            url = self.base_url + "/api.php?action=query&list=recentchanges&rcprop=title|timestamp&rclimit=50&format=json" + continue_param
            res = self.get_url(url)
            # TODO: Check for None result.

            json_data = json.loads(res.text)
            post_day = None
            yesterday = datetime.today() - timedelta(1)
            yesterday = yesterday.day
            for page in json_data["query"]["recentchanges"]:
                post_day = datetime.strptime(page["timestamp"][:10], '%Y-%m-%d').day
                if post_day == yesterday and page["title"] not in self.pages:
                    self.pages.append(page["title"])

            if post_day == yesterday:
                continue_param = "&rcstart=" + json_data["continue"]["rccontinue"]
            else:
                end_of_updates = True

        self.build_corpus()

    def get_url(self, url):
        """General GET request"""
        res = None

        try:
            res = requests.get(url, headers={'User-Agent': 'knutte-bot'})

        except KeyboardInterrupt:
            self.prompt_print("The program was manually interrupted, bye!")
            self.log_message("Manual Shut Down.", "log/general.log");
            sys.exit(0)

        except BaseException as e:
            message = "Exception in get_html: " + str(e)
            base.prompt_print(message)

        if res is not None:
            # TODO: Send notification on 404. Site down? other codes?
            if res.status_code != 200:
                res = None

        return res
