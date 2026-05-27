// API 基础配置
const API_BASE = '/api';

// 通用请求函数
async function request(url, options = {}) {
    try {
        const response = await fetch(API_BASE + url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || '请求失败');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// 认证相关
const authAPI = {
    register: (data) => request('/auth/register', {
        method: 'POST',
        body: JSON.stringify(data)
    }),
    
    login: (data) => request('/auth/login', {
        method: 'POST',
        body: JSON.stringify(data)
    }),
    
    logout: () => request('/auth/logout', {
        method: 'POST'
    }),
    
    getCurrentUser: () => request('/auth/current')
};

// 用户相关
const userAPI = {
    getProfile: () => request('/user/profile'),
    
    updateProfile: (data) => request('/user/profile', {
        method: 'PUT',
        body: JSON.stringify(data)
    }),
    
    changePassword: (data) => request('/user/password', {
        method: 'PUT',
        body: JSON.stringify(data)
    }),
    
    getAddresses: () => request('/user/address'),
    
    addAddress: (data) => request('/user/address', {
        method: 'POST',
        body: JSON.stringify(data)
    }),
    
    updateAddress: (id, data) => request(`/user/address/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
    }),
    
    deleteAddress: (id) => request(`/user/address/${id}`, {
        method: 'DELETE'
    })
};

// 商品相关
const productAPI = {
    getList: (params) => {
        const query = new URLSearchParams(params).toString();
        return request(`/product/list?${query}`);
    },
    
    getDetail: (id) => request(`/product/${id}`),
    
    create: (data) => request('/product/', {
        method: 'POST',
        body: JSON.stringify(data)
    }),
    
    update: (id, data) => request(`/product/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
    }),
    
    delete: (id) => request(`/product/${id}`, {
        method: 'DELETE'
    }),
    
    getSellerProducts: (params) => {
        const query = new URLSearchParams(params).toString();
        return request(`/product/seller/list?${query}`);
    },
    
    getCategories: () => request('/product/categories')
};

// 购物车相关
const cartAPI = {
    getCart: () => request('/cart/'),
    
    addToCart: (data) => request('/cart/', {
        method: 'POST',
        body: JSON.stringify(data)
    }),
    
    updateItem: (id, data) => request(`/cart/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
    }),
    
    removeItem: (id) => request(`/cart/${id}`, {
        method: 'DELETE'
    }),
    
    clearCart: () => request('/cart/clear', {
        method: 'DELETE'
    })
};

// 订单相关
const orderAPI = {
    create: (data) => request('/order/create', {
        method: 'POST',
        body: JSON.stringify(data)
    }),
    
    pay: (id) => request(`/order/pay/${id}`, {
        method: 'POST'
    }),
    
    ship: (id, data) => request(`/order/ship/${id}`, {
        method: 'POST',
        body: JSON.stringify(data)
    }),
    
    receive: (id) => request(`/order/receive/${id}`, {
        method: 'POST'
    }),
    
    cancel: (id) => request(`/order/cancel/${id}`, {
        method: 'POST'
    }),
    
    refund: (id, data) => request(`/order/refund/${id}`, {
        method: 'POST',
        body: JSON.stringify(data)
    }),
    
    approveRefund: (id) => request(`/order/refund/${id}/approve`, {
        method: 'POST'
    }),
    
    getBuyerOrders: (params) => {
        const query = new URLSearchParams(params).toString();
        return request(`/order/buyer/list?${query}`);
    },
    
    getSellerOrders: (params) => {
        const query = new URLSearchParams(params).toString();
        return request(`/order/seller/list?${query}`);
    },
    
    getDetail: (id) => request(`/order/${id}`),
    
    addReview: (id, data) => request(`/order/${id}/review`, {
        method: 'POST',
        body: JSON.stringify(data)
    })
};

// 管理员相关
const adminAPI = {
    getUsers: (params) => {
        const query = new URLSearchParams(params).toString();
        return request(`/admin/users?${query}`);
    },
    
    updateUserStatus: (id, data) => request(`/admin/users/${id}/status`, {
        method: 'PUT',
        body: JSON.stringify(data)
    }),
    
    deleteUser: (id) => request(`/admin/users/${id}`, {
        method: 'DELETE'
    }),
    
    getCategories: () => request('/admin/categories'),
    
    createCategory: (data) => request('/admin/categories', {
        method: 'POST',
        body: JSON.stringify(data)
    }),
    
    updateCategory: (id, data) => request(`/admin/categories/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
    }),
    
    deleteCategory: (id) => request(`/admin/categories/${id}`, {
        method: 'DELETE'
    }),
    
    getOrders: (params) => {
        const query = new URLSearchParams(params).toString();
        return request(`/admin/orders?${query}`);
    },
    
    getStatistics: () => request('/admin/statistics'),
    
    exportOrders: (params) => {
        const query = new URLSearchParams(params).toString();
        return request(`/admin/export/orders?${query}`);
    },
    
    getLogs: (params) => {
        const query = new URLSearchParams(params).toString();
        return request(`/admin/logs?${query}`);
    }
};
