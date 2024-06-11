<script lang='ts'>
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

  async function activateCaptions() {
    runCaptions = !runCaptions;
    await getUrl();
    (async () => {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      await chrome.tabs.sendMessage(tab.id!, {
        action: 'toggle',
      });
    })().then();
  }

  function getCurrentTime() {
    return document.querySelector('video')?.currentTime;
  }

</script>

<button on:click={activateCaptions}>Toggle captions</button>
<div>
  Current url is {url}
  {#if runCaptions}
    <div>captions activated:{captions}</div>
  {/if}
</div>
