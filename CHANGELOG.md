# Changelog

All notable changes to this project are listed here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- README header with a stats strip, navigation and language pills; numbered install steps; an animated "first 5 minutes" terminal card; a teaser for the live skill map.
- `CODE_OF_CONDUCT.md`, this changelog and Dependabot updates for GitHub Actions.
- A pixel-art banner and three link buttons for the GitHub profile (`scripts/assets/make_profile_banner.py`, `docs/assets/profile/`), with invariant tests in `scripts/test_assets.py`.

### Changed
- The repository moved to the account `msFoma`: install with `/plugin marketplace add msFoma/foma-skills`. The old repository path still redirects; the old Pages address does not, the live map is now at `https://msfoma.github.io/foma-skills/graph.html`.
- Decisions and the test ledger moved to `docs/engineering/`; the maintainer's private research notes are no longer part of the repository.
- The art generators moved to `scripts/assets/`.
- The three agents are called templates (the plugin installs none itself; `groundwork` copies them into a project). The install notes now say how to try the pack in one project, that Windows needs Git Bash and that `.scratch/` belongs in `.gitignore`.

## [0.1.0] - 2026-11-13

First public pre-release.

### Added
- 17 skills (16 automatic, 1 manual) for the work cycle: shaping, planning, executing, committing, handoff, tdd, debugging, reviewing, refactoring, documenting, tidying, learning, skill-finder, writing-skills, groundwork, design-interview, tuning.
- Three agent templates (`implementer`, `reviewer`, `explorer`, installed into your project by `groundwork`) and a session-start hook that adds one router line and keeps a local fire log (nothing leaves your project).
- Live interactive skill map (`docs/graph.html`), Russian documentation (`README.ru.md`, `docs/ru/`), static skill checks, trigger and smoke test harness.

[Unreleased]: https://github.com/msFoma/foma-skills/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/msFoma/foma-skills/releases/tag/v0.1.0
