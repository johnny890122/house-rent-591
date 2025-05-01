import json
import requests
from bs4 import BeautifulSoup

def handler(event, context):
    """
    POST body: { "url": "...", "selector": "css-selector" }
    """
    try:
        body = json.loads(event.get("body") or "{}")
        url = body["url"]
        selector = body.get("selector", "body")
    except (KeyError, json.JSONDecodeError):
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "must include JSON with ‘url’"})
        }

    resp = requests.get(url, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    items = [el.get_text(strip=True) for el in soup.select(selector)]

    return {
        "statusCode": 200,
        "body": json.dumps({"url": url, "selector": selector, "results": items})
    }
