# Joystick Converter / 手柄输入转换站

将无宏定义的手柄输入转换为自定义的宏定义，并提供方便的网页服务修改配置文件。

Convert non-macro joystick input to custom macro definitions with a convenient web interface for configuration management.

## 项目特点 / Features

- 🎮 支持任意USB手柄输入 / Support any USB joystick input
- ⌨️ 自定义按键映射为键盘/鼠标宏 / Custom button mapping to keyboard/mouse macros
- 🌐 友好的Web配置界面 / User-friendly web configuration interface
- 🔄 热重载配置无需重启 / Hot-reload configuration without restart
- 📝 JSON配置文件易于编辑 / Easy-to-edit JSON configuration files
- 🚀 开机自动启动 / Auto-start on boot

## 硬件推荐 / Hardware Recommendation

### 推荐方案 1: Raspberry Pi Zero 2 W (最佳性价比)

**优点:**
- ✅ 内置WiFi，方便网页访问
- ✅ USB OTG支持，可模拟USB HID设备
- ✅ 价格便宜（约15美元）
- ✅ 完整的Linux系统，驱动齐全
- ✅ 大量社区支持和类似项目
- ✅ 无需焊接，即插即用
- ✅ 低功耗，可用移动电源供电

**硬件需求:**
- Raspberry Pi Zero 2 W 主板
- Micro SD卡（8GB以上）
- USB OTG转接线（Micro USB转USB-A母口）
- 5V 2A电源适配器或移动电源

### 推荐方案 2: Raspberry Pi 4B (性能更强)

**优点:**
- ✅ 更强的性能，支持更多手柄同时连接
- ✅ 多个USB接口，无需转接线
- ✅ 更快的网页响应速度
- ✅ 同样支持USB Gadget模式

**硬件需求:**
- Raspberry Pi 4B (2GB版本即可)
- Micro SD卡（16GB以上）
- USB-C电源适配器（5V 3A）
- 普通USB线连接到目标设备

### 其他可选方案

- **Orange Pi Zero**: 更便宜的替代品
- **Raspberry Pi 3B+**: 中等性能选择

## 系统架构 / Architecture

```
┌─────────────────┐
│  USB Joystick   │
│   (Input)       │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│  Input Handler      │
│  (evdev/pygame)     │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Mapping Engine     │
│  (JSON Config)      │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Output Handler     │
│  (USB HID Gadget)   │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Target Device      │
│  (PC/Console)       │
└─────────────────────┘

┌─────────────────────┐
│  Web Interface      │
│  (Flask)            │
│  :8080              │
└─────────────────────┘
```

## 快速开始 / Quick Start

### 1. 系统安装

```bash
# 下载并烧录 Raspberry Pi OS Lite
# https://www.raspberrypi.org/software/

# 首次启动后，更新系统
sudo apt update && sudo apt upgrade -y

# 克隆项目
git clone https://github.com/Maxinyu-github/joystick_converter.git
cd joystick_converter

# 运行安装脚本
sudo bash install.sh
```

### 2. 配置USB Gadget模式

安装脚本会自动配置USB Gadget模式，使树莓派能够模拟USB键盘设备。

### 3. 启动服务

```bash
# 启动转换服务
sudo systemctl start joystick-converter

# 开机自启动
sudo systemctl enable joystick-converter

# 启动Web服务
sudo systemctl start joystick-web
sudo systemctl enable joystick-web
```

### 4. 访问Web界面

在浏览器中打开：`http://树莓派IP地址:8080`

## 配置说明 / Configuration

配置文件位于 `config/mappings.json`

### 示例配置

```json
{
  "device_name": "My Controller",
  "mappings": {
    "BTN_A": {
      "type": "keyboard",
      "key": "SPACE"
    },
    "BTN_B": {
      "type": "keyboard",
      "key": "ESC"
    },
    "BTN_X": {
      "type": "keyboard",
      "combo": ["LEFTCTRL", "C"]
    },
    "ABS_X": {
      "type": "mouse_move",
      "axis": "x",
      "sensitivity": 1.5
    },
    "ABS_HAT0X": {
      "type": "keyboard",
      "positive_key": "RIGHT",
      "negative_key": "LEFT"
    }
  }
}
```

### 支持的映射类型

- `keyboard`: 单个按键
- `keyboard_combo`: 组合键（如Ctrl+C）
- `mouse_move`: 鼠标移动
- `mouse_button`: 鼠标按键
- `macro`: 按键序列宏

## 使用场景 / Use Cases

1. **游戏控制器增强**: 为不支持手柄的游戏添加手柄支持
2. **辅助功能**: 将手柄映射为键鼠，方便行动不便用户
3. **自定义宏**: 在游戏中使用复杂的按键宏
4. **多平台兼容**: 将不兼容的手柄转换为标准HID设备

## 技术栈 / Tech Stack

- **Python 3**: 主要编程语言
- **evdev**: Linux输入设备处理
- **Flask**: Web框架
- **USB Gadget**: Linux USB设备模拟
- **systemd**: 服务管理

## 文件结构 / File Structure

```
joystick_converter/
├── README.md                 # 项目说明
├── HARDWARE_GUIDE.md         # 硬件设置指南
├── install.sh                # 安装脚本
├── src/                      # 源代码
│   ├── input_handler.py      # 输入处理
│   ├── mapping_engine.py     # 映射引擎
│   ├── output_handler.py     # 输出处理
│   └── web_server.py         # Web服务器
├── config/                   # 配置文件
│   ├── mappings.json         # 按键映射配置
│   └── examples/             # 示例配置
├── web/                      # Web界面
│   ├── static/               # 静态资源
│   └── templates/            # HTML模板
├── systemd/                  # 系统服务配置
│   ├── joystick-converter.service
│   └── joystick-web.service
└── requirements.txt          # Python依赖
```

## 故障排除 / Troubleshooting

### 手柄无法识别

```bash
# 检查手柄是否连接
ls /dev/input/
sudo evtest
```

### USB Gadget模式未启用

```bash
# 检查模块是否加载
lsmod | grep libcomposite
sudo modprobe libcomposite
```

### Web界面无法访问

```bash
# 检查服务状态
sudo systemctl status joystick-web
# 检查防火墙
sudo ufw allow 8080
```

## 贡献 / Contributing

欢迎提交Issue和Pull Request！

## 许可证 / License

MIT License

## 相关项目 / Related Projects

- [Raspberry Pi USB Gadget](https://www.raspberrypi.org/documentation/computers/configuration.html#usb-gadget-mode)
- [Python evdev](https://python-evdev.readthedocs.io/)
- [QMK Firmware](https://qmk.fm/) - 键盘固件，类似的宏功能

## 支持 / Support

如有问题，请提交Issue或联系作者。
