# Contributing

Thanks for helping. foma-skills stays small on purpose: a skill earns its place only if it beats a plain one-line instruction in tests.

## Before you start

- Open an issue first for a new skill or a large change. Fixes and wording improvements can go straight to a pull request.
- Read `docs/lite-standard.md`. Every skill follows it: layout, frontmatter keys, description and token caps, report format, attribution.
- Decisions and their evidence live in `research/`. Link IDs (`DEC-NNN`, `FACT-NNN`) when your change depends on them.

## Writing or changing a skill

1. Run `/foma-skills:writing-skills` (or follow the standard by hand).
2. Keep one skill per pull request.
3. If you adapt someone else's work, add a row to `plugins/foma-skills/CREDITS.md` (source repo pinned to a commit sha, license, what was taken) and copy the source's license text to `plugins/foma-skills/licenses/<owner>-<repo>.txt`. No license means ideas only, in your own words.
4. Check before you push:

   ```
   claude plugin validate . --strict
   claude plugin validate plugins/foma-skills --strict
   ```

5. Describe in the pull request how you tested triggering and the task (see §8 of the standard).

## Russian docs

The user-facing docs also exist in Russian (`README.ru.md`, `docs/ru/`). If your change alters what a user sees (a skill's behaviour, install steps, numbers), update both languages or say in the pull request that the Russian side needs an update.

## License

By contributing you agree that your work is licensed under Apache-2.0 (`LICENSE`).
