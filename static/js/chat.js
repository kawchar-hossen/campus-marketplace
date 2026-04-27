// =====================================
// static/js/chat.js
// =====================================

const socket = io();

const messageBox = document.getElementById("messages");
const messageInput = document.getElementById("message_input");


// =====================================
// Join Personal Room
// =====================================
socket.emit("join", {
    receiver_id: receiverId
});


// =====================================
// Receive New Message
// =====================================
socket.on("receive_message", function (data) {
    const newMessage = document.createElement("div");

    newMessage.classList.add("message-item");

    if (data.sender_id === currentUserId) {
        newMessage.classList.add("my-message");
        newMessage.innerHTML = `
            <strong>You</strong><br>
            ${data.text}
        `;
    } else {
        newMessage.classList.add("other-message");
        newMessage.innerHTML = `
            <strong>${data.sender}</strong><br>
            ${data.text}
        `;
    }

    messageBox.appendChild(newMessage);
    messageBox.scrollTop = messageBox.scrollHeight;
});


// =====================================
// Send Message
// =====================================
function sendMessage() {
    const text = messageInput.value.trim();

    if (!text) return;

    socket.emit("send_message", {
        receiver_id: receiverId,
        text: text
    });

    messageInput.value = "";
    messageInput.focus();
}


// =====================================
// Send on Enter Key
// =====================================
messageInput.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
        e.preventDefault();
        sendMessage();
    }
});


// =====================================
// Auto Scroll
// =====================================
messageBox.scrollTop = messageBox.scrollHeight;