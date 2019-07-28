# -*- coding: utf-8 -*-
import os
import json
import logging
from sender import ch_created_service
from sender import emoji_added_service
from sender import app_mention_service


# ログ設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def dispatch(slack_event: dict):
    """
    発火したイベントの種類を判断し処理を開始させる
    """

    event_type = slack_event.get("event").get("type")
    subtype = slack_event.get("event").get("subtype")

    if is_channel_created_event(event_type):
        logging.info("detected ch_created event.")
        ch_created_service.post(slack_event)

    if is_emoji_added_event(event_type, subtype):
        logging.info("detected emoji_added event.")
        emoji_added_service.post(slack_event)

    if is_app_mention_event(event_type):
        logging.info("detected app_mention event.")
        app_mention_service.post(slack_event)

    return


def is_channel_created_event(event_type: str) -> bool:
    """
    新規チャンネル作成イベントの場合はTrue
    """
    return event_type == "channel_created"


def is_emoji_added_event(event_type: str, subtype: str) -> bool:
    """
    emoji追加イベントの場合はTrue
    """
    return event_type == "emoji_changed" and subtype == "add"


def is_app_mention_event(event_type: str) -> bool:
    """
    Botがメンションされている場合はTrue
    """
    return event_type == "app_mention"
