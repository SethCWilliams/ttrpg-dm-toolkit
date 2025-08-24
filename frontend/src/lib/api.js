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

// Plot Hook API calls
export const plotHookAPI = {
    async getPlotHooks(campaignId, params = {}) {
        const query = new URLSearchParams(params).toString();
        return apiRequest(`/campaigns/${campaignId}/plot-hooks?${query}`);
    },

    async getPlotHook(campaignId, hookId) {
        return apiRequest(`/campaigns/${campaignId}/plot-hooks/${hookId}`);
    },

    async createPlotHook(campaignId, hookData) {
        return apiRequest(`/campaigns/${campaignId}/plot-hooks`, {
            method: 'POST',
            body: JSON.stringify(hookData)
        });
    },

    async updatePlotHook(campaignId, hookId, hookData) {
        return apiRequest(`/campaigns/${campaignId}/plot-hooks/${hookId}`, {
            method: 'PUT',
            body: JSON.stringify(hookData)
        });
    },

    async deletePlotHook(campaignId, hookId) {
        return apiRequest(`/campaigns/${campaignId}/plot-hooks/${hookId}`, {
            method: 'DELETE'
        });
    },

    async getPlotHookTemplateFields() {
        return apiRequest('/campaigns/0/plot-hooks/templates/fields');
    }
};

// Item API calls
export const itemAPI = {
    async getItems(campaignId, params = {}) {
        const query = new URLSearchParams(params).toString();
        return apiRequest(`/campaigns/${campaignId}/items?${query}`);
    },

    async getItem(campaignId, itemId) {
        return apiRequest(`/campaigns/${campaignId}/items/${itemId}`);
    },

    async createItem(campaignId, itemData) {
        return apiRequest(`/campaigns/${campaignId}/items`, {
            method: 'POST',
            body: JSON.stringify(itemData)
        });
    },

    async updateItem(campaignId, itemId, itemData) {
        return apiRequest(`/campaigns/${campaignId}/items/${itemId}`, {
            method: 'PUT',
            body: JSON.stringify(itemData)
        });
    },

    async deleteItem(campaignId, itemId) {
        return apiRequest(`/campaigns/${campaignId}/items/${itemId}`, {
            method: 'DELETE'
        });
    },

    async getItemTemplateFields() {
        return apiRequest('/campaigns/0/items/templates/fields');
    }
};

// Event API calls
export const eventAPI = {
    async getEvents(campaignId, params = {}) {
        const query = new URLSearchParams(params).toString();
        return apiRequest(`/campaigns/${campaignId}/events?${query}`);
    },

    async getEvent(campaignId, eventId) {
        return apiRequest(`/campaigns/${campaignId}/events/${eventId}`);
    },

    async createEvent(campaignId, eventData) {
        return apiRequest(`/campaigns/${campaignId}/events`, {
            method: 'POST',
            body: JSON.stringify(eventData)
        });
    },

    async updateEvent(campaignId, eventId, eventData) {
        return apiRequest(`/campaigns/${campaignId}/events/${eventId}`, {
            method: 'PUT',
            body: JSON.stringify(eventData)
        });
    },

    async deleteEvent(campaignId, eventId) {
        return apiRequest(`/campaigns/${campaignId}/events/${eventId}`, {
            method: 'DELETE'
        });
    }
};

// Ideas Inbox API calls
export const ideaAPI = {
    async getIdeas(campaignId, params = {}) {
        const query = new URLSearchParams(params).toString();
        return apiRequest(`/campaigns/${campaignId}/ideas?${query}`);
    },

    async getIdea(campaignId, ideaId) {
        return apiRequest(`/campaigns/${campaignId}/ideas/${ideaId}`);
    },

    async createIdea(campaignId, ideaData) {
        return apiRequest(`/campaigns/${campaignId}/ideas`, {
            method: 'POST',
            body: JSON.stringify(ideaData)
        });
    },

    async updateIdea(campaignId, ideaId, ideaData) {
        return apiRequest(`/campaigns/${campaignId}/ideas/${ideaId}`, {
            method: 'PUT',
            body: JSON.stringify(ideaData)
        });
    },

    async deleteIdea(campaignId, ideaId) {
        return apiRequest(`/campaigns/${campaignId}/ideas/${ideaId}`, {
            method: 'DELETE'
        });
    },

    async convertIdea(campaignId, ideaId, targetType) {
        return apiRequest(`/campaigns/${campaignId}/ideas/${ideaId}/convert?target_type=${targetType}`, {
            method: 'POST'
        });
    }
};

// Organization API calls
export const organizationAPI = {
    async getOrganizations(campaignId, params = {}) {
        const query = new URLSearchParams(params).toString();
        return apiRequest(`/campaigns/${campaignId}/organizations?${query}`);
    },

    async getOrganization(campaignId, organizationId) {
        return apiRequest(`/campaigns/${campaignId}/organizations/${organizationId}`);
    },

    async createOrganization(campaignId, organizationData) {
        return apiRequest(`/campaigns/${campaignId}/organizations`, {
            method: 'POST',
            body: JSON.stringify(organizationData)
        });
    },

    async updateOrganization(campaignId, organizationId, organizationData) {
        return apiRequest(`/campaigns/${campaignId}/organizations/${organizationId}`, {
            method: 'PUT',
            body: JSON.stringify(organizationData)
        });
    },

    async deleteOrganization(campaignId, organizationId) {
        return apiRequest(`/campaigns/${campaignId}/organizations/${organizationId}`, {
            method: 'DELETE'
        });
    },

    async getOrganizationTemplateFields() {
        return apiRequest('/campaigns/0/organizations/templates/fields');
    }
};

// Session Notes API calls
export const sessionNoteAPI = {
    async getSessionNotes(campaignId, params = {}) {
        const query = new URLSearchParams(params).toString();
        return apiRequest(`/campaigns/${campaignId}/sessions?${query}`);
    },

    async getSessionNote(campaignId, sessionNoteId) {
        return apiRequest(`/campaigns/${campaignId}/sessions/${sessionNoteId}`);
    },

    async createSessionNote(campaignId, sessionNoteData) {
        return apiRequest(`/campaigns/${campaignId}/sessions`, {
            method: 'POST',
            body: JSON.stringify(sessionNoteData)
        });
    },

    async updateSessionNote(campaignId, sessionNoteId, sessionNoteData) {
        return apiRequest(`/campaigns/${campaignId}/sessions/${sessionNoteId}`, {
            method: 'PUT',
            body: JSON.stringify(sessionNoteData)
        });
    },

    async deleteSessionNote(campaignId, sessionNoteId) {
        return apiRequest(`/campaigns/${campaignId}/sessions/${sessionNoteId}`, {
            method: 'DELETE'
        });
    },

    async duplicateSessionNote(campaignId, sessionNoteId) {
        return apiRequest(`/campaigns/${campaignId}/sessions/${sessionNoteId}/duplicate`, {
            method: 'POST'
        });
    }
};