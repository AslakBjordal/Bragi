function getCaptions(id, time) {
	console.log('opening connection');
	socket.send(
		JSON.stringify({
			delay: -0.15,
			action: 'stream_segments',
			youtube_id: id,
			segment_start_time: time
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

chrome.runtime.onMessage.addListener((message) => {
	if (message == 'abort') {
		socket?.close();
	}
	videoInfo = JSON.parse(message);
	console.log('Got id:', videoInfo.id);
	if (socket.readyState == socket.OPEN) {
		console.log('Socket is open, adding eventlisteners');
		getCaptions(videoInfo.id, videoInfo.time);
	} else {
		console.log('Socket is closed. opening new socket and adding eventlistener');
		socket = new WebSocket('ws://localhost:8000/ws');
		getCaptions(videoInfo.id, videoInfo.time);
	}
});

console.log('Backend Started');
let socket;

chrome.runtime.onStartup.addListener(() => {
	socket = new WebSocket('ws://localhost:8000/ws');
});
chrome.runtime.onInstalled.addListener(() => {
	socket = new WebSocket('ws://localhost:8000/ws');
});
