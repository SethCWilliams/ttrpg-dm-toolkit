<script>
    import { createEventDispatcher, onMount } from 'svelte';
    import { eventAPI, locationAPI, npcAPI } from '$lib/api.js';

    export let campaignId;
    export let event;
    
    const dispatch = createEventDispatcher();

    let loading = false;
    let saving = false;
    let error = '';
    let availableLocations = [];
    let availableNPCs = [];
    let formData = {
        title: event.title || '',
        description: event.description || '',
        event_type: event.event_type || 'historical',
        date: event.date || '',
        location_id: event.location_id,
        participants: event.participants || [],
        causes: event.causes || [],
        effects: event.effects || [],
        visibility: event.visibility || 'dm_only',
        status: event.status || 'draft',
        notes: event.notes || ''
    };

    const eventTypes = [
        { value: 'historical', label: 'Historical', description: 'Events from the past' },
        { value: 'current', label: 'Current', description: 'Ongoing events' },
        { value: 'scheduled', label: 'Scheduled', description: 'Planned future events' },
        { value: 'recurring', label: 'Recurring', description: 'Repeating events' }
    ];

    const statusOptions = [
        { value: 'draft', label: 'Draft' },
        { value: 'active', label: 'Active' },
        { value: 'completed', label: 'Completed' },
        { value: 'cancelled', label: 'Cancelled' }
    ];

    const visibilityOptions = [
        { value: 'dm_only', label: 'DM Only' },
        { value: 'partially_known', label: 'Partially Known' },
        { value: 'player_known', label: 'Known to Players' }
    ];

    onMount(async () => {
        await Promise.all([
            loadAvailableLocations(),
            loadAvailableNPCs()
        ]);
    });

    async function loadAvailableLocations() {
        try {
            const response = await locationAPI.getLocations(campaignId, { limit: 100 });
            availableLocations = response.items || [];
        } catch (err) {
            console.error('Failed to load locations:', err);
        }
    }

    async function loadAvailableNPCs() {
        try {
            const response = await npcAPI.getNPCs(campaignId, { limit: 100 });
            availableNPCs = response.items || [];
        } catch (err) {
            console.error('Failed to load NPCs:', err);
        }
    }

    function addParticipant() {
        formData.participants = [...formData.participants, { type: 'npc', id: null, role: '', notes: '' }];
    }

    function removeParticipant(index) {
        formData.participants = formData.participants.filter((_, i) => i !== index);
    }

    function addCause() {
        const input = document.getElementById('cause_input');
        if (input && input.value.trim()) {
            formData.causes = [...formData.causes, input.value.trim()];
            input.value = '';
        }
    }

    function removeCause(index) {
        formData.causes = formData.causes.filter((_, i) => i !== index);
    }

    function addEffect() {
        const input = document.getElementById('effect_input');
        if (input && input.value.trim()) {
            formData.effects = [...formData.effects, input.value.trim()];
            input.value = '';
        }
    }

    function removeEffect(index) {
        formData.effects = formData.effects.filter((_, i) => i !== index);
    }

    function handleKeydown(event, action) {
        if (event.key === 'Enter') {
            event.preventDefault();
            action();
        }
    }

    async function handleSubmit() {
        if (!formData.title.trim()) {
            error = 'Event title is required';
            return;
        }

        try {
            saving = true;
            error = '';
            
            // Clean up form data
            const submitData = { ...formData };
            
            // Convert empty strings to null for optional fields
            Object.keys(submitData).forEach(key => {
                if (submitData[key] === '' && typeof submitData[key] === 'string') {
                    submitData[key] = null;
                }
            });

            // Filter out participants without proper data
            submitData.participants = submitData.participants.filter(p => 
                p.type && (p.id || p.role || p.notes)
            );

            const updatedEvent = await eventAPI.updateEvent(campaignId, event.id, submitData);
            dispatch('updated', { event: updatedEvent });
        } catch (err) {
            error = err.message || 'Failed to update event';
        } finally {
            saving = false;
        }
    }

    function cancel() {
        dispatch('close');
    }

    function capitalizeWords(str) {
        if (!str) return '';
        return str.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
</script>

<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b border-gray-700">
            <h2 class="text-2xl font-semibold text-white">Edit Event</h2>
        </div>
        
        <div class="p-6">
            {#if error}
                <div class="bg-red-900 border border-red-700 text-red-100 px-4 py-3 rounded mb-6">
                    {error}
                </div>
            {/if}

            <form on:submit|preventDefault={handleSubmit} class="space-y-6">
                <!-- Basic Information -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="md:col-span-2">
                        <label class="block text-sm font-medium text-gray-300 mb-2">
                            Event Title <span class="text-red-400">*</span>
                        </label>
                        <input
                            type="text"
                            bind:value={formData.title}
                            class="input w-full"
                            placeholder="Enter event title"
                            required
                        />
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-300 mb-2">
                            Event Type
                        </label>
                        <select bind:value={formData.event_type} class="input w-full">
                            {#each eventTypes as type}
                                <option value={type.value}>{type.label}</option>
                            {/each}
                        </select>
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-300 mb-2">
                            Date (In-World)
                        </label>
                        <input
                            type="text"
                            bind:value={formData.date}
                            class="input w-full"
                            placeholder="e.g., 15th of Frostfall, Year 4E 201"
                        />
                    </div>

                    <div class="md:col-span-2">
                        <label class="block text-sm font-medium text-gray-300 mb-2">
                            Description
                        </label>
                        <textarea
                            bind:value={formData.description}
                            rows="4"
                            class="input w-full resize-y"
                            placeholder="Describe what happened or will happen..."
                        ></textarea>
                    </div>
                </div>

                <!-- Location -->
                <div>
                    <label class="block text-sm font-medium text-gray-300 mb-2">
                        Location
                    </label>
                    <select bind:value={formData.location_id} class="input w-full">
                        <option value={null}>No specific location</option>
                        {#each availableLocations as location}
                            <option value={location.id}>
                                {location.name} ({capitalizeWords(location.type)})
                            </option>
                        {/each}
                    </select>
                </div>

                <!-- Participants -->
                <div class="border-t border-gray-700 pt-6">
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-lg font-medium text-white">Participants</h3>
                        <button
                            type="button"
                            on:click={addParticipant}
                            class="btn btn-secondary text-sm"
                        >
                            Add Participant
                        </button>
                    </div>
                    
                    {#each formData.participants as participant, index}
                        <div class="bg-gray-700 p-4 rounded mb-4">
                            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                                <div>
                                    <label class="block text-sm font-medium text-gray-300 mb-1">Type</label>
                                    <select bind:value={participant.type} class="input w-full">
                                        <option value="npc">NPC</option>
                                        <option value="organization">Organization</option>
                                        <option value="group">Group</option>
                                        <option value="other">Other</option>
                                    </select>
                                </div>
                                
                                {#if participant.type === 'npc'}
                                    <div>
                                        <label class="block text-sm font-medium text-gray-300 mb-1">NPC</label>
                                        <select bind:value={participant.id} class="input w-full">
                                            <option value={null}>Select NPC</option>
                                            {#each availableNPCs as npc}
                                                <option value={npc.id}>{npc.name}</option>
                                            {/each}
                                        </select>
                                    </div>
                                {:else}
                                    <div>
                                        <label class="block text-sm font-medium text-gray-300 mb-1">Name</label>
                                        <input
                                            type="text"
                                            bind:value={participant.name}
                                            class="input w-full"
                                            placeholder="Enter name"
                                        />
                                    </div>
                                {/if}
                                
                                <div>
                                    <label class="block text-sm font-medium text-gray-300 mb-1">Role</label>
                                    <input
                                        type="text"
                                        bind:value={participant.role}
                                        class="input w-full"
                                        placeholder="e.g., Leader, Victim, Witness"
                                    />
                                </div>
                            </div>
                            
                            <div class="flex items-start gap-4">
                                <div class="flex-1">
                                    <label class="block text-sm font-medium text-gray-300 mb-1">Notes</label>
                                    <input
                                        type="text"
                                        bind:value={participant.notes}
                                        class="input w-full"
                                        placeholder="Additional participant details"
                                    />
                                </div>
                                <button
                                    type="button"
                                    on:click={() => removeParticipant(index)}
                                    class="btn bg-red-600 hover:bg-red-700 text-white mt-6"
                                >
                                    Remove
                                </button>
                            </div>
                        </div>
                    {/each}
                </div>

                <!-- Causes and Effects -->
                <div class="border-t border-gray-700 pt-6">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <!-- Causes -->
                        <div>
                            <h3 class="text-lg font-medium text-white mb-4">Causes</h3>
                            <div class="flex mb-3">
                                <input
                                    type="text"
                                    id="cause_input"
                                    class="input flex-1 mr-2"
                                    placeholder="Add a cause"
                                    on:keydown={(e) => handleKeydown(e, addCause)}
                                />
                                <button
                                    type="button"
                                    on:click={addCause}
                                    class="btn btn-secondary"
                                >
                                    Add
                                </button>
                            </div>
                            {#if formData.causes.length > 0}
                                <div class="space-y-2">
                                    {#each formData.causes as cause, index}
                                        <div class="flex items-center justify-between bg-gray-700 p-2 rounded">
                                            <span class="text-gray-300">{cause}</span>
                                            <button
                                                type="button"
                                                on:click={() => removeCause(index)}
                                                class="text-red-400 hover:text-red-300 ml-2"
                                            >
                                                ×
                                            </button>
                                        </div>
                                    {/each}
                                </div>
                            {/if}
                        </div>

                        <!-- Effects -->
                        <div>
                            <h3 class="text-lg font-medium text-white mb-4">Effects</h3>
                            <div class="flex mb-3">
                                <input
                                    type="text"
                                    id="effect_input"
                                    class="input flex-1 mr-2"
                                    placeholder="Add an effect"
                                    on:keydown={(e) => handleKeydown(e, addEffect)}
                                />
                                <button
                                    type="button"
                                    on:click={addEffect}
                                    class="btn btn-secondary"
                                >
                                    Add
                                </button>
                            </div>
                            {#if formData.effects.length > 0}
                                <div class="space-y-2">
                                    {#each formData.effects as effect, index}
                                        <div class="flex items-center justify-between bg-gray-700 p-2 rounded">
                                            <span class="text-gray-300">{effect}</span>
                                            <button
                                                type="button"
                                                on:click={() => removeEffect(index)}
                                                class="text-red-400 hover:text-red-300 ml-2"
                                            >
                                                ×
                                            </button>
                                        </div>
                                    {/each}
                                </div>
                            {/if}
                        </div>
                    </div>
                </div>

                <!-- Notes -->
                <div class="border-t border-gray-700 pt-6">
                    <label class="block text-sm font-medium text-gray-300 mb-2">Notes</label>
                    <textarea
                        bind:value={formData.notes}
                        rows="3"
                        class="input w-full resize-y"
                        placeholder="Additional notes and DM information..."
                    ></textarea>
                </div>

                <!-- Meta Fields -->
                <div class="border-t border-gray-700 pt-6">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label class="block text-sm font-medium text-gray-300 mb-2">Status</label>
                            <select bind:value={formData.status} class="input w-full">
                                {#each statusOptions as status}
                                    <option value={status.value}>{status.label}</option>
                                {/each}
                            </select>
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-300 mb-2">Visibility</label>
                            <select bind:value={formData.visibility} class="input w-full">
                                {#each visibilityOptions as visibility}
                                    <option value={visibility.value}>{visibility.label}</option>
                                {/each}
                            </select>
                        </div>
                    </div>
                </div>

                <!-- Actions -->
                <div class="flex justify-end space-x-3 pt-6 border-t border-gray-700">
                    <button
                        type="button"
                        on:click={cancel}
                        class="btn btn-secondary"
                        disabled={saving}
                    >
                        Cancel
                    </button>
                    <button
                        type="submit"
                        class="btn btn-primary"
                        disabled={saving}
                    >
                        {saving ? 'Saving...' : 'Save Changes'}
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>