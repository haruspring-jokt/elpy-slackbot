# -*- coding: utf-8 -*-
import os
import json
import logging
import urllib.request


def post_message(message: str, channel: str, link_names="true"):
    """
    Slackのchat.postMessage APIを利用して投稿する
    """

    url = "https://slack.com/api/chat.postMessage"

    # ヘッダーにはコンテンツタイプとボット認証トークンを付与する
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Authorization": "Bearer {0}".format(os.environ["SLACK_BOT_USER_ACCESS_TOKEN"])
    }

    # "link_name: true"によって#や@のリンク化を有効化
    data = {
        "token": os.environ["SLACK_APP_AUTH_TOKEN"],
        "channel": channel,
        "text": message,
        "username": os.environ["BOT_NAME"],
        "link_names": link_names
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        method="POST",
        headers=headers
    )

    urllib.request.urlopen(req)
    return
