# PanoViewer

[English](README.en.md) | 简体中文

免费开源、完全离线的 360° 全景照片查看器。无需上传照片，打开即可从展开、小行星、水晶球和隧道四种视角浏览等距圆柱投影全景图。

> 当前版本：**1.0.1** · 作者：**梁晓辉 Liang Xiaohui** · [MIT License](LICENSE)

![PanoViewer 小行星视图](assets/screenshots/tiny-planet.png)

<p align="center">
  <img src="assets/screenshots/unfold.png" width="32%" alt="展开视图">
  <img src="assets/screenshots/crystal-globe.png" width="32%" alt="水晶球视图">
  <img src="assets/screenshots/tunnel.png" width="32%" alt="隧道视图">
</p>

<p align="center"><sub>示例全景照片由梁晓辉拍摄于新疆。</sub></p>

## 下载与使用

### Windows

1. 在 [Releases](https://github.com/liang-xiaohui/PanoViewer/releases/latest) 下载 `PanoViewer-Windows-x64.exe`。
2. 双击运行，选择一张 360° 全景照片。
3. 也可将照片拖到 EXE 上，或在“打开方式”中选择 PanoViewer。

Windows 首次打开从 GitHub 下载的未签名程序时，SmartScreen 可能显示提示。请确认文件来自本项目的 GitHub Releases。

> v1.0.0 的 Windows 程序尚未进行商业代码签名。每个 Release 都提供 `SHA256SUMS.txt` 供完整性校验。

### macOS

1. 从 [Releases](https://github.com/liang-xiaohui/PanoViewer/releases/latest) 下载 `PanoViewer-macOS.dmg`。
2. 打开 DMG，将 PanoViewer 拖入“应用程序”，然后双击运行或把全景照片拖到 App 图标上。
3. 当前 macOS App 尚未经过 Apple 公证；首次运行如被拦截，请先在 Finder 中右键 App 并选择“打开”。如果仍无法打开，请前往“系统设置 → 隐私与安全性”，找到 PanoViewer 的安全提示并选择“仍要打开”。

### iPhone / iPad 快捷指令

1. 从 [Releases](https://github.com/liang-xiaohui/PanoViewer/releases/latest) 下载并安装 `PanoViewer.shortcut`。
2. 在“照片”中打开一张 360° 全景照片，点击“分享”，然后选择 PanoViewer。
3. 快捷指令会下载查看器模板、在设备本地处理照片，并直接在 Safari 网页视图中打开。照片不会上传，但运行时需要连接 GitHub 下载模板。

### Linux / 其他平台

从 Releases 下载 `PanoViewer-Standalone.html`，用支持 WebGL 的现代浏览器打开，再点击或拖入照片。该文件已内置所需程序，不需要网络或安装依赖。

macOS 和 Linux 用户也可从源码使用 Python 启动器：

```bash
python3 scripts/build.py
python3 scripts/pano.py /path/to/panorama.jpg
```

## 主要功能

- 展开、小行星、水晶球和隧道四种视角
- 鼠标、触摸和滚轮/捏合操作
- 小行星与隧道的自由俯仰和投影锁定
- 当前画面 PNG 截图
- JPG、JPEG、PNG、WebP 和 GIF 图片
- 单文件、无服务器、无云端依赖

PanoViewer 面向 2:1 等距圆柱投影（equirectangular）全景照片，例如 360 相机、无人机或全景拼接软件的输出。

## 隐私

PanoViewer 在本地读取和渲染照片，不会上传图片，不收集使用数据，也不包含分析或广告代码。Windows 程序会在系统临时目录生成一个用于浏览器显示的 HTML 文件。

## 从源码构建

需要 Python 3。Windows EXE 另需 Windows 自带的 .NET Framework C# 编译器。

```powershell
# 通用离线 HTML
py -3 scripts\build.py

# Windows EXE
powershell -ExecutionPolicy Bypass -File scripts\build_windows.ps1
```

产物位于 `dist/`。更多实现、测试和发布说明见 [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)。

## 贡献

欢迎提交 Issue 和 Pull Request。完整流程见 [CONTRIBUTING.md](CONTRIBUTING.md)；安全问题请按 [SECURITY.md](SECURITY.md) 私下报告。报告普通问题时，请尽量附上操作系统与浏览器版本、可复现步骤、图片格式与尺寸，以及屏幕截图或错误信息。

在提交代码前，请至少运行一次构建，并用 `tools/test_pano.png` 检查四种视角。

## 许可证与第三方代码

PanoViewer 由梁晓辉（Liang Xiaohui）以 [MIT License](LICENSE) 开源。

`vendor/three.min.js` 是 three.js r128，同样使用 MIT License，版权归 mrdoob 及 three.js 贡献者所有。

---

PanoViewer is a free, open-source, fully offline 360° panorama viewer for Windows and modern WebGL browsers. Download the latest build from [GitHub Releases](https://github.com/liang-xiaohui/PanoViewer/releases/latest). Photos stay on your device.
