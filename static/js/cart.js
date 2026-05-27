// 加载购物车数量
async function loadCartCount() {
    if (!currentUser) return;
    
    try {
        const data = await cartAPI.getCart();
        const count = data.cart_items.reduce((sum, item) => sum + item.quantity, 0);
        document.getElementById('cartCount').textContent = count;
    } catch (error) {
        console.error('加载购物车数量失败:', error);
    }
}

// 加载购物车页面
async function loadCartPage() {
    try {
        const data = await cartAPI.getCart();
        renderCart(data.cart_items);
    } catch (error) {
        console.error('加载购物车失败:', error);
    }
}

// 渲染购物车
function renderCart(items) {
    const container = document.getElementById('cartContent');
    
    if (!items || items.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #7f8c8d; padding: 50px;">购物车是空的</p>';
        return;
    }
    
    const validItems = items.filter(item => item.product_status === 'active');
    const total = validItems.reduce((sum, item) => sum + item.product_price * item.quantity, 0);
    
    const html = `
        <div class="cart-items">
            ${items.map(item => `
                <div class="cart-item">
                    <img src="${item.product_image || '/placeholder.jpg'}" alt="${item.product_name}">
                    <div class="cart-item-info">
                        <h4>${item.product_name}</h4>
                        <p style="color: #7f8c8d;">${item.product_status === 'active' ? '在售' : '已下架'}</p>
                    </div>
                    <div class="cart-item-price">¥${item.product_price.toFixed(2)}</div>
                    <div class="cart-item-quantity">
                        <button onclick="updateCartQuantity('${item.id}', ${item.quantity - 1})" ${item.quantity <= 1 ? 'disabled' : ''}>-</button>
                        <input type="number" value="${item.quantity}" min="1" max="${item.product_stock}" 
                               onchange="updateCartQuantity('${item.id}', this.value)" style="width: 60px; text-align: center;">
                        <button onclick="updateCartQuantity('${item.id}', ${item.quantity + 1})" ${item.quantity >= item.product_stock ? 'disabled' : ''}>+</button>
                    </div>
                    <div class="cart-item-subtotal">¥${(item.product_price * item.quantity).toFixed(2)}</div>
                    <button class="btn btn-danger" onclick="removeFromCart('${item.id}')">删除</button>
                </div>
            `).join('')}
        </div>
        <div class="cart-summary">
            <div class="cart-total">总计: ¥${total.toFixed(2)}</div>
            <button class="btn btn-primary" onclick="proceedToCheckout()" ${validItems.length === 0 ? 'disabled' : ''}>
                结算 (${validItems.length}件)
            </button>
        </div>
    `;
    
    container.innerHTML = html;
}

// 更新购物车数量
async function updateCartQuantity(itemId, quantity) {
    quantity = parseInt(quantity);
    
    if (quantity < 1) {
        alert('数量不能小于1');
        return;
    }
    
    try {
        await cartAPI.updateItem(itemId, { quantity });
        loadCartPage();
        loadCartCount();
    } catch (error) {
        alert(error.message || '更新失败');
        loadCartPage();
    }
}

// 从购物车移除
async function removeFromCart(itemId) {
    if (!(await confirmAsync('确定要删除这件商品吗？'))) return;
    
    try {
        await cartAPI.removeItem(itemId);
        loadCartPage();
        loadCartCount();
    } catch (error) {
        showError(error.message || '删除失败');
    }
}

// 结算
async function proceedToCheckout() {
    try {
        const cartData = await cartAPI.getCart();
        const validItems = cartData.cart_items.filter(item => item.product_status === 'active');
        
        if (validItems.length === 0) {
            alert('购物车中没有可结算的商品');
            return;
        }
        
        // 获取收货地址
        const addressData = await userAPI.getAddresses();
        const addresses = addressData.addresses;
        
        if (addresses.length === 0) {
            alert('请先添加收货地址');
            showPage('profile');
            showProfileTab('address');
            return;
        }
        
        // 显示结算页面
        showCheckoutPage(validItems, addresses);
    } catch (error) {
        alert(error.message || '加载失败');
    }
}

