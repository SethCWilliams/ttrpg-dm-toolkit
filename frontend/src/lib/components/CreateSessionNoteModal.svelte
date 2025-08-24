<script>
    import { createEventDispatcher } from 'svelte';
    import { sessionNoteAPI } from '$lib/api.js';

    export let campaignId;

    const dispatch = createEventDispatcher();

    let formData = {
        title: '',
        session_number: null,
        session_date: '',
        in_world_date: '',
        summary: '',
        detailed_notes: '',
        player_characters: [],
        npcs_encountered: [],
        locations_visited: [],
        plot_hooks_advanced: [],
        events_occurred: [],
        items_acquired: [],
        experience_gained: 0,
        loot_acquired: [],
        combat_encounters: [],
        social_encounters: [],
        exploration_discoveries: [],
        world_state_changes: [],
        dm_notes: '',
        next_session_prep: '',
        status: 'draft',
        visibility: 'dm_only'
    };
    
    let loading = false;
    let error = '';

    // Get today's date for default session date
    const today = new Date().toISOString().split('T')[0];
    formData.session_date = today;

    // Dynamic fields for arrays
    let newPC = { name: '', player: '', actions: '' };
    let newNPC = { name: '', interaction: '' };
    let newLocation = { name: '', description: '' };
    let newEvent = { description: '' };

    async function handleSubmit() {
        if (!formData.title.trim()) {
            error = 'Session title is required';
            return;
        }

        try {
            loading = true;
            error = '';
            
            const sessionNote = await sessionNoteAPI.createSessionNote(campaignId, formData);
            
            dispatch('created', { sessionNote });
        } catch (err) {
            error = err.message || 'Failed to create session note';
        } finally {
            loading = false;
        }
    }

    function handleCancel() {
        dispatch('close');
    }

    function addPlayerCharacter() {
        if (newPC.name.trim()) {
            formData.player_characters = [...formData.player_characters, { ...newPC }];
            newPC = { name: '', player: '', actions: '' };
        }
    }

    function removePlayerCharacter(index) {
        formData.player_characters = formData.player_characters.filter((_, i) => i !== index);
    }

    function addNPC() {
        if (newNPC.name.trim()) {
            formData.npcs_encountered = [...formData.npcs_encountered, { ...newNPC }];
            newNPC = { name: '', interaction: '' };
        }
    }

    function removeNPC(index) {
        formData.npcs_encountered = formData.npcs_encountered.filter((_, i) => i !== index);
    }

    function addLocation() {
        if (newLocation.name.trim()) {
            formData.locations_visited = [...formData.locations_visited, { ...newLocation }];
            newLocation = { name: '', description: '' };
        }
    }

    function removeLocation(index) {
        formData.locations_visited = formData.locations_visited.filter((_, i) => i !== index);
    }

    function addEvent() {
        if (newEvent.description.trim()) {
            formData.events_occurred = [...formData.events_occurred, { ...newEvent }];
            newEvent = { description: '' };
        }
    }

    function removeEvent(index) {
        formData.events_occurred = formData.events_occurred.filter((_, i) => i !== index);
    }
</script>

