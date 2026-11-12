# Flaky and timing bugs

- Goal is a higher failure rate, not a clean repro: loop the trigger many times, run in parallel, add load, narrow timing windows. Debug only once the rate is high enough to see.
- Replace fixed delays (`sleep`, `setTimeout`) with polling the real condition: check inside the loop with a fresh read, poll about every 10 ms, always a timeout whose error names what was awaited.
- Keep a fixed delay only when the timing itself is under test (debounce, tick interval). Wait for the triggering condition first, derive the delay from the known interval, and comment why.
- Pin what you can: clock, random seed, filesystem, network.
- Truly environmental or external cause after a full investigation: handle it (retry, timeout, clear error), record what you checked, and add logging for next time.
