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

## 5. Directions

Propose materially different sales logics based on available evidence. For each direction specify:
audience/problem, hook, promise, supporting shots, objection addressed, CTA, missing assets, and why
it differs from other directions.

## 6. Localization

Keep product facts shared. Recreate hook, syntax, rhythm, politeness, CTA, cover copy, description,
and tags for the selected market. Provide target-language text plus concise Chinese meaning.

## 7. Edit plan and render

Plan the timeline before rendering. Align spoken meaning with visible action. Avoid overlapping new
voice-over with meaningful source speech unless intentionally mixed. Use licensed or clearly
permitted music and duck it beneath voice.

When replacing hard subtitles, cover the complete original text interval and place concise,
synchronized narration captions inside the same region. Do not add a second caption track.

## 8. QA

Run technical and editorial checks. Compare every output against its direction instead of checking
only file validity. Record failures, warnings, source-usage ratios, and claims used.
