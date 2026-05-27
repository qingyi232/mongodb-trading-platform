// 加载订单页面
async function loadOrdersPage(status = '') {
    try {
        const data = await orderAPI.getBuyerOrders({ status, page: 1, limit: 20 });
        renderOrders(data.orders);
    } catch (error) {
        console.error('加载订单失败:', error);
    }
}

// 筛选订单
function filterOrders(status) {
    // 更新按钮状态
    document.querySelectorAll('.order-tabs button').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    loadOrdersPage(status);
}

// 渲染订单列表
function renderOrders(orders) {
    const container = document.getElementById('ordersList');
    
    if (!orders || orders.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #7f8c8d; padding: 50px;">暂无订单</p>';
        return;
    }
    
    const statusMap = {
        'pending_payment': '待支付',
        'paid': '待发货',
        'shipped': '待收货',
        'completed': '已完成',
        'cancelled': '已取消',
        'refund_pending': '退款中',
        'refunded': '已退款'
    };
    
    const html = orders.map(order => `
        <div class="order-card">
            <div class="order-header">
                <div>
                    <strong>订单号: ${order.order_no}</strong>
                    <span style="margin-left: 20px; color: #7f8c8d;">${order.created_at}</span>
                    ${order.tracking_no ? `<span style="margin-left: 20px; color: #27ae60;">物流单号: ${order.tracking_no}</span>` : ''}
                </div>
                <div style="color: var(--accent);">${statusMap[order.status]}</div>
            </div>
            <div class="order-items">
                ${order.items.map(item => `
                    <div class="order-item">
                        <img src="${item.product_image || '/placeholder.jpg'}" alt="${item.product_name}">
                        <div style="flex: 1;">
                            <h4>${item.product_name}</h4>
                            <p style="color: #7f8c8d;">¥${item.price.toFixed(2)} × ${item.quantity}</p>
                        </div>
                        <div style="font-weight: 600;">¥${item.subtotal.toFixed(2)}</div>
                    </div>
                `).join('')}
            </div>
            <div class="order-footer">
                <div>
                    <strong>总计: ¥${order.total_amount.toFixed(2)}</strong>
                </div>
                <div style="display: flex; gap: 10px;">
                    ${order.status === 'pending_payment' ? `
                        <button class="btn btn-primary" onclick="payOrder('${order.id}')">立即支付</button>
                        <button class="btn btn-danger" onclick="cancelOrder('${order.id}')">取消订单</button>
                    ` : ''}
                    ${order.status === 'shipped' ? `
                        <button class="btn btn-success" onclick="receiveOrder('${order.id}')">确认收货</button>
                    ` : ''}
                    ${order.status === 'completed' ? `
                        <button class="btn btn-warning" onclick="showReviewDialog('${order.id}', '${order.items[0].product_id}')">评价</button>
                    ` : ''}
                    ${order.status === 'paid' || order.status === 'shipped' ? `
                        <button class="btn btn-warning" onclick="refundOrder('${order.id}')">申请退款</button>
                    ` : ''}
                    <button class="btn" onclick="viewOrderDetail('${order.id}')">查看详情</button>
                </div>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

// 支付订单
async function payOrder(orderId) {
    try {
        await orderAPI.pay(orderId);
        showSuccess('支付成功');
        loadOrdersPage();
    } catch (error) {
        showError(error.message || '支付失败');
    }
}

// 取消订单
async function cancelOrder(orderId) {
    if (!(await confirmAsync('确定要取消这个订单吗？'))) return;
    
    try {
        await orderAPI.cancel(orderId);
        showSuccess('订单已取消');
        loadOrdersPage();
    } catch (error) {
        showError(error.message || '取消失败');
    }
}

// 确认收货
async function receiveOrder(orderId) {
    if (!(await confirmAsync('确认已收到货物吗？'))) return;
    
    try {
        await orderAPI.receive(orderId);
        showSuccess('确认收货成功');
        loadOrdersPage();
    } catch (error) {
        showError(error.message || '操作失败');
    }
}

// 申请退款
async function refundOrder(orderId) {
    showPrompt('请输入退款原因：', '', async (reason) => {
        if (!reason || !reason.trim()) {
            showWarning('请输入退款原因');
            return;
        }
        
        try {
            await orderAPI.refund(orderId, { reason: reason.trim() });
            showSuccess('退款申请已提交');
            loadOrdersPage();
        } catch (error) {
            showError(error.message || '申请失败');
        }
    });
}

// 查看订单详情
async function viewOrderDetail(orderId) {
    try {
        const data = await orderAPI.getDetail(orderId);
        const order = data.order;
        
        const statusMap = {
            'pending_payment': '待支付',
            'paid': '待发货',
            'shipped': '待收货',
            'completed': '已完成',
            'cancelled': '已取消',
            'refund_pending': '退款中',
            'refunded': '已退款'
        };
        
        let detailHTML = `
            <div style="text-align: left;">
                <h3 style="margin-bottom: 20px;">订单详情</h3>
                <p><strong>订单号:</strong> ${order.order_no}</p>
                <p><strong>状态:</strong> <span style="color: var(--accent);">${statusMap[order.status]}</span></p>
                <p><strong>总金额:</strong> <span style="color: var(--accent); font-size: 20px; font-weight: 700;">¥${order.total_amount.toFixed(2)}</span></p>
                <p><strong>创建时间:</strong> ${order.created_at}</p>
                ${order.tracking_no ? `<p><strong>物流单号:</strong> ${order.tracking_no}</p>` : ''}
                
                <h4 style="margin-top: 20px; margin-bottom: 10px;">收货地址</h4>
                <p>${order.address.receiver} ${order.address.phone}</p>
                <p>${order.address.province} ${order.address.city} ${order.address.district}</p>
                <p>${order.address.detail}</p>
                
                <h4 style="margin-top: 20px; margin-bottom: 10px;">商品清单</h4>
                ${order.items.map(item => `
                    <div style="padding: 10px 0; border-bottom: 1px solid #ecf0f1;">
                        <p><strong>${item.product_name}</strong></p>
                        <p style="color: #7f8c8d;">¥${item.price.toFixed(2)} × ${item.quantity} = ¥${item.subtotal.toFixed(2)}</p>
                    </div>
                `).join('')}
            </div>
        `;
        
        showInfo(detailHTML);
    } catch (error) {
        showError('加载订单详情失败');
    }
}

// 显示评价对话框
function showReviewDialog(orderId, productId) {
    showPrompt('请输入评分 (1-5)：', '5', (rating) => {
        const ratingNum = parseInt(rating);
        if (isNaN(ratingNum) || ratingNum < 1 || ratingNum > 5) {
            showWarning('评分必须在1-5之间');
            return;
        }
        
        showPrompt('请输入评价内容：', '', (comment) => {
            if (!comment || !comment.trim()) {
                showWarning('请输入评价内容');
                return;
            }
            submitReview(orderId, productId, ratingNum, comment.trim());
        });
    });
}

// 提交评价
async function submitReview(orderId, productId, rating, comment) {
    try {
        await orderAPI.addReview(orderId, { product_id: productId, rating, comment });
        showSuccess('评价成功');
        loadOrdersPage();
    } catch (error) {
        showError(error.message || '评价失败');
    }
}
