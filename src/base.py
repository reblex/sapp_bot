#!/usr/bin/env python3
"""
General helper functions
"""

from datetime import datetime


def prompt_print(text):
    """Wrapper function to print with prepended current time"""
    now = datetime.now()
    prompt = '[{}/{}/{} - {:02}:{:02}:{:02}] '.format(now.day, now.month, now.year, now.hour, now.minute, now.second)
    print(prompt + text)
