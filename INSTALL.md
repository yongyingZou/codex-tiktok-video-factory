# 商品视频工厂 V2.0.0 安装指南

本项目推荐安装到 Codex/ChatGPT 桌面应用中使用。它是纯 Skill 插件，不需要账号、API Key
或额外的 MCP 服务。视频处理仍需要本机安装 Python 3.10+ 和 FFmpeg。

## 方式一：安装到 Codex（推荐）

### 1. 准备 Codex 命令

安装并登录 ChatGPT/Codex 桌面应用。在终端确认：

```bash
codex plugin --help
```

如果系统找不到 `codex`，请先在桌面应用中完成 Codex CLI 的安装或 PATH 配置。

### 2. 添加商品视频工厂来源

```bash
codex plugin marketplace add yongyingZou/codex-tiktok-video-factory --ref V2.0.0
```

### 3. 安装插件

```bash
codex plugin add codex-tiktok-video-factory@tiktok-video-factory
```

### 4. 确认安装

```bash
codex plugin list
```

应看到：

```text
codex-tiktok-video-factory@tiktok-video-factory  installed, enabled  2.0.0
```

重新启动 ChatGPT/Codex 桌面应用，并新建一个任务。旧任务可能仍保留安装前的能力列表。

## 方式二：下载后独立运行

不安装插件也可以使用仓库自带命令，但商品理解、创意策划和完整内容审核仍建议在 Codex
中完成。

```bash
git clone --branch V2.0.0 --depth 1 https://github.com/yongyingZou/codex-tiktok-video-factory.git
cd codex-tiktok-video-factory
```

macOS / Linux：

```bash
python3 bootstrap.py
python3 factory.py doctor
python3 factory.py version
```

Windows PowerShell：

```powershell
py bootstrap.py
py factory.py doctor
py factory.py version
```

`factory.py version` 必须显示 `2.0.0`。如果缺少 FFmpeg，`doctor` 或安装程序会给出对应
系统的安装提示。

## 更新与卸载

V2.0.0 的普通后续版本将按 V2.0.1、V2.0.2 递增。更新时先升级 Marketplace，再重新安装：

```bash
codex plugin marketplace upgrade tiktok-video-factory
codex plugin add codex-tiktok-video-factory@tiktok-video-factory
```

卸载：

```bash
codex plugin remove codex-tiktok-video-factory@tiktok-video-factory
```

插件卸载不会主动删除用户自己的商品素材和成片。

## 常见问题

### 可以不安装 AivisSpeech 吗？

可以。默认多语言口播使用 Edge TTS。AivisSpeech 只是日本市场的可选增强项；切换语音
提供方时必须明确告知用户。

### 支持哪些系统？

安装脚本支持 macOS、Windows 和常见 Linux 环境。视频渲染依赖 FFmpeg；不同系统的
硬件、字体和编解码器差异仍需通过 `doctor` 和单视频校准确认。

### 为什么安装后没有看到插件？

先运行 `codex plugin list`，确认状态为 `installed, enabled`；然后重启桌面应用并新建任务。

