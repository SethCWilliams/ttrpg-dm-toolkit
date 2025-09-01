<script>
    import { createEventDispatcher, onMount } from 'svelte';
    import { locationAPI, aiAPI } from '$lib/api.js';
    import FieldLockButton from './FieldLockButton.svelte';

    export let campaignId;
    export let availableParents = [];

    const dispatch = createEventDispatcher();

    let loading = false;
    let saving = false;
    let generatingAI = false;
    let error = '';
    let templates = {};
    let selectedType = '';
    let currentTemplate = {};
    let formData = {
        name: '',
        type: '',
        parent_location_id: null,
        status: 'draft',
        visibility: 'dm_only'
    };

    // Field locking for AI generation
    let lockedFields = {
        // Common fields
        name: false,
        description: false,
        history: false,
        notable_features: false,
        ambient_description: false,
        
        // Settlement fields
        population: false,
        demographics: false,
        government_type: false,
        economic_status: false,
        defenses: false,
        trade_goods: false,
        
        // Structure fields  
        structure_type: false,
        owner: false,
        services: false,
        security: false,
        
        // Dungeon fields
        dungeon_type: false,
        difficulty: false,
        treasures: false,
        
        // Wilderness fields
        terrain_type: false,
        climate: false,
        dangers: false,
        wildlife: false,
        resources: false,
        
        // Region fields
        natural_resources: false
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
    });

    async function loadTemplates() {
        try {
            loading = true;
            templates = await locationAPI.getLocationTemplateFields(campaignId);
        } catch (err) {
            error = 'Failed to load location templates';
        } finally {
            loading = false;
        }
    }

    function selectType(type) {
        selectedType = type;
        formData.type = type;
        currentTemplate = templates[type] || {};
        
        // Reset dynamic fields when changing type
        Object.keys(formData).forEach(key => {
            if (!['name', 'type', 'parent_location_id', 'status', 'visibility'].includes(key)) {
                delete formData[key];
            }
        });
        
        // Initialize dynamic fields with default values
        Object.keys(currentTemplate).forEach(key => {
            if (!formData.hasOwnProperty(key)) {
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

        if (!selectedType) {
            error = 'Please select a location type';
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

            const newLocation = await locationAPI.createLocation(campaignId, submitData);
            dispatch('created', { location: newLocation });
        } catch (err) {
            error = err.message || 'Failed to create location';
        } finally {
            saving = false;
        }
    }

    function cancel() {
        dispatch('close');
    }

    function toggleFieldLock(fieldName) {
        lockedFields[fieldName] = !lockedFields[fieldName];
    }

    async function generateRandomLocation() {
        if (!selectedType) {
            error = 'Please select a location type first';
            return;
        }

        try {
            generatingAI = true;
            error = '';
            
            // Build locked data from current form values
            const lockedData = {};
            
            // Iterate through all locked fields dynamically
            Object.keys(lockedFields).forEach(fieldName => {
                if (lockedFields[fieldName] && formData[fieldName] != null && formData[fieldName] !== '') {
                    // Handle different field types appropriately
                    if (typeof formData[fieldName] === 'string') {
                        lockedData[fieldName] = formData[fieldName].trim();
                    } else {
                        lockedData[fieldName] = formData[fieldName];
                    }
                }
            });
            
            const response = await aiAPI.generateLocation(campaignId, selectedType, lockedData);
            
            if (response.success && response.location) {
                // Update only unlocked fields with AI-generated data
                // Common fields for all types
                if (!lockedFields.name) formData.name = response.location.name || '';
                if (!lockedFields.description) formData.description = response.location.description || '';
                if (!lockedFields.history) formData.history = response.location.history || '';
                if (!lockedFields.notable_features) formData.notable_features = response.location.notable_features || '';
                
                // Type-specific field mappings
                if (selectedType === 'structure') {
                    if (!lockedFields.structure_type) formData.structure_type = response.location.structure_type || '';
                    if (!lockedFields.owner) formData.owner = response.location.owner || '';
                    if (!lockedFields.services) formData.services = response.location.services || '';
                    if (!lockedFields.security) formData.security = response.location.security || '';
                    if (!lockedFields.ambient_description) formData.ambient_description = response.location.ambient_description || '';
                } else if (selectedType === 'settlement') {
                    if (!lockedFields.population) formData.population = response.location.population || 0;
                    if (!lockedFields.demographics) formData.demographics = response.location.demographics || '';
                    if (!lockedFields.government_type) formData.government_type = response.location.government_type || '';
                    if (!lockedFields.economic_status) formData.economic_status = response.location.economic_status || '';
                    if (!lockedFields.defenses) formData.defenses = response.location.defenses || '';
                    if (!lockedFields.trade_goods) formData.trade_goods = response.location.trade_goods || '';
                } else if (selectedType === 'dungeon') {
                    if (!lockedFields.dungeon_type) formData.dungeon_type = response.location.dungeon_type || '';
                    if (!lockedFields.difficulty) formData.difficulty = response.location.difficulty || '';
                    if (!lockedFields.defenses) formData.defenses = response.location.defenses || '';
                    if (!lockedFields.treasures) formData.treasures = response.location.treasures || '';
                    if (!lockedFields.ambient_description) formData.ambient_description = response.location.ambient_description || '';
                } else if (selectedType === 'wilderness') {
                    if (!lockedFields.terrain_type) formData.terrain_type = response.location.terrain_type || '';
                    if (!lockedFields.climate) formData.climate = response.location.climate || '';
                    if (!lockedFields.dangers) formData.dangers = response.location.dangers || '';
                    if (!lockedFields.resources) formData.resources = response.location.resources || '';
                    if (!lockedFields.wildlife) formData.wildlife = response.location.wildlife || '';
                    if (!lockedFields.ambient_description) formData.ambient_description = response.location.ambient_description || '';
                } else if (selectedType === 'region') {
                    if (!lockedFields.population) formData.population = response.location.population || 0;
                    if (!lockedFields.government_type) formData.government_type = response.location.government_type || '';
                    if (!lockedFields.economic_status) formData.economic_status = response.location.economic_status || '';
                    if (!lockedFields.climate) formData.climate = response.location.climate || '';
                    if (!lockedFields.natural_resources) formData.natural_resources = response.location.natural_resources || '';
                }
                
                if (response.warning) {
                    error = response.warning;
                }
            } else {
                throw new Error('Failed to generate location data');
            }
            
        } catch (err) {
            error = err.message || 'Failed to generate location. Please try again.';
        } finally {
            generatingAI = false;
        }
    }

</script>

<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b border-gray-700 flex justify-between items-center">
            <h2 class="text-2xl font-semibold text-white">Create New Location</h2>
            <button 
                type="button"
                on:click={generateRandomLocation}
                disabled={generatingAI || !selectedType}
                class="btn btn-secondary {generatingAI ? 'opacity-50' : ''}"
                title="Generate location details using AI"
            >
                {#if generatingAI}
                    Generating...
                {:else}
                    Randomize
                {/if}
            </button>
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
                            <label class="block text-sm font-medium text-gray-300 mb-2 flex items-center justify-between">
                                <span>Name <span class="text-red-400">*</span></span>
                                <FieldLockButton 
                                    isLocked={lockedFields.name} 
                                    fieldName="name"
                                    on:toggle={() => toggleFieldLock('name')} 
                                />
                            </label>
                            <input
                                type="text"
                                bind:value={formData.name}
                                class="input w-full {lockedFields.name ? 'border-yellow-400 bg-yellow-50 bg-opacity-10' : ''}"
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
                                {#each availableParents as parent}
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
                                        selectedType === type.value 
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
                    {#if selectedType && currentTemplate}
                        <div class="border-t border-gray-700 pt-6">
                            <h3 class="text-lg font-medium text-white mb-4">
                                {locationTypes.find(t => t.value === selectedType)?.label} Details
                            </h3>
                            
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {#each Object.entries(currentTemplate) as [fieldName, fieldConfig]}
                                    {#if fieldName !== 'name'} <!-- Skip name since it's handled above -->
                                        <div class="{fieldConfig.type === 'textarea' || fieldConfig.type === 'tags' ? 'md:col-span-2' : ''}">
                                            <label class="block text-sm font-medium text-gray-300 mb-2 flex items-center justify-between">
                                                <span>
                                                    {fieldConfig.label}
                                                    {#if fieldConfig.required}
                                                        <span class="text-red-400">*</span>
                                                    {/if}
                                                </span>
                                                {#if lockedFields.hasOwnProperty(fieldName)}
                                                    <FieldLockButton 
                                                        isLocked={lockedFields[fieldName]} 
                                                        fieldName={fieldName}
                                                        on:toggle={() => toggleFieldLock(fieldName)} 
                                                    />
                                                {/if}
                                            </label>
                                            
                                            {#if fieldConfig.type === 'text'}
                                                <input
                                                    type="text"
                                                    bind:value={formData[fieldName]}
                                                    class="input w-full {lockedFields[fieldName] ? 'border-yellow-400 bg-yellow-50 bg-opacity-10' : ''}"
                                                    placeholder={fieldConfig.label}
                                                    required={fieldConfig.required}
                                                />
                                            {:else if fieldConfig.type === 'number'}
                                                <input
                                                    type="number"
                                                    bind:value={formData[fieldName]}
                                                    class="input w-full {lockedFields[fieldName] ? 'border-yellow-400 bg-yellow-50 bg-opacity-10' : ''}"
                                                    placeholder={fieldConfig.label}
                                                    required={fieldConfig.required}
                                                />
                                            {:else if fieldConfig.type === 'textarea'}
                                                <textarea
                                                    bind:value={formData[fieldName]}
                                                    rows="3"
                                                    class="input w-full resize-y {lockedFields[fieldName] ? 'border-yellow-400 bg-yellow-50 bg-opacity-10' : ''}"
                                                    placeholder={fieldConfig.label + "..."}
                                                    required={fieldConfig.required}
                                                ></textarea>
                                            {:else if fieldConfig.type === 'select'}
                                                <select bind:value={formData[fieldName]} class="input w-full {lockedFields[fieldName] ? 'border-yellow-400 bg-yellow-50 bg-opacity-10' : ''}" required={fieldConfig.required}>
                                                    <option value="">Select {fieldConfig.label}...</option>
                                                    {#each fieldConfig.options as option}
                                                        <option value={option}>{option.replace('_', ' ')}</option>
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
                            disabled={saving || !selectedType}
                        >
                            {saving ? 'Creating...' : 'Create Location'}
                        </button>
                    </div>
                </form>
            {/if}
        </div>
    </div>
</div>