window.addEventListener('popstate', () => {
	let url = window.location.href;
	if (url.includes('www.youtube.com/watch?v=')) {
		let videoID = new URL(url).searchParams.get('v');
		let time = document.querySelector('video').currentTime;
		chrome.runtime.sendMessage(
			JSON.stringify({
				id: videoID,
				time: time
			})
		);
	}
});

//document.querySelector('video')?.addEventListener('seeking', () => {
//	let url = window.location.href;
//	let videoID = new URL(url).searchParams.get('v');
//	let time = document.querySelector('video').currentTime;
//
//	chrome.runtime.sendMessage(
//		JSON.stringify({
//			id: videoID,
//			time: time
//		})
//	);
//});

chrome.runtime.onMessage.addListener((caption) => {
	alert(caption);
});
