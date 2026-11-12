# Tracing a deep failure

1. Find the line that directly fails. Ask what called it and with which value; repeat up the chain until the value is first wrong. That place is the root cause. Fix there, never where the error appears.
2. Manual tracing stuck: add one probe before the failing operation (not after) that prints the argument, `cwd`, relevant env and `new Error().stack` (or the language's equivalent). In tests use stderr, not the logger, which may be suppressed. Run once, grep the probe tag, read the file names and line numbers in the stack.
3. Multi-component system (CI, build, service, database): probe each boundary once for what enters and leaves and whether config and env arrive. Run once, find the first boundary where data goes wrong, then investigate only that component.
4. Something appears during the test run (file, state) but the source is unknown: bisect by running test files one at a time and checking for the artifact after each.
5. After the fix, if the bad value could enter by other paths, add a cheap check at the entry point and at the dangerous operation. Test that bypassing the first check is caught by the second.
