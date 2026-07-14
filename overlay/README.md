# Setup
To add the overlay to OBS, create a new browser source:
- Set the URL to `file:///<path>/Worminator/overlay/index.html`
- Set the Width to `466`
- Set the Height to `119`
- Remove default custom CSS.
- Everything else stays default.

# Configuration
- If overlay is not needed, can use `WORMINATOR_WS_DISABLED=true` in .env to stop websocket server from starting.
