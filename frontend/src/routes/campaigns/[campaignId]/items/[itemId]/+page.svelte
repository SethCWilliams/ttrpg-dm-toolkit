<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { auth } from '$lib/stores/auth.js';
    import { currentCampaign } from '$lib/stores/campaigns.js';
    import { itemAPI } from '$lib/api.js';
    import EditItemModal from '$lib/components/EditItemModal.svelte';

    let campaignId;
    let itemId;
    let item = null;
    let loading = true;
    let error = '';
    let showEditModal = false;
    let showDeleteConfirm = false;
    let deleting = false;

    onMount(async () => {
        if (!$auth.user) {
            goto('/auth/login');
            return;
        }

        campaignId = $page.params.campaignId;
        itemId = $page.params.itemId;
        await loadItem();
    });

    async function loadItem() {
        try {
            loading = true;
            item = await itemAPI.getItem(campaignId, itemId);
        } catch (err) {
            error = err.message || 'Failed to load item';
        } finally {
            loading = false;
        }
    }

    async function handleDelete() {
        try {
            deleting = true;
            await itemAPI.deleteItem(campaignId, itemId);
            goto(`/campaigns/${campaignId}/items`);
        } catch (err) {
            error = err.message || 'Failed to delete item';
        } finally {
            deleting = false;
            showDeleteConfirm = false;
        }
    }

    function handleItemUpdated(event) {
        item = event.detail.item;
        showEditModal = false;
    }

    function handleModalClose() {
        showEditModal = false;
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
        if (value === null || value === undefined) return 'Not specified';
        return `${value} gp`;
    }

    function formatWeight(weight) {
        if (weight === null || weight === undefined) return 'Not specified';
        return `${weight} lb${weight !== 1 ? 's' : ''}`;
    }

    function formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    function renderTemplateField(key, value, type = 'text') {
        if (!value) return 'Not specified';
        
        if (type === 'tags' && Array.isArray(value)) {
            return value.join(', ');
        }
        
        if (typeof value === 'string') {
            return capitalizeWords(value);
        }
        
        return value;
    }
</script>

<svelte:head>
    <title>{item?.name || 'Item'} - {$currentCampaign?.name || 'Campaign'} - DM Toolkit</title>
</svelte:head>

