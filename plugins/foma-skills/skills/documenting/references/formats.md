# Doc formats

Use only when the project has no existing format to copy.

## Decision log
One file `decisions.md`, newest last, ids `DEC-001`, `DEC-002`. Table row or short block:

```
| DEC-007 | 2026-03-02 | Manual SQL, no ORM | ORM; query builder | Reports need hand-tuned joins | accepted |
```

Big projects: `decisions/NNNN-slug.md` (next number = highest + 1), body of 1-3 sentences (context, decision, why), optional `Status:` line, optional Considered options and Consequences only when non-obvious.

What passes the gates: architecture shape, lock-in technology (database, bus, auth, deploy target), boundaries and explicit no-s, deliberate deviations from the obvious path, constraints invisible in code (compliance, partner contracts), non-obvious rejected alternatives. Library picks that are cheap to swap do not.

## Short feature doc
`<docs home>/<topic>.md`: one paragraph on what it is and why, how to run or change it, gotchas. Link it from the README or CLAUDE.md `## Where things live`.

## Glossary
Only when the project has domain-specific terms that are used inconsistently. `GLOSSARY.md` (or inside the docs home):

```
**Order**: A customer's request to buy. 1-2 sentences, what it is, not what it does.
_Avoid_: purchase, transaction
```

Pick one word per concept and list the rejected ones under `_Avoid_`. Exclude general programming terms and implementation detail. When the user's wording conflicts with a defined term, point it out and ask which is meant. Update it the moment a term is settled.
