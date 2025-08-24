<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { auth } from '$lib/stores/auth.js';
    import { currentCampaign } from '$lib/stores/campaigns.js';
    import { ideaAPI } from '$lib/api.js';
    import { goto } from '$app/navigation';
    import CreateIdeaModal from '$lib/components/CreateIdeaModal.svelte';

    let campaignId;
    let ideas = [];
    let total = 0;
    let loading = true;
    let error = '';
    let searchQuery = '';
    let selectedStatus = '';
    let selectedType = '';
    let selectedPriority = '';
    let showCreateModal = false;

    const statusOptions = [
        { value: '', label: 'All Status' },
        { value: 'raw_idea', label: 'Raw Idea' },
        { value: 'developing', label: 'Developing' },
        { value: 'ready_to_implement', label: 'Ready to Implement' },
        { value: 'implemented', label: 'Implemented' }
    ];

    const ideaTypes = [
        { value: '', label: 'All Types' },
        { value: 'npc', label: 'NPC' },
        { value: 'location', label: 'Location' },
        { value: 'plot_hook', label: 'Plot Hook' },
        { value: 'lore', label: 'Lore' },
        { value: 'item', label: 'Item' },
        { value: 'organization', label: 'Organization' },
        { value: 'event', label: 'Event' }
    ];

    const priorityOptions = [
        { value: '', label: 'All Priorities' },
        { value: 'low', label: 'Low' },
        { value: 'medium', label: 'Medium' },
        { value: 'high', label: 'High' }
    ];

    onMount(async () => {
        if (!$auth.user) {
            goto('/auth/login');
            return;
        }

        campaignId = $page.params.campaignId;
        await loadIdeas();
    });

    async function loadIdeas() {
        try {
            loading = true;
            const params = {
                limit: 100
            };
            
            // Only add parameters that have actual values
            if (searchQuery) params.search = searchQuery;
            if (selectedStatus) params.status = selectedStatus;
            if (selectedType) params.idea_type = selectedType;
            if (selectedPriority) params.priority = selectedPriority;
            
            const response = await ideaAPI.getIdeas(campaignId, params);
            ideas = response.items || [];
            total = response.total || 0;
        } catch (err) {
            error = err.message || 'Failed to load ideas';
        } finally {
            loading = false;
        }
    }

    function handleSearch() {
        loadIdeas();
    }

    function handleFilterChange() {
        loadIdeas();
    }

    function getStatusBadgeClass(status) {
        const classes = {
            raw_idea: 'bg-gray-600 text-gray-300',
            developing: 'bg-yellow-600 text-yellow-100',
            ready_to_implement: 'bg-green-600 text-green-100',
            implemented: 'bg-blue-600 text-blue-100'
        };
        return classes[status] || 'bg-gray-600 text-gray-300';
    }

    function getPriorityBadgeClass(priority) {
        const classes = {
            low: 'bg-gray-600 text-gray-300',
            medium: 'bg-yellow-600 text-yellow-100',
            high: 'bg-red-600 text-red-100'
        };
        return classes[priority] || 'bg-gray-600 text-gray-300';
    }

    function capitalizeWords(str) {
        if (!str) return '';
        return str.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    function truncateText(text, maxLength = 200) {
        if (!text || text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    async function updateIdeaStatus(idea, newStatus) {
        try {
            await ideaAPI.updateIdea(campaignId, idea.id, { status: newStatus });
            await loadIdeas(); // Refresh the list
        } catch (err) {
            error = err.message || 'Failed to update idea status';
        }
    }

    async function convertIdea(idea, targetType) {
        try {
            await ideaAPI.convertIdea(campaignId, idea.id, targetType);
            await loadIdeas(); // Refresh the list
        } catch (err) {
            error = err.message || 'Failed to convert idea';
        }
    }

    function handleIdeaCreated(event) {
        showCreateModal = false;
        loadIdeas();
    }

    function handleModalClose() {
        showCreateModal = false;
    }

    // Group ideas by status for workflow display
    $: groupedIdeas = ideas.reduce((groups, idea) => {
        const status = idea.status || 'raw_idea';
        if (!groups[status]) groups[status] = [];
        groups[status].push(idea);
        return groups;
    }, {});
</script>

<svelte:head>
    <title>Ideas Inbox - {$currentCampaign?.name || 'Campaign'} - DM Toolkit</title>
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
                    <h1 class="text-3xl font-bold text-white">Ideas Inbox</h1>
                    <p class="text-gray-400">Capture, develop, and track your creative ideas</p>
                </div>
            </div>
            
            <button
                on:click={() => showCreateModal = true}
                class="btn btn-primary"
            >
                <svg class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                Add Idea
            </button>
        </div>
    </div>

    <!-- Filters -->
    <div class="card mb-6">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <div class="lg:col-span-2">
                <label class="block text-sm font-medium text-gray-300 mb-2">Search</label>
                <div class="relative">
                    <input
                        type="text"
                        bind:value={searchQuery}
                        on:input={handleSearch}
                        placeholder="Search ideas..."
                        class="input pl-10"
                    />
                    <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                </div>
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
                <label class="block text-sm font-medium text-gray-300 mb-2">Type</label>
                <select bind:value={selectedType} on:change={handleFilterChange} class="input">
                    {#each ideaTypes as type}
                        <option value={type.value}>{type.label}</option>
                    {/each}
                </select>
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-300 mb-2">Priority</label>
                <select bind:value={selectedPriority} on:change={handleFilterChange} class="input">
                    {#each priorityOptions as priority}
                        <option value={priority.value}>{priority.label}</option>
                    {/each}
                </select>
            </div>
        </div>
    </div>

    <!-- Results Summary -->
    <div class="flex items-center justify-between mb-6">
        <p class="text-gray-400">
            {#if loading}
                Loading ideas...
            {:else}
                Showing {ideas.length} of {total} ideas
            {/if}
        </p>
    </div>

    <!-- Ideas List -->
    {#if loading}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each Array(6) as _}
                <div class="card animate-pulse">
                    <div class="h-4 bg-gray-700 rounded w-3/4 mb-2"></div>
                    <div class="h-3 bg-gray-700 rounded w-1/2 mb-4"></div>
                    <div class="h-20 bg-gray-700 rounded mb-4"></div>
                    <div class="h-3 bg-gray-700 rounded w-1/3"></div>
                </div>
            {/each}
        </div>
    {:else if error}
        <div class="card bg-red-900 border-red-700">
            <p class="text-red-100">{error}</p>
            <button 
                on:click={loadIdeas}
                class="btn btn-secondary mt-4"
            >
                Try Again
            </button>
        </div>
    {:else if ideas.length === 0}
        <div class="card text-center py-12">
            <svg class="mx-auto h-12 w-12 text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <h3 class="text-xl font-medium text-gray-300 mb-2">No ideas yet</h3>
            <p class="text-gray-400 mb-6">Start capturing your creative ideas to build your world.</p>
            <button 
                on:click={() => showCreateModal = true}
                class="btn btn-primary"
            >
                Add Your First Idea
            </button>
        </div>
    {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each ideas as idea}
                <div class="card">
                    <div class="flex items-start justify-between mb-3">
                        <div class="flex flex-wrap gap-2">
                            <span class="px-2 py-1 rounded text-xs {getStatusBadgeClass(idea.status)}">
                                {capitalizeWords(idea.status)}
                            </span>
                            
                            <span class="px-2 py-1 rounded text-xs {getPriorityBadgeClass(idea.priority)}">
                                {capitalizeWords(idea.priority)}
                            </span>
                            
                            {#if idea.idea_type}
                                <span class="px-2 py-1 rounded text-xs bg-blue-600 text-blue-100">
                                    {capitalizeWords(idea.idea_type)}
                                </span>
                            {/if}
                        </div>
                    </div>
                    
                    <p class="text-gray-300 text-sm mb-4 line-clamp-4">
                        {truncateText(idea.content)}
                    </p>

                    {#if idea.notes}
                        <p class="text-gray-400 text-xs mb-4 line-clamp-2">
                            <strong>Notes:</strong> {truncateText(idea.notes, 100)}
                        </p>
                    {/if}

                    <!-- Action Buttons -->
                    <div class="flex flex-wrap gap-2 mb-4">
                        {#if idea.status === 'raw_idea'}
                            <button
                                on:click={() => updateIdeaStatus(idea, 'developing')}
                                class="btn-sm bg-yellow-600 hover:bg-yellow-700 text-white text-xs"
                            >
                                Start Developing
                            </button>
                        {:else if idea.status === 'developing'}
                            <button
                                on:click={() => updateIdeaStatus(idea, 'ready_to_implement')}
                                class="btn-sm bg-green-600 hover:bg-green-700 text-white text-xs"
                            >
                                Mark Ready
                            </button>
                        {:else if idea.status === 'ready_to_implement'}
                            <div class="relative group">
                                <button class="btn-sm bg-blue-600 hover:bg-blue-700 text-white text-xs">
                                    Convert to...
                                </button>
                                <div class="absolute bottom-full left-0 mb-2 hidden group-hover:block bg-gray-800 border border-gray-600 rounded shadow-lg py-1 z-10 whitespace-nowrap">
                                    {#each ['npc', 'location', 'plot_hook', 'item', 'organization', 'event'] as type}
                                        <button
                                            on:click={() => convertIdea(idea, type)}
                                            class="block px-3 py-1 text-xs text-gray-300 hover:bg-gray-700 hover:text-white w-full text-left"
                                        >
                                            {capitalizeWords(type)}
                                        </button>
                                    {/each}
                                </div>
                            </div>
                        {/if}
                        
                        <a
                            href="/campaigns/{campaignId}/ideas/{idea.id}"
                            class="btn-sm btn-secondary text-xs"
                        >
                            View Details
                        </a>
                    </div>

                    <div class="text-xs text-gray-500 flex items-center justify-between">
                        <span>
                            Created {new Date(idea.created_at).toLocaleDateString()}
                        </span>
                    </div>
                </div>
            {/each}
        </div>
    {/if}
</div>

{#if showCreateModal}
    <CreateIdeaModal 
        {campaignId}
        on:created={handleIdeaCreated}
        on:close={handleModalClose}
    />
{/if}