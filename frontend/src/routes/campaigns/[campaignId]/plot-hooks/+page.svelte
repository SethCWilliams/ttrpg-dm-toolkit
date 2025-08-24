<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { auth } from '$lib/stores/auth.js';
    import { currentCampaign } from '$lib/stores/campaigns.js';
    import { plotHookAPI } from '$lib/api.js';
    import { goto } from '$app/navigation';
    import CreatePlotHookModal from '$lib/components/CreatePlotHookModal.svelte';

    let campaignId;
    let plotHooks = [];
    let total = 0;
    let loading = true;
    let error = '';
    let searchQuery = '';
    let selectedType = '';
    let selectedStatus = '';
    let selectedUrgency = '';
    let selectedComplexity = '';
    let showCreateModal = false;

    const hookTypes = [
        { value: '', label: 'All Types' },
        { value: 'main_quest', label: 'Main Quest' },
        { value: 'side_quest', label: 'Side Quest' },
        { value: 'personal', label: 'Personal' },
        { value: 'political', label: 'Political' },
        { value: 'mystery', label: 'Mystery' },
        { value: 'combat', label: 'Combat' },
        { value: 'social', label: 'Social' }
    ];

    const statusOptions = [
        { value: '', label: 'All Status' },
        { value: 'draft', label: 'Draft' },
        { value: 'available', label: 'Available' },
        { value: 'active', label: 'Active' },
        { value: 'completed', label: 'Completed' },
        { value: 'failed', label: 'Failed' },
        { value: 'abandoned', label: 'Abandoned' }
    ];

    const urgencyOptions = [
        { value: '', label: 'All Urgency' },
        { value: 'immediate', label: 'Immediate' },
        { value: 'urgent', label: 'Urgent' },
        { value: 'moderate', label: 'Moderate' },
        { value: 'background', label: 'Background' }
    ];

    const complexityOptions = [
        { value: '', label: 'All Complexity' },
        { value: 'simple', label: 'Simple' },
        { value: 'moderate', label: 'Moderate' },
        { value: 'complex', label: 'Complex' },
        { value: 'epic', label: 'Epic' }
    ];

    onMount(async () => {
        if (!$auth.user) {
            goto('/auth/login');
            return;
        }

        campaignId = $page.params.campaignId;
        await loadPlotHooks();
    });

    async function loadPlotHooks() {
        try {
            loading = true;
            const params = {
                search: searchQuery || undefined,
                hook_type: selectedType || undefined,
                status: selectedStatus || undefined,
                urgency: selectedUrgency || undefined,
                complexity: selectedComplexity || undefined,
                limit: 100
            };
            
            const response = await plotHookAPI.getPlotHooks(campaignId, params);
            plotHooks = response.items || [];
            total = response.total || 0;
        } catch (err) {
            error = err.message || 'Failed to load plot hooks';
        } finally {
            loading = false;
        }
    }

    function handleSearch() {
        loadPlotHooks();
    }

    function handleFilterChange() {
        loadPlotHooks();
    }

    function getStatusBadgeClass(status) {
        const classes = {
            draft: 'bg-gray-600 text-gray-300',
            available: 'bg-blue-600 text-blue-100',
            active: 'bg-green-600 text-green-100',
            completed: 'bg-purple-600 text-purple-100',
            failed: 'bg-red-600 text-red-100',
            abandoned: 'bg-orange-600 text-orange-100'
        };
        return classes[status] || 'bg-gray-600 text-gray-300';
    }

    function getUrgencyBadgeClass(urgency) {
        const classes = {
            immediate: 'bg-red-600 text-red-100',
            urgent: 'bg-orange-600 text-orange-100',
            moderate: 'bg-yellow-600 text-yellow-100',
            background: 'bg-gray-600 text-gray-300'
        };
        return classes[urgency] || 'bg-gray-600 text-gray-300';
    }

    function capitalizeWords(str) {
        if (!str) return '';
        return str.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    function handlePlotHookCreated(event) {
        showCreateModal = false;
        loadPlotHooks();
    }

    function handleModalClose() {
        showCreateModal = false;
    }
</script>

<svelte:head>
    <title>Plot Hooks - {$currentCampaign?.name || 'Campaign'} - DM Toolkit</title>
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
                    <h1 class="text-3xl font-bold text-white">Plot Hooks</h1>
                    <p class="text-gray-400">Manage your adventure hooks and storylines</p>
                </div>
            </div>
            
            <button
                on:click={() => showCreateModal = true}
                class="btn btn-primary"
            >
                <svg class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                Create Plot Hook
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
                        placeholder="Search plot hooks..."
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
                    {#each hookTypes as type}
                        <option value={type.value}>{type.label}</option>
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
                <label class="block text-sm font-medium text-gray-300 mb-2">Urgency</label>
                <select bind:value={selectedUrgency} on:change={handleFilterChange} class="input">
                    {#each urgencyOptions as urgency}
                        <option value={urgency.value}>{urgency.label}</option>
                    {/each}
                </select>
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-300 mb-2">Complexity</label>
                <select bind:value={selectedComplexity} on:change={handleFilterChange} class="input">
                    {#each complexityOptions as complexity}
                        <option value={complexity.value}>{complexity.label}</option>
                    {/each}
                </select>
            </div>
        </div>
    </div>

    <!-- Results Summary -->
    <div class="flex items-center justify-between mb-6">
        <p class="text-gray-400">
            {#if loading}
                Loading plot hooks...
            {:else}
                Showing {plotHooks.length} of {total} plot hooks
            {/if}
        </p>
    </div>

    <!-- Plot Hooks List -->
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
                on:click={loadPlotHooks}
                class="btn btn-secondary mt-4"
            >
                Try Again
            </button>
        </div>
    {:else if plotHooks.length === 0}
        <div class="card text-center py-12">
            <svg class="mx-auto h-12 w-12 text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <h3 class="text-xl font-medium text-gray-300 mb-2">No plot hooks found</h3>
            <p class="text-gray-400 mb-6">Create your first plot hook to start building engaging adventures.</p>
            <button 
                on:click={() => showCreateModal = true}
                class="btn btn-primary"
            >
                Create Plot Hook
            </button>
        </div>
    {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each plotHooks as plotHook}
                <a 
                    href="/campaigns/{campaignId}/plot-hooks/{plotHook.id}"
                    class="card hover:bg-gray-750 transition-colors group"
                >
                    <div class="flex items-start justify-between mb-3">
                        <h3 class="text-lg font-semibold text-white group-hover:text-red-400 transition-colors line-clamp-2">
                            {plotHook.title}
                        </h3>
                    </div>
                    
                    {#if plotHook.description}
                        <p class="text-gray-400 text-sm mb-4 line-clamp-3">
                            {plotHook.description}
                        </p>
                    {/if}

                    <div class="flex flex-wrap gap-2 mb-4">
                        {#if plotHook.hook_type}
                            <span class="px-2 py-1 rounded text-xs bg-blue-600 text-blue-100">
                                {capitalizeWords(plotHook.hook_type)}
                            </span>
                        {/if}
                        
                        <span class="px-2 py-1 rounded text-xs {getStatusBadgeClass(plotHook.status)}">
                            {capitalizeWords(plotHook.status)}
                        </span>
                        
                        {#if plotHook.urgency}
                            <span class="px-2 py-1 rounded text-xs {getUrgencyBadgeClass(plotHook.urgency)}">
                                {capitalizeWords(plotHook.urgency)}
                            </span>
                        {/if}
                        
                        {#if plotHook.complexity}
                            <span class="px-2 py-1 rounded text-xs bg-purple-600 text-purple-100">
                                {capitalizeWords(plotHook.complexity)}
                            </span>
                        {/if}
                    </div>

                    <div class="flex items-center justify-between text-xs text-gray-500">
                        <span>
                            {#if plotHook.related_npcs?.length || plotHook.related_locations?.length || plotHook.related_organizations?.length}
                                Connected to {(plotHook.related_npcs?.length || 0) + (plotHook.related_locations?.length || 0) + (plotHook.related_organizations?.length || 0)} elements
                            {:else}
                                No connections
                            {/if}
                        </span>
                        <span>
                            {new Date(plotHook.created_at).toLocaleDateString()}
                        </span>
                    </div>
                </a>
            {/each}
        </div>
    {/if}
</div>

{#if showCreateModal}
    <CreatePlotHookModal 
        {campaignId}
        on:created={handlePlotHookCreated}
        on:close={handleModalClose}
    />
{/if}