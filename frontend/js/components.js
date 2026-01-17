// UI Components

// Render Navigation based on auth state
function renderNav() {
    const authNav = document.getElementById('authNav');

    if (auth.isAuthenticated()) {
        const user = auth.getUser();
        authNav.innerHTML = `
            <a href="#/dashboard" class="nav-link">Dashboard</a>
            <div class="dropdown">
                <button class="btn btn-sm btn-primary" onclick="toggleUserMenu(event)">
                    <span class="avatar">${getUserInitials(user.name)}</span>
                    ${user.name}
                </button>
                <div class="dropdown-menu" id="userMenu">
                    <span class="dropdown-item" style="font-weight:600; color: var(--gray);">
                        ${user.email}
                    </span>
                    <div class="dropdown-divider"></div>
                    <a href="#/profile" class="dropdown-item">Profile</a>
                    <a href="#" class="dropdown-item" onclick="handleLogout(event)">Logout</a>
                </div>
            </div>
        `;
    } else {
        authNav.innerHTML = `
            <a href="#/login" class="btn btn-secondary btn-sm">Login</a>
            <a href="#/register" class="btn btn-primary btn-sm">Sign Up</a>
        `;
    }
}

function toggleUserMenu(e) {
    e.stopPropagation();
    const menu = document.getElementById('userMenu');
    menu.classList.toggle('active');
}

function handleLogout(e) {
    e.preventDefault();
    auth.logout();
    showToast('Logged out successfully', 'success');
}

// Close dropdown when clicking outside
document.addEventListener('click', () => {
    const menus = document.querySelectorAll('.dropdown-menu');
    menus.forEach(menu => menu.classList.remove('active'));
});

// Instrument Card Component
function createInstrumentCard(ownership) {
    const instrument = ownership.instrument;
    const icon = getInstrumentIcon(instrument.category);

    return `
        <div class="card instrument-card" onclick="viewInstrument(${ownership.id})">
            ${ownership.is_available ?
            '<span class="badge-status">Available</span>' :
            '<span class="badge-status unavailable">Rented</span>'}
            <div class="instrument-card-img">${icon}</div>
            <div class="instrument-card-content">
                <h3>${instrument.name}</h3>
                <div class="instrument-card-meta">
                    <span>${instrument.brand || 'No brand'}</span>
                    <span>•</span>
                    <span>${instrument.category}</span>
                </div>
                <p class="text-muted">${ownership.condition || 'Good'} condition • ${ownership.location || 'Unknown location'}</p>
                <div class="card-footer">
                    <div class="instrument-card-price">
                        $${ownership.daily_rate}
                        <span>/day</span>
                    </div>
                    <button class="btn btn-primary btn-sm" onclick="event.stopPropagation(); ${auth.isRenter() ? `rentInstrument(${ownership.id})` : `viewInstrument(${ownership.id})`}">
                        ${auth.isRenter() ? 'Rent Now' : 'View'}
                    </button>
                </div>
            </div>
        </div>
    `;
}

// Rental Card Component
function createRentalCard(rental) {
    const instrument = rental.instru_ownership?.instrument;
    const icon = getInstrumentIcon(instrument?.category);
    const statusColors = {
        pending: 'warning',
        active: 'primary',
        completed: 'success',
        cancelled: 'danger'
    };

    return `
        <div class="card">
            <div class="flex items-center gap-md">
                <div class="instrument-card-img" style="width: 80px; height: 80px; font-size: 2rem;">
                    ${icon}
                </div>
                <div style="flex: 1;">
                    <h4>${instrument?.name || 'Unknown Instrument'}</h4>
                    <div class="instrument-card-meta">
                        <span>${formatDate(rental.start_date)} - ${formatDate(rental.end_date)}</span>
                    </div>
                    <div class="mt-sm">
                        <span class="badge badge-${statusColors[rental.status]}">${rental.status}</span>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div class="instrument-card-price mb-sm">
                        ${formatCurrency(rental.total_cost || 0)}
                    </div>
                    ${rental.status === 'active' && auth.isRenter() ?
            `<button class="btn btn-sm btn-success" onclick="returnRental(${rental.id})">Return</button>` : ''}
                </div>
            </div>
        </div>
    `;
}