<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
            <div class="flex items-center justify-between mb-6">
                <h2 class="text-2xl font-bold text-white">New Session Note</h2>
                <button
                    on:click={handleCancel}
                    class="text-gray-400 hover:text-white"
                    disabled={loading}
                >
                    <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>

            {#if error}
                <div class="bg-red-900 border border-red-700 text-red-100 px-4 py-3 rounded mb-6">
                    {error}
                </div>
            {/if}

            <form on:submit|preventDefault={handleSubmit} class="space-y-6">
                <!-- Basic Information -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label for="title" class="block text-sm font-medium text-gray-300 mb-2">
                            Session Title *
                        </label>
                        <input
                            type="text"
                            id="title"
                            bind:value={formData.title}
                            class="input"
                            placeholder="e.g., The Goblin Ambush"
                            required
                            disabled={loading}
                        />
                    </div>

                    <div>
                        <label for="session_number" class="block text-sm font-medium text-gray-300 mb-2">
                            Session Number
                        </label>
                        <input
                            type="number"
                            id="session_number"
                            bind:value={formData.session_number}
                            class="input"
                            placeholder="Auto-assigned if blank"
                            min="1"
                            disabled={loading}
                        />
                    </div>

                    <div>
                        <label for="session_date" class="block text-sm font-medium text-gray-300 mb-2">
                            Session Date (Real World)
                        </label>
                        <input
                            type="date"
                            id="session_date"
                            bind:value={formData.session_date}
                            class="input"
                            disabled={loading}
                        />
                    </div>

                    <div>
                        <label for="in_world_date" class="block text-sm font-medium text-gray-300 mb-2">
                            In-World Date
                        </label>
                        <input
                            type="text"
                            id="in_world_date"
                            bind:value={formData.in_world_date}
                            class="input"
                            placeholder="e.g., 15th of Flamerule, 1494 DR"
                            disabled={loading}
                        />
                    </div>
                </div>

                <!-- Summary and Notes -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label for="summary" class="block text-sm font-medium text-gray-300 mb-2">
                            Session Summary
                        </label>
                        <textarea
                            id="summary"
                            bind:value={formData.summary}
                            rows="4"
                            class="input"
                            placeholder="Brief overview of what happened..."
                            disabled={loading}
                        ></textarea>
                    </div>

                    <div>
                        <label for="detailed_notes" class="block text-sm font-medium text-gray-300 mb-2">
                            Detailed Notes
                        </label>
                        <textarea
                            id="detailed_notes"
                            bind:value={formData.detailed_notes}
                            rows="4"
                            class="input"
                            placeholder="Detailed session notes..."
                            disabled={loading}
                        ></textarea>
                    </div>
                </div>

                <!-- Player Characters -->
                <div class="card bg-gray-700">
                    <h3 class="text-lg font-semibold text-white mb-4">Player Characters</h3>
                    
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                        <input
                            type="text"
                            bind:value={newPC.name}
                            placeholder="Character name"
                            class="input"
                            disabled={loading}
                        />
                        <input
                            type="text"
                            bind:value={newPC.player}
                            placeholder="Player name"
                            class="input"
                            disabled={loading}
                        />
                        <div class="flex">
                            <input
                                type="text"
                                bind:value={newPC.actions}
                                placeholder="Key actions"
                                class="input rounded-r-none"
                                disabled={loading}
                            />
                            <button
                                type="button"
                                on:click={addPlayerCharacter}
                                class="btn btn-secondary rounded-l-none"
                                disabled={loading}
                            >
                                Add
                            </button>
                        </div>
                    </div>

                    {#if formData.player_characters.length > 0}
                        <div class="space-y-2">
                            {#each formData.player_characters as pc, index}
                                <div class="flex items-center justify-between bg-gray-600 p-3 rounded">
                                    <div>
                                        <span class="font-medium text-white">{pc.name}</span>
                                        {#if pc.player}
                                            <span class="text-gray-300">({pc.player})</span>
                                        {/if}
                                        {#if pc.actions}
                                            <span class="text-gray-400">- {pc.actions}</span>
                                        {/if}
                                    </div>
                                    <button
                                        type="button"
                                        on:click={() => removePlayerCharacter(index)}
                                        class="text-red-400 hover:text-red-300"
                                        disabled={loading}
                                    >
                                        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                                        </svg>
                                    </button>
                                </div>
                            {/each}
                        </div>
                    {/if}
                </div>

                <!-- NPCs Encountered -->
                <div class="card bg-gray-700">
                    <h3 class="text-lg font-semibold text-white mb-4">NPCs Encountered</h3>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <input
                            type="text"
                            bind:value={newNPC.name}
                            placeholder="NPC name"
                            class="input"
                            disabled={loading}
                        />
                        <div class="flex">
                            <input
                                type="text"
                                bind:value={newNPC.interaction}
                                placeholder="Interaction details"
                                class="input rounded-r-none"
                                disabled={loading}
                            />
                            <button
                                type="button"
                                on:click={addNPC}
                                class="btn btn-secondary rounded-l-none"
                                disabled={loading}
                            >
                                Add
                            </button>
                        </div>
                    </div>

                    {#if formData.npcs_encountered.length > 0}
                        <div class="space-y-2">
                            {#each formData.npcs_encountered as npc, index}
                                <div class="flex items-center justify-between bg-gray-600 p-3 rounded">
                                    <div>
                                        <span class="font-medium text-white">{npc.name}</span>
                                        {#if npc.interaction}
                                            <span class="text-gray-400">- {npc.interaction}</span>
                                        {/if}
                                    </div>
                                    <button
                                        type="button"
                                        on:click={() => removeNPC(index)}
                                        class="text-red-400 hover:text-red-300"
                                        disabled={loading}
                                    >
                                        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                                        </svg>
                                    </button>
                                </div>
                            {/each}
                        </div>
                    {/if}
                </div>

                <!-- Experience and Settings -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                        <label for="experience_gained" class="block text-sm font-medium text-gray-300 mb-2">
                            Experience Gained
                        </label>
                        <input
                            type="number"
                            id="experience_gained"
                            bind:value={formData.experience_gained}
                            class="input"
                            min="0"
                            disabled={loading}
                        />
                    </div>

                    <div>
                        <label for="status" class="block text-sm font-medium text-gray-300 mb-2">
                            Status
                        </label>
                        <select id="status" bind:value={formData.status} class="input" disabled={loading}>
                            <option value="draft">Draft</option>
                            <option value="published">Published</option>
                            <option value="archived">Archived</option>
                        </select>
                    </div>

                    <div>
                        <label for="visibility" class="block text-sm font-medium text-gray-300 mb-2">
                            Visibility
                        </label>
                        <select id="visibility" bind:value={formData.visibility} class="input" disabled={loading}>
                            <option value="dm_only">DM Only</option>
                            <option value="player_visible">Player Visible</option>
                        </select>
                    </div>
                </div>

                <!-- Submit Buttons -->
                <div class="flex justify-end space-x-3 pt-6">
                    <button
                        type="button"
                        on:click={handleCancel}
                        class="btn btn-secondary"
                        disabled={loading}
                    >
                        Cancel
                    </button>
                    <button
                        type="submit"
                        class="btn btn-primary"
                        disabled={loading || !formData.title.trim()}
                    >
                        {loading ? 'Creating...' : 'Create Session Note'}
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>