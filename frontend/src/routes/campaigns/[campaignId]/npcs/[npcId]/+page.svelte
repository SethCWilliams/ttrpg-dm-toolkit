<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { auth } from '$lib/stores/auth.js';
    import { currentCampaign } from '$lib/stores/campaigns.js';
    import { npcAPI, campaignAPI } from '$lib/api.js';
    import { goto } from '$app/navigation';
    import EditNPCModal from '$lib/components/EditNPCModal.svelte';
    import RelationshipManager from '$lib/components/RelationshipManager.svelte';

    let campaignId;
    let npcId;
    let npc = null;
    let loading = true;
    let error = '';
    let showEditModal = false;
    let relationships = [];
    let showRelationshipManager = false;

    onMount(async () => {
        if (!$auth.user) {
            goto('/auth/login');
            return;
        }

        campaignId = $page.params.campaignId;
        npcId = $page.params.npcId;
        
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

        await loadNPC();
        await loadRelationships();
    });

    async function loadNPC() {
        try {
            loading = true;
            npc = await npcAPI.getNPC(campaignId, npcId);
        } catch (err) {
            error = err.message || 'Failed to load NPC';
        } finally {
            loading = false;
        }
    }

    async function loadRelationships() {
        try {
            const response = await npcAPI.getNPCRelationships(campaignId, npcId);
            relationships = response.relationships || [];
        } catch (err) {
            console.error('Failed to load relationships:', err);
        }
    }

    function handleNPCUpdated() {
        showEditModal = false;
        loadNPC();
    }

    function handleRelationshipsSaved(event) {
        relationships = event.detail.relationships;
        showRelationshipManager = false;
        // Update the NPC object with the new relationships
        if (npc) {
            npc.relationships = relationships;
        }
    }

    async function handleDelete() {
        if (!confirm('Are you sure you want to delete this NPC? This action cannot be undone.')) {
            return;
        }

        try {
            await npcAPI.deleteNPC(campaignId, npcId);
            goto(`/campaigns/${campaignId}/npcs`);
        } catch (err) {
            alert('Failed to delete NPC: ' + err.message);
        }
    }

    function getStatusColor(status) {
        switch (status) {
            case 'active': return 'bg-green-600';
            case 'draft': return 'bg-yellow-600';
            case 'historical': return 'bg-blue-600';
            case 'dead': return 'bg-red-600';
            default: return 'bg-gray-600';
        }
    }

    function getVisibilityText(visibility) {
        switch (visibility) {
            case 'player_known': return 'Known to Players';
            case 'partially_known': return 'Partially Known';
            case 'dm_only': return 'DM Only';
            default: return 'Unknown';
        }
    }

    function formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }
</script>

<svelte:head>
    <title>{npc?.name || 'NPC'} - {$currentCampaign?.name || 'Campaign'} - DM Toolkit</title>
</svelte:head>

