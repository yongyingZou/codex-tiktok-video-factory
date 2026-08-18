---
name: tk-product-video-factory
description: Analyze complete product-image and source-video folders, establish verified product facts, build a reusable shot library, devise distinct TikTok commerce-video narratives, localize them for one or more markets, prepare edit plans, render deliverables, and run quality checks. Use when a user asks to analyze a product ID, remix product videos, produce localized TikTok Shop content, batch-process product folders, or review outputs from the video factory.
---

# TikTok Product Video Factory

Create conversion-oriented product videos from supplied assets. Treat product understanding,
sales logic, and editorial judgment as the core work; treat OCR, scene detection, TTS, Remotion,
and FFmpeg as supporting and execution tools.

## Start

1. Run `python3 scripts/setup_runtime.py` once when the plugin-local `.venv` is absent. Then use
   that environment's Python for bundled scripts. Do not install dependencies into system Python.
2. Locate the product folder. Expect `product/` for product images, `SP/` for source videos,
   optional `product.md` for user-confirmed facts, and generated `output/`.
3. Run `python scripts/factory.py inspect <product-folder>` to inventory every input.
4. Read [workflow.md](references/workflow.md) before analysis or production.
5. Read [product-understanding.md](references/product-understanding.md) before establishing facts
   or proposing directions.
6. Write the human-authored `analysis/v1/product-analysis.md` before proposing directions. Do not
   generate its conclusions from a template or mark it approved merely because media processing
   completed.
7. Read [editing.md](references/editing.md) before preparing edit plans or rendering.
8. Read [markets.md](references/markets.md) and only the selected locale file under
   `references/markets/` when present.
9. Read [subtitles.md](references/subtitles.md) when any selected clip contains hard subtitles.
10. Never render until product understanding, material limitations, and proposed directions have
   been shown to the user once.
11. Create `analysis/v1/workflow-state.json` from the bundled example. Render one `baseline` plan
    first; do not render a `batch` plan until full-motion visual and audio review marks the baseline
    `approved`.

## Non-negotiable rules

- Analyze every supplied image and video, including visual content, original audio, and hard
  subtitles. Report unreadable or skipped inputs explicitly.
- Separate problem cause, experienced symptom, discovery moment, and product-use scene. Never turn
  an available use-scene shot into the cause of the user's need. Reconcile product images, source
  speech, hard subtitles, and visible action before writing any purchase logic.
- Before rendering, state one purchase thesis in the form: target user + problem-producing
  situation + concrete problem + product mechanism + direct bounded help. Stop when this sentence
  is unsupported or internally contradictory instead of filling gaps with plausible copy.
- Keep product facts separate from creator sales tactics. Learn hook and persuasion structure from
  creators, but do not promote repeated exaggeration into a product fact.
- Prefer product, hand, body-detail, back-view, and use-scene shots over identifiable real faces.
  Allow clearly AI-generated faces when useful. When face origin is uncertain, treat it as real.
  Do not use drifting stickers, large blocks, or other conspicuous face covers; reframe or reject
  the shot when a real face has no necessary sales function.
- Treat no-original-footage remixing as a supported production constraint. Do not repeatedly tell
  the user to film new footage after they state that constraint. Instead, atomize all supplied
  sources, rebuild narrative, visuals, text, and sound, and report residual originality risk.
- Distinguish confirmed facts, strong evidence, single-source claims, reasonable inference, and
  prohibited/unverified claims.
- Identify the product's literal category before functions or marketing language. Do not use the
  user's folder suffix as product identity or treat an auxiliary feature as the core value.
- Separate the primary purchase reason, solution mechanism, use scenes, objections, supporting
  benefits, and variant information. An auxiliary feature does not deserve an independent video
  unless it creates a complete and credible buying reason.
- Use one clear sales logic per finished video. Multiple clips may support that logic.
- Do not create variants by merely reordering the same shots. Track source and shot reuse.
- Treat historical edit plans as exclusion references, never as the candidate-shot pool for a new
  video. Select again from the complete shot library and block rendering when source-range overlap,
  trimmed near-duplicate shots, repeated openings/endings, or the same purchase reason exceed the
  internal historical-uniqueness policy.
- Do not use a source video's recognizable original opening sequence as the finished video's
  opening. Build the new hook from a different source or a later self-contained action. A useful
  source opening may appear later only when it supports the new narrative; do not preserve its
  original picture, audio, text, and order as one recognizable opening package.
- Record source provenance without blocking analysis: `self_shot`, `authorized`,
  `seller_supplied`, or `unknown`. Never pretend that a transformation parameter grants rights or
  guarantees review approval.
- Prefer source-video storytelling. Do not insert product stills merely to prove every spoken claim.
- Assign `preserve`, `crop`, `replace`, or `reject` to every selected hard-subtitle clip. Prefer a
  clean shot, then a purposeful crop, then semantically compatible source text, and only then a
  small localized replacement. Reject shots that require a large mask. Never leave a visibly
  blurred subtitle band, a conspicuous cover block, or a second caption track elsewhere.
