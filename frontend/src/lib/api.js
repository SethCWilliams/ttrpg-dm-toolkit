import { auth } from './stores/auth.js';
import { get } from 'svelte/store';

const API_BASE = 'http://localhost:8000';

// Helper function to get auth headers
function getAuthHeaders() {
    const authState = get(auth);
    const headers = {
        'Content-Type': 'application/json'
    };
    
    if (authState.token) {
        headers['Authorization'] = `Bearer ${authState.token}`;
    }
    
    return headers;
}

// Generic API request function
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const config = {
        headers: getAuthHeaders(),
        ...options
    };

    try {
        const response = await fetch(url, config);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }

        // Handle empty responses
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        }
        
        return null;
    } catch (error) {
        console.error('API Request failed:', error);
        throw error;
    }
}

// Auth API calls
export const authAPI = {
    async register(userData) {
        return apiRequest('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    },

    async login(email, password) {
        const formData = new FormData();
        formData.append('username', email); // FastAPI expects username field
        formData.append('password', password);
        
        return apiRequest('/auth/login', {
            method: 'POST',
            headers: {}, // Don't include Content-Type for FormData
            body: formData
        });
    },

    async getMe() {
        return apiRequest('/auth/me');
    }
};

// Campaign API calls
export const campaignAPI = {
    async getCampaigns() {
        return apiRequest('/campaigns/');
    },

    async getCampaign(id) {
        return apiRequest(`/campaigns/${id}`);
    },

    async createCampaign(campaignData) {
        return apiRequest('/campaigns/', {
            method: 'POST',
            body: JSON.stringify(campaignData)
        });
    },

    async updateCampaign(id, campaignData) {
        return apiRequest(`/campaigns/${id}`, {
            method: 'PUT',
            body: JSON.stringify(campaignData)
        });
    },

    async deleteCampaign(id) {
        return apiRequest(`/campaigns/${id}`, {
            method: 'DELETE'
        });
    }
};

// NPC API calls
export const npcAPI = {
    async getNPCs(campaignId, params = {}) {
        const query = new URLSearchParams(params).toString();
        return apiRequest(`/campaigns/${campaignId}/npcs?${query}`);
    },

    async getNPC(campaignId, npcId) {
        return apiRequest(`/campaigns/${campaignId}/npcs/${npcId}`);
    },

    async createNPC(campaignId, npcData) {
        return apiRequest(`/campaigns/${campaignId}/npcs`, {
            method: 'POST',
            body: JSON.stringify(npcData)
        });
    },

    async updateNPC(campaignId, npcId, npcData) {
        return apiRequest(`/campaigns/${campaignId}/npcs/${npcId}`, {
            method: 'PUT',
            body: JSON.stringify(npcData)
        });
    },

    async deleteNPC(campaignId, npcId) {
        return apiRequest(`/campaigns/${campaignId}/npcs/${npcId}`, {
            method: 'DELETE'
        });
    },

    async getNPCRelationships(campaignId, npcId) {
        return apiRequest(`/campaigns/${campaignId}/npcs/${npcId}/relationships`);
    },

    async updateNPCRelationships(campaignId, npcId, relationships) {
        return apiRequest(`/campaigns/${campaignId}/npcs/${npcId}/relationships`, {
            method: 'PUT',
            body: JSON.stringify(relationships)
        });
    }
};

// Location API calls
export const locationAPI = {
    async getLocations(campaignId, params = {}) {
        const query = new URLSearchParams(params).toString();
        return apiRequest(`/campaigns/${campaignId}/locations?${query}`);
    },

    async getLocation(campaignId, locationId) {
        return apiRequest(`/campaigns/${campaignId}/locations/${locationId}`);
    },

    async createLocation(campaignId, locationData) {
        return apiRequest(`/campaigns/${campaignId}/locations`, {
            method: 'POST',
            body: JSON.stringify(locationData)
        });
    },

    async updateLocation(campaignId, locationId, locationData) {
        return apiRequest(`/campaigns/${campaignId}/locations/${locationId}`, {
            method: 'PUT',
            body: JSON.stringify(locationData)
        });
    },

    async deleteLocation(campaignId, locationId) {
        return apiRequest(`/campaigns/${campaignId}/locations/${locationId}`, {
            method: 'DELETE'
        });
    },

    async getLocationTemplateFields(campaignId) {
        return apiRequest(`/campaigns/${campaignId}/locations/templates/fields`);
    }
};