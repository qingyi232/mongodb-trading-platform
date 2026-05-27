// 加载管理后台
function loadAdminPage() {
    showAdminTab('dashboard');
}

// 切换管理标签
function showAdminTab(tab) {
    // 更新菜单状态
    document.querySelectorAll('.admin-menu a').forEach(link => {
        link.classList.remove('active');
    });
    if (window.event?.target) {
        window.event.target.classList.add('active');
    }
    
    // 隐藏所有标签
    document.querySelectorAll('.admin-tab').forEach(tabEl => {
        tabEl.classList.remove('active');
    });
    
    // 显示目标标签
    const targetTab = document.getElementById('admin' + tab.charAt(0).toUpperCase() + tab.slice(1));
    if (targetTab) {
        targetTab.classList.add('active');
        
        // 加载标签内容
        switch(tab) {
            case 'dashboard':
                loadDashboard();
                break;
            case 'users':
                loadAdminUsers();
                break;
            case 'categories':
                loadAdminCategories();
                break;
            case 'orders':
                loadAdminOrders();
                break;
            case 'logs':
                loadAdminLogs();
                break;
        }
    }
}

// 加载数据统计
async function loadDashboard() {
    try {
        const data = await adminAPI.getStatistics();
        
        const html = `
            <h3>数据统计</h3>
            <div class="stats-grid">
                <div class="stat-card">
                    <h4>总用户数</h4>
                    <div class="value">${data.users.total}</div>
                    <p style="color: #7f8c8d; margin-top: 10px;">买家: ${data.users.buyers} | 卖家: ${data.users.sellers}</p>
                </div>
                <div class="stat-card">
                    <h4>今日新增用户</h4>
                    <div class="value">${data.users.today_new}</div>
                </div>
                <div class="stat-card">
                    <h4>商品总数</h4>
                    <div class="value">${data.products.total}</div>
                </div>
                <div class="stat-card">
                    <h4>订单总数</h4>
                    <div class="value">${data.orders.total}</div>
                    <p style="color: #7f8c8d; margin-top: 10px;">已完成: ${data.orders.completed}</p>
                </div>
                <div class="stat-card">
                    <h4>总销售额</h4>
                    <div class="value">¥${data.sales.total.toFixed(2)}</div>
                </div>
                <div class="stat-card">
                    <h4>今日销售额</h4>
                    <div class="value">¥${data.sales.today.toFixed(2)}</div>
                </div>
            </div>
            
            <h3 style="margin-top: 40px;">热门商品排行</h3>
            <table>
                <thead>
                    <tr>
                        <th>排名</th>
                        <th>商品名称</th>
                        <th>分类</th>
                        <th>价格</th>
                        <th>销量</th>
                        <th>评分</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.top_products.map((product, index) => `
                        <tr>
                            <td>${index + 1}</td>
                            <td>${product.name}</td>
                            <td>${product.category}</td>
                            <td>¥${product.price.toFixed(2)}</td>
                            <td>${product.sales}</td>
                            <td>${product.rating || 0}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
            
            <h3 style="margin-top: 40px;">近7天销售趋势</h3>
            <table>
                <thead>
                    <tr>
                        <th>日期</th>
                        <th>订单数</th>
                        <th>销售额</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.sales_trend.map(day => `
                        <tr>
                            <td>${day.date}</td>
                            <td>${day.orders}</td>
                            <td>¥${day.sales.toFixed(2)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        document.getElementById('adminDashboard').innerHTML = html;
    } catch (error) {
        console.error('加载统计数据失败:', error);
    }
}

// 加载用户管理
async function loadAdminUsers() {
    try {
        const data = await adminAPI.getUsers({ page: 1, limit: 20 });
        
        const html = `
            <h3>用户管理</h3>
            <div style="margin-bottom: 20px;">
                <input type="text" id="userSearchKeyword" placeholder="搜索用户名或邮箱" style="padding: 10px; width: 300px; margin-right: 10px;">
                <select id="userRoleFilter" style="padding: 10px; margin-right: 10px;">
                    <option value="">全部角色</option>
                    <option value="buyer">买家</option>
                    <option value="seller">卖家</option>
                    <option value="admin">管理员</option>
                </select>
                <button class="btn btn-primary" onclick="searchUsers()">搜索</button>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>用户名</th>
                        <th>邮箱</th>
                        <th>手机号</th>
                        <th>角色</th>
                        <th>状态</th>
                        <th>注册时间</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.users.map(user => `
                        <tr>
                            <td>${user.username}</td>
                            <td>${user.email}</td>
                            <td>${user.phone || '-'}</td>
                            <td>${user.role === 'buyer' ? '买家' : user.role === 'seller' ? '卖家' : '管理员'}</td>
                            <td>${user.status === 'active' ? '正常' : '禁用'}</td>
                            <td>${user.created_at}</td>
                            <td>
                                ${user.role !== 'admin' ? `
                                    <button class="btn ${user.status === 'active' ? 'btn-warning' : 'btn-success'}" 
                                            onclick="toggleUserStatus('${user.id}', '${user.status === 'active' ? 'inactive' : 'active'}')">
                                        ${user.status === 'active' ? '禁用' : '启用'}
                                    </button>
                                    <button class="btn btn-danger" onclick="deleteAdminUser('${user.id}')">删除</button>
                                ` : '-'}
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        document.getElementById('adminUsers').innerHTML = html;
    } catch (error) {
        console.error('加载用户列表失败:', error);
    }
}

// 搜索用户
function searchUsers() {
    const keyword = document.getElementById('userSearchKeyword').value;
    const role = document.getElementById('userRoleFilter').value;
    
    adminAPI.getUsers({ keyword, role, page: 1, limit: 20 })
        .then(data => {
            // 重新渲染表格
            loadAdminUsers();
        });
}

// 切换用户状态
async function toggleUserStatus(userId, status) {
    try {
        await adminAPI.updateUserStatus(userId, { status });
        alert('状态更新成功');
        loadAdminUsers();
    } catch (error) {
        alert(error.message || '操作失败');
    }
}

// 删除用户
async function deleteAdminUser(userId) {
    if (!(await confirmAsync('确定要删除这个用户吗？'))) return;
    
    try {
        await adminAPI.deleteUser(userId);
        showSuccess('用户已删除');
        loadAdminUsers();
    } catch (error) {
        showError(error.message || '删除失败');
    }
}

// 加载分类管理
async function loadAdminCategories() {
    try {
        const data = await adminAPI.getCategories();
        
        const html = `
            <h3>分类管理</h3>
            <button class="btn btn-primary" onclick="showAddCategoryForm()" style="margin-bottom: 20px;">添加分类</button>
            
            <div id="categoryForm" style="display: none; margin-bottom: 30px; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                <h4>添加/编辑分类</h4>
                <form onsubmit="saveCategory(event)">
                    <input type="hidden" id="categoryId">
                    <div class="form-group">
                        <label>分类名称</label>
                        <input type="text" id="categoryName" required>
                    </div>
                    <div class="form-group">
                        <label>分类描述</label>
                        <input type="text" id="categoryDescription">
                    </div>
                    <button type="submit" class="btn btn-success">保存</button>
                    <button type="button" class="btn" onclick="hideCategoryForm()">取消</button>
                </form>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>分类名称</th>
                        <th>描述</th>
                        <th>商品数量</th>
                        <th>创建时间</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.categories.map(cat => `
                        <tr>
                            <td>${cat.name}</td>
                            <td>${cat.description}</td>
                            <td>${cat.product_count}</td>
                            <td>${cat.created_at}</td>
                            <td>
                                <button class="btn btn-warning" onclick='editCategory(${JSON.stringify(cat)})'>编辑</button>
                                <button class="btn btn-danger" onclick="deleteCategory('${cat.id}')" ${cat.product_count > 0 ? 'disabled' : ''}>删除</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        document.getElementById('adminCategories').innerHTML = html;
    } catch (error) {
        console.error('加载分类失败:', error);
    }
}

// 显示添加分类表单
function showAddCategoryForm() {
    document.getElementById('categoryForm').style.display = 'block';
    document.getElementById('categoryId').value = '';
    document.getElementById('categoryName').value = '';
    document.getElementById('categoryDescription').value = '';
}

// 隐藏分类表单
function hideCategoryForm() {
    document.getElementById('categoryForm').style.display = 'none';
}

// 编辑分类
function editCategory(category) {
    document.getElementById('categoryForm').style.display = 'block';
    document.getElementById('categoryId').value = category.id;
    document.getElementById('categoryName').value = category.name;
    document.getElementById('categoryDescription').value = category.description;
}

// 保存分类
async function saveCategory(event) {
    event.preventDefault();
    
    const categoryId = document.getElementById('categoryId').value;
    const data = {
        name: document.getElementById('categoryName').value,
        description: document.getElementById('categoryDescription').value
    };
    
    try {
        if (categoryId) {
            await adminAPI.updateCategory(categoryId, data);
        } else {
            await adminAPI.createCategory(data);
        }
        alert('保存成功');
        hideCategoryForm();
        loadAdminCategories();
    } catch (error) {
        alert(error.message || '保存失败');
    }
}

// 删除分类
async function deleteCategory(categoryId) {
    if (!(await confirmAsync('确定要删除这个分类吗？'))) return;
    
    try {
        await adminAPI.deleteCategory(categoryId);
        showSuccess('删除成功');
        loadAdminCategories();
    } catch (error) {
        showError(error.message || '删除失败');
    }
}

// 加载订单管理
async function loadAdminOrders() {
    try {
        const data = await adminAPI.getOrders({ page: 1, limit: 20 });
        
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
            <div style="margin-bottom: 20px;">
                <button class="btn btn-success" onclick="exportOrders()">导出订单数据</button>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>订单号</th>
                        <th>买家</th>
                        <th>金额</th>
                        <th>状态</th>
                        <th>创建时间</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.orders.map(order => `
                        <tr>
                            <td>${order.order_no}</td>
                            <td>${order.buyer_name}</td>
                            <td>¥${order.total_amount.toFixed(2)}</td>
                            <td>${statusMap[order.status]}</td>
                            <td>${order.created_at}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        document.getElementById('adminOrders').innerHTML = html;
    } catch (error) {
        console.error('加载订单失败:', error);
    }
}

// 导出订单
async function exportOrders() {
    try {
        const data = await adminAPI.exportOrders({});
        
        // 创建下载链接
        const link = document.createElement('a');
        link.href = 'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,' + data.data;
        link.download = data.filename;
        link.click();
        
        alert('导出成功');
    } catch (error) {
        alert(error.message || '导出失败');
    }
}

// 加载日志管理
async function loadAdminLogs() {
    try {
        const data = await adminAPI.getLogs({ page: 1, limit: 50 });
        
        const html = `
            <h3>日志管理</h3>
            <table>
                <thead>
                    <tr>
                        <th>用户</th>
                        <th>操作</th>
                        <th>详情</th>
                        <th>时间</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.logs.map(log => `
                        <tr>
                            <td>${log.username}</td>
                            <td>${log.action}</td>
                            <td>${log.details || '-'}</td>
                            <td>${log.timestamp}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        document.getElementById('adminLogs').innerHTML = html;
    } catch (error) {
        console.error('加载日志失败:', error);
    }
}
