<script lang="ts">
  import 'carbon-components-svelte/css/all.css';
  import Logout from 'carbon-icons-svelte/lib/Logout.svelte';
  import ArrowDownRight from 'carbon-icons-svelte/lib/ArrowDownRight.svelte';
  import Copy from 'carbon-icons-svelte/lib/Copy.svelte';
  import {
    SideNav,
    SideNavItems,
    SideNavMenu,
    SideNavMenuItem,
    SideNavDivider,
    FileUploaderButton,
    Button,
    TextArea,
    Tabs,
    Tab,
    TabContent,
  } from 'carbon-components-svelte';

  let isSideNavOpen = false;
  let uploadedFiles: File[] = []; // Array to hold the uploaded files
  let videoElement: HTMLVideoElement;
  let uploadedFile: File | null = null;
  let transcribedText: string = 'Here will be the transcribed text...';
  let SRTFormat: string = 'dsadsadsadsadsasda';

  function handleFileSelect(event: CustomEvent): void {
    const files = event.detail.files as File[];
    uploadedFiles = [...uploadedFiles, ...files]; // Add new files to the existing list
    if (files.length > 0) {
      uploadedFile = files[0];
      loadVideo(uploadedFile);
    }
  }
  function loadVideo(file: File): void {
    const fileURL = URL.createObjectURL(file);
    videoElement.src = fileURL;
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

<div class="main-container">
  <!-- Sidebar -->
  <SideNav bind:isOpen={isSideNavOpen} rail class="sidebar">
    <SideNavItems>
      <FileUploaderButton
        on:change={handleFileSelect}
        labelText="Add file"
        accept={['.mp3', '.mp4']}
      />
      <SideNavDivider />
      <SideNavMenu icon={ArrowDownRight} text="Your files">
        {#each uploadedFiles as file (file.name)}
          <SideNavMenuItem text={file.name} />
        {/each}
      </SideNavMenu>
      <SideNavDivider />
      <!-- Logout button at the bottom of the SideNav -->
      <Button
        kind="danger-tertiary"
        class="logout-button"
        on:click={handleLogout}
        icon={Logout}
        iconDescription="Log out"
      >
        Log out
      </Button>
    </SideNavItems>
  </SideNav>

  <!-- Main content: Video Player and Transcription -->
  <div class="content">
    <div class="video-and-text">
      <video bind:this={videoElement} controls class="video-player">
        <track kind="captions" label="English" srcLang="en" src="" default />
        <track kind="subtitles" label="English" srcLang="en" src="" />
      </video>
      <div class="transcription">
        <Tabs>
          <Tab label="Plain text" />
          <Tab label="SRT format" />
          <svelte:fragment slot="content">
            <TabContent>
              <TextArea
                bind:value={transcribedText}
                rows={10}
                labelText="Transcribed Text"
                class="textarea"
              />
              <Button icon={Copy} on:click={handleCopyText}>Copy Text</Button>
            </TabContent>
            <TabContent>
              <TextArea
                bind:value={SRTFormat}
                rows={10}
                labelText="Transcribed Text on SRT Format"
                class="textarea"
              />
              <Button icon={Copy} on:click={handleCopySRT}>Copy Text</Button>
            </TabContent>
          </svelte:fragment>
        </Tabs>
      </div>
    </div>
  </div>
</div>

<style>
  .main-container {
    display: flex;
    height: 100vh;
  }

  :global(.logout-button) {
    position: absolute;
    bottom: 4rem;
    width: 100%;
  }

  .content {
    flex: 1;
    padding: 2rem;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    gap: 1rem;
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
