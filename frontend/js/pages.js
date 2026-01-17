// Page Rendering Functions

// Home Page
function renderHomePage() {
    return `
        <section class="hero-section">
            <div class="container hero-content">
                <h1 class="hero-title">Rent Musical Instruments with Ease</h1>
                <p class="hero-subtitle">Connect with instrument owners and renters in a trusted marketplace. Find your perfect instrument or list yours for rental.</p>
                <div class="flex justify-center gap-md mt-xl">
                    <a href="#/browse" class="btn btn-primary btn-lg">Browse Instruments</a>
                    ${!auth.isAuthenticated() ? '<a href="#/register" class="btn btn-secondary btn-lg">Get Started</a>' : ''}
                </div>
            </div>
        </section>
        
        <section class="page-section">
            <div class="container">
                <h2 class="text-center mb-xl">How It Works</h2>
                <div class="grid-3">
                    <div class="card text-center">
                        <div style="font-size: 3rem; margin-bottom: var(--spacing-md);">🔍</div>
                        <h3>Browse & Search</h3>
                        <p class="text-muted">Find the perfect instrument from our curated collection</p>
                    </div>
                    <div class="card text-center">
                        <div style="font-size: 3rem; margin-bottom: var(--spacing-md);">📅</div>
                        <h3>Book Your Rental</h3>
                        <p class="text-muted">Select your dates and confirm your booking instantly</p>
                    </div>
                    <div class="card text-center">
                        <div style="font-size: 3rem; margin-bottom: var(--spacing-md);">🎵</div>
                        <h3>Play & Enjoy</h3>
                        <p class="text-muted">Pick up your instrument and start making music</p>
                    </div>
                </div>
            </div>
        </section>
        
        ${auth.isAuthenticated() ? renderQuickStats() : ''}
    `;
}

async function renderQuickStats() {
    try {
        const stats = await api.getDashboardStats();
        const user = auth.getUser();

        if (user.user_type === 'renter') {
            return `
                <section class="page-section" style="background: var(--lightest);">
                    <div class="container">
                        <h2 class="text-center mb-xl">Your Stats</h2>
                        <div class="stats-grid">
                            ${createStatCard('Total Rentals', stats.statistics.total_rentals, '📦')}
                            ${createStatCard('Active', stats.statistics.active_rentals, '⚡')}
                            ${createStatCard('Total Spent', formatCurrency(stats.statistics.total_spent), '💰')}
                        </div>
                    </div>
                </section>
            `;
        } else {
            return `
                <section class="page-section" style="background: var(--lightest);">
                    <div class="container">
                        <h2 class="text-center mb-xl">Your Stats</h2>
                        <div class="stats-grid">
                            ${createStatCard('Instruments', stats.statistics.total_instruments, '🎸')}
                            ${createStatCard('Available', stats.statistics.available_instruments, '✓')}
                            ${createStatCard('Total Earned', formatCurrency(stats.statistics.total_earned), '💵')}
                        </div>
                    </div>
                </section>
            `;
        }
    } catch (error) {
        return '';
    }
}

// Browse Page
async function renderBrowsePage() {
    document.getElementById('app').innerHTML = `
        <section class="page-section">
            <div class="container">
                <h1 class="mb-xl">Browse Instruments</h1>
                <div id="instrumentsGrid" class="grid-3">
                    <div class="card"><div style="text-align:center; padding:2rem;">Loading...</div></div>
                </div>
            </div>
        </section>
    `;

    try {
        appState.setLoading(true);
        const ownerships = await api.getAvailableInstruments();

        const grid = document.getElementById('instrumentsGrid');

        if (ownerships.length === 0) {
            grid.innerHTML = `
                <div class="empty-state" style="grid-column: 1 / -1;">
                    <div class="empty-state-icon">🎵</div>
                    <h3 class="empty-state-title">No Instruments Available</h3>
                    <p class="empty-state-text">Check back later for new listings!</p>
                </div>
            `;
        } else {
            grid.innerHTML = ownerships.map(createInstrumentCard).join('');
        }
    } catch (error) {
        showToast(error.message, 'error');
        document.getElementById('instrumentsGrid').innerHTML = `
            <div class="empty-state" style="grid-column: 1 / -1;">
                <div class="empty-state-icon">⚠️</div>
                <h3 class="empty-state-title">Error Loading Instruments</h3>
                <p class="empty-state-text">${error.message}</p>
            </div>
        `;
    } finally {
        appState.setLoading(false);
    }
}

