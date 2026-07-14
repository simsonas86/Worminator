const WS_URL = "ws://127.0.0.1:8765/ws";
const waitingOverlay = document.getElementById("waiting-overlay");
const raffleOverlay = document.getElementById("raffle-overlay");
const winnerOverlay = document.getElementById("winner-overlay");
const overlays = [waitingOverlay, raffleOverlay, winnerOverlay];
const entryCount = document.getElementById("entry-count");
const claimCount = document.getElementById("claim-count");
const timer = document.getElementById("timer");
const winnerName = document.getElementById("winner-name");

let state = {
    open: false,
    entries: 0,
    claims: 0,
    end_timestamp: null,
    winner: null,
};
let timerId = null;
let reconnectId = null;
let connectTimeoutId = null;
let reconnectDelay = 1000;

function showOverlay(activeOverlay) {
    for (const overlay of overlays) {
        overlay.classList.toggle("is-open", overlay === activeOverlay);
    }
}

function formatTime(remainingSeconds) {
    const safeSeconds = Math.max(0, Math.ceil(remainingSeconds));
    const minutes = Math.floor(safeSeconds / 60);
    const seconds = safeSeconds % 60;
    return `${minutes}:${String(seconds).padStart(2, "0")}`;
}

function updateTimer() {
    if (!state.open || !state.end_timestamp) {
        timer.textContent = "0:00";
        return;
    }

    const remainingSeconds = state.end_timestamp - Date.now() / 1000;
    timer.textContent = formatTime(remainingSeconds);
}

function startTimerLoop() {
    if (timerId) {
        return;
    }

    timerId = setInterval(updateTimer, 250);
}

function stopTimerLoop() {
    if (!timerId) {
        return;
    }

    clearInterval(timerId);
    timerId = null;
}

function renderState(nextState) {
    state = {
        open: false,
        entries: 0,
        claims: 0,
        end_timestamp: null,
        winner: null,
        ...nextState,
    };

    entryCount.textContent = String(state.entries ?? 0);
    claimCount.textContent = String(state.claims ?? 0);
    winnerName.textContent = state.winner?.username ?? "";

    if (state.open) {
        showOverlay(raffleOverlay);
        startTimerLoop();
    } else if (state.winner) {
        showOverlay(winnerOverlay);
        stopTimerLoop();
    } else {
        showOverlay(null);
        stopTimerLoop();
    }

    updateTimer();
}

function clearConnectTimeout() {
    if (connectTimeoutId) {
        clearTimeout(connectTimeoutId);
        connectTimeoutId = null;
    }
}

function showDisconnected() {
    stopTimerLoop();
    showOverlay(waitingOverlay);
}

function scheduleReconnect() {
    if (reconnectId) {
        return;
    }

    showDisconnected();
    reconnectId = setTimeout(() => {
        reconnectId = null;
        connect();
    }, reconnectDelay);

    reconnectDelay = Math.min(reconnectDelay * 2, 10000);
}

function handleDisconnect() {
    clearConnectTimeout();
    scheduleReconnect();
}

function connect() {
    clearConnectTimeout();

    const ws = new WebSocket(WS_URL);
    console.log("[WEBSOCKET] Connecting to: ", WS_URL);

    connectTimeoutId = setTimeout(() => {
        if (ws.readyState === WebSocket.CONNECTING) {
            ws.close();
        }
    }, 5000);

    ws.onopen = () => {
        clearConnectTimeout();

        if (reconnectId) {
            clearTimeout(reconnectId);
            reconnectId = null;
        }

        reconnectDelay = 1000;
        showOverlay(null);
        console.log("[WEBSOCKET] Connected");
    };

    ws.onmessage = (event) => {
        try {
            const message = JSON.parse(event.data);
            if (message.type === "raffle_state" && message.state) {
                renderState(message.state);
                console.log("[WEBSOCKET] Received raffle state:", message.state);
            }
        } catch (error) {
            console.error("Invalid websocket payload", error);
        }
    };

    ws.onclose = handleDisconnect;

    ws.onerror = handleDisconnect;
}

showOverlay(waitingOverlay);
connect();