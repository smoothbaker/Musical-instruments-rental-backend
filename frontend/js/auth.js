// Authentication Management
class AuthManager {
    constructor() {
        this.currentUser = null;
        this.listeners = [];
    }

    subscribe(callback) {
        this.listeners.push(callback);
    }

    notify() {
        this.listeners.forEach(cb => cb(this.currentUser));
    }

    async init() {
        const token = localStorage.getItem('token');
        if (token) {
            try {
                const user = await api.getProfile();
                this.setUser(user);
            } catch (error) {
                this.logout();
            }
        }
    }

    setUser(user) {
        this.currentUser = user;
        this.notify();
    }

    getUser() {
        return this.currentUser;
    }

    isAuthenticated() {
        return !!this.currentUser;
    }

    isOwner() {
        return this.currentUser?.user_type === 'owner';
    }

    isRenter() {
        return this.currentUser?.user_type === 'renter';
    }

    async login(email, password) {
        const data = await api.login({ email, password });
        this.setUser(data.user);
        return data;
    }

    async register(userData) {
        const user = await api.register(userData);
        // Auto-login after registration
        await this.login(userData.email, userData.password);
        return user;
    }

    logout() {
        this.currentUser = null;
        api.clearToken();
        this.notify();
        navigate('/');
    }
}

// Create global auth instance
const auth = new AuthManager();
