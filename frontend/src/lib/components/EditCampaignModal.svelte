<script>
    import { createEventDispatcher } from 'svelte';
    import { campaignAPI } from '$lib/api.js';

    export let campaign;

    const dispatch = createEventDispatcher();

    let formData = {
        name: campaign?.name || '',
        description: campaign?.description || '',
        world_name: campaign?.world_name || '',
        current_date: campaign?.current_date || ''
    };
    
    let loading = false;
    let error = '';

    async function handleSubmit() {
        if (!formData.name.trim()) {
            error = 'Campaign name is required';
            return;
        }

        try {
            loading = true;
            error = '';
            
            const updatedCampaign = await campaignAPI.updateCampaign(campaign.id, formData);
            
            dispatch('updated', { campaign: updatedCampaign });
        } catch (err) {
            error = err.message || 'Failed to update campaign';
        } finally {
            loading = false;
        }
    }

    function handleCancel() {
        dispatch('close');
    }
</script>

<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
            <div class="flex items-center justify-between mb-6">
                <h2 class="text-2xl font-bold text-white">Edit Campaign</h2>
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
                <!-- Campaign Name -->
                <div>
                    <label for="name" class="block text-sm font-medium text-gray-300 mb-2">
                        Campaign Name *
                    </label>
                    <input
                        type="text"
                        id="name"
                        bind:value={formData.name}
                        class="input"
                        placeholder="Enter campaign name..."
                        required
                        disabled={loading}
                    />
                </div>

                <!-- Description -->
                <div>
                    <label for="description" class="block text-sm font-medium text-gray-300 mb-2">
                        Description
                    </label>
                    <textarea
                        id="description"
                        bind:value={formData.description}
                        rows="4"
                        class="input"
                        placeholder="Describe your campaign..."
                        disabled={loading}
                    ></textarea>
                </div>

                <!-- World Name -->
                <div>
                    <label for="world_name" class="block text-sm font-medium text-gray-300 mb-2">
                        World Name
                    </label>
                    <input
                        type="text"
                        id="world_name"
                        bind:value={formData.world_name}
                        class="input"
                        placeholder="Enter world name..."
                        disabled={loading}
                    />
                </div>

                <!-- Current Date -->
                <div>
                    <label for="current_date" class="block text-sm font-medium text-gray-300 mb-2">
                        Current Date (in-game)
                    </label>
                    <input
                        type="text"
                        id="current_date"
                        bind:value={formData.current_date}
                        class="input"
                        placeholder="e.g., 15th of Flamerule, 1494 DR"
                        disabled={loading}
                    />
                    <p class="text-sm text-gray-400 mt-1">
                        Enter the current date in your campaign world
                    </p>
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
                        disabled={loading || !formData.name.trim()}
                    >
                        {loading ? 'Saving...' : 'Save Changes'}
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>