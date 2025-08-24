<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { auth } from '$lib/stores/auth.js';
    import { currentCampaign } from '$lib/stores/campaigns.js';
    import { sessionNoteAPI } from '$lib/api.js';
    import EditSessionNoteModal from '$lib/components/EditSessionNoteModal.svelte';

    let campaignId;
    let sessionId;
    let sessionNote = null;
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
        sessionId = $page.params.sessionId;
        await loadSessionNote();
    });

    async function loadSessionNote() {
        try {
            loading = true;
            sessionNote = await sessionNoteAPI.getSessionNote(campaignId, sessionId);
        } catch (err) {
            error = err.message || 'Failed to load session note';
        } finally {
            loading = false;
        }
    }

    async function handleDelete() {
        try {
            deleting = true;
            await sessionNoteAPI.deleteSessionNote(campaignId, sessionId);
            goto(`/campaigns/${campaignId}/sessions`);
        } catch (err) {
            error = err.message || 'Failed to delete session note';
        } finally {
            deleting = false;
            showDeleteConfirm = false;
        }
    }

    async function handleDuplicate() {
        try {
            const newSession = await sessionNoteAPI.duplicateSessionNote(campaignId, sessionId);
            goto(`/campaigns/${campaignId}/sessions/${newSession.id}`);
        } catch (err) {
            error = err.message || 'Failed to duplicate session note';
        }
    }

    function handleSessionNoteUpdated(event) {
        sessionNote = event.detail.sessionNote;
        showEditModal = false;
    }

    function handleModalClose() {
        showEditModal = false;
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

    function formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }
</script>

<svelte:head>
    <title>{sessionNote?.title || 'Session'} - {$currentCampaign?.name || 'Campaign'} - DM Toolkit</title>
</svelte:head>

