Mocks and test doubles in a TDD loop.

- Mock only at system boundaries: external APIs, time, randomness, and sometimes the database (prefer a test DB) or file system.
- Never mock your own modules or internal collaborators.
- Assert on real behaviour, never on the mock itself or on call counts of a stub you set up.
- Pass external dependencies in (dependency injection) instead of constructing them inside the function.
- Prefer one function per external operation (`getUser`, `createOrder`) over one generic `fetch(endpoint, options)`; each mock then returns one shape with no branching in setup.
- Understand what the real dependency does (side effects, state) before replacing it.
- Keep test-only helpers in test utilities, not in production classes.
- Must mock everything or setup is huge: the code is too coupled; simplify the interface first.
- Do not assert constants or exact message wording; assert the behaviour that depends on them.
