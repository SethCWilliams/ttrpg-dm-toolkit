<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { auth } from '$lib/stores/auth.js';
    import { currentCampaign } from '$lib/stores/campaigns.js';
    import { plotHookAPI, npcAPI, locationAPI, organizationAPI } from '$lib/api.js';
    import { goto } from '$app/navigation';

    let campaignId;
    let hookId;
    let plotHook = null;
    let relatedNPCs = [];
    let relatedLocations = [];
    let relatedOrganizations = [];
    let loading = true;
    let error = '';

    onMount(async () => {
        if (!$auth.user) {
            goto('/auth/login');
            return;
        }

        campaignId = $page.params.campaignId;
        hookId = $page.params.hookId;
        await loadPlotHook();
    });

    async function loadPlotHook() {
        try {
            loading = true;
            plotHook = await plotHookAPI.getPlotHook(campaignId, hookId);
            
            // Load related entities
            await loadRelatedEntities();
        } catch (err) {
            error = err.message || 'Failed to load plot hook';
        } finally {
            loading = false;
        }
    }

    async function loadRelatedEntities() {
        try {
            const promises = [];
            
            // Load related NPCs
            if (plotHook.related_npcs?.length > 0) {
                promises.push(
                    Promise.all(
                        plotHook.related_npcs.map(npcId => 
                            npcAPI.getNPC(campaignId, npcId).catch(() => null)
                        )
                    ).then(npcs => {
                        relatedNPCs = npcs.filter(npc => npc !== null);
                    })
                );
            }
            
            // Load related locations
            if (plotHook.related_locations?.length > 0) {
                promises.push(
                    Promise.all(
                        plotHook.related_locations.map(locationId => 
                            locationAPI.getLocation(campaignId, locationId).catch(() => null)
                        )
                    ).then(locations => {
                        relatedLocations = locations.filter(location => location !== null);
                    })
                );
            }
            
            // Load related organizations
            if (plotHook.related_organizations?.length > 0) {
                promises.push(
                    Promise.all(
                        plotHook.related_organizations.map(orgId => 
                            organizationAPI.getOrganization(campaignId, orgId).catch(() => null)
                        )
                    ).then(orgs => {
                        relatedOrganizations = orgs.filter(org => org !== null);
                    })
                );
            }
            
            await Promise.all(promises);
        } catch (err) {
            console.error('Error loading related entities:', err);
        }
    }

    function getStatusBadgeClass(status) {
        const classes = {
            draft: 'bg-gray-600 text-gray-300',
            available: 'bg-blue-600 text-blue-100',
            active: 'bg-green-600 text-green-100',
            completed: 'bg-purple-600 text-purple-100',
            failed: 'bg-red-600 text-red-100',
            abandoned: 'bg-orange-600 text-orange-100'
        };
        return classes[status] || 'bg-gray-600 text-gray-300';
    }

    function getUrgencyBadgeClass(urgency) {
        const classes = {
            immediate: 'bg-red-600 text-red-100',
            urgent: 'bg-orange-600 text-orange-100',
            moderate: 'bg-yellow-600 text-yellow-100',
            background: 'bg-gray-600 text-gray-300'
        };
        return classes[urgency] || 'bg-gray-600 text-gray-300';
    }

    function capitalizeWords(str) {
        if (!str) return '';
        return str.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    function formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }
</script>

