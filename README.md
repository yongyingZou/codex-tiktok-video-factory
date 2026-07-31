# TikTok 商品视频工厂

一个面向多国家 TikTok 店铺的 Codex 插件。它将完整商品理解、全素材分析、本地化策划、
口播、混剪计划和质检组织成可重复的工作流。

当前版本已包含环境检查、全素材清点、视频总览、多市场语言和音色、计划驱动渲染、
封面、发布资料、自动质检和本地操作页面。商品理解、镜头销售作用与视频方向由
Codex Skill 完成，并在渲染前要求用户确认。

## 三分钟开始

先运行一次安装：

```bash
python3 bootstrap.py
```

它只在项目内创建 `.venv`，不会污染系统 Python，也不要求账号或 API Key。

商品目录：

```text
商品ID_辅助名称/
├── product/       商品图片
├── SP/            视频素材
└── product.md     可选，用户确认的事实
```

检查电脑：

```bash
.venv/bin/python plugins/codex-tiktok-video-factory/skills/tk-product-video-factory/scripts/factory.py doctor
```

检查商品素材是否完整：

```bash
.venv/bin/python plugins/codex-tiktok-video-factory/skills/tk-product-video-factory/scripts/factory.py inspect "/path/to/商品目录"
```

建立日本、韩国和泰国的生产任务：

```bash
.venv/bin/python plugins/codex-tiktok-video-factory/skills/tk-product-video-factory/scripts/factory.py plan "/path/to/商品目录" \
  --markets JP KR TH --count 3
```

试听当地推荐女声：

```bash
.venv/bin/python plugins/codex-tiktok-video-factory/skills/tk-product-video-factory/scripts/factory.py voice-test --market 日本
```

启动本地页面：

```bash
python3 start.py --workspace "/path/to/商品工作区"
```

页面会自动列出工作区里的商品目录；普通用户不需要复制语言代码、音色名称或编辑 YAML。

也可以在 Codex 中直接说：

```text
分析这个商品的全部素材，然后为日本、韩国和泰国各策划3条视频。
```

## 口播

默认计划使用 Edge TTS：无需账号和 API Key，支持多个目标市场。

`bootstrap.py` 会自动安装，不需要单独配置。

日本用户可选装 AivisSpeech 提升日语口播表现；Azure 等官方服务留给需要更高稳定性的
用户。增强服务不是首次使用的前置条件。

## 当前原则

- 必须分析全部图片和全部视频，明确报告遗漏。
- 一个成片讲清楚一个销售逻辑，多段镜头共同完成叙事。
- 不通过简单换序伪造不同版本。
- 商品事实跨市场共享，文案针对市场重新创作。
- 不确定的商品事实不编造。
- 不承诺爆款或收益。

## 完整生产流程

```text
读取全部 product/ 与 SP/
→ 为全部视频生成完整时段总览
→ Codex 检查商品图片、视频画面、原音和硬字幕
→ 输出商品事实、原视频打法、镜头库和不同销售方向
→ 用户确认
→ 为各市场直接创作文案和口播
→ 生成 edit-plan JSON
→ 通用渲染器输出视频、封面和发布资料
→ 单条质检和批量差异检查
```

生成全部视频总览：

```bash
.venv/bin/python plugins/codex-tiktok-video-factory/skills/tk-product-video-factory/scripts/factory.py \
  preprocess "/path/to/商品目录"
```

按确认的剪辑计划渲染：

```bash
.venv/bin/python plugins/codex-tiktok-video-factory/skills/tk-product-video-factory/scripts/factory.py \
  render "/path/to/商品目录" "/path/to/edit-plan.json"
```

质检：

```bash
.venv/bin/python plugins/codex-tiktok-video-factory/skills/tk-product-video-factory/scripts/factory.py \
  qa "/path/to/商品目录" "/path/to/edit-plan.json"
```

剪辑计划格式见 `examples/edit-plan.example.json`。

## 从 GitHub 安装到 Codex

仓库是标准 Codex marketplace。发布到 GitHub 后，用户执行：

```bash
codex plugin marketplace add owner/codex-tiktok-video-factory
codex plugin add codex-tiktok-video-factory@tiktok-video-factory
```

然后启动新任务，让 Codex 载入插件。

## 系统要求

- Python 3.10 或更高；
- FFmpeg 与 FFprobe；
- 可以联网时使用免费的 Edge TTS。

macOS 可用 `brew install ffmpeg`，Ubuntu/Debian 可用 `sudo apt install ffmpeg`，
Windows 可用 `winget install Gyan.FFmpeg`。`bootstrap.py` 不会擅自修改系统软件。

高级 OCR 与分镜工具属于可选增强；缺少时仍会为每条视频生成完整时段总览，但不会谎称
已经自动识别完所有字幕。内容语义仍需 Codex 完整复核。

## License

MIT。请勿把无权分发的 TikTok 视频、音乐、商品素材或第三方语音模型提交到本仓库。
