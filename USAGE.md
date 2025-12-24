# 使用指南 / User Guide

## 目录 / Table of Contents

1. [快速上手](#快速上手)
2. [配置说明](#配置说明)
3. [Web界面使用](#web界面使用)
4. [命令行工具](#命令行工具)
5. [高级功能](#高级功能)
6. [常见问题](#常见问题)

## 快速上手

### 第一次使用

1. **安装系统** (参见 HARDWARE_GUIDE.md)
   ```bash
   sudo bash install.sh
   sudo reboot
   ```

2. **启动服务**
   ```bash
   sudo systemctl start joystick-converter
   sudo systemctl start joystick-web
   ```

3. **访问Web界面**
   - 打开浏览器访问: `http://树莓派IP:8080`
   - 默认配置已包含基本的按键映射

4. **测试手柄**
   - 连接USB手柄到树莓派
   - 在Web界面查看设备信息
   - 按下按键测试映射是否正确

## 配置说明

### 配置文件格式

配置文件位于 `config/mappings.json`，使用JSON格式：

```json
{
  "device_name": "设备名称",
  "mappings": {
    "事件名": {
      "type": "映射类型",
      ...其他参数
    }
  }
}
```

### 支持的事件名

**按钮事件:**
- `BTN_A`, `BTN_B`, `BTN_X`, `BTN_Y` - 四个主按键
- `BTN_TL`, `BTN_TR` - 左右肩键
- `BTN_START`, `BTN_SELECT` - 开始/选择键
- `BTN_THUMBL`, `BTN_THUMBR` - 左右摇杆按下

**轴向事件:**
- `ABS_X`, `ABS_Y` - 左摇杆 X/Y 轴
- `ABS_RX`, `ABS_RY` - 右摇杆 X/Y 轴
- `ABS_Z`, `ABS_RZ` - 扳机 (L2/R2)
- `ABS_HAT0X`, `ABS_HAT0Y` - 方向键 X/Y 轴

### 映射类型

#### 1. keyboard - 单键映射

映射单个按键：

```json
{
  "type": "keyboard",
  "key": "SPACE",
  "description": "跳跃"
}
```

支持的按键名见 [按键对照表](#按键对照表)

#### 2. keyboard_combo - 组合键

映射组合键（如 Ctrl+C）：

```json
{
  "type": "keyboard_combo",
  "combo": ["LEFTCTRL", "C"],
  "description": "复制"
}
```

#### 3. dpad_horizontal - 水平方向键

映射 D-Pad 或摇杆的水平方向：

```json
{
  "type": "dpad_horizontal",
  "positive_key": "RIGHT",
  "negative_key": "LEFT",
  "description": "左右移动"
}
```

#### 4. dpad_vertical - 垂直方向键

映射 D-Pad 或摇杆的垂直方向：

```json
{
  "type": "dpad_vertical",
  "positive_key": "DOWN",
  "negative_key": "UP",
  "description": "上下移动"
}
```

### 按键对照表

常用按键名称：

| 类别 | 按键名 |
|------|--------|
| **字母** | A-Z |
| **数字** | 0-9 (注意0在最后) |
| **功能键** | F1-F12 |
| **方向键** | UP, DOWN, LEFT, RIGHT |
| **控制键** | ENTER, ESC, BACKSPACE, TAB, SPACE |
| **修饰键** | LEFTCTRL, RIGHTCTRL, LEFTSHIFT, RIGHTSHIFT, LEFTALT, RIGHTALT |
| **特殊键** | HOME, END, PAGEUP, PAGEDOWN, INSERT, DELETE |

完整列表参见 `src/mapping_engine.py` 的 `KEY_MAP`

## Web界面使用

### 主界面功能

1. **设备信息**
   - 显示当前设备名称
   - 显示映射数量
   - 显示配置文件路径

2. **操作按钮**
   - **🔄 重新加载**: 从文件重新加载配置
   - **📤 导出配置**: 下载配置为JSON文件
   - **📥 导入配置**: 从JSON文件导入配置
   - **➕ 新建映射**: 添加新的按键映射

3. **映射列表**
   - 查看所有按键映射
   - 搜索功能：按事件名搜索
   - 类型过滤：按映射类型过滤
   - 编辑/删除：每个映射可编辑或删除

### 创建新映射

1. 点击 **"➕ 新建映射"** 按钮
2. 填写表单：
   - **事件名称**: 选择要映射的输入事件（如 BTN_A）
   - **类型**: 选择映射类型
   - **具体参数**: 根据类型填写（如按键名）
   - **描述**: 可选，便于记忆
3. 点击 **"保存"**

### 编辑映射

1. 找到要编辑的映射
2. 点击 **"✏️ 编辑"** 按钮
3. 修改参数
4. 点击 **"保存"**

### 导入/导出配置

**导出配置:**
1. 点击 **"📤 导出配置"**
2. 浏览器会下载 `joystick_mappings.json` 文件

**导入配置:**
1. 点击 **"📥 导入配置"**
2. 在文本框中粘贴JSON内容
3. 点击 **"导入"**

## 命令行工具

### 查看输入设备

```bash
cd ~/joystick_converter
python3 src/input_handler.py
```

输出所有可用的输入设备及其类型。

### 测试手柄输入

```bash
python3 src/input_handler.py /dev/input/event0
```

显示手柄的实时输入事件。

### 测试映射配置

```bash
python3 src/mapping_engine.py
```

加载并显示当前配置。

### 手动运行转换器

```bash
sudo python3 src/main.py
```

手动运行转换器（需要root权限）。

### 查看日志

```bash
# 查看转换器日志
sudo journalctl -u joystick-converter -f

# 查看Web服务日志
sudo journalctl -u joystick-web -f
```

## 高级功能

### 多配置文件

创建不同场景的配置文件：

```bash
# 游戏配置
cp config/mappings.json config/gaming.json

# 办公配置
cp config/examples/productivity_mappings.json config/office.json

# 切换配置
sudo systemctl stop joystick-converter
cp config/gaming.json config/mappings.json
sudo systemctl start joystick-converter
```

### 热重载配置

修改配置后无需重启服务：

```bash
# 方法1: 使用Web界面的"重新加载"按钮

# 方法2: 重启服务
sudo systemctl restart joystick-converter
```

### 调试模式

启用详细日志：

```bash
# 临时启用
sudo LOGLEVEL=DEBUG python3 src/main.py

# 修改服务配置
sudo nano /etc/systemd/system/joystick-converter.service
# 在 [Service] 下添加：
# Environment="LOGLEVEL=DEBUG"
```

### 自定义USB设备信息

修改 `src/output_handler.py` 中的设备描述符：

```python
# 修改厂商ID和产品ID
with open(f"{gadget_path}/idVendor", "w") as f:
    f.write("0x1234")  # 自定义厂商ID
with open(f"{gadget_path}/idProduct", "w") as f:
    f.write("0x5678")  # 自定义产品ID
```

### 性能优化

1. **降低CPU使用**
   ```python
   # 在 input_handler.py 中添加延迟
   import time
   for event in self.device.read_loop():
       self.process_event(event)
       time.sleep(0.001)  # 1ms延迟
   ```

2. **使用更快的轮询**
   - 需要修改内核模块参数
   - 适用于需要极低延迟的场景

## 常见问题

### Q: 手柄连接后没有反应

**A:** 检查以下几点：
```bash
# 1. 确认手柄被识别
lsusb

# 2. 查看输入设备
ls /dev/input/
python3 src/input_handler.py

# 3. 检查权限
sudo usermod -a -G input pi
```

### Q: 目标设备无法识别树莓派

**A:** 
1. 确保使用**数据线**而非充电线
2. 检查USB Gadget模式是否启用：
   ```bash
   lsmod | grep dwc2
   lsmod | grep libcomposite
   ```
3. 检查 /dev/hidg0 是否存在

### Q: 映射不生效

**A:**
1. 重启转换器服务：
   ```bash
   sudo systemctl restart joystick-converter
   ```
2. 检查配置文件格式是否正确
3. 查看日志：
   ```bash
   sudo journalctl -u joystick-converter -n 50
   ```

### Q: Web界面无法访问

**A:**
```bash
# 检查服务状态
sudo systemctl status joystick-web

# 检查端口占用
sudo netstat -tlnp | grep 8080

# 检查防火墙
sudo ufw status
sudo ufw allow 8080
```

### Q: 延迟太高

**A:**
1. 使用Raspberry Pi 4代替Zero
2. 超频CPU（需要散热）
3. 关闭不必要的服务
4. 使用USB 2.0口（某些USB 3.0可能有兼容性问题）

### Q: 如何同时连接多个手柄

**A:**
当前版本仅支持单手柄。多手柄支持需要修改代码：
1. 在 `input_handler.py` 中维护多个设备
2. 为每个手柄分配独立的映射配置
3. 需要多个HID Gadget实例

### Q: 可以模拟鼠标吗？

**A:**
当前版本主要支持键盘。鼠标支持需要：
1. 修改HID描述符添加鼠标报告
2. 实现鼠标事件处理
3. 将摇杆映射到鼠标移动

### Q: 如何备份配置

**A:**
```bash
# 备份
cp config/mappings.json config/backup_$(date +%Y%m%d).json

# 恢复
cp config/backup_20240101.json config/mappings.json
sudo systemctl restart joystick-converter
```

## 技巧和最佳实践

1. **定期备份配置**: 使用Web界面导出功能
2. **测试后保存**: 先测试映射是否正确再保存
3. **使用描述字段**: 便于记忆每个按键的作用
4. **创建多个配置**: 为不同游戏/应用准备不同配置
5. **查看示例**: 参考 `config/examples/` 中的示例配置

## 获取帮助

- **GitHub Issues**: https://github.com/Maxinyu-github/joystick_converter/issues
- **查看日志**: `sudo journalctl -u joystick-converter -f`
- **社区支持**: 提交Issue描述你的问题

## 参考资源

- [evdev文档](https://python-evdev.readthedocs.io/)
- [USB HID规范](https://www.usb.org/hid)
- [Flask文档](https://flask.palletsprojects.com/)
- [Raspberry Pi USB Gadget](https://www.raspberrypi.org/documentation/computers/configuration.html#usb-gadget-mode)
