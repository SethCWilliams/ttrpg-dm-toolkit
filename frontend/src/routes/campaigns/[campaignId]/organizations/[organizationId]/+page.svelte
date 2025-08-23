<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { auth } from '$lib/stores/auth.js';
    import { currentCampaign } from '$lib/stores/campaigns.js';
    import { organizationAPI, campaignAPI, npcAPI, locationAPI } from '$lib/api.js';
    import { goto } from '$app/navigation';
    import EditOrganizationModal from '$lib/components/EditOrganizationModal.svelte';

    let campaignId;
    let organizationId;
    let organization = null;
    let leader = null;
    let headquarters = null;
    let members = [];
    let loading = true;
    let error = '';
    let showEditModal = false;

    onMount(async () => {
        if (!$auth.user) {
            goto('/auth/login');
            return;
        }

        campaignId = $page.params.campaignId;
        organizationId = parseInt($page.params.organizationId);
        
        // Load campaign info if not already loaded
        if (!$currentCampaign || $currentCampaign.id != campaignId) {
            try {
                const campaign = await campaignAPI.getCampaign(campaignId);
                currentCampaign.set(campaign);
            } catch (err) {
                error = 'Campaign not found';
                return;
            }
        }

        await loadOrganization();
        await loadRelatedData();
    });

    async function loadOrganization() {
        try {
            loading = true;
            organization = await organizationAPI.getOrganization(campaignId, organizationId);
        } catch (err) {
            error = err.message || 'Failed to load organization';
        } finally {
            loading = false;
        }
    }

    async function loadRelatedData() {
        if (!organization) return;

        try {
            // Load leader NPC if exists
            if (organization.leader_npc_id) {
                try {
                    leader = await npcAPI.getNPC(campaignId, organization.leader_npc_id);
                } catch (err) {
                    console.error('Failed to load leader:', err);
                }
            }

            // Load headquarters location if exists
            if (organization.headquarters_location_id) {
                try {
                    headquarters = await locationAPI.getLocation(campaignId, organization.headquarters_location_id);
                } catch (err) {
                    console.error('Failed to load headquarters:', err);
                }
            }

            // Load member NPCs
            if (organization.notable_members && organization.notable_members.length > 0) {
                const memberPromises = organization.notable_members.map(memberId =>
                    npcAPI.getNPC(campaignId, memberId).catch(err => {
                        console.error(`Failed to load member ${memberId}:`, err);
                        return null;
                    })
                );
                const memberResults = await Promise.all(memberPromises);
                members = memberResults.filter(member => member !== null);
            }
        } catch (err) {
            console.error('Failed to load related data:', err);
        }
    }

    async function handleDelete() {
        if (!confirm('Are you sure you want to delete this organization? This action cannot be undone.')) {
            return;
        }

        try {
            await organizationAPI.deleteOrganization(campaignId, organizationId);
            goto(`/campaigns/${campaignId}/organizations`);
        } catch (err) {
            alert('Failed to delete organization: ' + err.message);
        }
    }

    function handleOrganizationUpdated(event) {
        showEditModal = false;
        organization = event.detail.organization;
        // Reload related data in case relationships changed
        loadRelatedData();
    }

    // Get available parent locations for the edit modal
    async function getAvailableParents() {
        try {
            const response = await locationAPI.getLocations(campaignId, { limit: 100 });
            return response.items || [];
        } catch (err) {
            console.error('Failed to load parent locations:', err);
            return [];
        }
    }

    function getOrganizationIcon(type) {
        switch (type) {
            case 'guild': return '🏛️';
            case 'government': return '🏛️';
            case 'religion': return '⛪';
            case 'criminal': return '🗡️';
            case 'military': return '⚔️';
            case 'academic': return '📚';
            case 'merchant': return '💰';
            default: return '🏢';
        }
    }

    function getStatusColor(status) {
        switch (status) {
            case 'active': return 'bg-green-600';
            case 'draft': return 'bg-yellow-600';
            case 'historical': return 'bg-blue-600';
            case 'disbanded': return 'bg-red-600';
            default: return 'bg-gray-600';
        }
    }

    function getVisibilityText(visibility) {
        switch (visibility) {
            case 'player_known': return 'Known to Players';
            case 'partially_known': return 'Partially Known';
            case 'dm_only': return 'DM Only';
            default: return 'Unknown';
        }
    }

    function formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    function capitalizeWords(str) {
        if (!str) return '';
        return str.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    }

    function renderTags(tags) {
        if (!Array.isArray(tags)) return [];
        return tags;
    }
