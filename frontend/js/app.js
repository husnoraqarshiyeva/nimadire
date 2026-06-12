// Auth Check
function checkAuth() {
    if (!localStorage.getItem('access_token')) {
        if (window.location.pathname !== '/index.html' && window.location.pathname !== '/') {
            window.location.href = 'index.html';
        }
    }
}

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = 'index.html';
}

// User Info
function displayUserInfo() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const userNameElement = document.getElementById('user-name');
    if (userNameElement && user.email) {
        userNameElement.textContent = user.full_name || user.email.split('@')[0];
    }
}

// Document Ready behavior
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    displayUserInfo();
    
    // Initialize icons if lucide is present
    if (window.lucide) {
        lucide.createIcons();
    }
});
