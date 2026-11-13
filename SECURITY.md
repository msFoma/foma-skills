# Security

foma-skills is a set of instruction files plus a few small POSIX shell scripts (session-start hook, fire-log hook). It makes no network calls of its own; `skill-finder` fetches third-party skills only when you ask it to, and installs them only after your ok.

## Reporting a problem

Please use GitHub's **private** vulnerability reporting: the repository's *Security* tab, then *Report a vulnerability*. Do not open a public issue for anything that could be exploited.

In scope: the hook scripts in `plugins/foma-skills/hooks/`, anything a skill could be tricked into doing without your ok (writing, deleting, pushing, installing), and the vetting steps of `skill-finder`.

## What the usage log stores

`.scratch/fires.jsonl` in your project: skill name, UTC time, session id. No prompt text. Disable it with `FOMA_FIRE_LOG=off`.
