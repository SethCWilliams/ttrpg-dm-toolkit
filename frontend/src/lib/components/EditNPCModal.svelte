<script>
    import { createEventDispatcher, onMount } from 'svelte';
    import { npcAPI, locationAPI } from '$lib/api.js';

    export let campaignId;
    export let npc;

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

    onMount(async () => {
        // Populate form with existing NPC data
        name = npc.name || '';
        race = npc.race || '';
        gender = npc.gender || '';
        age = npc.age ? npc.age.toString() : '';
        occupation = npc.occupation || '';
        locationId = npc.location_id ? npc.location_id.toString() : '';
        personalityTraits = npc.personality_traits && npc.personality_traits.length > 0 
            ? npc.personality_traits 
            : [''];
        ideals = npc.ideals || '';
        bonds = npc.bonds || '';
        flaws = npc.flaws || '';
        appearanceDescription = npc.appearance_description || '';
        background = npc.background || '';
        voiceDescription = npc.voice_description || '';
        status = npc.status || 'draft';
        visibility = npc.visibility || 'dm_only';
        notes = npc.notes || '';

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

            await npcAPI.updateNPC(campaignId, npc.id, npcData);
            dispatch('updated');
        } catch (err) {
            error = err.message || 'Failed to update NPC';
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
            <h2 class="text-xl font-semibold text-white">Edit {npc.name}</h2>
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
                                <label for="name" class="block text-sm font-medium text-gray-300 mb-2">
                                    Name <span class="text-red-400">*</span>
                                </label>
                                <input
                                    id="name"
                                    type="text"
                                    bind:value={name}
                                    class="input w-full"
                                    placeholder="Enter NPC name"
                                    required
                                />
                            </div>

                            <div class="grid grid-cols-2 gap-4">
                                <div>
                                    <label for="race" class="block text-sm font-medium text-gray-300 mb-2">
                                        Race
                                    </label>
                                    <input
                                        id="race"
                                        type="text"
                                        bind:value={race}
                                        class="input w-full"
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
                                    <label for="occupation" class="block text-sm font-medium text-gray-300 mb-2">
                                        Occupation
                                    </label>
                                    <input
                                        id="occupation"
                                        type="text"
                                        bind:value={occupation}
                                        class="input w-full"
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
                    {loading ? 'Updating...' : 'Update NPC'}
                </button>
            </div>
        </form>
    </div>
</div>