<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { auth } from '$lib/stores/auth.js';
    import { currentCampaign } from '$lib/stores/campaigns.js';
    import { sessionNoteAPI } from '$lib/api.js';
    import { goto } from '$app/navigation';
    import CreateSessionNoteModal from '$lib/components/CreateSessionNoteModal.svelte';

    let campaignId;
    let sessionNotes = [];
    let total = 0;
    let loading = true;
    let error = '';
    let searchQuery = '';
    let selectedStatus = '';
    let selectedVisibility = '';
    let showCreateModal = false;
    let showDeleteConfirm = false;
    let sessionToDelete = null;
    let deleting = false;

    const statusOptions = [
        { value: '', label: 'All Status' },
        { value: 'draft', label: 'Draft' },
        { value: 'published', label: 'Published' },
        { value: 'archived', label: 'Archived' }
    ];

    const visibilityOptions = [
        { value: '', label: 'All Visibility' },
        { value: 'dm_only', label: 'DM Only' },
        { value: 'player_visible', label: 'Player Visible' }
    ];

    onMount(async () => {
        if (!$auth.user) {
            goto('/auth/login');
            return;
        }

        campaignId = $page.params.campaignId;
        await loadSessionNotes();
    });

    async function loadSessionNotes() {
        try {
            loading = true;
            const params = {
                limit: 100
            };
            
            // Only add parameters that have actual values
            if (searchQuery) params.search = searchQuery;
            if (selectedStatus) params.status = selectedStatus;
            if (selectedVisibility) params.visibility = selectedVisibility;
            
            const response = await sessionNoteAPI.getSessionNotes(campaignId, params);
            sessionNotes = response.items || [];
            total = response.total || 0;
        } catch (err) {
            error = err.message || 'Failed to load session notes';
        } finally {
            loading = false;
        }
    }

    function handleSearch() {
        loadSessionNotes();
    }

    function handleFilterChange() {
        loadSessionNotes();
    }

    function getStatusBadgeClass(status) {
        const classes = {
            draft: 'bg-gray-600 text-gray-300',
            published: 'bg-green-600 text-green-100',
            archived: 'bg-blue-600 text-blue-100'
        };
        return classes[status] || 'bg-gray-600 text-gray-300';
    }

    function getVisibilityBadgeClass(visibility) {
        const classes = {
            dm_only: 'bg-red-600 text-red-100',
            player_visible: 'bg-green-600 text-green-100'
        };
        return classes[visibility] || 'bg-gray-600 text-gray-300';
    }

    function capitalizeWords(str) {
        if (!str) return '';
        return str.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    function truncateText(text, maxLength = 150) {
        if (!text || text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    function formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    function handleSessionNoteCreated(event) {
        showCreateModal = false;
        loadSessionNotes();
    }

    function handleModalClose() {
        showCreateModal = false;
    }

    async function handleDuplicateSession(sessionNote) {
        try {
            await sessionNoteAPI.duplicateSessionNote(campaignId, sessionNote.id);
            await loadSessionNotes();
        } catch (err) {
            error = err.message || 'Failed to duplicate session note';
        }
    }

    function showDeleteConfirmation(sessionNote) {
        sessionToDelete = sessionNote;
        showDeleteConfirm = true;
    }

    async function handleDeleteSession() {
        if (!sessionToDelete) return;
        
        try {
            deleting = true;
            await sessionNoteAPI.deleteSessionNote(campaignId, sessionToDelete.id);
            await loadSessionNotes();
            showDeleteConfirm = false;
            sessionToDelete = null;
        } catch (err) {
            error = err.message || 'Failed to delete session note';
        } finally {
            deleting = false;
        }
    }

    function cancelDelete() {
        showDeleteConfirm = false;
        sessionToDelete = null;
    }
</script>

<svelte:head>
    <title>Session Notes - {$currentCampaign?.name || 'Campaign'} - DM Toolkit</title>
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
                    <h1 class="text-3xl font-bold text-white">Session Notes</h1>
                    <p class="text-gray-400">Track your campaign sessions and world changes</p>
                </div>
            </div>
            
            <button
                on:click={() => showCreateModal = true}
                class="btn btn-primary"
            >
                <svg class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                New Session
            </button>
        </div>
    </div>

    <!-- Filters -->
    <div class="card mb-6">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div class="lg:col-span-2">
                <label class="block text-sm font-medium text-gray-300 mb-2">Search</label>
                <div class="relative">
                    <input
                        type="text"
                        bind:value={searchQuery}
                        on:input={handleSearch}
                        placeholder="Search session notes..."
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
                Loading session notes...
            {:else}
                Showing {sessionNotes.length} of {total} session notes
            {/if}
        </p>
    </div>

    <!-- Session Notes List -->
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
                on:click={loadSessionNotes}
                class="btn btn-secondary mt-4"
            >
                Try Again
            </button>
        </div>
    {:else if sessionNotes.length === 0}
        <div class="card text-center py-12">
            <svg class="mx-auto h-12 w-12 text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 class="text-xl font-medium text-gray-300 mb-2">No session notes yet</h3>
            <p class="text-gray-400 mb-6">Start documenting your campaign sessions to track progress and world changes.</p>
            <button 
                on:click={() => showCreateModal = true}
                class="btn btn-primary"
            >
                Create Your First Session
            </button>
        </div>
    {:else}
        <div class="space-y-4">
            {#each sessionNotes as sessionNote}
                <div class="card">
                    <div class="flex items-start justify-between">
                        <div class="flex-1 min-w-0">
                            <div class="flex items-start justify-between mb-3">
                                <div class="flex-1">
                                    <div class="flex items-center space-x-3 mb-2">
                                        <a
                                            href="/campaigns/{campaignId}/sessions/{sessionNote.id}"
                                            class="text-lg font-semibold text-white hover:text-red-400 transition-colors line-clamp-2"
                                        >
                                            {sessionNote.title}
                                        </a>
                                        {#if sessionNote.session_number}
                                            <span class="px-2 py-1 rounded text-xs bg-blue-600 text-blue-100">
                                                Session #{sessionNote.session_number}
                                            </span>
                                        {/if}
                                    </div>
                                    
                                    <div class="flex items-center space-x-4 text-sm text-gray-400">
                                        {#if sessionNote.session_date}
                                            <span>📅 {sessionNote.session_date}</span>
                                        {/if}
                                        {#if sessionNote.in_world_date}
                                            <span>🌍 {sessionNote.in_world_date}</span>
                                        {/if}
                                        <span>Created {formatDate(sessionNote.created_at)}</span>
                                    </div>
                                </div>
                                
                                <div class="flex flex-wrap gap-2 ml-4 flex-shrink-0">
                                    <span class="px-2 py-1 rounded text-xs {getStatusBadgeClass(sessionNote.status)}">
                                        {capitalizeWords(sessionNote.status)}
                                    </span>
                                    
                                    <span class="px-2 py-1 rounded text-xs {getVisibilityBadgeClass(sessionNote.visibility)}">
                                        {capitalizeWords(sessionNote.visibility)}
                                    </span>
                                </div>
                            </div>
                            
                            {#if sessionNote.summary}
                                <p class="text-gray-400 text-sm mb-4 line-clamp-3">
                                    {truncateText(sessionNote.summary)}
                                </p>
                            {/if}

                            <div class="flex items-center justify-between text-xs text-gray-500">
                                <div class="flex space-x-4">
                                    {#if sessionNote.experience_gained > 0}
                                        <span>⚡ {sessionNote.experience_gained} XP</span>
                                    {/if}
                                    {#if sessionNote.npcs_encountered && sessionNote.npcs_encountered.length > 0}
                                        <span>👥 {sessionNote.npcs_encountered.length} NPCs</span>
                                    {/if}
                                    {#if sessionNote.locations_visited && sessionNote.locations_visited.length > 0}
                                        <span>📍 {sessionNote.locations_visited.length} locations</span>
                                    {/if}
                                </div>
                                
                                <div class="flex space-x-2">
                                    <button
                                        on:click|stopPropagation={() => handleDuplicateSession(sessionNote)}
                                        class="text-gray-500 hover:text-gray-300 text-xs"
                                        title="Duplicate as next session"
                                    >
                                        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                        </svg>
                                    </button>
                                    <button
                                        on:click|stopPropagation={() => showDeleteConfirmation(sessionNote)}
                                        class="text-gray-500 hover:text-red-400 text-xs"
                                        title="Delete session"
                                    >
                                        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            {/each}
        </div>
    {/if}
</div>

{#if showCreateModal}
    <CreateSessionNoteModal 
        {campaignId}
        on:created={handleSessionNoteCreated}
        on:close={handleModalClose}
    />
{/if}

<!-- Delete Confirmation Modal -->
{#if showDeleteConfirm && sessionToDelete}
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div class="bg-gray-800 rounded-lg max-w-md w-full p-6">
            <h3 class="text-xl font-semibold text-white mb-4">Delete Session Note</h3>
            <p class="text-gray-300 mb-6">
                Are you sure you want to delete "<strong>{sessionToDelete.title}</strong>"? This action cannot be undone.
            </p>
            <div class="flex justify-end space-x-3">
                <button
                    on:click={cancelDelete}
                    class="btn btn-secondary"
                    disabled={deleting}
                >
                    Cancel
                </button>
                <button
                    on:click={handleDeleteSession}
                    class="btn bg-red-600 hover:bg-red-700 text-white"
                    disabled={deleting}
                >
                    {deleting ? 'Deleting...' : 'Delete'}
                </button>
            </div>
        </div>
    </div>
{/if}