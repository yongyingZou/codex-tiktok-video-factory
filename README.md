# TikTok Shop AI Video Remix Factory

**Codex plugin for AI-assisted product video analysis, TikTok Shop video remixing, multilingual
voice-over, multi-market localization, FFmpeg rendering, covers, publishing copy, and quality
control.**

面向多国家 TikTok Shop 商家的AI商品视频混剪工厂：完整理解商品和全部素材，为不同市场
重新策划带货逻辑、口播、剪辑、封面、视频描述与标签，而不是把同一批镜头简单换顺序。

它重点解决：

- 素材很多，却只反复使用少数镜头；
- 不理解商品、用户痛点和原热门视频打法；
- 同一条文案机械翻译到不同国家；
- 口播、画面和原视频声音互相打架；
- 批量视频看起来只是镜头顺序不同；
- 缺少封面、发布资料和成片质检；
- 普通商家不会配置OCR、TTS、FFmpeg和语言代码。

当前版本已包含环境检查、全素材清点、视频总览、多市场语言和音色、计划驱动渲染、
封面、发布资料、自动质检和本地操作页面。商品理解、镜头销售作用与视频方向由
Codex Skill 完成，并在渲染前要求用户确认。

## 三分钟开始

先运行一次安装：

```bash
# macOS / Linux
python3 bootstrap.py

# Windows PowerShell
py bootstrap.py
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
# macOS / Linux
python3 factory.py doctor

# Windows PowerShell
py factory.py doctor
```

检查商品素材是否完整：

```bash
python3 factory.py inspect "/path/to/商品目录"
```

查看当前经过核验的TikTok Shop市场、默认语言和币种：

```bash
python3 factory.py markets
```

建立日本、泰国和美国的生产任务：

```bash
python3 factory.py plan "/path/to/商品目录" --markets JP TH US --count 3
```

试听当地推荐女声：

```bash
python3 factory.py voice-test --market 日本
```

启动本地页面：

```bash
python3 start.py --workspace "/path/to/商品工作区"
```

页面会自动列出工作区里的商品目录；普通用户不需要复制语言代码、音色名称或编辑 YAML。

也可以在 Codex 中直接说：

```text
分析这个商品的全部素材，然后根据我选择的TikTok Shop市场分别策划视频。
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
python3 factory.py preprocess "/path/to/商品目录"
```

按确认的剪辑计划渲染：

```bash
python3 factory.py render "/path/to/商品目录" "/path/to/edit-plan.json"
```

质检：

```bash
python3 factory.py qa "/path/to/商品目录" "/path/to/edit-plan.json"
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
Windows 可用 `winget install Gyan.FFmpeg`。所有项目入口均为Python，不依赖zsh或bash；
路径、虚拟环境和可执行文件会按照当前系统自动处理。

项目通过GitHub Actions在Windows、macOS和Linux，以及Python 3.10与3.13上运行测试。
`bootstrap.py`不会擅自修改系统软件。

高级 OCR 与分镜工具属于可选增强；缺少时仍会为每条视频生成完整时段总览，但不会谎称
已经自动识别完所有字幕。内容语义仍需 Codex 完整复核。

## TikTok Shop市场不是固定常量

市场目录记录核验日期、官方来源、默认内容语言、可选语言、币种和语音。2026年官方帮助
中心与欧洲扩张公告存在更新时间差异，因此本项目不会把用户举例的国家永久写死。

当前目录包括官方资料可以确认的亚太、美洲和欧洲市场。韩国没有因为示例而被纳入
TikTok Shop市场；未来如官方开放，应更新来源和核验日期后再加入。

多语言市场允许选择主语言，例如：

- 马来西亚：马来语、英语或中文；
- 新加坡：英语、中文、马来语或泰米尔语；
- 菲律宾：菲律宾语或英语；
- 比利时：荷兰语或法语。

市场信息以TikTok官方的[Shop与Showcase帮助页](https://ads.tiktok.com/help/article/tiktok-shopping-and-showcase)
及[欧洲扩张公告](https://newsroom.tiktok.com/tiktok-shop-expands-across-europe)为依据。

## GitHub搜索关键词

TikTok Shop video editor · AI video remix · product video generator · ecommerce video automation ·
multilingual TTS · TikTok localization · Codex plugin · Codex skill · FFmpeg video pipeline ·
TikTok带货视频 · 商品视频混剪 · 多市场本地化

## License

MIT。请勿把无权分发的 TikTok 视频、音乐、商品素材或第三方语音模型提交到本仓库。
