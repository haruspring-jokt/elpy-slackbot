# -*- coding: utf-8 -*-
import os
import json
import logging
import urllib.request
from sender import messenger


def post(slack_event: dict):
    """
    チャンネル作成イベントの通知
    """
    channel_name = slack_event.get("event").get("channel").get("name")

    messenger.post_message(f"新しいチャンネルが作成されました: #{channel_name}",
                           os.environ["DIST_CHANNEL_CH_CREATED"])

    return
