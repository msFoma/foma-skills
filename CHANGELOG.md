# Changelog

All notable changes to this project are listed here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- README header with a stats strip, navigation and language pills; numbered install steps; an animated "first 5 minutes" terminal card; a teaser for the live skill map.
- `CODE_OF_CONDUCT.md`, this changelog and Dependabot updates for GitHub Actions.

### Changed
- Decisions and the test ledger moved to `docs/engineering/`; the maintainer's private research notes are no longer part of the repository.
- The art generators moved to `scripts/assets/`.

## [0.1.0] - 2026-11-13

First public pre-release.

### Added
- 17 skills (16 automatic, 1 manual) for the work cycle: shaping, planning, executing, committing, handoff, tdd, debugging, reviewing, refactoring, documenting, tidying, learning, skill-finder, writing-skills, groundwork, design-interview, tuning.
- Three agent templates (`implementer`, `reviewer`, `explorer`, installed into your project by `groundwork`) and a session-start hook that adds one router line and keeps a local fire log (nothing leaves your project).
- Live interactive skill map (`docs/graph.html`), Russian documentation (`README.ru.md`, `docs/ru/`), static skill checks, trigger and smoke test harness.

[Unreleased]: https://github.com/t8jwscc7qy-sketch/foma-skills/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/t8jwscc7qy-sketch/foma-skills/releases/tag/v0.1.0
