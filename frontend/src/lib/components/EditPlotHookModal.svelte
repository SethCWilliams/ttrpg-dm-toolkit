<script>
    import { createEventDispatcher, onMount } from 'svelte';
    import { plotHookAPI, npcAPI, locationAPI, organizationAPI } from '$lib/api.js';

    export let campaignId;
    export let plotHook;
    
    const dispatch = createEventDispatcher();

    let loading = false;
    let saving = false;
    let error = '';
    let templates = {};
    let currentTemplate = {};
    let availableNPCs = [];
    let availableLocations = [];
    let availableOrganizations = [];
    let formData = {
        title: plotHook.title || '',
        description: plotHook.description || '',
        hook_type: plotHook.hook_type || '',
        urgency: plotHook.urgency || 'moderate',
        complexity: plotHook.complexity || 'moderate',
        related_npcs: plotHook.related_npcs || [],
        related_locations: plotHook.related_locations || [],
        related_organizations: plotHook.related_organizations || [],
        prerequisites: plotHook.prerequisites || [],
        rewards: plotHook.rewards || null,
        consequences: plotHook.consequences || null,
        status: plotHook.status || 'draft',
        visibility: plotHook.visibility || 'dm_only',
        notes: plotHook.notes || ''
    };

    const hookTypes = [
        { value: 'main_quest', label: 'Main Quest', description: 'Primary storyline adventure' },
        { value: 'side_quest', label: 'Side Quest', description: 'Optional adventure content' },
        { value: 'personal', label: 'Personal', description: 'Character-specific storyline' },
        { value: 'political', label: 'Political', description: 'Involving factions and politics' },
        { value: 'mystery', label: 'Mystery', description: 'Investigation and puzzle-solving' },
        { value: 'combat', label: 'Combat', description: 'Action and battle-focused' },
        { value: 'social', label: 'Social', description: 'Roleplay and interaction-focused' }
    ];

    const urgencyLevels = [
        { value: 'immediate', label: 'Immediate', description: 'Must be addressed right now' },
        { value: 'urgent', label: 'Urgent', description: 'Should be addressed soon' },
        { value: 'moderate', label: 'Moderate', description: 'Can wait but shouldn\'t be ignored' },
        { value: 'background', label: 'Background', description: 'Long-term or ongoing concern' }
    ];

    const complexityLevels = [
        { value: 'simple', label: 'Simple', description: 'Single session, straightforward' },
        { value: 'moderate', label: 'Moderate', description: 'Few sessions, some complexity' },
        { value: 'complex', label: 'Complex', description: 'Multi-session, intricate plot' },
        { value: 'epic', label: 'Epic', description: 'Campaign-spanning, major storyline' }
    ];

    onMount(async () => {
        await Promise.all([
            loadTemplates(),
            loadAvailableNPCs(),
            loadAvailableLocations(),
            loadAvailableOrganizations()
        ]);
        initializeFormData();
    });

    async function loadTemplates() {
        try {
            loading = true;
            templates = await plotHookAPI.getPlotHookTemplateFields();
            if (formData.hook_type && templates[formData.hook_type]) {
                currentTemplate = templates[formData.hook_type];
            }
        } catch (err) {
            error = 'Failed to load plot hook templates';
        } finally {
            loading = false;
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

    async function loadAvailableLocations() {
        try {
            const response = await locationAPI.getLocations(campaignId, { limit: 100 });
            availableLocations = response.items || [];
        } catch (err) {
            console.error('Failed to load locations:', err);
        }
    }

    async function loadAvailableOrganizations() {
        try {
            const response = await organizationAPI.getOrganizations(campaignId, { limit: 100 });
            availableOrganizations = response.items || [];
        } catch (err) {
            console.error('Failed to load organizations:', err);
        }
    }

    function initializeFormData() {
        // Initialize form data with existing plot hook data
        Object.keys(plotHook).forEach(key => {
            if (plotHook[key] !== null && plotHook[key] !== undefined) {
                formData[key] = plotHook[key];
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
        formData.hook_type = type;
        currentTemplate = templates[type] || {};
        
        // Preserve existing data but ensure new fields are initialized
        Object.keys(currentTemplate).forEach(key => {
            if (!formData.hasOwnProperty(key) || formData[key] === null) {
                const field = currentTemplate[key];
                if (field.type === 'tags') {
                    formData[key] = [];
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

    function handleRelatedEntityChange(event, type) {
        const entityId = parseInt(event.target.value);
        if (!entityId) return;

        if (type === 'npc') {
            if (!formData.related_npcs.includes(entityId)) {
                formData.related_npcs = [...formData.related_npcs, entityId];
            }
        } else if (type === 'location') {
            if (!formData.related_locations.includes(entityId)) {
                formData.related_locations = [...formData.related_locations, entityId];
            }
        } else if (type === 'organization') {
            if (!formData.related_organizations.includes(entityId)) {
                formData.related_organizations = [...formData.related_organizations, entityId];
            }
        }
        event.target.value = '';
    }

    function removeRelatedEntity(entityId, type) {
        if (type === 'npc') {
            formData.related_npcs = formData.related_npcs.filter(id => id !== entityId);
        } else if (type === 'location') {
            formData.related_locations = formData.related_locations.filter(id => id !== entityId);
        } else if (type === 'organization') {
            formData.related_organizations = formData.related_organizations.filter(id => id !== entityId);
        }
    }

    function getEntityName(entityId, type) {
        if (type === 'npc') {
            const npc = availableNPCs.find(n => n.id === entityId);
            return npc ? `${npc.name} ${npc.occupation ? `(${npc.occupation})` : ''}` : `NPC #${entityId}`;
        } else if (type === 'location') {
            const location = availableLocations.find(l => l.id === entityId);
            return location ? `${location.name} (${location.type})` : `Location #${entityId}`;
        } else if (type === 'organization') {
            const org = availableOrganizations.find(o => o.id === entityId);
            return org ? `${org.name} (${org.type})` : `Organization #${entityId}`;
        }
        return `Unknown #${entityId}`;
    }

    async function handleSubmit() {
        if (!formData.title.trim()) {
            error = 'Plot hook title is required';
            return;
        }

        if (!formData.hook_type) {
            error = 'Plot hook type is required';
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

            const updatedPlotHook = await plotHookAPI.updatePlotHook(campaignId, plotHook.id, submitData);
            dispatch('updated', { plotHook: updatedPlotHook });
        } catch (err) {
            error = err.message || 'Failed to update plot hook';
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
            <h2 class="text-2xl font-semibold text-white">Edit Plot Hook</h2>
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
                        <div class="md:col-span-2">
                            <label class="block text-sm font-medium text-gray-300 mb-2">
                                Plot Hook Title <span class="text-red-400">*</span>
                            </label>
                            <input
                                type="text"
                                bind:value={formData.title}
                                class="input w-full"
                                placeholder="Enter plot hook title"
                                required
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
                                placeholder="Describe the plot hook, its context, and potential developments..."
                            ></textarea>
                        </div>
                    </div>

                    <!-- Hook Type Selection -->
                    <div>
                        <label class="block text-sm font-medium text-gray-300 mb-3">
                            Hook Type <span class="text-red-400">*</span>
                        </label>
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                            {#each hookTypes as type}
                                <button
                                    type="button"
                                    on:click={() => selectType(type.value)}
                                    class="p-4 rounded-lg border-2 text-left transition-colors {
                                        formData.hook_type === type.value 
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

                    <!-- Urgency and Complexity -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label class="block text-sm font-medium text-gray-300 mb-2">
                                Urgency Level
                            </label>
                            <select bind:value={formData.urgency} class="input w-full">
                                {#each urgencyLevels as level}
                                    <option value={level.value}>{level.label} - {level.description}</option>
                                {/each}
                            </select>
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-300 mb-2">
                                Complexity Level
                            </label>
                            <select bind:value={formData.complexity} class="input w-full">
                                {#each complexityLevels as level}
                                    <option value={level.value}>{level.label} - {level.description}</option>
                                {/each}
                            </select>
                        </div>
                    </div>

                    <!-- Related Entities -->
                    <div class="border-t border-gray-700 pt-6">
                        <h3 class="text-lg font-medium text-white mb-4">Related Elements</h3>
                        
                        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                            <!-- Related NPCs -->
                            <div>
                                <label class="block text-sm font-medium text-gray-300 mb-2">
                                    Related NPCs
                                </label>
                                <div class="space-y-3">
                                    <div class="flex space-x-2">
                                        <select
                                            on:change={(e) => handleRelatedEntityChange(e, 'npc')}
                                            class="input flex-1"
                                        >
                                            <option value="">Add an NPC...</option>
                                            {#each availableNPCs.filter(npc => !formData.related_npcs.includes(npc.id)) as npc}
                                                <option value={npc.id}>
                                                    {npc.name} {npc.occupation ? `(${npc.occupation})` : ''}
                                                </option>
                                            {/each}
                                        </select>
                                    </div>
                                    {#if formData.related_npcs.length > 0}
                                        <div class="space-y-2">
                                            {#each formData.related_npcs as npcId}
                                                <div class="flex items-center justify-between p-2 bg-gray-700 rounded">
                                                    <span class="text-sm text-white">{getEntityName(npcId, 'npc')}</span>
                                                    <button
                                                        type="button"
                                                        on:click={() => removeRelatedEntity(npcId, 'npc')}
                                                        class="text-red-400 hover:text-red-300 text-sm"
                                                    >
                                                        Remove
                                                    </button>
                                                </div>
                                            {/each}
                                        </div>
                                    {/if}
                                </div>
                            </div>

                            <!-- Related Locations -->
                            <div>
                                <label class="block text-sm font-medium text-gray-300 mb-2">
                                    Related Locations
                                </label>
                                <div class="space-y-3">
                                    <div class="flex space-x-2">
                                        <select
                                            on:change={(e) => handleRelatedEntityChange(e, 'location')}
                                            class="input flex-1"
                                        >
                                            <option value="">Add a location...</option>
                                            {#each availableLocations.filter(location => !formData.related_locations.includes(location.id)) as location}
                                                <option value={location.id}>
                                                    {location.name} ({location.type})
                                                </option>
                                            {/each}
                                        </select>
                                    </div>
                                    {#if formData.related_locations.length > 0}
                                        <div class="space-y-2">
                                            {#each formData.related_locations as locationId}
                                                <div class="flex items-center justify-between p-2 bg-gray-700 rounded">
                                                    <span class="text-sm text-white">{getEntityName(locationId, 'location')}</span>
                                                    <button
                                                        type="button"
                                                        on:click={() => removeRelatedEntity(locationId, 'location')}
                                                        class="text-red-400 hover:text-red-300 text-sm"
                                                    >
                                                        Remove
                                                    </button>
                                                </div>
                                            {/each}
                                        </div>
                                    {/if}
                                </div>
                            </div>

                            <!-- Related Organizations -->
                            <div>
                                <label class="block text-sm font-medium text-gray-300 mb-2">
                                    Related Organizations
                                </label>
                                <div class="space-y-3">
                                    <div class="flex space-x-2">
                                        <select
                                            on:change={(e) => handleRelatedEntityChange(e, 'organization')}
                                            class="input flex-1"
                                        >
                                            <option value="">Add an organization...</option>
                                            {#each availableOrganizations.filter(org => !formData.related_organizations.includes(org.id)) as org}
                                                <option value={org.id}>
                                                    {org.name} ({org.type})
                                                </option>
                                            {/each}
                                        </select>
                                    </div>
                                    {#if formData.related_organizations.length > 0}
                                        <div class="space-y-2">
                                            {#each formData.related_organizations as orgId}
                                                <div class="flex items-center justify-between p-2 bg-gray-700 rounded">
                                                    <span class="text-sm text-white">{getEntityName(orgId, 'organization')}</span>
                                                    <button
                                                        type="button"
                                                        on:click={() => removeRelatedEntity(orgId, 'organization')}
                                                        class="text-red-400 hover:text-red-300 text-sm"
                                                    >
                                                        Remove
                                                    </button>
                                                </div>
                                            {/each}
                                        </div>
                                    {/if}
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Dynamic Fields Based on Type -->
                    {#if formData.hook_type && currentTemplate && Object.keys(currentTemplate).length > 0}
                        <div class="border-t border-gray-700 pt-6">
                            <h3 class="text-lg font-medium text-white mb-4">
                                {hookTypes.find(t => t.value === formData.hook_type)?.label} Details
                            </h3>
                            
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {#each Object.entries(currentTemplate) as [fieldName, fieldConfig]}
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
                                {/each}
                            </div>
                        </div>
                    {/if}

                    <!-- Additional Fields -->
                    <div class="border-t border-gray-700 pt-6">
                        <div class="space-y-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-300 mb-2">Notes</label>
                                <textarea
                                    bind:value={formData.notes}
                                    rows="3"
                                    class="input w-full resize-y"
                                    placeholder="Additional notes, reminders, or DM considerations..."
                                ></textarea>
                            </div>
                        </div>
                    </div>

                    <!-- Meta Fields -->
                    <div class="border-t border-gray-700 pt-6">
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label class="block text-sm font-medium text-gray-300 mb-2">Status</label>
                                <select bind:value={formData.status} class="input w-full">
                                    <option value="draft">Draft</option>
                                    <option value="available">Available</option>
                                    <option value="active">Active</option>
                                    <option value="completed">Completed</option>
                                    <option value="failed">Failed</option>
                                    <option value="abandoned">Abandoned</option>
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