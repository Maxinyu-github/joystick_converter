// API base URL
const API_BASE = '/api';

// Current mappings data
let mappingsData = {};
let currentEditEvent = null;

// Gamepad testing variables
let gamepadConnected = false;
let gamepadIndex = null;
let gamepadAnimationId = null;

// Gamepad testing constants
const BUTTON_OPACITY_MIN = 0.3;
const BUTTON_OPACITY_RANGE = 0.7;
const AXIS_DEADZONE_THRESHOLD = 0.1;

// Backend input detection variables
let backendInputConnected = false;
let backendEventSource = null;
let backendEventLog = [];
const MAX_BACKEND_EVENTS = 50;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_BASE_DELAY = 2000; // 2 seconds

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadDeviceInfo();
    loadMappings();
    initGamepadTester();
    initBackendInputTester();
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

// ============================================
// Gamepad Tester Functions
// ============================================

function initGamepadTester() {
    // Listen for gamepad connection events
    window.addEventListener('gamepadconnected', (e) => {
        console.log('Gamepad connected:', e.gamepad);
        gamepadConnected = true;
        gamepadIndex = e.gamepad.index;
        updateGamepadStatus(e.gamepad);
        startGamepadPolling();
    });

    window.addEventListener('gamepaddisconnected', (e) => {
        console.log('Gamepad disconnected:', e.gamepad);
        gamepadConnected = false;
        gamepadIndex = null;
        updateGamepadStatus(null);
        stopGamepadPolling();
    });

    // Start polling for gamepad state
    pollGamepads();
}

function pollGamepads() {
    // Some browsers require polling to detect gamepad connection
    const gamepads = navigator.getGamepads ? navigator.getGamepads() : [];
    
    for (let i = 0; i < gamepads.length; i++) {
        if (gamepads[i] && !gamepadConnected) {
            gamepadConnected = true;
            gamepadIndex = i;
            updateGamepadStatus(gamepads[i]);
            startGamepadPolling();
            return;
        }
    }
    
    // Continue polling if not connected
    if (!gamepadConnected) {
        requestAnimationFrame(pollGamepads);
    }
}

function updateGamepadStatus(gamepad) {
    const statusDot = document.querySelector('.status-dot');
    const statusText = document.getElementById('gamepadStatusText');
    const gamepadName = document.getElementById('gamepadName');
    
    if (gamepad) {
        statusDot.className = 'status-dot connected';
        statusText.textContent = '手柄已连接';
        gamepadName.textContent = gamepad.id;
        gamepadName.style.display = 'block';
        initGamepadDisplay(gamepad);
    } else {
        statusDot.className = 'status-dot disconnected';
        statusText.textContent = '未连接手柄 - 按下任意手柄按键以连接';
        gamepadName.textContent = '';
        gamepadName.style.display = 'none';
        document.getElementById('buttonsList').innerHTML = '<p class="loading">等待手柄连接...</p>';
        document.getElementById('axesList').innerHTML = '<p class="loading">等待手柄连接...</p>';
    }
}

function initGamepadDisplay(gamepad) {
    // Initialize buttons display
    const buttonsList = document.getElementById('buttonsList');
    buttonsList.innerHTML = '';
    
    for (let i = 0; i < gamepad.buttons.length; i++) {
        const buttonDiv = document.createElement('div');
        buttonDiv.className = 'button-indicator';
        buttonDiv.id = `button-${i}`;
        buttonDiv.innerHTML = `
            <div class="button-visual"></div>
            <div class="button-label">按键 ${i}</div>
            <div class="button-value">0.00</div>
        `;
        buttonsList.appendChild(buttonDiv);
    }
    
    // Initialize axes display
    const axesList = document.getElementById('axesList');
    axesList.innerHTML = '';
    
    // Standard gamepad axis names (fallback to generic names for non-standard controllers)
    const standardAxisNames = ['左摇杆 X', '左摇杆 Y', '右摇杆 X', '右摇杆 Y', 'L2', 'R2', 'D-Pad X', 'D-Pad Y'];
    
    for (let i = 0; i < gamepad.axes.length; i++) {
        const axisDiv = document.createElement('div');
        axisDiv.className = 'axis-indicator';
        axisDiv.id = `axis-${i}`;
        
        // Use standard name if available, otherwise fall back to generic name
        const axisName = i < standardAxisNames.length ? standardAxisNames[i] : `轴向 ${i}`;
        
        axisDiv.innerHTML = `
            <div class="axis-label">${axisName}</div>
            <div class="axis-bar-container">
                <div class="axis-bar" id="axis-bar-${i}"></div>
                <div class="axis-center"></div>
            </div>
            <div class="axis-value">0.00</div>
        `;
        axesList.appendChild(axisDiv);
    }
}

