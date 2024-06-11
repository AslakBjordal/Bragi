<script lang='ts'>
  import 'carbon-components-svelte/css/all.css';
  import { Dropdown, FileUploaderButton } from 'carbon-components-svelte';
  import { onMount } from 'svelte';
  import { sendRequest } from '../../utils';

  let isSideNavOpen = false;
  let uploadedFiles: File[] = []; // Array to hold the uploaded files
  let videoElement: HTMLVideoElement;
  let uploadedFile: File | null = null;
  let transcribedText: string = 'Here will be the transcribed text...';
  let SRTFormat: string = 'dsadsadsadsadsasda';
  let serverVideos = [];
  let selectedLanguage = 'en';

  onMount(async () => {
    const res = await sendRequest('GET', '/videos');
    serverVideos = res.videos;
  });

  async function handleFileSelect(event: CustomEvent): void {
    const files = event.detail as File[];
    uploadedFiles = [...uploadedFiles, ...files]; // Add new files to the existing list
    if (files.length === 0) {
      return;
    }

    if (files.length > 1) {
      alert('Please select only one file at a time.');
      return;
    }

    uploadedFile = files[0];

    // Do form upload
    const formData = new FormData();
    formData.append('file', uploadedFile);

    // Send the file to the server for transcription
    const token = localStorage.getItem('token');
    if (!token) {
      alert('Please log in to transcribe files.');
      return;
    }

    const res = await fetch('/api/file', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`
      },
      body: formData
    });
    const json = await res.json();

    // Redirect to the transcription page
    window.location.href = `/newcaption/${json.uuid}?lang=${selectedLanguage}`;
  }

  function handleCopyText(): void {
    navigator.clipboard
    .writeText(transcribedText)
    .catch((err) => console.error('Failed to copy text: ', err));
  }

  function handleCopySRT(): void {
    navigator.clipboard
    .writeText(SRTFormat)
    .catch((err) => console.error('Failed to copy text: ', err));
  }

  function handleLogout(): void {
    // Implement logout logic here
    console.log('Logging out...');
    // E.g., clear session, redirect to login, etc.
  }
</script>

<div class='main-container'>
  <div class='content'>
    <FileUploaderButton
      on:change={handleFileSelect}
      labelText='Add file'
      accept={['.mp3', '.mp4']}
    />
    <Dropdown
      selectedId={selectedLanguage}
      on:select={ (event) => selectedLanguage = event.detail.selectedItem.id }
      titleText='Language'
      items={[
        {
          text: 'English',
          id: 'en'
        },
        {
          text: 'Spanish',
          id: 'es'
        },
        {
          text: 'French',
          id: 'fr'
        },
        {
          text: 'Norwegian',
          id: 'no'
        },
        {
          text: 'Turkish',
          id: 'tr'
        },
        {
          text: 'Swedish',
          id: 'sv'
        }
      ]}
    />
    <div class='files'>
      <h1>Your files</h1>
      {#each serverVideos as video}
        <a href='/newcaption/{video.custom_url}'>{video.name}</a>
      {/each}
    </div>
  </div>
</div>

<style>
  .main-container {
    margin-top: 3rem;
    padding: 0;
  }

  :global(.logout-button) {
    position: absolute;
    bottom: 4rem;
    width: 100%;
  }

  .content {
    row-gap: 1rem;
    gap: 1rem;
  }

  .files {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-top: 1rem;

    & > a {
      text-decoration: none;
      color: var(--cds-interactive-04);
    }
  }

  .video-and-text {
    display: flex;
    flex-direction: row;
    gap: 1rem;
  }

  .video-player {
    flex: 2;
    width: 100%;
    max-width: 960px; /* Adjust based on your layout needs */
  }

  .transcription {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  :global(.textarea) {
    min-width: 500px;
    max-width: 500px;
    width: 100%; /* Ensures full width within the limits */
  }

  @media (max-width: 960px) {
    .video-and-text {
      flex-direction: column;
    }

    .video-player {
      max-width: 100%;
    }
  }
</style>
