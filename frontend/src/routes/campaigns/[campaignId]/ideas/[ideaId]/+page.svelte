<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { auth } from '$lib/stores/auth.js';
    import { currentCampaign } from '$lib/stores/campaigns.js';
    import { ideaAPI } from '$lib/api.js';
    import EditIdeaModal from '$lib/components/EditIdeaModal.svelte';

    let campaignId;
    let ideaId;
    let idea = null;
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
        ideaId = $page.params.ideaId;
        await loadIdea();
    });

    async function loadIdea() {
        try {
            loading = true;
            idea = await ideaAPI.getIdea(campaignId, ideaId);
        } catch (err) {
            error = err.message || 'Failed to load idea';
        } finally {
            loading = false;
        }
    }

    async function handleDelete() {
        try {
            deleting = true;
            await ideaAPI.deleteIdea(campaignId, ideaId);
            goto(`/campaigns/${campaignId}/ideas`);
        } catch (err) {
            error = err.message || 'Failed to delete idea';
        } finally {
            deleting = false;
            showDeleteConfirm = false;
        }
    }

    async function updateStatus(newStatus) {
        try {
            const updated = await ideaAPI.updateIdea(campaignId, ideaId, { status: newStatus });
            idea = updated;
        } catch (err) {
            error = err.message || 'Failed to update status';
        }
    }

    async function convertIdea(targetType) {
        try {
            await ideaAPI.convertIdea(campaignId, ideaId, targetType);
            await loadIdea(); // Refresh to show updated status
        } catch (err) {
            error = err.message || 'Failed to convert idea';
        }
    }

    function handleIdeaUpdated(event) {
        idea = event.detail.idea;
        showEditModal = false;
    }

    function handleModalClose() {
        showEditModal = false;
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

    function formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }
</script>

<svelte:head>
    <title>Idea - {$currentCampaign?.name || 'Campaign'} - DM Toolkit</title>
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
                    on:click={loadIdea}
                    class="btn btn-secondary"
                >
                    Try Again
                </button>
            </div>
        </div>
    {:else if idea}
        <!-- Header -->
        <div class="mb-8">
            <div class="flex items-center space-x-4 mb-4">
                <button
                    on:click={() => goto(`/campaigns/${campaignId}/ideas`)}
                    class="text-gray-400 hover:text-white flex items-center"
                >
                    <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                    </svg>
                    Back to Ideas
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
                    <div class="flex flex-wrap gap-2 mb-4">
                        <span class="px-2 py-1 rounded text-xs {getStatusBadgeClass(idea.status)}">
                            {capitalizeWords(idea.status)}
                        </span>
                        
                        <span class="px-2 py-1 rounded text-xs {getPriorityBadgeClass(idea.priority)}">
                            {capitalizeWords(idea.priority)} Priority
                        </span>
                        
                        {#if idea.idea_type}
                            <span class="px-2 py-1 rounded text-xs bg-blue-600 text-blue-100">
                                {capitalizeWords(idea.idea_type)}
                            </span>
                        {/if}
                    </div>

                    <div class="text-gray-400 space-y-1">
                        <p>Created on {formatDate(idea.created_at)}</p>
                        {#if idea.updated_at !== idea.created_at}
                            <p>Updated on {formatDate(idea.updated_at)}</p>
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
            <!-- Idea Content -->
            <div class="card">
                <h2 class="text-xl font-semibold text-white mb-3">Idea</h2>
                <p class="text-gray-300 whitespace-pre-wrap">{idea.content}</p>
            </div>

            <!-- Workflow Actions -->
            <div class="card">
                <h2 class="text-xl font-semibold text-white mb-4">Workflow Actions</h2>
                <div class="flex flex-wrap gap-3">
                    {#if idea.status === 'raw_idea'}
                        <button
                            on:click={() => updateStatus('developing')}
                            class="btn bg-yellow-600 hover:bg-yellow-700 text-white"
                        >
                            Start Developing
                        </button>
                    {:else if idea.status === 'developing'}
                        <button
                            on:click={() => updateStatus('ready_to_implement')}
                            class="btn bg-green-600 hover:bg-green-700 text-white"
                        >
                            Mark as Ready
                        </button>
                        <button
                            on:click={() => updateStatus('raw_idea')}
                            class="btn btn-secondary"
                        >
                            Back to Raw Idea
                        </button>
                    {:else if idea.status === 'ready_to_implement'}
                        <div class="relative group">
                            <button class="btn bg-blue-600 hover:bg-blue-700 text-white">
                                Convert to Element
                            </button>
                            <div class="absolute top-full left-0 mt-2 hidden group-hover:block bg-gray-800 border border-gray-600 rounded shadow-lg py-1 z-10 whitespace-nowrap">
                                {#each ['npc', 'location', 'plot_hook', 'item', 'organization', 'event'] as type}
                                    <button
                                        on:click={() => convertIdea(type)}
                                        class="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 hover:text-white w-full text-left"
                                    >
                                        {capitalizeWords(type)}
                                    </button>
                                {/each}
                            </div>
                        </div>
                        <button
                            on:click={() => updateStatus('developing')}
                            class="btn btn-secondary"
                        >
                            Back to Developing
                        </button>
                    {:else if idea.status === 'implemented'}
                        <p class="text-green-400 flex items-center">
                            <svg class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                            </svg>
                            This idea has been implemented!
                        </p>
                    {/if}
                </div>
            </div>

            <!-- Properties -->
            <div class="card">
                <h2 class="text-xl font-semibold text-white mb-4">Properties</h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <dt class="text-sm font-medium text-gray-400">Type</dt>
                        <dd class="text-white">{idea.idea_type ? capitalizeWords(idea.idea_type) : 'General Idea'}</dd>
                    </div>
                    <div>
                        <dt class="text-sm font-medium text-gray-400">Priority</dt>
                        <dd class="text-white">{capitalizeWords(idea.priority)}</dd>
                    </div>
                    <div>
                        <dt class="text-sm font-medium text-gray-400">Status</dt>
                        <dd class="text-white">{capitalizeWords(idea.status)}</dd>
                    </div>
                </div>
            </div>

            <!-- Notes -->
            {#if idea.notes}
                <div class="card">
                    <h2 class="text-xl font-semibold text-white mb-3">Development Notes</h2>
                    <p class="text-gray-300 whitespace-pre-wrap">{idea.notes}</p>
                </div>
            {/if}
        </div>
    {/if}
</div>

<!-- Edit Modal -->
{#if showEditModal && idea}
    <EditIdeaModal 
        {campaignId}
        {idea}
        on:updated={handleIdeaUpdated}
        on:close={handleModalClose}
    />
{/if}

<!-- Delete Confirmation Modal -->
{#if showDeleteConfirm}
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div class="bg-gray-800 rounded-lg max-w-md w-full p-6">
            <h3 class="text-xl font-semibold text-white mb-4">Delete Idea</h3>
            <p class="text-gray-300 mb-6">
                Are you sure you want to delete this idea? This action cannot be undone.
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