<script>
    import { auth } from '$lib/stores/auth.js';
    import { currentCampaign } from '$lib/stores/campaigns.js';
    import { goto } from '$app/navigation';

    function handleLogout() {
        auth.logout();
        goto('/auth/login');
    }
</script>

<nav class="navbar px-6 py-4">
    <div class="flex items-center justify-between max-w-7xl mx-auto">
        <!-- Logo -->
        <div class="flex items-center">
            <a href="/dashboard" class="text-2xl font-bold text-red-600">
                DM Toolkit
            </a>
        </div>

        <!-- Main Navigation -->
        {#if $auth.user}
            <div class="hidden md:flex items-center space-x-6">
                <a href="/dashboard" class="text-gray-300 hover:text-white transition-colors">
                    Dashboard
                </a>
                
                {#if $currentCampaign}
                    <a href="/campaigns/{$currentCampaign.id}/npcs" class="text-gray-300 hover:text-white transition-colors">
                        NPCs
                    </a>
                    <a href="/campaigns/{$currentCampaign.id}/locations" class="text-gray-300 hover:text-white transition-colors">
                        Locations
                    </a>
                    <a href="/campaigns/{$currentCampaign.id}/organizations" class="text-gray-300 hover:text-white transition-colors">
                        Organizations
                    </a>
                    <a href="/campaigns/{$currentCampaign.id}/plot-hooks" class="text-gray-300 hover:text-white transition-colors">
                        Plot Hooks
                    </a>
                    <a href="/campaigns/{$currentCampaign.id}/ideas" class="text-gray-300 hover:text-white transition-colors">
                        Ideas
                    </a>
                {/if}
            </div>

            <!-- User Menu -->
            <div class="flex items-center space-x-4">
                {#if $currentCampaign}
                    <span class="text-sm text-gray-400">
                        {$currentCampaign.name}
                    </span>
                {/if}
                
                <span class="text-gray-300">
                    {$auth.user.username}
                </span>
                
                <button 
                    on:click={handleLogout}
                    class="btn btn-secondary text-sm"
                >
                    Logout
                </button>
            </div>
        {:else}
            <!-- Unauthenticated state -->
            <div class="space-x-4">
                <a href="/auth/login" class="btn btn-secondary">
                    Login
                </a>
                <a href="/auth/register" class="btn btn-primary">
                    Register
                </a>
            </div>
        {/if}
    </div>
</nav>