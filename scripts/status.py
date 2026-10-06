"""Print the latest status of every Uptime Kuma monitor, grouped. Uses the same env as provision_monitors.py."""

import os

from uptime_kuma_api import UptimeKumaApi

STATUS = {0: "DOWN", 1: "UP", 2: "PENDING", 3: "MAINT"}


def flatten(items: list) -> list:
    out = []
    for item in items or []:
        out.extend(flatten(item) if isinstance(item, list) else [item])
    return out


def main() -> None:
    api = UptimeKumaApi(os.environ["KUMA_URL"], timeout=60)
    api.login(os.environ["KUMA_USER"], os.environ["KUMA_PASS"])
    monitors = api.get_monitors()
    beats = api.get_heartbeats()
    names = {m["id"]: m["name"] for m in monitors}

    rows = []
    for m in monitors:
        if m["type"] == "group":
            continue
        latest = max(flatten(beats.get(m["id"])), key=lambda b: b.get("time", ""), default={})
        status = STATUS.get(getattr(latest.get("status"), "value", latest.get("status")), "NO DATA")
        rows.append((names.get(m["parent"], "-"), status, m["name"], (latest.get("msg") or "")[:70]))

    for group, status, name, msg in sorted(rows, key=lambda r: (r[0], r[1] != "DOWN", r[2])):
        print(f"{group:<15} {status:<8} {name:<42} {msg}")
    up = sum(1 for r in rows if r[1] == "UP")
    print(f"\n{up}/{len(rows)} up")
    api.disconnect()


if __name__ == "__main__":
    main()
