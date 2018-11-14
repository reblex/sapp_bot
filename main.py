#!/usr/bin/env python3
""" Main interface """

import sys
from random import randint

from src.twitter_bot import TwitterBot
from src.wiki_scraper import WikiScraper
from src.sentence import Sentence
from src.chain import Chain

HELP_STRING = ("\nTweets sentences generated by markov chains,\n"
               "using minervawikin.nu as learning material.\n\n"
               "Usage: sapp_bot <command> [arguments]...\n\n"
               "Commands:\n"
               "  help                   Print this helpful information.\n"
               "  run                    Run the bot.\n"
               "  print  [count]         Print generated sentences *count* times (default 1).\n"
               "  update [recent|all]    Update all or recent corpus pages (default recent).\n"
              )

USAGE = "Usage: sapp_bot <command> [arguments]..."

VERSION = "0.9.0"

def main():
    """Main function"""
    args = sys.argv[1:]

    if len(args) == 0:
        print("Please select command")
        sys.exit(1)

    if args[0] == 'help':
        print(HELP_STRING)

    elif args[0] == 'print':
        opts = args[1:]
        count = 1

        if len(opts) == 1:
            if opts[0].isdigit():
                count = opts[0]
            else:
                print("Print count must be integer!")
                print(USAGE)
                sys.exit(1)


        # TODO: seond option = first_word

        chain = Chain("corpus")
        chain.build_model()

        for _ in range(int(count)):
            try:
                sentence = Sentence(chain, randint(180, 260))
                sentence.generate()
                print(str(sentence) + "\n")
            except Exception as e:
                print("Error:", str(e))

    elif args[0] == 'update':
        opts = args[1:]
        all = False
        if len(opts) == 1:
            if opts[0] == 'all':
                all = True

        ws = WikiScraper()
        if all:
            ws.update_all_pages()
        else:
            ws.update_recent_changes()

    elif args[0] == 'run':
        bot = TwitterBot("bot_config.json")
        bot.run()

    else:
        print("Invalid command: " + args[0])
        print(USAGE)
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
