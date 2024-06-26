let socket = null;

async function getCaptions(msg) {
  if (msg.action !== 'stream_segments') {
    return;
  }

  if (socket) {
    if (msg.segment_stop) {
      socket.close();
      socket = null;
      return;
    }
  } else {
    socket = new WebSocket('ws://localhost:8000/ws');
  }

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  socket.addEventListener('open', () => {
    socket?.send(JSON.stringify(msg));
    socket?.addEventListener('message', (event) => {
      const data = JSON.parse(event.data);
      if (data.action === 'stream_segments') {
        chrome.tabs.sendMessage(tab.id, {
          action: 'caption',
          caption: data.segment_text
        });
      }
    });
  });
}

chrome.runtime.onMessage.addListener(getCaptions);
