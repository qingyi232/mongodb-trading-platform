// 加载个人信息页面
async function loadProfilePage() {
    showProfileTab('info');
}

// 切换个人信息标签
function showProfileTab(tab) {
    // 更新菜单状态
    document.querySelectorAll('.profile-menu a').forEach(link => {
        link.classList.remove('active');
    });
    if (window.event?.target) {
        window.event.target.classList.add('active');
    }
    
    // 隐藏所有标签
    document.querySelectorAll('.profile-tab').forEach(tabEl => {
        tabEl.classList.remove('active');
    });
    
    // 显示目标标签
    const targetTab = document.getElementById('profile' + tab.charAt(0).toUpperCase() + tab.slice(1));
    if (targetTab) {
        targetTab.classList.add('active');
        
        // 加载标签内容
        switch(tab) {
            case 'info':
                loadProfileInfo();
                break;
            case 'address':
                loadAddresses();
                break;
            case 'password':
                loadPasswordForm();
                break;
        }
    }
}

// 加载个人信息
async function loadProfileInfo() {
    try {
        const data = await userAPI.getProfile();
        const user = data.user;
        
        const html = `
            <h3>个人信息</h3>
            <form onsubmit="updateProfile(event)" style="max-width: 500px;">
                <div class="form-group">
                    <label>用户名</label>
                    <input type="text" value="${user.username}" disabled>
                </div>
                <div class="form-group">
                    <label>邮箱</label>
                    <input type="email" id="profileEmail" value="${user.email}" required>
                </div>
                <div class="form-group">
                    <label>手机号</label>
                    <input type="tel" id="profilePhone" value="${user.phone || ''}">
                </div>
                <div class="form-group">
                    <label>角色</label>
                    <input type="text" value="${user.role === 'buyer' ? '买家' : user.role === 'seller' ? '卖家' : '管理员'}" disabled>
                </div>
                <div class="form-group">
                    <label>注册时间</label>
                    <input type="text" value="${user.created_at}" disabled>
                </div>
                <button type="submit" class="btn btn-primary">保存修改</button>
            </form>
        `;
        
        document.getElementById('profileInfo').innerHTML = html;
    } catch (error) {
        console.error('加载个人信息失败:', error);
    }
}

// 更新个人信息
async function updateProfile(event) {
    event.preventDefault();
    
    const email = document.getElementById('profileEmail').value;
    const phone = document.getElementById('profilePhone').value;
    
    try {
        await userAPI.updateProfile({ email, phone });
        alert('更新成功');
    } catch (error) {
        alert(error.message || '更新失败');
    }
}

// 加载收货地址
async function loadAddresses() {
    try {
        const data = await userAPI.getAddresses();
        const addresses = data.addresses;
        
        const html = `
            <h3>收货地址</h3>
            <button class="btn btn-primary" onclick="showAddAddressForm()" style="margin-bottom: 20px;">添加新地址</button>
            <div id="addressForm" style="display: none; margin-bottom: 30px; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                <h4>添加地址</h4>
                <form onsubmit="saveAddress(event)">
                    <input type="hidden" id="addressId">
                    <div class="form-group">
                        <label>收货人</label>
                        <input type="text" id="addressReceiver" required>
                    </div>
                    <div class="form-group">
                        <label>手机号</label>
                        <input type="tel" id="addressPhone" required>
                    </div>
                    <div class="form-group">
                        <label>省份</label>
                        <input type="text" id="addressProvince" required>
                    </div>
                    <div class="form-group">
                        <label>城市</label>
                        <input type="text" id="addressCity" required>
                    </div>
                    <div class="form-group">
                        <label>区县</label>
                        <input type="text" id="addressDistrict" required>
                    </div>
                    <div class="form-group">
                        <label>详细地址</label>
                        <input type="text" id="addressDetail" required>
                    </div>
                    <div class="form-group">
                        <label style="display: flex; align-items: center; gap: 8px;">
                            <input type="checkbox" id="addressDefault" style="width: auto; margin: 0;">
                            <span>设为默认地址</span>
                        </label>
                    </div>
                    <button type="submit" class="btn btn-success">保存</button>
                    <button type="button" class="btn" onclick="hideAddressForm()">取消</button>
                </form>
            </div>
            <div class="addresses-list">
                ${addresses.length === 0 ? '<p style="color: #7f8c8d;">暂无收货地址</p>' : addresses.map(addr => `
                    <div class="address-card" style="padding: 20px; background: white; border: 1px solid #ecf0f1; border-radius: 8px; margin-bottom: 15px;">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <h4>${addr.receiver} ${addr.phone} ${addr.is_default ? '<span style="color: var(--accent); font-size: 12px;">[默认]</span>' : ''}</h4>
                                <p style="color: #7f8c8d; margin-top: 10px;">${addr.province} ${addr.city} ${addr.district} ${addr.detail}</p>
                            </div>
                            <div style="display: flex; gap: 10px;">
                                <button class="btn btn-warning" onclick='editAddress(${JSON.stringify(addr)})'>编辑</button>
                                <button class="btn btn-danger" onclick="deleteAddress('${addr.id}')">删除</button>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        document.getElementById('profileAddress').innerHTML = html;
    } catch (error) {
        console.error('加载地址失败:', error);
    }
}

