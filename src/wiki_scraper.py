#!/usr/bin/env python3
""" Wiki scraper """

import sys
import json
import os
import re
import time
import requests

import src.base as base


class WikiScraper():
    """Web Scraper for minervawikin.nu"""
    def __init__(self):
        self.base_url = "https://minervawikin.nu"
        self.pages = list()
        self.corpus_folder = "corpus_test"
        self.corpus_path = "corpus_test"

    def build_corpus(self):
        """Build corpus files"""
        i = 0
        for page_title in self.pages:
            url = self.base_url + "/wiki/" + page_title
            res = self.get_url(url)

            regex = r"<p>(.*)<\/p>"

            content = re.search(regex, res.text, re.DOTALL)
            if content:
                content = content.group(0)[:-1]
            else:
                content = ""

            # Remove HTML tags
            clean = re.compile('<.*?>')
            content = re.sub(clean, '', content)
            content = re.sub("</p", '', content)

            if not os.path.exists(self.corpus_path):
                os.makedirs(self.corpus_path)

            # Strip slashes from page_title and set as file_name.
            # Then build file_path.
            file_name = re.sub(r"[\/]", '_', page_title)
            file_path = self.corpus_path + "/" + file_name + ".txt"

            with open(file_path, "w") as file:
                file.write(content)

            base.prompt_print(str(i))
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
