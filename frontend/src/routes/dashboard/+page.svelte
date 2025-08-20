<script>
    import { onMount } from 'svelte';
    import { auth } from '$lib/stores/auth.js';
    import { campaigns, currentCampaign } from '$lib/stores/campaigns.js';
    import { campaignAPI } from '$lib/api.js';
    import { goto } from '$app/navigation';
    import CampaignCard from '$lib/components/CampaignCard.svelte';
    import CreateCampaignModal from '$lib/components/CreateCampaignModal.svelte';

    let loading = true;
    let error = '';
    let showCreateModal = false;

    // Redirect if not authenticated
    onMount(() => {
        if (!$auth.user) {
            goto('/auth/login');
            return;
        }

        loadCampaigns();
    });

    async function loadCampaigns() {
        try {
            loading = true;
            const campaignList = await campaignAPI.getCampaigns();
            campaigns.set(campaignList);
        } catch (err) {
            error = err.message || 'Failed to load campaigns';
        } finally {
            loading = false;
        }
    }

    function handleCampaignCreated() {
        showCreateModal = false;
        loadCampaigns();
    }

    function selectCampaign(campaign) {
        currentCampaign.set(campaign);
        goto(`/campaigns/${campaign.id}`);
    }
</script>

<svelte:head>
    <title>Dashboard - DM Toolkit</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="mb-8">
        <h1 class="text-3xl font-bold text-white mb-2">
            Welcome back, {$auth.user?.username}!
        </h1>
        <p class="text-gray-400">
            Manage your campaigns and build amazing worlds.
        </p>
    </div>

    <!-- Campaigns Section -->
    <div class="mb-8">
        <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-semibold text-white">Your Campaigns</h2>
            <button 
                on:click={() => showCreateModal = true}
                class="btn btn-primary"
            >
                New Campaign
            </button>
        </div>

        {#if loading}
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {#each Array(3) as _}
                    <div class="card animate-pulse">
                        <div class="h-4 bg-gray-700 rounded mb-2"></div>
                        <div class="h-3 bg-gray-700 rounded w-3/4 mb-4"></div>
                        <div class="h-2 bg-gray-700 rounded w-1/2"></div>
                    </div>
                {/each}
            </div>
        {:else if error}
            <div class="card bg-red-900 border-red-700">
                <p class="text-red-100">{error}</p>
                <button 
                    on:click={loadCampaigns}
                    class="btn btn-secondary mt-4"
                >
                    Try Again
                </button>
            </div>
        {:else if $campaigns.length === 0}
            <div class="text-center py-12">
                <div class="mb-4">
                    <svg class="mx-auto h-16 w-16 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                </div>
                <h3 class="text-lg font-medium text-gray-300 mb-2">No campaigns yet</h3>
                <p class="text-gray-500 mb-6">Get started by creating your first campaign</p>
                <button 
                    on:click={() => showCreateModal = true}
                    class="btn btn-primary"
                >
                    Create Your First Campaign
                </button>
            </div>
        {:else}
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {#each $campaigns as campaign}
                    <CampaignCard 
                        {campaign} 
                        on:select={() => selectCampaign(campaign)}
                        on:refresh={loadCampaigns}
                    />
                {/each}
            </div>
        {/if}
    </div>

    <!-- Quick Stats -->
    {#if $campaigns.length > 0}
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div class="card text-center">
                <div class="text-2xl font-bold text-red-500 mb-1">
                    {$campaigns.length}
                </div>
                <div class="text-sm text-gray-400">Campaigns</div>
            </div>
            
            <div class="card text-center">
                <div class="text-2xl font-bold text-red-500 mb-1">
                    {$campaigns.reduce((total, c) => total + (c.stats?.npc_count || 0), 0)}
                </div>
                <div class="text-sm text-gray-400">NPCs</div>
            </div>
            
            <div class="card text-center">
                <div class="text-2xl font-bold text-red-500 mb-1">
                    {$campaigns.reduce((total, c) => total + (c.stats?.location_count || 0), 0)}
                </div>
                <div class="text-sm text-gray-400">Locations</div>
            </div>
            
            <div class="card text-center">
                <div class="text-2xl font-bold text-red-500 mb-1">
                    {$campaigns.reduce((total, c) => total + (c.stats?.plot_hook_count || 0), 0)}
                </div>
                <div class="text-sm text-gray-400">Plot Hooks</div>
            </div>
        </div>
    {/if}
</div>

{#if showCreateModal}
    <CreateCampaignModal
        on:close={() => showCreateModal = false}
        on:created={handleCampaignCreated}
    />
{/if}