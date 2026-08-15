# PanoViewer — 离线单文件 360° 全景查看器

一个零依赖、双击即用的 360° 全景照片查看器（macOS / iPhone 通用），模仿大疆 App 的四种观赏视角：**展开 / 小行星 / 水晶球 / 隧道**，外加截图导出。

- 输入：等距圆柱投影（equirectangular）全景图，如 DJI 无人机拍摄的 360° 照片
- 输出：单个 HTML 文件，three.js 已内联，**完全离线**可用
- 渲染：WebGL（three.js r128 非模块版），Safari / Chrome 均可

## 功能

| 模式 | 投影本质 | 视觉特征 | 交互 |
|---|---|---|---|
| 展开 | 球内透视 | 正常第一人称环视 | 拖动环视，滚轮/捏合变焦 |
| 小行星 | 极射赤面投影（视线锁天底） | 地面卷成星球充满画面，地平线成圆 | 水平拖动自转，滚轮/捏合缩放 |
| 隧道 | 极射赤面投影（视线锁天顶） | 天空卷进中心成隧道口 | 同上 |
| 水晶球 | 从球体**外部**正交观看 | 整张全景缩成一枚可拨转的悬浮球体 | 拖动拨转，滚轮/捏合拉近拉远 |
| 📸 截图 | — | 抓取当前画面 | iPhone 长按保存；Mac 点按钮下载 PNG |

模式切换带补间动画（easeInOutCubic），加载照片后自动播放「小行星 → 展开」开场动画。

## 快速开始

```bash
git clone <repo> && cd PanoViewer
./scripts/install.sh        # 构建并安装 Mac 端入口（见下）
```

安装后三种打开方式：

1. **拖放**：把全景图拖到 Dock 或 `~/Applications/360°全景查看.app` 图标
2. **右键**：Finder 中右键图片 → 打开方式 → 360°全景查看
3. **点选**：双击 App → 选择图片

也可以不开 App，直接用浏览器打开 `dist/全景查看器-独立版.html`，点选或拖入图片。

### iPhone

`install.sh` 会把独立版同步到 iCloud Drive（`全景查看器-独立版.html`）。iPhone 上建一条快捷指令：

```
获取文件（iCloud Drive/全景查看器-独立版.html）→ 快速查看
```

快速查看（Quick Look）可渲染 HTML + JS，即可在手机上用全部四种视角。

## 构建

```bash
python3 scripts/build.py                     # 构建 → dist/
python3 scripts/build.py --install           # 构建并部署到系统位置
python3 scripts/build.py --embed 照片.jpg     # 额外产出内嵌图片的测试版
```

构建即两步字符串替换：

- `__THREE_JS__` ← `vendor/three.min.js`（three.js r128，MIT）
- `__EMBEDDED_IMAGE__` ← 独立版置空；`template.html` 保留标记，由 `pano.sh` 在运行时注入 `data:<mime>;base64,...`

## 目录结构

```
PanoViewer/
├── src/viewer_source.html     # ★ 查看器源码（唯一需要编辑的文件，含两个占位标记）
├── vendor/three.min.js        # three.js r128 非模块版（全局 THREE）
├── scripts/
│   ├── build.py               # 组装构建（src + vendor → dist/）
│   ├── install.sh             # 一键安装：构建 + 部署模板 + osacompile 拖放 App + iCloud
│   ├── pano.sh                # 拖放 App 的注入脚本：base64 图片 → 临时 HTML → open
│   └── pano_applet.applescript# 拖放 App 的 AppleScript 源（on open / on run）
├── tools/
│   └── make_test_pano.py      # 生成带地标的测试全景图（经纬网格/方位标注/拼缝标记）
└── dist/                      # 构建产物（不入库）
```

## 架构与关键设计

三种渲染器同场景叠加，按模式切换透明度补间：

| 渲染器 | 用途 | 实现要点 |
|---|---|---|
| 内视球体 | 展开模式主画面；极射模式的背景天空 | `SphereGeometry(500,128,64)` + `scale(-1,1,1)` 从内部观看；材质透明度可补间（水晶球模式下淡出成暗背景） |
| 极射圆盘 | 小行星 / 隧道 | 200×360 极网格，顶点着色器直接输出 NDC 坐标（不经过相机矩阵）；`r = f·2tan(θ/2)`，`θ = θmax·ρ^2.5`（极点加密）；边缘 smoothstep 渐隐 |
| 外视球体 | 水晶球 | 正常 `SphereGeometry(1)`（不翻转），位置每帧跟随相机视线方向 `_target × dist` |

### 拼缝正确性（本项目最深的坑，改动前务必阅读）

等距圆柱图左右边缘必须无缝贴合。所有方案都栽在 **u 坐标回绕**上，最终结论：

