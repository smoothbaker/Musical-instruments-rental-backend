// Main Application File - Router & Initialization

// Define routes
const routes = {
    '/': renderHomePage,
    '/browse': renderBrowsePage,
    '/login': renderLoginPage,
    '/register': renderRegisterPage,  // Fixed: was registerRegisterPage
    '/dashboard': renderDashboardPage,
};

// Router function
async function router() {
    const hash = window.location.hash.slice(1) || '/';
    const route = routes[hash] || routes['/'];

    // Update active nav link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${hash}`) {
            link.classList.add('active');
        }
    });

    // Render page
    const app = document.getElementById('app');

    if (typeof route === 'function') {
        const content = await route();
        if (content) {
            app.innerHTML = content;
        }
    } else {
        app.innerHTML = '<div class="container"><h1>404 - Page Not Found</h1></div>';
    }

    // Scroll to top
    window.scrollTo(0, 0);
}

// Navigate function
function navigate(path) {
    window.location.hash = path;
}

// Initialize app
async function initApp() {
    // Initialize auth
    await auth.init();

    // Render navigation
    renderNav();

    // Set up routing
    window.addEventListener('hashchange', router);

    // Initial route
    await router();

    console.log('🎵 MusicRent App Initialized');
}

// Start app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}
