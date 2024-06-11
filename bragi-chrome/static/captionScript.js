const video = document.querySelector('video');
let enabled = false;

async function sendNewMessage(message) {
  await chrome.runtime.sendMessage(message);
}

chrome.runtime.onMessage.addListener((message) => {
  if (message.action === 'caption') {
    // If not enabled, then enable and create overlay
    if (!enabled) {
      enabled = true;
      createOverlay();
    }

    const caption = message.caption;
    // Write to overlay
    const overlay = document.querySelector('#bragi-overlay');
    overlay.innerText = caption;
  } else if (message.action === 'toggle') {
    enabled = !enabled;
    if (enabled) {
      createOverlay();
    } else {
      destroyOverlay();
    }
    sendNewMessage({
      delay: -0.15,
      action: 'stream_segments',
      youtube_id: new URL(document.location.href).searchParams.get('v'),
      segment_stop: !enabled,
      segment_start_time: video?.currentTime
    });
  }
});

function createOverlay() {
  // If overlay already exists, do nothing
  if (document.querySelector('#bragi-overlay-container')) {
    return;
  }

  const video = document.querySelector('video');
  const videoContainer = video.closest('#container');
  const overlayContainer = document.createElement('div');
  overlayContainer.id = 'bragi-overlay-container';
  overlayContainer.style.position = 'absolute';
  overlayContainer.style.top = '0';
  overlayContainer.style.left = '0';
  overlayContainer.style.width = '100%';
  overlayContainer.style.height = '100%';
  overlayContainer.style.display = 'flex';
  overlayContainer.style.pointerEvents = 'none';

  const overlay = document.createElement('div');
  overlay.id = 'bragi-overlay';
  overlay.style.position = 'absolute';
  overlay.style.bottom = '50px';
  overlay.style.left = '20px';
  overlay.style.right = '20px';
  overlay.style.height = '100px';
  overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
  overlay.style.color = 'white';
  overlay.style.fontSize = '30px';
  overlay.style.display = 'flex';
  overlay.style.alignItems = 'center';
  overlay.style.justifyContent = 'center';

  overlayContainer.appendChild(overlay);
  videoContainer.appendChild(overlayContainer);
}

function destroyOverlay() {
  const overlayContainer = document.querySelector('#bragi-overlay-container');
  overlayContainer?.remove();
}


video?.addEventListener('seeking', (evt) => {
  const target = evt.target;
  if (target.paused) {
    destroyOverlay();
    return;
  }
  createOverlay();

  sendNewMessage({
    delay: -0.15,
    action: 'stream_segments',
    youtube_id: new URL(document.location.href).searchParams.get('v'),
    segment_start_time: target.currentTime,
    segment_stop: target.paused
  });
});

video?.addEventListener('pause', (evt) => {
  destroyOverlay();

  sendNewMessage({
    action: 'stream_segments',
    youtube_id: new URL(url).searchParams.get('v'),
    segment_stop: true
  });
});

video?.addEventListener('play', (evt) => {
  const target = evt.target;
  createOverlay();
  sendNewMessage({
    delay: -0.15,
    action: 'stream_segments',
    youtube_id: new URL(url).searchParams.get('v'),
    segment_start_time: target.currentTime,
    segment_stop: false
  });
});
