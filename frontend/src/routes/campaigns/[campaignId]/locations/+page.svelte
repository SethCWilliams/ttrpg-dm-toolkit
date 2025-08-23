<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { auth } from '$lib/stores/auth.js';
    import { currentCampaign } from '$lib/stores/campaigns.js';
    import { locationAPI, campaignAPI } from '$lib/api.js';
    import { goto } from '$app/navigation';
    import CreateLocationModal from '$lib/components/CreateLocationModal.svelte';

    let campaignId;
    let locations = [];
    let loading = true;
    let error = '';
    let searchTerm = '';
    let selectedType = '';
    let selectedStatus = '';
    let showCreateModal = false;

    // Pagination
    let currentPage = 1;
    let totalPages = 1;
    let totalLocations = 0;
    let itemsPerPage = 20;

    // Filters
    const locationTypes = ['region', 'settlement', 'structure', 'dungeon', 'wilderness'];
    const statusTypes = ['draft', 'active', 'historical', 'destroyed'];

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

        await loadLocations();
    });

    async function loadLocations() {
        try {
            loading = true;
            const params = {
                skip: (currentPage - 1) * itemsPerPage,
                limit: itemsPerPage
            };

            if (searchTerm) params.search = searchTerm;
            if (selectedType) params.location_type = selectedType;
            if (selectedStatus) params.status = selectedStatus;

            const response = await locationAPI.getLocations(campaignId, params);
            
            locations = response.items || [];
            totalLocations = response.total || 0;
            totalPages = Math.ceil(totalLocations / itemsPerPage);
        } catch (err) {
            error = err.message || 'Failed to load locations';
        } finally {
            loading = false;
        }
    }

    function handleSearch() {
        currentPage = 1;
        loadLocations();
    }

    function handleFilterChange() {
        currentPage = 1;
        loadLocations();
    }

    function clearFilters() {
        searchTerm = '';
        selectedType = '';
        selectedStatus = '';
        currentPage = 1;
        loadLocations();
    }

    function changePage(newPage) {
        if (newPage >= 1 && newPage <= totalPages) {
            currentPage = newPage;
            loadLocations();
        }
    }

    function handleLocationCreated(event) {
        showCreateModal = false;
        loadLocations(); // Refresh the list
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

    function buildHierarchyPath(location) {
        // This would need to be enhanced to show full path
        // For now, just show parent if exists
        return location.parent_location_id ? '← Has Parent' : '';
    }

    // Get available parent locations for the create modal
    async function getAvailableParents() {
        try {
            const response = await locationAPI.getLocations(campaignId, { limit: 100 });
            return response.items || [];
        } catch (err) {
            console.error('Failed to load parent locations:', err);
            return [];
        }
    }
</script>

<svelte:head>
    <title>Locations - {$currentCampaign?.name || 'Campaign'} - DM Toolkit</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
        <div>
            <button
                on:click={() => goto(`/campaigns/${campaignId}`)}
                class="text-gray-400 hover:text-white mb-2 flex items-center"
            >
                <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
                Back to Campaign
            </button>
            <h1 class="text-3xl font-bold text-white">Locations</h1>
            <p class="text-gray-400">Manage your world's geography and points of interest</p>
        </div>
        
        <button
            on:click={() => showCreateModal = true}
            class="btn btn-primary"
        >
            <svg class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            New Location
        </button>
    </div>

    <!-- Search and Filters -->
    <div class="card mb-6">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <!-- Search -->
            <div class="md:col-span-2">
                <div class="relative">
                    <input
                        type="text"
                        bind:value={searchTerm}
                        on:keydown={(e) => e.key === 'Enter' && handleSearch()}
                        class="input w-full pl-10"
                        placeholder="Search locations..."
                    />
                    <svg class="h-5 w-5 text-gray-400 absolute left-3 top-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                </div>
            </div>

            <!-- Type Filter -->
            <div>
                <select bind:value={selectedType} on:change={handleFilterChange} class="input w-full">
                    <option value="">All Types</option>
                    {#each locationTypes as type}
                        <option value={type}>{type.charAt(0).toUpperCase() + type.slice(1)}</option>
                    {/each}
                </select>
            </div>

            <!-- Status Filter -->
            <div>
                <select bind:value={selectedStatus} on:change={handleFilterChange} class="input w-full">
                    <option value="">All Status</option>
                    {#each statusTypes as status}
                        <option value={status}>{status.charAt(0).toUpperCase() + status.slice(1)}</option>
                    {/each}
                </select>
            </div>
        </div>

        <div class="flex items-center justify-between mt-4">
            <div class="flex items-center space-x-4">
                <button on:click={handleSearch} class="btn btn-primary btn-sm">
                    Search
                </button>
                <button on:click={clearFilters} class="btn btn-secondary btn-sm">
                    Clear Filters
                </button>
            </div>
            
            {#if totalLocations > 0}
                <div class="text-sm text-gray-400">
                    Showing {((currentPage - 1) * itemsPerPage) + 1}-{Math.min(currentPage * itemsPerPage, totalLocations)} of {totalLocations} locations
                </div>
            {/if}
        </div>
    </div>

    <!-- Results -->
    {#if error}
        <div class="card bg-red-900 border-red-700">
            <p class="text-red-100">{error}</p>
            <button on:click={loadLocations} class="btn btn-secondary mt-4">
                Try Again
            </button>
        </div>
    {:else if loading}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each Array(6) as _}
                <div class="card animate-pulse">
                    <div class="h-4 bg-gray-700 rounded mb-2"></div>
                    <div class="h-3 bg-gray-700 rounded w-2/3 mb-4"></div>
                    <div class="h-3 bg-gray-700 rounded w-1/2"></div>
                </div>
            {/each}
        </div>
    {:else if locations.length === 0}
        <div class="text-center py-12">
            <div class="text-6xl mb-4">🗺️</div>
            <h3 class="text-xl font-medium text-gray-300 mb-2">No locations yet</h3>
            <p class="text-gray-500 mb-6">Start building your world by creating your first location</p>
            <button
                on:click={() => showCreateModal = true}
                class="btn btn-primary"
            >
                Create First Location
            </button>
        </div>
    {:else}
        <!-- Location Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
            {#each locations as location}
                <a
                    href="/campaigns/{campaignId}/locations/{location.id}"
                    class="card hover:bg-gray-750 transition-colors group"
                >
                    <div class="flex items-start justify-between mb-3">
                        <div class="flex items-center space-x-3">
                            <div class="text-2xl">{getLocationIcon(location.type)}</div>
                            <div>
                                <h3 class="font-semibold text-white group-hover:text-red-400 transition-colors">
                                    {location.name}
                                </h3>
                                <p class="text-sm text-gray-400 capitalize">{location.type}</p>
                            </div>
                        </div>
                        
                        <div class="flex items-center space-x-2">
                            <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium text-white {getStatusColor(location.status)}">
                                {location.status}
                            </span>
                        </div>
                    </div>

                    {#if location.description}
                        <p class="text-gray-300 text-sm mb-3 line-clamp-2">{location.description}</p>
                    {/if}

                    <div class="flex items-center justify-between text-sm text-gray-500">
                        <div class="flex items-center space-x-4">
                            {#if location.population}
                                <span>👥 {location.population.toLocaleString()}</span>
                            {/if}
                            <span>{getVisibilityText(location.visibility)}</span>
                        </div>
                        
                        {#if buildHierarchyPath(location)}
                            <span class="text-xs">{buildHierarchyPath(location)}</span>
                        {/if}
                    </div>
                </a>
            {/each}
        </div>

        <!-- Pagination -->
        {#if totalPages > 1}
            <div class="flex items-center justify-center space-x-2">
                <button
                    on:click={() => changePage(currentPage - 1)}
                    disabled={currentPage === 1}
                    class="btn btn-secondary btn-sm"
                    class:opacity-50={currentPage === 1}
                    class:cursor-not-allowed={currentPage === 1}
                >
                    Previous
                </button>
                
                {#each Array(totalPages) as _, i}
                    {@const pageNum = i + 1}
                    {#if pageNum === 1 || pageNum === totalPages || (pageNum >= currentPage - 2 && pageNum <= currentPage + 2)}
                        <button
                            on:click={() => changePage(pageNum)}
                            class="btn btn-sm"
                            class:btn-primary={pageNum === currentPage}
                            class:btn-secondary={pageNum !== currentPage}
                        >
                            {pageNum}
                        </button>
                    {:else if pageNum === currentPage - 3 || pageNum === currentPage + 3}
                        <span class="text-gray-500">...</span>
                    {/if}
                {/each}
                
                <button
                    on:click={() => changePage(currentPage + 1)}
                    disabled={currentPage === totalPages}
                    class="btn btn-secondary btn-sm"
                    class:opacity-50={currentPage === totalPages}
                    class:cursor-not-allowed={currentPage === totalPages}
                >
                    Next
                </button>
            </div>
        {/if}
    {/if}
</div>

<!-- Create Location Modal -->
{#if showCreateModal}
    {#await getAvailableParents()}
        <CreateLocationModal
            {campaignId}
            availableParents={[]}
            on:created={handleLocationCreated}
            on:close={() => showCreateModal = false}
        />
    {:then availableParents}
        <CreateLocationModal
            {campaignId}
            {availableParents}
            on:created={handleLocationCreated}
            on:close={() => showCreateModal = false}
        />
    {:catch}
        <CreateLocationModal
            {campaignId}
            availableParents={[]}
            on:created={handleLocationCreated}
            on:close={() => showCreateModal = false}
        />
    {/await}
{/if}