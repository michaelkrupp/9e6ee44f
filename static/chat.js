function createMessageElement(message) {
    const el = document.createElement('li');
    switch (message.sender) {
        case 'agent':
            el.className = 'chat-message chat-message-agent';
            break;
        case 'system':
            el.className = 'chat-message chat-message-system';
            break;
        default:
            el.className = 'chat-message chat-message-customer';
    }
    el.setAttribute('data-message-id', message.id);
    el.textContent = message.text;
    return el;
}

function connectMessageWebSocket(path, chatId, chatView) {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.hostname}:${window.location.port}/${path}/${chatId}`;
    const ws = new WebSocket(wsUrl);
    ws.onopen = function() {
        console.log('Message WebSocket connection established');
    };
    ws.onclose = function() {
        console.log('Message WebSocket connection closed');
    };
    ws.onmessage = function(event) {
        const message = JSON.parse(event.data);

        console.log('Message received:', message);

        const el = createMessageElement(message);
        chatView.appendChild(el);
        chatView.scrollTop = chatView.scrollHeight;
    };
    return ws
}


function sendMessage(ws, el) {
    if (el.value.trim().length === 0) {
        return;
    }
    ws.send(JSON.stringify({
        text: chatInputText.value,
    }));
    el.value = '';
}

function createChatElement(room_id, selectChat) {
    const el = document.createElement('li');
    el.className = 'chat-list-item';
    el.textContent = room_id;
    el.setAttribute('data-room-id', room_id);
    el.addEventListener('click', function() {
        selectChat(room_id);
    });
    return el;
}

function connectNotificationWebSocket(path, chatList, connectToChat) {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.hostname}:${window.location.port}/${path}`;
    const ws = new WebSocket(wsUrl);
    ws.onopen = function() {
        console.log('Notification WebSocket connection established');
    };
    ws.onclose = function() {
        console.log('Notification WebSocket connection closed');
    };
    ws.onmessage = function(event) {
        const notification = JSON.parse(event.data);

        console.log('Notification received:', notification);

        // remove non-existing rooms
        for (el of document.querySelectorAll('.chat-list-item')) {
            if (notification.room_ids.includes(el.getAttribute('data-room-id'))) {
                continue
            }
            chatList.removeChild(el)
        }

        // add new rooms
        for (room_id of notification.room_ids) {
            let el = document.querySelector(`.chat-list-item[data-room-id="${room_id}"]`);
            if (el) {
                continue
            }
            el = createChatElement(room_id, connectToChat);
            chatList.appendChild(el)
        }

        
    }
    return ws
}