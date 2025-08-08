import asyncio
import json
import os
import logging
from aiohttp import web
from homeassistant.components.http import HomeAssistantView

from .token_manager import get_existing_token
from .utils import save_tunnel_info, start_tcp_tunnel

_LOGGER = logging.getLogger(__name__)
DOMAIN = "tunnel_proxy"

class TunnelCreateView(HomeAssistantView):
    url = "/api/tunnel_proxy/create"
    name = "api:tunnel_proxy:create"
    requires_auth = False

    def __init__(self, hass):
        self.hass = hass

    async def post(self, request):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return self.json({"error": "Missing token"}, status_code=401)
        token = auth[7:]

        token_path = self.hass.config.path("server_tokens.json")
        valid_token = get_existing_token(token_path)
        if token != valid_token:
            return self.json({"error": "Invalid token"}, status_code=401)

        body = await request.json()
        local_port = body.get("local_port")
        target_ip = body.get("target_ip")
        target_port = body.get("target_port")

        if not local_port or not target_ip or not target_port:
            return self.json({"error": "Missing parameters"}, status_code=400)

        try:
            start_tcp_tunnel(local_port, target_ip, target_port)
        except Exception as e:
            _LOGGER.error(f"Errore avviando socat: {e}")
            return self.json({"error": f"Failed to create tunnel: {e}"}, status_code=500)

        # Salva su file
        tunnel_data = {
            "local_port": local_port,
            "target_ip": target_ip,
            "target_port": target_port
        }
        save_tunnel_info(self.hass, tunnel_data)
        _LOGGER.info(f"✅ Tunnel creato: {local_port} -> {target_ip}:{target_port}")
        return self.json({"status": "Tunnel created"}, status_code=200)


class RebootView(HomeAssistantView):
    url = "/api/tunnel_proxy/reboot"
    name = "api:tunnel_proxy:reboot"
    requires_auth = False

    async def get(self, request: web.Request) -> web.Response:
        """Riavvia HA se header Authorization valido."""
        hass = request.app["hass"]
        token_path = hass.config.path("server_tokens.json")
        valid_token = get_existing_token(token_path)

        auth_header = request.headers.get("Authorization", "")
        req_token = auth_header.split()[-1] if auth_header else None
        if req_token != valid_token:
            return web.Response(status=401, text="Unauthorized")

        hass.async_create_task(
            hass.services.async_call("homeassistant", "restart")
        )
        return web.Response(status=200, text="Reboot initiated")


class PingTunnelsView(HomeAssistantView):
    url = "/api/tunnel_proxy/ping"
    name = "api:tunnel_proxy:ping"
    requires_auth = False

    async def get(self, request: web.Request) -> web.Response:
        """Ping dei dispositivi in tunnels.json -> {ip: online/offline}."""
        hass = request.app["hass"]
        token_path = hass.config.path("server_tokens.json")
        valid_token = get_existing_token(token_path)

        auth_header = request.headers.get("Authorization", "")
        req_token = auth_header.split()[-1] if auth_header else None
        if req_token != valid_token:
            return web.Response(status=401, text="Unauthorized")

        # Lettura tunnels
        tunnels_file = hass.config.path("tunnels.json")
        try:
            with open(tunnels_file, "r") as f:
                tunnels = json.load(f)
        except Exception:
            tunnels = []

        results = {}
        async def do_ping(ip: str) -> bool:
            proc = await asyncio.create_subprocess_exec(
                "ping", "-c", "1", "-W", "1", ip,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            return await proc.wait() == 0

        tasks = {t["target_ip"]: asyncio.create_task(do_ping(t["target_ip"])) for t in tunnels}
        for ip, task in tasks.items():
            try:
                alive = await task
            except:
                alive = False
            results[ip] = "online" if alive else "offline"

        return web.json_response(results)
