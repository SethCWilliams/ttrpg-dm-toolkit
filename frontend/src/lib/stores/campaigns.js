import { writable } from 'svelte/store';

// Current campaign store
export const currentCampaign = writable(null);

// All campaigns store
export const campaigns = writable([]);

// Loading states
export const campaignsLoading = writable(false);