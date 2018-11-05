#!/usr/bin/env python3
""" Main interface """

from src.twitter_bot import TwitterBot


def main():
    """Main function"""
    bot = TwitterBot("bot_config.json")
    bot.run()

if __name__ == "__main__":
    main()
