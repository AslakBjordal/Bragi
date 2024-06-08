<script lang="ts">
	let url = '';
	let runCaptions = false;
	let captions = '';
	let timerValue = '';
	let socket: WebSocket | null = null;

	const container = document.createElement('div');
	const text = document.createElement('div');
	container.appendChild(text);

	async function getUrl() {
		const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
		url = tab.url ?? '';
		if (url.includes('www.youtube.com/watch?v')) {
			chrome.scripting
				.executeScript({
					target: { tabId: tab.id ?? 0 },
					func: getCurrentTime
				})
				.then((results) => {
					for (const { result } of results) {
						timerValue = result?.toString() ?? 'no video found';
					}
				});
		}
	}
	async function activateCaptions() {
		runCaptions = !runCaptions;
		await getUrl();
		if (runCaptions) {
			getCaptions();
		} else {
			socket?.close();
			socket = null;
		}
	}
	function getCurrentTime() {
		return document.querySelector('video')?.currentTime;
	}

	async function getCaptions() {
		if (!socket) {
			socket = new WebSocket('ws://localhost:8000/ws');
		}
		document.cookie = 'token=f6b30474186343810b005dab574111869e4095e271a1a284ab80592adbf1; path=/';
		document.querySelector('video')?.addEventListener('seeking', () => {
			socket?.send(
				JSON.stringify({
					delay: -0.15,
					action: 'stream_segments',
					youtube_id: new URL(url).searchParams.get('v'),
					segment_start_time: getCurrentTime()
				})
			);
		});

		socket.addEventListener('open', () => {
			socket?.send(
				JSON.stringify({
					delay: -0.15,
					action: 'stream_segments',
					youtube_id: new URL(url).searchParams.get('v'),
					segment_start_time: getCurrentTime()
				})
			);
			socket?.addEventListener('message', (event) => {
				const data = JSON.parse(event.data);
				if (data.action === 'stream_segments') {
					captions = data.segment_text;
				}
			});
		});
	}
</script>

<button on:click={activateCaptions}>Toggle captions</button>
<div>
	Current url is {url}
	{#if runCaptions}
		<div>captions activated:{captions}</div>
	{/if}
</div>
