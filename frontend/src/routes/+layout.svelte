<!-- src/routes/layout.svelte -->
<script lang="ts">
    import AppHeader from '../components/AppHeader.svelte'; // Adjust path if necessary
  </script>
  
  <div class="app-container">
    <AppHeader />
    <main>
      <slot></slot> <!-- Content of nested routes will render here -->
    </main>
  </div>
  
  <style>
    .app-container {
      display: flex;
      flex-direction: column;
      min-height: 100vh;
    }
  
    main {
      flex-grow: 1;
      width: 100%;
      padding: 20px; /* Add padding as needed */
    }
  
  </style>