- Create target-language copy directly; do not translate Chinese literally. Also provide a Chinese
  meaning check for the user.
- For Japan, write narration and captions as native spoken Japanese, including natural omission,
  word order, sentence endings, pauses, politeness level, and social-commerce rhythm. Do not map
  Chinese sentence structure into Japanese. Use standard conversational Japanese by default;
  introduce regional dialect only when a defined audience, character, or source context supports
  it. Captions may condense speech naturally and need not transcribe every spoken word.
- When expressive narration is synthesized in segments, build the final audio first, measure every
  rendered segment and pause, then lock the picture and caption timeline to those actual durations.
  Never time captions or action cuts from estimated reading speed. If performance changes alter
  duration, regenerate timing; do not preserve stale caption cues or silently stretch speech.
- Keep promotion, price, quantity, size, material, and performance claims consistent with confirmed
  facts.
- Flag missing footage or ambiguous evidence immediately. Never fabricate product behavior.
- Map every narration unit to a visible shot and an evidence source before rendering. Delete,
  narrow, or flag any line that lacks both factual support and a reasonable visual relationship.
- Do not select clips merely because they are visually attractive. Every selected range must have
  a narrative role, a supported spoken meaning, and a reason for following the previous range.
- Do not use effects on a timer. Reframing, speed changes, motion text, transitions, and sound
  effects must emphasize an action, meaning change, comparison, or scene transition.
- On a requested redo, remove superseded generated outputs after resolving the exact output target.
- Treat corrections as workflow evidence. Record the failed assumption, its cause, replacement
  rule, affected artifacts, and a regression example in `analysis/v1/workflow-improvements.json`.
  A conversational promise alone is not a workflow update.

## Market and speech behavior

Ask for the target market, not locale codes. Map the market to its default content language.
For multilingual markets, ask for the primary content language once and remember it.

Default to Edge TTS for markets without a configured local or cloud provider because it needs no
account or API key. For Japanese production on this workspace, prefer the installed AivisSpeech
service and use Edge only as an explicitly reported fallback. Never silently change provider or
voice after an edit plan is approved. Show general users only `automatic`, `female`, `male`, or
`no voice`; advanced provider choice remains optional configuration.

## Output contract

Write structured analysis beneath `analysis/v1/` and deliverables beneath `output/<market>/`.
Use the schemas described in [artifacts.md](references/artifacts.md). Each market output contains
`videos/`, `covers/`, `publish/`, `reports/`, and `edit-plans/`.

For publishing data, keep internal structured records as JSON, but deliver one consolidated
bilingual Markdown publishing document per market unless the user requests another format. Keep
the product name within 30 characters and free of emoji. Make the
product name stable and search-oriented instead of turning each video's angle into a different
product identity. Write each description as a combination of accurate product description and the
specific finished-video content: identify what the product is, connect it to this video's hook or
pain point and visible value, then give a natural reason to open the product link. Do not write a
generic product paragraph or merely summarize the footage; colorful emoji are allowed. Use five to
seven relevant tags split between stable product/category terms and terms specific to this video's
problem, scene, or feature. Never label guessed tags as trending. Record whether real-time trend
verification was performed and keep unverified tags as relevance candidates. Provide a Chinese
meaning check for every publishing field: product name, video direction, cover copy, narration,
description, CTA, and each hashtag. The target-market fields remain publication-ready and must not
contain the Chinese checks. Create Japanese descriptions and hashtags directly from natural
Japanese commerce-video language and Japanese search/category usage; never translate Chinese copy
literally or use Chinese ecommerce phrasing with Japanese words substituted. Chinese is a
post-writing meaning check only. Keep each target-market description within 3000 characters.

## Quality gate

Before completion, check product-identity accuracy, sales-logic completeness, narrative continuity,
action-cut accuracy, source repetition, duplicate endings, audio overlap,
voice cutoff, black frames, silence, dimensions, claims, promotions, market language, cover-video
relevance, publishing-data completeness, unnecessary identifiable real faces, subtitle leakage,
mask area, crop damage to products or hands, unmotivated effects, music ducking, and action-sound
synchronization. Also reject a finished hook that directly reuses any source video's recognizable
original opening sequence. Report failures rather than hiding them. A technical QA pass is not an editorial
or visual pass.

Also calculate remix-depth diagnostics from the edit plan: unique source count, longest continuous
clip, largest single-source share, preserved-hard-subtitle share, kept-source-audio share,
transformed-shot share, identical range reuse across the batch, and declared source provenance.
Treat thresholds as configurable internal heuristics, not platform rules. Preserve sales clarity;
do not add random frames, unrelated overlays, fixed color disturbances, or other evasive edits.

After publication, record pass, violation, appeal, and performance outcomes with the workflow
version. Use real results to revise heuristics instead of claiming a universal safe parameter.

Do not promise virality or revenue. Optimize for understandable value, retention, click intent, and
conversion while preserving factual integrity.
