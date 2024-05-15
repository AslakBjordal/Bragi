<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';

  let segments = [];

  onMount(async () => {
    const youtubeId = $page.params.id;

    if (!youtubeId) {
      alert('Please enter a Youtube ID');
      return;
    }

    const socket = new WebSocket('ws://localhost:5173/ws');
    socket.addEventListener('open', () => {
      socket.send(JSON.stringify({
        action: 'stream_segments',
        'youtube_id': youtubeId,
      }));
    })

    socket.addEventListener('message', (event) => {
      const data = JSON.parse(event.data);
      if (data.action === 'stream_segments') {
        segments = [...segments, data];
      }
    });
  });
</script>

<style>
  .main-container {
    margin-top: 3rem;
    padding: 0;
  }
  .content {
    display: grid;
    row-gap: 1rem;
  }
  p {
    line-height: 1.7;
    font-size: 1.2rem;
  }
</style>

<div class="main-container">
  <div class="content">
    <h1>Youtube ID: {$page.params.id}</h1>
    <div>
      {#each segments as segment}
        <p>{segment.segment_start_time}: {segment.segment_text}</p>
      {/each}
    </div>
  </div>
</div>
