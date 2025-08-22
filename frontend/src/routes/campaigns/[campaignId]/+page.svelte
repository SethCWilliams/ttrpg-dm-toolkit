<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { auth } from '$lib/stores/auth.js';
    import { currentCampaign } from '$lib/stores/campaigns.js';
    import { campaignAPI, npcAPI, locationAPI } from '$lib/api.js';
    import { goto } from '$app/navigation';

    let campaignId;
    let campaign = null;
    let loading = true;
    let error = '';
    let stats = {
        npcs: 0,
        locations: 0,
        organizations: 0,
        plotHooks: 0,
        events: 0,
        items: 0
    };

    onMount(async () => {
        if (!$auth.user) {
            goto('/auth/login');
            return;
        }

        campaignId = $page.params.campaignId;
        await loadCampaign();
    });

    async function loadCampaign() {
        try {
            loading = true;
            campaign = await campaignAPI.getCampaign(campaignId);
            currentCampaign.set(campaign);
            
            // Update stats from the campaign data
            if (campaign.stats) {
                stats = {
                    npcs: campaign.stats.npc_count || 0,
                    locations: campaign.stats.location_count || 0,
                    organizations: campaign.stats.organization_count || 0,
                    plotHooks: campaign.stats.plot_hook_count || 0,
                    events: campaign.stats.event_count || 0,
                    items: campaign.stats.item_count || 0
                };
            }
        } catch (err) {
            error = err.message || 'Failed to load campaign';
        } finally {
            loading = false;
        }
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
    <title>{campaign?.name || 'Campaign'} - DM Toolkit</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    {#if loading}
        <div class="animate-pulse">
            <div class="h-8 bg-gray-700 rounded w-1/3 mb-4"></div>
            <div class="h-4 bg-gray-700 rounded w-1/2 mb-8"></div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                {#each Array(6) as _}
                    <div class="card">
                        <div class="h-6 bg-gray-700 rounded mb-2"></div>
                        <div class="h-8 bg-gray-700 rounded w-16"></div>
                    </div>
                {/each}
            </div>
        </div>
    {:else if error}
        <div class="card bg-red-900 border-red-700">
            <p class="text-red-100">{error}</p>
            <button 
                on:click={() => goto('/dashboard')}
                class="btn btn-secondary mt-4"
            >
                Back to Dashboard
            </button>
        </div>
    {:else if campaign}
        <!-- Header -->
        <div class="mb-8">
            <button
                on:click={() => goto('/dashboard')}
                class="text-gray-400 hover:text-white mb-4 flex items-center"
            >
                <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
                Back to Dashboard
            </button>
            
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-3xl font-bold text-white mb-2">{campaign.name}</h1>
                    {#if campaign.description}
                        <p class="text-gray-400 mb-2">{campaign.description}</p>
                    {/if}
                    {#if campaign.world_name}
                        <p class="text-sm text-gray-500">World: <span class="text-gray-400">{campaign.world_name}</span></p>
                    {/if}
                    {#if campaign.current_date}
                        <p class="text-sm text-gray-500">Current Date: <span class="text-gray-400">{campaign.current_date}</span></p>
                    {/if}
                </div>
                
                <div class="text-right">
                    <p class="text-sm text-gray-500">Created</p>
                    <p class="text-gray-300">{formatDate(campaign.created_at)}</p>
                </div>
            </div>
        </div>

        <!-- Quick Stats -->
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
            <a href="/campaigns/{campaignId}/npcs" class="card hover:bg-gray-750 transition-colors text-center">
                <h3 class="text-sm font-medium text-gray-400 mb-1">NPCs</h3>
                <p class="text-2xl font-bold text-red-500">{stats.npcs}</p>
            </a>
            
            <div class="card text-center opacity-60">
                <h3 class="text-sm font-medium text-gray-400 mb-1">Locations</h3>
                <p class="text-2xl font-bold text-red-500">{stats.locations}</p>
                <p class="text-xs text-gray-600 mt-1">Coming Soon</p>
            </div>
            
            <div class="card text-center opacity-60">
                <h3 class="text-sm font-medium text-gray-400 mb-1">Organizations</h3>
                <p class="text-2xl font-bold text-red-500">{stats.organizations}</p>
                <p class="text-xs text-gray-600 mt-1">Coming Soon</p>
            </div>
            
            <div class="card text-center opacity-60">
                <h3 class="text-sm font-medium text-gray-400 mb-1">Plot Hooks</h3>
                <p class="text-2xl font-bold text-red-500">{stats.plotHooks}</p>
                <p class="text-xs text-gray-600 mt-1">Coming Soon</p>
            </div>
            
            <div class="card text-center opacity-60">
                <h3 class="text-sm font-medium text-gray-400 mb-1">Events</h3>
                <p class="text-2xl font-bold text-red-500">{stats.events}</p>
                <p class="text-xs text-gray-600 mt-1">Coming Soon</p>
            </div>
            
            <div class="card text-center opacity-60">
                <h3 class="text-sm font-medium text-gray-400 mb-1">Items</h3>
                <p class="text-2xl font-bold text-red-500">{stats.items}</p>
                <p class="text-xs text-gray-600 mt-1">Coming Soon</p>
            </div>
        </div>

        <!-- Quick Actions -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <a href="/campaigns/{campaignId}/npcs" class="card hover:bg-gray-750 transition-colors group">
                <div class="flex items-center">
                    <div class="bg-red-600 p-3 rounded-lg mr-4">
                        <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                        </svg>
                    </div>
                    <div>
                        <h3 class="text-lg font-semibold text-white group-hover:text-red-400 transition-colors">Manage NPCs</h3>
                        <p class="text-gray-400">Create and organize your characters</p>
                    </div>
                </div>
            </a>
            
            <div class="card opacity-60">
                <div class="flex items-center">
                    <div class="bg-gray-600 p-3 rounded-lg mr-4">
                        <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                    </div>
                    <div>
                        <h3 class="text-lg font-semibold text-gray-400">Manage Locations</h3>
                        <p class="text-gray-500">Build your world's geography</p>
                        <p class="text-xs text-gray-600 mt-1">Coming Soon</p>
                    </div>
                </div>
            </div>
            
            <div class="card opacity-60">
                <div class="flex items-center">
                    <div class="bg-gray-600 p-3 rounded-lg mr-4">
                        <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                        </svg>
                    </div>
                    <div>
                        <h3 class="text-lg font-semibold text-gray-400">Ideas Inbox</h3>
                        <p class="text-gray-500">Capture and develop your ideas</p>
                        <p class="text-xs text-gray-600 mt-1">Coming Soon</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Recent Activity Placeholder -->
        <div class="card">
            <h2 class="text-xl font-semibold text-white mb-4">Recent Activity</h2>
            <div class="text-center py-8">
                <svg class="mx-auto h-12 w-12 text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <h3 class="text-lg font-medium text-gray-400 mb-2">No recent activity</h3>
                <p class="text-gray-500">Activity will appear here as you build your world</p>
            </div>
        </div>
    {/if}
</div>