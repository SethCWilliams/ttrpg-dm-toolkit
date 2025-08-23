<script>
    import { createEventDispatcher, onMount } from 'svelte';
    import { npcAPI, locationAPI } from '$lib/api.js';

    export let campaignId;
    export let npcId;
    export let npcName = '';
    export let initialRelationships = [];

    const dispatch = createEventDispatcher();

    let relationships = [];
    let availableNPCs = [];
    let availableLocations = [];
    let loading = false;
    let saving = false;
    let error = '';

    // Form for adding new relationship
    let showAddForm = false;
    let newRelationship = {
        target_id: '',
        target_type: 'npc',
        relationship_type: '',
        description: '',
        strength: 'moderate',
        public_knowledge: false
    };

    const npcRelationshipTypes = [
        'family', 'friend', 'ally', 'romantic', 'mentor', 'student',
        'enemy', 'rival', 'employer', 'employee', 'neighbor', 'acquaintance',
        'business_partner', 'creditor', 'debtor', 'protector', 'protected',
        'blackmailer', 'victim', 'other'
    ];

    const locationRelationshipTypes = [
        'lives_in', 'works_at', 'owns', 'frequents', 'avoids', 'born_in',
        'exiled_from', 'wants_to_visit', 'has_history_with', 'protects',
        'seeks_to_destroy', 'hiding_in', 'imprisoned_in', 'rules', 'serves',
        'trades_with', 'studies_at', 'worships_at', 'performs_at', 'other'
    ];

    $: currentRelationshipTypes = newRelationship.target_type === 'location' 
        ? locationRelationshipTypes 
        : npcRelationshipTypes;

    const strengthLevels = [
        { value: 'weak', label: 'Weak' },
        { value: 'moderate', label: 'Moderate' },
        { value: 'strong', label: 'Strong' }
    ];

    onMount(async () => {
        relationships = [...initialRelationships];
        await loadAvailableNPCs();
        await loadAvailableLocations();
    });

    async function loadAvailableNPCs() {
        try {
            loading = true;
            const response = await npcAPI.getNPCs(campaignId, { limit: 100 });
            // Filter out the current NPC
            availableNPCs = (response.items || []).filter(npc => npc.id != npcId);
        } catch (err) {
            console.error('Failed to load NPCs:', err);
            error = `Failed to load available NPCs: ${err.message || err}`;
        } finally {
            loading = false;
        }
    }

    async function loadAvailableLocations() {
        try {
            const response = await locationAPI.getLocations(campaignId, { limit: 100 });
            availableLocations = response.items || [];
        } catch (err) {
            console.error('Failed to load locations:', err);
            error = `Failed to load available locations: ${err.message || err}`;
        }
    }

    function startAddRelationship() {
        newRelationship = {
            target_id: '',
            target_type: 'npc',
            relationship_type: '',
            description: '',
            strength: 'moderate',
            public_knowledge: false
        };
        showAddForm = true;
    }

    function cancelAddRelationship() {
        showAddForm = false;
        newRelationship = {
            target_id: '',
            target_type: 'npc',
            relationship_type: '',
            description: '',
            strength: 'moderate',
            public_knowledge: false
        };
    }

    function addRelationship() {
        if (!newRelationship.target_id || !newRelationship.relationship_type) {
            error = 'Target and relationship type are required';
            return;
        }

        let relationship = {
            ...newRelationship,
            target_id: parseInt(newRelationship.target_id)
        };

        if (newRelationship.target_type === 'npc') {
            const targetNPC = availableNPCs.find(npc => npc.id == newRelationship.target_id);
            relationship.target_name = targetNPC?.name;
            relationship.target_occupation = targetNPC?.occupation;
        } else if (newRelationship.target_type === 'location') {
            const targetLocation = availableLocations.find(loc => loc.id == newRelationship.target_id);
            relationship.target_name = targetLocation?.name;
            relationship.target_location_type = targetLocation?.type;
        }

        relationships = [...relationships, relationship];
        cancelAddRelationship();
        error = '';
    }

    async function removeRelationship(index) {
        if (confirm('Are you sure you want to remove this relationship?')) {
            relationships = relationships.filter((_, i) => i !== index);
            // Auto-save after removal
            await saveRelationships();
        }
    }

    function editRelationship(index) {
        const rel = relationships[index];
        newRelationship = { ...rel };
        showAddForm = true;
        // Remove the relationship being edited
        relationships = relationships.filter((_, i) => i !== index);
    }

    async function saveRelationships() {
        try {
            saving = true;
            error = '';
            await npcAPI.updateNPCRelationships(campaignId, npcId, relationships);
            dispatch('saved', { relationships });
        } catch (err) {
            error = err.message || 'Failed to save relationships';
        } finally {
            saving = false;
        }
    }

    function getRelationshipIcon(type, targetType) {
        if (targetType === 'location') {
            switch (type) {
                case 'lives_in': return '🏠';
                case 'works_at': return '💼';
                case 'owns': return '🏛️';
                case 'frequents': return '🚶';
                case 'avoids': return '🚫';
                case 'born_in': return '👶';
                case 'exiled_from': return '⛓️';
                case 'wants_to_visit': return '🎯';
                case 'has_history_with': return '📜';
                case 'protects': return '🛡️';
                case 'seeks_to_destroy': return '💥';
                case 'hiding_in': return '🕵️';
                case 'imprisoned_in': return '⛓️';
                case 'rules': return '👑';
                case 'serves': return '🤝';
                case 'trades_with': return '💰';
                case 'studies_at': return '📚';
                case 'worships_at': return '🙏';
                case 'performs_at': return '🎭';
                default: return '📍';
            }
        } else {
            switch (type) {
                case 'family': return '👨‍👩‍👧‍👦';
                case 'friend': return '🤝';
                case 'ally': return '🤜🤛';
                case 'romantic': return '💕';
                case 'mentor': return '👨‍🏫';
                case 'student': return '🎓';
                case 'enemy': return '⚔️';
                case 'rival': return '🥊';
                case 'employer': return '👔';
                case 'employee': return '👷';
                case 'business_partner': return '💼';
                case 'neighbor': return '🏠';
                default: return '👤';
            }
        }
    }

    function getStrengthColor(strength) {
        switch (strength) {
            case 'weak': return 'text-gray-400';
            case 'moderate': return 'text-yellow-400';
            case 'strong': return 'text-red-400';
            default: return 'text-gray-400';
        }
    }
