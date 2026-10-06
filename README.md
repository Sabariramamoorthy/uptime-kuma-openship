# Uptime Kuma on Openship

[Uptime Kuma](https://github.com/louislam/uptime-kuma) monitoring for CloudShift, deployed with Openship
to the **Raspbery Pi - Network** server.

- Public URL: https://uptime.app.cloudshiftsolutions.in
- Traffic: Hetzner VPS Caddy → Tailscale → Pi Openship edge → container
- Data: SQLite in the `uptime_kuma_data` volume

## Deploy

Openship reads `openship.json` and deploys `docker-compose.yml` (image only, nothing to build).
Container port `3001`. Pin the image tag in `docker-compose.yml` and redeploy to upgrade.
