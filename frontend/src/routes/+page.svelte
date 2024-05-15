<script lang="ts">
  import 'carbon-components-svelte/css/all.css';
  import LogoGithub from 'carbon-icons-svelte/lib/LogoGithub.svelte';
  import Login from 'carbon-icons-svelte/lib/Login.svelte';

  import {
    TextInput,
    Button,
    FluidForm,
    PasswordInput,
    Tabs,
    Tab,
    TabContent,
  } from 'carbon-components-svelte';
  import { sendRequest } from '../utils';
  import { redirect } from '@sveltejs/kit';
  import { onMount } from 'svelte';

  let email = '';
  let password = '';
  let repeatPassword = '';

  interface UserCredentials {
    email: string;
    password: string;
  }

  // Check if user already signed in
  onMount(async () => {
    const res = await sendRequest('GET', '/me');
    console.log(res);
    if (res.id) {
      window.location.href = '/youtubetranscribe';
    }
  });

  async function handleLogin(event: Event) {
    event.preventDefault();

    const res = await sendRequest('POST', '/users:login', { email, password });
    if (res.error) {
      console.error('Error logging in:', res.error);
    } else {
      window.location.href = '/youtubetranscribe';
    }
  }

  $: passwordsMatch = password === repeatPassword;

  function registerUser(event: Event) {
    event.preventDefault();
    if (!passwordsMatch) {
      console.log('Passwords do not match.');
      return; // Prevent the form from submitting
    }
    console.log('Registering user...', { email, password });
    // Implement registration logic here
  }

  function loginWithGitHub(event: Event) {
    event.preventDefault();
    console.log('Logging in with GitHub...');
    // Integrate GitHub OAuth flow here
  }
</script>

<div class="bx--grid bx--grid--full-width">
  <div class="bx--row">
    <div class="bx--tabs-wrapper">
      <Tabs autoWidth>
        <Tab label="Login" />
        <Tab label="Create user" />
        <svelte:fragment slot="content">
          <TabContent>
            <FluidForm>
              <TextInput
                bind:value={email}
                labelText="Email"
                placeholder="Enter email..."
                required
              />
              <PasswordInput
                bind:value={password}
                labelText="Password"
                placeholder="Enter password..."
                required
              />
              <Button on:click={handleLogin} icon={Login}>Log In</Button>
              <Button
                kind="tertiary"
                on:click={loginWithGitHub}
                icon={LogoGithub}>Login with GitHub</Button
              >
            </FluidForm>
          </TabContent>

          <TabContent>
            <FluidForm>
              <TextInput
                bind:value={email}
                labelText="Email"
                placeholder="Enter email..."
                required
              />
              <PasswordInput
                bind:value={password}
                labelText="Password"
                placeholder="Enter password..."
                required
              />
              <PasswordInput
                bind:value={repeatPassword}
                labelText="Repeat Password"
                placeholder="Repeat password..."
                required
              />
              <Button on:click={registerUser}>Register</Button>
              <Button
                kind="tertiary"
                on:click={loginWithGitHub}
                icon={LogoGithub}>Login with GitHub</Button
              >
            </FluidForm>
          </TabContent>
        </svelte:fragment>
      </Tabs>
    </div>
  </div>
</div>

<style>
  .bx--row {
    justify-content: center;
    padding-top: 20rem;
  }

  .bx--tabs-wrapper {
    width: 100%;
    max-width: 400px;
  }
</style>