// 显示结算页面
function showCheckoutPage(items, addresses) {
    const total = items.reduce((sum, item) => sum + item.product_price * item.quantity, 0);
    const defaultAddress = addresses.find(addr => addr.is_default) || addresses[0];
    
    const html = `
        <h2>确认订单</h2>
        <div style="background: white; padding: 30px; border-radius: 12px; margin-bottom: 20px;">
            <h3 style="margin-bottom: 20px;">选择收货地址</h3>
            <div id="checkoutAddresses">
                ${addresses.map(addr => `
                    <div class="address-option" style="padding: 15px; border: 2px solid ${addr.id === defaultAddress.id ? 'var(--accent)' : '#ecf0f1'}; border-radius: 8px; margin-bottom: 10px; cursor: pointer; transition: all 0.3s;" 
                         onclick="selectCheckoutAddress('${addr.id}')">
                        <input type="radio" name="checkout_address" value="${addr.id}" ${addr.id === defaultAddress.id ? 'checked' : ''} style="margin-right: 10px;">
                        <strong>${addr.receiver}</strong> ${addr.phone} ${addr.is_default ? '<span style="color: var(--accent); font-size: 12px;">[默认]</span>' : ''}
                        <p style="color: #7f8c8d; margin: 5px 0 0 25px;">${addr.province} ${addr.city} ${addr.district} ${addr.detail}</p>
                    </div>
                `).join('')}
            </div>
        </div>
        
        <div style="background: white; padding: 30px; border-radius: 12px; margin-bottom: 20px;">
            <h3 style="margin-bottom: 20px;">商品清单</h3>
            ${items.map(item => `
                <div style="display: flex; align-items: center; padding: 15px 0; border-bottom: 1px solid #ecf0f1;">
                    <img src="${item.product_image}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 8px; margin-right: 15px;">
                    <div style="flex: 1;">
                        <h4>${item.product_name}</h4>
                        <p style="color: #7f8c8d;">¥${item.product_price.toFixed(2)} × ${item.quantity}</p>
                    </div>
                    <div style="font-size: 18px; color: var(--accent); font-weight: 600;">¥${(item.product_price * item.quantity).toFixed(2)}</div>
                </div>
            `).join('')}
        </div>
        
        <div style="background: white; padding: 30px; border-radius: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <p style="color: #7f8c8d;">商品数量：${items.length} 件</p>
                    <p style="font-size: 24px; color: var(--accent); font-weight: 700; margin-top: 10px;">总计：¥${total.toFixed(2)}</p>
                </div>
                <div style="display: flex; gap: 15px;">
                    <button class="btn" onclick="showPage('cart')">返回购物车</button>
                    <button class="btn btn-primary" onclick="confirmCheckout()" style="padding: 15px 40px; font-size: 16px;">提交订单</button>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('cartContent').innerHTML = html;
    
    // 保存结算数据到全局变量
    window.checkoutData = { items, addresses };
}

// 选择收货地址
function selectCheckoutAddress(addressId) {
    // 更新所有地址选项的样式
    document.querySelectorAll('.address-option').forEach(option => {
        option.style.borderColor = '#ecf0f1';
    });
    
    // 高亮选中的地址
    event.currentTarget.style.borderColor = 'var(--accent)';
    
    // 选中对应的单选框
    document.querySelector(`input[value="${addressId}"]`).checked = true;
}

// 确认结算
async function confirmCheckout() {
    try {
        const selectedAddressId = document.querySelector('input[name="checkout_address"]:checked').value;
        const items = window.checkoutData.items;
        
        // 创建订单
        const orderData = {
            items: items.map(item => ({
                product_id: item.product_id,
                quantity: item.quantity
            })),
            address_id: selectedAddressId,
            payment_method: 'online'
        };
        
        const result = await orderAPI.create(orderData);
        
        // 支付订单
        await orderAPI.pay(result.order_id);
        
        alert('订单创建成功！');
        loadCartCount();
        showPage('orders');
    } catch (error) {
        alert(error.message || '提交订单失败');
    }
}
