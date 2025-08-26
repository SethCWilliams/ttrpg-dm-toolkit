<script>
    import { createEventDispatcher } from 'svelte';
    import { npcAPI, locationAPI, aiAPI } from '$lib/api.js';
    import { onMount } from 'svelte';

    export let campaignId;

    const dispatch = createEventDispatcher();

    // Form data
    let name = '';
    let race = '';
    let gender = '';
    let age = '';
    let occupation = '';
    let locationId = '';
    let personalityTraits = [''];
    let ideals = '';
    let bonds = '';
    let flaws = '';
    let appearanceDescription = '';
    let background = '';
    let voiceDescription = '';
    let status = 'draft';
    let visibility = 'dm_only';
    let notes = '';

    // Form state
    let loading = false;
    let error = '';
    let locations = [];
    let generatingAI = false;
    
    // Field locking state
    let lockedFields = {
        name: false,
        race: false,
        gender: false,
        age: false,
        occupation: false,
        location: false,
        personalityTraits: false,
        ideals: false,
        bonds: false,
        flaws: false,
        appearanceDescription: false,
        background: false,
        voiceDescription: false,
        notes: false
    };

    onMount(async () => {
        await loadLocations();
    });

    async function loadLocations() {
        try {
            const response = await locationAPI.getLocations(campaignId);
            locations = response.items || [];
        } catch (err) {
            console.error('Failed to load locations:', err);
        }
    }

    function addPersonalityTrait() {
        personalityTraits = [...personalityTraits, ''];
    }

    function removePersonalityTrait(index) {
        personalityTraits = personalityTraits.filter((_, i) => i !== index);
    }

    function toggleFieldLock(field) {
        lockedFields[field] = !lockedFields[field];
        lockedFields = { ...lockedFields }; // Trigger reactivity
    }

    async function generateRandomNPC() {
        generatingAI = true;
        error = '';

        try {
            // Collect locked field data to send as constraints
            const lockedData = {};
            if (lockedFields.name && name.trim()) lockedData.name = name.trim();
            if (lockedFields.race && race.trim()) lockedData.race = race.trim();
            if (lockedFields.gender && gender.trim()) lockedData.gender = gender.trim();
            if (lockedFields.age && age.trim()) lockedData.age = age.trim();
            if (lockedFields.occupation && occupation.trim()) lockedData.occupation = occupation.trim();
            if (lockedFields.ideals && ideals.trim()) lockedData.ideals = ideals.trim();
            if (lockedFields.bonds && bonds.trim()) lockedData.bonds = bonds.trim();
            if (lockedFields.flaws && flaws.trim()) lockedData.flaws = flaws.trim();
            if (lockedFields.background && background.trim()) lockedData.background = background.trim();
            if (lockedFields.appearanceDescription && appearanceDescription.trim()) lockedData.appearance = appearanceDescription.trim();
            if (lockedFields.voiceDescription && voiceDescription.trim()) lockedData.voice_mannerisms = voiceDescription.trim();
            if (lockedFields.notes && notes.trim()) lockedData.notes = notes.trim();
            
            const response = await aiAPI.generateNPC(campaignId, lockedData);
            
            if (response.success && response.npc) {
                const npc = response.npc;
                
                // Only populate unlocked fields with generated data
                if (!lockedFields.name) name = npc.name || '';
                if (!lockedFields.race) race = npc.race || '';
                if (!lockedFields.gender) gender = npc.gender || '';
                if (!lockedFields.age) age = npc.age?.toString() || '';
                if (!lockedFields.occupation) occupation = npc.occupation || '';
                
                // Handle personality traits only if unlocked
                if (!lockedFields.personalityTraits) {
                    if (typeof npc.personality_traits === 'string') {
                        personalityTraits = npc.personality_traits.split(',').map(t => t.trim()).filter(t => t);
                    } else if (Array.isArray(npc.personality_traits)) {
                        personalityTraits = npc.personality_traits;
                    }
                    
                    // Ensure we have at least one trait field
                    if (personalityTraits.length === 0) {
                        personalityTraits = [''];
                    }
                }
                
                if (!lockedFields.ideals) ideals = npc.ideals || '';
                if (!lockedFields.bonds) bonds = npc.bonds || '';
                if (!lockedFields.flaws) flaws = npc.flaws || '';
                if (!lockedFields.appearanceDescription) appearanceDescription = npc.appearance || '';
                if (!lockedFields.background) background = npc.background || '';
                if (!lockedFields.voiceDescription) voiceDescription = npc.voice_mannerisms || '';
                if (!lockedFields.notes) notes = npc.notes || '';
                
                // Show success message if there was a warning
                if (response.warning) {
                    error = response.warning;
                }
            } else {
                error = response.message || 'Failed to generate NPC';
            }
        } catch (err) {
            error = err.message || 'Failed to generate NPC. Please try again.';
        } finally {
            generatingAI = false;
        }
    }

    async function handleSubmit() {
        if (!name.trim()) {
            error = 'NPC name is required';
            return;
        }

        loading = true;
        error = '';

        try {
            const npcData = {
                name: name.trim(),
                race: race.trim() || null,
                gender: gender.trim() || null,
                age: age ? parseInt(age) : null,
                occupation: occupation.trim() || null,
                location_id: locationId ? parseInt(locationId) : null,
                personality_traits: personalityTraits.filter(trait => trait.trim()),
                ideals: ideals.trim() || null,
                bonds: bonds.trim() || null,
                flaws: flaws.trim() || null,
                appearance_description: appearanceDescription.trim() || null,
                background: background.trim() || null,
                voice_description: voiceDescription.trim() || null,
                status,
                visibility,
                notes: notes.trim() || null
            };

            await npcAPI.createNPC(campaignId, npcData);
            dispatch('created');
        } catch (err) {
            error = err.message || 'Failed to create NPC';
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
    <div class="bg-gray-800 rounded-lg max-w-4xl w-full max-h-screen overflow-y-auto">
        <!-- Header -->
        <div class="flex items-center justify-between p-6 border-b border-gray-700">
            <div class="flex items-center space-x-4">
                <h2 class="text-xl font-semibold text-white">Create New NPC</h2>
                <button
                    on:click={generateRandomNPC}
                    disabled={generatingAI}
                    class="btn btn-secondary flex items-center space-x-2 text-sm {generatingAI ? 'opacity-50 cursor-not-allowed' : ''}"
                    title="Generate a random NPC using AI"
                >
                    {#if generatingAI}
                        <div class="animate-spin h-4 w-4 border-2 border-gray-300 border-t-red-500 rounded-full"></div>
                        <span>Generating...</span>
                    {:else}
                        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                        <span>Randomize</span>
                    {/if}
                </button>
            </div>
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
        <form on:submit|preventDefault={handleSubmit} class="p-6">
            {#if error}
                <div class="bg-red-900 border border-red-700 text-red-100 px-4 py-3 rounded mb-6">
                    {error}
                </div>
            {/if}

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Left Column -->
                <div class="space-y-4">
                    <!-- Basic Information -->
                    <div>
                        <h3 class="text-lg font-medium text-white mb-4">Basic Information</h3>
                        
                        <div class="space-y-4">
                            <div>
                                <label for="name" class="block text-sm font-medium text-gray-300 mb-2 flex items-center justify-between">
                                    <span>Name <span class="text-red-400">*</span></span>
                                    <button
                                        type="button"
                                        on:click={() => toggleFieldLock('name')}
                                        class="text-gray-400 hover:text-white transition-colors ml-2"
                                        title="{lockedFields.name ? 'Unlock field (will be randomized)' : 'Lock field (keep current value)'}"
                                    >
                                        {#if lockedFields.name}
                                            <svg class="h-4 w-4 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                                            </svg>
                                        {:else}
                                            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z" />
                                            </svg>
                                        {/if}
                                    </button>
                                </label>
                                <input
                                    id="name"
                                    type="text"
                                    bind:value={name}
                                    class="input w-full {lockedFields.name ? 'border-yellow-400 bg-yellow-50 bg-opacity-10' : ''}"
                                    placeholder="Enter NPC name"
                                    required
                                />
                            </div>

                            <div class="grid grid-cols-2 gap-4">
                                <div>
                                    <label for="race" class="block text-sm font-medium text-gray-300 mb-2 flex items-center justify-between">
                                        <span>Race</span>
                                        <button
                                            type="button"
                                            on:click={() => toggleFieldLock('race')}
                                            class="text-gray-400 hover:text-white transition-colors ml-2"
                                            title="{lockedFields.race ? 'Unlock field (will be randomized)' : 'Lock field (keep current value)'}"
                                        >
                                            {#if lockedFields.race}
                                                <svg class="h-4 w-4 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                                                </svg>
                                            {:else}
                                                <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z" />
                                                </svg>
                                            {/if}
                                        </button>
                                    </label>
                                    <input
                                        id="race"
                                        type="text"
                                        bind:value={race}
                                        class="input w-full {lockedFields.race ? 'border-yellow-400 bg-yellow-50 bg-opacity-10' : ''}"
                                        placeholder="e.g., Human, Elf"
                                    />
                                </div>
                                <div>
                                    <label for="gender" class="block text-sm font-medium text-gray-300 mb-2">
                                        Gender
                                    </label>
                                    <input
                                        id="gender"
                                        type="text"
                                        bind:value={gender}
                                        class="input w-full"
                                        placeholder="e.g., Male, Female"
                                    />
                                </div>
                            </div>

                            <div class="grid grid-cols-2 gap-4">
                                <div>
                                    <label for="age" class="block text-sm font-medium text-gray-300 mb-2">
                                        Age
                                    </label>
                                    <input
                                        id="age"
                                        type="number"
                                        bind:value={age}
                                        class="input w-full"
                                        placeholder="Age in years"
                                        min="0"
                                    />
                                </div>
                                <div>
                                    <label for="occupation" class="block text-sm font-medium text-gray-300 mb-2 flex items-center justify-between">
                                        <span>Occupation</span>
                                        <button
                                            type="button"
                                            on:click={() => toggleFieldLock('occupation')}
                                            class="text-gray-400 hover:text-white transition-colors ml-2"
                                            title="{lockedFields.occupation ? 'Unlock field (will be randomized)' : 'Lock field (keep current value)'}"
                                        >
                                            {#if lockedFields.occupation}
                                                <svg class="h-4 w-4 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                                                </svg>
                                            {:else}
                                                <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z" />
                                                </svg>
                                            {/if}
                                        </button>
                                    </label>
                                    <input
                                        id="occupation"
                                        type="text"
                                        bind:value={occupation}
                                        class="input w-full {lockedFields.occupation ? 'border-yellow-400 bg-yellow-50 bg-opacity-10' : ''}"
                                        placeholder="e.g., Blacksmith, Noble"
                                    />
                                </div>
                            </div>

                            <div>
                                <label for="location" class="block text-sm font-medium text-gray-300 mb-2">
                                    Location
                                </label>
                                <select
                                    id="location"
                                    bind:value={locationId}
                                    class="input w-full"
                                >
                                    <option value="">No specific location</option>
                                    {#each locations as location}
                                        <option value={location.id}>{location.name}</option>
                                    {/each}
                                </select>
                            </div>
                        </div>
                    </div>

                    <!-- Personality Traits -->
                    <div>
                        <h3 class="text-lg font-medium text-white mb-4">Personality</h3>
                        
                        <div class="space-y-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-300 mb-2">
                                    Personality Traits
                                </label>
                                {#each personalityTraits as trait, index}
                                    <div class="flex gap-2 mb-2">
                                        <input
                                            type="text"
                                            bind:value={trait}
                                            class="input flex-1"
                                            placeholder="e.g., Friendly, Suspicious"
                                        />
                                        {#if personalityTraits.length > 1}
                                            <button
                                                type="button"
                                                on:click={() => removePersonalityTrait(index)}
                                                class="btn btn-danger px-3"
                                            >
                                                ×
                                            </button>
                                        {/if}
                                    </div>
                                {/each}
                                <button
                                    type="button"
                                    on:click={addPersonalityTrait}
                                    class="btn btn-secondary text-sm mt-2"
                                >
                                    Add Trait
                                </button>
                            </div>

                            <div>
                                <label for="ideals" class="block text-sm font-medium text-gray-300 mb-2">
                                    Ideals
                                </label>
                                <textarea
                                    id="ideals"
                                    bind:value={ideals}
                                    rows="2"
                                    class="input w-full resize-none"
                                    placeholder="What drives this character..."
                                ></textarea>
                            </div>

                            <div>
                                <label for="bonds" class="block text-sm font-medium text-gray-300 mb-2">
                                    Bonds
                                </label>
                                <textarea
                                    id="bonds"
                                    bind:value={bonds}
                                    rows="2"
                                    class="input w-full resize-none"
                                    placeholder="Important connections and relationships..."
                                ></textarea>
                            </div>

                            <div>
                                <label for="flaws" class="block text-sm font-medium text-gray-300 mb-2">
                                    Flaws
                                </label>
                                <textarea
                                    id="flaws"
                                    bind:value={flaws}
                                    rows="2"
                                    class="input w-full resize-none"
                                    placeholder="Character weaknesses and vices..."
                                ></textarea>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Right Column -->
                <div class="space-y-4">
                    <!-- Description -->
                    <div>
                        <h3 class="text-lg font-medium text-white mb-4">Description</h3>
                        
                        <div class="space-y-4">
                            <div>
                                <label for="appearance" class="block text-sm font-medium text-gray-300 mb-2">
                                    Appearance
                                </label>
                                <textarea
                                    id="appearance"
                                    bind:value={appearanceDescription}
                                    rows="3"
                                    class="input w-full resize-none"
                                    placeholder="Physical description..."
                                ></textarea>
                            </div>

                            <div>
                                <label for="voice" class="block text-sm font-medium text-gray-300 mb-2">
                                    Voice & Mannerisms
                                </label>
                                <textarea
                                    id="voice"
                                    bind:value={voiceDescription}
                                    rows="2"
                                    class="input w-full resize-none"
                                    placeholder="How they speak and act..."
                                ></textarea>
                            </div>

                            <div>
                                <label for="background" class="block text-sm font-medium text-gray-300 mb-2">
                                    Background
                                </label>
                                <textarea
                                    id="background"
                                    bind:value={background}
                                    rows="4"
                                    class="input w-full resize-none"
                                    placeholder="Character history and background..."
                                ></textarea>
                            </div>
                        </div>
                    </div>

                    <!-- Settings -->
                    <div>
                        <h3 class="text-lg font-medium text-white mb-4">Settings</h3>
                        
                        <div class="grid grid-cols-2 gap-4 mb-4">
                            <div>
                                <label for="status" class="block text-sm font-medium text-gray-300 mb-2">
                                    Status
                                </label>
                                <select
                                    id="status"
                                    bind:value={status}
                                    class="input w-full"
                                >
                                    <option value="draft">Draft</option>
                                    <option value="active">Active</option>
                                    <option value="historical">Historical</option>
                                    <option value="dead">Dead</option>
                                </select>
                            </div>

                            <div>
                                <label for="visibility" class="block text-sm font-medium text-gray-300 mb-2">
                                    Visibility
                                </label>
                                <select
                                    id="visibility"
                                    bind:value={visibility}
                                    class="input w-full"
                                >
                                    <option value="dm_only">DM Only</option>
                                    <option value="partially_known">Partially Known</option>
                                    <option value="player_known">Player Known</option>
                                </select>
                            </div>
                        </div>

                        <div>
                            <label for="notes" class="block text-sm font-medium text-gray-300 mb-2">
                                Notes
                            </label>
                            <textarea
                                id="notes"
                                bind:value={notes}
                                rows="3"
                                class="input w-full resize-none"
                                placeholder="Additional notes..."
                            ></textarea>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Actions -->
            <div class="flex justify-end space-x-3 pt-6 mt-6 border-t border-gray-700">
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
                    {loading ? 'Creating...' : 'Create NPC'}
                </button>
            </div>
        </form>
    </div>
</div>