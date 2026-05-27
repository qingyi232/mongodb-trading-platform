// 加载卖家中心
function loadSellerPage() {
    showSellerTab('products');
}

// 切换卖家标签
function showSellerTab(tab) {
    // 更新菜单状态
    document.querySelectorAll('.seller-menu a').forEach(link => {
        link.classList.remove('active');
    });
    if (window.event?.target) {
        window.event.target.classList.add('active');
    }
    
    // 隐藏所有标签
    document.querySelectorAll('.seller-tab').forEach(tabEl => {
        tabEl.classList.remove('active');
    });
    
    // 显示目标标签
    const targetTab = document.getElementById('seller' + tab.charAt(0).toUpperCase() + tab.slice(1));
    if (targetTab) {
        targetTab.classList.add('active');
        
        // 加载标签内容
        switch(tab) {
            case 'products':
                loadSellerProducts();
                break;
            case 'orders':
                loadSellerOrders();
                break;
            case 'add':
                loadAddProductForm();
                break;
        }
    }
}

// 加载卖家商品列表
async function loadSellerProducts() {
    try {
        const data = await productAPI.getSellerProducts({ page: 1, limit: 20 });
        
        const html = `
            <h3>我的商品</h3>
            <table>
                <thead>
                    <tr>
                        <th>商品名称</th>
                        <th>分类</th>
                        <th>价格</th>
                        <th>库存</th>
                        <th>销量</th>
                        <th>状态</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.products.length === 0 ? '<tr><td colspan="7" style="text-align: center; color: #7f8c8d;">暂无商品</td></tr>' : 
                    data.products.map(product => `
                        <tr>
                            <td>${product.name}</td>
                            <td>${product.category}</td>
                            <td>¥${product.price.toFixed(2)}</td>
                            <td>${product.stock}</td>
                            <td>${product.sales}</td>
                            <td>${product.status === 'active' ? '在售' : '已下架'}</td>
                            <td>
                                <button class="btn btn-warning" onclick="editProduct('${product.id}')">编辑</button>
                                <button class="btn btn-danger" onclick="deleteProduct('${product.id}')">下架</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        document.getElementById('sellerProducts').innerHTML = html;
    } catch (error) {
        console.error('加载商品列表失败:', error);
    }
}

// 加载卖家订单
async function loadSellerOrders() {
    try {
        const data = await orderAPI.getSellerOrders({ page: 1, limit: 20 });
        
        const statusMap = {
            'pending_payment': '待支付',
            'paid': '待发货',
            'shipped': '待收货',
            'completed': '已完成',
            'cancelled': '已取消',
            'refund_pending': '退款中',
            'refunded': '已退款'
        };
        
        const html = `
            <h3>订单管理</h3>
            <table>
                <thead>
                    <tr>
                        <th>订单号</th>
                        <th>买家</th>
                        <th>金额</th>
                        <th>状态</th>
                        <th>创建时间</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.orders.length === 0 ? '<tr><td colspan="6" style="text-align: center; color: #7f8c8d;">暂无订单</td></tr>' :
                    data.orders.map(order => `
                        <tr>
                            <td>${order.order_no}</td>
                            <td>${order.buyer_name}</td>
                            <td>¥${order.total_amount.toFixed(2)}</td>
                            <td>${statusMap[order.status]}</td>
                            <td>${order.created_at}</td>
                            <td>
                                ${order.status === 'paid' ? `
                                    <button class="btn btn-success" onclick="shipOrder('${order.id}')">发货</button>
                                ` : ''}
                                ${order.status === 'refund_pending' ? `
                                    <button class="btn btn-warning" onclick="approveRefund('${order.id}')">同意退款</button>
                                ` : ''}
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        document.getElementById('sellerOrders').innerHTML = html;
    } catch (error) {
        console.error('加载订单失败:', error);
    }
}

// 发货
async function shipOrder(orderId) {
    showPrompt('请输入物流单号：', '', async (trackingNo) => {
        if (!trackingNo || !trackingNo.trim()) {
            showWarning('请输入物流单号');
            return;
        }
        
        try {
            await orderAPI.ship(orderId, { tracking_no: trackingNo.trim() });
            showSuccess('发货成功');
            loadSellerOrders();
        } catch (error) {
            showError(error.message || '发货失败');
        }
    });
}

