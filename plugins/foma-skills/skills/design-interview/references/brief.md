# Variant brief

Fill every `<…>` and send one brief per variant. The agent has no access to the interview, so the brief is all it knows.

```
Build one design variant as a single self-contained HTML file: <path>/<a|b|c>.html.
Screen: <what screen or moment, for whom, the one thing it must make easy>.
Platform: <web desktop+mobile | iOS (HIG) | Android (Material 3)>; must work at 375, 768 and 1440 px wide.
Lens: <safe | bold | odd> — <one sentence: the direction this variant takes>.
Specs (binding): <the approved table: type, colour, spacing, radius, motion, layout idea>.
Existing system: <tokens, components or "none">; where you break it, say so.
Content: <real copy and data, or the files to take it from>. No lorem, John Doe, Acme, round fake numbers.
Avoid: <the user's anti-reference> and the list below.
Technical: inline <style> and <script> only; no CDN, fetch or modules; web fonts only via a Google Fonts <link>. Include designed states where they apply: empty, loading, error, disabled, hover, keyboard focus.
At the end of <body>, add:
<script>window.FOMA={lens:"<lens>",tokens:{/* final colours, fonts, sizes, radius */}};addEventListener("message",e=>{if(e.data==="foma:get")parent.postMessage({type:"foma:state",lens:FOMA.lens,state:FOMA.tokens},"*")});</script>
Do not touch any other file. Answer in ≤10 lines: lens, three key choices, final tokens, anything from the specs you could not follow.
```

## Avoid-list (generic AI look)

Pass this list with every brief; step 7 greps for the checkable ones.

- Inter, Roboto or a bare system sans as the display face; one weight everywhere.
- Purple, indigo or violet accents; purple-to-blue gradients; gradient text; cyan glow on dark; glassmorphism.
- Centered hero with one button above three equal feature cards; an icon tile above every heading; cards inside cards.
- Rounded corners and soft shadows on everything; identical hover on every element; decorative looping motion.
- Everything centered, uniform rhythm, no clear first thing to look at.
- Emoji as icons; hype copy (seamless, supercharge, unlock); exclamation marks; greeting headlines.
- Grey text on a coloured background; more than one accent colour in the chrome.

Grep for: `Inter`, `Roboto`, `#6366f1`, `#8b5cf6`, `indigo`, `violet`, `purple`, `background-clip: *text`, `backdrop-filter`, `lorem`, `John Doe`, `Acme`. A hit is fine only when the user's specs ask for it.
