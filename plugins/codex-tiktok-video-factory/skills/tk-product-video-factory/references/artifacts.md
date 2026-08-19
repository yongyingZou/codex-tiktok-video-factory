# Artifact contract

Store analysis in `analysis/v1/`:

- `inventory.json`: every input file, hash, media metadata, and analysis status.
- `product-facts.json`: facts with value, evidence level, source, and notes.
- `product-model.json`: literal category, users, primary need, solution mechanism, scenes,
  objections, benefit hierarchy, variants, claim limits, and unknowns.
- `product-analysis.md`: concise human-authored semantic synthesis, contradiction resolution, and
  one-sentence purchase thesis. This is a decision artifact, not an automated media report.
- `source-videos.json`: full-video summaries and original tactics.
- `shot-library.json`: timestamped reusable shots with sales functions.
- `video-directions.json`: distinct narratives and required shots.
- `narrative-evidence.json`: every narration unit mapped to evidence and selected shot IDs, with a
  support status of `supported`, `conditional`, `unsupported`, or `contradicted`.
- `workflow-improvements.json`: regression ledger for structural failures and enforceable fixes.
- `publish-feedback.json`: publication outcomes and violations used to improve later heuristics.

Store each market under `output/<market>/`:

- `edit-plans/<id>.json`: direction, timeline, source ranges, audio, copy, and cover plan.
- `videos/<id>.mp4`: rendered video.
- `covers/<id>.jpg`: simple related cover.
- `publish/<id>.json`: bilingual-review publishing data containing stable product name,
  video-specific description, CTA, cover copy, narration, actual rendered caption units with
  timing and Chinese meanings, five to seven tags with per-tag Chinese meanings, and hashtag
  strategy/verification status. Target-market fields remain publishable; Chinese fields are
  review-only.
- `reports/qa-report.json`: technical and editorial checks.

Every edit-plan timeline item must include `source`, `start`, `end`, `purpose`, `spoken_meaning`,
`supported_line`, `action_phase`, `entry_reason`, `exit_reason`, `relation_to_previous`,
`attention_role`, `provenance.status`, `transform`, `speed`, `sound`, `text_overlays`, `renderer`,
and a `subtitle.mode`. Provenance status is one of `self_shot`, `authorized`, `seller_supplied`, or
`unknown`. A `replace` subtitle also includes normalized `region`, `source_text_intervals`,
`mask_intervals`, synchronized `cues`, and `style`. These fields make narrative logic, action
timing, sound, motion design, and hard-subtitle replacement deterministic and reviewable.

Supported deterministic transform fields are `scale` (1.0–1.2), normalized `focus_x` and
`focus_y` (0–1), `brightness` (-0.2–0.2), `contrast` (0.8–1.3), and `saturation` (0–2). Use them
per shot for composition and visual consistency, never as fixed anti-detection parameters.

`speed` records purposeful segments rather than a blanket multiplier. `sound` records source-audio
policy, ambience, synchronized action effects, and transition accents. `text_overlays` records only
short information elements that add meaning. `renderer` is normally `remotion` for editorial and
motion work or `ffmpeg` for a deliberately simple treatment; unsupported requested treatments must
be reported rather than silently removed.

Every narrated edit plan also contains `caption_track` with `mode: "burn_in"`, timed `cues`, and
optional style fields. These cues are the renderer's source of truth. Their text and timing must
match the publishing `captions` records; the latter additionally carry Chinese meanings and
narration-unit references.

Recommended publishing shape:

```json
{
  "publish_schema_version": 2,
  "product_name": "Search-oriented product name within 30 characters",
  "product_name_cn": "Chinese meaning of the product name",
  "direction": "Target-market video direction",
  "direction_cn": "Chinese meaning of the direction",
  "cover_copy": "Target-market cover copy",
  "cover_copy_cn": "Chinese meaning of the cover copy",
  "narration": "Complete target-market narration",
  "narration_cn": "Complete Chinese meaning check",
  "description": "What the product is + this video's hook/content/value + natural product-link CTA ✨",
  "description_cn": "Complete Chinese meaning check of the description",
  "description_max_characters": 3000,
  "captions": [
    {
      "start": 0.1,
      "end": 1.8,
      "text": "Target-market rendered caption",
      "meaning_cn": "Chinese meaning check",
      "narration_unit": "L1"
    }
  ],
  "tags": ["#core_product", "#category", "#feature", "#scene", "#problem"],
  "tag_translations": [
    {"tag": "#core_product", "meaning_cn": "核心商品词"},
    {"tag": "#category", "meaning_cn": "商品类别词"}
  ],
  "hashtag_strategy": {
    "core_product": ["#core_product", "#category"],
    "video_specific": ["#feature", "#scene", "#problem"],
    "realtime_hot_verified": false,
    "note": "Relevant search candidates; verify real-time trends on publication day."
  }
}
```

Persist this object as `output/<market>/publish/<video-id>.json`. The human-facing
`发布资料_中日对照.md` is a deterministic consolidation of every JSON record in that directory;
adding or regenerating one video must not remove the other video sections. Narration and description
must be independently written, and `tag_translations` must contain one non-empty Chinese meaning for
every value in `tags`. Publishing schema v2 also requires every rendered caption unit to include
start/end time, target-market text, Chinese meaning, and its narration-unit reference. The Markdown
must include a directly copyable one-line target-market hashtag block, a same-order Chinese meaning
line, and the per-tag bilingual table.
