# -*- coding: utf-8 -*-
import os
import json
import logging
import urllib.request
from auth import auth_checker
from controller import event_dispatcher


# ログ設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handle_slack_event(slack_event: dict, context) -> str:
    """
    メインメソッド
    """

    logging.info(json.dumps(slack_event))

    if auth_checker.is_authorized(slack_event):
        return slack_event.get("challenge")

    if auth_checker.is_bot(slack_event.get("event").get("subtype")):
        return "OK"

    event_dispatcher.dispatch(slack_event)

    return "OK"
