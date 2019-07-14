# -*- coding: utf-8 -*-
import os
import json
import logging
import urllib.request
from sender import messenger


def post(slack_event: dict):
    """
    emoji追加イベントの通知
    """

    emoji_name = slack_event.get("event").get("name")

    messenger.post_message(
        f"emojiが追加されました! :{emoji_name}: `{emoji_name}`",
        os.environ["DIST_CHANNEL_EMOJI_ADDED"])

    return
