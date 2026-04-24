# Tunnel Proxy - Project History

## Project
- Name: `tunnel_proxy`
- Type: Home Assistant custom integration (HACS compatible)
- Domain: `tunnel_proxy`
- Main path: `custom_components/tunnel_proxy/`

## Repository Structure
- `custom_components/tunnel_proxy/`: integration code
- `hacs.json`: HACS metadata
- `LICENSE`
- `logo.png`
- `readme.md`

## Git Timeline (recent)
- `07ca997` - fix version
- `13906ef` - merge from main
- `35c3904` - fix ping and reboot
- `3654ab9` - state scan adjustment
- `b77f965` - minor update
- `b33f226` - minor update
- `78ce02e` - initial commit

## Local Maintenance Notes
- Backup created before repo realignment:
  - `C:\Users\NUC Alex\OneDrive\EA SAS\0000000033-TOOL\HASSIO Custom Component\_backup_tunnel_proxy_local_20260424_114713`
- Local folder was converted into a proper git repository and aligned to `origin/main`.

## Version History (operational)
- `1.5.0`: baseline before async I/O hardening
- `2.0.0`: async-safe file I/O and sensor token-format compatibility improvements

## Changes in 2.0.0
- Avoid blocking file access in async request handlers:
  - token checks in views moved through `hass.async_add_executor_job(...)`
  - tunnel file loading in ping endpoint moved to sync helper executed in executor
  - tunnel persistence call from async endpoint moved to executor
- Restore phase made async-safe:
  - `tunnels.json` loading moved to sync helper executed in executor during setup
- Sensor token load hardened:
  - token file read moved to executor path
  - no direct key access (`item["name"]`) that caused `'name'` errors
  - added fallback for legacy token format `[{ "token": "..." }]`

## Runtime/Data Files
- `/config/server_tokens.json`
- `/config/tunnels.json`

## Known Compatibility Goal
- Keep current behavior stable while removing Home Assistant loop warnings for blocking file operations.
