import urllib.request
import os
import json
import logging

# ログ設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def run():
    # 詳細APIのURLを構築する
    memo_id: str = os.environ["DOCBASE_MEMO_ID"]
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

    # 公開範囲が全員または準じるグループではない場合終了する
    # 限定グループの場合はPublicチャンネルに表示してはいけないため
    if content["scope"] != "everyone" and content['groups'][0]['name'] != os.environ["DOCBASE_ALL_USER_GROUP"]:
        logging.warning(f"private memo isn't able to be opened!")
        return

    # Block kitのガラを用意する
    skeleton = open("./block_detail_skeleton.json", "r")
    block = json.load(skeleton)

    # ガラに取ってきた情報を詰める
    # title
    block[0]["text"]["text"] = f"*<{content['url']}|{content['title']}>*"

    # group
    if content["scope"] == "everyone":
        block[1]["fields"][0]["text"] = f"*group:*\n全員"
    else:
        block[1]["fields"][0]["text"] = f"*group:*\n{content['groups'][0]['name']}"

    # tags
    tags = ""
    for i, tag in enumerate(content["tags"]):
        tags += content["tags"][i]["name"] + ", "
        if i == len(content["tags"]) - 1:
            tags = tags[:-2]
    block[1]["fields"][1]["text"] = f"*Tags:*\n{tags}"

    # created at
    created_at = content["created_at"][0:10] + \
        " " + content["created_at"][11:16]
    block[1]["fields"][2]["text"] = f"*Created at:*\n{created_at}"

    # author
    block[1]["fields"][3]["text"] = f"*Author:*\n{content['user']['name']}"

    # overview
    if len(content["body"]) <= 200:
        block[2]["text"]["text"] = f"*Overview:*\n{content['body']}"
    else:
        block[2]["text"]["text"] = f"*Overview:*\n{content['body'][:200]}..."

    logging.info(f"block: \n{block}")

    # Slackに投稿する
    post_url = "https://slack.com/api/chat.postMessage"

    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Authorization": f"Bearer {os.environ['SLACK_BOT_USER_ACCESS_TOKEN']}"
    }

    data = {
        "token": os.environ["SLACK_BOT_TOKEN"],
        "channel": "sandbox",
        "blocks": block,
        "username": os.environ["BOT_NAME"]
    }

    req = urllib.request.Request(
        post_url,
        data=json.dumps(data).encode("utf-8"),
        method="POST",
        headers=headers
    )

    # res = urllib.request.urlopen(req)

    return


if __name__ == "__main__":
    run()
