# TikTok Shop AI Video Remix Factory

## 不会剪辑，也能建立自己的TikTok Shop视频生产线

**把商品图片和素材视频放进文件夹，AI从理解商品、看完素材、策划卖点，到多语言口播、
混剪、封面、发布文案和质检，帮你走完从素材到成片的完整流程。**

```text
不需要先学Premiere或剪映
一份素材可以策划多种销售打法
一次准备可以制作多个国家版本
不是把同一条视频换30次顺序
```

> 别再一条一条拖时间轴。把重复的剪辑劳动交给视频工厂，把时间留给选品、素材和销售策略。

**Turn a folder full of product clips into distinct, localized TikTok Shop videos—not endless
reorders of the same edit.**

## 找了很多素材，为什么还是做不出足够多的带货视频？

你可能已经下载了十几条甚至几十条热门商品视频。真正开始批量制作时，却会发现：

- 找素材花了很久，剪辑时来来回回仍然只用那几个片段；
- 一次生成五条，实际只是镜头顺序不同，开头、卖点和结尾都差不多；
- 剪辑人员会拼接画面，却不一定理解商品解决什么问题、用户为什么购买；
- 原视频字幕、原声、人物和新口播互相冲突，成片看起来像生硬搬运；
- 做日本站还勉强能处理，扩展到其他国家后，又要重新解决语言、口播和当地表达；
- 视频剪完还没结束，仍要制作封面、名称、描述、标签，再逐条检查错误；
- 最终大量时间耗在机械整理上，真正重要的商品理解和销售逻辑反而没有做好。

这不是单纯缺少一个剪辑命令，而是缺少一套从“商品素材”到“可发布带货视频”的完整方法。

## 这个项目如何解决

把商品图片和全部视频放进一个文件夹，视频工厂会协助完成：

1. **先理解商品**：识别商品是什么、解决什么问题、适用场景、目标人群、购买顾虑和可用事实；
2. **再看完所有素材**：不是抽查一两条，而是建立全部视频和全部镜头的素材清单；
3. **拆解热门视频为什么有效**：区分钩子、痛点、演示、场景、结果、优惠和行动引导；
4. **策划真正不同的视频方向**：每条成片讲清楚一个销售逻辑，多段镜头共同完成叙事；
5. **针对目标市场重新表达**：根据TikTok Shop站点选择语言、自然口播、当地文案和币种；
6. **完成整套发布物料**：输出成片、相关封面、商品名称、视频描述、标签和质检报告；
7. **拦截批量生产问题**：检查重复镜头、相同方向、口播截断、声音重叠、黑屏、静音和错误宣传。

最终目标不是“随机多剪几条”，而是：

> 让你辛苦收集的每一批素材被充分理解和利用，持续产出销售逻辑不同、适合目标市场、
> 可以检查和继续优化的TikTok Shop商品视频。

它不承诺一键爆单，也不会把简单换序包装成AI创作。工具负责减少重复劳动、暴露问题和
稳定执行；商品判断、销售逻辑和成片质量仍然保留明确的确认环节。

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

### 原视频带硬字幕怎么办？

系统不会默认在底部留下一条明显的模糊带，再在别处新增一套字幕。每个镜头会选择：

- `preserve`：原字幕语义和新叙事一致，直接保留；
- `replace`：完整覆盖原字幕，并在相同区域显示同步的新口播字幕；
- `reject`：无法干净覆盖或会遮挡商品演示时，舍弃该镜头。

替换模式会记录原字幕区域和出现时间，避免字幕闪现、固定遮罩、挡住商品、字幕过长和
口播不同步。具体剪辑计划格式见 `examples/edit-plan.example.json`。

## 完整生产流程

```text
读取全部 product/ 与 SP/
→ 为全部视频生成完整时段总览
→ Codex 检查商品图片、视频画面、原音和硬字幕
→ 输出商品事实、原视频打法、镜头库和不同销售方向
→ 用户确认
→ 为各市场直接创作文案和口播
→ 为每个方向建立“钩子—需求—演示—结果/场景—行动理由”叙事映射
→ 检查素材覆盖率、镜头复用、重复结尾和仅换顺序的伪变体
→ 生成 edit-plan JSON
→ 通用渲染器输出视频、封面和发布资料
→ 单条质检和批量差异检查
```

### 发布资料不是附带的一句话

每条成片同时生成可直接检查和复制的发布资料：

- 商品名称保持稳定、准确、便于搜索，不拿每条视频的卖点冒充不同商品名；
- 视频描述对应本条叙事，包含用户痛点或钩子、画面中能看到的价值，以及自然的商品链接行动理由；
- 商品名称不超过30个字符且不放表情，描述可以使用适量鲜艳表情；
- 每条使用5至7个强相关标签，区分核心商品/类目词和本条视频的场景、问题或功能词；
- 猜测的标签不会标记为“实时热门”，只有发布当天经过平台趋势工具复核后才会记录为已验证。

模板和字段见 `examples/edit-plan.example.json`。渲染前验证和成片质检都会检查发布资料是否完整。

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
codex plugin marketplace add yongyingZou/codex-tiktok-video-factory
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
