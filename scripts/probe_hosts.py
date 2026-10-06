"""Probe public CloudShift hostnames to pick a health path and accepted status codes per monitor.

Usage: python scripts/probe_hosts.py hosts.txt > probe.json
"""

import json
import ssl
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

PATHS = ["/", "/health", "/api/health", "/api/v1/health", "/healthz", "/minio/health/live"]
CTX = ssl.create_default_context()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


OPENER = urllib.request.build_opener(NoRedirect, urllib.request.HTTPSHandler(context=CTX))


def fetch(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "cloudshift-uptime-probe"})
    try:
        with OPENER.open(req, timeout=10) as resp:
            body = resp.read(300).decode("utf-8", "replace")
            return {"status": resp.status, "type": resp.headers.get("content-type", ""), "body": body[:120]}
    except urllib.error.HTTPError as err:
        return {"status": err.code, "type": err.headers.get("content-type", ""), "location": err.headers.get("location")}
    except Exception as err:  # noqa: BLE001 - probe records every failure mode
        return {"status": None, "error": f"{type(err).__name__}: {err}"[:160]}


def probe(host: str) -> dict:
    return {"host": host, "paths": {p: fetch(f"https://{host}{p}") for p in PATHS}}


def main() -> None:
    hosts = [h.strip() for h in open(sys.argv[1], encoding="utf-8") if h.strip()]
    with ThreadPoolExecutor(max_workers=12) as pool:
        results = list(pool.map(probe, hosts))
    json.dump(results, sys.stdout, indent=1)


if __name__ == "__main__":
    main()
