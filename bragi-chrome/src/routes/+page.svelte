<script lang="ts">
	let url = '';
	let runCaptions = false;
	let captions = '';
	let timerValue = '';

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
	function activateCaptions() {
		runCaptions = !runCaptions;
	}
	function getCurrentTime() {
		return document.querySelector('video')?.currentTime;
	}
	async function getCaptions() {
		const socket = new WebSocket('ws://localhost:8000');
		document.querySelector('video')?.addEventListener('seeking', () => {
			socket.send(
				JSON.stringify({
					action: 'stream-segments',
					youtube_id: new URL(url).searchParams.get('v'),
					segment_start_time: getCurrentTime()
				})
			);
		});

		socket.addEventListener('open', () => {
			socket.send(
				JSON.stringify({
					action: 'stream-segments',
					youtube_id: new URL(url).searchParams.get('v'),
					segment_start_time: getCurrentTime()
				})
			);
			socket.addEventListener('message', (event) => {
				const data = JSON.parse(event.data);
				if (data.action === 'stream_segments') {
					captions = data.segment_text;
				}
			});
		});
	}

	if (runCaptions) {
		getCaptions();
	}
</script>

<button on:click={getUrl}>Reveal url</button>
<button on:click={activateCaptions}>Toggle captions</button>
{#if url != ''}
	<div>
		Current url is {url}
		{#if runCaptions}
			<div>{captions}</div>
		{/if}
	</div>
{/if}
