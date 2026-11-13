<div align="center">

<img src="docs/assets/banner.jpg" alt="Foma Skills: lightweight skills for Claude Code" width="100%">

<p><img src="docs/assets/header/lang-en.on.svg" height="34" alt="English"> <a href="README.ru.md"><img src="docs/assets/header/lang-ru.off.svg" height="34" alt="Русский"></a></p>

<img src="docs/assets/header/stats.en.svg" width="860" alt="17 skills, about 1.4k tokens always on, 3 helper agents, Apache-2.0, version 0.1.0 pre-release">

[![validate](https://github.com/t8jwscc7qy-sketch/foma-skills/actions/workflows/validate.yml/badge.svg?branch=main)](https://github.com/t8jwscc7qy-sketch/foma-skills/actions/workflows/validate.yml)

### Say what you want. The right skill wakes up, asks first, and does the careful part.

<p><a href="#install"><img src="docs/assets/header/nav-install.en.svg" height="40" alt="Install"></a> <a href="#what-you-get"><img src="docs/assets/header/nav-what-you-get.en.svg" height="40" alt="What you get"></a> <a href="#first-5-minutes"><img src="docs/assets/header/nav-first-5-minutes.en.svg" height="40" alt="First 5 minutes"></a> <a href="#skills"><img src="docs/assets/header/nav-skills.en.svg" height="40" alt="All skills"></a> <a href="docs/ru/quickstart.md"><img src="docs/assets/header/nav-docs.en.svg" height="40" alt="Документация на русском"></a></p>

</div>

> [!NOTE]
> **New to skills?** A *skill* is a short instruction file that Claude loads only when your request matches it. Without skills Claude improvises every time; with them it follows a proven routine (plan, test first, small commits) and asks before it changes anything important.

<a id="install"></a>
## <img src="docs/assets/icons/install.svg" width="28" height="28" align="absmiddle" alt=""> Install

In Claude Code, run two commands:

```
/plugin marketplace add t8jwscc7qy-sketch/foma-skills
/plugin install foma-skills@foma
```

Then **restart Claude Code in your project** (the plugin loads when a session starts) and just talk to it. Nothing else to configure.

> [!TIP]
> Try it on a small or throwaway project first. To remove it: `/plugin uninstall foma-skills@foma`. Install only for one project with `--scope local` (`claude plugin install foma-skills@foma --scope local`).

<a id="what-you-get"></a>
## <img src="docs/assets/icons/what-you-get.svg" width="28" height="28" align="absmiddle" alt=""> What you get

| <img src="docs/assets/icons/f-light.svg" width="18" height="18" align="absmiddle" alt=""> **Light** | <img src="docs/assets/icons/f-careful.svg" width="18" height="18" align="absmiddle" alt=""> **Careful** |
|---|---|
| Only short skill descriptions (≈1.4k tokens) are always in context. A skill's full text loads only when it fires, so your limits go to your work. | Skills **propose first and write after your ok**. Nothing is pushed on its own, files are removed reversibly, third-party skills are vetted before install. |
| <img src="docs/assets/icons/f-tested.svg" width="18" height="18" align="absmiddle" alt=""> **Tested** | <img src="docs/assets/icons/f-open.svg" width="18" height="18" align="absmiddle" alt=""> **Open** |
| Every skill passes static checks, trigger tests and a smoke run. Failures and fixes are logged honestly in [`research/`](research/). | Apache-2.0. The whole research history, decisions and test ledger are public. |

<a id="first-5-minutes"></a>
## <img src="docs/assets/icons/first-5-minutes.svg" width="28" height="28" align="absmiddle" alt=""> Your first 5 minutes

You do not call skills by name. You describe the work, and the matching skill wakes up (illustrative session):

![A terminal session: you describe a loyalty points system and the shaping skill asks questions; planning makes a plan; executing runs it; committing makes small commits; handoff saves a note for tomorrow](docs/assets/charts/first-5-minutes.en.svg)

You can also call any skill by hand: `/foma-skills:planning`, `/foma-skills:tidying`, ...

<a id="how-a-task-flows"></a>
## <img src="docs/assets/icons/task-flow.svg" width="28" height="28" align="absmiddle" alt=""> How a task flows

![A typical task: your idea goes through shaping, planning, executing, committing and handoff; executing uses tdd, debugging and reviewing on the way](docs/assets/charts/task-flow.en.svg)

<a id="skills"></a>
## <img src="docs/assets/icons/all-skills.svg" width="28" height="28" align="absmiddle" alt=""> All 17 skills

Say something like the example in the third column. **auto** = fires on its own when the task fits, **manual** = you call it.

### <img src="docs/assets/icons/g-setup.svg" width="24" height="24" align="absmiddle" alt=""> Setup and upkeep

| Skill | Mode | Say something like | What it does |
|---|---|---|---|
| <img src="docs/assets/icons/skill-groundwork.svg" width="18" height="18" align="absmiddle" alt=""> `groundwork` | auto | "Set up this project for Claude" | Sets up or audits a project: safety, a short `CLAUDE.md` contract, docs layout, helper agents. Writes after your ok. |
| <img src="docs/assets/icons/skill-tidying.svg" width="18" height="18" align="absmiddle" alt=""> `tidying` | auto | "The repo is messy, clean it up" | Finds junk by tier, shows a report, removes reversibly (`.trash/` or `git rm`). |
| <img src="docs/assets/icons/skill-learning.svg" width="18" height="18" align="absmiddle" alt=""> `learning` | auto | "You keep forgetting X, make it a rule" | Turns a repeated mistake into the smallest lasting fix and prunes stale rules. Proposes first. |
| <img src="docs/assets/icons/skill-skill-finder.svg" width="18" height="18" align="absmiddle" alt=""> `skill-finder` | auto | "Is there a skill for release notes?" | Finds a third-party skill, vets every file, installs only after your ok. |
| <img src="docs/assets/icons/skill-handoff.svg" width="18" height="18" align="absmiddle" alt=""> `handoff` | auto | "Wrap up, I'll continue tomorrow" | Writes a short session note so the next session resumes in one step. |

### <img src="docs/assets/icons/g-proc.svg" width="24" height="24" align="absmiddle" alt=""> Ideas, design and build

| Skill | Mode | Say something like | What it does |
|---|---|---|---|
| <img src="docs/assets/icons/skill-shaping.svg" width="18" height="18" align="absmiddle" alt=""> `shaping` | auto | "I want to build a loyalty points system" | Questions a raw idea until it becomes an approved spec. |
| <img src="docs/assets/icons/skill-design-interview.svg" width="18" height="18" align="absmiddle" alt=""> `design-interview` | auto | "I need a new look for the settings screen" | Shows three different variants side by side in the browser and records your pick in `DESIGN.md`. |
| <img src="docs/assets/icons/skill-planning.svg" width="18" height="18" align="absmiddle" alt=""> `planning` | auto | "Make a plan for the refunds feature" | Breaks work into ordered, checkable tasks and picks a model and effort per task. Small change: no plan needed. |
| <img src="docs/assets/icons/skill-executing.svg" width="18" height="18" align="absmiddle" alt=""> `executing` | auto | "Execute the plan" | Runs the plan task by task with checks, one review per feature, archives the plan. |

### <img src="docs/assets/icons/g-meth.svg" width="24" height="24" align="absmiddle" alt=""> Methods

| Skill | Mode | Say something like | What it does |
|---|---|---|---|
| <img src="docs/assets/icons/skill-debugging.svg" width="18" height="18" align="absmiddle" alt=""> `debugging` | auto | "Why does checkout throw an error?" | Reproduce, form a hypothesis, find the root cause, then fix with a regression test. |
| <img src="docs/assets/icons/skill-reviewing.svg" width="18" height="18" align="absmiddle" alt=""> `reviewing` | auto | "Review my branch, is it ready to merge?" | Reviews against your standards and the spec, ends with ship or fix-first. |
| <img src="docs/assets/icons/skill-refactoring.svg" width="18" height="18" align="absmiddle" alt=""> `refactoring` | auto | "Refactor report.py, remove the duplication" | Changes structure, never behaviour, only after tests are green. |

### <img src="docs/assets/icons/g-atom.svg" width="24" height="24" align="absmiddle" alt=""> Atomic

| Skill | Mode | Say something like | What it does |
|---|---|---|---|
| <img src="docs/assets/icons/skill-tdd.svg" width="18" height="18" align="absmiddle" alt=""> `tdd` | auto | "Add the discount rule test-first" | Red-green slices with independent expected values. |
| <img src="docs/assets/icons/skill-committing.svg" width="18" height="18" align="absmiddle" alt=""> `committing` | auto | "Commit my changes" | Small commits in your project's style; never pushes on its own. |
| <img src="docs/assets/icons/skill-documenting.svg" width="18" height="18" align="absmiddle" alt=""> `documenting` | auto | "Record the decision to use Decimal" | Puts docs and decision records in their home. |

### <img src="docs/assets/icons/g-meta.svg" width="24" height="24" align="absmiddle" alt=""> Meta

| Skill | Mode | Say something like | What it does |
|---|---|---|---|
| <img src="docs/assets/icons/skill-writing-skills.svg" width="18" height="18" align="absmiddle" alt=""> `writing-skills` | auto | "Write a skill for our release routine" | Writes or tightens a skill: short description, tight steps, tested triggers. |
| <img src="docs/assets/icons/skill-tuning.svg" width="18" height="18" align="absmiddle" alt=""> `tuning` | **manual** | `/foma-skills:tuning` | Reads the usage log and saved test runs, finds skills that never fire or keep failing, proposes the smallest fix. Spends tokens only on flagged skills. |

### <img src="docs/assets/icons/skill-map.svg" width="24" height="24" align="absmiddle" alt=""> How the skills connect

![Skill map: five groups of skills, the CLAUDE.md contract, the helper agents and who calls whom](docs/assets/charts/skill-map.en.svg)

**[Open the live, interactive map](https://t8jwscc7qy-sketch.github.io/foma-skills/graph.html)**: hover a skill, click for details, press “Play a task”. (Source: [`docs/graph.html`](docs/graph.html).)

<a id="safe"></a>
## <img src="docs/assets/icons/safe.svg" width="28" height="28" align="absmiddle" alt=""> Safe by design

![The propose-first cycle: you ask, the skill reads, shows the exact change, you say ok, only then it writes, and the report ends with what was not checked](docs/assets/charts/propose-first.en.svg)

- **Propose first.** Skills that change files show the exact change and write only after your ok.
- **No surprise pushes.** `committing` never pushes on its own; destructive commands are not part of any skill.
- **Reversible cleanup.** `tidying` moves files to `.trash/` or uses `git rm`; it never runs `rm -rf`.
- **Vetted installs.** `skill-finder` reads every file of a third-party skill through a read-only agent, pins a commit and never passes `-y`.
- **Honest reports.** Each skill ends with what it did not check.

<a id="usage-log"></a>
## <img src="docs/assets/icons/usage-log.svg" width="28" height="28" align="absmiddle" alt=""> Usage log and privacy

A tiny hook counts which skills fire: skill name, UTC time and session id go to `.scratch/fires.jsonl` **in your project**. No prompt text is stored and nothing is sent anywhere. After about 20 sessions `/foma-skills:tuning` can show which skills never fired. Turn it off with the environment variable `FOMA_FIRE_LOG=off`, or delete the file.

<a id="cost"></a>
## <img src="docs/assets/icons/cost.svg" width="28" height="28" align="absmiddle" alt=""> What it costs in tokens

![Tokens per skill: about 80 to 90 always on, and 0.7 to 1.4k only when the skill fires](docs/assets/charts/token-cost.en.svg)

Claude keeps every installed skill's name and one-paragraph description in context so it can pick one: about 80–90 tokens each, and the pack keeps descriptions short (≤250 characters). On top of that the session-start hook adds one short router line. A skill's full instructions (about 0.7–1.4k tokens) are read only when it fires, and long details live in reference files read only when needed. The ≈1.4k figure is Claude Code's own estimate; check it yourself with `claude plugin details foma-skills`.

<details>
<summary><b><img src="docs/assets/icons/dropped.svg" width="20" height="20" align="absmiddle" alt=""> Skills that were tried and dropped</b></summary>

Rules the models already follow are not skills here. Tested on Haiku and Sonnet against a no-skill and a one-line baseline (DEC-025):

| Was | Result | Now |
|-----|--------|-----|
| `coding` (minimal scope, no fake fallbacks) | Fired on 5–6 of 10 code prompts; never fired in a long task; no gain over baseline | Rules in the `implementer` agent + one CLAUDE.md line |
| `verifying` (evidence before "done") | Fired on 7–8 of 10; no gain on short tasks; a one-line CLAUDE.md rule did as well (6/6) on the long task | Rules in `implementer`/`reviewer` + one CLAUDE.md line |

</details>

<a id="docs"></a>
## <img src="docs/assets/icons/docs.svg" width="28" height="28" align="absmiddle" alt=""> Documentation

| | |
|---|---|
| <img src="docs/assets/icons/lang.svg" width="18" height="18" align="absmiddle" alt=""> **Русская документация** | [Быстрый старт](docs/ru/quickstart.md) · [Справочник по скиллам](docs/ru/skills.md) · [Как это работает](docs/ru/how-it-works.md) · [FAQ](docs/ru/faq.md) |
| <img src="docs/assets/icons/standard.svg" width="18" height="18" align="absmiddle" alt=""> **Lite standard** | How every skill is written and checked: [`docs/lite-standard.md`](docs/lite-standard.md) |
| <img src="docs/assets/icons/research.svg" width="18" height="18" align="absmiddle" alt=""> **Research** | Sources, decisions and the test ledger: [`research/`](research/) |
| <img src="docs/assets/icons/credits.svg" width="18" height="18" align="absmiddle" alt=""> **Credits** | Third-party work: [`CREDITS.md`](plugins/foma-skills/CREDITS.md) |

> [!IMPORTANT]
> **Status: pre-release (0.1.0).** All 17 skills pass static checks, trigger tests (the 16 automatic ones) and one smoke run each. Not done yet: the final eval against a no-pack baseline. The numbers in `research/` come from small samples; treat them as indicative, not proven.

## <img src="docs/assets/icons/contributing.svg" width="28" height="28" align="absmiddle" alt=""> Contributing

> <img src="docs/assets/icons/report.svg" width="18" height="18" align="absmiddle" alt=""> **A skill did not fire?** That is the most useful report you can send: [tell us the exact words you said](https://github.com/t8jwscc7qy-sketch/foma-skills/issues/new?template=skill_didnt_fire.yml).

Issues and pull requests are welcome; see [`CONTRIBUTING.md`](CONTRIBUTING.md). The pack stays small on purpose: a skill earns its place only if it beats a plain one-line instruction in tests.

## <img src="docs/assets/icons/license.svg" width="28" height="28" align="absmiddle" alt=""> License

[Apache-2.0](LICENSE). Copyright 2026 Vladislav Fomin (foma); see [`NOTICE`](plugins/foma-skills/NOTICE).

README icons: [Lucide](https://lucide.dev) (ISC, recoloured; [licence](docs/assets/icons/LICENSE-lucide.txt)) plus one original icon (`safe`). Regenerate with `scripts/make_icons.py`.
