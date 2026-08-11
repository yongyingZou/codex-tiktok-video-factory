# Hard-subtitle handling

Choose one policy for every selected clip:

- `preserve`: Keep the original hard subtitle only when its meaning and timing fit the new story.
- `crop`: Reframe the shot to move edge subtitles outside the final canvas while keeping the
  product, hands, action, and intended scene legible.
- `replace`: Cover the original subtitle region and place synchronized target-language narration
  captions in that same region.
- `reject`: Exclude the clip when text cannot be covered cleanly without hiding the product,
  hands, demonstration, or other essential visual evidence.

Use this preference order: clean shot, crop, semantically compatible preserve, small localized
replace, reject. Do not treat replacement as the default.

Do not blur hard subtitles by default. A blur often leaves readable color and glyph shapes and looks
like an obvious removal. Prefer an intentional caption panel: a sufficiently opaque solid or
gradient mask whose bounds cover the complete original text, outline, and shadow.

Do not use a large solid or translucent block merely because a smaller region leaks text. If the
panel becomes a dominant visual element, crosses the product or hands, or still exposes source
glyphs, reject the shot. Never stack a replacement panel over a broad blur band.

For `replace`, record normalized final-canvas coordinates, every original-text interval, every mask
interval, and clip-relative target caption cues. Ensure the mask begins no later than the original
text and ends no earlier. Never allow one frame of the source subtitle to flash before replacement.

Keep target captions concise:

- Express one spoken meaning at a time.
- Use no more than two lines by default.
- For Japanese, target roughly 8–14 characters per displayed phrase.
- Segment Japanese by natural reading and breath groups; do not preserve Chinese word order or
  force every narrated word onto screen. Prefer familiar Japanese product and scene vocabulary.
- Time captions to the narration, not merely to clip boundaries.
- Derive caption intervals from the final synthesized narration segments, including inserted pauses.
  If a voice segment is regenerated or retimed, invalidate and rebuild its caption cues before render.
- Keep styling consistent within one finished video.
- Do not place a second caption track elsewhere when the replacement region already carries it.

Reject or redesign a replacement when its region overlaps product details, installation actions,
hands, before/after evidence, platform controls, product cards, or other market-specific safe areas.
Review each clip independently; hard-subtitle position may change between clips or over time.

After rendering, inspect both a time-distributed contact sheet and the full-motion output. Confirm
that no source glyph flashes at the beginning or end, crop motion does not reveal the text, and the
replacement does not look like an artificial patch.
