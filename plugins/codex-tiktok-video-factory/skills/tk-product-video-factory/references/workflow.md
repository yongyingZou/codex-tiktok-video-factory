# Production workflow

## 1. Inventory and completeness

Enumerate every file in `product/` and `SP/`. Record file hashes, dimensions, duration, frame rate,
audio presence, and processing status. The inventory count is the completion denominator.

## 2. Product understanding

Read `product.md` first when present, then inspect every product image. Extract identity, target
users, primary need, use scenes, differentiators, objections, variants, sizes, quantities,
promotions, and unsafe/unconfirmed claims.

Assign each fact one evidence level: `confirmed_user`, `product_source`, `repeated_source`,
`single_source`, `inference`, or `blocked`.

## 3. Source-video analysis

Analyze every video from start to finish. Segment scenes, OCR hard subtitles, transcribe meaningful
speech, and describe each shot's action and sales function. Identify hook, pain, mechanism,
demonstration, scenario, objection handling, proof, result, offer, and call to action.

Do not equate a high-impact shot with a strong purchase argument. Record both separately.

## 4. Shot library

Create stable shot IDs linked to source file and timestamps. Record visual cleanliness, face
presence, hard subtitles and meaning, original speech, product visibility, usable duration,
continuity dependencies, and allowed sales functions.

For hard subtitles, record final-canvas bounding regions and appearance intervals. Choose
`preserve`, `replace`, or `reject` before the shot enters an edit plan. See `subtitles.md`.

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

Across a batch, measure source-file coverage and shot reuse before rendering. Reusing a strong shot
is allowed when it serves a genuinely different meaning, but changing only shot order, narration
wording, or the opening clip does not create a new sales direction. Give each video a different
viewer problem, purchase reason, supporting-shot combination, and ending where the assets allow it.

## 6. Localization

Keep product facts shared. Recreate hook, syntax, rhythm, politeness, CTA, cover copy, description,
and tags for the selected market. Provide target-language text plus concise Chinese meaning.

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

When replacing hard subtitles, cover the complete original text interval and place concise,
synchronized narration captions inside the same region. Do not add a second caption track.

## 8. QA

Run technical and editorial checks. Compare every output against its direction instead of checking
only file validity. Record failures, warnings, source-usage ratios, and claims used.

Review publishing data as part of editorial QA. Keep one stable, searchable product identity across
the batch; put the per-video angle in the description. Require five to seven relevant tags, including
stable product/category tags and video-specific tags. Record real-time trend verification separately
so relevance guesses are never presented as current hot tags.

Record publication outcomes in `analysis/v1/publish-feedback.json`. Include market, video ID,
workflow version, result, violation type, appeal state, notes, and optional performance metrics.
When a video is rejected, pause sibling outputs that share its source/editing pattern until the
failure has been reviewed.
