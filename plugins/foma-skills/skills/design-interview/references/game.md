# Game mode

Feel can't be chosen by reading. Variants here are playable micro-prototypes of one mechanic, each with live sliders.

## Interview (replaces step 3)
- The mechanic or moment to decide: jump, dash, hit, camera, aiming, a menu or HUD screen. One per session.
- The core loop in one sentence, and where this moment sits in it.
- 3 feel words for the moment (snappy, floaty, heavy, crunchy) and reference games for feel, not looks; what feels bad in them.
- Controls and target platform (keyboard, gamepad, touch).

Turn feel words into numbers before briefing (step 4): e.g. jump height in tiles, time to apex, fall gravity multiplier, coyote time, input buffer, acceleration and stop time, hit-stop length, shake amplitude.

## Lenses
- **safe**: genre-standard values from the references.
- **bold**: one quality pushed hard (very fast, very heavy, huge hit-stop).
- **odd**: an unusual rule (variable gravity on hold, mid-air redirect, slow-motion near danger).

## Prototype brief (on top of the variant brief, minus its web-only lines)
- One `<canvas>`, shapes only, no assets; fixed-timestep update in `requestAnimationFrame`; restart key `R`.
- A small level that exercises the mechanic (gaps, a wall, a target).
- Every tunable as a labelled slider with units and its current value; a **juice** toggle (shake, squash, particles) so feel and juice are judged apart.
- Units are engine-agnostic: state the scale once (1 tile = 32 px), values in tiles and seconds.
- `window.FOMA.tokens` holds the current slider values, updated on every change.
- HUD or menu screens are briefed as web variants with the game's palette and an in-game frame.

## Output
`choice.md` lists the tuned values (copied from the gallery state) with units. DESIGN.md gets a **Feel** section (values per mechanic, juice on/off, why) and, when the look was decided, an **Art direction** section: references, palette, mood, lighting, do/don't, HUD rules.
