html="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Room WebSocket Demo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 20px;
        }
        #messages {
            border: 1px solid #ccc;
            height: 250px;
            padding: 10px;
            overflow-y: auto;
            margin-bottom: 10px;
        }
        input, button {
            padding: 8px;
        }
    </style>
</head>
<body>

<h2>WebSocket Room Demo</h2>

<label>Room ID:</label>
<input id="roomId" value="1" />
<button onclick="connect()">Connect</button>

<div id="status"></div>

<hr>

<div id="messages"></div>

<input id="messageInput" placeholder="Type message..." />
<button onclick="sendMessage()">Send</button>

<script>
    let socket = null;

    function connect() {
        const roomId = Number(document.getElementById("roomId").value);
        socket = new WebSocket(`ws://localhost:8000/ws/rooms/${roomId}`);

        socket.onopen = () => {
            document.getElementById("status").innerText = "✅ Connected";
        };

        socket.onmessage = (event) => {
            const messages = document.getElementById("messages");
            messages.innerHTML += `<div>${event.data}</div>`;
        };

        socket.onclose = () => {
            document.getElementById("status").innerText = "❌ Disconnected";
        };

        socket.onerror = (error) => {
            console.error("WebSocket error:", error);
        };
    }

    function sendMessage() {
        const input = document.getElementById("messageInput");
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(input.value);
            input.value = "";
        }
    }
</script>

</body>
</html>




"""