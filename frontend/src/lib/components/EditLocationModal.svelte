<script>
    import { createEventDispatcher, onMount } from 'svelte';
    import { locationAPI } from '$lib/api.js';

    export let campaignId;
    export let location;
    export let availableParents = [];

    const dispatch = createEventDispatcher();

    let loading = false;
    let saving = false;
    let error = '';
    let templates = {};
    let currentTemplate = {};
    let formData = {
        name: location.name || '',
        type: location.type || '',
        parent_location_id: location.parent_location_id || null,
        status: location.status || 'draft',
        visibility: location.visibility || 'dm_only'
    };

    const locationTypes = [
        { value: 'region', label: 'Region', description: 'Large geographical area' },
        { value: 'settlement', label: 'Settlement', description: 'City, town, or village' },
        { value: 'structure', label: 'Structure', description: 'Building or constructed area' },
        { value: 'dungeon', label: 'Dungeon', description: 'Underground complex or ruins' },
        { value: 'wilderness', label: 'Wilderness', description: 'Natural outdoor area' }
    ];

    onMount(async () => {
        await loadTemplates();
        initializeFormData();
    });

    async function loadTemplates() {
        try {
            loading = true;
            templates = await locationAPI.getLocationTemplateFields(campaignId);
            if (location.type && templates[location.type]) {
                currentTemplate = templates[location.type];
            }
        } catch (err) {
            error = 'Failed to load location templates';
        } finally {
            loading = false;
        }
    }

    function initializeFormData() {
        // Initialize form data with existing location data
        Object.keys(location).forEach(key => {
            if (location[key] !== null && location[key] !== undefined) {
                formData[key] = location[key];
            }
        });

        // Ensure arrays are properly initialized
        if (currentTemplate) {
            Object.keys(currentTemplate).forEach(key => {
                const field = currentTemplate[key];
                if (field.type === 'tags' && !Array.isArray(formData[key])) {
                    formData[key] = formData[key] ? [formData[key]] : [];
                }
            });
        }
    }

    function selectType(type) {
        formData.type = type;
        currentTemplate = templates[type] || {};
        
        // Preserve existing data but ensure new fields are initialized
        Object.keys(currentTemplate).forEach(key => {
            if (!formData.hasOwnProperty(key) || formData[key] === null) {
                const field = currentTemplate[key];
                if (field.type === 'tags') {
                    formData[key] = [];
                } else if (field.type === 'demographics') {
                    formData[key] = {};
                } else {
                    formData[key] = '';
                }
            }
        });
    }

    function addTag(fieldName) {
        const input = document.getElementById(`${fieldName}_input`);
        if (input && input.value.trim()) {
            if (!formData[fieldName]) formData[fieldName] = [];
            formData[fieldName] = [...formData[fieldName], input.value.trim()];
            input.value = '';
        }
    }

    function removeTag(fieldName, index) {
        formData[fieldName] = formData[fieldName].filter((_, i) => i !== index);
    }

    function handleTagInputKeydown(event, fieldName) {
        if (event.key === 'Enter') {
            event.preventDefault();
            addTag(fieldName);
        }
    }

    async function handleSubmit() {
        if (!formData.name.trim()) {
            error = 'Name is required';
            return;
        }

        try {
            saving = true;
            error = '';
            
            // Clean up form data
            const submitData = { ...formData };
            
            // Convert empty strings to null for optional fields
            Object.keys(submitData).forEach(key => {
                if (submitData[key] === '' && !currentTemplate[key]?.required) {
                    submitData[key] = null;
                }
            });

            const updatedLocation = await locationAPI.updateLocation(campaignId, location.id, submitData);
            dispatch('updated', { location: updatedLocation });
        } catch (err) {
            error = err.message || 'Failed to update location';
        } finally {
            saving = false;
        }
    }

    function cancel() {
        dispatch('close');
    }

    function capitalizeWords(str) {
        if (!str) return '';
        return str.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    }
</script>

