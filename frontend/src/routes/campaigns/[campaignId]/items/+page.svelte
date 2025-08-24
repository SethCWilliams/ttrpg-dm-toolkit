<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { auth } from '$lib/stores/auth.js';
    import { currentCampaign } from '$lib/stores/campaigns.js';
    import { itemAPI } from '$lib/api.js';
    import { goto } from '$app/navigation';
    import CreateItemModal from '$lib/components/CreateItemModal.svelte';

    let campaignId;
    let items = [];
    let total = 0;
    let loading = true;
    let error = '';
    let searchQuery = '';
    let selectedType = '';
    let selectedRarity = '';
    let selectedStatus = '';
    let selectedOwner = '';
    let selectedLocation = '';
    let showAttunementOnly = false;
    let showCreateModal = false;

    const itemTypes = [
        { value: '', label: 'All Types' },
        { value: 'weapon', label: 'Weapon' },
        { value: 'armor', label: 'Armor' },
        { value: 'tool', label: 'Tool' },
        { value: 'treasure', label: 'Treasure' },
        { value: 'consumable', label: 'Consumable' },
        { value: 'quest_item', label: 'Quest Item' },
        { value: 'artifact', label: 'Artifact' }
    ];

    const rarityOptions = [
        { value: '', label: 'All Rarities' },
        { value: 'common', label: 'Common' },
        { value: 'uncommon', label: 'Uncommon' },
        { value: 'rare', label: 'Rare' },
        { value: 'very_rare', label: 'Very Rare' },
        { value: 'legendary', label: 'Legendary' },
        { value: 'artifact', label: 'Artifact' }
    ];

    const statusOptions = [
        { value: '', label: 'All Status' },
        { value: 'draft', label: 'Draft' },
        { value: 'active', label: 'Active' },
        { value: 'lost', label: 'Lost' },
        { value: 'destroyed', label: 'Destroyed' }
    ];

    onMount(async () => {
        if (!$auth.user) {
            goto('/auth/login');
            return;
        }

        campaignId = $page.params.campaignId;
        await loadItems();
    });

    async function loadItems() {
        try {
            loading = true;
            const params = {
                limit: 100
            };
            
            // Only add parameters that have actual values
            if (searchQuery) params.search = searchQuery;
            if (selectedType) params.type = selectedType;
            if (selectedRarity) params.rarity = selectedRarity;
            if (selectedStatus) params.status = selectedStatus;
            if (showAttunementOnly) params.attunement_required = true;
            
            const response = await itemAPI.getItems(campaignId, params);
            items = response.items || [];
            total = response.total || 0;
        } catch (err) {
            error = err.message || 'Failed to load items';
        } finally {
            loading = false;
        }
    }

    function handleSearch() {
        loadItems();
    }

    function handleFilterChange() {
        loadItems();
    }

    function getRarityBadgeClass(rarity) {
        const classes = {
            common: 'bg-gray-600 text-gray-300',
            uncommon: 'bg-green-600 text-green-100',
            rare: 'bg-blue-600 text-blue-100',
            very_rare: 'bg-purple-600 text-purple-100',
            legendary: 'bg-orange-600 text-orange-100',
            artifact: 'bg-red-600 text-red-100'
        };
        return classes[rarity] || 'bg-gray-600 text-gray-300';
    }

    function getStatusBadgeClass(status) {
        const classes = {
            draft: 'bg-gray-600 text-gray-300',
            active: 'bg-green-600 text-green-100',
            lost: 'bg-yellow-600 text-yellow-100',
            destroyed: 'bg-red-600 text-red-100'
        };
        return classes[status] || 'bg-gray-600 text-gray-300';
    }

    function capitalizeWords(str) {
        if (!str) return '';
        return str.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    function formatValue(value) {
        if (value === null || value === undefined) return '';
        return `${value} gp`;
    }

    function formatWeight(weight) {
        if (weight === null || weight === undefined) return '';
        return `${weight} lb${weight !== 1 ? 's' : ''}`;
    }

    function handleItemCreated(event) {
        showCreateModal = false;
        loadItems();
    }

    function handleModalClose() {
        showCreateModal = false;
    }
</script>

<svelte:head>
    <title>Items - {$currentCampaign?.name || 'Campaign'} - DM Toolkit</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="mb-8">
        <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
                <button
                    on:click={() => goto(`/campaigns/${campaignId}`)}
                    class="text-gray-400 hover:text-white flex items-center"
                >
                    <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                    </svg>
                    Back to Campaign
                </button>
                
                <div>
                    <h1 class="text-3xl font-bold text-white">Items</h1>
                    <p class="text-gray-400">Manage weapons, armor, treasures, and magical items</p>
                </div>
            </div>
            
            <button
                on:click={() => showCreateModal = true}
                class="btn btn-primary"
            >
                <svg class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                Create Item
            </button>
        </div>
    </div>

    <!-- Filters -->
    <div class="card mb-6">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
            <div class="lg:col-span-2">
                <label class="block text-sm font-medium text-gray-300 mb-2">Search</label>
                <div class="relative">
                    <input
                        type="text"
                        bind:value={searchQuery}
                        on:input={handleSearch}
                        placeholder="Search items..."
                        class="input pl-10"
                    />
                    <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                </div>
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-300 mb-2">Type</label>
                <select bind:value={selectedType} on:change={handleFilterChange} class="input">
                    {#each itemTypes as type}
                        <option value={type.value}>{type.label}</option>
                    {/each}
                </select>
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-300 mb-2">Rarity</label>
                <select bind:value={selectedRarity} on:change={handleFilterChange} class="input">
                    {#each rarityOptions as rarity}
                        <option value={rarity.value}>{rarity.label}</option>
                    {/each}
                </select>
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-300 mb-2">Status</label>
                <select bind:value={selectedStatus} on:change={handleFilterChange} class="input">
                    {#each statusOptions as status}
                        <option value={status.value}>{status.label}</option>
                    {/each}
                </select>
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-300 mb-2">Filters</label>
                <label class="flex items-center">
                    <input
                        type="checkbox"
                        bind:checked={showAttunementOnly}
                        on:change={handleFilterChange}
                        class="mr-2"
                    />
                    <span class="text-sm text-gray-300">Attunement Only</span>
                </label>
            </div>
        </div>
    </div>

    <!-- Results Summary -->
    <div class="flex items-center justify-between mb-6">
        <p class="text-gray-400">
            {#if loading}
                Loading items...
            {:else}
                Showing {items.length} of {total} items
            {/if}
        </p>
    </div>

    <!-- Items List -->
    {#if loading}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each Array(6) as _}
                <div class="card animate-pulse">
                    <div class="h-6 bg-gray-700 rounded w-3/4 mb-2"></div>
                    <div class="h-4 bg-gray-700 rounded w-1/2 mb-4"></div>
                    <div class="h-3 bg-gray-700 rounded w-full mb-2"></div>
                    <div class="h-3 bg-gray-700 rounded w-2/3"></div>
                </div>
            {/each}
        </div>
    {:else if error}
        <div class="card bg-red-900 border-red-700">
            <p class="text-red-100">{error}</p>
            <button 
                on:click={loadItems}
                class="btn btn-secondary mt-4"
            >
                Try Again
            </button>
        </div>
    {:else if items.length === 0}
        <div class="card text-center py-12">
            <svg class="mx-auto h-12 w-12 text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
            <h3 class="text-xl font-medium text-gray-300 mb-2">No items found</h3>
            <p class="text-gray-400 mb-6">Create your first item to start building your treasure hoard.</p>
            <button 
                on:click={() => showCreateModal = true}
                class="btn btn-primary"
            >
                Create Item
            </button>
        </div>
    {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each items as item}
                <a 
                    href="/campaigns/{campaignId}/items/{item.id}"
                    class="card hover:bg-gray-750 transition-colors group"
                >
                    <div class="flex items-start justify-between mb-3">
                        <h3 class="text-lg font-semibold text-white group-hover:text-red-400 transition-colors line-clamp-2">
                            {item.name}
                        </h3>
                        {#if item.attunement_required}
                            <span class="text-xs bg-yellow-600 text-yellow-100 px-2 py-1 rounded ml-2 flex-shrink-0">
                                Attunement
                            </span>
                        {/if}
                    </div>
                    
                    {#if item.description}
                        <p class="text-gray-400 text-sm mb-4 line-clamp-3">
                            {item.description}
                        </p>
                    {/if}

                    <div class="flex flex-wrap gap-2 mb-4">
                        {#if item.type}
                            <span class="px-2 py-1 rounded text-xs bg-blue-600 text-blue-100">
                                {capitalizeWords(item.type)}
                            </span>
                        {/if}
                        
                        {#if item.rarity}
                            <span class="px-2 py-1 rounded text-xs {getRarityBadgeClass(item.rarity)}">
                                {capitalizeWords(item.rarity)}
                            </span>
                        {/if}
                        
                        <span class="px-2 py-1 rounded text-xs {getStatusBadgeClass(item.status)}">
                            {capitalizeWords(item.status)}
                        </span>
                    </div>

                    <div class="flex items-center justify-between text-xs text-gray-500">
                        <div class="flex space-x-4">
                            {#if item.value}
                                <span>{formatValue(item.value)}</span>
                            {/if}
                            {#if item.weight}
                                <span>{formatWeight(item.weight)}</span>
                            {/if}
                        </div>
                        <span>
                            {new Date(item.created_at).toLocaleDateString()}
                        </span>
                    </div>
                </a>
            {/each}
        </div>
    {/if}
</div>

{#if showCreateModal}
    <CreateItemModal 
        {campaignId}
        on:created={handleItemCreated}
        on:close={handleModalClose}
    />
{/if}