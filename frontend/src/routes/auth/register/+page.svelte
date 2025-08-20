<script>
    import { auth } from '$lib/stores/auth.js';
    import { authAPI } from '$lib/api.js';
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';

    let email = '';
    let username = '';
    let password = '';
    let confirmPassword = '';
    let loading = false;
    let error = '';

    // Redirect if already logged in
    onMount(() => {
        if ($auth.user) {
            goto('/dashboard');
        }
    });

    async function handleRegister() {
        // Validation
        if (!email || !username || !password || !confirmPassword) {
            error = 'Please fill in all fields';
            return;
        }

        if (password !== confirmPassword) {
            error = 'Passwords do not match';
            return;
        }

        if (password.length < 6) {
            error = 'Password must be at least 6 characters long';
            return;
        }

        loading = true;
        error = '';

        try {
            await authAPI.register({ email, username, password });
            
            // Auto-login after registration
            const loginResponse = await authAPI.login(email, password);
            auth.login(loginResponse.user, loginResponse.access_token);
            goto('/dashboard');
        } catch (err) {
            error = err.message || 'Registration failed';
        } finally {
            loading = false;
        }
    }

    function handleKeydown(event) {
        if (event.key === 'Enter') {
            handleRegister();
        }
    }
</script>

<svelte:head>
    <title>Register - DM Toolkit</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
        <div class="text-center">
            <h2 class="text-3xl font-bold text-red-600">
                Create your account
            </h2>
            <p class="mt-2 text-gray-400">
                Or <a href="/auth/login" class="text-red-500 hover:text-red-400">sign in to existing account</a>
            </p>
        </div>

        <div class="card">
            <form on:submit|preventDefault={handleRegister} class="space-y-6">
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
                    <label for="username" class="block text-sm font-medium text-gray-300 mb-2">
                        Username
                    </label>
                    <input
                        id="username"
                        type="text"
                        bind:value={username}
                        on:keydown={handleKeydown}
                        class="input w-full"
                        placeholder="Choose a username"
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

                <div>
                    <label for="confirmPassword" class="block text-sm font-medium text-gray-300 mb-2">
                        Confirm Password
                    </label>
                    <input
                        id="confirmPassword"
                        type="password"
                        bind:value={confirmPassword}
                        on:keydown={handleKeydown}
                        class="input w-full"
                        placeholder="Confirm your password"
                        required
                    />
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    class="w-full btn btn-primary py-3 {loading ? 'opacity-50 cursor-not-allowed' : ''}"
                >
                    {loading ? 'Creating account...' : 'Create account'}
                </button>
            </form>
        </div>
    </div>
</div>