</script>

<svelte:head>
    <title>{organization?.name || 'Organization'} - DM Toolkit</title>
</svelte:head>

<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    {#if loading}
        <div class="animate-pulse">
            <div class="h-8 bg-gray-700 rounded w-1/3 mb-4"></div>
            <div class="h-6 bg-gray-700 rounded w-1/2 mb-8"></div>
            <div class="space-y-4">
                {#each Array(4) as _}
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
                on:click={() => goto(`/campaigns/${campaignId}/organizations`)}
                class="btn btn-secondary mt-4"
            >
                Back to Organizations
            </button>
        </div>
    {:else if organization}
        <!-- Header -->
        <div class="mb-8">
            <button
                on:click={() => goto(`/campaigns/${campaignId}/organizations`)}
                class="text-gray-400 hover:text-white mb-4 flex items-center"
            >
                <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
                Back to Organizations
            </button>
            
            <div class="flex items-start justify-between">
                <div class="flex items-start space-x-4 flex-1">
                    <div class="text-4xl">{getOrganizationIcon(organization.type)}</div>
                    <div class="flex-1">
                        <h1 class="text-3xl font-bold text-white mb-2">{organization.name}</h1>
                        
                        <div class="flex items-center space-x-3 mb-4">
                            <span class="px-2 py-1 text-xs font-medium rounded {getStatusColor(organization.status)} text-white">
                                {organization.status}
                            </span>
                            <span class="px-2 py-1 text-xs font-medium rounded bg-gray-700 text-gray-300">
                                {capitalizeWords(organization.type)}
                            </span>
                            {#if organization.scope}
                                <span class="px-2 py-1 text-xs font-medium rounded bg-blue-700 text-blue-300">
                                    {capitalizeWords(organization.scope)}
                                </span>
                            {/if}
                            <span class="text-sm text-gray-400">
                                {getVisibilityText(organization.visibility)}
                            </span>
                        </div>

                        <div class="flex items-center space-x-6 text-sm text-gray-400">
                            {#if organization.membership_size}
                                <div class="flex items-center space-x-1">
                                    <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                                    </svg>
                                    <span>{capitalizeWords(organization.membership_size)} Membership</span>
                                </div>
                            {/if}
                            {#if organization.influence_level}
                                <div class="flex items-center space-x-1">
                                    <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                                    </svg>
                                    <span>{capitalizeWords(organization.influence_level)} Influence</span>
                                </div>
                            {/if}
                        </div>
                    </div>
                </div>
                
                <div class="flex items-center space-x-3">
                    <button
                        on:click={() => showEditModal = true}
                        class="btn btn-secondary"
                    >
                        Edit
                    </button>
                    <button
                        on:click={handleDelete}
                        class="btn btn-danger"
                    >
                        Delete
                    </button>
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Main Content -->
            <div class="lg:col-span-2 space-y-6">
                <!-- Goals -->
                {#if organization.goals && renderTags(organization.goals).length > 0}
                    <div class="card">
                        <h2 class="text-xl font-semibold text-white mb-4">Goals</h2>
                        <div class="space-y-2">
                            {#each renderTags(organization.goals) as goal}
                                <div class="flex items-center space-x-2">
                                    <svg class="h-4 w-4 text-green-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                    <span class="text-gray-300">{goal}</span>
                                </div>
                            {/each}
                        </div>
                    </div>
                {/if}

                <!-- Methods -->
                {#if organization.methods && renderTags(organization.methods).length > 0}
                    <div class="card">
                        <h2 class="text-xl font-semibold text-white mb-4">Methods</h2>
                        <div class="flex flex-wrap gap-2">
                            {#each renderTags(organization.methods) as method}
                                <span class="px-3 py-1 bg-blue-700 text-blue-300 text-sm rounded">
                                    {method}
                                </span>
                            {/each}
                        </div>
                    </div>
                {/if}

                <!-- Resources -->
                {#if organization.resources}
                    <div class="card">
                        <h2 class="text-xl font-semibold text-white mb-4">Resources</h2>
                        <p class="text-gray-300 whitespace-pre-wrap">{organization.resources}</p>
                    </div>
                {/if}

                <!-- Reputation -->
                {#if organization.reputation}
                    <div class="card">
                        <h2 class="text-xl font-semibold text-white mb-4">Reputation</h2>
                        <p class="text-gray-300 whitespace-pre-wrap">{organization.reputation}</p>
                    </div>
                {/if}

                <!-- Notes -->
                {#if organization.notes}
                    <div class="card">
                        <h2 class="text-xl font-semibold text-white mb-4">Notes</h2>
                        <p class="text-gray-300 whitespace-pre-wrap">{organization.notes}</p>
                    </div>
                {/if}
            </div>

            <!-- Sidebar -->
            <div class="space-y-6">
                <!-- Leadership -->
                {#if leader || headquarters}
                    <div class="card">
                        <h2 class="text-lg font-semibold text-white mb-4">Leadership & Location</h2>
                        <div class="space-y-4">
                            {#if leader}
                                <div>
                                    <h3 class="text-sm font-medium text-gray-400 mb-2">Leader</h3>
                                    <a
                                        href="/campaigns/{campaignId}/npcs/{leader.id}"
                                        class="block p-3 bg-gray-700 hover:bg-gray-600 rounded transition-colors"
                                    >
                                        <div class="text-sm font-medium text-white">{leader.name}</div>
                                        {#if leader.occupation}
                                            <div class="text-xs text-gray-400">{leader.occupation}</div>
                                        {/if}
                                    </a>
                                </div>
                            {/if}

                            {#if headquarters}
                                <div>
                                    <h3 class="text-sm font-medium text-gray-400 mb-2">Headquarters</h3>
                                    <a
                                        href="/campaigns/{campaignId}/locations/{headquarters.id}"
                                        class="block p-3 bg-gray-700 hover:bg-gray-600 rounded transition-colors"
                                    >
                                        <div class="text-sm font-medium text-white">{headquarters.name}</div>
                                        <div class="text-xs text-gray-400 capitalize">{headquarters.type}</div>
                                    </a>
                                </div>
                            {/if}
                        </div>
                    </div>
                {/if}

                <!-- Notable Members -->
                {#if members.length > 0}
                    <div class="card">
                        <h2 class="text-lg font-semibold text-white mb-4">Notable Members</h2>
                        <div class="space-y-3">
                            {#each members as member}
                                <a
                                    href="/campaigns/{campaignId}/npcs/{member.id}"
                                    class="block p-3 bg-gray-700 hover:bg-gray-600 rounded transition-colors"
                                >
                                    <div class="text-sm font-medium text-white">{member.name}</div>
                                    {#if member.occupation}
                                        <div class="text-xs text-gray-400">{member.occupation}</div>
                                    {/if}
                                </a>
                            {/each}
                        </div>
                    </div>
                {/if}

                <!-- Relationships -->
                {#if (organization.allies && organization.allies.length > 0) || (organization.enemies && organization.enemies.length > 0)}
                    <div class="card">
                        <h2 class="text-lg font-semibold text-white mb-4">Relationships</h2>
                        <div class="space-y-4">
                            {#if organization.allies && organization.allies.length > 0}
                                <div>
                                    <h3 class="text-sm font-medium text-green-400 mb-2">Allies</h3>
                                    <div class="text-sm text-gray-300">
                                        {organization.allies.length} allied organization(s)
                                    </div>
                                </div>
                            {/if}

                            {#if organization.enemies && organization.enemies.length > 0}
                                <div>
                                    <h3 class="text-sm font-medium text-red-400 mb-2">Enemies</h3>
                                    <div class="text-sm text-gray-300">
                                        {organization.enemies.length} enemy organization(s)
                                    </div>
                                </div>
                            {/if}
                        </div>
                    </div>
                {/if}

                <!-- Meta Information -->
                <div class="card">
                    <h2 class="text-lg font-semibold text-white mb-4">Information</h2>
                    <div class="space-y-3 text-sm">
                        <div>
                            <span class="text-gray-500">Created:</span>
                            <div class="text-gray-300">{formatDate(organization.created_at)}</div>
                        </div>
                        <div>
                            <span class="text-gray-500">Last Updated:</span>
                            <div class="text-gray-300">{formatDate(organization.updated_at)}</div>
                        </div>
                        <div>
                            <span class="text-gray-500">ID:</span>
                            <div class="text-gray-300">#{organization.id}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    {/if}
</div>

<!-- Edit Organization Modal -->
{#if showEditModal && organization}
    <EditOrganizationModal
        {campaignId}
        {organization}
        on:updated={handleOrganizationUpdated}
        on:close={() => showEditModal = false}
    />
{/if}