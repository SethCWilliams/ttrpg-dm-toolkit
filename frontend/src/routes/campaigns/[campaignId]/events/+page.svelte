<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { auth } from '$lib/stores/auth.js';
    import { currentCampaign } from '$lib/stores/campaigns.js';
    import { eventAPI } from '$lib/api.js';
    import { goto } from '$app/navigation';
    import CreateEventModal from '$lib/components/CreateEventModal.svelte';

    let campaignId;
    let events = [];
    let total = 0;
    let loading = true;
    let error = '';
    let searchQuery = '';
    let selectedType = '';
    let selectedStatus = '';
    let selectedVisibility = '';
    let showCreateModal = false;

    const eventTypes = [
        { value: '', label: 'All Types' },
        { value: 'historical', label: 'Historical' },
        { value: 'current', label: 'Current' },
        { value: 'scheduled', label: 'Scheduled' },
        { value: 'recurring', label: 'Recurring' }
    ];

    const statusOptions = [
        { value: '', label: 'All Status' },
        { value: 'draft', label: 'Draft' },
        { value: 'active', label: 'Active' },
        { value: 'completed', label: 'Completed' },
        { value: 'cancelled', label: 'Cancelled' }
    ];

    const visibilityOptions = [
        { value: '', label: 'All Visibility' },
        { value: 'dm_only', label: 'DM Only' },
        { value: 'partially_known', label: 'Partially Known' },
        { value: 'player_known', label: 'Known to Players' }
    ];

    onMount(async () => {
        if (!$auth.user) {
            goto('/auth/login');
            return;
        }

        campaignId = $page.params.campaignId;
        await loadEvents();
    });

    async function loadEvents() {
        try {
            loading = true;
            const params = {
                limit: 100
            };
            
            // Only add parameters that have actual values
            if (searchQuery) params.search = searchQuery;
            if (selectedType) params.event_type = selectedType;
            if (selectedStatus) params.status = selectedStatus;
            if (selectedVisibility) params.visibility = selectedVisibility;
            
            const response = await eventAPI.getEvents(campaignId, params);
            events = response.items || [];
            total = response.total || 0;
        } catch (err) {
            error = err.message || 'Failed to load events';
        } finally {
            loading = false;
        }
    }

    function handleSearch() {
        loadEvents();
    }

    function handleFilterChange() {
        loadEvents();
    }

    function getTypeBadgeClass(type) {
        const classes = {
            historical: 'bg-blue-600 text-blue-100',
            current: 'bg-green-600 text-green-100',
            scheduled: 'bg-purple-600 text-purple-100',
            recurring: 'bg-orange-600 text-orange-100'
        };
        return classes[type] || 'bg-gray-600 text-gray-300';
    }

    function getStatusBadgeClass(status) {
        const classes = {
            draft: 'bg-gray-600 text-gray-300',
            active: 'bg-green-600 text-green-100',
            completed: 'bg-blue-600 text-blue-100',
            cancelled: 'bg-red-600 text-red-100'
        };
        return classes[status] || 'bg-gray-600 text-gray-300';
    }

    function capitalizeWords(str) {
        if (!str) return '';
        return str.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    function formatDate(dateString) {
        if (!dateString) return '';
        return dateString;
    }

    function truncateText(text, maxLength = 150) {
        if (!text || text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    function handleEventCreated(event) {
        showCreateModal = false;
        loadEvents();
    }

    function handleModalClose() {
        showCreateModal = false;
    }
</script>

<svelte:head>
    <title>Events - {$currentCampaign?.name || 'Campaign'} - DM Toolkit</title>
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
                    <h1 class="text-3xl font-bold text-white">Events</h1>
                    <p class="text-gray-400">Timeline of historical, current, and scheduled events</p>
                </div>
            </div>
            
            <button
                on:click={() => showCreateModal = true}
                class="btn btn-primary"
            >
                <svg class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                Create Event
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
                        placeholder="Search events..."
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
                    {#each eventTypes as type}
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
                <label class="block text-sm font-medium text-gray-300 mb-2">Visibility</label>
                <select bind:value={selectedVisibility} on:change={handleFilterChange} class="input">
                    {#each visibilityOptions as visibility}
                        <option value={visibility.value}>{visibility.label}</option>
                    {/each}
                </select>
            </div>
        </div>
    </div>

    <!-- Results Summary -->
    <div class="flex items-center justify-between mb-6">
        <p class="text-gray-400">
            {#if loading}
                Loading events...
            {:else}
                Showing {events.length} of {total} events
            {/if}
        </p>
    </div>

    <!-- Events List -->
    {#if loading}
        <div class="space-y-4">
            {#each Array(6) as _}
                <div class="card animate-pulse">
                    <div class="flex items-start justify-between">
                        <div class="flex-1">
                            <div class="h-6 bg-gray-700 rounded w-3/4 mb-2"></div>
                            <div class="h-4 bg-gray-700 rounded w-1/2 mb-4"></div>
                            <div class="h-3 bg-gray-700 rounded w-full mb-2"></div>
                            <div class="h-3 bg-gray-700 rounded w-2/3"></div>
                        </div>
                    </div>
                </div>
            {/each}
        </div>
    {:else if error}
        <div class="card bg-red-900 border-red-700">
            <p class="text-red-100">{error}</p>
            <button 
                on:click={loadEvents}
                class="btn btn-secondary mt-4"
            >
                Try Again
            </button>
        </div>
    {:else if events.length === 0}
        <div class="card text-center py-12">
            <svg class="mx-auto h-12 w-12 text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 class="text-xl font-medium text-gray-300 mb-2">No events found</h3>
            <p class="text-gray-400 mb-6">Create your first event to start building your campaign timeline.</p>
            <button 
                on:click={() => showCreateModal = true}
                class="btn btn-primary"
            >
                Create Event
            </button>
        </div>
    {:else}
        <div class="space-y-4">
            {#each events as event}
                <a 
                    href="/campaigns/{campaignId}/events/{event.id}"
                    class="card hover:bg-gray-750 transition-colors group block"
                >
                    <div class="flex items-start justify-between">
                        <div class="flex-1 min-w-0">
                            <div class="flex items-start justify-between mb-3">
                                <div class="flex-1">
                                    <h3 class="text-lg font-semibold text-white group-hover:text-red-400 transition-colors line-clamp-2">
                                        {event.title}
                                    </h3>
                                    {#if event.date}
                                        <p class="text-sm text-gray-400 mt-1">{formatDate(event.date)}</p>
                                    {/if}
                                </div>
                                
                                <div class="flex flex-wrap gap-2 ml-4 flex-shrink-0">
                                    {#if event.event_type}
                                        <span class="px-2 py-1 rounded text-xs {getTypeBadgeClass(event.event_type)}">
                                            {capitalizeWords(event.event_type)}
                                        </span>
                                    {/if}
                                    
                                    <span class="px-2 py-1 rounded text-xs {getStatusBadgeClass(event.status)}">
                                        {capitalizeWords(event.status)}
                                    </span>
                                </div>
                            </div>
                            
                            {#if event.description}
                                <p class="text-gray-400 text-sm mb-4 line-clamp-3">
                                    {truncateText(event.description)}
                                </p>
                            {/if}

                            <div class="flex items-center justify-between text-xs text-gray-500">
                                <div class="flex space-x-4">
                                    {#if event.participants && event.participants.length > 0}
                                        <span>{event.participants.length} participant{event.participants.length !== 1 ? 's' : ''}</span>
                                    {/if}
                                    {#if event.causes && event.causes.length > 0}
                                        <span>{event.causes.length} cause{event.causes.length !== 1 ? 's' : ''}</span>
                                    {/if}
                                    {#if event.effects && event.effects.length > 0}
                                        <span>{event.effects.length} effect{event.effects.length !== 1 ? 's' : ''}</span>
                                    {/if}
                                </div>
                                <span>
                                    Created {new Date(event.created_at).toLocaleDateString()}
                                </span>
                            </div>
                        </div>
                    </div>
                </a>
            {/each}
        </div>
    {/if}
</div>

{#if showCreateModal}
    <CreateEventModal 
        {campaignId}
        on:created={handleEventCreated}
        on:close={handleModalClose}
    />
{/if}