<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b border-gray-700">
            <h2 class="text-2xl font-semibold text-white">Edit Location</h2>
        </div>
        
        <div class="p-6">
            {#if error}
                <div class="bg-red-900 border border-red-700 text-red-100 px-4 py-3 rounded mb-6">
                    {error}
                </div>
            {/if}

            {#if loading}
                <div class="text-center py-8">
                    <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-red-600"></div>
                    <p class="text-gray-400 mt-2">Loading templates...</p>
                </div>
            {:else}
                <form on:submit|preventDefault={handleSubmit} class="space-y-6">
                    <!-- Basic Information -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label class="block text-sm font-medium text-gray-300 mb-2">
                                Name <span class="text-red-400">*</span>
                            </label>
                            <input
                                type="text"
                                bind:value={formData.name}
                                class="input w-full"
                                placeholder="Location name"
                                required
                            />
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-300 mb-2">
                                Parent Location
                            </label>
                            <select bind:value={formData.parent_location_id} class="input w-full">
                                <option value={null}>None (Top Level)</option>
                                {#each availableParents.filter(p => p.id !== location.id) as parent}
                                    <option value={parent.id}>{parent.name} ({parent.type})</option>
                                {/each}
                            </select>
                        </div>
                    </div>

                    <!-- Location Type Selection -->
                    <div>
                        <label class="block text-sm font-medium text-gray-300 mb-3">
                            Location Type <span class="text-red-400">*</span>
                        </label>
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                            {#each locationTypes as type}
                                <button
                                    type="button"
                                    on:click={() => selectType(type.value)}
                                    class="p-4 rounded-lg border-2 text-left transition-colors {
                                        formData.type === type.value 
                                            ? 'border-red-500 bg-red-900 bg-opacity-20' 
                                            : 'border-gray-600 bg-gray-700 hover:border-gray-500'
                                    }"
                                >
                                    <div class="font-medium text-white">{type.label}</div>
                                    <div class="text-sm text-gray-400 mt-1">{type.description}</div>
                                </button>
                            {/each}
                        </div>
                    </div>

                    <!-- Dynamic Fields Based on Type -->
                    {#if formData.type && currentTemplate}
                        <div class="border-t border-gray-700 pt-6">
                            <h3 class="text-lg font-medium text-white mb-4">
                                {locationTypes.find(t => t.value === formData.type)?.label} Details
                            </h3>
                            
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {#each Object.entries(currentTemplate) as [fieldName, fieldConfig]}
                                    {#if fieldName !== 'name'} <!-- Skip name since it's handled above -->
                                        <div class="{fieldConfig.type === 'textarea' || fieldConfig.type === 'tags' ? 'md:col-span-2' : ''}">
                                            <label class="block text-sm font-medium text-gray-300 mb-2">
                                                {fieldConfig.label}
                                                {#if fieldConfig.required}
                                                    <span class="text-red-400">*</span>
                                                {/if}
                                            </label>
                                            
                                            {#if fieldConfig.type === 'text'}
                                                <input
                                                    type="text"
                                                    bind:value={formData[fieldName]}
                                                    class="input w-full"
                                                    placeholder={fieldConfig.label}
                                                    required={fieldConfig.required}
                                                />
                                            {:else if fieldConfig.type === 'number'}
                                                <input
                                                    type="number"
                                                    bind:value={formData[fieldName]}
                                                    class="input w-full"
                                                    placeholder={fieldConfig.label}
                                                    required={fieldConfig.required}
                                                />
                                            {:else if fieldConfig.type === 'textarea'}
                                                <textarea
                                                    bind:value={formData[fieldName]}
                                                    rows="3"
                                                    class="input w-full resize-y"
                                                    placeholder={fieldConfig.label + "..."}
                                                    required={fieldConfig.required}
                                                ></textarea>
                                            {:else if fieldConfig.type === 'select'}
                                                <select bind:value={formData[fieldName]} class="input w-full" required={fieldConfig.required}>
                                                    <option value="">Select {fieldConfig.label}...</option>
                                                    {#each fieldConfig.options as option}
                                                        <option value={option}>{capitalizeWords(option)}</option>
                                                    {/each}
                                                </select>
                                            {:else if fieldConfig.type === 'tags'}
                                                <div>
                                                    <div class="flex mb-2">
                                                        <input
                                                            type="text"
                                                            id="{fieldName}_input"
                                                            class="input flex-1 mr-2"
                                                            placeholder="Add {fieldConfig.label.toLowerCase()}"
                                                            on:keydown={(e) => handleTagInputKeydown(e, fieldName)}
                                                        />
                                                        <button
                                                            type="button"
                                                            on:click={() => addTag(fieldName)}
                                                            class="btn btn-secondary"
                                                        >
                                                            Add
                                                        </button>
                                                    </div>
                                                    {#if formData[fieldName] && formData[fieldName].length > 0}
                                                        <div class="flex flex-wrap gap-2">
                                                            {#each formData[fieldName] as tag, index}
                                                                <span class="inline-flex items-center px-3 py-1 rounded-full text-xs bg-gray-600 text-gray-300">
                                                                    {tag}
                                                                    <button
                                                                        type="button"
                                                                        on:click={() => removeTag(fieldName, index)}
                                                                        class="ml-2 text-red-400 hover:text-red-300"
                                                                    >
                                                                        ×
                                                                    </button>
                                                                </span>
                                                            {/each}
                                                        </div>
                                                    {/if}
                                                </div>
                                            {/if}
                                        </div>
                                    {/if}
                                {/each}
                            </div>
                        </div>
                    {/if}

                    <!-- Meta Fields -->
                    <div class="border-t border-gray-700 pt-6">
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label class="block text-sm font-medium text-gray-300 mb-2">Status</label>
                                <select bind:value={formData.status} class="input w-full">
                                    <option value="draft">Draft</option>
                                    <option value="active">Active</option>
                                    <option value="historical">Historical</option>
                                    <option value="destroyed">Destroyed</option>
                                </select>
                            </div>

                            <div>
                                <label class="block text-sm font-medium text-gray-300 mb-2">Visibility</label>
                                <select bind:value={formData.visibility} class="input w-full">
                                    <option value="dm_only">DM Only</option>
                                    <option value="partially_known">Partially Known</option>
                                    <option value="player_known">Known to Players</option>
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
            {/if}
        </div>
    </div>
</div>