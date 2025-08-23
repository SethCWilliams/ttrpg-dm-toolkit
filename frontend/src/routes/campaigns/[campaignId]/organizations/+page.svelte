<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { auth } from '$lib/stores/auth.js';
    import { currentCampaign } from '$lib/stores/campaigns.js';
    import { organizationAPI, campaignAPI } from '$lib/api.js';
    import { goto } from '$app/navigation';
    import CreateOrganizationModal from '$lib/components/CreateOrganizationModal.svelte';

    let campaignId;
    let organizations = [];
    let loading = true;
    let error = '';
    let showCreateModal = false;

    // Filtering and search
    let searchTerm = '';
    let selectedType = '';
    let selectedScope = '';
    let selectedStatus = '';
    let selectedVisibility = '';

    // Pagination
    let currentPage = 1;
    let totalPages = 1;
    let totalOrganizations = 0;
    const pageSize = 20;

    const organizationTypes = [
        { value: 'guild', label: 'Guild', icon: '🏛️' },
        { value: 'government', label: 'Government', icon: '🏛️' },
        { value: 'religion', label: 'Religious Order', icon: '⛪' },
        { value: 'criminal', label: 'Criminal Organization', icon: '🗡️' },
        { value: 'military', label: 'Military Unit', icon: '⚔️' },
        { value: 'academic', label: 'Academic Institution', icon: '📚' },
        { value: 'merchant', label: 'Merchant Organization', icon: '💰' }
    ];

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

        await loadOrganizations();
    });

    async function loadOrganizations() {
        try {
            loading = true;
            const params = {
                skip: (currentPage - 1) * pageSize,
                limit: pageSize
            };

            if (searchTerm) params.search = searchTerm;
            if (selectedType) params.type = selectedType;
            if (selectedScope) params.scope = selectedScope;
            if (selectedStatus) params.status = selectedStatus;
            if (selectedVisibility) params.visibility = selectedVisibility;

            const response = await organizationAPI.getOrganizations(campaignId, params);
            organizations = response.items || [];
            totalOrganizations = response.total || 0;
            totalPages = Math.ceil(totalOrganizations / pageSize);
        } catch (err) {
            error = err.message || 'Failed to load organizations';
        } finally {
            loading = false;
        }
    }

    function handleSearch() {
        currentPage = 1;
        loadOrganizations();
    }

    function handleFilterChange() {
        currentPage = 1;
        loadOrganizations();
    }

    function clearFilters() {
        searchTerm = '';
        selectedType = '';
        selectedScope = '';
        selectedStatus = '';
        selectedVisibility = '';
        currentPage = 1;
        loadOrganizations();
    }

    function nextPage() {
        if (currentPage < totalPages) {
            currentPage++;
            loadOrganizations();
        }
    }

    function prevPage() {
        if (currentPage > 1) {
            currentPage--;
            loadOrganizations();
        }
    }

    function handleOrganizationCreated(event) {
        showCreateModal = false;
        organizations = [event.detail.organization, ...organizations];
        totalOrganizations++;
    }

    function getOrganizationIcon(type) {
        const orgType = organizationTypes.find(t => t.value === type);
        return orgType?.icon || '🏢';
    }

    function getStatusColor(status) {
        switch (status) {
            case 'active': return 'bg-green-600';
            case 'draft': return 'bg-yellow-600';
            case 'historical': return 'bg-blue-600';
            case 'disbanded': return 'bg-red-600';
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

    function capitalizeWords(str) {
        if (!str) return '';
        return str.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    }

    function truncateText(text, maxLength = 100) {
        if (!text) return '';
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }
</script>

<svelte:head>
    <title>Organizations - {$currentCampaign?.name || 'Campaign'} - DM Toolkit</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="mb-8">
        <div class="flex items-center justify-between">
            <div>
                <h1 class="text-3xl font-bold text-white">Organizations</h1>
                <p class="text-gray-400 mt-1">
                    Manage guilds, governments, and other organizations in {$currentCampaign?.name}
                </p>
            </div>
            <button
                on:click={() => showCreateModal = true}
                class="btn btn-primary"
            >
                <svg class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                Create Organization
            </button>
        </div>
    </div>

    <!-- Search and Filters -->
    <div class="card mb-6">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
            <!-- Search -->
            <div class="lg:col-span-2">
                <label class="block text-sm font-medium text-gray-300 mb-2">Search</label>
                <div class="flex">
                    <input
                        type="text"
                        bind:value={searchTerm}
                        class="input flex-1 rounded-r-none"
                        placeholder="Search organizations..."
                        on:keydown={(e) => e.key === 'Enter' && handleSearch()}
                    />
                    <button
                        on:click={handleSearch}
                        class="btn btn-secondary rounded-l-none border-l-0"
                    >
                        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                    </button>
                </div>
            </div>

            <!-- Type Filter -->
            <div>
                <label class="block text-sm font-medium text-gray-300 mb-2">Type</label>
                <select
                    bind:value={selectedType}
                    on:change={handleFilterChange}
                    class="input w-full"
                >
                    <option value="">All Types</option>
                    {#each organizationTypes as type}
                        <option value={type.value}>{type.label}</option>
                    {/each}
                </select>
            </div>

            <!-- Scope Filter -->
            <div>
                <label class="block text-sm font-medium text-gray-300 mb-2">Scope</label>
                <select
                    bind:value={selectedScope}
                    on:change={handleFilterChange}
                    class="input w-full"
                >
                    <option value="">All Scopes</option>
                    <option value="local">Local</option>
                    <option value="regional">Regional</option>
                    <option value="national">National</option>
                    <option value="international">International</option>
                </select>
            </div>

            <!-- Status Filter -->
            <div>
                <label class="block text-sm font-medium text-gray-300 mb-2">Status</label>
                <select
                    bind:value={selectedStatus}
                    on:change={handleFilterChange}
                    class="input w-full"
                >
                    <option value="">All Statuses</option>
                    <option value="draft">Draft</option>
                    <option value="active">Active</option>
                    <option value="historical">Historical</option>
                    <option value="disbanded">Disbanded</option>
                </select>
            </div>

            <!-- Actions -->
            <div class="flex items-end">
                <button
                    on:click={clearFilters}
                    class="btn btn-secondary w-full"
                >
                    Clear Filters
                </button>
            </div>
        </div>
    </div>

    <!-- Results Summary -->
    <div class="flex items-center justify-between mb-6">
        <p class="text-sm text-gray-400">
            Showing {organizations.length} of {totalOrganizations} organizations
            {#if currentPage > 1}
                (page {currentPage} of {totalPages})
            {/if}
        </p>
    </div>

    {#if error}
        <div class="card bg-red-900 border-red-700">
            <p class="text-red-100">{error}</p>
        </div>
    {:else if loading}
        <!-- Loading State -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each Array(6) as _}
                <div class="card animate-pulse">
                    <div class="h-6 bg-gray-700 rounded mb-3"></div>
                    <div class="h-4 bg-gray-700 rounded mb-2"></div>
                    <div class="h-4 bg-gray-700 rounded w-3/4"></div>
                </div>
            {/each}
        </div>
    {:else if organizations.length === 0}
        <!-- Empty State -->
        <div class="text-center py-12">
            <div class="text-6xl mb-4">🏢</div>
            <h3 class="text-xl font-semibold text-white mb-2">No organizations found</h3>
            <p class="text-gray-400 mb-6">
                {searchTerm || selectedType || selectedScope || selectedStatus || selectedVisibility
                    ? 'Try adjusting your search criteria'
                    : 'Start building your world by creating your first organization'}
            </p>
            <button
                on:click={() => showCreateModal = true}
                class="btn btn-primary"
            >
                Create Your First Organization
            </button>
        </div>
    {:else}
        <!-- Organizations Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {#each organizations as org}
                <a
                    href="/campaigns/{campaignId}/organizations/{org.id}"
                    class="card hover:bg-gray-750 transition-colors group"
                >
                    <div class="flex items-start justify-between mb-3">
                        <div class="flex items-center space-x-3 flex-1">
                            <div class="text-2xl">
                                {getOrganizationIcon(org.type)}
                            </div>
                            <div class="flex-1 min-w-0">
                                <h3 class="font-semibold text-white group-hover:text-red-400 transition-colors truncate">
                                    {org.name}
                                </h3>
                                <div class="flex items-center space-x-2 mt-1">
                                    <span class="text-xs text-gray-400">
                                        {capitalizeWords(org.type)}
                                    </span>
                                    {#if org.scope}
                                        <span class="text-xs text-gray-500">•</span>
                                        <span class="text-xs text-gray-400">
                                            {capitalizeWords(org.scope)}
                                        </span>
                                    {/if}
                                </div>
                            </div>
                        </div>
                        
                        <div class="flex flex-col items-end space-y-1">
                            <span class="px-2 py-1 text-xs font-medium rounded {getStatusColor(org.status)} text-white">
                                {org.status}
                            </span>
                        </div>
                    </div>

                    {#if org.reputation}
                        <p class="text-sm text-gray-300 mb-3">
                            {truncateText(org.reputation)}
                        </p>
                    {/if}

                    <div class="flex items-center justify-between text-xs text-gray-500">
                        <div class="flex items-center space-x-4">
                            {#if org.membership_size}
                                <span>{capitalizeWords(org.membership_size)} Size</span>
                            {/if}
                            {#if org.influence_level}
                                <span>{capitalizeWords(org.influence_level)} Influence</span>
                            {/if}
                        </div>
                        <span>{getVisibilityText(org.visibility)}</span>
                    </div>
                </a>
            {/each}
        </div>

        <!-- Pagination -->
        {#if totalPages > 1}
            <div class="flex items-center justify-between">
                <button
                    on:click={prevPage}
                    disabled={currentPage === 1}
                    class="btn btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                    </svg>
                    Previous
                </button>

                <span class="text-sm text-gray-400">
                    Page {currentPage} of {totalPages}
                </span>

                <button
                    on:click={nextPage}
                    disabled={currentPage === totalPages}
                    class="btn btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    Next
                    <svg class="h-4 w-4 ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                    </svg>
                </button>
            </div>
        {/if}
    {/if}
</div>

<!-- Create Organization Modal -->
{#if showCreateModal}
    <CreateOrganizationModal
        {campaignId}
        on:created={handleOrganizationCreated}
        on:close={() => showCreateModal = false}
    />
{/if}