const API_BASE_URL = 'http://localhost:8000/api';

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

        const data = await response.json();
        if (!response.ok) {
            console.error('API Error:', data);
            throw new Error(data.detail || 'Xatolik yuz berdi');
        }
        return data;
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
