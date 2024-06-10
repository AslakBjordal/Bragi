function getCaptions(id) {
	console.log('opening connection');
	socket.send(
		JSON.stringify({
			delay: -0.15,
			action: 'stream_segments',
			youtube_id: id,
			segment_start_time: 0
		})
	);
	socket.addEventListener('message', (event) => {
		const data = JSON.parse(event.data);
		if (data.action === 'stream_segments') {
			captions = data.segment_text;
			console.log('sending caption:', captions);
			chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
				chrome.tabs.sendMessage(tabs[0].id, captions);
			});
		}
	});
}

chrome.runtime.onMessage.addListener((id) => {
	console.log('Got id:', id);
	if (socket.readyState == socket.OPEN) {
		console.log('Socket is open, adding eventlisteners');
		getCaptions(id);
	} else {
		console.log('Socket is closed. opening new socket and adding eventlistener');
		socket = new WebSocket('ws://localhost:8000/ws');
		getCaptions(id);
	}
});

console.log('Backend Started');
let socket = new WebSocket('ws://localhost:8000/ws');
