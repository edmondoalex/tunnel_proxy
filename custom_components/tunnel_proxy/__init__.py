# custom_components/tunnel_proxy/__init__.py

import json
import os
import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .token_manager import async_generate_token_and_notify
from .views import TunnelCreateView, RebootView, PingTunnelsView
from .utils import start_tcp_tunnel

_LOGGER = logging.getLogger(__name__)
DOMAIN = "tunnel_proxy"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup dell'integrazione e registrazione degli endpoint."""
    name = entry.data["name"]
    url = entry.data["url"]
    device_id = entry.data["id"]

    # Genera e invia token se non esiste
    await async_generate_token_and_notify(hass, name, url, device_id)

    # Registra API Views
    hass.http.register_view(TunnelCreateView(hass))
    hass.http.register_view(RebootView)
    hass.http.register_view(PingTunnelsView)

    # Ripristino tunnel precedenti
    tunnels_path = hass.config.path("tunnels.json")

    if os.path.exists(tunnels_path):
        try:
            # se il file è vuoto o solo whitespace, considera lista vuota
            if os.path.getsize(tunnels_path) == 0:
                tunnels = []
            else:
                with open(tunnels_path, "r") as f:
                    try:
                        tunnels = json.load(f)
                    except json.JSONDecodeError:
                        _LOGGER.warning("tunnels.json vuoto o corrotto, resetto lista tunnel")
                        tunnels = []
            for t in tunnels:
                start_tcp_tunnel(
                    t.get("local_port"),
                    t.get("target_ip"),
                    t.get("target_port")
                )
                _LOGGER.info(
                    f"🔁 Tunnel ripristinato: {t.get('local_port')} -> {t.get('target_ip')}:{t.get('target_port')}"
                )
        except Exception as e:
            _LOGGER.error(f"Errore caricando tunnel: {e}")


    # Carica piattaforma sensor
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    )

    return True
