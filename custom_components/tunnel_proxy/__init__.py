# custom_components/tunnel_proxy/__init__.py

import json
import logging
import os
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .token_manager import async_generate_token_and_notify
from .utils import start_tcp_tunnel
from .views import PingTunnelsView, RebootView, TunnelCreateView

_LOGGER = logging.getLogger(__name__)
DOMAIN = "tunnel_proxy"


def _load_saved_tunnels(tunnels_path):
    if not os.path.exists(tunnels_path):
        return []
    try:
        if os.path.getsize(tunnels_path) == 0:
            return []
        with open(tunnels_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        _LOGGER.warning("tunnels.json vuoto o corrotto, resetto lista tunnel")
        return []
    except Exception as e:
        _LOGGER.error(f"Errore caricando tunnel: {e}")
        return []


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup dell'integrazione e registrazione degli endpoint."""
    name = entry.data["name"]
    url = entry.data["url"]
    device_id = entry.data["id"]

    await async_generate_token_and_notify(hass, name, url, device_id)

    hass.http.register_view(TunnelCreateView(hass))
    hass.http.register_view(RebootView)
    hass.http.register_view(PingTunnelsView)

    tunnels_path = hass.config.path("tunnels.json")
    tunnels = await hass.async_add_executor_job(_load_saved_tunnels, tunnels_path)
    for t in tunnels:
        if not isinstance(t, dict):
            continue
        start_tcp_tunnel(
            t.get("local_port"),
            t.get("target_ip"),
            t.get("target_port"),
        )
        _LOGGER.info(
            "Tunnel ripristinato: %s -> %s:%s",
            t.get("local_port"),
            t.get("target_ip"),
            t.get("target_port"),
        )

    hass.async_create_task(hass.config_entries.async_forward_entry_setups(entry, ["sensor"]))

    return True
