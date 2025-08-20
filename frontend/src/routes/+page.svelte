<script>
    import { auth } from '$lib/stores/auth.js';
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';

    let loading = true;

    onMount(() => {
        const unsubscribe = auth.subscribe(authState => {
            loading = authState.loading;
            
            if (!authState.loading) {
                if (authState.user) {
                    goto('/dashboard');
                } else {
                    goto('/auth/login');
                }
            }
        });

        return unsubscribe;
    });
</script>

<svelte:head>
    <title>DM Toolkit</title>
</svelte:head>

{#if loading}
    <div class="flex items-center justify-center min-h-screen">
        <div class="text-center">
            <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-red-600 mx-auto mb-4"></div>
            <p class="text-gray-400">Loading...</p>
        </div>
    </div>
{:else}
    <div class="flex items-center justify-center min-h-screen">
        <div class="text-center">
            <h1 class="text-4xl font-bold text-red-600 mb-4">DM Toolkit</h1>
            <p class="text-gray-400">Redirecting...</p>
        </div>
    </div>
{/if}