<script lang="ts">
  import 'carbon-components-svelte/css/all.css';
  import BrightnessContrast from 'carbon-icons-svelte/lib/BrightnessContrast.svelte';
  import {
    Header,
    HeaderUtilities,
    HeaderAction,
    HeaderPanelLinks,
    HeaderPanelDivider,
    HeaderPanelLink,
    SkipToContent,
    Theme,
  } from 'carbon-components-svelte';

  type CarbonTheme = 'white' | 'g10' | 'g80' | 'g90' | 'g100';
  let theme: CarbonTheme = 'g90'; // This state must be reactive for Theme component
  let isOpen = false; // State for app switcher panel

  // Function to set the theme reactively
  function setTheme(selectedTheme: CarbonTheme) {
    theme = selectedTheme;
    //  close the switcher panel after selection
    isOpen = false;
  }
</script>

<Header company="BRAGI" href="/newcaption">
  <svelte:fragment slot="skip-to-content">
    <SkipToContent />
  </svelte:fragment>
  <HeaderUtilities>
    <HeaderAction bind:isOpen aria-label="Switcher" icon={BrightnessContrast}>
      <HeaderPanelLinks>
        <HeaderPanelDivider>Themes</HeaderPanelDivider>
        <!-- Direct theme switch links -->
        <HeaderPanelLink on:click={() => setTheme('white')}
          >White Theme</HeaderPanelLink
        >
        <HeaderPanelLink on:click={() => setTheme('g10')}
          >Gray 10 Theme</HeaderPanelLink
        >
        <HeaderPanelLink on:click={() => setTheme('g80')}
          >Gray 80 Theme</HeaderPanelLink
        >
        <HeaderPanelLink on:click={() => setTheme('g90')}
          >Gray 90 Theme</HeaderPanelLink
        >
        <HeaderPanelLink on:click={() => setTheme('g100')}
          >Gray 100 Theme</HeaderPanelLink
        >
      </HeaderPanelLinks>
    </HeaderAction>
    <!-- Bind the Theme component to the reactive theme variable -->
    <Theme bind:theme persist persistKey="__carbon-theme" />
  </HeaderUtilities>
</Header>
