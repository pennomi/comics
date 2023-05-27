from typing import List

import requests


def purge_paths(comic, paths: List[str], everything=False):
    # Don't purge paths if we don't have Cloudflare configured
    if not comic.cloudflare_zone or not comic.cloudflare_token:
        return

    # TODO: Don't leave this testing override in!
    comic.domain = "swordscomic.com"

    if everything:
        body = {"purge_everything": True}
    else:
        body = {"files": [f"https://{comic.domain}{p}" for p in paths]}

    url = f"https://api.cloudflare.com/client/v4/zones/{comic.cloudflare_zone}/purge_cache"
    headers = {
        "Authorization": f"Bearer {comic.cloudflare_token}",
        "Content-Type": "application/json",
    }
    response = requests.post(url, json=body, headers=headers).json()
    if not response["success"]:
        raise Exception(response["errors"][0]["message"])


def build_resize_url(path: str, width: int) -> str:
    return f"/cdn-cgi/image/width={width},format=auto{path}"
