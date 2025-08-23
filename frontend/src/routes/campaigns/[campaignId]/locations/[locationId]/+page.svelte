<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { auth } from '$lib/stores/auth.js';
    import { currentCampaign } from '$lib/stores/campaigns.js';
    import { locationAPI, campaignAPI, npcAPI } from '$lib/api.js';
    import { goto } from '$app/navigation';
    import EditLocationModal from '$lib/components/EditLocationModal.svelte';

    let campaignId;
    let locationId;
    let location = null;
    let relatedNPCs = [];
    let childLocations = [];
    let parentLocation = null;
    let loading = true;
    let error = '';
    let showEditModal = false;

    onMount(async () => {
        if (!$auth.user) {
            goto('/auth/login');
            return;
        }

        campaignId = $page.params.campaignId;
        locationId = parseInt($page.params.locationId);
        
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

        await loadLocation();
        await loadRelatedData();
    });

    async function loadLocation() {
        try {
            loading = true;
            location = await locationAPI.getLocation(campaignId, locationId);
        } catch (err) {
            error = err.message || 'Failed to load location';
        } finally {
            loading = false;
        }
    }

    async function loadRelatedData() {
        if (!location) return;

        try {
            // Load NPCs in this location
            const npcResponse = await npcAPI.getNPCs(campaignId, { location_id: locationId, limit: 100 });
            relatedNPCs = npcResponse.items || [];

            // Load child locations
            const childResponse = await locationAPI.getLocations(campaignId, { parent_location_id: locationId, limit: 100 });
            childLocations = childResponse.items || [];

            // Load parent location if exists
            if (location.parent_location_id) {
                try {
                    parentLocation = await locationAPI.getLocation(campaignId, location.parent_location_id);
                } catch (err) {
                    console.error('Failed to load parent location:', err);
                }
            }
        } catch (err) {
            console.error('Failed to load related data:', err);
        }
    }

    function handleLocationUpdated(event) {
        showEditModal = false;
        location = event.detail.location;
        // Reload related data in case relationships changed
        loadRelatedData();
    }

    async function handleDelete() {
        if (!confirm('Are you sure you want to delete this location? This action cannot be undone.')) {
            return;
        }

        try {
            await locationAPI.deleteLocation(campaignId, locationId);
            goto(`/campaigns/${campaignId}/locations`);
        } catch (err) {
            alert('Failed to delete location: ' + err.message);
        }
    }

    // Get available parent locations for the edit modal
    async function getAvailableParents() {
        try {
            const response = await locationAPI.getLocations(campaignId, { limit: 100 });
            return response.items || [];
        } catch (err) {
            console.error('Failed to load parent locations:', err);
            return [];
        }
    }

    function getLocationIcon(type) {
        switch (type) {
            case 'region': return '🗺️';
            case 'settlement': return '🏘️';
            case 'structure': return '🏢';
            case 'dungeon': return '🏰';
            case 'wilderness': return '🌲';
            default: return '📍';
        }
    }

    function getStatusColor(status) {
        switch (status) {
            case 'active': return 'bg-green-600';
            case 'draft': return 'bg-yellow-600';
            case 'historical': return 'bg-blue-600';
            case 'destroyed': return 'bg-red-600';
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
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    function renderTags(tags) {
        if (!Array.isArray(tags)) return [];
        return tags;
    }

    function capitalizeWords(str) {
        if (!str) return '';
        return str.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    }
</script>

<svelte:head>
    <title>{location?.name || 'Location'} - DM Toolkit</title>
</svelte:head>

<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    {#if loading}
        <div class="animate-pulse">
            <div class="h-8 bg-gray-700 rounded w-1/3 mb-4"></div>
            <div class="h-6 bg-gray-700 rounded w-1/2 mb-8"></div>
            <div class="space-y-4">
                {#each Array(4) as _}
                    <div class="card">
                        <div class="h-6 bg-gray-700 rounded mb-2"></div>
                        <div class="h-4 bg-gray-700 rounded w-3/4"></div>
                    </div>
                {/each}
            </div>
        </div>
    {:else if error}
        <div class="card bg-red-900 border-red-700">
            <p class="text-red-100">{error}</p>
            <button 
                on:click={() => goto(`/campaigns/${campaignId}/locations`)}
                class="btn btn-secondary mt-4"
            >
                Back to Locations
            </button>
        </div>
    {:else if location}
        <!-- Header -->
        <div class="mb-8">
            <button
                on:click={() => goto(`/campaigns/${campaignId}/locations`)}
                class="text-gray-400 hover:text-white mb-4 flex items-center"
            >
                <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
                Back to Locations
            </button>
            
            <div class="flex items-start justify-between">
                <div class="flex items-start space-x-4 flex-1">
                    <div class="text-4xl">{getLocationIcon(location.type)}</div>
                    <div class="flex-1">
                        <h1 class="text-3xl font-bold text-white mb-2">{location.name}</h1>
                        
                        <div class="flex items-center space-x-3 mb-4">
                            <span class="px-2 py-1 text-xs font-medium rounded {getStatusColor(location.status)} text-white">
                                {location.status}
                            </span>
                            <span class="px-2 py-1 text-xs font-medium rounded bg-gray-700 text-gray-300">
                                {capitalizeWords(location.type)}
                            </span>
                            <span class="text-sm text-gray-400">
                                {getVisibilityText(location.visibility)}
                            </span>
                        </div>

                        <!-- Hierarchy -->
                        {#if parentLocation}
                            <div class="mb-4">
                                <span class="text-sm text-gray-500">Part of:</span>
                                <a 
                                    href="/campaigns/{campaignId}/locations/{parentLocation.id}"
                                    class="text-red-400 hover:text-red-300 ml-1"
                                >
                                    {parentLocation.name}
                                </a>
                            </div>
                        {/if}
                    </div>
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
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Main Content -->
            <div class="lg:col-span-2 space-y-6">
                <!-- Description -->
                {#if location.description}
                    <div class="card">
                        <h2 class="text-xl font-semibold text-white mb-4">Description</h2>
                        <p class="text-gray-300 whitespace-pre-wrap">{location.description}</p>
                    </div>
                {/if}

                <!-- History -->
                {#if location.history}
                    <div class="card">
                        <h2 class="text-xl font-semibold text-white mb-4">History</h2>
                        <p class="text-gray-300 whitespace-pre-wrap">{location.history}</p>
                    </div>
                {/if}

                <!-- Type-specific Information -->
                <div class="card">
                    <h2 class="text-xl font-semibold text-white mb-4">Details</h2>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {#if location.population}
                            <div>
                                <span class="text-sm text-gray-500">Population</span>
                                <p class="text-gray-300">{location.population.toLocaleString()}</p>
                            </div>
                        {/if}
                        
                        {#if location.government_type}
                            <div>
                                <span class="text-sm text-gray-500">Government</span>
                                <p class="text-gray-300">{capitalizeWords(location.government_type)}</p>
                            </div>
                        {/if}
                        
                        {#if location.economic_status}
                            <div>
                                <span class="text-sm text-gray-500">Economic Status</span>
                                <p class="text-gray-300">{capitalizeWords(location.economic_status)}</p>
                            </div>
                        {/if}
                    </div>
                </div>

                <!-- Notable Features -->
                {#if location.notable_features && renderTags(location.notable_features).length > 0}
                    <div class="card">
                        <h2 class="text-xl font-semibold text-white mb-4">Notable Features</h2>
                        <div class="flex flex-wrap gap-2">
                            {#each renderTags(location.notable_features) as feature}
                                <span class="px-3 py-1 bg-gray-700 text-gray-300 text-sm rounded">
                                    {feature}
                                </span>
                            {/each}
                        </div>
                    </div>
                {/if}

                <!-- Trade Goods (for settlements) -->
                {#if location.trade_goods && renderTags(location.trade_goods).length > 0}
                    <div class="card">
                        <h2 class="text-xl font-semibold text-white mb-4">Trade Goods</h2>
                        <div class="flex flex-wrap gap-2">
                            {#each renderTags(location.trade_goods) as good}
                                <span class="px-3 py-1 bg-green-700 text-green-300 text-sm rounded">
                                    {good}
                                </span>
                            {/each}
                        </div>
                    </div>
                {/if}

                <!-- Defenses -->
                {#if location.defenses}
                    <div class="card">
                        <h2 class="text-xl font-semibold text-white mb-4">Defenses</h2>
                        <p class="text-gray-300 whitespace-pre-wrap">{location.defenses}</p>
                    </div>
                {/if}

                <!-- Ambient Description -->
                {#if location.ambient_description}
                    <div class="card">
                        <h2 class="text-xl font-semibold text-white mb-4">Atmosphere</h2>
                        <p class="text-gray-300 whitespace-pre-wrap">{location.ambient_description}</p>
                    </div>
                {/if}

                <!-- Notes -->
                {#if location.notes}
                    <div class="card">
                        <h2 class="text-xl font-semibold text-white mb-4">Notes</h2>
                        <p class="text-gray-300 whitespace-pre-wrap">{location.notes}</p>
                    </div>
                {/if}
            </div>

            <!-- Sidebar -->
            <div class="space-y-6">
                <!-- Child Locations -->
                {#if childLocations.length > 0}
                    <div class="card">
                        <h2 class="text-lg font-semibold text-white mb-4">Sub-locations</h2>
                        <div class="space-y-3">
                            {#each childLocations as child}
                                <a
                                    href="/campaigns/{campaignId}/locations/{child.id}"
                                    class="block p-3 bg-gray-700 hover:bg-gray-600 rounded transition-colors"
                                >
                                    <div class="flex items-center space-x-2">
                                        <span class="text-lg">{getLocationIcon(child.type)}</span>
                                        <div>
                                            <div class="text-sm font-medium text-white">{child.name}</div>
                                            <div class="text-xs text-gray-400 capitalize">{child.type}</div>
                                        </div>
                                    </div>
                                </a>
                            {/each}
                        </div>
                    </div>
                {/if}

                <!-- Related NPCs -->
                {#if relatedNPCs.length > 0}
                    <div class="card">
                        <h2 class="text-lg font-semibold text-white mb-4">NPCs Here</h2>
                        <div class="space-y-3">
                            {#each relatedNPCs as npc}
                                <a
                                    href="/campaigns/{campaignId}/npcs/{npc.id}"
                                    class="block p-3 bg-gray-700 hover:bg-gray-600 rounded transition-colors"
                                >
                                    <div class="text-sm font-medium text-white">{npc.name}</div>
                                    {#if npc.occupation}
                                        <div class="text-xs text-gray-400">{npc.occupation}</div>
                                    {/if}
                                </a>
                            {/each}
                        </div>
                    </div>
                {/if}

                <!-- Meta Information -->
                <div class="card">
                    <h2 class="text-lg font-semibold text-white mb-4">Information</h2>
                    <div class="space-y-3 text-sm">
                        <div>
                            <span class="text-gray-500">Created:</span>
                            <div class="text-gray-300">{formatDate(location.created_at)}</div>
                        </div>
                        <div>
                            <span class="text-gray-500">Last Updated:</span>
                            <div class="text-gray-300">{formatDate(location.updated_at)}</div>
                        </div>
                        <div>
                            <span class="text-gray-500">ID:</span>
                            <div class="text-gray-300">#{location.id}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    {/if}
</div>

<!-- Edit Location Modal -->
{#if showEditModal && location}
    {#await getAvailableParents()}
        <EditLocationModal
            {campaignId}
            {location}
            availableParents={[]}
            on:updated={handleLocationUpdated}
            on:close={() => showEditModal = false}
        />
    {:then availableParents}
        <EditLocationModal
            {campaignId}
            {location}
            {availableParents}
            on:updated={handleLocationUpdated}
            on:close={() => showEditModal = false}
        />
    {:catch}
        <EditLocationModal
            {campaignId}
            {location}
            availableParents={[]}
            on:updated={handleLocationUpdated}
            on:close={() => showEditModal = false}
        />
    {/await}
{/if}