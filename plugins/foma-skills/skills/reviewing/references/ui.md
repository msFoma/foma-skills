Adapted from unslop by heydamir, CC BY 4.0, https://github.com/heydamir/unslop; changes: condensed and reworded.

Use for UI code. The project's design system and existing components override everything here. Report findings in this order, as `file:line` with a suggested fix; do not redesign while reviewing.

1. **Spacing:** values off the project's scale or a 4px grid (`mt-[13px]`); equal things with unequal sizes; no grouping (gaps inside a group not smaller than between groups); icons and labels not aligned in a column.
2. **Color:** hue gradients on surfaces, gradient text, colored glows or shadows, blobs behind content, neon borders; more than one accent in the chrome; many near-identical text colors instead of primary/secondary/muted; accent text below 4.5:1 contrast.
3. **Icons:** emoji used as icons or label decoration; mixed icon sets, sizes or strokes; icons with their own colors.
4. **Copy:** exclamation marks; greeting headlines ("Welcome back! 👋"); hype words (supercharge, seamless, unlock, magic); unverifiable claims ("10x faster", "loved by 10,000+ teams"); "New ✨" badges; placeholder data like `123,456`; a change without what it compares to.
5. **Type:** heavy 700-900 headings; uppercase tracked labels; negative tracking on small text; italic emphasis; numbers without tabular figures or in mixed formats.
6. **Layout:** everything stacked and centered by default; more than one primary action in a hero; an app squeezed into a narrow column; no mobile stacking.
7. **Details:** inner radius not equal to outer radius minus padding; rainbow bars in one series; stat cards padded with sparklines or icons; glowing active states; missing hover or visible keyboard focus states.
8. **Motion:** `animate-pulse` or ping on non-live things, `transition-all`, bouncy springs, hover scale on cards, animated width/height/margins, looping decoration.
9. **Visuals:** decorative filler (orbs, blobs, glowing grids) that says nothing about the product.

Template check: swap in another product's name; if the screen still fits, say the copy and visuals are generic. Severity: mostly nice-to-have; must-fix only for accessibility (contrast, focus, tap targets) or broken layout.