// 同意退款
async function approveRefund(orderId) {
    if (!(await confirmAsync('确定同意退款吗？'))) return;
    
    try {
        await orderAPI.approveRefund(orderId);
        showSuccess('退款已批准');
        loadSellerOrders();
    } catch (error) {
        showError(error.message || '操作失败');
    }
}

// 加载发布商品表单
async function loadAddProductForm() {
    try {
        const categoriesData = await productAPI.getCategories();
        
        const html = `
            <h3>发布商品</h3>
            <form onsubmit="saveProduct(event)" style="max-width: 600px;">
                <input type="hidden" id="productId">
                <div class="form-group">
                    <label>商品名称</label>
                    <input type="text" id="productName" required>
                </div>
                <div class="form-group">
                    <label>分类</label>
                    <select id="productCategory" required>
                        <option value="">请选择分类</option>
                        ${categoriesData.categories.map(cat => 
                            `<option value="${cat.name}">${cat.name}</option>`
                        ).join('')}
                    </select>
                </div>
                <div class="form-group">
                    <label>价格</label>
                    <input type="number" id="productPrice" step="0.01" min="0" required>
                </div>
                <div class="form-group">
                    <label>库存</label>
                    <input type="number" id="productStock" min="0" required>
                </div>
                <div class="form-group">
                    <label>商品描述</label>
                    <textarea id="productDescription"></textarea>
                </div>
                <div class="form-group">
                    <label>商品图片URL（多个用逗号分隔）</label>
                    <input type="text" id="productImages" placeholder="https://example.com/image1.jpg,https://example.com/image2.jpg">
                </div>
                <button type="submit" class="btn btn-success">发布商品</button>
                <button type="button" class="btn" onclick="resetProductForm()">重置</button>
            </form>
        `;
        
        document.getElementById('sellerAdd').innerHTML = html;
    } catch (error) {
        console.error('加载表单失败:', error);
    }
}

// 保存商品
async function saveProduct(event) {
    event.preventDefault();
    
    const productId = document.getElementById('productId').value;
    const data = {
        name: document.getElementById('productName').value,
        category: document.getElementById('productCategory').value,
        price: parseFloat(document.getElementById('productPrice').value),
        stock: parseInt(document.getElementById('productStock').value),
        description: document.getElementById('productDescription').value,
        images: document.getElementById('productImages').value.split(',').map(s => s.trim()).filter(s => s)
    };
    
    try {
        if (productId) {
            await productAPI.update(productId, data);
            showSuccess('商品更新成功');
        } else {
            await productAPI.create(data);
            showSuccess('商品发布成功');
        }
        resetProductForm();
        showSellerTab('products');
    } catch (error) {
        showError(error.message || '操作失败');
    }
}

// 编辑商品
async function editProduct(productId) {
    try {
        const data = await productAPI.getDetail(productId);
        const product = data.product;
        
        showSellerTab('add');
        
        setTimeout(() => {
            document.getElementById('productId').value = product.id;
            document.getElementById('productName').value = product.name;
            document.getElementById('productCategory').value = product.category;
            document.getElementById('productPrice').value = product.price;
            document.getElementById('productStock').value = product.stock;
            document.getElementById('productDescription').value = product.description || '';
            document.getElementById('productImages').value = product.images.join(', ');
        }, 100);
    } catch (error) {
        showError('加载商品信息失败');
    }
}

// 删除商品
async function deleteProduct(productId) {
    if (!(await confirmAsync('确定要下架这个商品吗？'))) return;
    
    try {
        await productAPI.delete(productId);
        showSuccess('商品已下架');
        loadSellerProducts();
    } catch (error) {
        showError(error.message || '操作失败');
    }
}

// 重置表单
function resetProductForm() {
    document.getElementById('productId').value = '';
    document.getElementById('productName').value = '';
    document.getElementById('productCategory').value = '';
    document.getElementById('productPrice').value = '';
    document.getElementById('productStock').value = '';
    document.getElementById('productDescription').value = '';
    document.getElementById('productImages').value = '';
}
