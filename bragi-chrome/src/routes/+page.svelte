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

	if (runCaptions) {
		captions = 'UseAPI and get captions';
	}
</script>

<button on:click={getUrl}>Reveal url</button>
<button on:click={activateCaptions}>Toggle captions</button>
{#if url != ''}
	<div>
		Current url is {url}
		{#if timerValue}
			<div>Current progress in video {timerValue}</div>
		{/if}
	</div>
{/if}
