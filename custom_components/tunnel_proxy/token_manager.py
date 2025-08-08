import json
import os
import secrets
import logging
import requests

_LOGGER = logging.getLogger(__name__)

async def async_generate_token_and_notify(hass, name, url, device_id):
    token_path = hass.config.path("server_tokens.json")
    existing = await hass.async_add_executor_job(get_existing_token, token_path)
    if existing:
        return
    token = secrets.token_urlsafe(32)
    await hass.async_add_executor_job(save_token, token_path, token)
    await hass.async_add_executor_job(send_token, url, token, device_id)

def get_existing_token(token_path):
    """
    Restituisce il primo token presente in server_tokens.json, se esiste.
    """
    if not os.path.exists(token_path):
        _LOGGER.debug(f"File token {token_path} non trovato.")
        return None
    try:
        with open(token_path, "r") as f:
            tokens = json.load(f)
        if isinstance(tokens, list) and tokens:
            return tokens[0].get("token")
    except Exception as e:
        _LOGGER.warning(f"Errore leggendo file token: {e}")
    return None

def save_token(token_path, token):
    """Salva un token in server_tokens.json"""
    tokens = []
    try:
        if os.path.exists(token_path):
            with open(token_path, "r") as f:
                tokens = json.load(f)
    except Exception:
        tokens = []

    if token not in [t.get("token") for t in tokens]:
        tokens.append({"token": token})
        with open(token_path, "w") as f:
            json.dump(tokens, f, indent=2)
        _LOGGER.info("Token salvato.")

def send_token(url, token, device_id):
    """Invia il token al server esterno."""
    try:
        payload = {"token": token, "id": device_id}
        headers = {"Content-Type": "application/json"}
        full_url = f"{url}/proxy/register"
        response = requests.post(full_url, json=payload, headers=headers, timeout=5)
        if response.status_code == 200:
            _LOGGER.info("Token inviato con successo")
        else:
            _LOGGER.error(f"Errore dal server {url}: {response.status_code}")
    except Exception as e:
        _LOGGER.error(f"Errore durante invio token: {e}")
