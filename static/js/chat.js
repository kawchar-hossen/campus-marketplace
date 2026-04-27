const socket = io();

socket.emit("join", {});

function sendMessage() {
    const input = document.getElementById("message_input");
    const text = input.value.trim();

    if (!text) return;

    socket.emit("send_message", {
        receiver_id: receiverId,
        text: text
    });

    input.value = "";
}

socket.on("receive_message", function(data) {
    const messages = document.getElementById("messages");

    const div = document.createElement("div");
    div.classList.add("message-item");

    if (data.sender_id === currentUserId) {
        div.classList.add("my-message");
        div.innerHTML = "<strong>You</strong><br>" + data.text;
    } else {
        div.classList.add("other-message");
        div.innerHTML = "<strong>" + data.sender + "</strong><br>" + data.text;
    }

    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
});