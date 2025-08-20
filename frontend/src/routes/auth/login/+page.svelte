<script>
    import { auth } from '$lib/stores/auth.js';
    import { authAPI } from '$lib/api.js';
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';

    let email = '';
    let password = '';
    let loading = false;
    let error = '';

    // Redirect if already logged in
    onMount(() => {
        if ($auth.user) {
            goto('/dashboard');
        }
    });

    async function handleLogin() {
        if (!email || !password) {
            error = 'Please fill in all fields';
            return;
        }

        loading = true;
        error = '';

        try {
            const response = await authAPI.login(email, password);
            auth.login(response.user, response.access_token);
            goto('/dashboard');
        } catch (err) {
            error = err.message || 'Login failed';
        } finally {
            loading = false;
        }
    }

    function handleKeydown(event) {
        if (event.key === 'Enter') {
            handleLogin();
        }
    }
</script>

<svelte:head>
    <title>Login - DM Toolkit</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
        <div class="text-center">
            <h2 class="text-3xl font-bold text-red-600">
                Sign in to your account
            </h2>
            <p class="mt-2 text-gray-400">
                Or <a href="/auth/register" class="text-red-500 hover:text-red-400">create a new account</a>
            </p>
        </div>

        <div class="card">
            <form on:submit|preventDefault={handleLogin} class="space-y-6">
                {#if error}
                    <div class="bg-red-900 border border-red-700 text-red-100 px-4 py-3 rounded">
                        {error}
                    </div>
                {/if}

                <div>
                    <label for="email" class="block text-sm font-medium text-gray-300 mb-2">
                        Email address
                    </label>
                    <input
                        id="email"
                        type="email"
                        bind:value={email}
                        on:keydown={handleKeydown}
                        class="input w-full"
                        placeholder="Enter your email"
                        required
                    />
                </div>

                <div>
                    <label for="password" class="block text-sm font-medium text-gray-300 mb-2">
                        Password
                    </label>
                    <input
                        id="password"
                        type="password"
                        bind:value={password}
                        on:keydown={handleKeydown}
                        class="input w-full"
                        placeholder="Enter your password"
                        required
                    />
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    class="w-full btn btn-primary py-3 {loading ? 'opacity-50 cursor-not-allowed' : ''}"
                >
                    {loading ? 'Signing in...' : 'Sign in'}
                </button>
            </form>
        </div>
    </div>
</div>