<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
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
                    on:click={loadSessionNote}
                    class="btn btn-secondary"
                >
                    Try Again
                </button>
            </div>
        </div>
    {:else if sessionNote}
        <!-- Header -->
        <div class="mb-8">
            <div class="flex items-center space-x-4 mb-4">
                <button
                    on:click={() => goto(`/campaigns/${campaignId}/sessions`)}
                    class="text-gray-400 hover:text-white flex items-center"
                >
                    <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                    </svg>
                    Back to Sessions
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
                    <div class="flex items-center space-x-4 mb-2">
                        <h1 class="text-3xl font-bold text-white">{sessionNote.title}</h1>
                        {#if sessionNote.session_number}
                            <span class="px-3 py-1 rounded text-sm bg-blue-600 text-blue-100">
                                Session #{sessionNote.session_number}
                            </span>
                        {/if}
                    </div>
                    
                    <div class="flex flex-wrap gap-2 mb-4">
                        <span class="px-2 py-1 rounded text-xs {getStatusBadgeClass(sessionNote.status)}">
                            {capitalizeWords(sessionNote.status)}
                        </span>
                        
                        <span class="px-2 py-1 rounded text-xs {getVisibilityBadgeClass(sessionNote.visibility)}">
                            {capitalizeWords(sessionNote.visibility)}
                        </span>
                    </div>

                    <div class="text-gray-400 space-y-1">
                        {#if sessionNote.session_date}
                            <p><strong>Session Date:</strong> {sessionNote.session_date}</p>
                        {/if}
                        {#if sessionNote.in_world_date}
                            <p><strong>In-World Date:</strong> {sessionNote.in_world_date}</p>
                        {/if}
                        <p>Created on {formatDate(sessionNote.created_at)}</p>
                        {#if sessionNote.updated_at !== sessionNote.created_at}
                            <p>Updated on {formatDate(sessionNote.updated_at)}</p>
                        {/if}
                    </div>
                </div>

                <div class="flex space-x-3">
                    <button
                        on:click={handleDuplicate}
                        class="btn btn-secondary"
                        title="Duplicate as next session"
                    >
                        <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                        Duplicate
                    </button>

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
            <!-- Summary and Notes -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {#if sessionNote.summary}
                    <div class="card">
                        <h2 class="text-xl font-semibold text-white mb-3">Session Summary</h2>
                        <p class="text-gray-300 whitespace-pre-wrap">{sessionNote.summary}</p>
                    </div>
                {/if}

                {#if sessionNote.detailed_notes}
                    <div class="card">
                        <h2 class="text-xl font-semibold text-white mb-3">Detailed Notes</h2>
                        <p class="text-gray-300 whitespace-pre-wrap">{sessionNote.detailed_notes}</p>
                    </div>
                {/if}
            </div>

            <!-- Player Characters -->
            {#if sessionNote.player_characters && sessionNote.player_characters.length > 0}
                <div class="card">
                    <h2 class="text-xl font-semibold text-white mb-4">Player Characters</h2>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {#each sessionNote.player_characters as pc}
                            <div class="bg-gray-700 p-4 rounded">
                                <h3 class="font-medium text-white">{pc.name}</h3>
                                {#if pc.player}
                                    <p class="text-sm text-gray-400 mb-2">Player: {pc.player}</p>
                                {/if}
                                {#if pc.actions}
                                    <p class="text-gray-300 text-sm">{pc.actions}</p>
                                {/if}
                            </div>
                        {/each}
                    </div>
                </div>
            {/if}

            <!-- NPCs and Locations -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {#if sessionNote.npcs_encountered && sessionNote.npcs_encountered.length > 0}
                    <div class="card">
                        <h2 class="text-xl font-semibold text-white mb-4">NPCs Encountered</h2>
                        <div class="space-y-3">
                            {#each sessionNote.npcs_encountered as npc}
                                <div class="bg-gray-700 p-3 rounded">
                                    <h3 class="font-medium text-white">{npc.name}</h3>
                                    {#if npc.interaction}
                                        <p class="text-gray-300 text-sm mt-1">{npc.interaction}</p>
                                    {/if}
                                </div>
                            {/each}
                        </div>
                    </div>
                {/if}

                {#if sessionNote.locations_visited && sessionNote.locations_visited.length > 0}
                    <div class="card">
                        <h2 class="text-xl font-semibold text-white mb-4">Locations Visited</h2>
                        <div class="space-y-3">
                            {#each sessionNote.locations_visited as location}
                                <div class="bg-gray-700 p-3 rounded">
                                    <h3 class="font-medium text-white">{location.name}</h3>
                                    {#if location.description}
                                        <p class="text-gray-300 text-sm mt-1">{location.description}</p>
                                    {/if}
                                </div>
                            {/each}
                        </div>
                    </div>
                {/if}
            </div>

            <!-- Events and Experience -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {#if sessionNote.events_occurred && sessionNote.events_occurred.length > 0}
                    <div class="card">
                        <h2 class="text-xl font-semibold text-white mb-4">Events</h2>
                        <div class="space-y-3">
                            {#each sessionNote.events_occurred as event}
                                <div class="bg-gray-700 p-3 rounded">
                                    <p class="text-gray-300 text-sm">{event.description}</p>
                                </div>
                            {/each}
                        </div>
                    </div>
                {/if}

                {#if sessionNote.experience_gained > 0}
                    <div class="card">
                        <h2 class="text-xl font-semibold text-white mb-3">Experience Gained</h2>
                        <div class="text-center py-6">
                            <span class="text-4xl font-bold text-green-400">{sessionNote.experience_gained}</span>
                            <span class="text-gray-400 ml-2">XP</span>
                        </div>
                    </div>
                {/if}
            </div>

            <!-- DM Notes -->
            {#if sessionNote.dm_notes}
                <div class="card">
                    <h2 class="text-xl font-semibold text-white mb-3">DM Notes</h2>
                    <p class="text-gray-300 whitespace-pre-wrap">{sessionNote.dm_notes}</p>
                </div>
            {/if}

            <!-- Next Session Prep -->
            {#if sessionNote.next_session_prep}
                <div class="card">
                    <h2 class="text-xl font-semibold text-white mb-3">Next Session Preparation</h2>
                    <p class="text-gray-300 whitespace-pre-wrap">{sessionNote.next_session_prep}</p>
                </div>
            {/if}
        </div>
    {/if}
</div>

<!-- Edit Modal -->
{#if showEditModal && sessionNote}
    <EditSessionNoteModal 
        {campaignId}
        {sessionNote}
        on:updated={handleSessionNoteUpdated}
        on:close={handleModalClose}
    />
{/if}

<!-- Delete Confirmation Modal -->
{#if showDeleteConfirm}
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div class="bg-gray-800 rounded-lg max-w-md w-full p-6">
            <h3 class="text-xl font-semibold text-white mb-4">Delete Session Note</h3>
            <p class="text-gray-300 mb-6">
                Are you sure you want to delete "{sessionNote?.title}"? This action cannot be undone.
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