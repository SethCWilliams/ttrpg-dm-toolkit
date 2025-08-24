<script>
    import { createEventDispatcher } from 'svelte';
    import { campaignAPI } from '$lib/api.js';
    import { goto } from '$app/navigation';

    export let campaignId;
    export let placeholder = 'Search campaign...';

    const dispatch = createEventDispatcher();

    let searchQuery = '';
    let searchResults = null;
    let loading = false;
    let showDropdown = false;
    let searchTimeout;
    let searchInput;
    let selectedIndex = -1;

    // Reactive search - trigger search when query changes
    $: if (searchQuery.trim() && searchQuery.length >= 2 && campaignId) {
        performSearch();
    } else {
        searchResults = null;
        showDropdown = false;
    }

    async function performSearch() {
        // Debounce search requests
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(async () => {
            if (!searchQuery.trim() || searchQuery.length < 2 || !campaignId) return;

            try {
                loading = true;
                const results = await campaignAPI.globalSearch(campaignId, searchQuery, 5);
                searchResults = results;
                showDropdown = true;
                selectedIndex = -1;
            } catch (err) {
                console.error('Search failed:', err);
                searchResults = null;
                showDropdown = false;
            } finally {
                loading = false;
            }
        }, 300);
    }

    function handleSubmit() {
        if (searchQuery.trim() && campaignId) {
            showDropdown = false;
            goto(`/campaigns/${campaignId}/search?q=${encodeURIComponent(searchQuery)}`);
        }
    }

    function handleResultClick(result) {
        showDropdown = false;
        searchQuery = '';
        goto(result.url);
    }

    function handleKeydown(event) {
        if (!showDropdown || !searchResults) return;

        const allResults = getAllResults();
        
        if (event.key === 'ArrowDown') {
            event.preventDefault();
            selectedIndex = Math.min(selectedIndex + 1, allResults.length - 1);
        } else if (event.key === 'ArrowUp') {
            event.preventDefault();
            selectedIndex = Math.max(selectedIndex - 1, -1);
        } else if (event.key === 'Enter') {
            event.preventDefault();
            if (selectedIndex >= 0 && allResults[selectedIndex]) {
                handleResultClick(allResults[selectedIndex]);
            } else {
                handleSubmit();
            }
        } else if (event.key === 'Escape') {
            showDropdown = false;
            selectedIndex = -1;
            searchInput?.blur();
        }
    }

    function getAllResults() {
        if (!searchResults?.results) return [];
        return Object.values(searchResults.results).flat();
    }

    function handleClickOutside(event) {
        if (!event.target.closest('.global-search-container')) {
            showDropdown = false;
            selectedIndex = -1;
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
            session: 'Session'
        };
        return names[type] || 'Item';
    }

    // Clean up timeout on destroy
    import { onDestroy } from 'svelte';
    onDestroy(() => {
        clearTimeout(searchTimeout);
    });
</script>

<svelte:window on:click={handleClickOutside} />

<div class="global-search-container relative">
    <form on:submit|preventDefault={handleSubmit} class="relative">
        <div class="relative">
            <input
                bind:this={searchInput}
                bind:value={searchQuery}
                on:keydown={handleKeydown}
                type="text"
                placeholder={placeholder}
                class="input pl-10 pr-4 w-full"
                autocomplete="off"
                spellcheck="false"
            />
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
            </div>
            {#if loading}
                <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                    <div class="animate-spin h-4 w-4 border-2 border-gray-300 border-t-red-500 rounded-full"></div>
                </div>
            {/if}
        </div>
    </form>

    <!-- Search Results Dropdown -->
    {#if showDropdown && searchResults}
        <div class="absolute top-full left-0 right-0 mt-1 bg-gray-800 border border-gray-600 rounded-lg shadow-lg z-50 max-h-96 overflow-y-auto">
            {#if searchResults.total_results === 0}
                <div class="p-4 text-center text-gray-400">
                    <p>No results found for "{searchQuery}"</p>
                </div>
            {:else}
                <!-- Search Summary -->
                <div class="px-4 py-2 border-b border-gray-600 bg-gray-750">
                    <p class="text-xs text-gray-400">
                        {searchResults.total_results} result{searchResults.total_results !== 1 ? 's' : ''} found
                    </p>
                </div>

                {#each Object.entries(searchResults.results) as [category, results], categoryIndex}
                    {#if results.length > 0}
                        <!-- Category Header -->
                        <div class="px-4 py-2 bg-gray-750 border-b border-gray-700">
                            <h3 class="text-sm font-medium text-gray-300 capitalize">
                                {getTypeName(category.slice(0, -1))}s ({results.length})
                            </h3>
                        </div>

                        <!-- Results in Category -->
                        {#each results as result, resultIndex}
                            {@const globalIndex = Object.values(searchResults.results).slice(0, categoryIndex).flat().length + resultIndex}
                            <button
                                on:click={() => handleResultClick(result)}
                                class="w-full px-4 py-3 text-left hover:bg-gray-700 focus:bg-gray-700 flex items-start space-x-3 transition-colors {selectedIndex === globalIndex ? 'bg-gray-700' : ''}"
                            >
                                <span class="text-lg flex-shrink-0 mt-0.5">{getTypeIcon(result.type)}</span>
                                <div class="flex-1 min-w-0">
                                    <p class="text-white font-medium truncate">{result.name}</p>
                                    <p class="text-xs text-gray-400 truncate">{result.description}</p>
                                </div>
                                <div class="flex-shrink-0">
                                    <svg class="h-4 w-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                                    </svg>
                                </div>
                            </button>
                        {/each}
                    {/if}
                {/each}

                <!-- View All Results -->
                {#if searchResults.total_results > 5}
                    <div class="border-t border-gray-600">
                        <button
                            on:click={handleSubmit}
                            class="w-full px-4 py-3 text-left hover:bg-gray-700 focus:bg-gray-700 transition-colors"
                        >
                            <div class="flex items-center justify-center space-x-2 text-red-400">
                                <span>View all {searchResults.total_results} results</span>
                                <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                                </svg>
                            </div>
                        </button>
                    </div>
                {/if}
            {/if}
        </div>
    {/if}
</div>

<style>
    /* Ensure dropdown appears above other content */
    .global-search-container {
        z-index: 40;
    }
</style>