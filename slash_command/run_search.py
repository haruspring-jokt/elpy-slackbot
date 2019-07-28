import urllib.request
import urllib.parse
import os
import json
import logging

# ログ設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def run():

    # 検索ワードをURLを設定
    search = "input search word"
    domain = os.environ["DOCBASE_DOMAIN"]
    url: str = f"https://api.docbase.io/teams/{domain}/posts/?q={search}"

    # urlに日本語がある場合はエンコードする必要があるので、以下を実施
    # https://algorithm.joho.info/programming/python/urllib-request-japanese/
    p = urllib.parse.urlparse(url)
    query = urllib.parse.quote_plus(p.query, safe='=&')
    url = '{}://{}{}{}{}{}{}{}{}'.format(
        p.scheme, p.netloc, p.path,
        ';' if p.params else '', p.params,
        '?' if p.query else '', query,
        '#' if p.fragment else '', p.fragment)

    # APIトークンをヘッダーに付与
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