// Stats Card Component
function createStatCard(label, value, icon) {
    return `
        <div class="card stat-card">
            <div class="stat-icon" style="font-size: 2rem; margin-bottom: var(--spacing-md);">${icon}</div>
            <div class="stat-value">${value}</div>
            <div class="stat-label">${label}</div>
        </div>
    `;
}

// View Instrument Details (simplified - opens modal)
async function viewInstrument(ownershipId) {
    try {
        appState.setLoading(true);
        const ownership = await api.getOwnership(ownershipId);
        const instrument = ownership.instrument;
        const icon = getInstrumentIcon(instrument.category);

        const modalContent = `
            <div class="modal-header">
                <h2 class="modal-title">${instrument.name}</h2>
            </div>
            <div class="modal-body">
                <div class="instrument-card-img" style="height: 250px; font-size: 6rem; margin-bottom: var(--spacing-lg);">
                    ${icon}
                </div>
                <div class="grid-2 gap-md mb-lg">
                    <div>
                        <strong>Brand:</strong> ${instrument.brand || 'N/A'}
                    </div>
                    <div>
                        <strong>Category:</strong> ${instrument.category}
                    </div>
                    <div>
                        <strong>Condition:</strong> ${ownership.condition}
                    </div>
                    <div>
                        <strong>Location:</strong> ${ownership.location}
                    </div>
                </div>
                <div class="mb-lg">
                    <h3 class="instrument-card-price mb-sm">
                        $${ownership.daily_rate} <span>/day</span>
                    </h3>
                    ${ownership.is_available ?
                '<span class="badge badge-success">Available</span>' :
                '<span class="badge badge-danger">Currently Rented</span>'}
                </div>
                ${instrument.description ? `<p>${instrument.description}</p>` : ''}
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closeModal()">Close</button>
                ${auth.isRenter() && ownership.is_available ?
                `<button class="btn btn-primary" onclick="closeModal(); rentInstrument(${ownershipId})">Rent Now</button>` : ''}
            </div>
        `;

        showModal(modalContent);
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        appState.setLoading(false);
    }
}

// Rent Instrument
function rentInstrument(ownershipId) {
    const modalContent = `
        <div class="modal-header">
            <h2 class="modal-title">Book Rental</h2>
        </div>
        <div class="modal-body">
            <form id="rentalForm" onsubmit="submitRental(event, ${ownershipId})">
                <div class="form-group">
                    <label class="form-label required">Start Date</label>
                    <input type="date" class="form-input" name="start_date" required 
                           min="${new Date().toISOString().split('T')[0]}">
                </div>
                <div class="form-group">
                    <label class="form-label required">End Date</label>
                    <input type="date" class="form-input" name="end_date" required 
                           min="${new Date().toISOString().split('T')[0]}">
                </div>
                <div class="modal-footer" style="border: none; padding: 0;">
                    <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                    <button type="submit" class="btn btn-primary">Confirm Booking</button>
                </div>
            </form>
        </div>
    `;
    showModal(modalContent);
}

async function submitRental(e, ownershipId) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = {
        instru_ownership_id: ownershipId,
        start_date: formData.get('start_date'),
        end_date: formData.get('end_date')
    };

    try {
        appState.setLoading(true);
        await api.createRental(data);
        showToast('Rental booked successfully!', 'success');
        closeModal();
        navigate('/dashboard');
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        appState.setLoading(false);
    }
}

async function returnRental(rentalId) {
    if (!confirm('Are you sure you want to return this instrument?')) return;

    try {
        appState.setLoading(true);
        await api.returnRental(rentalId);
        showToast('Instrument returned successfully!', 'success');
        navigate('/dashboard');
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        appState.setLoading(false);
    }
}

// Subscribe to auth changes to update nav
auth.subscribe(() => renderNav());
