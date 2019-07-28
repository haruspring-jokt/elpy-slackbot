import urllib.request
import os
import json
import logging

# ログ設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def run():
    # 詳細APIのURLを構築する
    memo_id: str = "memo_id"
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
    logging.info(f"res: {content}")

    return


if __name__ == "__main__":
    run()
