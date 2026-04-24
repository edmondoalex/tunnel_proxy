# Tunnel Proxy

Integrazione custom per Home Assistant che espone endpoint API per:
- creazione tunnel TCP
- ping dei target configurati
- reboot remoto di Home Assistant tramite token

## Versione

Versione corrente componente: **2.0.12**

## Funzionalita principali

- Config flow da interfaccia Home Assistant
- Gestione token server (`/config/server_tokens.json`)
- Persistenza tunnel (`/config/tunnels.json`)
- Sensore token dedicato
- Endpoint API:
  - `POST /api/tunnel_proxy/create`
  - `GET /api/tunnel_proxy/ping`
  - `GET /api/tunnel_proxy/reboot`

## Installazione (HACS)

1. HACS -> Integrazioni -> menu tre punti -> Repository personalizzati.
2. Aggiungi `https://github.com/edmondoalex/tunnel_proxy` come categoria `Integration`.
3. Installa `Tunnel Proxy` e riavvia Home Assistant.
4. Aggiungi l'integrazione da `Impostazioni -> Dispositivi e servizi`.

## Note 2.0.12

- Rimosse chiamate file bloccanti dal loop async nelle view.
- Lettura tunnel di bootstrap resa async-safe tramite executor.
- Sensore reso compatibile con formati token legacy (fix errore `'name'`).
- Allineamento metadati release/documentazione.
- Fix import `os` nel sensore (errore `name 'os' is not defined`).
- Gestione timeout rete durante invio token con log a livello warning.
- Aggiunti sensori dedicati ai tunnel connessi visibili nella pagina dispositivo.
- Nomi entita accorciati per migliorare leggibilita nella card dispositivo.
- Aggiunti brand assets locali (`brand/icon.png`, `brand/logo.png`) per mostrare il logo nell'integrazione.











