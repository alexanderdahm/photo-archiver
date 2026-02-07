## Phase 1 – Configuration & CLI

Context
This repository follows a strict, phase-based development plan.
You are currently implementing Phase 1: Configuration & CLI as defined in PLAN.md.
All architectural rules in ARCHITECTURE.md are normative and must be followed strictly.

Task
Review and, if necessary, implement or refine the Phase 1 components:

src/photo_tool/config.py

src/photo_tool/cli.py

corresponding unit tests in tests/

Requirements (Strict)

Do NOT implement functionality from Phase 2 or later

Do NOT perform any filesystem write operations

Do NOT scan directories or touch user files

Dry-run must remain the default behavior

All behavior must be configuration-driven

Configuration validation must fail fast and explicitly

Use typed dataclasses for configuration

Raise clear, specific errors for invalid configuration

All logic must be covered by unit tests

Quality Constraints

Deterministic behavior only

Explicit code preferred over clever shortcuts

No hidden side effects

No hard-coded paths or constants

Code must be readable and testable

Exit Criteria

CLI starts successfully with a valid config

Invalid config causes a clear error

No filesystem access beyond reading the config file

All tests pass

If any requirement cannot be fulfilled, explain why instead of guessing.