# -*- coding: utf-8 -*-
import os
import json
import logging
import urllib.request
import urllib.parse


# ログ設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: dict, context) -> str:
    """
    メインメソッド
    """

    # デコード前のログ
    logging.info(f"request: {json.dumps(event)}")

    # トークンで認証
    if not is_authorized(event["token"]):
        logging.warning("invalid request token!")
        return "403 Authentication Error"

    decoded = decode_event(event)
    logging.info(f"decoded: {json.dumps(decoded)}")

    # コマンドからディスパッチ先を決める
    if decoded["command"] == "/docbase-detail":
        memo_id = decoded["text"][-6:]
        channel_id = decoded["channel_id"]
        return post_docbase_detail(memo_id, channel_id)

    if decoded["command"] == "/elpy":
        return "200 health check OK."

    return "404 there is no command you ordered."


def post_docbase_detail(memo_id: str, channel_id: str) -> str:
    """
    docbaseメモの概要を投稿する。
    メモの公開範囲が全体または"*****_***"以外の場合は、プライベートグループの
    メモであるため投稿せずに終了する。
    """

    content = fetch_docbail_detail(memo_id)

    # 公開範囲が全員または準じるグループではない場合終了する
    # 限定グループの場合はPublicチャンネルに表示してはいけないため
    if is_private_memo(content):
        logging.warning(f"private memo isn't able to be opened!")
        return "403 private memo isn't able to be opened."

    blocks = build_docbase_detail_block(content)
    status = post_slack_with_blocks(blocks, channel_id)
    return status


def fetch_docbail_detail(memo_id: str) -> dict:
    """
    DocBase APIを使ってメモ情報を取得する。
    """
    domain: str = os.environ["DOCBASE_DOMAIN"]
    url: str = f"https://api.docbase.io/teams/{domain}/posts/{memo_id}"

    # APIトークンをヘッダーに設定する
    token = os.environ["DOCBASE_API_TOKEN"]
    headers = {
        "X-DocBaseToken": f"{token}",
    }

    req = urllib.request.Request(url, headers=headers)
    res = urllib.request.urlopen(req)

    content = json.loads(res.read().decode('utf8'))
    return content


def is_private_memo(content):
    """
    DocBaseのメモがプライベートグループへ公開されたものの場合Trueを返す。
    """
    if content["scope"] != "everyone" \
            and content['groups'][0]['name'] != os.environ["DOCBASE_ALL_USER_GROUP"]:
        return True
    return False


def build_docbase_detail_block(content) -> dict:
    """
    DocBase詳細表示用のBlock kitを作成する。
    `block_detail_skeleton.json`からガラを取得し、そこにそれぞれ値を埋め込む。
    """

    skeleton = open("./block_detail_skeleton.json", "r")
    block = json.load(skeleton)

    block[0]["text"]["text"] = f"*<{content['url']}|{content['title']}>*"

    # tagsは複数あるため、カンマで区切って挿入する。
    tags = ""
    for i, tag in enumerate(content["tags"]):
        tags += content["tags"][i]["name"] + ", "
        if i == len(content["tags"]) - 1:
            tags = tags[:-2]
    block[1]["fields"][0]["text"] = f"*Tags:*\n{tags}"

    created_at = content["created_at"][0:10] + \
        " " + content["created_at"][11:16]
    block[1]["fields"][1]["text"] = f"*Created at:*\n{created_at}"
    block[1]["fields"][2]["text"] = f"*Author:*\n{content['user']['name']}"
    block[1]["fields"][3]["text"] = f"*Comment:*\n{len(content['comments'])}"
    block[1]["fields"][4]["text"] = f"*Good jobs:*\n{content['good_jobs_count']}"
    block[1]["fields"][5]["text"] = f"*Stars count:*\n{content['stars_count']}"

    # Overview（概要）は長い場合省略する
    if len(content["body"]) <= 200:
        block[2]["text"]["text"] = f"*Overview:*\n{content['body']}"
    else:
        block[2]["text"]["text"] = f"*Overview:*\n{content['body'][:200]}..."

    logging.info(f"block: {json.dumps(block)}")
    return block


def post_slack_with_blocks(blocks, channel_id):
    """
    block kitを使ってSlackに投稿する。
    """
    post_url = "https://slack.com/api/chat.postMessage"

    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Authorization": f"Bearer {os.environ['SLACK_BOT_USER_ACCESS_TOKEN']}"
    }

    data = {
        "token": os.environ["SLACK_BOT_TOKEN"],
        "channel": channel_id,
        "blocks": blocks,
        "username": os.environ["BOT_NAME"]
    }

    req = urllib.request.Request(
        post_url,
        data=json.dumps(data).encode("utf-8"),
        method="POST",
        headers=headers
    )

    res = urllib.request.urlopen(req)
    return res.status


def is_authorized(request_token: str) -> bool:
    """
    リクエストに含まれるtokenとLambdaのtokenを照合し、一致している場合はTrueを返す。
    """
    return os.environ["SLACK_BOT_TOKEN"] == request_token


def decode_event(event: dict) -> dict:
    """
    URLエンコードされているリクエストをデコードして辞書型に格納して返す。
    `urllib.parse.unquote(str)`メソッドを使用する場合、
    半角スペースは"+"に変換されるので、テキストの変換のみ
    urllib.parse.unquote_plus(str)`を使用して"+"が残らないようにする。
    """
    decoded_event = {}
    decoded_event["token"] = urllib.parse.unquote(event["token"])
    decoded_event["team_id"] = urllib.parse.unquote(event["team_id"])
    decoded_event["team_domain"] = urllib.parse.unquote(event["team_domain"])
    decoded_event["channel_id"] = urllib.parse.unquote(event["channel_id"])
    decoded_event["channel_name"] = urllib.parse.unquote(event["channel_name"])
    decoded_event["user_id"] = urllib.parse.unquote(event["user_id"])
    decoded_event["user_name"] = urllib.parse.unquote(event["user_name"])
    decoded_event["command"] = urllib.parse.unquote(event["command"])
    decoded_event["text"] = urllib.parse.unquote_plus(event["text"])
    decoded_event["response_url"] = urllib.parse.unquote(event["response_url"])
    decoded_event["trigger_id"] = urllib.parse.unquote(event["trigger_id"])

    return decoded_event


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
        "token": os.environ["SLACK_BOT_TOKEN"],
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

    res = urllib.request.urlopen(req)
    return
