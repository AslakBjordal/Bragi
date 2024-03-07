<script>
  import "carbon-components-svelte/css/all.css";
  import { TextInput, Button } from "carbon-components-svelte";
</script>

<body>
  <div class="input-container">
    <div class="inputbox">
      <TextInput placeholder="Insert Video link" />
      <Button>Caption Video</Button>
    </div>
  </div>
</body>

<style>
  .inputbox {
    width: 400px;
    display: flex;
  }
  .input-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
  }
</style>
