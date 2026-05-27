// 全局状态
let currentUser = null;
let currentPage = 'home';

// 页面初始化
document.addEventListener('DOMContentLoaded', async () => {
    await checkAuth();
    loadHomePage();
    
    // 监听浏览器前进/后退按钮
    window.addEventListener('popstate', handlePopState);
});

// 处理浏览器前进/后退
function handlePopState(event) {
    const hash = window.location.hash.slice(1) || 'home';
    showPage(hash, false); // false 表示不添加历史记录
}

// 检查登录状态
async function checkAuth() {
    try {
        const data = await authAPI.getCurrentUser();
        currentUser = data.user;
        updateNavbar();
        loadCartCount();
    } catch (error) {
        currentUser = null;
        updateNavbar();
    }
}

// 更新导航栏
function updateNavbar() {
    const navUser = document.getElementById('navUser');
    const navUserInfo = document.getElementById('navUserInfo');
    const sellerLink = document.getElementById('sellerLink');
    const adminLink = document.getElementById('adminLink');
    
    if (currentUser) {
        navUser.style.display = 'none';
        navUserInfo.style.display = 'flex';
        document.getElementById('username').textContent = currentUser.username;
        
        // 根据角色显示/隐藏菜单
        // 只有卖家显示卖家中心，管理员不显示
        if (currentUser.role === 'seller') {
            sellerLink.style.display = 'block';
        } else {
            sellerLink.style.display = 'none';
        }
        
        // 只有管理员显示管理后台
        if (currentUser.role === 'admin') {
            adminLink.style.display = 'block';
        } else {
            adminLink.style.display = 'none';
        }
    } else {
        navUser.style.display = 'flex';
        navUserInfo.style.display = 'none';
        sellerLink.style.display = 'none';
        adminLink.style.display = 'none';
    }
}

// 页面切换
function showPage(pageName, addToHistory = true) {
    // 隐藏所有页面
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    // 显示目标页面
    const targetPage = document.getElementById(pageName + 'Page');
    if (targetPage) {
        targetPage.classList.add('active');
        currentPage = pageName;
        
        // 更新URL（添加到历史记录）
        if (addToHistory) {
            window.history.pushState({ page: pageName }, '', `#${pageName}`);
        }
        
        // 加载页面内容
        switch(pageName) {
            case 'home':
                loadHomePage();
                break;
            case 'products':
                loadProductsPage();
                break;
            case 'cart':
                if (!currentUser) {
                    showPage('login');
                    showWarning('请先登录');
                    return;
                }
                loadCartPage();
                break;
            case 'orders':
                if (!currentUser) {
                    showPage('login');
                    showWarning('请先登录');
                    return;
                }
                loadOrdersPage();
                break;
            case 'profile':
                if (!currentUser) {
                    showPage('login');
                    showWarning('请先登录');
                    return;
                }
                loadProfilePage();
                break;
            case 'seller':
                if (!currentUser || currentUser.role !== 'seller') {
                    showWarning('权限不足');
                    return;
                }
                loadSellerPage();
                break;
            case 'admin':
                if (!currentUser || currentUser.role !== 'admin') {
                    showWarning('权限不足');
                    return;
                }
                loadAdminPage();
                break;
        }
    }
}

// 加载首页
async function loadHomePage() {
    try {
        // 加载分类
        const categoriesData = await productAPI.getCategories();
        const categoriesHtml = categoriesData.categories.slice(0, 5).map(cat => `
            <div class="category-card" onclick="filterByCategory('${cat.name}')">
                <h4>${cat.name}</h4>
                <p>${cat.description}</p>
            </div>
        `).join('');
        document.getElementById('homeCategories').innerHTML = categoriesHtml;
        
        // 加载热门商品
        const productsData = await productAPI.getList({ limit: 8, sort_by: 'sales', order: 'desc' });
        renderProducts(productsData.products, 'homeProducts');
    } catch (error) {
        console.error('加载首页失败:', error);
    }
}

// 渲染商品列表
function renderProducts(products, containerId) {
    const container = document.getElementById(containerId);
    if (!products || products.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #7f8c8d;">暂无商品</p>';
        return;
    }
    
    const html = products.map(product => `
        <div class="product-card" onclick="showProductDetail('${product.id}')">
            <img src="${product.images[0] || '/placeholder.jpg'}" alt="${product.name}" class="product-image">
            <div class="product-info">
                <div class="product-name">${product.name}</div>
                <div class="product-price">¥${product.price.toFixed(2)}</div>
                <div class="product-meta">
                    <span>销量: ${product.sales}</span>
                    <span>评分: ${product.rating || 0}</span>
                </div>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

// 搜索商品
function searchProducts() {
    const keyword = document.getElementById('searchInput').value.trim();
    if (!keyword) {
        alert('请输入搜索关键词');
        return;
    }
    showPage('products');
    setTimeout(() => {
        loadProductsPage({ keyword: keyword });
    }, 100);
}

// 按分类筛选
function filterByCategory(category) {
    showPage('products');
    // 等待页面切换完成后再设置筛选条件
    setTimeout(() => {
        const categoryFilter = document.getElementById('categoryFilter');
        if (categoryFilter) {
            categoryFilter.value = category;
        }
        loadProductsPage({ category: category });
    }, 100);
}

// 登录
async function login(event) {
    event.preventDefault();
    
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const data = await authAPI.login({ username, password });
        alert('登录成功');
        await checkAuth();
        showPage('home');
    } catch (error) {
        alert(error.message || '登录失败');
    }
}

// 注册
async function register(event) {
    event.preventDefault();
    
    const username = document.getElementById('regUsername').value;
    const email = document.getElementById('regEmail').value;
    const phone = document.getElementById('regPhone').value;
    const password = document.getElementById('regPassword').value;
    const role = document.getElementById('regRole').value;
    
    try {
        await authAPI.register({ username, email, phone, password, role });
        alert('注册成功，请登录');
        showPage('login');
    } catch (error) {
        alert(error.message || '注册失败');
    }
}

// 退出登录
async function logout() {
    try {
        await authAPI.logout();
        currentUser = null;
        updateNavbar();
        showPage('home');
        alert('已退出登录');
    } catch (error) {
        console.error('退出失败:', error);
    }
}
