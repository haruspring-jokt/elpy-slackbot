# -*- coding: utf-8 -*-
import os
import json
import logging
import urllib.request
from sender import messenger


# ログ設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def post(slack_event: dict):
    """
    チャンネル作成イベントの通知
    """

    channel_id = slack_event.get("event").get("channel")

    strip_str = f"<@{os.environ['BOT_ID']}>"
    text = slack_event.get("event").get("text").strip(strip_str)
    logging.info(f"{text}")

    messenger.post_message(f"you said: {text}",
                           channel_id)

    return
