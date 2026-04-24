# custom_components/tunnel_proxy/sensor.py

import json
import logging
import os
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)
DOMAIN = "tunnel_proxy"


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


async def async_setup_entry(hass, entry, async_add_entities):
    token_path = hass.config.path("server_tokens.json")
    name = entry.data["name"]
    url = entry.data["url"]

    entity = TunnelTokenSensor(token_path, name, url)
    async_add_entities([entity], update_before_add=True)


class TunnelTokenSensor(Entity):
    def __init__(self, token_path, name, url):
        self._token_path = token_path
        self._name = name
        self._url = url
        self._state = None

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
        }

    @property
    def name(self):
        return f"Tunnel Token {self._name}"

    @property
    def state(self):
        return self._state

    async def async_update(self):
        try:
            self._state = await self.hass.async_add_executor_job(
                _load_sensor_token,
                self._token_path,
                self._name,
                self._url,
            )
        except Exception as e:
            _LOGGER.error(f"Errore caricando token: {e}")
            self._state = None