1. **极射圆盘的 u/v 必须用 φ/θ 的解析线性式**（见 `POLES` 表）：
   - 天底（小行星）：`u = (φ-π)/2π`，`v = θ/π`
   - 天顶（隧道）：`u = (π-φ)/2π`，`v = 1-θ/π`
   - **绝不在着色器里用 `atan`/`asin` 反算**——`atan` 自身回绕 [0,1)，分支切割线落在网格内部时会产生 1° 宽的脏楔形带（整图反向压缩显示）。线性式下首末列顶点重合但无三角形跨越，`RepeatWrapping` 自然回绕，处处连续。
2. **纹理必须归一到 2 的幂尺寸**（`makePOTCanvas`）——WebGL1 下 mipmap + 无缝 RepeatWrapping 的硬性要求。
3. `texture.wrapS = RepeatWrapping`、`anisotropy` 拉满。
4. 全屏片元着色器方案（逐像素反算经纬度）被验证不可行：接缝处 mipmap 导数不连续 → 模糊竖线。**不要走回头路**。

### 为什么水晶球单独用一个球体

水晶球（博客园原理：投影面切于极点、视点无穷远 ≈ 从外部正交看球）**不是**「缩小的小行星」。用极射投影缩小只会得到一个缩小的圆盘，没有球体的立体透视感。直接放一个真实 3D 球体从外面看，就是正确的地球仪效果，且拖转交互天然正确。

### 拖放 App 链路

```
拖图到 App → AppleScript(on open) → pano.sh <路径>
  → base64 编码 → 逐行替换 template.html 的 __EMBEDDED_IMAGE__
  → 写临时 HTML → open（默认浏览器）
```

选 zsh 逐行替换而不是 sed，是因为 base64 单行超长会触发 BSD sed 的行长度限制。

## 调试 / 验证流程

改完渲染代码后**不要直接交付**，用测试图 + 无头浏览器截图验证：

```bash
python3 tools/make_test_pano.py          # 生成地标测试图（方位文字可查镜像，边缘色线可查拼缝）
python3 scripts/build.py --embed tools/test_pano.png
cd dist && python3 -m http.server 8765   # file:// 协议会被部分工具拦截，走 http
# playwright-cli（或任意无头浏览器）打开 http://localhost:8765/测试-内嵌图-test_pano.png.html
# 依次点击四个模式按钮，等 ~1.2s（补间完成）后截图，肉眼检查：
#   - 文字方向正确（不镜像）、方位顺序正确
#   - 拼缝处无脏楔形/模糊线（洋红-白线应无缝贴合或仅细线）
#   - 小行星/隧道有明显的鱼眼卷曲，水晶球是悬浮球体
```

业务 JS 语法检查（不含 three.js）：

```bash
python3 -c "src=open('src/viewer_source.html').read();open('/tmp/check.js','w').write(src.split('<script>')[2].split('</script>')[0])"
node --check /tmp/check.js
```

## 踩坑记录（前车之鉴）

| 尝试 | 结果 | 原因 |
|---|---|---|
| Pannellum 2.5.6 + blob/data URL | "could not be accessed" | 同源检查判 blob:/data: 为跨域，XHR 抓取被拦 |
| three.js 球体贴图 | ✅ 拼缝可靠 | 几何连续，沿用至今 |
| 全屏片元着色器逐像素反算 | ❌ 接缝模糊竖线 | u 在接缝跳变，mipmap 导数误判 |
| 极射圆盘 + atan + ±1 整数偏移 | ❌ 1° 脏楔形 | atan 自身回绕，偏移符号两极性都错 |
| 极射圆盘 + 解析线性 u/v | ✅ 当前方案 | 数学上杜绝回绕不连续 |
| 极点柔化（smoothstep 混合平均色） | ❌ 死板色斑 | 单色平均本身就是错的 |
| 手写现代版 Automator workflow | ❌ 判"已损坏" | 二进制 plist 结构复杂，手写易错 |
| `shortcuts import` CLI | ❌ 无此子命令 | 本机版本不支持，改用 osacompile |
| `automator` CLI 运行 workflow | ❌ 沙盒限制 | Automator.framework 禁止沙盒调用，只能实测 |
| osacompile 编译拖放 App | ✅ 当前方案 | 照片拖 Dock / Finder 右键 / 双击选图三入口 |

## 后续可改进

- [ ] 小行星/隧道模式支持连续变焦到展开视角（投影参数 s 从 1 → 0 补间，需解决中间态的拼缝问题）
- [ ] 视频全景（.mp4 输入）
- [ ] 水晶球背景改为实时模糊全景而非纯色
- [ ] 多图浏览（拖入多张时左右切换）

## 许可

- 本项目代码：随意使用
- three.js（vendor/）：MIT License © 2010-2024 mrdoob / three.js authors