</script>

<div class="space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold text-white">Relationships</h3>
        <button
            on:click={startAddRelationship}
            class="btn btn-primary text-sm"
            disabled={loading}
        >
            Add Relationship
        </button>
    </div>

    {#if error}
        <div class="bg-red-900 border border-red-700 text-red-100 px-4 py-3 rounded">
            {error}
        </div>
    {/if}

    <!-- Existing Relationships -->
    {#if relationships.length > 0}
        <div class="space-y-3">
            {#each relationships as relationship, index}
                <div class="card bg-gray-750 border-gray-600">
                    <div class="flex items-start justify-between">
                        <div class="flex items-start space-x-3 flex-1">
                            <div class="text-2xl">
                                {getRelationshipIcon(relationship.relationship_type, relationship.target_type)}
                            </div>
                            
                            <div class="flex-1">
                                <div class="flex items-center space-x-2 mb-1">
                                    <span class="font-medium text-white">
                                        {relationship.target_name || `ID: ${relationship.target_id}`}
                                    </span>
                                    <span class="text-sm text-gray-400">
                                        ({relationship.relationship_type})
                                    </span>
                                    <span class="text-xs {getStrengthColor(relationship.strength)} capitalize">
                                        {relationship.strength}
                                    </span>
                                    {#if relationship.public_knowledge}
                                        <span class="text-xs text-blue-400" title="Public Knowledge">👁️</span>
                                    {/if}
                                </div>
                                
                                {#if relationship.target_occupation}
                                    <div class="text-sm text-gray-500 mb-1">
                                        {relationship.target_occupation}
                                    </div>
                                {:else if relationship.target_location_type}
                                    <div class="text-sm text-gray-500 mb-1">
                                        {relationship.target_location_type.charAt(0).toUpperCase() + relationship.target_location_type.slice(1)}
                                    </div>
                                {/if}
                                
                                {#if relationship.description}
                                    <p class="text-sm text-gray-300">
                                        {relationship.description}
                                    </p>
                                {/if}
                            </div>
                        </div>
                        
                        <div class="flex items-center space-x-2">
                            <button
                                on:click={() => editRelationship(index)}
                                class="text-gray-400 hover:text-white text-sm"
                            >
                                Edit
                            </button>
                            <button
                                on:click={() => removeRelationship(index)}
                                class="text-red-400 hover:text-red-300 text-sm"
                            >
                                Remove
                            </button>
                        </div>
                    </div>
                </div>
            {/each}
        </div>
    {:else if !loading}
        <div class="text-center py-8 text-gray-500">
            <div class="text-4xl mb-2">👥</div>
            <p>No relationships yet</p>
            <p class="text-sm">Add relationships to build connections between characters</p>
        </div>
    {/if}

    <!-- Add Relationship Form -->
    {#if showAddForm}
        <div class="card bg-gray-750 border-gray-600">
            <h4 class="font-medium text-white mb-4">Add New Relationship</h4>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- Target Type Selection -->
                <div>
                    <label class="block text-sm font-medium text-gray-300 mb-2">
                        Relationship With <span class="text-red-400">*</span>
                    </label>
                    <select
                        bind:value={newRelationship.target_type}
                        class="input w-full"
                        on:change={() => { newRelationship.target_id = ''; newRelationship.relationship_type = ''; }}
                    >
                        <option value="npc">NPC</option>
                        <option value="location">Location</option>
                    </select>
                </div>

                <!-- Target Selection -->
                <div>
                    <label class="block text-sm font-medium text-gray-300 mb-2">
                        Select {newRelationship.target_type === 'location' ? 'Location' : 'NPC'} <span class="text-red-400">*</span>
                    </label>
                    <select
                        bind:value={newRelationship.target_id}
                        class="input w-full"
                        required
                    >
                        {#if newRelationship.target_type === 'location'}
                            <option value="">Select a location...</option>
                            {#each availableLocations as location}
                                <option value={location.id}>
                                    {location.name} ({location.type})
                                </option>
                            {/each}
                        {:else}
                            <option value="">Select an NPC...</option>
                            {#each availableNPCs as npc}
                                <option value={npc.id}>
                                    {npc.name} {npc.occupation ? `(${npc.occupation})` : ''}
                                </option>
                            {/each}
                        {/if}
                    </select>
                </div>

                <!-- Relationship Type -->
                <div>
                    <label class="block text-sm font-medium text-gray-300 mb-2">
                        Relationship Type <span class="text-red-400">*</span>
                    </label>
                    <select
                        bind:value={newRelationship.relationship_type}
                        class="input w-full"
                        required
                    >
                        <option value="">Select type...</option>
                        {#each currentRelationshipTypes as type}
                            <option value={type}>{type.replace(/_/g, ' ')}</option>
                        {/each}
                    </select>
                </div>

                <div>
                    <label class="block text-sm font-medium text-gray-300 mb-2">
                        Strength
                    </label>
                    <select
                        bind:value={newRelationship.strength}
                        class="input w-full"
                    >
                        {#each strengthLevels as level}
                            <option value={level.value}>{level.label}</option>
                        {/each}
                    </select>
                </div>

                <div class="flex items-center">
                    <label class="flex items-center space-x-2 text-sm text-gray-300">
                        <input
                            type="checkbox"
                            bind:checked={newRelationship.public_knowledge}
                            class="rounded border-gray-600 bg-gray-700 text-red-600 focus:ring-red-500"
                        />
                        <span>Public Knowledge</span>
                    </label>
                </div>

                <div class="md:col-span-2">
                    <label class="block text-sm font-medium text-gray-300 mb-2">
                        Description
                    </label>
                    <textarea
                        bind:value={newRelationship.description}
                        rows="2"
                        class="input w-full resize-none"
                        placeholder="Describe the nature of this relationship..."
                    ></textarea>
                </div>
            </div>

            <div class="flex justify-end space-x-3 mt-4">
                <button
                    on:click={cancelAddRelationship}
                    class="btn btn-secondary"
                >
                    Cancel
                </button>
                <button
                    on:click={addRelationship}
                    class="btn btn-primary"
                >
                    Add Relationship
                </button>
            </div>
        </div>
    {/if}

    <!-- Save Button -->
    {#if relationships.length > 0}
        <div class="flex justify-end pt-4 border-t border-gray-700">
            <button
                on:click={saveRelationships}
                disabled={saving}
                class="btn btn-primary {saving ? 'opacity-50 cursor-not-allowed' : ''}"
            >
                {saving ? 'Saving...' : 'Save Relationships'}
            </button>
        </div>
    {/if}
</div>