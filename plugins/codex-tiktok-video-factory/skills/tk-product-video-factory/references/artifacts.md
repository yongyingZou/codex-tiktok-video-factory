# Artifact contract

Store analysis in `analysis/v1/`:

- `inventory.json`: every input file, hash, media metadata, and analysis status.
- `product-facts.json`: facts with value, evidence level, source, and notes.
- `source-videos.json`: full-video summaries and original tactics.
- `shot-library.json`: timestamped reusable shots with sales functions.
- `video-directions.json`: distinct narratives and required shots.

Store each market under `output/<market>/`:

- `edit-plans/<id>.json`: direction, timeline, source ranges, audio, copy, and cover plan.
- `videos/<id>.mp4`: rendered video.
- `covers/<id>.jpg`: simple related cover.
- `publish/<id>.json`: product name, description, and tags.
- `reports/qa-report.json`: technical and editorial checks.

Every edit-plan timeline item must include `source`, `start`, `end`, `purpose`, `spoken_meaning`,
and a `subtitle.mode`. A `replace` subtitle also includes normalized `region`,
`source_text_intervals`, `mask_intervals`, synchronized `cues`, and `style`. This makes hard
subtitle replacement deterministic and reviewable.
