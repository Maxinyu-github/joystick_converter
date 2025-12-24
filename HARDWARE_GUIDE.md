# 硬件设置指南 / Hardware Setup Guide

## 硬件采购清单 / Shopping List

### 方案 1: Raspberry Pi Zero 2 W (推荐新手)

| 项目 | 说明 | 参考价格 | 购买链接 |
|------|------|----------|----------|
| Raspberry Pi Zero 2 W | 主板 | ¥120 | 淘宝/树莓派官方 |
| Micro SD卡 | 16GB Class 10 | ¥25 | 京东/淘宝 |
| USB OTG线 | Micro USB公转USB-A母 | ¥5 | 淘宝 |
| 电源适配器 | 5V 2.5A Micro USB | ¥15 | 淘宝 |
| 散热片 | 可选 | ¥5 | 淘宝 |
| **总计** | | **¥170** | |

### 方案 2: Raspberry Pi 4B (性能更强)

| 项目 | 说明 | 参考价格 | 购买链接 |
|------|------|----------|----------|
| Raspberry Pi 4B 2GB | 主板 | ¥280 | 淘宝/树莓派官方 |
| Micro SD卡 | 16GB Class 10 | ¥25 | 京东/淘宝 |
| USB-C电源适配器 | 5V 3A | ¥25 | 淘宝 |
| USB-A数据线 | 用于连接目标设备 | ¥10 | 淘宝 |
| 外壳 | 可选 | ¥20 | 淘宝 |
| **总计** | | **¥360** | |

## 硬件连接图 / Hardware Connection

### Raspberry Pi Zero 2 W 连接方式

```
                                    ┌─────────────────┐
                                    │   Power Bank    │
                                    │   或电源适配器   │
                                    └────────┬────────┘
                                             │
                                    ┌────────▼────────┐
                                    │   Micro USB     │
                                    │   (Power)       │
┌──────────────┐                    ├─────────────────┤
│  USB 手柄    │                    │  Raspberry Pi   │
│  Joystick    │                    │   Zero 2 W      │
└──────┬───────┘                    ├─────────────────┤
       │                            │   Micro USB     │
       │    ┌─────────────┐        │   (Data+OTG)    │
       └────►  USB OTG转   ├────────┴─────────────────┘
            │   接线       │                │
            └──────────────┘                │
                                            │
                                   ┌────────▼────────┐
                                   │   目标设备 PC    │
                                   │   或游戏机       │
                                   └─────────────────┘
```

### Raspberry Pi 4B 连接方式

```
                               ┌─────────────────┐
                               │  USB-C 电源     │
                               └────────┬────────┘
                                        │
┌──────────────┐              ┌─────────▼──────────┐
│  USB 手柄    │              │  Raspberry Pi 4B   │
│  Joystick    ├──────────────►  USB 2.0 Port      │
└──────────────┘              │                    │
                              │  USB-C Port (Data) ├────┐
                              └────────────────────┘    │
                                                         │
                                                ┌────────▼────────┐
                                                │   目标设备 PC    │
                                                └─────────────────┘
```

## 详细设置步骤 / Detailed Setup Steps

### 第一步：准备SD卡

1. **下载系统镜像**
   - 访问 https://www.raspberrypi.org/software/
   - 下载 Raspberry Pi OS Lite (64-bit) - 无需桌面环境
   - 或使用 Raspberry Pi Imager 工具

2. **烧录镜像**
   ```bash
   # 使用 Raspberry Pi Imager (推荐)
   # 或使用 dd 命令 (Linux/Mac)
   sudo dd if=raspios-lite.img of=/dev/sdX bs=4M status=progress
   ```

3. **启用SSH (无屏幕操作)**
   ```bash
   # 在SD卡boot分区创建空文件
   touch /path/to/boot/ssh
   ```

4. **配置WiFi (可选)**
   ```bash
   # 在boot分区创建 wpa_supplicant.conf
   cat > /path/to/boot/wpa_supplicant.conf << EOF
   country=CN
   ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
   update_config=1

   network={
       ssid="你的WiFi名称"
       psk="你的WiFi密码"
       key_mgmt=WPA-PSK
   }
   EOF
   ```

### 第二步：首次启动

1. **插入SD卡并上电**
   - Raspberry Pi Zero 2 W: 使用5V 2A以上电源
   - Raspberry Pi 4B: 使用5V 3A USB-C电源

2. **找到树莓派IP地址**
   ```bash
   # 方法1: 路由器管理页面查看
   # 方法2: 使用nmap扫描
   nmap -sn 192.168.1.0/24
   
   # 方法3: 使用hostname (如果配置了mDNS)
   ping raspberrypi.local
   ```

3. **SSH登录**
   ```bash
   ssh pi@树莓派IP地址
   # 默认密码: raspberry
   # 首次登录后务必修改密码
   passwd
   ```

### 第三步：系统配置

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 配置时区
sudo raspi-config
# 选择: Localisation Options -> Timezone -> Asia -> Shanghai

# 配置主机名 (可选)
sudo hostnamectl set-hostname joystick-converter

# 扩展文件系统 (首次必须)
sudo raspi-config
# 选择: Advanced Options -> Expand Filesystem
sudo reboot
```

### 第四步：启用USB Gadget模式

#### Raspberry Pi Zero 2 W / Pi 4B 配置

1. **编辑 /boot/config.txt**
   ```bash
   sudo nano /boot/config.txt
   # 在文件末尾添加:
   dtoverlay=dwc2
   ```

2. **编辑 /boot/cmdline.txt**
   ```bash
   sudo nano /boot/cmdline.txt
   # 在 rootwait 后面添加 (注意是同一行):
   modules-load=dwc2,libcomposite
   ```

3. **重启**
   ```bash
   sudo reboot
   ```

### 第五步：安装项目

```bash
# 安装Git
sudo apt install git -y

