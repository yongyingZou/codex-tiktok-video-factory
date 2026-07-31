---
name: tk-product-video-factory
description: Analyze complete product-image and source-video folders, establish verified product facts, build a reusable shot library, devise distinct TikTok commerce-video narratives, localize them for one or more markets, prepare edit plans, render deliverables, and run quality checks. Use when a user asks to analyze a product ID, remix product videos, produce localized TikTok Shop content, batch-process product folders, or review outputs from the video factory.
---

# TikTok Product Video Factory

Create conversion-oriented product videos from supplied assets. Treat product understanding and
sales logic as the core work; treat OCR, scene detection, TTS, and FFmpeg as supporting tools.

## Start

1. Run `python3 scripts/setup_runtime.py` once when the plugin-local `.venv` is absent. Then use
   that environment's Python for bundled scripts. Do not install dependencies into system Python.
2. Locate the product folder. Expect `product/` for product images, `SP/` for source videos,
   optional `product.md` for user-confirmed facts, and generated `output/`.
3. Run `python scripts/factory.py inspect <product-folder>` to inventory every input.
4. Read [workflow.md](references/workflow.md) before analysis or production.
5. Read [markets.md](references/markets.md) and only the selected locale file under
   `references/markets/` when present.
6. Read [subtitles.md](references/subtitles.md) when any selected clip contains hard subtitles.
7. Never render until product facts and proposed directions have been shown to the user once.

## Non-negotiable rules

- Analyze every supplied image and video, including visual content, original audio, and hard
  subtitles. Report unreadable or skipped inputs explicitly.
- Distinguish confirmed facts, strong evidence, single-source claims, reasonable inference, and
  prohibited/unverified claims.
- Use one clear sales logic per finished video. Multiple clips may support that logic.
- Do not create variants by merely reordering the same shots. Track source and shot reuse.
- Prefer source-video storytelling. Do not insert product stills merely to prove every spoken claim.
- Assign `preserve`, `replace`, or `reject` to every selected hard-subtitle clip. Prefer replacing
  conflicting hard subtitles with synchronized narration captions in the same region; never leave
  a visibly blurred subtitle band plus a second caption track elsewhere.
- Create target-language copy directly; do not translate Chinese literally. Also provide a Chinese
  meaning check for the user.
- Keep promotion, price, quantity, size, material, and performance claims consistent with confirmed
  facts.
- Flag missing footage or ambiguous evidence immediately. Never fabricate product behavior.
- On a requested redo, remove superseded generated outputs after resolving the exact output target.

## Market and speech behavior

Ask for the target market, not locale codes. Map the market to its default content language.
For multilingual markets, ask for the primary content language once and remember it.

Default to Edge TTS because it needs no account or API key. Show users only `automatic`, `female`,
`male`, or `no voice`. Treat AivisSpeech for Japanese and official cloud providers as optional
quality upgrades, never onboarding requirements.

## Output contract

Write structured analysis beneath `analysis/v1/` and deliverables beneath `output/<market>/`.
Use the schemas described in [artifacts.md](references/artifacts.md). Each market output contains
`videos/`, `covers/`, `publish/`, `reports/`, and `edit-plans/`.

For publishing data, keep the product name within 30 characters and free of emoji. Make the
description specific to the video; colorful emoji are allowed. Use only relevant tags and label
unverified trending tags as candidates.

## Quality gate

Before completion, check narrative continuity, source repetition, duplicate endings, audio overlap,
voice cutoff, black frames, silence, dimensions, claims, promotions, market language, cover-video
relevance, and completeness of publishing data. Report failures rather than hiding them.

Do not promise virality or revenue. Optimize for understandable value, retention, click intent, and
conversion while preserving factual integrity.
