// API Service Layer
class APIService {
    constructor() {
        this.baseURL = 'http://127.0.0.1:5000/api';
        this.token = localStorage.getItem('token');
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('token', token);
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem('token');
    }

    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json',
        };
        if (includeAuth && this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        return headers;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            ...options,
            headers: {
                ...this.getHeaders(options.auth !== false),
                ...options.headers,
            },
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                throw new Error(data.message || `HTTP Error: ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    }

    // Auth endpoints
    async register(userData) {
        return this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData),
            auth: false,
        });
    }

    async login(credentials) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify(credentials),
            auth: false,
        });
        if (data.access_token) {
            this.setToken(data.access_token);
        }
        return data;
    }

    async getProfile() {
        return this.request('/auth/profile');
    }

    // Instrument endpoints
    async getInstruments(filters = {}) {
        const params = new URLSearchParams(filters);
        return this.request(`/instruments?${params}`);
    }

    async getInstrument(id) {
        return this.request(`/instruments/${id}`);
    }

    async createInstrument(data) {
        return this.request('/instruments', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    // Instrument Ownership endpoints
    async getAvailableInstruments() {
        return this.request('/instru-ownership');
    }

    async createOwnership(data) {
        return this.request('/instru-ownership', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async getOwnership(id) {
        return this.request(`/instru-ownership/${id}`);
    }

    // Rental endpoints
    async createRental(data) {
        return this.request('/rentals', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async getRentals() {
        return this.request('/rentals');
    }

    async returnRental(id) {
        return this.request(`/rentals/${id}/return`, {
            method: 'POST',
        });
    }

    // Dashboard endpoints
    async getDashboardStats() {
        return this.request('/dashboard/stats');
    }

    async getRenterDashboard() {
        return this.request('/dashboard/renter');
    }

    async getOwnerDashboard() {
        return this.request('/dashboard/owner');
    }

    // User endpoints
    async getUsers() {
        return this.request('/users');
    }

    async getUser(id) {
        return this.request(`/users/${id}`);
    }
}

// Create global API instance
const api = new APIService();
