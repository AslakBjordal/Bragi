<script lang='ts'>
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import Copy from 'carbon-icons-svelte/lib/Copy.svelte';
  import { Button, Tab, TabContent, Tabs, TextArea } from 'carbon-components-svelte';

  let segments = '';

  onMount(async () => {
    const customURL = $page.params.id;

    if (!customURL) {
      alert('Please enter a Youtube ID');
      return;
    }

    const socket = new WebSocket('ws://localhost:5173/ws');
    socket.addEventListener('open', () => {
      socket.send(JSON.stringify({
        action: 'stream_segments',
        'custom_url': customURL
      }));
    });

    socket.addEventListener('message', (event) => {
      const data = JSON.parse(event.data);
      if (data.action === 'stream_segments') {
        segments += `${data.segment_start_time}: ${data.segment_text}\n`;
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
    <video controls class='video-player' autoplay>
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
                rows={10}
                labelText='Transcribed Text on SRT Format'
                class='textarea'
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
