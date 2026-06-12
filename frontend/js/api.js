// Use relative API base so the frontend works behind a reverse-proxy or different host
const API_BASE_URL = '/api';

const API = {
    async request(endpoint, options = {}) {
        const token = localStorage.getItem('access_token');
        const headers = {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
            ...options.headers
        };

        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers
        });

        if (response.status === 401) {
            localStorage.removeItem('access_token');
            if (window.location.pathname !== '/index.html' && window.location.pathname !== '/') {
                window.location.href = 'index.html';
            }
        }

        // Try to parse JSON, but if the server returned HTML (eg. nginx welcome page)
        // fall back to returning the text for easier debugging.
        const contentType = response.headers.get('content-type') || '';
        if (contentType.includes('application/json')) {
            const data = await response.json();
            if (!response.ok) {
                console.error('API Error:', data);
                throw new Error(data.detail || 'Xatolik yuz berdi');
            }
            return data;
        } else {
            const text = await response.text();
            console.error('Non-JSON response from API:', text);
            throw new Error('Server returned non-JSON response: ' + text.slice(0, 200));
        }
    },

    async login(username, password) {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Login xatosi');
        return data;
    },

    // CRM
    getCustomers: () => API.request('/crm/customers'),
    createCustomer: (data) => API.request('/crm/customers', { method: 'POST', body: JSON.stringify(data) }),

    // ERP
    getOrders: () => API.request('/erp/orders'),
    
    // WMS
    getProducts: () => API.request('/wms/products'),
    getInventory: () => API.request('/wms/inventory'),

    // Dashboard
    getStats: () => API.request('/reports/dashboard')
};

function showNotification(message, type = 'success') {
    const container = document.getElementById('notification-container');
    const div = document.createElement('div');
    div.className = `notification ${type}`;
    div.textContent = message;
    container.appendChild(div);
    
    setTimeout(() => {
        div.style.opacity = '0';
        setTimeout(() => div.remove(), 300);
    }, 3000);
}

// Expose API on the global window for inline scripts that expect `API`.
try {
    if (typeof window !== 'undefined') window.API = API;
} catch (e) {}
