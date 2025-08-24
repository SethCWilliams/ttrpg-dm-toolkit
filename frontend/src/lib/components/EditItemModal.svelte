<script>
    import { createEventDispatcher, onMount } from 'svelte';
    import { itemAPI, npcAPI, locationAPI } from '$lib/api.js';

    export let campaignId;
    export let item;
    
    const dispatch = createEventDispatcher();

    let loading = false;
    let saving = false;
    let error = '';
    let templates = {};
    let currentTemplate = {};
    let availableNPCs = [];
    let availableLocations = [];
    let formData = {
        name: item.name || '',
        type: item.type || '',
        rarity: item.rarity || 'common',
        description: item.description || '',
        mechanical_effects: item.mechanical_effects || null,
        history: item.history || '',
        current_owner_id: item.current_owner_id,
        current_location_id: item.current_location_id,
        value: item.value,
        weight: item.weight,
        attunement_required: item.attunement_required || false,
        status: item.status || 'draft',
        visibility: item.visibility || 'dm_only',
        notes: item.notes || ''
    };

    const itemTypes = [
        { value: 'weapon', label: 'Weapon', description: 'Combat weapons and tools' },
        { value: 'armor', label: 'Armor', description: 'Protective gear and shields' },
        { value: 'tool', label: 'Tool', description: 'Utility items and instruments' },
        { value: 'treasure', label: 'Treasure', description: 'Valuable items and currency' },
        { value: 'consumable', label: 'Consumable', description: 'Potions, scrolls, and temporary items' },
        { value: 'quest_item', label: 'Quest Item', description: 'Story-important objects' },
        { value: 'artifact', label: 'Artifact', description: 'Legendary and magical artifacts' }
    ];

    const rarityOptions = [
        { value: 'common', label: 'Common', color: 'text-gray-400' },
        { value: 'uncommon', label: 'Uncommon', color: 'text-green-400' },
        { value: 'rare', label: 'Rare', color: 'text-blue-400' },
        { value: 'very_rare', label: 'Very Rare', color: 'text-purple-400' },
        { value: 'legendary', label: 'Legendary', color: 'text-orange-400' },
        { value: 'artifact', label: 'Artifact', color: 'text-red-400' }
    ];

    onMount(async () => {
        await Promise.all([
            loadTemplates(),
            loadAvailableNPCs(),
            loadAvailableLocations()
        ]);
        
        // Load current template and populate mechanical effects
        if (formData.type) {
            currentTemplate = templates[formData.type] || {};
            if (item.mechanical_effects) {
                Object.keys(item.mechanical_effects).forEach(key => {
                    formData[key] = item.mechanical_effects[key];
                });
            }
        }
    });

    async function loadTemplates() {
        try {
            loading = true;
            templates = await itemAPI.getItemTemplateFields();
        } catch (err) {
            error = 'Failed to load item templates';
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

    function selectType(type) {
        formData.type = type;
        currentTemplate = templates[type] || {};
        
        // Initialize template fields
        Object.keys(currentTemplate).forEach(key => {
            if (!formData.hasOwnProperty(key)) {
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

    async function handleSubmit() {
        if (!formData.name.trim()) {
            error = 'Item name is required';
            return;
        }

        if (!formData.type) {
            error = 'Item type is required';
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

            // Parse numeric fields
            if (submitData.value !== null && submitData.value !== '') {
                submitData.value = parseInt(submitData.value);
            }
            if (submitData.weight !== null && submitData.weight !== '') {
                submitData.weight = parseInt(submitData.weight);
            }

            // Build mechanical_effects from template fields
            const mechanicalEffects = {};
            Object.keys(currentTemplate).forEach(key => {
                if (formData[key] !== null && formData[key] !== '' && formData[key] !== undefined) {
                    mechanicalEffects[key] = formData[key];
                }
            });
            
            if (Object.keys(mechanicalEffects).length > 0) {
                submitData.mechanical_effects = mechanicalEffects;
            } else {
                submitData.mechanical_effects = null;
            }

            // Remove template fields from root level
            Object.keys(currentTemplate).forEach(key => {
                delete submitData[key];
            });

            const updatedItem = await itemAPI.updateItem(campaignId, item.id, submitData);
            dispatch('updated', { item: updatedItem });
        } catch (err) {
            error = err.message || 'Failed to update item';
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

    function getRarityColor(rarity) {
        const rarityOption = rarityOptions.find(r => r.value === rarity);
        return rarityOption ? rarityOption.color : 'text-gray-400';
    }
</script>

<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b border-gray-700">
            <h2 class="text-2xl font-semibold text-white">Edit Item</h2>
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
                                Item Name <span class="text-red-400">*</span>
                            </label>
                            <input
                                type="text"
                                bind:value={formData.name}
                                class="input w-full"
                                placeholder="Enter item name"
                                required
                            />
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-300 mb-2">
                                Rarity
                            </label>
                            <select bind:value={formData.rarity} class="input w-full">
                                {#each rarityOptions as rarity}
                                    <option value={rarity.value} class={rarity.color}>
                                        {rarity.label}
                                    </option>
                                {/each}
                            </select>
                        </div>

                        <div class="md:col-span-2">
                            <label class="block text-sm font-medium text-gray-300 mb-2">
                                Description
                            </label>
                            <textarea
                                bind:value={formData.description}
                                rows="3"
                                class="input w-full resize-y"
                                placeholder="Describe the item's appearance and basic properties..."
                            ></textarea>
                        </div>
                    </div>

                    <!-- Item Type Selection -->
                    <div>
                        <label class="block text-sm font-medium text-gray-300 mb-3">
                            Item Type <span class="text-red-400">*</span>
                        </label>
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                            {#each itemTypes as type}
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

                    <!-- Value and Weight -->
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div>
                            <label class="block text-sm font-medium text-gray-300 mb-2">
                                Value (gold pieces)
                            </label>
                            <input
                                type="number"
                                bind:value={formData.value}
                                min="0"
                                class="input w-full"
                                placeholder="0"
                            />
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-300 mb-2">
                                Weight (pounds)
                            </label>
                            <input
                                type="number"
                                bind:value={formData.weight}
                                min="0"
                                step="0.1"
                                class="input w-full"
                                placeholder="0"
                            />
                        </div>

                        <div class="flex items-center">
                            <label class="flex items-center">
                                <input
                                    type="checkbox"
                                    bind:checked={formData.attunement_required}
                                    class="mr-2"
                                />
                                <span class="text-sm text-gray-300">Requires Attunement</span>
                            </label>
                        </div>
                    </div>

                    <!-- Ownership -->
                    <div class="border-t border-gray-700 pt-6">
                        <h3 class="text-lg font-medium text-white mb-4">Ownership & Location</h3>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label class="block text-sm font-medium text-gray-300 mb-2">
                                    Current Owner
                                </label>
                                <select bind:value={formData.current_owner_id} class="input w-full">
                                    <option value={null}>No owner</option>
                                    {#each availableNPCs as npc}
                                        <option value={npc.id}>
                                            {npc.name} {npc.occupation ? `(${npc.occupation})` : ''}
                                        </option>
                                    {/each}
                                </select>
                            </div>

                            <div>
                                <label class="block text-sm font-medium text-gray-300 mb-2">
                                    Current Location
                                </label>
                                <select bind:value={formData.current_location_id} class="input w-full">
                                    <option value={null}>No location</option>
                                    {#each availableLocations as location}
                                        <option value={location.id}>
                                            {location.name} ({location.type})
                                        </option>
                                    {/each}
                                </select>
                            </div>
                        </div>
                    </div>

                    <!-- Dynamic Fields Based on Type -->
                    {#if formData.type && currentTemplate && Object.keys(currentTemplate).length > 0}
                        <div class="border-t border-gray-700 pt-6">
                            <h3 class="text-lg font-medium text-white mb-4">
                                {itemTypes.find(t => t.value === formData.type)?.label} Properties
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
                                <label class="block text-sm font-medium text-gray-300 mb-2">History</label>
                                <textarea
                                    bind:value={formData.history}
                                    rows="3"
                                    class="input w-full resize-y"
                                    placeholder="Describe the item's origin, previous owners, and significance..."
                                ></textarea>
                            </div>

                            <div>
                                <label class="block text-sm font-medium text-gray-300 mb-2">Notes</label>
                                <textarea
                                    bind:value={formData.notes}
                                    rows="3"
                                    class="input w-full resize-y"
                                    placeholder="Additional notes and DM information..."
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
                                    <option value="active">Active</option>
                                    <option value="lost">Lost</option>
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