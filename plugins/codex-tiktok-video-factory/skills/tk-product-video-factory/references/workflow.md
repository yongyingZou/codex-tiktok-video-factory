# Production workflow

## 0. Workflow state and hard gates

Treat `analysis/v1/workflow-state.json` as the machine-readable source of truth. Conversation
memory, an existing output folder, or a technical QA pass cannot substitute for this file.

Rendering has two explicit stages:

- `baseline`: render exactly one proposed direction after inventory, product model, complete source
  analysis, shot library, and direction confirmation have passed;
- `batch`: render additional directions only after the baseline has passed full-motion visual and
  audio review and its gate is marked `approved`.

The source-analysis gate records total and reviewed counts for images, videos, meaningful audio,
and hard subtitles. A failed transcription or unreadable asset must be listed in `blocked_items` and
reported to the user. It cannot be silently counted as reviewed. If incomplete evidence affects the
planned claim or narrative, narrow the plan or stop; never continue merely because rendering works.

Lock confirmed market, content language, voice policy, face policy, duration policy, output format,
and user-confirmed promotion/specification facts in workflow state. A later script may not change a
locked choice without an explicit revision record.

## 1. Inventory and completeness

Enumerate every file in `product/` and `SP/`. Record file hashes, dimensions, duration, frame rate,
audio presence, and processing status. The inventory count is the completion denominator.

Do not begin direction selection until every inventory item has an explicit analyzed, unreadable,
or failed status. Sampling a few familiar sources is not a substitute for full coverage.

## 2. Product understanding

Read `product.md` first when present, then inspect every product image. Extract identity, target
users, primary need, use scenes, differentiators, objections, variants, sizes, quantities,
promotions, and unsafe/unconfirmed claims.

Do not accept the folder suffix or a seller slogan as product identity. Establish the literal
searchable category first, then the primary need, solution mechanism, common and niche scenes,
objections, primary benefits, supporting benefits, variant information, and unknowns. Apply the
completion and value-hierarchy tests in `product-understanding.md`.

Assign each fact one evidence level: `confirmed_user`, `product_source`, `repeated_source`,
`single_source`, `inference`, or `blocked`.

After extraction, perform a separate semantic synthesis pass. Scripts may collect evidence but may
not author or approve the conclusions. Write `analysis/v1/product-analysis.md` with these decision
sections: literal identity, target buyer, problem-producing situation, experienced symptom or need,
product mechanism, product-use scene, direct bounded help, benefit hierarchy, blocked claims,
creator tactics versus verified facts, contradictions and their resolution, and one purchase
thesis.

Keep the problem-producing situation separate from the discovery moment and the product-use scene.
Run a contradiction check across images, speech, hard subtitles, visible action, and the purchase
thesis. Do not approve the product model when the thesis is empty, relies on the folder suffix,
confuses cause with use scene, or contains an unresolved contradiction.

## 3. Source-video analysis

Analyze every video from start to finish. Segment scenes, OCR hard subtitles, transcribe meaningful
speech, and describe each shot's action and sales function. Identify hook, pain, mechanism,
demonstration, scenario, objection handling, proof, result, offer, and call to action.

Summarize how each complete source video explains the product, including its spoken argument,
visual structure, pacing, and sales tactic. Compare source claims with the product model instead of
copying them automatically. Separate what the picture proves, what speech claims, and what viewers
may reasonably infer from an associated scene.

Do not equate a high-impact shot with a strong purchase argument. Record both separately.

## 4. Shot library

Create stable shot IDs linked to source file and timestamps. Record visual cleanliness, face
presence, hard subtitles and meaning, original speech, product visibility, usable duration,
continuity dependencies, and allowed sales functions.

Classify faces as `real`, `ai_generated`, or `uncertain`. Prefer no-face product demonstrations,
hands, body details, back views, and brief context shots. Use a real face only when it contributes a
necessary scene, reaction, or sales function and no cleaner shot serves the same role. Treat
`uncertain` as real. Do not solve face selection with moving stickers or conspicuous cover blocks.

For hard subtitles, record final-canvas bounding regions and appearance intervals. Choose
`preserve`, `crop`, `replace`, or `reject` before the shot enters an edit plan. See `subtitles.md`.

When the user has no self-shot footage, treat that as a constraint rather than a blocker. Split
sources into short semantic actions instead of preserving complete source arguments. Record source
provenance separately from creative usefulness. Unknown provenance increases risk but does not
justify inventing a guaranteed transformation threshold.

## 5. Directions

Propose materially different sales logics based on available evidence. For each direction specify:
audience/problem, hook, promise, supporting shots, objection addressed, CTA, missing assets, and why
it differs from other directions.

Before editing, build a narrative evidence map for every direction:

- `hook`: the first visual or source speech that creates attention;
- `problem_or_need`: the viewer situation the video is about;
- `mechanism_or_demo`: what the product visibly does;
- `result_or_scene`: the change, outcome, or believable use scene;
- `cta`: the reason to inspect the linked product.

