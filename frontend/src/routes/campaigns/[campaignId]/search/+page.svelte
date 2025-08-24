<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { auth } from '$lib/stores/auth.js';
    import { currentCampaign } from '$lib/stores/campaigns.js';
    import { campaignAPI } from '$lib/api.js';
    import { goto } from '$app/navigation';
    import GlobalSearch from '$lib/components/GlobalSearch.svelte';

    let campaignId;
    let searchQuery = '';
    let searchResults = null;
    let loading = false;
    let error = '';

    // Reactive statement to get campaignId from page params
    $: campaignId = $page.params.campaignId;

    onMount(async () => {
        if (!$auth.user) {
            goto('/auth/login');
            return;
        }
        const urlParams = new URLSearchParams($page.url.search);
        searchQuery = urlParams.get('q') || '';

        if (searchQuery.trim()) {
            await performSearch();
        }
    });

    async function performSearch() {
        if (!searchQuery.trim() || !campaignId) return;

        try {
            loading = true;
            error = '';
            searchResults = await campaignAPI.globalSearch(campaignId, searchQuery, 100);
        } catch (err) {
            error = err.message || 'Failed to perform search';
            searchResults = null;
        } finally {
            loading = false;
        }
    }

    function getTypeIcon(type) {
        const icons = {
            npc: '👥',
            location: '📍',
            organization: '🏛️',
            plot_hook: '🎯',
            item: '⚔️',
            event: '📅',
            idea: '💡',
            session: '📝'
        };
        return icons[type] || '📄';
    }

    function getTypeName(type) {
        const names = {
            npc: 'NPC',
            location: 'Location',
            organization: 'Organization',
            plot_hook: 'Plot Hook',
            item: 'Item',
            event: 'Event',
            idea: 'Idea',
            session: 'Session Note'
        };
        return names[type] || 'Item';
    }

    function getTypeColor(type) {
        const colors = {
            npc: 'bg-blue-600 text-blue-100',
            location: 'bg-green-600 text-green-100',
            organization: 'bg-purple-600 text-purple-100',
            plot_hook: 'bg-orange-600 text-orange-100',
            item: 'bg-yellow-600 text-yellow-100',
            event: 'bg-red-600 text-red-100',
            idea: 'bg-pink-600 text-pink-100',
            session: 'bg-indigo-600 text-indigo-100'
        };
        return colors[type] || 'bg-gray-600 text-gray-300';
    }

    function highlightSearchTerm(text, searchTerm) {
        if (!text || !searchTerm) return text;
        
        const regex = new RegExp(`(${searchTerm})`, 'gi');
        return text.replace(regex, '<mark class="bg-yellow-200 text-yellow-800 px-1 rounded">$1</mark>');
    }

    // Reactive search when URL changes
    $: if ($page.url.search) {
        const urlParams = new URLSearchParams($page.url.search);
        const newQuery = urlParams.get('q') || '';
        if (newQuery !== searchQuery) {
            searchQuery = newQuery;
            if (searchQuery.trim()) {
                performSearch();
            }
        }
    }
</script>

<svelte:head>
    <title>Search Results - {$currentCampaign?.name || 'Campaign'} - DM Toolkit</title>
</svelte:head>

