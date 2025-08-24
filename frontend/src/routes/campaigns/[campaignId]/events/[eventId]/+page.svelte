<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { auth } from '$lib/stores/auth.js';
    import { currentCampaign } from '$lib/stores/campaigns.js';
    import { eventAPI } from '$lib/api.js';
    import EditEventModal from '$lib/components/EditEventModal.svelte';

    let campaignId;
    let eventId;
    let event = null;
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
        eventId = $page.params.eventId;
        await loadEvent();
    });

    async function loadEvent() {
        try {
            loading = true;
            event = await eventAPI.getEvent(campaignId, eventId);
        } catch (err) {
            error = err.message || 'Failed to load event';
        } finally {
            loading = false;
        }
    }

    async function handleDelete() {
        try {
            deleting = true;
            await eventAPI.deleteEvent(campaignId, eventId);
            goto(`/campaigns/${campaignId}/events`);
        } catch (err) {
            error = err.message || 'Failed to delete event';
        } finally {
            deleting = false;
            showDeleteConfirm = false;
        }
    }

    function handleEventUpdated(event) {
        event = event.detail.event;
        showEditModal = false;
    }

    function handleModalClose() {
        showEditModal = false;
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
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }
</script>

<svelte:head>
    <title>{event?.title || 'Event'} - {$currentCampaign?.name || 'Campaign'} - DM Toolkit</title>
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
                    on:click={loadEvent}
                    class="btn btn-secondary"
                >
                    Try Again
                </button>
            </div>
        </div>
    {:else if event}
        <!-- Header -->
        <div class="mb-8">
            <div class="flex items-center space-x-4 mb-4">
                <button
                    on:click={() => goto(`/campaigns/${campaignId}/events`)}
                    class="text-gray-400 hover:text-white flex items-center"
                >
                    <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                    </svg>
                    Back to Events
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
                    <h1 class="text-3xl font-bold text-white mb-2">{event.title}</h1>
                    
                    <div class="flex flex-wrap gap-2 mb-4">
                        {#if event.event_type}
                            <span class="px-2 py-1 rounded text-xs {getTypeBadgeClass(event.event_type)}">
                                {capitalizeWords(event.event_type)}
                            </span>
                        {/if}
                        
                        <span class="px-2 py-1 rounded text-xs {getStatusBadgeClass(event.status)}">
                            {capitalizeWords(event.status)}
                        </span>
                    </div>

                    <div class="text-gray-400 space-y-1">
                        {#if event.date}
                            <p><strong>Date:</strong> {event.date}</p>
                        {/if}
                        <p>Created on {formatDate(event.created_at)}</p>
                        {#if event.updated_at !== event.created_at}
                            <p>Updated on {formatDate(event.updated_at)}</p>
                        {/if}
                    </div>
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
            {#if event.description}
                <div class="card">
                    <h2 class="text-xl font-semibold text-white mb-3">Description</h2>
                    <p class="text-gray-300 whitespace-pre-wrap">{event.description}</p>
                </div>
            {/if}

            <!-- Participants -->
            {#if event.participants && event.participants.length > 0}
                <div class="card">
                    <h2 class="text-xl font-semibold text-white mb-4">Participants</h2>
                    <div class="space-y-3">
                        {#each event.participants as participant}
                            <div class="bg-gray-700 p-4 rounded">
                                <div class="flex items-start justify-between">
                                    <div>
                                        <p class="font-medium text-white">
                                            {participant.name || participant.id || 'Unknown'}
                                            {#if participant.role}
                                                <span class="text-gray-400">- {participant.role}</span>
                                            {/if}
                                        </p>
                                        <p class="text-sm text-gray-400">{capitalizeWords(participant.type)}</p>
                                        {#if participant.notes}
                                            <p class="text-sm text-gray-300 mt-2">{participant.notes}</p>
                                        {/if}
                                    </div>
                                </div>
                            </div>
                        {/each}
                    </div>
                </div>
            {/if}

            <!-- Causes and Effects -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Causes -->
                {#if event.causes && event.causes.length > 0}
                    <div class="card">
                        <h2 class="text-xl font-semibold text-white mb-4">Causes</h2>
                        <ul class="space-y-2">
                            {#each event.causes as cause}
                                <li class="text-gray-300 flex items-start">
                                    <span class="text-red-400 mr-2">•</span>
                                    {cause}
                                </li>
                            {/each}
                        </ul>
                    </div>
                {/if}

                <!-- Effects -->
                {#if event.effects && event.effects.length > 0}
                    <div class="card">
                        <h2 class="text-xl font-semibold text-white mb-4">Effects</h2>
                        <ul class="space-y-2">
                            {#each event.effects as effect}
                                <li class="text-gray-300 flex items-start">
                                    <span class="text-red-400 mr-2">•</span>
                                    {effect}
                                </li>
                            {/each}
                        </ul>
                    </div>
                {/if}
            </div>

            <!-- Properties -->
            <div class="card">
                <h2 class="text-xl font-semibold text-white mb-4">Properties</h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <dt class="text-sm font-medium text-gray-400">Event Type</dt>
                        <dd class="text-white">{capitalizeWords(event.event_type) || 'Not specified'}</dd>
                    </div>
                    <div>
                        <dt class="text-sm font-medium text-gray-400">Status</dt>
                        <dd class="text-white">{capitalizeWords(event.status)}</dd>
                    </div>
                    <div>
                        <dt class="text-sm font-medium text-gray-400">Visibility</dt>
                        <dd class="text-white">{capitalizeWords(event.visibility)}</dd>
                    </div>
                </div>
            </div>

            <!-- Notes -->
            {#if event.notes}
                <div class="card">
                    <h2 class="text-xl font-semibold text-white mb-3">DM Notes</h2>
                    <p class="text-gray-300 whitespace-pre-wrap">{event.notes}</p>
                </div>
            {/if}
        </div>
    {/if}
</div>

<!-- Edit Modal -->
{#if showEditModal && event}
    <EditEventModal 
        {campaignId}
        {event}
        on:updated={handleEventUpdated}
        on:close={handleModalClose}
    />
{/if}

<!-- Delete Confirmation Modal -->
{#if showDeleteConfirm}
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div class="bg-gray-800 rounded-lg max-w-md w-full p-6">
            <h3 class="text-xl font-semibold text-white mb-4">Delete Event</h3>
            <p class="text-gray-300 mb-6">
                Are you sure you want to delete "{event?.title}"? This action cannot be undone.
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