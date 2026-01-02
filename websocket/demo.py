
html="""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Live Room + Chat</title>
<script src="https://www.youtube.com/iframe_api"></script>
<style>
body { font-family: Arial; padding: 20px; }
#status { font-weight: bold; font-size: 18px; margin-bottom: 10px; }
#messages { border: 1px solid #ccc; height: 200px; padding: 10px; overflow-y: auto; margin-bottom: 10px; }
#controls button { margin-right: 5px; }
#player-container { margin-bottom: 20px; }
button { margin-top: 5px; }
.system { color: blue; }
.join { color: green; }
.leave { color: red; }
</style>
</head>
<body>

<h2 id="room-title">Room</h2>
<div id="status">❌ Not connected</div>

<label>Room ID:</label>
<input id="roomId" value="1">
<button id="connect-btn">Connect & Load Video</button>

<hr>
<div id="player-container"><div id="player"></div></div>

<div id="controls">
  <button id="play-btn">Play</button>
  <button id="pause-btn">Pause</button>
  <button id="restart-btn">Restart</button>
</div>

<hr>
<div id="messages"></div>
<input id="messageInput" placeholder="Type message...">
<button id="send-btn">Send</button>

<script>
const API_BASE =
  window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:8000"
    : "https://chat-flix-kishan.onrender.com";

let socket = null;
let isAdmin = false;
let player = null;
let videoId = null;
let roomId = null;

// ---------------- Helpers ----------------
function logState(event, data={}) {
    console.log(`%c[ROOM STATE] ${event}`, "color:#00bcd4;font-weight:bold;", data);
}
function appendMessage(msg, cls="") {
    const messages = document.getElementById("messages");
    messages.innerHTML += `<div class="${cls}">${msg}</div>`;
    messages.scrollTop = messages.scrollHeight;
}
function extractYouTubeId(url) {
    if (!url) return null;
    const r = /(?:youtube\.com\/(?:watch\?v=|embed\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})/;
    const m = url.match(r);
    return m ? m[1] : null;
}

// ---------------- YouTube ----------------
function onYouTubeIframeAPIReady() {
    logState("YouTube API Ready");
}

function createPlayer() {
    if (!videoId) videoId = "KEvXoPFi28k"; // fallback
    player = new YT.Player("player", {
        videoId: videoId,
        playerVars: { controls: 1, autoplay: 0, origin: window.location.origin },
        events: {
            onReady: () => logState("Player Ready"),
            onStateChange: onPlayerStateChange
        }
    });
}

function onPlayerStateChange(event) {
    if (!isAdmin || !socket) return;
    const currentTime = player.getCurrentTime();
    const action = event.data === YT.PlayerState.PLAYING ? "play" :
                   event.data === YT.PlayerState.PAUSED ? "pause" : "seek";

    socket.send(JSON.stringify({
        type: "video_action",
        video_id: videoId,
        action: action,
        time: currentTime
    }));

    logState("Player State Change Sent", { action, time: currentTime });
}

// ---------------- Room & Role ----------------
async function checkRole(roomId) {
    const res = await fetch(`${API_BASE}/rooms/${roomId}/role`, { credentials: "include" });
    if (!res.ok) throw "Failed to get role";
    const data = await res.json();
    isAdmin = data.is_admin;
    document.getElementById("controls").style.display = isAdmin ? "block" : "none";
    logState("Role determined", { isAdmin });
}

async function loadRoom() {
    roomId = Number(document.getElementById("roomId").value);
    const res = await fetch(`${API_BASE}/rooms/${roomId}`, { credentials: "include" });
    if (!res.ok) throw "Room not found";
    const room = await res.json();
    document.getElementById("room-title").innerText = room.room_name;
    videoId = extractYouTubeId(room.video_url);
    await checkRole(roomId);
    createPlayer();
}

async function connect() {
    await loadRoom();
    const roomId = Number(document.getElementById("roomId").value);
    const wsProtocol = location.protocol === "https:" ? "wss" : "ws";

    socket = new WebSocket(`${wsProtocol}://${location.host}/ws/rooms/${roomId}`);

    socket.onopen = () => {
        document.getElementById("status").innerText = "✅ Connected";
        appendMessage("Joined room", "join");
        logState("WS Connected", { roomId });
    };

    socket.onmessage = (e) => {
        const data = JSON.parse(e.data);
        logState("WS Message", data);

        if (data.type === "chat") {
            appendMessage(data.message);
        }

        if (data.type === "video_action") {
            // Apply host's action for new users or updates
            if (!isAdmin) {
                applyVideoAction(data);

                // ---------- CONSOLE LOG LIVE ADMIN STATE ----------
                console.log('--------------------ADMIN LIVE STATE--------------------');
                console.log('Video ID:', data.video_id);
                console.log('Action:', data.action);
                console.log('Time:', data.time);
                console.log('-------------------------------------------------------');
            }
        }

        if (data.type === "kicked") {
            alert("You were kicked from the room!");
            location.reload();
        }
    };

    socket.onclose = () => {
        document.getElementById("status").innerText = "❌ Disconnected";
        logState("WS Disconnected");
    };
}

// ---------------- Video Sync ----------------
function applyVideoAction(data) {
    if (!player) return;
    if (data.video_id) videoId = data.video_id;
    const time = data.time ?? 0;

    switch (data.action) {
        case "play": player.seekTo(time, true); player.playVideo(); break;
        case "pause": player.seekTo(time, true); player.pauseVideo(); break;
        case "seek": player.seekTo(time, true); break;
    }
    logState("Apply Video Action", data);

    // ---------- OPTIONAL: LOG AGAIN IF YOU WANT FRONTEND STATE ----------
    console.log('--------------------ADMIN LIVE STATE AFTER SYNC--------------------');
    console.log('Video ID:', videoId);
    console.log('Current Player Time:', player.getCurrentTime());
    console.log('-------------------------------------------------------');
}


// ---------------- Controls ----------------
function sendVideoAction(action) {
    if (!isAdmin || !socket || !player) return;
    const currentTime = player.getCurrentTime();
    socket.send(JSON.stringify({ type: "video_action", video_id: videoId, action, time: currentTime }));
}

document.getElementById("play-btn").onclick = () => sendVideoAction("play");
document.getElementById("pause-btn").onclick = () => sendVideoAction("pause");
document.getElementById("restart-btn").onclick = () => sendVideoAction("seek");

// ---------------- Chat ----------------
document.getElementById("send-btn").onclick = () => {
    const msg = document.getElementById("messageInput").value;
    if (!msg || !socket) return;
    socket.send(JSON.stringify({ type: "chat", message: msg }));
    document.getElementById("messageInput").value = "";
};

// ---------------- Connect ----------------
document.getElementById("connect-btn").onclick = connect;

</script>
</body>
</html>



"""

