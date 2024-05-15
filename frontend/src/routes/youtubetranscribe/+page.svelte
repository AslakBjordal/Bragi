<script lang="ts">
  import { Button, TextInput } from "carbon-components-svelte";

  let youtubeId = '';

  const onSubmit = async () => {
    if (!youtubeId) {
      alert('Please enter a Youtube ID');
      return;
    }

    const socket = new WebSocket('ws://localhost:5173/ws');
    socket.addEventListener('open', () => {
      socket.send(JSON.stringify({
        action: 'start_transcription',
        'youtube_id': youtubeId,
      }));
    })

    socket.addEventListener('message', (event) => {
      const data = JSON.parse(event.data);
      if (data.action === 'start_transcription') {
        window.location.href = '/youtubetranscribe/' + youtubeId;
      }
    });
  };
</script>

<style>
  .main-container {
    margin-top: 3rem;
    padding: 0;
  }
  .content > form {
    display: grid;
    row-gap: 1rem;
  }
</style>

<div class="main-container">
  <div class="content">
    <form on:submit={onSubmit}>
      <TextInput bind:value={youtubeId} labelText="Youtube ID" id="youtube-id" />
      <Button type="submit">Transcribe</Button>
    </form>
  </div>
</div>
