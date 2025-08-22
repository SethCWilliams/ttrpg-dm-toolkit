<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { auth } from '$lib/stores/auth.js';
    import { currentCampaign } from '$lib/stores/campaigns.js';
    import { npcAPI, campaignAPI } from '$lib/api.js';
    import { goto } from '$app/navigation';
    import NPCCard from '$lib/components/NPCCard.svelte';
    import CreateNPCModal from '$lib/components/CreateNPCModal.svelte';

    let campaignId;
    let npcs = [];
    let loading = true;
    let error = '';
    let showCreateModal = false;

    // Search and filter state
    let searchTerm = '';
    let statusFilter = '';
    let visibilityFilter = '';
    let filteredNPCs = [];

    onMount(async () => {
        if (!$auth.user) {
            goto('/auth/login');
            return;
        }

        campaignId = $page.params.campaignId;
        
        // Load campaign info if not already loaded
        if (!$currentCampaign || $currentCampaign.id != campaignId) {
            try {
                const campaign = await campaignAPI.getCampaign(campaignId);
                currentCampaign.set(campaign);
            } catch (err) {
                error = 'Campaign not found';
                return;
            }
        }

        await loadNPCs();
    });

    async function loadNPCs() {
        try {
            loading = true;
            const response = await npcAPI.getNPCs(campaignId);
            npcs = response.items || [];
            filterNPCs();
        } catch (err) {
            error = err.message || 'Failed to load NPCs';
        } finally {
            loading = false;
        }
    }

    function filterNPCs() {
        filteredNPCs = npcs.filter(npc => {
            const matchesSearch = !searchTerm || 
                npc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                (npc.occupation && npc.occupation.toLowerCase().includes(searchTerm.toLowerCase())) ||
                (npc.background && npc.background.toLowerCase().includes(searchTerm.toLowerCase()));
            
            const matchesStatus = !statusFilter || npc.status === statusFilter;
            const matchesVisibility = !visibilityFilter || npc.visibility === visibilityFilter;
            
            return matchesSearch && matchesStatus && matchesVisibility;
        });
    }

    function handleNPCCreated() {
        showCreateModal = false;
        loadNPCs();
    }

    function handleNPCClick(npc) {
        goto(`/campaigns/${campaignId}/npcs/${npc.id}`);
    }

    // Reactive filtering
    $: {
        if (npcs.length > 0) {
            filterNPCs();
        }
    }
</script>

<svelte:head>
    <title>NPCs - {$currentCampaign?.name || 'Campaign'} - DM Toolkit</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="mb-8">
        <div class="flex items-center justify-between mb-4">
            <div>
                <h1 class="text-3xl font-bold text-white mb-2">NPCs</h1>
                <p class="text-gray-400">
                    {$currentCampaign?.name || 'Campaign'} • {filteredNPCs.length} characters
                </p>
            </div>
            <button 
                on:click={() => showCreateModal = true}
                class="btn btn-primary"
            >
                New NPC
            </button>
        </div>

        <!-- Search and Filters -->
        <div class="card mb-6">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div class="md:col-span-2">
                    <label for="search" class="block text-sm font-medium text-gray-300 mb-2">
                        Search NPCs
                    </label>
                    <input
                        id="search"
                        type="text"
                        bind:value={searchTerm}
                        class="input w-full"
                        placeholder="Search by name, occupation, or background..."
                    />
                </div>
                
                <div>
                    <label for="status" class="block text-sm font-medium text-gray-300 mb-2">
                        Status
                    </label>
                    <select
                        id="status"
                        bind:value={statusFilter}
                        class="input w-full"
                    >
                        <option value="">All Statuses</option>
                        <option value="draft">Draft</option>
                        <option value="active">Active</option>
                        <option value="historical">Historical</option>
                        <option value="dead">Dead</option>
                    </select>
                </div>
                
                <div>
                    <label for="visibility" class="block text-sm font-medium text-gray-300 mb-2">
                        Visibility
                    </label>
                    <select
                        id="visibility"
                        bind:value={visibilityFilter}
                        class="input w-full"
                    >
                        <option value="">All Visibility</option>
                        <option value="dm_only">DM Only</option>
                        <option value="partially_known">Partially Known</option>
                        <option value="player_known">Player Known</option>
                    </select>
                </div>
            </div>
        </div>
    </div>

    <!-- Content -->
    {#if loading}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each Array(6) as _}
                <div class="card animate-pulse">
                    <div class="h-4 bg-gray-700 rounded mb-2"></div>
                    <div class="h-3 bg-gray-700 rounded w-3/4 mb-4"></div>
                    <div class="h-2 bg-gray-700 rounded w-1/2 mb-2"></div>
                    <div class="h-2 bg-gray-700 rounded w-2/3"></div>
                </div>
            {/each}
        </div>
    {:else if error}
        <div class="card bg-red-900 border-red-700">
            <p class="text-red-100">{error}</p>
            <button 
                on:click={loadNPCs}
                class="btn btn-secondary mt-4"
            >
                Try Again
            </button>
        </div>
    {:else if filteredNPCs.length === 0}
        <div class="text-center py-12">
            <div class="mb-4">
                <svg class="mx-auto h-16 w-16 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
            </div>
            <h3 class="text-lg font-medium text-gray-300 mb-2">
                {npcs.length === 0 ? 'No NPCs yet' : 'No NPCs match your filters'}
            </h3>
            <p class="text-gray-500 mb-6">
                {npcs.length === 0 ? 'Start building your world by creating your first NPC' : 'Try adjusting your search or filters'}
            </p>
            {#if npcs.length === 0}
                <button 
                    on:click={() => showCreateModal = true}
                    class="btn btn-primary"
                >
                    Create Your First NPC
                </button>
            {:else}
                <button 
                    on:click={() => { searchTerm = ''; statusFilter = ''; visibilityFilter = ''; }}
                    class="btn btn-secondary"
                >
                    Clear Filters
                </button>
            {/if}
        </div>
    {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each filteredNPCs as npc}
                <NPCCard 
                    {npc} 
                    on:click={() => handleNPCClick(npc)}
                    on:refresh={loadNPCs}
                />
            {/each}
        </div>
    {/if}
</div>

{#if showCreateModal}
    <CreateNPCModal
        {campaignId}
        on:close={() => showCreateModal = false}
        on:created={handleNPCCreated}
    />
{/if}