// Login Page
function renderLoginPage() {
    if (auth.isAuthenticated()) {
        navigate('/dashboard');
        return '';
    }

    return `
        <div class="auth-container">
            <div class="card auth-card">
                <div class="auth-header">
                    <h2>Welcome Back</h2>
                    <p class="text-muted">Login to your MusicRent account</p>
                </div>
                <form id="loginForm" onsubmit="handleLogin(event)">
                    <div class="form-group">
                        <label class="form-label required">Email</label>
                        <input type="email" class="form-input" name="email" required placeholder="your@email.com">
                    </div>
                    <div class="form-group">
                        <label class="form-label required">Password</label>
                        <input type="password" class="form-input" name="password" required placeholder="••••••••">
                    </div>
                    <button type="submit" class="btn btn-primary" style="width: 100%;">Login</button>
                </form>
                <div class="auth-toggle">
                    Don't have an account? <a href="#/register">Sign up</a>
                </div>
            </div>
        </div>
    `;
}

async function handleLogin(e) {
    e.preventDefault();
    const formData = new FormData(e.target);

    try {
        appState.setLoading(true);
        await auth.login(formData.get('email'), formData.get('password'));
        showToast('Login successful!', 'success');
        navigate('/dashboard');
    } catch (error) {
        showToast(error.message || 'Login failed', 'error');
    } finally {
        appState.setLoading(false);
    }
}

// Register Page
function renderRegisterPage() {
    if (auth.isAuthenticated()) {
        navigate('/dashboard');
        return '';
    }

    return `
        <div class="auth-container">
            <div class="card auth-card">
                <div class="auth-header">
                    <h2>Create Account</h2>
                    <p class="text-muted">Join MusicRent today</p>
                </div>
                <form id="registerForm" onsubmit="handleRegister(event)">
                    <div class="form-group">
                        <label class="form-label required">Full Name</label>
                        <input type="text" class="form-input" name="name" required placeholder="John Doe">
                    </div>
                    <div class="form-group">
                        <label class="form-label required">Email</label>
                        <input type="email" class="form-input" name="email" required placeholder="your@email.com">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Phone</label>
                        <input type="tel" class="form-input" name="phone" placeholder="+1 (555) 000-0000">
                    </div>
                    <div class="form-group">
                        <label class="form-label required">Password</label>
                        <input type="password" class="form-input" name="password" required minlength="6" placeholder="••••••••">
                    </div>
                    <div class="form-group">
                        <label class="form-label required">I want to</label>
                        <select class="form-select" name="user_type" required>
                            <option value="">Select an option</option>
                            <option value="renter">Rent instruments</option>
                            <option value="owner">List my instruments</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary" style="width: 100%;">Create Account</button>
                </form>
                <div class="auth-toggle">
                    Already have an account? <a href="#/login">Login</a>
                </div>
            </div>
        </div>
    `;
}

async function handleRegister(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = {
        name: formData.get('name'),
        email: formData.get('email'),
        phone: formData.get('phone'),
        password: formData.get('password'),
        user_type: formData.get('user_type')
    };

    try {
        appState.setLoading(true);
        await auth.register(data);
        showToast('Account created successfully!', 'success');
        navigate('/dashboard');
    } catch (error) {
        showToast(error.message || 'Registration failed', 'error');
    } finally {
        appState.setLoading(false);
    }
}

// Dashboard Page
async function renderDashboardPage() {
    if (!auth.isAuthenticated()) {
        navigate('/login');
        return '';
    }

    const user = auth.getUser();

    document.getElementById('app').innerHTML = `
        <section class="page-section">
            <div class="container">
                <div class="dashboard-header">
                    <h1 class="dashboard-title">Welcome back, ${user.name}!</h1>
                    <p class="text-muted">${user.user_type === 'owner' ? 'Manage your instruments and rentals' : 'Your recent activity'}</p>
                </div>
                <div id="dashboardContent">
                    <div style="text-align:center; padding:2rem;">Loading dashboard...</div>
                </div>
            </div>
        </section>
    `;

    try {
        appState.setLoading(true);

        if (user.user_type === 'renter') {
            await renderRenterDashboard();
        } else {
            await renderOwnerDashboard();
        }
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        appState.setLoading(false);
    }
}