<svelte:head>
    <title>{plotHook?.title || 'Plot Hook'} - {$currentCampaign?.name || 'Campaign'} - DM Toolkit</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    {#if loading}
        <div class="animate-pulse">
            <div class="h-8 bg-gray-700 rounded w-1/3 mb-4"></div>
            <div class="h-4 bg-gray-700 rounded w-1/2 mb-8"></div>
            <div class="space-y-4">
                {#each Array(3) as _}
                    <div class="card">
                        <div class="h-6 bg-gray-700 rounded mb-2"></div>
                        <div class="h-4 bg-gray-700 rounded w-3/4"></div>
                    </div>
                {/each}
            </div>
        </div>
    {:else if error}
        <div class="card bg-red-900 border-red-700">
            <p class="text-red-100">{error}</p>
            <button 
                on:click={() => goto(`/campaigns/${campaignId}/plot-hooks`)}
                class="btn btn-secondary mt-4"
            >
                Back to Plot Hooks
            </button>
        </div>
    {:else if plotHook}
        <!-- Header -->
        <div class="mb-8">
            <button
                on:click={() => goto(`/campaigns/${campaignId}/plot-hooks`)}
                class="text-gray-400 hover:text-white mb-4 flex items-center"
            >
                <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
                Back to Plot Hooks
            </button>
            
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-3xl font-bold text-white mb-2">{plotHook.title}</h1>
                    <div class="flex flex-wrap gap-2 mb-4">
                        {#if plotHook.hook_type}
                            <span class="px-3 py-1 rounded-full text-sm bg-blue-600 text-blue-100">
                                {capitalizeWords(plotHook.hook_type)}
                            </span>
                        {/if}
                        
                        <span class="px-3 py-1 rounded-full text-sm {getStatusBadgeClass(plotHook.status)}">
                            {capitalizeWords(plotHook.status)}
                        </span>
                        
                        {#if plotHook.urgency}
                            <span class="px-3 py-1 rounded-full text-sm {getUrgencyBadgeClass(plotHook.urgency)}">
                                {capitalizeWords(plotHook.urgency)} Urgency
                            </span>
                        {/if}
                        
                        {#if plotHook.complexity}
                            <span class="px-3 py-1 rounded-full text-sm bg-purple-600 text-purple-100">
                                {capitalizeWords(plotHook.complexity)} Complexity
                            </span>
                        {/if}
                    </div>
                </div>
                
                <div class="flex space-x-3">
                    <button class="btn btn-secondary">
                        <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                        Edit
                    </button>
                    <button class="btn btn-danger">
                        <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                        Delete
                    </button>
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <!-- Main Content -->
            <div class="lg:col-span-2 space-y-6">
                <!-- Description -->
                {#if plotHook.description}
                    <div class="card">
                        <h2 class="text-xl font-semibold text-white mb-4">Description</h2>
                        <div class="prose prose-gray prose-invert max-w-none">
                            <p class="text-gray-300 whitespace-pre-wrap">{plotHook.description}</p>
                        </div>
                    </div>
                {/if}

                <!-- Type-specific Fields -->
                {#if plotHook.hook_type}
                    <div class="card">
                        <h2 class="text-xl font-semibold text-white mb-4">
                            {capitalizeWords(plotHook.hook_type)} Details
                        </h2>
                        
                        <div class="space-y-4">
                            {#each Object.entries(plotHook).filter(([key, value]) => 
                                !['id', 'campaign_id', 'title', 'description', 'hook_type', 'urgency', 'complexity', 'related_npcs', 'related_locations', 'related_organizations', 'prerequisites', 'rewards', 'consequences', 'status', 'visibility', 'notes', 'created_at', 'updated_at'].includes(key) && 
                                value !== null && value !== '' && (Array.isArray(value) ? value.length > 0 : true)
                            ) as [key, value]}
                                <div>
                                    <h3 class="text-sm font-medium text-gray-400 mb-1">
                                        {capitalizeWords(key)}
                                    </h3>
                                    {#if Array.isArray(value)}
                                        <div class="flex flex-wrap gap-2">
                                            {#each value as item}
                                                <span class="px-2 py-1 bg-gray-700 text-gray-300 text-sm rounded">
                                                    {item}
                                                </span>
                                            {/each}
                                        </div>
                                    {:else}
                                        <p class="text-gray-300 whitespace-pre-wrap">{value}</p>
                                    {/if}
                                </div>
                            {/each}
                        </div>
                    </div>
                {/if}

                <!-- Prerequisites -->
                {#if plotHook.prerequisites && plotHook.prerequisites.length > 0}
                    <div class="card">
                        <h2 class="text-xl font-semibold text-white mb-4">Prerequisites</h2>
                        <div class="space-y-2">
                            {#each plotHook.prerequisites as prerequisite, index}
                                <div class="flex items-center p-3 bg-gray-700 rounded">
                                    <div class="w-6 h-6 bg-yellow-600 text-yellow-100 rounded-full flex items-center justify-center text-xs font-medium mr-3">
                                        {index + 1}
                                    </div>
                                    <div class="text-gray-300">
                                        {typeof prerequisite === 'string' ? prerequisite : JSON.stringify(prerequisite)}
                                    </div>
                                </div>
                            {/each}
                        </div>
                    </div>
                {/if}

                <!-- Rewards -->
                {#if plotHook.rewards}
                    <div class="card">
                        <h2 class="text-xl font-semibold text-white mb-4">Rewards</h2>
                        <div class="p-4 bg-green-900 bg-opacity-20 border border-green-700 rounded">
                            <pre class="text-green-100 whitespace-pre-wrap">{JSON.stringify(plotHook.rewards, null, 2)}</pre>
                        </div>
                    </div>
                {/if}

                <!-- Consequences -->
                {#if plotHook.consequences}
                    <div class="card">
                        <h2 class="text-xl font-semibold text-white mb-4">Consequences</h2>
                        <div class="p-4 bg-red-900 bg-opacity-20 border border-red-700 rounded">
                            <pre class="text-red-100 whitespace-pre-wrap">{JSON.stringify(plotHook.consequences, null, 2)}</pre>
                        </div>
                    </div>
                {/if}

                <!-- Notes -->
                {#if plotHook.notes}
                    <div class="card">
                        <h2 class="text-xl font-semibold text-white mb-4">Notes</h2>
                        <div class="prose prose-gray prose-invert max-w-none">
                            <p class="text-gray-300 whitespace-pre-wrap">{plotHook.notes}</p>
                        </div>
                    </div>
                {/if}
            </div>

            <!-- Sidebar -->
            <div class="space-y-6">
                <!-- Quick Info -->
                <div class="card">
                    <h2 class="text-lg font-semibold text-white mb-4">Quick Info</h2>
                    <div class="space-y-3">
                        <div>
                            <span class="text-sm text-gray-400">Created:</span>
                            <span class="text-gray-300 ml-2">{formatDate(plotHook.created_at)}</span>
                        </div>
                        <div>
                            <span class="text-sm text-gray-400">Updated:</span>
                            <span class="text-gray-300 ml-2">{formatDate(plotHook.updated_at)}</span>
                        </div>
                        <div>
                            <span class="text-sm text-gray-400">Visibility:</span>
                            <span class="text-gray-300 ml-2">{capitalizeWords(plotHook.visibility)}</span>
                        </div>
                    </div>
                </div>

                <!-- Related NPCs -->
                {#if relatedNPCs.length > 0}
                    <div class="card">
                        <h2 class="text-lg font-semibold text-white mb-4">Related NPCs</h2>
                        <div class="space-y-2">
                            {#each relatedNPCs as npc}
                                <a 
                                    href="/campaigns/{campaignId}/npcs/{npc.id}"
                                    class="block p-3 bg-gray-700 hover:bg-gray-600 rounded transition-colors"
                                >
                                    <div class="text-white font-medium">{npc.name}</div>
                                    {#if npc.occupation}
                                        <div class="text-gray-400 text-sm">{npc.occupation}</div>
                                    {/if}
                                </a>
                            {/each}
                        </div>
                    </div>
                {/if}

                <!-- Related Locations -->
                {#if relatedLocations.length > 0}
                    <div class="card">
                        <h2 class="text-lg font-semibold text-white mb-4">Related Locations</h2>
                        <div class="space-y-2">
                            {#each relatedLocations as location}
                                <a 
                                    href="/campaigns/{campaignId}/locations/{location.id}"
                                    class="block p-3 bg-gray-700 hover:bg-gray-600 rounded transition-colors"
                                >
                                    <div class="text-white font-medium">{location.name}</div>
                                    {#if location.type}
                                        <div class="text-gray-400 text-sm">{capitalizeWords(location.type)}</div>
                                    {/if}
                                </a>
                            {/each}
                        </div>
                    </div>
                {/if}

                <!-- Related Organizations -->
                {#if relatedOrganizations.length > 0}
                    <div class="card">
                        <h2 class="text-lg font-semibold text-white mb-4">Related Organizations</h2>
                        <div class="space-y-2">
                            {#each relatedOrganizations as org}
                                <a 
                                    href="/campaigns/{campaignId}/organizations/{org.id}"
                                    class="block p-3 bg-gray-700 hover:bg-gray-600 rounded transition-colors"
                                >
                                    <div class="text-white font-medium">{org.name}</div>
                                    {#if org.type}
                                        <div class="text-gray-400 text-sm">{capitalizeWords(org.type)}</div>
                                    {/if}
                                </a>
                            {/each}
                        </div>
                    </div>
                {/if}
            </div>
        </div>
    {/if}
</div>