Not every video needs all five as separate shots, but the finished sequence must communicate a
complete buying idea. A spoken claim can be supported by a strongly associated scene; do not force
an unrelated product still or laboratory-style proof into the timeline merely because narration
mentions the feature. If the needed visual relationship is absent or ambiguous, narrow the copy or
report missing footage.

For every narration unit, record `line`, `fact_or_inference`, `evidence`, `shot_ids`, and
`support_status`. Only `supported` lines may enter the baseline. Narrow `conditional` lines
explicitly. `unsupported` and `contradicted` lines block rendering. Never invent a discovery
moment, cause, use scene, or product behavior to make available footage feel coherent.

Across a batch, measure source-file coverage and shot reuse before rendering. Reusing a strong shot
is allowed when it serves a genuinely different meaning, but changing only shot order, narration
wording, or the opening clip does not create a new sales direction. Give each video a different
viewer problem, purchase reason, supporting-shot combination, and ending where the assets allow it.

When adding a video to a product that already has finished plans, historical edit plans are
exclusion references, not the candidate-shot pool. Select from the complete semantic shot library
again. Declare the new purchase reason, how it differs from history, and that selection was based on
the shot library. Before rendering, compare source intervals against every historical plan using
duration overlap, trimmed/near-identical shot reuse, opening reuse, ending reuse, and sales-direction
identity. A failed comparison blocks rendering; changing narration, music, transforms, filenames,
or a few cut boundaries cannot override the failure. If the remaining material cannot support a
materially new argument, report insufficient footage instead of manufacturing another version.

For every proposed hook, compare its source time range with the source video's opening. Reject a
hook that directly reuses the recognizable original opening sequence. Prefer another source or a
later self-contained action, while preserving enough setup and result for the hook to remain clear.

## 6. Localization

Keep product facts shared. Recreate hook, syntax, rhythm, politeness, CTA, cover copy, description,
and tags for the selected market. Provide target-language text plus concise Chinese meaning.

For Japanese production, create narration directly as spoken Japanese rather than translating a
Chinese script. Check natural omission, word order, particles, sentence endings, pause placement,
politeness, emotional progression, and short-video rhythm. Use standard conversational Japanese by
default. Use a regional dialect only when the intended audience or speaker persona is explicitly
defined and the dialect can be used accurately; forced dialect lowers credibility. Write captions
as concise Japanese reading units that match the spoken meaning, not as rigid word-for-word
transcripts. Generate the Chinese meaning check only after the Japanese copy is finalized.

For expressive segmented TTS, use this order: finalize the performance plan, synthesize all
segments, join them with deliberate pauses, measure the actual audio, and only then lock picture
cuts, action cues, and caption intervals. Store each segment's final start/end time. Any regenerated
voice segment invalidates downstream caption and action timing until those cues are rebuilt.

For every narrated plan, create `caption_track.mode = burn_in` with concise target-language cues
timed to the final narration audio. Rendering is blocked if the track is missing or empty. The
publishing caption records must carry identical cue text and start/end times so the delivered
document describes what viewers actually see.

## 7. Edit plan and render

Plan the timeline before rendering. Align spoken meaning with visible action. Avoid overlapping new
voice-over with meaningful source speech unless intentionally mixed. Use licensed or clearly
permitted music and duck it beneath voice.

Record each shot's narrative role, why it follows the previous shot, and what spoken line it
supports. Prefer action-to-result, problem-to-solution, feature-to-scene, or question-to-answer
transitions. Reject decorative shots that interrupt the argument. Do not impose a fixed duration;
end when the sales idea is complete and remove repeated conclusions.

For each selected shot, define a purposeful transform only when it improves the new presentation:
reframe/zoom around the product or action, modest timing adjustment, unified color correction,
subtitle replacement, source-audio handling, and synchronized informational overlays or action
sounds. Do not apply the same transform to every shot. Do not alter file hashes, filenames, frame
rates, random frames, or unrelated layers as an originality strategy.

Apply `editing.md`. Mark the useful action phase, exact entry and exit reasons, relationship to the
previous shot, supported narration line, speed treatment, motion-text purpose, action sounds, music
ducking, and intended renderer for every timeline item. Effects follow action and meaning; they are
never inserted at fixed intervals.

Prefer Remotion for programmable composition, keyframed movement, motion text, overlays,
transitions, captions, and audio automation when available. Keep FFmpeg for media inspection,
extraction, normalization, encoding, muxing, and technical QA. Falling back to FFmpeg must not
silently discard editorial fields; report unsupported treatments before rendering.

When replacing hard subtitles, cover the complete original text interval and place concise,
synchronized narration captions inside the same region. Do not add a second caption track.

Do not enlarge a mask repeatedly to rescue a poor shot. If the replacement region becomes visually
dominant, still leaks glyphs, hides the product or hands, or looks unlike a native creator edit,
reject the shot and select another source. Review a rendered contact sheet and the full-motion video;
still-frame OCR and technical checks alone cannot approve the result.

