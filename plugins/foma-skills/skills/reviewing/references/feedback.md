Use when acting on review feedback that someone else gave. Verify before implementing.

1. Read all items first. Restate any item in your own words; if any item is unclear, ask about it before implementing anything, because items may be related.
2. Check each suggestion against the codebase: correct for this stack and version? Breaks existing behaviour? Is there a reason the current code is the way it is? Does the reviewer have the full context?
3. A reviewer asking to "implement it properly": grep for real usage. Unused → propose removing it instead of building it out.
4. Wrong or unverifiable: push back with evidence (code, a passing test, a doc line) and a specific question. Cannot verify without something: say what you need and ask whether to investigate or proceed. Conflicts with an earlier decision of the user: stop and ask first.
5. Implement one item at a time, test each, check for regressions. Order: blocking (breaks, security), simple fixes, then complex ones.
6. Replies: state the fix or the requirement ("Fixed: <what changed>"). No performative agreement, no "you're absolutely right", no thanks. If you pushed back and were wrong, say so once, factually, and fix it.
7. Inline PR comments on GitHub: reply in the comment's thread, not as a top-level comment.
