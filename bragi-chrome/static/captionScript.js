window.addEventListener('popstate', () => {
	let url = window.location.href;
	if (url.includes('www.youtube.com/watch?v=')) {
		let videoID = new URL(url).searchParams.get('v');
		chrome.runtime.sendMessage(videoID);
	}
});
chrome.runtime.onMessage.addListener((caption) => {
	alert(caption);
});