## 8. QA

Run technical and editorial checks. Compare every output against its direction instead of checking
only file validity. Record failures, warnings, source-usage ratios, and claims used.

Run a separate visual gate that checks every shot for identifiable real faces, subtitle leakage,
large masks or blurred bands, crop damage, irrelevant inserts, duplicate conclusions, and motion
continuity. A technical pass cannot override a visual failure.

Run a full-motion editorial gate with sound. Check action-cut accuracy, shot-to-shot relation,
narration-picture agreement, motivated text and effects, action-sound synchronization, voice/BGM
balance, silent tails, and whether the completed video communicates one understandable purchase
reason. Contact sheets and automated reports are supporting evidence only.

For every additional video, place the new and historical outputs side by side and watch them in
full with sound. Automated uniqueness metrics are a pre-render gate, not editorial approval. The
reviewer must answer whether an ordinary viewer would perceive a new argument and a substantially
different visual construction. Record the comparison result in the QA report.

Repeat the contradiction check on the finished script: cause versus symptom, cause versus use
scene, mechanism versus claimed result, and creator tactic versus verified fact. A technically
valid video fails editorial QA when any relationship is wrong.

Review publishing data as part of editorial QA. Keep one stable, searchable product identity across
the batch. Every description must combine an accurate explanation of what the product is with the
specific content and purchase reason shown in that finished video, followed by a natural product-link
CTA. Do not publish a generic product paragraph or a footage-only summary. Require five to seven relevant tags, including
stable product/category tags and video-specific tags. Record real-time trend verification separately
so relevance guesses are never presented as current hot tags.

Narration and description are separate assets. Narration carries the timed spoken argument; the
description identifies the product, reframes this video's hook/value for feed and search context,
and supplies a concise click reason. Do not paste the narration into the description or append a CTA
to an otherwise identical transcript. Automated validation blocks direct and near-direct copies.

The consolidated publishing document must provide target-market text and Chinese meaning side by
side for every publish-facing item: product name, video direction, cover copy, narration,
description, CTA, every rendered caption unit, and each hashtag. Caption rows include start/end
time and their narration-unit references so the exact text burned into the video remains auditable.
Keep the target-market description within 3000 characters. The
Chinese text is an internal review aid and must not be mixed into the actual target-market fields.
Store each video's publishing record separately under `publish/<video-id>.json`. Whenever a new
video is rendered, rebuild the consolidated bilingual Markdown from all per-video records; never
overwrite it with only the newest entry. Preserve an unstructured legacy Markdown document verbatim
until it has been migrated. Every hashtag row must contain the target-market tag and a non-empty
Chinese meaning. Also output all target-market hashtags on one directly copyable line, followed by
one same-order Chinese meaning line and then the per-tag bilingual table. The table alone is not a
sufficient publishing handoff.

For Japan, write descriptions and hashtags natively in Japanese from the start. Use Japanese
product-category vocabulary, natural social-commerce phrasing, and search terms Japanese shoppers
would plausibly use. Do not translate a Chinese draft sentence by sentence, invent awkward compound
tags, or copy Chinese marketplace keyword-stacking habits. Add Chinese meanings only after the
Japanese publishing copy is complete.

Record publication outcomes in `analysis/v1/publish-feedback.json`. Include market, video ID,
workflow version, result, violation type, appeal state, notes, and optional performance metrics.
When a video is rejected, pause sibling outputs that share its source/editing pattern until the
failure has been reviewed.

## 9. Continuous workflow improvement

When the user identifies a recurring or structural failure, do not only repair the current video.
Classify the failure as `understanding`, `evidence`, `direction`, `editing`, `localization`,
`rendering`, `qa`, or `publishing`. Write a regression entry to
`analysis/v1/workflow-improvements.json` containing the observed failure, root cause, enforceable
replacement rule, enforcement location, failing example, expected behavior, affected artifacts,
and validation result.

Update the reusable skill only for generalizable failures. Keep product-specific corrections in
the product analysis. Validate the skill and relevant scripts after each structural change. Do not
claim the workflow was improved until an instruction or code gate changed and a regression check
passed. A conversational agreement is not a persisted workflow improvement.

## 10. Delivery contract

Internal edit plans, evidence, render manifests, and QA reports may remain JSON. The human-facing
publishing deliverable is one consolidated bilingual Markdown file per market unless the user
explicitly requests another format. It contains each video's stable product name, direction, cover
copy, target-language narration, Chinese meaning check, description, CTA, hashtags and Chinese
meanings. Do not expose per-video internal JSON as the primary publishing document.

Completion language must distinguish three states: `rendered`, `technical_pass`, and
`editorial_approved`. Never describe a merely rendered or technically valid batch as ready to
publish. Only full-motion review with sound can set `editorial_approved`.