<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    {#if loading}
        <div class="animate-pulse">
            <div class="h-8 bg-gray-700 rounded w-1/3 mb-4"></div>
            <div class="h-4 bg-gray-700 rounded w-1/4 mb-8"></div>
            <div class="card">
                <div class="h-6 bg-gray-700 rounded w-1/2 mb-4"></div>
                <div class="h-4 bg-gray-700 rounded w-full mb-2"></div>
                <div class="h-4 bg-gray-700 rounded w-2/3"></div>
            </div>
        </div>
    {:else if error}
        <div class="card bg-red-900 border-red-700">
            <div class="flex items-center justify-between">
                <div>
                    <h3 class="text-lg font-medium text-red-100">Error</h3>
                    <p class="text-red-200">{error}</p>
                </div>
                <button 
                    on:click={loadItem}
                    class="btn btn-secondary"
                >
                    Try Again
                </button>
            </div>
        </div>
    {:else if item}
        <!-- Header -->
        <div class="mb-8">
            <div class="flex items-center space-x-4 mb-4">
                <button
                    on:click={() => goto(`/campaigns/${campaignId}/items`)}
                    class="text-gray-400 hover:text-white flex items-center"
                >
                    <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                    </svg>
                    Back to Items
                </button>

                <button
                    on:click={() => goto(`/campaigns/${campaignId}`)}
                    class="text-gray-400 hover:text-white"
                >
                    Campaign Dashboard
                </button>
            </div>

            <div class="flex items-start justify-between">
                <div class="flex-1">
                    <div class="flex items-center space-x-3 mb-2">
                        <h1 class="text-3xl font-bold text-white">{item.name}</h1>
                        {#if item.attunement_required}
                            <span class="px-3 py-1 rounded text-sm bg-yellow-600 text-yellow-100">
                                Requires Attunement
                            </span>
                        {/if}
                    </div>
                    
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

                    <p class="text-gray-400">
                        Created on {formatDate(item.created_at)}
                        {#if item.updated_at !== item.created_at}
                            • Updated on {formatDate(item.updated_at)}
                        {/if}
                    </p>
                </div>

                <div class="flex space-x-3">
                    <button
                        on:click={() => showEditModal = true}
                        class="btn btn-secondary"
                    >
                        <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                        Edit
                    </button>
                    <button
                        on:click={() => showDeleteConfirm = true}
                        class="btn bg-red-600 hover:bg-red-700 text-white"
                    >
                        <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                        Delete
                    </button>
                </div>
            </div>
        </div>

        <!-- Main Content -->
        <div class="space-y-6">
            <!-- Description -->
            {#if item.description}
                <div class="card">
                    <h2 class="text-xl font-semibold text-white mb-3">Description</h2>
                    <p class="text-gray-300 whitespace-pre-wrap">{item.description}</p>
                </div>
            {/if}

            <!-- Basic Properties -->
            <div class="card">
                <h2 class="text-xl font-semibold text-white mb-4">Properties</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div>
                        <dt class="text-sm font-medium text-gray-400">Value</dt>
                        <dd class="text-white">{formatValue(item.value)}</dd>
                    </div>
                    <div>
                        <dt class="text-sm font-medium text-gray-400">Weight</dt>
                        <dd class="text-white">{formatWeight(item.weight)}</dd>
                    </div>
                    <div>
                        <dt class="text-sm font-medium text-gray-400">Visibility</dt>
                        <dd class="text-white">{capitalizeWords(item.visibility)}</dd>
                    </div>
                    <div>
                        <dt class="text-sm font-medium text-gray-400">Status</dt>
                        <dd class="text-white">{capitalizeWords(item.status)}</dd>
                    </div>
                </div>
            </div>

            <!-- Ownership -->
            {#if item.current_owner_id || item.current_location_id}
                <div class="card">
                    <h2 class="text-xl font-semibold text-white mb-4">Current Location</h2>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {#if item.current_owner}
                            <div>
                                <dt class="text-sm font-medium text-gray-400">Owner</dt>
                                <dd class="text-white">
                                    {item.current_owner.name}
                                    {#if item.current_owner.occupation}
                                        <span class="text-gray-400">({item.current_owner.occupation})</span>
                                    {/if}
                                </dd>
                            </div>
                        {/if}
                        {#if item.current_location}
                            <div>
                                <dt class="text-sm font-medium text-gray-400">Location</dt>
                                <dd class="text-white">
                                    {item.current_location.name}
                                    <span class="text-gray-400">({capitalizeWords(item.current_location.type)})</span>
                                </dd>
                            </div>
                        {/if}
                    </div>
                </div>
            {/if}

            <!-- Type-specific Properties -->
            {#if item.mechanical_effects}
                <div class="card">
                    <h2 class="text-xl font-semibold text-white mb-4">
                        {capitalizeWords(item.type)} Properties
                    </h2>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {#each Object.entries(item.mechanical_effects) as [key, value]}
                            <div>
                                <dt class="text-sm font-medium text-gray-400">{capitalizeWords(key)}</dt>
                                <dd class="text-white">{renderTemplateField(key, value)}</dd>
                            </div>
                        {/each}
                    </div>
                </div>
            {/if}

            <!-- History -->
            {#if item.history}
                <div class="card">
                    <h2 class="text-xl font-semibold text-white mb-3">History</h2>
                    <p class="text-gray-300 whitespace-pre-wrap">{item.history}</p>
                </div>
            {/if}

            <!-- Notes -->
            {#if item.notes}
                <div class="card">
                    <h2 class="text-xl font-semibold text-white mb-3">DM Notes</h2>
                    <p class="text-gray-300 whitespace-pre-wrap">{item.notes}</p>
                </div>
            {/if}
        </div>
    {/if}
</div>

<!-- Edit Modal -->
{#if showEditModal && item}
    <EditItemModal 
        {campaignId}
        {item}
        on:updated={handleItemUpdated}
        on:close={handleModalClose}
    />
{/if}

<!-- Delete Confirmation Modal -->
{#if showDeleteConfirm}
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div class="bg-gray-800 rounded-lg max-w-md w-full p-6">
            <h3 class="text-xl font-semibold text-white mb-4">Delete Item</h3>
            <p class="text-gray-300 mb-6">
                Are you sure you want to delete "{item?.name}"? This action cannot be undone.
            </p>
            <div class="flex justify-end space-x-3">
                <button
                    on:click={() => showDeleteConfirm = false}
                    class="btn btn-secondary"
                    disabled={deleting}
                >
                    Cancel
                </button>
                <button
                    on:click={handleDelete}
                    class="btn bg-red-600 hover:bg-red-700 text-white"
                    disabled={deleting}
                >
                    {deleting ? 'Deleting...' : 'Delete'}
                </button>
            </div>
        </div>
    </div>
{/if}