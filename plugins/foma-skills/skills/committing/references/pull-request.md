# Pull request

Create a PR only when the user asks for one in this conversation, and never push to do it without their explicit ok: show the branch, base, title and body, then ask once.

1. Check the branch is not the default branch (if it is, propose a new branch name first), `git log <base>..HEAD --oneline` and `git diff <base>...HEAD --stat`. The PR describes all commits on the branch, not just the last.
2. Title: imperative, under about 70 chars, in the project's commit style.
3. Body, brief, no preamble, in the project's domain terms (use its glossary if one exists):
   - **Summary**: the smallest view that makes the point: a sentence, pseudocode for logic, a call or file tree for structure, a diff sketch for a change to existing shape. Place it next to the text it supports; do not stack several.
   - **Evidence**: before and after. Prefer a screenshot for visual changes, otherwise the exact test or command output that failed and now passes. If nothing was run, say so.
   - **Merge danger**: one-way or two-way door (can it be rolled back cheaply?), and the blast radius in a word or two (consumers, migrations, layout, mobile). Skip for trivial changes.
4. Create with `gh pr create` after the ok; return the URL.
