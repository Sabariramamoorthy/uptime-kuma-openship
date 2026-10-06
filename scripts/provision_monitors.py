"""Create the CloudShift monitor set in Uptime Kuma. Safe to re-run: existing monitors (by name) are skipped.

Env:
  KUMA_URL   e.g. https://uptime.app.cloudshiftsolutions.in
  KUMA_USER  admin username (created on first run if Kuma is not set up yet)
  KUMA_PASS  admin password

Usage: pip install uptime-kuma-api2 && python scripts/provision_monitors.py
"""

import os
import sys

from uptime_kuma_api import MonitorType, UptimeKumaApi

VPS_IP = "162.55.47.255"
OK_2XX = ["200-299"]
# The service answered (even 404 on a bare API root); 5xx / timeouts from Caddy mean the upstream is down.
OK_RESPONDING = ["200-299", "300-399", "400-499"]

WEBSITES = [
    ("Dashboard", "dashboard.app.cloudshiftsolutions.in", "/", OK_2XX),
    ("Face Mark", "facemark.app.cloudshiftsolutions.in", "/", OK_2XX),
    ("RepairFlow", "repairflow.app.cloudshiftsolutions.in", "/", OK_2XX),
    ("RepairFlow Bug-Fix", "bugfix.repairflow.app.cloudshiftsolutions.in", "/", OK_2XX),
    ("NFC Admin", "nfc.app.cloudshiftsolutions.in", "/", OK_2XX),
    ("NFC-QR", "nfc-qr.app.cloudshiftsolutions.in", "/", OK_2XX),
    ("OCR Invoices", "ocr.app.cloudshiftsolutions.in", "/", OK_2XX),
    ("CPPAS Exam App", "cppas-exam.app.cloudshiftsolutions.in", "/", OK_2XX),
    ("CPPAS Admin Dashboard", "cppas-admin.app.cloudshiftsolutions.in", "/", OK_2XX),
    ("Kitchen R&D", "kitchen.app.cloudshiftsolutions.in", "/", OK_2XX),
    ("CloudShift Hub", "hub.app.cloudshiftsolutions.in", "/", OK_2XX),
    ("DB-GPT", "dbgpt.app.cloudshiftsolutions.in", "/", OK_2XX),
    ("Registration", "registration.app.cloudshiftsolutions.in", "/", OK_2XX),
    ("POS", "pos.cloudshiftsolutions.in", "/", OK_2XX),
    ("KAAPI", "kaapi.cloudshiftsolutions.in", "/", OK_2XX),
    ("Plane", "plane.cloudshiftsolutions.in", "/", OK_2XX),
    ("MinIO Console", "storage.app.cloudshiftsolutions.in", "/", OK_2XX),
    ("Jellyfin", "jellyfin.app.cloudshiftsolutions.in", "/", OK_2XX),
    ("Webmail", "webmail.cloudshiftsolutions.in", "/", OK_2XX),
    ("Openship", "openship.app.cloudshiftsolutions.in", "/", OK_2XX),
    ("WA-AKG", "wa-akg.app.cloudshiftsolutions.in", "/", OK_2XX),
    ("Databasement", "databasement.app.cloudshiftsolutions.in", "/", OK_2XX),
    # Caddy basicauth sits in front of Hermes, so 401 is the healthy answer.
    ("Hermes Agent", "hermes.app.cloudshiftsolutions.in", "/", ["401"]),
    ("GeeCee App", "app.geecee.app.cloudshiftsolutions.in", "/", OK_2XX),
    ("GeeCee Command", "command.geecee.app.cloudshiftsolutions.in", "/", OK_2XX),
    ("Document Service Web", "document-service.app.cloudshiftsolutions.in", "/", OK_2XX),
    ("Veloce", "veloce.app.cloudshiftsolutions.in", "/", OK_2XX),
    ("DentalPin", "dentalpin.app.cloudshiftsolutions.in", "/", OK_2XX),
    ("Uptime Kuma (public path)", "uptime.app.cloudshiftsolutions.in", "/", OK_2XX),
]

APIS = [
    ("Dashboard API", "api.dashboard.app.cloudshiftsolutions.in", "/health", OK_2XX),
    ("Face Mark API", "api.facemark.app.cloudshiftsolutions.in", "/", OK_RESPONDING),
    ("RepairFlow API", "api.repairflow.app.cloudshiftsolutions.in", "/", OK_RESPONDING),
    ("NFC Admin API", "api.nfc.app.cloudshiftsolutions.in", "/", OK_RESPONDING),
    ("NFC-QR API", "api.nfc-qr.app.cloudshiftsolutions.in", "/", OK_RESPONDING),
    ("OCR Invoices API", "api.ocr.app.cloudshiftsolutions.in", "/", OK_RESPONDING),
    ("CPPAS Exam API", "api.cppas-exam.app.cloudshiftsolutions.in", "/health", OK_2XX),
    ("Registration API", "api.registration.app.cloudshiftsolutions.in", "/api/health", OK_2XX),
    ("Openship API", "api.openship.app.cloudshiftsolutions.in", "/api/health", OK_2XX),
    ("GeeCee Auth API", "auth.geecee.app.cloudshiftsolutions.in", "/health", OK_2XX),
    ("GeeCee Backend API", "api.geecee.app.cloudshiftsolutions.in", "/health", OK_2XX),
    ("GeeCee Procurement API", "procurement.geecee.app.cloudshiftsolutions.in", "/health", OK_2XX),
    ("Document Service API", "api.document-service.app.cloudshiftsolutions.in", "/api/v1/health", OK_2XX),
    ("MinIO S3 API", "s3.app.cloudshiftsolutions.in", "/minio/health/live", OK_2XX),
    ("Plane MCP Server", "mcp.app.cloudshiftsolutions.in", "/", OK_RESPONDING),
    ("WA-AKG API", "wa-akg.app.cloudshiftsolutions.in", "/api/health", OK_2XX),
    ("Databasement health", "databasement.app.cloudshiftsolutions.in", "/health", OK_2XX),
    ("DentalPin health", "dentalpin.app.cloudshiftsolutions.in", "/health", OK_2XX),
]