# 克隆项目
cd ~
git clone https://github.com/Maxinyu-github/joystick_converter.git
cd joystick_converter

# 运行安装脚本
sudo bash install.sh

# 脚本会自动完成：
# - 安装Python依赖
# - 配置USB Gadget
# - 设置systemd服务
# - 创建配置文件
```

### 第六步：连接手柄

1. **连接USB手柄**
   - Pi Zero 2 W: 通过OTG转接线连接手柄到Data口
   - Pi 4B: 直接连接到任意USB 2.0/3.0口

2. **验证手柄识别**
   ```bash
   # 列出输入设备
   ls /dev/input/
   
   # 查看事件设备
   cat /proc/bus/input/devices
   
   # 测试手柄输入 (按Ctrl+C退出)
   sudo evtest
   # 选择你的手柄设备编号
   ```

3. **查看手柄详细信息**
   ```bash
   # 安装evtest工具
   sudo apt install evtest -y
   
   # 运行evtest并选择设备
   sudo evtest
   ```

### 第七步：连接目标设备

1. **Raspberry Pi Zero 2 W**
   - 使用Micro USB数据线连接Data口到PC
   - PC会识别为USB键盘设备

2. **Raspberry Pi 4B**
   - 使用USB-C数据线连接USB-C口到PC
   - 或配置网络模式，通过WiFi工作

### 第八步：启动服务

```bash
# 启动转换服务
sudo systemctl start joystick-converter
sudo systemctl enable joystick-converter

# 启动Web服务
sudo systemctl start joystick-web
sudo systemctl enable joystick-web

# 检查服务状态
sudo systemctl status joystick-converter
sudo systemctl status joystick-web
```

## 测试验证 / Testing

### 1. 测试手柄输入

```bash
# 运行测试脚本
cd ~/joystick_converter
python3 src/test_input.py

# 按下手柄按键，应该看到输出
```

### 2. 测试USB输出

```bash
# 检查HID设备是否创建
ls /dev/hidg*

# 应该看到 /dev/hidg0
```

### 3. 访问Web界面

```bash
# 获取树莓派IP
hostname -I

# 在浏览器访问
http://树莓派IP:8080
```

## 常见问题 / FAQ

### Q1: USB Gadget模式不工作？

**检查内核模块:**
```bash
lsmod | grep dwc2
lsmod | grep libcomposite
```

**手动加载模块:**
```bash
sudo modprobe dwc2
sudo modprobe libcomposite
```

### Q2: 手柄无法识别？

**检查权限:**
```bash
sudo usermod -a -G input pi
sudo reboot
```

**检查设备:**
```bash
lsusb
dmesg | grep -i usb
```

### Q3: 目标设备无法识别树莓派？

**检查USB线:**
- 确保使用**数据线**而非**充电线**
- 某些充电线只有电源线，没有数据线

**检查连接口:**
- Pi Zero: 必须使用标记为"USB"或"Data"的口
- Pi 4: 使用USB-C口

### Q4: Web界面无法访问？

**检查端口:**
```bash
sudo netstat -tlnp | grep 8080
```

**检查防火墙:**
```bash
sudo ufw status
sudo ufw allow 8080
```

### Q5: 性能不足，延迟高？

**优化建议:**
- 使用Pi 4代替Pi Zero
- 降低配置中的轮询频率
- 关闭不必要的系统服务
- 超频 (需要好的散热)

## 进阶配置 / Advanced Configuration

### 超频 (提升性能)

```bash
sudo nano /boot/config.txt

# Pi Zero 2 W
over_voltage=2
arm_freq=1200

# Pi 4B
over_voltage=6
arm_freq=2000

# 添加散热
temp_limit=80
```

### 设置静态IP

```bash
sudo nano /etc/dhcpcd.conf

# 添加:
interface wlan0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=8.8.8.8
```

### 开启串口调试 (高级)

```bash
sudo raspi-config
# Interface Options -> Serial Port
# Login shell: No
# Serial port hardware: Yes
```

## 购买建议 / Purchase Tips

1. **官方授权商**: 避免山寨板，确保品质
2. **套件优先**: 新手建议购买含外壳、散热、电源的套件
3. **备用SD卡**: 建议准备2张SD卡，一张做备份
4. **品牌电源**: 电源不稳定会导致各种问题
5. **质量OTG线**: 劣质OTG线可能导致识别问题

## 推荐配件 / Recommended Accessories

- **散热片/风扇**: 长时间运行必备
- **外壳**: 保护电路板
- **USB Hub**: 连接多个手柄 (Pi 4B)
- **显示器**: 调试时方便 (可选)
- **读卡器**: 方便烧录SD卡

## 总结 / Summary

按照本指南，即使没有任何硬件和嵌入式知识，也能顺利完成硬件选择和设置。关键点：

1. ✅ 选择Raspberry Pi - 无需焊接，即插即用
2. ✅ 使用Raspberry Pi OS - 驱动完全，社区支持好
3. ✅ USB Gadget模式 - 标准Linux功能，稳定可靠
4. ✅ Python开发 - 简单易学，库丰富

有问题随时在Issue中提问！
