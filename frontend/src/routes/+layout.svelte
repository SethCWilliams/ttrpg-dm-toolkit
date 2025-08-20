<script>
    import '../app.css';
    import { onMount } from 'svelte';
    import { auth } from '$lib/stores/auth.js';
    import Navigation from '$lib/components/Navigation.svelte';

    onMount(() => {
        auth.init();
    });
</script>

<div class="min-h-screen bg-gray-900">
    <Navigation />
    
    <main>
        <slot />
    </main>
</div>