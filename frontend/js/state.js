// Application State Management
class AppState {
    constructor() {
        this.state = {
            instruments: [],
            ownerships: [],
            rentals: [],
            currentInstrument: null,
            filters: {},
            loading: false,
        };
        this.listeners = [];
    }

    subscribe(callback) {
        this.listeners.push(callback);
    }

    getState() {
        return this.state;
    }

    setState(updates) {
        this.state = { ...this.state, ...updates };
        this.notify();
    }

    notify() {
        this.listeners.forEach(cb => cb(this.state));
    }

    setLoading(loading) {
        this.setState({ loading });
        const overlay = document.getElementById('loadingOverlay');
        if (loading) {
            overlay.classList.add('active');
        } else {
            overlay.classList.remove('active');
        }
    }
}

// Create global state instance
const appState = new AppState();
