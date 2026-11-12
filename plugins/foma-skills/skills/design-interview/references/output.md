# Output files

Folder: the Design entry in `## Where things live`, else `docs/design/<feature>/` (kebab-case). DESIGN.md sits at the project root unless the contract names another place.

## choice.md

```markdown
# Design choice: <feature>
Date: YYYY-MM-DD · Mode: web | mobile | game · Round: 1 | 2

Picked: <A | B | C | D>, lens <…>
Mixed: <part = variant, …, or "none">
Why (user's words): <…>
Rejected: <variant — the reason the user gave>
State: <tokens or tuned values pasted from the gallery>
```

## DESIGN.md

One home for the look; implementing skills read it. Keep it to values and rules, no essays.

```markdown
# Design

## Direction
<one line: the lens and feel picked> · references: <…> · never: <anti-reference>

## Tokens
Colour: base, surface, text, muted, accent (where it may appear), danger
Type: families, scale (sizes), weights, line heights
Spacing: scale · Radius: values · Shadow: none | <value>
Motion: durations, easing, what may move

## Rules
- Do: <3-5 lines from the choice>
- Don't: <the anti-reference and avoid-list items the user confirmed>

## Screens
- <feature>: docs/design/<feature>/choice.md
```

Game projects add the **Feel** and **Art direction** sections of game mode.

On an existing DESIGN.md: change only the sections this choice touches, keep the user's wording, show the diff and wait for ok. A conflict with an earlier choice is asked about, never overwritten silently.
