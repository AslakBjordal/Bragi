<script lang='ts'>
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import Copy from 'carbon-icons-svelte/lib/Copy.svelte';
  import { Button, Tab, TabContent, Tabs, TextArea } from 'carbon-components-svelte';

  let segments = '';
  let srtSegments = '';
  let socket: WebSocket | null = null;

  onMount(async () => {
    const customURL = $page.params.id;

    if (!customURL) {
      alert('Please enter a Youtube ID');
      return;
    }

    socket = new WebSocket('ws://localhost:5173/ws');
    socket.addEventListener('open', () => {
      socket?.send(JSON.stringify({
        action: 'stream_segments',
        'custom_url': customURL,
        language: $page.url.searchParams.get('lang') || 'en',
      }));
    });

    socket.addEventListener('message', (event) => {
      const data = JSON.parse(event.data);
      if (data.action === 'stream_segments') {
        segments += `${data.segment_start_time}: ${data.segment_text}\n`;
        srtSegments += data.segment_srt;
      }
    });
  });

  function onSeek(event) {
    segments = '';
    socket?.send(JSON.stringify({
      action: 'stream_segments',
      custom_url: $page.params.id,
      segment_start_time: event.target.currentTime,
      segment_stop: event.target.paused,
      language: $page.url.searchParams.get('lang') || 'en',
    }));
  }

  function onPause(event) {
    socket?.send(JSON.stringify({
      action: 'stream_segments',
      custom_url: $page.params.id,
      segment_stop: true,
      language: $page.url.searchParams.get('lang') || 'en',
    }));
  }

  function onPlay(event) {
    segments = '';
    socket?.send(JSON.stringify({
      action: 'stream_segments',
      custom_url: $page.params.id,
      segment_stop: false,
      segment_start_time: event.target.currentTime,
      language: $page.url.searchParams.get('lang') || 'en',
    }));
  }
</script>

<style>
  .main-container {
    margin-top: 3rem;
    padding: 0;
  }

  .content {
    display: flex;
    justify-content: space-between;
    row-gap: 1rem;
    gap: 1rem;

    & > video {
      flex-grow: 1;
    }
  }

  p {
    line-height: 1.7;
    font-size: 1.2rem;
  }
</style>

<div class='main-container'>
  <!-- Main content: Video Player and Transcription -->
  <div class='content'>
    <video on:seeking={onSeek} on:pause={onPause} on:play={onPlay} controls class='video-player' autoplay>
      <track kind='captions' label='English' srcLang='en' src='' default />
      <track kind='subtitles' label='English' srcLang='en' src='' />
      <source src="/api/videos/{$page.params.id}/stream" type="video/mp4">
    </video>
    <div class='transcription'>
      <Tabs>
        <Tab label='Plain text' />
        <Tab label='SRT format' />
        <svelte:fragment slot='content'>
          <TabContent>
              <TextArea
                rows={30}
                labelText='Transcribed Text'
                class='textarea'
                disabled
                bind:value={segments}
              />
            <Button icon={Copy}>Copy Text</Button>
          </TabContent>
          <TabContent>
              <TextArea
                rows={30}
                labelText='Transcribed Text on SRT Format'
                class='textarea'
                disabled
                bind:value={srtSegments}
              />
            <Button icon={Copy}>Copy Text</Button>
          </TabContent>
        </svelte:fragment>
      </Tabs>
    </div>
    <!--<div>
      {#each segments as segment}
        <p>{segment.segment_start_time}: {segment.segment_text}</p>
      {/each}
    </div>-->
  </div>
</div>
