<script>
    import { createEventDispatcher } from 'svelte';
    import { campaignAPI } from '$lib/api.js';

    const dispatch = createEventDispatcher();

    let name = '';
    let description = '';
    let worldName = '';
    let currentDate = '';
    let loading = false;
    let error = '';

    async function handleSubmit() {
        if (!name.trim()) {
            error = 'Campaign name is required';
            return;
        }

        loading = true;
        error = '';

        try {
            const campaignData = {
                name: name.trim(),
                description: description.trim() || null,
                world_name: worldName.trim() || null,
                current_date: currentDate.trim() || null
            };

            await campaignAPI.createCampaign(campaignData);
            dispatch('created');
        } catch (err) {
            error = err.message || 'Failed to create campaign';
        } finally {
            loading = false;
        }
    }

    function handleClose() {
        dispatch('close');
    }

    function handleKeydown(event) {
        if (event.key === 'Escape') {
            handleClose();
        }
    }
</script>

<svelte:window on:keydown={handleKeydown} />

<!-- Modal Backdrop -->
<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
    <!-- Modal Content -->
    <div class="bg-gray-800 rounded-lg max-w-md w-full max-h-screen overflow-y-auto">
        <!-- Header -->
        <div class="flex items-center justify-between p-6 border-b border-gray-700">
            <h2 class="text-xl font-semibold text-white">Create New Campaign</h2>
            <button
                on:click={handleClose}
                class="text-gray-400 hover:text-white"
            >
                <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>
        </div>

        <!-- Form -->
        <form on:submit|preventDefault={handleSubmit} class="p-6 space-y-4">
            {#if error}
                <div class="bg-red-900 border border-red-700 text-red-100 px-4 py-3 rounded">
                    {error}
                </div>
            {/if}

            <div>
                <label for="campaignName" class="block text-sm font-medium text-gray-300 mb-2">
                    Campaign Name <span class="text-red-400">*</span>
                </label>
                <input
                    id="campaignName"
                    type="text"
                    bind:value={name}
                    class="input w-full"
                    placeholder="Enter campaign name"
                    required
                />
            </div>

            <div>
                <label for="worldName" class="block text-sm font-medium text-gray-300 mb-2">
                    World Name
                </label>
                <input
                    id="worldName"
                    type="text"
                    bind:value={worldName}
                    class="input w-full"
                    placeholder="Enter world name (optional)"
                />
            </div>

            <div>
                <label for="currentDate" class="block text-sm font-medium text-gray-300 mb-2">
                    Current Date
                </label>
                <input
                    id="currentDate"
                    type="text"
                    bind:value={currentDate}
                    class="input w-full"
                    placeholder="e.g., 1st of Tarsakh, 1491 DR"
                />
                <p class="text-xs text-gray-500 mt-1">
                    In-world calendar date (optional)
                </p>
            </div>

            <div>
                <label for="description" class="block text-sm font-medium text-gray-300 mb-2">
                    Description
                </label>
                <textarea
                    id="description"
                    bind:value={description}
                    rows="3"
                    class="input w-full resize-none"
                    placeholder="Brief description of your campaign (optional)"
                ></textarea>
            </div>

            <!-- Actions -->
            <div class="flex justify-end space-x-3 pt-4">
                <button
                    type="button"
                    on:click={handleClose}
                    class="btn btn-secondary"
                    disabled={loading}
                >
                    Cancel
                </button>
                <button
                    type="submit"
                    class="btn btn-primary {loading ? 'opacity-50 cursor-not-allowed' : ''}"
                    disabled={loading}
                >
                    {loading ? 'Creating...' : 'Create Campaign'}
                </button>
            </div>
        </form>
    </div>
</div>