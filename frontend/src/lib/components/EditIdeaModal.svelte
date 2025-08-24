<script>
    import { createEventDispatcher } from 'svelte';
    import { ideaAPI } from '$lib/api.js';

    export let campaignId;
    export let idea;
    
    const dispatch = createEventDispatcher();

    let saving = false;
    let error = '';
    let formData = {
        content: idea.content || '',
        status: idea.status || 'raw_idea',
        idea_type: idea.idea_type || '',
        priority: idea.priority || 'medium',
        notes: idea.notes || ''
    };

    const statusOptions = [
        { value: 'raw_idea', label: 'Raw Idea', description: 'Initial concept, needs development' },
        { value: 'developing', label: 'Developing', description: 'Being worked on and refined' },
        { value: 'ready_to_implement', label: 'Ready to Implement', description: 'Fully planned and ready to use' },
        { value: 'implemented', label: 'Implemented', description: 'Already used in the campaign' }
    ];

    const ideaTypes = [
        { value: '', label: 'General Idea' },
        { value: 'npc', label: 'NPC' },
        { value: 'location', label: 'Location' },
        { value: 'plot_hook', label: 'Plot Hook' },
        { value: 'lore', label: 'Lore' },
        { value: 'item', label: 'Item' },
        { value: 'organization', label: 'Organization' },
        { value: 'event', label: 'Event' }
    ];

    const priorityOptions = [
        { value: 'low', label: 'Low', color: 'text-gray-400' },
        { value: 'medium', label: 'Medium', color: 'text-yellow-400' },
        { value: 'high', label: 'High', color: 'text-red-400' }
    ];

    async function handleSubmit() {
        if (!formData.content.trim()) {
            error = 'Idea content is required';
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

            const updatedIdea = await ideaAPI.updateIdea(campaignId, idea.id, submitData);
            dispatch('updated', { idea: updatedIdea });
        } catch (err) {
            error = err.message || 'Failed to update idea';
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
    <div class="bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b border-gray-700">
            <h2 class="text-2xl font-semibold text-white">Edit Idea</h2>
        </div>
        
        <div class="p-6">
            {#if error}
                <div class="bg-red-900 border border-red-700 text-red-100 px-4 py-3 rounded mb-6">
                    {error}
                </div>
            {/if}

            <form on:submit|preventDefault={handleSubmit} class="space-y-6">
                <!-- Idea Content -->
                <div>
                    <label class="block text-sm font-medium text-gray-300 mb-2">
                        Idea <span class="text-red-400">*</span>
                    </label>
                    <textarea
                        bind:value={formData.content}
                        rows="4"
                        class="input w-full resize-y"
                        placeholder="Describe your idea in detail..."
                        required
                    ></textarea>
                </div>

                <!-- Type and Priority -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label class="block text-sm font-medium text-gray-300 mb-2">
                            Type
                        </label>
                        <select bind:value={formData.idea_type} class="input w-full">
                            {#each ideaTypes as type}
                                <option value={type.value}>{type.label}</option>
                            {/each}
                        </select>
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-300 mb-2">
                            Priority
                        </label>
                        <select bind:value={formData.priority} class="input w-full">
                            {#each priorityOptions as priority}
                                <option value={priority.value} class={priority.color}>
                                    {priority.label}
                                </option>
                            {/each}
                        </select>
                    </div>
                </div>

                <!-- Status -->
                <div>
                    <label class="block text-sm font-medium text-gray-300 mb-3">
                        Status
                    </label>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {#each statusOptions as status}
                            <button
                                type="button"
                                on:click={() => formData.status = status.value}
                                class="p-4 rounded-lg border-2 text-left transition-colors {
                                    formData.status === status.value 
                                        ? 'border-red-500 bg-red-900 bg-opacity-20' 
                                        : 'border-gray-600 bg-gray-700 hover:border-gray-500'
                                }"
                            >
                                <div class="font-medium text-white">{status.label}</div>
                                <div class="text-sm text-gray-400 mt-1">{status.description}</div>
                            </button>
                        {/each}
                    </div>
                </div>

                <!-- Notes -->
                <div>
                    <label class="block text-sm font-medium text-gray-300 mb-2">Notes</label>
                    <textarea
                        bind:value={formData.notes}
                        rows="3"
                        class="input w-full resize-y"
                        placeholder="Additional notes and development thoughts..."
                    ></textarea>
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