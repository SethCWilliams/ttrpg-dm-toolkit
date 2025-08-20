<script>
    import { createEventDispatcher } from 'svelte';
    import { campaignAPI } from '$lib/api.js';

    export let campaign;

    const dispatch = createEventDispatcher();

    let showDeleteModal = false;
    let deleting = false;

    function handleSelect() {
        dispatch('select');
    }

    async function handleDelete() {
        if (!confirm('Are you sure you want to delete this campaign? This action cannot be undone.')) {
            return;
        }

        try {
            deleting = true;
            await campaignAPI.deleteCampaign(campaign.id);
            dispatch('refresh');
        } catch (error) {
            alert('Failed to delete campaign: ' + error.message);
        } finally {
            deleting = false;
        }
    }

    function formatDate(dateString) {
        return new Date(dateString).toLocaleDateString();
    }
</script>

<div class="card hover:bg-gray-750 transition-colors cursor-pointer group">
    <div on:click={handleSelect} class="mb-4">
        <h3 class="text-lg font-semibold text-white mb-2 group-hover:text-red-400">
            {campaign.name}
        </h3>
        
        {#if campaign.description}
            <p class="text-gray-400 text-sm mb-3 line-clamp-2">
                {campaign.description}
            </p>
        {/if}

        {#if campaign.world_name}
            <p class="text-xs text-gray-500 mb-2">
                World: <span class="text-gray-400">{campaign.world_name}</span>
            </p>
        {/if}

        {#if campaign.current_date}
            <p class="text-xs text-gray-500 mb-3">
                Date: <span class="text-gray-400">{campaign.current_date}</span>
            </p>
        {/if}

        <!-- Stats -->
        {#if campaign.stats}
            <div class="grid grid-cols-2 gap-2 text-xs">
                <div class="text-gray-500">
                    NPCs: <span class="text-gray-300">{campaign.stats.npc_count || 0}</span>
                </div>
                <div class="text-gray-500">
                    Locations: <span class="text-gray-300">{campaign.stats.location_count || 0}</span>
                </div>
                <div class="text-gray-500">
                    Organizations: <span class="text-gray-300">{campaign.stats.organization_count || 0}</span>
                </div>
                <div class="text-gray-500">
                    Plot Hooks: <span class="text-gray-300">{campaign.stats.plot_hook_count || 0}</span>
                </div>
            </div>
        {/if}
    </div>

    <!-- Actions -->
    <div class="flex items-center justify-between pt-4 border-t border-gray-700">
        <span class="text-xs text-gray-500">
            Created {formatDate(campaign.created_at)}
        </span>
        
        <button
            on:click|stopPropagation={handleDelete}
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