<div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="mb-8">
        <div class="flex items-center space-x-4 mb-6">
            <button
                on:click={() => goto(`/campaigns/${campaignId}`)}
                class="text-gray-400 hover:text-white flex items-center"
            >
                <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
                Back to Campaign
            </button>
        </div>

        <h1 class="text-3xl font-bold text-white mb-4">Search Results</h1>

        <!-- Search Bar -->
        <div class="max-w-2xl">
            {#if campaignId}
                <GlobalSearch 
                    {campaignId}
                    placeholder="Search NPCs, locations, events, and more..."
                />
            {:else}
                <div class="input pl-10 pr-4 w-full bg-gray-700 text-gray-500">
                    Loading search...
                </div>
            {/if}
        </div>
    </div>

    <!-- Search Results -->
    {#if loading}
        <div class="animate-pulse space-y-4">
            {#each Array(6) as _}
                <div class="card">
                    <div class="flex items-center space-x-4">
                        <div class="w-12 h-12 bg-gray-700 rounded"></div>
                        <div class="flex-1">
                            <div class="h-4 bg-gray-700 rounded w-1/3 mb-2"></div>
                            <div class="h-3 bg-gray-700 rounded w-2/3"></div>
                        </div>
                    </div>
                </div>
            {/each}
        </div>
    {:else if error}
        <div class="card bg-red-900 border-red-700">
            <div class="flex items-center justify-between">
                <div>
                    <h3 class="text-lg font-medium text-red-100">Search Error</h3>
                    <p class="text-red-200">{error}</p>
                </div>
                <button 
                    on:click={performSearch}
                    class="btn btn-secondary"
                >
                    Try Again
                </button>
            </div>
        </div>
    {:else if searchResults}
        <!-- Results Summary -->
        <div class="mb-6">
            {#if searchQuery}
                <p class="text-gray-400">
                    {#if searchResults.total_results === 0}
                        No results found for <span class="text-white font-medium">"{searchQuery}"</span>
                    {:else}
                        {searchResults.total_results} result{searchResults.total_results !== 1 ? 's' : ''} found for 
                        <span class="text-white font-medium">"{searchQuery}"</span>
                    {/if}
                </p>
            {/if}
        </div>

        {#if searchResults.total_results === 0}
            <div class="card text-center py-12">
                <svg class="mx-auto h-12 w-12 text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <h3 class="text-xl font-medium text-gray-300 mb-2">No results found</h3>
                <p class="text-gray-400 mb-6">Try adjusting your search terms or check the spelling.</p>
                <div class="space-y-2 text-sm text-gray-500">
                    <p><strong>Search tips:</strong></p>
                    <ul class="list-disc list-inside space-y-1">
                        <li>Try shorter or more general terms</li>
                        <li>Check for typos in your search</li>
                        <li>Use different keywords that might appear in names or descriptions</li>
                    </ul>
                </div>
            </div>
        {:else}
            <!-- Search Results by Category -->
            {#each Object.entries(searchResults.results) as [category, results]}
                {#if results.length > 0}
                    <div class="mb-8">
                        <!-- Category Header -->
                        <div class="flex items-center space-x-3 mb-4">
                            <span class="text-2xl">{getTypeIcon(category.slice(0, -1))}</span>
                            <h2 class="text-xl font-semibold text-white">
                                {getTypeName(category.slice(0, -1))}s ({results.length})
                            </h2>
                        </div>

                        <!-- Results Grid -->
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {#each results as result}
                                <a
                                    href={result.url}
                                    class="card hover:bg-gray-750 transition-colors group block"
                                >
                                    <div class="flex items-start space-x-4">
                                        <div class="flex-shrink-0">
                                            <div class="w-12 h-12 {getTypeColor(result.type)} rounded-lg flex items-center justify-center text-xl">
                                                {getTypeIcon(result.type)}
                                            </div>
                                        </div>
                                        <div class="flex-1 min-w-0">
                                            <div class="flex items-start justify-between">
                                                <div class="flex-1">
                                                    <h3 class="text-lg font-medium text-white group-hover:text-red-400 transition-colors line-clamp-1">
                                                        {@html highlightSearchTerm(result.name, searchQuery)}
                                                    </h3>
                                                    <p class="text-sm text-gray-400 mt-1 line-clamp-2">
                                                        {@html highlightSearchTerm(result.description, searchQuery)}
                                                    </p>
                                                    <div class="flex items-center mt-2">
                                                        <span class="px-2 py-1 rounded text-xs {getTypeColor(result.type)}">
                                                            {getTypeName(result.type)}
                                                        </span>
                                                    </div>
                                                </div>
                                                <div class="ml-4 flex-shrink-0">
                                                    <svg class="h-5 w-5 text-gray-400 group-hover:text-red-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                                                    </svg>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </a>
                            {/each}
                        </div>
                    </div>
                {/if}
            {/each}
        {/if}
    {:else}
        <!-- Initial state when no search has been performed -->
        <div class="card text-center py-12">
            <svg class="mx-auto h-12 w-12 text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <h3 class="text-xl font-medium text-gray-300 mb-2">Search Your Campaign</h3>
            <p class="text-gray-400">Use the search bar above to find NPCs, locations, items, and more.</p>
        </div>
    {/if}
</div>

<style>
    :global(.search-results mark) {
        background-color: #fef3c7;
        color: #92400e;
        padding: 0.125rem 0.25rem;
        border-radius: 0.25rem;
    }
</style>