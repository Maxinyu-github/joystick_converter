// API base URL
const API_BASE = '/api';

// Current mappings data
let mappingsData = {};
let currentEditEvent = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadDeviceInfo();
    loadMappings();
});

// Load device information
async function loadDeviceInfo() {
    try {
        const response = await fetch(`${API_BASE}/device`);
        const data = await response.json();
        
        document.getElementById('deviceName').value = data.device_name;
        document.getElementById('mappingsCount').textContent = data.mappings_count;
        document.getElementById('configPath').textContent = data.config_path;
    } catch (error) {
        console.error('Error loading device info:', error);
        showAlert('加载设备信息失败', 'error');
    }
}

// Load all mappings
async function loadMappings() {
    try {
        const response = await fetch(`${API_BASE}/mappings`);
        const data = await response.json();
        
        mappingsData = data.mappings;
        displayMappings(mappingsData);
        
        document.getElementById('mappingsCount').textContent = Object.keys(mappingsData).length;
    } catch (error) {
        console.error('Error loading mappings:', error);
        showAlert('加载映射失败', 'error');
        document.getElementById('mappingsList').innerHTML = '<p class="loading">加载失败</p>';
    }
}

// Display mappings
function displayMappings(mappings) {
    const container = document.getElementById('mappingsList');
    
    if (Object.keys(mappings).length === 0) {
        container.innerHTML = '<p class="loading">暂无映射配置，点击"新建映射"添加</p>';
        return;
    }
    
    let html = '';
    for (const [eventName, mapping] of Object.entries(mappings)) {
        html += createMappingCard(eventName, mapping);
    }
    
    container.innerHTML = html;
}

// Create mapping card HTML
function createMappingCard(eventName, mapping) {
    const type = mapping.type || 'unknown';
    const description = mapping.description || '';
    
    let details = '';
    
    if (type === 'keyboard') {
        details = `<div><strong>按键:</strong> ${mapping.key}</div>`;
    } else if (type === 'keyboard_combo') {
        details = `<div><strong>组合键:</strong> ${mapping.combo.join(' + ')}</div>`;
    } else if (type === 'dpad_horizontal' || type === 'dpad_vertical') {
        details = `
            <div><strong>正方向:</strong> ${mapping.positive_key}</div>
            <div><strong>负方向:</strong> ${mapping.negative_key}</div>
        `;
    }
    
    return `
        <div class="mapping-item" data-event="${eventName}" data-type="${type}">
            <div class="mapping-header">
                <span class="mapping-name">${eventName}</span>
                <span class="mapping-type">${getTypeLabel(type)}</span>
            </div>
            <div class="mapping-details">
                ${details}
            </div>
            ${description ? `<div class="mapping-description">${description}</div>` : ''}
            <div class="mapping-actions">
                <button class="btn-secondary btn-small" onclick="editMapping('${eventName}')">✏️ 编辑</button>
                <button class="btn-danger btn-small" onclick="deleteMapping('${eventName}')">🗑️ 删除</button>
            </div>
        </div>
    `;
}

// Get type label in Chinese
function getTypeLabel(type) {
    const labels = {
        'keyboard': '键盘',
        'keyboard_combo': '组合键',
        'dpad_horizontal': 'D-Pad 横向',
        'dpad_vertical': 'D-Pad 纵向'
    };
    return labels[type] || type;
}

// Filter mappings
function filterMappings() {
    const searchText = document.getElementById('searchFilter').value.toLowerCase();
    const typeFilter = document.getElementById('typeFilter').value;
    
    const items = document.querySelectorAll('.mapping-item');
    
    items.forEach(item => {
        const eventName = item.dataset.event.toLowerCase();
        const type = item.dataset.type;
        
        const matchesSearch = eventName.includes(searchText);
        const matchesType = !typeFilter || type === typeFilter;
        
        item.style.display = (matchesSearch && matchesType) ? 'block' : 'none';
    });
}