// 显示添加地址表单
function showAddAddressForm() {
    document.getElementById('addressForm').style.display = 'block';
    document.getElementById('addressId').value = '';
    document.getElementById('addressReceiver').value = '';
    document.getElementById('addressPhone').value = '';
    document.getElementById('addressProvince').value = '';
    document.getElementById('addressCity').value = '';
    document.getElementById('addressDistrict').value = '';
    document.getElementById('addressDetail').value = '';
    document.getElementById('addressDefault').checked = false;
}

// 隐藏地址表单
function hideAddressForm() {
    document.getElementById('addressForm').style.display = 'none';
}

// 编辑地址
function editAddress(address) {
    document.getElementById('addressForm').style.display = 'block';
    document.getElementById('addressId').value = address.id;
    document.getElementById('addressReceiver').value = address.receiver;
    document.getElementById('addressPhone').value = address.phone;
    document.getElementById('addressProvince').value = address.province;
    document.getElementById('addressCity').value = address.city;
    document.getElementById('addressDistrict').value = address.district;
    document.getElementById('addressDetail').value = address.detail;
    document.getElementById('addressDefault').checked = address.is_default;
}

// 保存地址
async function saveAddress(event) {
    event.preventDefault();
    
    const addressId = document.getElementById('addressId').value;
    const data = {
        receiver: document.getElementById('addressReceiver').value,
        phone: document.getElementById('addressPhone').value,
        province: document.getElementById('addressProvince').value,
        city: document.getElementById('addressCity').value,
        district: document.getElementById('addressDistrict').value,
        detail: document.getElementById('addressDetail').value,
        is_default: document.getElementById('addressDefault').checked
    };
    
    try {
        if (addressId) {
            await userAPI.updateAddress(addressId, data);
        } else {
            await userAPI.addAddress(data);
        }
        alert('保存成功');
        hideAddressForm();
        loadAddresses();
    } catch (error) {
        alert(error.message || '保存失败');
    }
}

// 删除地址
async function deleteAddress(addressId) {
    if (!(await confirmAsync('确定要删除这个地址吗？'))) return;
    
    try {
        await userAPI.deleteAddress(addressId);
        showSuccess('删除成功');
        loadAddresses();
    } catch (error) {
        showError(error.message || '删除失败');
    }
}

// 加载修改密码表单
function loadPasswordForm() {
    const html = `
        <h3>修改密码</h3>
        <form onsubmit="changePassword(event)" style="max-width: 500px;">
            <div class="form-group">
                <label>原密码</label>
                <input type="password" id="oldPassword" required>
            </div>
            <div class="form-group">
                <label>新密码</label>
                <input type="password" id="newPassword" required minlength="6">
            </div>
            <div class="form-group">
                <label>确认新密码</label>
                <input type="password" id="confirmPassword" required minlength="6">
            </div>
            <button type="submit" class="btn btn-primary">修改密码</button>
        </form>
    `;
    
    document.getElementById('profilePassword').innerHTML = html;
}

// 修改密码
async function changePassword(event) {
    event.preventDefault();
    
    const oldPassword = document.getElementById('oldPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    if (newPassword !== confirmPassword) {
        alert('两次输入的新密码不一致');
        return;
    }
    
    try {
        await userAPI.changePassword({ old_password: oldPassword, new_password: newPassword });
        alert('密码修改成功，请重新登录');
        logout();
    } catch (error) {
        alert(error.message || '修改失败');
    }
}