async function renderRenterDashboard() {
    const [stats, rentals] = await Promise.all([
        api.getDashboardStats(),
        api.getRentals()
    ]);

    const content = document.getElementById('dashboardContent');
    content.innerHTML = `
        <div class="stats-grid mb-xl">
            ${createStatCard('Total Rentals', stats.statistics.total_rentals, '📦')}
            ${createStatCard('Active', stats.statistics.active_rentals, '⚡')}
            ${createStatCard('Completed', stats.statistics.completed_rentals, '✓')}
            ${createStatCard('Total Spent', formatCurrency(stats.statistics.total_spent), '💰')}
        </div>
        
        <div class="section-title">
            <h3>Your Rentals</h3>
            <a href="#/browse" class="btn btn-primary btn-sm">Browse More</a>
        </div>
        
        <div class="grid gap-md">
            ${rentals.length > 0 ?
            rentals.map(createRentalCard).join('') :
            '<div class="empty-state"><div class="empty-state-icon">🎵</div><h3>No Rentals Yet</h3><p>Start by browsing our instrument collection!</p><a href="#/browse" class="btn btn-primary mt-md">Browse Instruments</a></div>'}
        </div>
    `;
}

async function renderOwnerDashboard() {
    const stats = await api.getDashboardStats();

    const content = document.getElementById('dashboardContent');
    content.innerHTML = `
        <div class="stats-grid mb-xl">
            ${createStatCard('Instruments', stats.statistics.total_instruments, '🎸')}
            ${createStatCard('Available', stats.statistics.available_instruments, '✓')}
            ${createStatCard('Active Rentals', stats.statistics.active_rentals, '⚡')}
            ${createStatCard('Total Earned', formatCurrency(stats.statistics.total_earned), '💵')}
        </div>
        
        <div class="section-title">
            <h3>Quick Actions</h3>
        </div>
        
        <div class="grid-2 mb-xl">
            <button class="btn btn-primary btn-lg" onclick="showAddInstrumentModal()">
                + Add New Instrument
            </button>
            <a href="#/browse" class="btn btn-secondary btn-lg">
                View All Listings
            </a>
        </div>
        
        <div class="empty-state">
            <div class="empty-state-icon">📊</div>
            <h3>Owner Dashboard</h3>
            <p>Here you can manage your instruments and track your earnings</p>
        </div>
    `;
}

function showAddInstrumentModal() {
    const modalContent = `
        <div class="modal-header">
            <h2 class="modal-title">Add New Instrument</h2>
        </div>
        <div class="modal-body">
            <form id="addInstrumentForm" onsubmit="handleAddInstrument(event)">
                <div class="form-group">
                    <label class="form-label required">Instrument Name</label>
                    <input type="text" class="form-input" name="name" required placeholder="e.g., Yamaha Acoustic Guitar">
                </div>
                <div class="form-group">
                    <label class="form-label required">Category</label>
                    <select class="form-select" name="category" required>
                        <option value="">Select category</option>
                        <option value="guitar">Guitar</option>
                        <option value="piano">Piano</option>
                        <option value="drums">Drums</option>
                        <option value="violin">Violin</option>
                        <option value="saxophone">Saxophone</option>
                        <option value="trumpet">Trumpet</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Brand</label>
                    <input type="text" class="form-input" name="brand" placeholder="e.g., Yamaha">
                </div>
                <div class="form-group">
                    <label class="form-label">Model</label>
                    <input type="text" class="form-input" name="model" placeholder="e.g., FS800">
                </div>
                <div class="form-group">
                    <label class="form-label">Description</label>
                    <textarea class="form-textarea" name="description" placeholder="Describe your instrument..."></textarea>
                </div>
                <div class="form-group">
                    <label class="form-label required">Condition</label>
                    <select class="form-select" name="condition" required>
                        <option value="new">New</option>
                        <option value="good">Good</option>
                        <option value="fair">Fair</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label required">Daily Rate ($)</label>
                    <input type="number" class="form-input" name="daily_rate" required min="1" step="0.01" placeholder="25.00">
                </div>
                <div class="form-group">
                    <label class="form-label required">Location</label>
                    <input type="text" class="form-input" name="location" required placeholder="e.g., New York, NY">
                </div>
                <div class="modal-footer" style="border: none; padding: 0;">
                    <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                    <button type="submit" class="btn btn-primary">Add Instrument</button>
                </div>
            </form>
        </div>
    `;
    showModal(modalContent);
}

async function handleAddInstrument(e) {
    e.preventDefault();
    const formData = new FormData(e.target);

    try {
        appState.setLoading(true);

        // First create the instrument
        const instrument = await api.createInstrument({
            name: formData.get('name'),
            category: formData.get('category'),
            brand: formData.get('brand'),
            model: formData.get('model'),
            description: formData.get('description')
        });

        // Then create the ownership
        await api.createOwnership({
            instrument_id: instrument.id,
            condition: formData.get('condition'),
            daily_rate: parseFloat(formData.get('daily_rate')),
            location: formData.get('location')
        });

        showToast('Instrument added successfully!', 'success');
        closeModal();
        navigate('/dashboard');
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        appState.setLoading(false);
    }
}
