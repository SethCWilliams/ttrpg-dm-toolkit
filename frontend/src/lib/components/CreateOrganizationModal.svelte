<script>
    import { createEventDispatcher, onMount } from 'svelte';
    import { organizationAPI, npcAPI, locationAPI } from '$lib/api.js';

    export let campaignId;
    
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
        name: '',
        type: '',
        scope: 'local',
        parent_organization_id: null,
        headquarters_location_id: null,
        leader_npc_id: null,
        goals: [],
        methods: [],
        resources: '',
        influence_level: 'minor',
        membership_size: 'small',
        members: [],
        notable_members: [],
        allies: [],
        enemies: [],
        reputation: '',
        status: 'draft',
        visibility: 'dm_only',
        notes: ''
    };

    const organizationTypes = [
        { value: 'guild', label: 'Guild', description: 'Professional or trade organization' },
        { value: 'government', label: 'Government', description: 'Political governing body' },
        { value: 'religion', label: 'Religious Order', description: 'Faith-based organization' },
        { value: 'criminal', label: 'Criminal Organization', description: 'Illegal operations group' },
        { value: 'military', label: 'Military Unit', description: 'Armed forces organization' },
        { value: 'academic', label: 'Academic Institution', description: 'Educational or research body' },
        { value: 'merchant', label: 'Merchant Organization', description: 'Trade and commerce group' }
    ];

    const scopeOptions = [
        { value: 'local', label: 'Local' },
        { value: 'regional', label: 'Regional' },
        { value: 'national', label: 'National' },
        { value: 'international', label: 'International' }
    ];

    const influenceLevels = [
        { value: 'minor', label: 'Minor' },
        { value: 'moderate', label: 'Moderate' },
        { value: 'major', label: 'Major' },
        { value: 'dominant', label: 'Dominant' }
    ];

    const membershipSizes = [
        { value: 'tiny', label: 'Tiny (1-10)' },
        { value: 'small', label: 'Small (11-50)' },
        { value: 'medium', label: 'Medium (51-200)' },
        { value: 'large', label: 'Large (201-1000)' },
        { value: 'huge', label: 'Huge (1000+)' }
    ];

    onMount(async () => {
        await Promise.all([
            loadTemplates(),
            loadAvailableNPCs(),
            loadAvailableLocations(),
            loadAvailableOrganizations()
        ]);
    });

    async function loadTemplates() {
        try {
            loading = true;
            templates = await organizationAPI.getOrganizationTemplateFields();
        } catch (err) {
            error = 'Failed to load organization templates';
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

    function handleMembershipChange(event, isLeader = false) {
        const npcId = parseInt(event.target.value);
        if (!npcId) return;

        if (isLeader) {
            formData.leader_npc_id = npcId;
        } else {
            if (!formData.notable_members.includes(npcId)) {
                formData.notable_members = [...formData.notable_members, npcId];
            }
        }
        event.target.value = '';
    }

    function removeMember(npcId) {
        formData.notable_members = formData.notable_members.filter(id => id !== npcId);
    }

    async function handleSubmit() {
        if (!formData.name.trim()) {
            error = 'Organization name is required';
            return;
        }

        if (!formData.type) {
            error = 'Organization type is required';
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

            const organization = await organizationAPI.createOrganization(campaignId, submitData);
            dispatch('created', { organization });
        } catch (err) {
            error = err.message || 'Failed to create organization';
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

    function getNPCName(npcId) {
        const npc = availableNPCs.find(n => n.id === npcId);
        return npc ? `${npc.name} ${npc.occupation ? `(${npc.occupation})` : ''}` : `NPC #${npcId}`;
    }

    function handleOrganizationRelationship(event, type) {
        const orgId = parseInt(event.target.value);
        if (!orgId) return;

        if (type === 'ally') {
            if (!formData.allies.includes(orgId)) {
                formData.allies = [...formData.allies, orgId];
            }
        } else if (type === 'enemy') {
            if (!formData.enemies.includes(orgId)) {
                formData.enemies = [...formData.enemies, orgId];
            }
        }
        event.target.value = '';
    }

    function removeOrganizationRelationship(orgId, type) {
        if (type === 'ally') {
            formData.allies = formData.allies.filter(id => id !== orgId);
        } else if (type === 'enemy') {
            formData.enemies = formData.enemies.filter(id => id !== orgId);
        }
    }

    function getOrganizationName(orgId) {
        const org = availableOrganizations.find(o => o.id === orgId);
        return org ? `${org.name} (${org.type})` : `Organization #${orgId}`;
    }
</script>

<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b border-gray-700">
            <h2 class="text-2xl font-semibold text-white">Create New Organization</h2>
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
                                Organization Name <span class="text-red-400">*</span>
                            </label>
                            <input
                                type="text"
                                bind:value={formData.name}
                                class="input w-full"
                                placeholder="Enter organization name"
                                required
                            />
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-300 mb-2">
                                Scope
                            </label>
                            <select bind:value={formData.scope} class="input w-full">
                                {#each scopeOptions as scope}
                                    <option value={scope.value}>{scope.label}</option>
                                {/each}
                            </select>
                        </div>
                    </div>

                    <!-- Parent Organization -->
                    <div>
                        <label class="block text-sm font-medium text-gray-300 mb-2">
                            Parent Organization
                        </label>
                        <select bind:value={formData.parent_organization_id} class="input w-full">
                            <option value={null}>None (Independent Organization)</option>
                            {#each availableOrganizations as org}
                                <option value={org.id}>
                                    {org.name} ({org.type})
                                </option>
                            {/each}
                        </select>
                        <p class="text-xs text-gray-500 mt-1">
                            Select a parent if this is a subsidiary, branch, or sub-organization
                        </p>
                    </div>

                    <!-- Organization Type Selection -->
                    <div>
                        <label class="block text-sm font-medium text-gray-300 mb-3">
                            Organization Type <span class="text-red-400">*</span>
                        </label>
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                            {#each organizationTypes as type}
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

                    <!-- Leadership and Location -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label class="block text-sm font-medium text-gray-300 mb-2">
                                Leader
                            </label>
                            <select bind:value={formData.leader_npc_id} class="input w-full">
                                <option value={null}>No leader selected</option>
                                {#each availableNPCs as npc}
                                    <option value={npc.id}>
                                        {npc.name} {npc.occupation ? `(${npc.occupation})` : ''}
                                    </option>
                                {/each}
                            </select>
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-300 mb-2">
                                Headquarters Location
                            </label>
                            <select bind:value={formData.headquarters_location_id} class="input w-full">
                                <option value={null}>No headquarters selected</option>
                                {#each availableLocations as location}
                                    <option value={location.id}>
                                        {location.name} ({location.type})
                                    </option>
                                {/each}
                            </select>
                        </div>
                    </div>

                    <!-- Organization Details -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label class="block text-sm font-medium text-gray-300 mb-2">
                                Influence Level
                            </label>
                            <select bind:value={formData.influence_level} class="input w-full">
                                {#each influenceLevels as level}
                                    <option value={level.value}>{level.label}</option>
                                {/each}
                            </select>
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-300 mb-2">
                                Membership Size
                            </label>
                            <select bind:value={formData.membership_size} class="input w-full">
                                {#each membershipSizes as size}
                                    <option value={size.value}>{size.label}</option>
                                {/each}
                            </select>
                        </div>
                    </div>

                    <!-- Goals and Methods -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label class="block text-sm font-medium text-gray-300 mb-2">
                                Goals
                            </label>
                            <div>
                                <div class="flex mb-2">
                                    <input
                                        type="text"
                                        id="goals_input"
                                        class="input flex-1 mr-2"
                                        placeholder="Add organizational goal"
                                        on:keydown={(e) => handleTagInputKeydown(e, 'goals')}
                                    />
                                    <button
                                        type="button"
                                        on:click={() => addTag('goals')}
                                        class="btn btn-secondary"
                                    >
                                        Add
                                    </button>
                                </div>
                                {#if formData.goals.length > 0}
                                    <div class="flex flex-wrap gap-2">
                                        {#each formData.goals as goal, index}
                                            <span class="inline-flex items-center px-3 py-1 rounded-full text-xs bg-gray-600 text-gray-300">
                                                {goal}
                                                <button
                                                    type="button"
                                                    on:click={() => removeTag('goals', index)}
                                                    class="ml-2 text-red-400 hover:text-red-300"
                                                >
                                                    ×
                                                </button>
                                            </span>
                                        {/each}
                                    </div>
                                {/if}
                            </div>
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-300 mb-2">
                                Methods
                            </label>
                            <div>
                                <div class="flex mb-2">
                                    <input
                                        type="text"
                                        id="methods_input"
                                        class="input flex-1 mr-2"
                                        placeholder="Add method or approach"
                                        on:keydown={(e) => handleTagInputKeydown(e, 'methods')}
                                    />
                                    <button
                                        type="button"
                                        on:click={() => addTag('methods')}
                                        class="btn btn-secondary"
                                    >
                                        Add
                                    </button>
                                </div>
                                {#if formData.methods.length > 0}
                                    <div class="flex flex-wrap gap-2">
                                        {#each formData.methods as method, index}
                                            <span class="inline-flex items-center px-3 py-1 rounded-full text-xs bg-gray-600 text-gray-300">
                                                {method}
                                                <button
                                                    type="button"
                                                    on:click={() => removeTag('methods', index)}
                                                    class="ml-2 text-red-400 hover:text-red-300"
                                                >
                                                    ×
                                                </button>
                                            </span>
                                        {/each}
                                    </div>
                                {/if}
                            </div>
                        </div>
                    </div>

                    <!-- Notable Members -->
                    <div>
                        <label class="block text-sm font-medium text-gray-300 mb-2">
                            Notable Members
                        </label>
                        <div class="space-y-3">
                            <div class="flex space-x-2">
                                <select
                                    on:change={(e) => handleMembershipChange(e, false)}
                                    class="input flex-1"
                                >
                                    <option value="">Add a member...</option>
                                    {#each availableNPCs.filter(npc => npc.id !== formData.leader_npc_id && !formData.notable_members.includes(npc.id)) as npc}
                                        <option value={npc.id}>
                                            {npc.name} {npc.occupation ? `(${npc.occupation})` : ''}
                                        </option>
                                    {/each}
                                </select>
                            </div>
                            {#if formData.notable_members.length > 0}
                                <div class="space-y-2">
                                    <h4 class="text-sm font-medium text-gray-400">Current Members:</h4>
                                    {#each formData.notable_members as memberId}
                                        <div class="flex items-center justify-between p-2 bg-gray-700 rounded">
                                            <span class="text-sm text-white">{getNPCName(memberId)}</span>
                                            <button
                                                type="button"
                                                on:click={() => removeMember(memberId)}
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

                    <!-- Alliance and Enemy Relationships -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label class="block text-sm font-medium text-gray-300 mb-2">
                                Allied Organizations
                            </label>
                            <div class="space-y-3">
                                <div class="flex space-x-2">
                                    <select
                                        on:change={(e) => handleOrganizationRelationship(e, 'ally')}
                                        class="input flex-1"
                                    >
                                        <option value="">Add an ally...</option>
                                        {#each availableOrganizations.filter(org => !formData.allies.includes(org.id) && !formData.enemies.includes(org.id)) as org}
                                            <option value={org.id}>
                                                {org.name} ({org.type})
                                            </option>
                                        {/each}
                                    </select>
                                </div>
                                {#if formData.allies.length > 0}
                                    <div class="space-y-2">
                                        <h4 class="text-sm font-medium text-gray-400">Current Allies:</h4>
                                        {#each formData.allies as allyId}
                                            <div class="flex items-center justify-between p-2 bg-green-900 bg-opacity-20 border border-green-700 rounded">
                                                <span class="text-sm text-white">{getOrganizationName(allyId)}</span>
                                                <button
                                                    type="button"
                                                    on:click={() => removeOrganizationRelationship(allyId, 'ally')}
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

                        <div>
                            <label class="block text-sm font-medium text-gray-300 mb-2">
                                Enemy Organizations
                            </label>
                            <div class="space-y-3">
                                <div class="flex space-x-2">
                                    <select
                                        on:change={(e) => handleOrganizationRelationship(e, 'enemy')}
                                        class="input flex-1"
                                    >
                                        <option value="">Add an enemy...</option>
                                        {#each availableOrganizations.filter(org => !formData.allies.includes(org.id) && !formData.enemies.includes(org.id)) as org}
                                            <option value={org.id}>
                                                {org.name} ({org.type})
                                            </option>
                                        {/each}
                                    </select>
                                </div>
                                {#if formData.enemies.length > 0}
                                    <div class="space-y-2">
                                        <h4 class="text-sm font-medium text-gray-400">Current Enemies:</h4>
                                        {#each formData.enemies as enemyId}
                                            <div class="flex items-center justify-between p-2 bg-red-900 bg-opacity-20 border border-red-700 rounded">
                                                <span class="text-sm text-white">{getOrganizationName(enemyId)}</span>
                                                <button
                                                    type="button"
                                                    on:click={() => removeOrganizationRelationship(enemyId, 'enemy')}
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

                    <!-- Dynamic Fields Based on Type -->
                    {#if formData.type && currentTemplate && Object.keys(currentTemplate).length > 0}
                        <div class="border-t border-gray-700 pt-6">
                            <h3 class="text-lg font-medium text-white mb-4">
                                {organizationTypes.find(t => t.value === formData.type)?.label} Details
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
                                <label class="block text-sm font-medium text-gray-300 mb-2">Resources</label>
                                <textarea
                                    bind:value={formData.resources}
                                    rows="2"
                                    class="input w-full resize-y"
                                    placeholder="Describe the organization's resources, assets, and capabilities..."
                                ></textarea>
                            </div>

                            <div>
                                <label class="block text-sm font-medium text-gray-300 mb-2">Reputation</label>
                                <textarea
                                    bind:value={formData.reputation}
                                    rows="2"
                                    class="input w-full resize-y"
                                    placeholder="How is this organization viewed by others..."
                                ></textarea>
                            </div>

                            <div>
                                <label class="block text-sm font-medium text-gray-300 mb-2">Notes</label>
                                <textarea
                                    bind:value={formData.notes}
                                    rows="3"
                                    class="input w-full resize-y"
                                    placeholder="Additional notes and information..."
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
                                    <option value="historical">Historical</option>
                                    <option value="disbanded">Disbanded</option>
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
                            {saving ? 'Creating...' : 'Create Organization'}
                        </button>
                    </div>
                </form>
            {/if}
        </div>
    </div>
</div>