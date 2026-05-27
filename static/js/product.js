// 加载商品列表页
async function loadProductsPage(params = {}) {
    try {
        // 加载分类选项
        const categoriesData = await productAPI.getCategories();
        const categoryFilter = document.getElementById('categoryFilter');
        categoryFilter.innerHTML = '<option value="">全部分类</option>' + 
            categoriesData.categories.map(cat => 
                `<option value="${cat.name}" ${params.category === cat.name ? 'selected' : ''}>${cat.name}</option>`
            ).join('');
        
        // 获取筛选参数
        const minPriceInput = document.getElementById('minPrice');
        const maxPriceInput = document.getElementById('maxPrice');
        const sortBySelect = document.getElementById('sortBy');
        
        // 设置筛选值
        if (params.min_price !== undefined && minPriceInput) {
            minPriceInput.value = params.min_price;
        }
        if (params.max_price !== undefined && maxPriceInput) {
            maxPriceInput.value = params.max_price;
        }
        if (params.sort_by !== undefined && sortBySelect) {
            sortBySelect.value = params.sort_by;
        }
        
        // 构建查询参数
        const queryParams = {
            page: params.page || 1,
            limit: 12,
            keyword: params.keyword || '',
            category: params.category || categoryFilter?.value || '',
            min_price: params.min_price || minPriceInput?.value || '',
            max_price: params.max_price || maxPriceInput?.value || '',
            sort_by: params.sort_by || sortBySelect?.value || 'created_at',
            order: 'desc'
        };
        
        console.log('查询参数:', queryParams); // 调试信息
        
        // 加载商品
        const data = await productAPI.getList(queryParams);
        console.log('返回商品数:', data.products.length, '总数:', data.total); // 调试信息
        renderProducts(data.products, 'productsList');
        renderPagination(data, 'productsPagination', (pageParams) => {
            loadProductsPage({ ...queryParams, ...pageParams });
        });
    } catch (error) {
        console.error('加载商品列表失败:', error);
        document.getElementById('productsList').innerHTML = '<p style="text-align: center; color: #e74c3c;">加载失败，请刷新重试</p>';
    }
}

// 筛选商品
function filterProducts() {
    const params = {
        category: document.getElementById('categoryFilter').value,
        min_price: document.getElementById('minPrice').value,
        max_price: document.getElementById('maxPrice').value,
        sort_by: document.getElementById('sortBy').value,
        page: 1
    };
    loadProductsPage(params);
}

// 显示商品详情
async function showProductDetail(productId) {
    try {
        const data = await productAPI.getDetail(productId);
        const product = data.product;
        
        const html = `
            <div class="detail-layout">
                <div class="detail-images">
                    <img src="${product.images[0] || '/placeholder.jpg'}" alt="${product.name}">
                </div>
                <div class="detail-info">
                    <h2>${product.name}</h2>
                    <div class="detail-price">¥${product.price.toFixed(2)}</div>
                    <div class="detail-meta">
                        <div>销量: ${product.sales}</div>
                        <div>库存: ${product.stock}</div>
                        <div>评分: ${product.rating || 0}</div>
                    </div>
                    <div class="detail-seller">
                        <p>卖家: ${product.seller_name}</p>
                    </div>
                    <div class="detail-actions">
                        <button class="btn-primary" onclick="addToCart('${product.id}')">加入购物车</button>
                        <button class="btn-secondary" onclick="buyNow('${product.id}')">立即购买</button>
                    </div>
                </div>
            </div>
            <div class="detail-description">
                <h3>商品详情</h3>
                <p>${product.description || '暂无详情'}</p>
            </div>
            <div class="detail-reviews">
                <h3>用户评价 (${product.reviews?.length || 0})</h3>
                <div class="reviews-list">
                    ${product.reviews?.map(review => `
                        <div class="review-item" style="padding: 15px 0; border-bottom: 1px solid #ecf0f1;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                                <strong>${review.buyer_name}</strong>
                                <span style="color: #f39c12;">${'★'.repeat(review.rating)}${'☆'.repeat(5-review.rating)}</span>
                            </div>
                            <p>${review.comment}</p>
                            <small style="color: #7f8c8d;">${review.created_at}</small>
                        </div>
                    `).join('') || '<p style="color: #7f8c8d;">暂无评价</p>'}
                </div>
            </div>
        `;
        
        document.getElementById('productDetail').innerHTML = html;
        showPage('productDetail');
    } catch (error) {
        alert('加载商品详情失败');
        console.error(error);
    }
}

// 加入购物车
async function addToCart(productId) {
    if (!currentUser) {
        alert('请先登录');
        showPage('login');
        return;
    }
    
    try {
        await cartAPI.addToCart({ product_id: productId, quantity: 1 });
        alert('已添加到购物车');
        loadCartCount();
    } catch (error) {
        alert(error.message || '添加失败');
    }
}

// 立即购买
async function buyNow(productId) {
    if (!currentUser) {
        alert('请先登录');
        showPage('login');
        return;
    }
    
    try {
        await cartAPI.addToCart({ product_id: productId, quantity: 1 });
        showPage('cart');
    } catch (error) {
        alert(error.message || '操作失败');
    }
}

// 渲染分页
function renderPagination(data, containerId, callback) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const { page, pages } = data;
    
    if (pages <= 1) {
        container.innerHTML = '';
        return;
    }
    
    let html = '';
    
    if (page > 1) {
        html += `<button onclick="loadPage(${page - 1})">上一页</button>`;
    }
    
    for (let i = 1; i <= Math.min(pages, 10); i++) {
        html += `<button class="${i === page ? 'active' : ''}" onclick="loadPage(${i})">${i}</button>`;
    }
    
    if (page < pages) {
        html += `<button onclick="loadPage(${page + 1})">下一页</button>`;
    }
    
    container.innerHTML = html;
    
    window.loadPage = (pageNum) => {
        callback({ page: pageNum });
    };
}