function startGamepadPolling() {
    if (gamepadAnimationId) {
        return; // Already polling
    }
    
    function updateGamepadState() {
        if (!gamepadConnected) {
            gamepadAnimationId = null;
            return;
        }
        
        const gamepads = navigator.getGamepads();
        const gamepad = gamepads[gamepadIndex];
        
        if (!gamepad) {
            gamepadConnected = false;
            updateGamepadStatus(null);
            return;
        }
        
        // Update buttons
        for (let i = 0; i < gamepad.buttons.length; i++) {
            const button = gamepad.buttons[i];
            const buttonDiv = document.getElementById(`button-${i}`);
            
            if (buttonDiv) {
                const visual = buttonDiv.querySelector('.button-visual');
                const valueDisplay = buttonDiv.querySelector('.button-value');
                
                const value = typeof button === 'object' ? button.value : button;
                const pressed = typeof button === 'object' ? button.pressed : button === 1.0;
                
                // Update visual state
                if (pressed) {
                    visual.classList.add('active');
                } else {
                    visual.classList.remove('active');
                }
                
                // Update opacity based on value for pressure-sensitive buttons
                visual.style.opacity = BUTTON_OPACITY_MIN + (value * BUTTON_OPACITY_RANGE);
                valueDisplay.textContent = value.toFixed(2);
            }
        }
        
        // Update axes
        for (let i = 0; i < gamepad.axes.length; i++) {
            const value = gamepad.axes[i];
            const axisDiv = document.getElementById(`axis-${i}`);
            
            if (axisDiv) {
                const bar = document.getElementById(`axis-bar-${i}`);
                const valueDisplay = axisDiv.querySelector('.axis-value');
                
                // Update bar position (value ranges from -1 to 1)
                const percentage = ((value + 1) / 2) * 100;
                bar.style.left = `${percentage}%`;
                
                // Color based on position
                if (Math.abs(value) < AXIS_DEADZONE_THRESHOLD) {
                    bar.style.backgroundColor = '#999';
                } else {
                    bar.style.backgroundColor = '#4CAF50';
                }
                
                valueDisplay.textContent = value.toFixed(2);
            }
        }
        
        gamepadAnimationId = requestAnimationFrame(updateGamepadState);
    }
    
    gamepadAnimationId = requestAnimationFrame(updateGamepadState);
}

function stopGamepadPolling() {
    if (gamepadAnimationId) {
        cancelAnimationFrame(gamepadAnimationId);
        gamepadAnimationId = null;
    }
}

// ============================================
// Backend Input Tester Functions
// ============================================

async function initBackendInputTester() {
    // Load available input devices
    await refreshBackendDevices();
}

async function refreshBackendDevices() {
    try {
        const response = await fetch(`${API_BASE}/input/devices`);
        const data = await response.json();
        
        const selectElement = document.getElementById('backendDeviceSelect');
        selectElement.innerHTML = '';
        
        if (data.devices && data.devices.length > 0) {
            // Add default option
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = '-- 选择设备 --';
            selectElement.appendChild(defaultOption);
            
            // Add devices
            data.devices.forEach(device => {
                const option = document.createElement('option');
                option.value = device.path;
                option.textContent = `${device.name} (${device.path})${device.is_gamepad ? ' [手柄]' : ''}`;
                selectElement.appendChild(option);
            });
            
            showAlert('设备列表已刷新', 'success');
        } else {
            selectElement.innerHTML = '<option value="">未找到输入设备</option>';
            showAlert('未找到输入设备', 'error');
        }
    } catch (error) {
        console.error('Error loading devices:', error);
        showAlert('加载设备列表失败', 'error');
    }
}

async function connectBackendDevice() {
    const selectElement = document.getElementById('backendDeviceSelect');
    const devicePath = selectElement.value;
    
    if (!devicePath) {
        showAlert('请选择一个设备', 'error');
        return;
    }
    
    try {
        // Disconnect existing connection
        if (backendInputConnected) {
            await disconnectBackendDevice();
        }
        
        // Connect to device
        const response = await fetch(`${API_BASE}/input/connect`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({device_path: devicePath})
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            backendInputConnected = true;
            reconnectAttempts = 0; // Reset reconnect counter
            updateBackendStatus(true, data.device_name);
            startBackendEventStream();
            showAlert('已连接到设备', 'success');
        } else {
            showAlert(data.error || '连接失败', 'error');
        }
    } catch (error) {
        console.error('Error connecting to device:', error);
        showAlert('连接设备失败', 'error');
    }
}

