<script>
    import { createEventDispatcher } from 'svelte';
    import { npcAPI } from '$lib/api.js';

    export let npc;

    const dispatch = createEventDispatcher();

    let deleting = false;

    function handleClick() {
        dispatch('click');
    }

    async function handleDelete(event) {
        event.stopPropagation();
        
        if (!confirm('Are you sure you want to delete this NPC? This action cannot be undone.')) {
            return;
        }

        try {
            deleting = true;
            await npcAPI.deleteNPC(npc.campaign_id, npc.id);
            dispatch('refresh');
        } catch (error) {
            alert('Failed to delete NPC: ' + error.message);
        } finally {
            deleting = false;
        }
    }

    function getStatusColor(status) {
        switch (status) {
            case 'active': return 'text-green-400';
            case 'draft': return 'text-yellow-400';
            case 'historical': return 'text-blue-400';
            case 'dead': return 'text-red-400';
            default: return 'text-gray-400';
        }
    }

    function getVisibilityIcon(visibility) {
        switch (visibility) {
            case 'player_known': return '👁️';
            case 'partially_known': return '👁️‍🗨️';
            case 'dm_only': return '🔒';
            default: return '❓';
        }
    }

    function formatDate(dateString) {
        return new Date(dateString).toLocaleDateString();
    }
</script>

<div class="card hover:bg-gray-750 transition-colors cursor-pointer group" on:click={handleClick}>
    <div class="mb-4">
        <!-- Header with name and status -->
        <div class="flex items-start justify-between mb-2">
            <h3 class="text-lg font-semibold text-white group-hover:text-red-400 transition-colors">
                {npc.name}
            </h3>
            <div class="flex items-center space-x-2">
                <span class="text-sm {getStatusColor(npc.status)} capitalize">
                    {npc.status}
                </span>
                <span title="{npc.visibility}" class="text-sm">
                    {getVisibilityIcon(npc.visibility)}
                </span>
            </div>
        </div>

        <!-- Basic Info -->
        <div class="space-y-1 mb-3">
            {#if npc.race || npc.gender || npc.age}
                <p class="text-sm text-gray-400">
                    {npc.race || 'Unknown race'}
                    {#if npc.gender}, {npc.gender}{/if}
                    {#if npc.age}, {npc.age} years old{/if}
                </p>
            {/if}
            
            {#if npc.occupation}
                <p class="text-sm text-gray-300">
                    <span class="text-gray-500">Occupation:</span> {npc.occupation}
                </p>
            {/if}
        </div>

        <!-- Personality Traits -->
        {#if npc.personality_traits && npc.personality_traits.length > 0}
            <div class="mb-3">
                <div class="flex flex-wrap gap-1">
                    {#each npc.personality_traits.slice(0, 3) as trait}
                        <span class="inline-block bg-gray-700 text-gray-300 text-xs px-2 py-1 rounded">
                            {trait}
                        </span>
                    {/each}
                    {#if npc.personality_traits.length > 3}
                        <span class="inline-block bg-gray-600 text-gray-400 text-xs px-2 py-1 rounded">
                            +{npc.personality_traits.length - 3} more
                        </span>
                    {/if}
                </div>
            </div>
        {/if}

        <!-- Background snippet -->
        {#if npc.background}
            <p class="text-gray-400 text-sm line-clamp-2 mb-3">
                {npc.background}
            </p>
        {/if}

        <!-- Relationships count -->
        {#if npc.relationships && npc.relationships.length > 0}
            <p class="text-xs text-gray-500">
                {npc.relationships.length} relationship{npc.relationships.length !== 1 ? 's' : ''}
            </p>
        {/if}
    </div>

    <!-- Actions -->
    <div class="flex items-center justify-between pt-4 border-t border-gray-700">
        <span class="text-xs text-gray-500">
            Created {formatDate(npc.created_at)}
        </span>
        
        <button
            on:click={handleDelete}
            disabled={deleting}
            class="text-red-400 hover:text-red-300 text-xs {deleting ? 'opacity-50' : ''}"
        >
            {deleting ? 'Deleting...' : 'Delete'}
        </button>
    </div>
</div>

<style>
    .line-clamp-2 {
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
</style>