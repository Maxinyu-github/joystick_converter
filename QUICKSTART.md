# 快速开始指南 / Quick Start Guide

> 5分钟上手使用手柄转换器！

## 第一步：准备硬件 (5分钟)

### 需要购买的设备

1. **Raspberry Pi Zero 2 W** (¥120)
   - 或者 Raspberry Pi 4B (性能更强，¥280)
   
2. **Micro SD卡** 16GB (¥25)
   - Class 10或更快

3. **USB OTG转接线** (¥5)
   - Micro USB公转USB-A母

4. **电源适配器** 5V 2A (¥15)
   - Micro USB接口

5. **USB数据线** (¥5)
   - 用于连接到目标电脑

**总预算：约¥170**

## 第二步：安装系统 (15分钟)

### 下载并烧录系统

1. 下载 [Raspberry Pi Imager](https://www.raspberrypi.org/software/)

2. 打开软件，选择：
   - 操作系统：Raspberry Pi OS Lite (64-bit)
   - 存储卡：你的SD卡

3. 点击设置图标⚙️，配置：
   - ✅ 启用SSH
   - ✅ 设置用户名：`pi` 密码：`raspberry`
   - ✅ 配置WiFi（SSID和密码）
   - ✅ 设置时区：Asia/Shanghai

4. 点击"写入"，等待完成

### 首次启动

1. 插入SD卡到树莓派
2. 连接电源
3. 等待2-3分钟启动

## 第三步：连接树莓派 (5分钟)

### 找到树莓派IP地址

**方法1：路由器管理页面**
- 登录路由器，查看设备列表
- 找到名为 `raspberrypi` 的设备

**方法2：使用mDNS**
```bash
ping raspberrypi.local
```

### SSH连接

```bash
ssh pi@树莓派IP地址
# 或
ssh pi@raspberrypi.local

# 密码：raspberry (首次登录后建议修改)
```

## 第四步：安装软件 (10分钟)

### 一键安装

连接SSH后，运行：

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 克隆项目
git clone https://github.com/Maxinyu-github/joystick_converter.git
cd joystick_converter

# 运行安装脚本
sudo bash install.sh

# 安装完成后重启
sudo reboot
```

等待重启完成（约1分钟）。

## 第五步：启动服务 (2分钟)

重新SSH连接后：

```bash
# 启动转换服务
sudo systemctl start joystick-converter
sudo systemctl start joystick-web

# 设置开机自启动
sudo systemctl enable joystick-converter
sudo systemctl enable joystick-web

# 检查服务状态
sudo systemctl status joystick-converter
sudo systemctl status joystick-web
```

看到 `active (running)` 表示运行正常！

## 第六步：连接设备 (2分钟)

### 物理连接

```
手柄 → (USB OTG线) → 树莓派 Data口
树莓派 Power口 → 电源
树莓派 Data口 → (USB线) → 目标电脑
```

### 验证手柄

```bash
# 列出所有输入设备
ls /dev/input/

# 查看手柄详情
python3 ~/joystick_converter/src/input_handler.py
```

应该能看到你的手柄设备！

## 第七步：配置映射 (5分钟)

### 访问Web界面

1. 在浏览器打开：
   ```
   http://树莓派IP:8080
   ```

2. 你会看到配置界面！

### 创建第一个映射

1. 点击 **"➕ 新建映射"**

2. 填写：
   - 事件名称：`BTN_A` (A键)
   - 类型：`keyboard` (键盘)
   - 按键：`SPACE` (空格)
   - 描述：`跳跃`

3. 点击 **"保存"**

### 测试映射

1. 按下手柄的A键
2. 目标电脑应该接收到空格键输入
3. 成功！🎉

## 常用配置示例

### 游戏配置

```
A键 → 空格 (跳跃)
B键 → ESC (退出)
X键 → E (互动)
Y键 → R (换弹)
方向键 → WASD (移动)
```

### 办公配置

```
X键 → Ctrl+C (复制)
Y键 → Ctrl+V (粘贴)
A键 → Enter (确认)
B键 → ESC (取消)
```

## 故障排除

### 手柄无法识别

```bash
# 检查USB连接
lsusb

# 查看输入设备
ls /dev/input/

# 测试手柄
sudo evtest
```

### 目标电脑无法识别树莓派

1. 检查USB线是否为**数据线**（不是充电线）
2. 确认使用正确的USB口（Data口）
3. 查看HID设备：`ls /dev/hidg*`

### Web界面无法访问

```bash
# 检查服务状态
sudo systemctl status joystick-web

# 检查端口
sudo netstat -tlnp | grep 8080

# 重启服务
sudo systemctl restart joystick-web
```

### 映射不生效

```bash
# 重启转换器
sudo systemctl restart joystick-converter

# 查看日志
sudo journalctl -u joystick-converter -f
```

## 下一步

现在你已经成功设置了手柄转换器！

**进阶功能：**
- 📖 阅读 [USAGE.md](USAGE.md) 了解所有功能
- 🔧 阅读 [HARDWARE_GUIDE.md](HARDWARE_GUIDE.md) 了解硬件详情
- 💡 查看 `config/examples/` 中的示例配置
- 🎮 为不同游戏创建多个配置文件

**获取帮助：**
- 📝 查看 [项目文档](PROJECT_SUMMARY.md)
- 🐛 [提交Issue](https://github.com/Maxinyu-github/joystick_converter/issues)
- 💬 加入讨论

## 预计时间总结

| 步骤 | 时间 |
|------|------|
| 准备硬件 | 5分钟 (到货时间除外) |
| 安装系统 | 15分钟 |
| 连接树莓派 | 5分钟 |
| 安装软件 | 10分钟 |
| 启动服务 | 2分钟 |
| 连接设备 | 2分钟 |
| 配置映射 | 5分钟 |
| **总计** | **约45分钟** |

享受你的手柄转换器吧！🎮✨