TCP = [
    ("Hetzner VPS - HTTPS 443", VPS_IP, 443),
    ("Hetzner VPS - HTTP 80", VPS_IP, 80),
    ("Hetzner VPS - SSH 22", VPS_IP, 22),
    ("Homelab Openship edge - 80 (LAN)", "192.168.1.102", 80),
    ("Homelab Openship edge - 80 (Tailscale)", "100.82.11.127", 80),
    ("Homelab - SSH 22 (LAN)", "192.168.1.102", 22),
    ("Apps server - SSH 22 (LAN)", "192.168.1.150", 22),
    ("Apps server - HTTP 80 (LAN)", "192.168.1.150", 80),
]

PING = [
    ("Router 192.168.1.1", "192.168.1.1"),
    ("Homelab 192.168.1.102", "192.168.1.102"),
    ("Apps server 192.168.1.150", "192.168.1.150"),
    ("Hetzner VPS", VPS_IP),
]

# (name, hostname, record type, value the answer must contain)
DNS = [
    ("DNS - *.app wildcard -> VPS", "kuma-wildcard-check.app.cloudshiftsolutions.in", "A", VPS_IP),
    ("DNS - plane -> VPS", "plane.cloudshiftsolutions.in", "A", VPS_IP),
    ("DNS - pos -> VPS", "pos.cloudshiftsolutions.in", "A", VPS_IP),
    ("DNS - webmail -> VPS", "webmail.cloudshiftsolutions.in", "A", VPS_IP),
    ("DNS - NS on Vercel", "cloudshiftsolutions.in", "NS", "vercel-dns.com"),
    ("DNS - MX on Google", "cloudshiftsolutions.in", "MX", "smtp.google.com"),
]


def contains(value: str) -> list:
    return [{"type": "expression", "andOr": "and", "variable": "record", "operator": "contains", "value": value}]


def main() -> None:
    url, user, password = (os.environ.get(k) for k in ("KUMA_URL", "KUMA_USER", "KUMA_PASS"))
    if not (url and user and password):
        sys.exit("Set KUMA_URL, KUMA_USER and KUMA_PASS.")

    api = UptimeKumaApi(url, timeout=60)
    if api.need_setup():
        api.setup(user, password)
        print(f"created admin user {user}")
    api.login(user, password)

    existing = {m["name"]: m["id"] for m in api.get_monitors()}
    created = 0

    def ensure(name: str, **kwargs) -> int:
        nonlocal created
        if name in existing:
            return existing[name]
        monitor_id = api.add_monitor(name=name, **kwargs)["monitorID"]
        existing[name] = monitor_id
        created += 1
        print(f"+ {name}")
        return monitor_id

    def group(name: str) -> int:
        return ensure(name, type=MonitorType.GROUP)

    http_common = {"type": MonitorType.HTTP, "interval": 60, "retryInterval": 30, "maxretries": 2,
                   "expiryNotification": True, "timeout": 30}

    websites = group("Websites")
    for name, host, path, codes in WEBSITES:
        ensure(name, parent=websites, url=f"https://{host}{path}", accepted_statuscodes=codes, **http_common)

    apis = group("APIs")
    for name, host, path, codes in APIS:
        ensure(name, parent=apis, url=f"https://{host}{path}", accepted_statuscodes=codes, **http_common)

    infra = group("Infrastructure")
    for name, host, port in TCP:
        ensure(name, parent=infra, type=MonitorType.PORT, hostname=host, port=port,
               interval=60, retryInterval=30, maxretries=2)
    for name, host in PING:
        ensure(name, parent=infra, type=MonitorType.PING, hostname=host, interval=60, retryInterval=30, maxretries=2)

    dns = group("DNS")
    for name, host, rtype, expected in DNS:
        ensure(name, parent=dns, type=MonitorType.DNS, hostname=host, dns_resolve_type=rtype,
               dns_resolve_server="1.1.1.1", port=53, conditions=contains(expected),
               interval=300, retryInterval=60, maxretries=2)

    ensure("Domain - cloudshiftsolutions.in", parent=dns, type=MonitorType.HTTP,
           url="https://plane.cloudshiftsolutions.in/", accepted_statuscodes=OK_2XX,
           domainExpiryNotification=True, expiryNotification=True, interval=3600, maxretries=1)

    api.disconnect()
    print(f"done: {created} created, {len(existing)} total")


if __name__ == "__main__":
    main()
