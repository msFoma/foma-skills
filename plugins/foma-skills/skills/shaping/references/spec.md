# Spec format

Path: the Specs entry in `## Where things live`, else `docs/specs/<name>.md` (kebab-case name). Create it as `Status: draft` after the first answered round, so the work can resume; set `approved (YYYY-MM-DD)` only on the user's explicit ok.

Write for a capable builder who can't ask the user. Their words for the problem and goals; your fill-ins end with "(Claude's call: <reason>)". No file paths or code: they go stale. Exception: a schema or state shape that encodes a decision better than prose. Drop empty sections; a small change keeps Problem, Solution, Not doing, a few lines each.

```markdown
# <Name>
Status: draft

## Problem
Who hurts, when (the concrete moment), what they do today instead. Their words.

## Appetite
Time it is worth; what gets cut first if it runs over.

## Solution
What the user gets, from their side. Text sketch if there is something to look at.

## Approaches
2-3 considered, the trade-off of each, which was picked and why.

## Decisions
Parts of the how that were decided, as decided. Your calls marked.

## Testing
The behaviour that proves it works; the seam to test at (highest existing one, ideally one).

## Not doing
No-gos, and anti-goals: what would make it a failure even if it works.

## Risks and assumptions
Rabbit holes; the 2-3 riskiest assumptions and how to check each cheaply.

## Open questions

## Clarifications
- YYYY-MM-DD: Q -> A
```

## Builder check (full path only)

Before asking for approval, send a fresh subagent (`model: sonnet`) this brief, with the path filled in:

> You are a capable builder in this domain. Read <spec path>. You must plan the build and can't talk to its author. List only the questions you'd have to guess at where a wrong guess changes the plan, most important first, each with why. Skip what the spec leaves to the builder, what you could decide yourself, and wording nits. If nothing is left, say "nothing important left". Answer in ≤10 lines.

Sort the answers: already answered by the conversation or the project → write the answer in; minor (a sensible builder would settle it) → settle it, mark as your call; theirs (only the user can answer, and it changes what gets built) → one message, most important first. That is the only round the check produces.
