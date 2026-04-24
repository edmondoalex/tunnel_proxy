# custom_components/tunnel_proxy/sensor.py

import json
import logging
import os
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)
DOMAIN = "tunnel_proxy"


def _load_integration_version():
    manifest_path = os.path.join(os.path.dirname(__file__), "manifest.json")
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        return manifest.get("version", "unknown")
    except Exception:
        return "unknown"


def _load_sensor_token(token_path, entry_name, entry_url):
    if not os.path.exists(token_path):
        return None
    try:
        with open(token_path, "r", encoding="utf-8") as f:
            tokens = json.load(f)
    except Exception:
        return None

    if not isinstance(tokens, list):
        return None

    for item in tokens:
        if not isinstance(item, dict):
            continue
        if item.get("name") == entry_name and item.get("url") == entry_url:
            return item.get("token")

    # Retrocompatibilita: vecchio formato [{"token": "..."}]
    for item in tokens:
        if isinstance(item, dict) and item.get("token"):
            return item.get("token")

    return None


def _load_tunnels(tunnels_path):
    if not os.path.exists(tunnels_path):
        return []
    try:
        with open(tunnels_path, "r", encoding="utf-8") as f:
            tunnels = json.load(f)
    except Exception:
        return []

    if not isinstance(tunnels, list):
        return []

    connected = []
    for tunnel in tunnels:
        if not isinstance(tunnel, dict):
            continue
        ip = tunnel.get("target_ip")
        if not ip:
            continue
        connected.append(
            {
                "target_ip": ip,
                "target_port": tunnel.get("target_port"),
                "local_port": tunnel.get("local_port"),
            }
        )
    return connected


def _load_sensor_payload(token_path, tunnels_path, entry_name, entry_url):
    token = _load_sensor_token(token_path, entry_name, entry_url)
    connected = _load_tunnels(tunnels_path)
    return token, connected


async def async_setup_entry(hass, entry, async_add_entities):
    token_path = hass.config.path("server_tokens.json")
    tunnels_path = hass.config.path("tunnels.json")
    name = entry.data["name"]
    url = entry.data["url"]
    version = await hass.async_add_executor_job(_load_integration_version)

    entity = TunnelTokenSensor(token_path, tunnels_path, name, url, version)
    async_add_entities([entity], update_before_add=True)


class TunnelTokenSensor(Entity):
    def __init__(self, token_path, tunnels_path, name, url, version):
        self._token_path = token_path
        self._tunnels_path = tunnels_path
        self._name = name
        self._url = url
        self._version = version
        self._state = "not_available"
        self._attributes = {
            "integration_version": self._version,
            "connected_devices_count": 0,
            "connected_devices": [],
        }

    @property
    def unique_id(self):
        return f"tunnel_token_{self._name}_{self._url}"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, f"{self._name}_{self._url}")},
            "name": f"Tunnel Proxy {self._name}",
            "manufacturer": "Custom",
            "model": "Tunnel Token",
            "sw_version": self._version,
        }

    @property
    def name(self):
        return f"Tunnel Token {self._name}"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    async def async_update(self):
        try:
            token, connected = await self.hass.async_add_executor_job(
                _load_sensor_payload,
                self._token_path,
                self._tunnels_path,
                self._name,
                self._url,
            )
            self._state = token if token else "not_available"
            self._attributes = {
                "integration_version": self._version,
                "connected_devices_count": len(connected),
                "connected_devices": connected,
            }
        except Exception as e:
            _LOGGER.error(f"Errore caricando token: {e}")
            self._state = "not_available"
            self._attributes = {
                "integration_version": self._version,
                "connected_devices_count": 0,
                "connected_devices": [],
            }