// Update device name
async function updateDeviceName() {
    const deviceName = document.getElementById('deviceName').value;
    
    if (!deviceName.trim()) {
        showAlert('请输入设备名称', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/device/name`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({device_name: deviceName})
        });
        
        if (response.ok) {
            showAlert('设备名称已更新', 'success');
        } else {
            showAlert('更新失败', 'error');
        }
    } catch (error) {
        console.error('Error updating device name:', error);
        showAlert('更新失败', 'error');
    }
}

// Reload configuration
async function reloadConfig() {
    try {
        const response = await fetch(`${API_BASE}/reload`, {method: 'POST'});
        
        if (response.ok) {
            showAlert('配置已重新加载', 'success');
            loadDeviceInfo();
            loadMappings();
        } else {
            showAlert('重新加载失败', 'error');
        }
    } catch (error) {
        console.error('Error reloading config:', error);
        showAlert('重新加载失败', 'error');
    }
}

// Export configuration
async function exportConfig() {
    try {
        const response = await fetch(`${API_BASE}/export`);
        const data = await response.json();
        
        const json = JSON.stringify(data, null, 2);
        const blob = new Blob([json], {type: 'application/json'});
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = 'joystick_mappings.json';
        a.click();
        
        showAlert('配置已导出', 'success');
    } catch (error) {
        console.error('Error exporting config:', error);
        showAlert('导出失败', 'error');
    }
}

// Show import dialog
function showImportDialog() {
    document.getElementById('importDialog').style.display = 'block';
}

// Close import dialog
function closeImportDialog() {
    document.getElementById('importDialog').style.display = 'none';
    document.getElementById('importJson').value = '';
}

// Import configuration
async function importConfig() {
    const jsonText = document.getElementById('importJson').value;
    
    if (!jsonText.trim()) {
        showAlert('请粘贴配置JSON', 'error');
        return;
    }
    
    try {
        const data = JSON.parse(jsonText);
        
        const response = await fetch(`${API_BASE}/import`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showAlert('配置已导入', 'success');
            closeImportDialog();
            loadDeviceInfo();
            loadMappings();
        } else {
            showAlert('导入失败', 'error');
        }
    } catch (error) {
        console.error('Error importing config:', error);
        showAlert('导入失败: JSON格式错误', 'error');
    }
}

// Add new mapping
function addNewMapping() {
    currentEditEvent = null;
    document.getElementById('editDialogTitle').textContent = '新建映射';
    document.getElementById('editEventName').value = '';
    document.getElementById('editEventName').disabled = false;
    document.getElementById('editType').value = 'keyboard';
    document.getElementById('editDescription').value = '';
    updateEditForm();
    document.getElementById('editDialog').style.display = 'block';
}

// Edit mapping
function editMapping(eventName) {
    currentEditEvent = eventName;
    const mapping = mappingsData[eventName];
    
    document.getElementById('editDialogTitle').textContent = '编辑映射';
    document.getElementById('editEventName').value = eventName;
    document.getElementById('editEventName').disabled = true;
    document.getElementById('editType').value = mapping.type;
    document.getElementById('editDescription').value = mapping.description || '';
    
    updateEditForm();
    
    // Fill in type-specific fields
    if (mapping.type === 'keyboard') {
        document.getElementById('editKey').value = mapping.key;
    } else if (mapping.type === 'keyboard_combo') {
        document.getElementById('editCombo').value = mapping.combo.join(', ');
    } else if (mapping.type === 'dpad_horizontal' || mapping.type === 'dpad_vertical') {
        document.getElementById('editPositiveKey').value = mapping.positive_key;
        document.getElementById('editNegativeKey').value = mapping.negative_key;
    }
    
    document.getElementById('editDialog').style.display = 'block';
}

// Update edit form based on type
function updateEditForm() {
    const type = document.getElementById('editType').value;
    const fieldsContainer = document.getElementById('editFormFields');
    
    let html = '';
    
    if (type === 'keyboard') {
        html = `
            <div class="form-group">
                <label>按键:</label>
                <input type="text" id="editKey" required placeholder="例如: SPACE, A, ENTER">
            </div>
        `;
    } else if (type === 'keyboard_combo') {
        html = `
            <div class="form-group">
                <label>组合键 (逗号分隔):</label>
                <input type="text" id="editCombo" required placeholder="例如: LEFTCTRL, C">
            </div>
        `;
    } else if (type === 'dpad_horizontal' || type === 'dpad_vertical') {
        html = `
            <div class="form-group">
                <label>正方向按键:</label>
                <input type="text" id="editPositiveKey" required placeholder="例如: RIGHT, DOWN">
            </div>
            <div class="form-group">
                <label>负方向按键:</label>
                <input type="text" id="editNegativeKey" required placeholder="例如: LEFT, UP">
            </div>
        `;
    }
    
    fieldsContainer.innerHTML = html;
}

// Close edit dialog
function closeEditDialog() {
    document.getElementById('editDialog').style.display = 'none';
}

// Save mapping
async function saveMapping(event) {
    event.preventDefault();
    
    const eventName = document.getElementById('editEventName').value;
    const type = document.getElementById('editType').value;
    const description = document.getElementById('editDescription').value;
    
    let mapping = {
        type: type,
        description: description
    };
    
    // Add type-specific fields
    if (type === 'keyboard') {
        mapping.key = document.getElementById('editKey').value.toUpperCase();
    } else if (type === 'keyboard_combo') {
        const combo = document.getElementById('editCombo').value;
        mapping.combo = combo.split(',').map(k => k.trim().toUpperCase());
    } else if (type === 'dpad_horizontal' || type === 'dpad_vertical') {
        mapping.positive_key = document.getElementById('editPositiveKey').value.toUpperCase();
        mapping.negative_key = document.getElementById('editNegativeKey').value.toUpperCase();
    }
    
    try {
        const response = await fetch(`${API_BASE}/mappings/${eventName}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(mapping)
        });
        
        if (response.ok) {
            showAlert('映射已保存', 'success');
            closeEditDialog();
            loadMappings();
        } else {
            showAlert('保存失败', 'error');
        }
    } catch (error) {
        console.error('Error saving mapping:', error);
        showAlert('保存失败', 'error');
    }
}

// Delete mapping
async function deleteMapping(eventName) {
    if (!confirm(`确定要删除映射 "${eventName}" 吗？`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/mappings/${eventName}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showAlert('映射已删除', 'success');
            loadMappings();
        } else {
            showAlert('删除失败', 'error');
        }
    } catch (error) {
        console.error('Error deleting mapping:', error);
        showAlert('删除失败', 'error');
    }
}

// Show alert message
function showAlert(message, type) {
    const alertClass = type === 'success' ? 'alert-success' : 
                       type === 'error' ? 'alert-error' : 'alert-info';
    
    const alert = document.createElement('div');
    alert.className = `alert ${alertClass}`;
    alert.textContent = message;
    
    document.body.insertBefore(alert, document.body.firstChild);
    
    setTimeout(() => {
        alert.remove();
    }, 3000);
}
