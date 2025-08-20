import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import Cookies from 'js-cookie';

// Auth store
function createAuthStore() {
    const { subscribe, set, update } = writable({
        user: null,
        token: null,
        loading: true
    });

    return {
        subscribe,
        
        // Initialize auth state from cookies
        init() {
            if (browser) {
                const token = Cookies.get('auth_token');
                const userStr = Cookies.get('auth_user');
                
                if (token && userStr) {
                    try {
                        const user = JSON.parse(userStr);
                        set({ user, token, loading: false });
                    } catch (e) {
                        // Invalid stored data, clear it
                        this.logout();
                    }
                } else {
                    set({ user: null, token: null, loading: false });
                }
            }
        },

        // Login user
        login(user, token) {
            if (browser) {
                Cookies.set('auth_token', token, { expires: 1 }); // 1 day
                Cookies.set('auth_user', JSON.stringify(user), { expires: 1 });
            }
            set({ user, token, loading: false });
        },

        // Logout user
        logout() {
            if (browser) {
                Cookies.remove('auth_token');
                Cookies.remove('auth_user');
            }
            set({ user: null, token: null, loading: false });
        },

        // Update user info
        updateUser(user) {
            update(state => {
                if (browser && user) {
                    Cookies.set('auth_user', JSON.stringify(user), { expires: 1 });
                }
                return { ...state, user };
            });
        }
    };
}

export const auth = createAuthStore();