<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    {#if loading}
        <div class="animate-pulse">
            <div class="h-8 bg-gray-700 rounded w-1/3 mb-4"></div>
            <div class="card">
                <div class="h-4 bg-gray-700 rounded mb-2"></div>
                <div class="h-4 bg-gray-700 rounded w-3/4 mb-4"></div>
                <div class="h-20 bg-gray-700 rounded"></div>
            </div>
        </div>
    {:else if error}
        <div class="card bg-red-900 border-red-700">
            <p class="text-red-100">{error}</p>
            <button 
                on:click={() => goto(`/campaigns/${campaignId}/npcs`)}
                class="btn btn-secondary mt-4"
            >
                Back to NPCs
            </button>
        </div>
    {:else if npc}
        <!-- Header -->
        <div class="flex items-center justify-between mb-8">
            <div>
                <button
                    on:click={() => goto(`/campaigns/${campaignId}/npcs`)}
                    class="text-gray-400 hover:text-white mb-2 flex items-center"
                >
                    <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                    </svg>
                    Back to NPCs
                </button>
                <h1 class="text-3xl font-bold text-white">{npc.name}</h1>
                {#if npc.occupation}
                    <p class="text-lg text-gray-400">{npc.occupation}</p>
                {/if}
            </div>
            
            <div class="flex items-center space-x-3">
                <button
                    on:click={() => showEditModal = true}
                    class="btn btn-secondary"
                >
                    Edit
                </button>
                <button
                    on:click={handleDelete}
                    class="btn btn-danger"
                >
                    Delete
                </button>
            </div>
        </div>

        <!-- Status Bar -->
        <div class="flex items-center space-x-4 mb-6">
            <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium text-white {getStatusColor(npc.status)}">
                {npc.status}
            </span>
            <span class="text-sm text-gray-400">
                {getVisibilityText(npc.visibility)}
            </span>
        </div>

        <!-- Main Content -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <!-- Main Info -->
            <div class="lg:col-span-2 space-y-6">
                <!-- Basic Information -->
                <div class="card">
                    <h2 class="text-xl font-semibold text-white mb-4">Basic Information</h2>
                    <div class="grid grid-cols-2 gap-4">
                        {#if npc.race}
                            <div>
                                <span class="text-sm text-gray-500">Race</span>
                                <p class="text-gray-300">{npc.race}</p>
                            </div>
                        {/if}
                        
                        {#if npc.gender}
                            <div>
                                <span class="text-sm text-gray-500">Gender</span>
                                <p class="text-gray-300">{npc.gender}</p>
                            </div>
                        {/if}
                        
                        {#if npc.age}
                            <div>
                                <span class="text-sm text-gray-500">Age</span>
                                <p class="text-gray-300">{npc.age} years old</p>
                            </div>
                        {/if}
                        
                        {#if npc.occupation}
                            <div>
                                <span class="text-sm text-gray-500">Occupation</span>
                                <p class="text-gray-300">{npc.occupation}</p>
                            </div>
                        {/if}
                    </div>
                </div>

                <!-- Personality -->
                <div class="card">
                    <h2 class="text-xl font-semibold text-white mb-4">Personality</h2>
                    
                    {#if npc.personality_traits && npc.personality_traits.length > 0}
                        <div class="mb-4">
                            <h3 class="text-sm font-medium text-gray-400 mb-2">Traits</h3>
                            <div class="flex flex-wrap gap-2">
                                {#each npc.personality_traits as trait}
                                    <span class="inline-block bg-gray-700 text-gray-300 text-sm px-3 py-1 rounded">
                                        {trait}
                                    </span>
                                {/each}
                            </div>
                        </div>
                    {/if}

                    <div class="space-y-4">
                        {#if npc.ideals}
                            <div>
                                <h3 class="text-sm font-medium text-gray-400 mb-1">Ideals</h3>
                                <p class="text-gray-300">{npc.ideals}</p>
                            </div>
                        {/if}

                        {#if npc.bonds}
                            <div>
                                <h3 class="text-sm font-medium text-gray-400 mb-1">Bonds</h3>
                                <p class="text-gray-300">{npc.bonds}</p>
                            </div>
                        {/if}

                        {#if npc.flaws}
                            <div>
                                <h3 class="text-sm font-medium text-gray-400 mb-1">Flaws</h3>
                                <p class="text-gray-300">{npc.flaws}</p>
                            </div>
                        {/if}
                    </div>
                </div>

                <!-- Background -->
                {#if npc.background}
                    <div class="card">
                        <h2 class="text-xl font-semibold text-white mb-4">Background</h2>
                        <p class="text-gray-300 whitespace-pre-wrap">{npc.background}</p>
                    </div>
                {/if}

                <!-- Appearance -->
                {#if npc.appearance_description}
                    <div class="card">
                        <h2 class="text-xl font-semibold text-white mb-4">Appearance</h2>
                        <p class="text-gray-300 whitespace-pre-wrap">{npc.appearance_description}</p>
                    </div>
                {/if}

                <!-- Voice & Mannerisms -->
                {#if npc.voice_description}
                    <div class="card">
                        <h2 class="text-xl font-semibold text-white mb-4">Voice & Mannerisms</h2>
                        <p class="text-gray-300 whitespace-pre-wrap">{npc.voice_description}</p>
                    </div>
                {/if}

                <!-- Notes -->
                {#if npc.notes}
                    <div class="card">
                        <h2 class="text-xl font-semibold text-white mb-4">Notes</h2>
                        <p class="text-gray-300 whitespace-pre-wrap">{npc.notes}</p>
                    </div>
                {/if}
            </div>

            <!-- Sidebar -->
            <div class="space-y-6">
                <!-- Relationships -->
                <div class="card">
                    <div class="flex items-center justify-between mb-4">
                        <h2 class="text-lg font-semibold text-white">Relationships</h2>
                        <button
                            on:click={() => showRelationshipManager = !showRelationshipManager}
                            class="btn btn-sm {showRelationshipManager ? 'btn-secondary' : 'btn-primary'}"
                        >
                            {showRelationshipManager ? 'View' : 'Manage'}
                        </button>
                    </div>
                    
                    {#if showRelationshipManager}
                        <RelationshipManager
                            {campaignId}
                            {npcId}
                            npcName={npc.name}
                            initialRelationships={relationships}
                            on:saved={handleRelationshipsSaved}
                        />
                    {:else if relationships.length > 0}
                        <div class="space-y-3">
                            {#each relationships as relationship}
                                <div class="border-l-4 border-red-600 pl-3">
                                    <div class="flex items-center space-x-2 mb-1">
                                        <span class="text-sm font-medium text-gray-300">
                                            {relationship.target_name || `NPC #${relationship.target_id}`}
                                        </span>
                                        <span class="text-xs text-gray-500">
                                            ({relationship.relationship_type})
                                        </span>
                                        <span class="text-xs text-gray-400 capitalize">
                                            {relationship.strength}
                                        </span>
                                        {#if relationship.public_knowledge}
                                            <span class="text-xs text-blue-400" title="Public Knowledge">👁️</span>
                                        {/if}
                                    </div>
                                    {#if relationship.target_occupation}
                                        <div class="text-xs text-gray-500 mb-1">
                                            {relationship.target_occupation}
                                        </div>
                                    {/if}
                                    {#if relationship.description}
                                        <div class="text-sm text-gray-400">
                                            {relationship.description}
                                        </div>
                                    {/if}
                                </div>
                            {/each}
                        </div>
                    {:else}
                        <div class="text-center py-4 text-gray-500">
                            <div class="text-2xl mb-2">👥</div>
                            <p class="text-sm">No relationships yet</p>
                            <button
                                on:click={() => showRelationshipManager = true}
                                class="btn btn-primary btn-sm mt-2"
                            >
                                Add Relationships
                            </button>
                        </div>
                    {/if}
                </div>

                <!-- Game Stats -->
                {#if npc.stats}
                    <div class="card">
                        <h2 class="text-lg font-semibold text-white mb-4">Game Stats</h2>
                        <div class="space-y-2 text-sm">
                            {#each Object.entries(npc.stats) as [stat, value]}
                                <div class="flex justify-between">
                                    <span class="text-gray-400 capitalize">{stat.replace('_', ' ')}</span>
                                    <span class="text-gray-300">{value}</span>
                                </div>
                            {/each}
                        </div>
                    </div>
                {/if}

                <!-- Meta Information -->
                <div class="card">
                    <h2 class="text-lg font-semibold text-white mb-4">Information</h2>
                    <div class="space-y-2 text-sm">
                        <div>
                            <span class="text-gray-500">Created</span>
                            <p class="text-gray-300">{formatDate(npc.created_at)}</p>
                        </div>
                        <div>
                            <span class="text-gray-500">Last Updated</span>
                            <p class="text-gray-300">{formatDate(npc.updated_at)}</p>
                        </div>
                        <div>
                            <span class="text-gray-500">Status</span>
                            <p class="text-gray-300 capitalize">{npc.status}</p>
                        </div>
                        <div>
                            <span class="text-gray-500">Visibility</span>
                            <p class="text-gray-300">{getVisibilityText(npc.visibility)}</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    {/if}
</div>

{#if showEditModal && npc}
    <EditNPCModal
        {campaignId}
        {npc}
        on:close={() => showEditModal = false}
        on:updated={handleNPCUpdated}
    />
{/if}