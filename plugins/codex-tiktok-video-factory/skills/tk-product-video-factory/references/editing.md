# Editorial and motion-design workflow

The renderer must execute a deliberate edit, not decorate a concatenation. Build the spoken and
visual argument first, then use motion, text, sound, and transitions to make that argument easier to
feel and understand.

## Editing grammar

For every selected source range, identify:

- `action_phase`: setup, approach, contact, key action, reveal, result, or hold;
- `entry_reason`: why this is the correct first visible frame;
- `exit_reason`: why the shot ends at this frame;
- `relation_to_previous`: problem-to-solution, action-to-result, detail-to-whole,
  feature-to-scene, question-to-answer, matched action, matched composition, contrast, or deliberate
  reset;
- `supported_line`: the exact narration meaning supported by the visible action;
- `attention_role`: visual impact separately from sales function.

Trim dead hand movement, repeated setup, duplicate conclusions, and decorative footage. Preserve
enough of an action to remain understandable. Duration follows the completed sales idea, not a fixed
video length.

## Pace inside a shot

Use normal speed for the product behavior a viewer must judge. Modest acceleration may shorten
setup or travel. Slowdown, freeze, punch-in, or replay may emphasize a genuinely important action
such as fastening, opening, stretching, pouring, fitting, or revealing a result. Do not apply a
uniform speed change to every clip.

## Visual continuity

Prefer motivated cuts: cut on action, match motion direction, match product position, continue a
spoken thought, or make a clear contrast. Alternate useful shot scale when assets allow: context,
product, detail, result. Do not add a transition merely because time elapsed. A hard cut is often
stronger than an effect.

## Text and overlays

Use motion text for short information units: a hook, keyword, scene name, comparison, specification,
or CTA. It should complement the narration rather than duplicate every spoken word. Arrows, labels,
and picture-in-picture must point to visible product information. Follow `subtitles.md` when source
text is present; do not create a second competing caption track.

## Sound design

Build a complete sound timeline:

- narration with a deliberate start and no overlap with meaningful source speech;
- licensed or clearly permitted BGM with fades and voice ducking;
- retained source ambience only when it improves credibility or action comprehension;
- synchronized action sounds for clicks, snaps, pulls, pours, reveals, or other visible events;
- restrained transition accents only where the visual edit motivates them.

Never fill time with unrelated sound effects. Check the full output for silent tails, clipped speech,
double voices, abrupt music endings, and action sounds that drift from the picture.

## Rendering roles

Use Remotion as the programmable editorial and motion layer when available: per-shot framing,
keyframed movement, speed treatment, motion text, overlays, transitions, captions, and audio
automation. Use FFmpeg for probing, extraction, normalization, encoding, muxing, and technical QA.
Neither renderer decides the product truth, sales direction, or shot meaning.

## Opening-source rule

Do not place a source video's recognizable original opening sequence at the opening of the finished
video. Opening picture, opening text, opening audio, and their original order are especially easy to
recognize when retained together. Select the new hook from another source or from a later
self-contained action that still has a complete setup and result. Record the source time range for
the finished hook and fail the editorial gate when it directly reproduces a source opening.

This is a risk-control and editorial rule, not a guarantee of platform approval. Do not replace it
with random trimming, meaningless first frames, mirroring, or decorative effects. A useful source
opening may appear later only when it has a valid role in the new story and no longer functions as
the original opening package.

AI generation tools such as TikTok Symphony may supply a missing connector, product-safe motion
asset, or clearly labeled AI scene. Inspect product identity and behavior frame by frame; reject
generated footage that changes construction, color, quantity, operation, or implied performance.

## Batch differentiation

Changing only order, narration wording, opening clip, color treatment, or effects does not create a
new video direction. Across the batch, require a different viewer problem or desire, purchase
reason, supporting-shot combination, and conclusion where the evidence allows it. Reuse a strong
shot only when it serves a genuinely different meaning.

## Editorial quality gate

Watch the rendered video with sound from beginning to end. Confirm:

- the product and purchase reason are understandable;
- each cut advances the same sales logic;
- narration and visible action agree;
- actions retain enough setup and result to remain legible;
- effects, text, and sound are motivated and restrained;
- there is no avoidable real face, subtitle leakage, large patch, damaged crop, repeated ending,
  silent tail, or meaningless filler;
- the cover and publishing information describe the actual finished video.

A contact sheet, OCR report, waveform, or automated QA result cannot replace full-motion editorial
review.
