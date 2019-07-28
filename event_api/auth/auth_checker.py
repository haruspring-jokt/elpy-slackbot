# -*- coding: utf-8 -*-
import os
import json
import logging


def is_authorized(slack_event: dict) -> bool:
    """
    event jsonの認証を行う。
    """
    if "challenge" in slack_event:
        return True
    else:
        return False


def is_bot(event_subtype: str) -> bool:
    """
    event jsonがbotから出力されたものかを判断する。
    """
    return event_subtype == "bot_message"
