// 自定义弹窗系统

// 显示提示消息
function showMessage(message, type = 'info') {
    const modal = document.createElement('div');
    modal.className = 'custom-modal';
    
    // 检查消息是否包含HTML标签
    const isHTML = /<[a-z][\s\S]*>/i.test(message);
    
    modal.innerHTML = `
        <div class="modal-overlay" onclick="closeModal(this.parentElement)"></div>
        <div class="modal-content modal-${type}">
            <div class="modal-icon">
                ${getModalIcon(type)}
            </div>
            <div class="modal-message">${isHTML ? message : escapeHtml(message)}</div>
            <div class="modal-actions">
                <button class="btn btn-primary" onclick="closeModal(this.closest('.custom-modal'))">确定</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    setTimeout(() => modal.classList.add('show'), 10);
}

// HTML转义函数
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 显示确认对话框
function showConfirm(message, onConfirm, onCancel) {
    const modal = document.createElement('div');
    modal.className = 'custom-modal';
    modal.innerHTML = `
        <div class="modal-overlay" onclick="handleCancel(this.parentElement)"></div>
        <div class="modal-content modal-confirm">
            <div class="modal-icon">
                ${getModalIcon('question')}
            </div>
            <div class="modal-message">${message}</div>
            <div class="modal-actions">
                <button class="btn" onclick="handleCancel(this.closest('.custom-modal'))">取消</button>
                <button class="btn btn-primary" onclick="handleConfirm(this.closest('.custom-modal'))">确定</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    setTimeout(() => modal.classList.add('show'), 10);
    
    // 保存回调函数
    modal._onConfirm = onConfirm;
    modal._onCancel = onCancel;
}

// 显示输入对话框
function showPrompt(message, defaultValue = '', onConfirm, onCancel) {
    const modal = document.createElement('div');
    modal.className = 'custom-modal';
    modal.innerHTML = `
        <div class="modal-overlay" onclick="handleCancel(this.parentElement)"></div>
        <div class="modal-content modal-prompt">
            <div class="modal-message">${message}</div>
            <input type="text" class="modal-input" value="${defaultValue}" placeholder="请输入...">
            <div class="modal-actions">
                <button class="btn" onclick="handleCancel(this.closest('.custom-modal'))">取消</button>
                <button class="btn btn-primary" onclick="handlePromptConfirm(this.closest('.custom-modal'))">确定</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    setTimeout(() => {
        modal.classList.add('show');
        modal.querySelector('.modal-input').focus();
    }, 10);
    
    // 保存回调函数
    modal._onConfirm = onConfirm;
    modal._onCancel = onCancel;
    
    // 回车确认
    modal.querySelector('.modal-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handlePromptConfirm(modal);
        }
    });
}

// 获取图标
function getModalIcon(type) {
    const icons = {
        'success': '<svg width="48" height="48" viewBox="0 0 48 48" fill="none"><circle cx="24" cy="24" r="20" stroke="#27ae60" stroke-width="3"/><path d="M16 24l6 6 12-12" stroke="#27ae60" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>',
        'error': '<svg width="48" height="48" viewBox="0 0 48 48" fill="none"><circle cx="24" cy="24" r="20" stroke="#e74c3c" stroke-width="3"/><path d="M18 18l12 12M30 18l-12 12" stroke="#e74c3c" stroke-width="3" stroke-linecap="round"/></svg>',
        'warning': '<svg width="48" height="48" viewBox="0 0 48 48" fill="none"><path d="M24 4L4 40h40L24 4z" stroke="#f39c12" stroke-width="3" stroke-linejoin="round"/><path d="M24 18v10M24 32v2" stroke="#f39c12" stroke-width="3" stroke-linecap="round"/></svg>',
        'info': '<svg width="48" height="48" viewBox="0 0 48 48" fill="none"><circle cx="24" cy="24" r="20" stroke="#3498db" stroke-width="3"/><path d="M24 16v2M24 22v12" stroke="#3498db" stroke-width="3" stroke-linecap="round"/></svg>',
        'question': '<svg width="48" height="48" viewBox="0 0 48 48" fill="none"><circle cx="24" cy="24" r="20" stroke="#9b59b6" stroke-width="3"/><path d="M18 20c0-3.3 2.7-6 6-6s6 2.7 6 6c0 2.4-1.4 4.5-3.5 5.5L24 28M24 34v2" stroke="#9b59b6" stroke-width="3" stroke-linecap="round"/></svg>'
    };
    return icons[type] || icons['info'];
}

// 关闭弹窗
function closeModal(modal) {
    modal.classList.remove('show');
    setTimeout(() => modal.remove(), 300);
}

// 处理确认
function handleConfirm(modal) {
    if (modal._onConfirm) {
        modal._onConfirm();
    }
    closeModal(modal);
}

// 处理取消
function handleCancel(modal) {
    if (modal._onCancel) {
        modal._onCancel();
    }
    closeModal(modal);
}

// 处理输入确认
function handlePromptConfirm(modal) {
    const value = modal.querySelector('.modal-input').value;
    if (modal._onConfirm) {
        modal._onConfirm(value);
    }
    closeModal(modal);
}

// 重写全局 alert
window.alert = function(message) {
    showMessage(message, 'info');
};

// 创建同步版本的 confirm（用于兼容）
const originalConfirm = window.confirm;
window.confirm = function(message) {
    // 如果在 async 函数中调用，返回 Promise
    if (new Error().stack.includes('async')) {
        return new Promise((resolve) => {
            showConfirm(message, () => resolve(true), () => resolve(false));
        });
    }
    // 否则使用原生 confirm
    return originalConfirm(message);
};

// 提供异步版本
window.confirmAsync = function(message) {
    return new Promise((resolve) => {
        showConfirm(message, () => resolve(true), () => resolve(false));
    });
};

// 添加便捷方法
window.showSuccess = (message) => showMessage(message, 'success');
window.showError = (message) => showMessage(message, 'error');
window.showWarning = (message) => showMessage(message, 'warning');
window.showInfo = (message) => showMessage(message, 'info');