async function disconnectBackendDevice() {
    try {
        // Stop event stream
        stopBackendEventStream();
        
        // Disconnect from backend
        await fetch(`${API_BASE}/input/disconnect`, {
            method: 'POST'
        });
        
        backendInputConnected = false;
        reconnectAttempts = 0; // Reset reconnect counter
        updateBackendStatus(false);
        clearBackendEvents();
        showAlert('已断开连接', 'success');
    } catch (error) {
        console.error('Error disconnecting device:', error);
        showAlert('断开连接失败', 'error');
    }
}

function updateBackendStatus(connected, deviceName = '') {
    const statusDot = document.querySelector('#backendInputStatus .status-dot');
    const statusText = document.getElementById('backendInputStatusText');
    const deviceNameDisplay = document.getElementById('backendDeviceName');
    const eventDisplay = document.getElementById('backendEventDisplay');
    
    if (connected) {
        statusDot.className = 'status-dot connected';
        statusText.textContent = '已连接';
        deviceNameDisplay.textContent = deviceName;
        deviceNameDisplay.style.display = 'block';
        eventDisplay.style.display = 'block';
    } else {
        statusDot.className = 'status-dot disconnected';
        statusText.textContent = '未连接设备';
        deviceNameDisplay.textContent = '';
        deviceNameDisplay.style.display = 'none';
        eventDisplay.style.display = 'none';
    }
}

function startBackendEventStream() {
    // Close existing connection
    if (backendEventSource) {
        backendEventSource.close();
    }
    
    // Create new EventSource for SSE
    backendEventSource = new EventSource(`${API_BASE}/input/events`);
    
    backendEventSource.onmessage = function(event) {
        try {
            const eventData = JSON.parse(event.data);
            addBackendEvent(eventData);
            reconnectAttempts = 0; // Reset on successful message
        } catch (error) {
            console.error('Error parsing event data:', error);
            showAlert('接收事件数据时出错', 'error');
        }
    };
    
    backendEventSource.onerror = function(error) {
        console.error('EventSource error:', error);
        if (backendInputConnected && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
            // Exponential backoff: 2s, 4s, 8s, 16s, 32s
            const delay = RECONNECT_BASE_DELAY * Math.pow(2, reconnectAttempts);
            reconnectAttempts++;
            
            console.log(`Attempting to reconnect (${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS}) in ${delay}ms...`);
            
            setTimeout(() => {
                if (backendInputConnected && backendEventSource.readyState === EventSource.CLOSED) {
                    startBackendEventStream();
                }
            }, delay);
        } else if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
            showAlert('事件流连接失败，已达到最大重试次数', 'error');
            backendInputConnected = false;
            updateBackendStatus(false);
        }
    };
}

function stopBackendEventStream() {
    if (backendEventSource) {
        backendEventSource.close();
        backendEventSource = null;
    }
}

function addBackendEvent(eventData) {
    // Add to event log
    backendEventLog.unshift(eventData);
    
    // Keep only recent events
    if (backendEventLog.length > MAX_BACKEND_EVENTS) {
        backendEventLog = backendEventLog.slice(0, MAX_BACKEND_EVENTS);
    }
    
    // Update display
    displayBackendEvents();
}

function displayBackendEvents() {
    const eventsList = document.getElementById('backendEventsList');
    
    if (backendEventLog.length === 0) {
        eventsList.innerHTML = '<p class="loading">等待输入事件...</p>';
        return;
    }
    
    let html = '<div class="events-container">';
    
    // Group recent events by event name for better visualization
    const recentEvents = backendEventLog.slice(0, 10);
    
    recentEvents.forEach(event => {
        const timestamp = new Date(event.timestamp * 1000).toLocaleTimeString();
        const eventClass = event.value === 0 ? 'event-release' : 'event-press';
        
        html += `
            <div class="event-item ${eventClass}">
                <span class="event-name">${event.event_name}</span>
                <span class="event-value">${event.value}</span>
                <span class="event-time">${timestamp}</span>
            </div>
        `;
    });
    
    html += '</div>';
    
    // Add summary of all unique events seen
    const uniqueEvents = [...new Set(backendEventLog.map(e => e.event_name))];
    html += `
        <div class="events-summary">
            <strong>检测到的事件类型 (${uniqueEvents.length}):</strong>
            <div class="event-tags">
                ${uniqueEvents.map(name => `<span class="event-tag">${name}</span>`).join('')}
            </div>
        </div>
    `;
    
    eventsList.innerHTML = html;
}

function clearBackendEvents() {
    backendEventLog = [];
    const eventsList = document.getElementById('backendEventsList');
    eventsList.innerHTML = '<p class="loading">等待输入事件...</p>';
}
