<script>
    import { createEventDispatcher } from 'svelte';
    
    export let isLocked = false;
    export let fieldName = '';
    export let size = 'h-4 w-4';
    
    const dispatch = createEventDispatcher();
    
    function toggleLock() {
        dispatch('toggle');
    }
</script>

<button
    type="button"
    on:click={toggleLock}
    class="text-gray-400 hover:text-white transition-colors ml-2"
    title="{isLocked ? `Unlock ${fieldName} field (will be randomized)` : `Lock ${fieldName} field (keep current value)`}"
>
    {#if isLocked}
        <svg class="{size} text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
    {:else}
        <svg class="{size}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z" />
        </svg>
    {/if}
</button>