<script lang="ts">
    import {
      Header,
      HeaderUtilities,
      HeaderGlobalAction,
      SkipToContent
    } from 'carbon-components-svelte';
    import "carbon-components-svelte/css/g90.css";
    import BrightnessContrast from "carbon-icons-svelte/lib/BrightnessContrast.svelte";


  </script>
  
  <Header company="BRAGI">
    <svelte:fragment slot="skip-to-content">
      <SkipToContent />
    </svelte:fragment>
    <HeaderUtilities>
      <HeaderGlobalAction
        icon={BrightnessContrast}
      />
    </HeaderUtilities>
  </Header>