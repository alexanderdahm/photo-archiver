# Contributing Guidelines

This document defines mandatory rules for all contributions to this repository,
including AI-assisted contributions (e.g. Microsoft Copilot).

These rules are normative. Violations are considered bugs.

---

## 1. General Rules

- Follow `ARCHITECTURE.md` strictly
- Follow the development order defined in `PLAN.md`
- Prefer explicit, readable code over clever code
- All behavior must be deterministic
- Safety and auditability are higher priority than performance

---

## 2. AI-Assisted Development Rules

When using AI tools:

- Always reference the current phase from `PLAN.md`
- Explicitly state forbidden behavior in prompts
- Require unit tests for all logic
- Never accept code that violates dry-run guarantees
- Never allow silent filesystem modifications

---

## 3. Code Style

- Language: Python 3.11+
- Use type hints everywhere
- Use `dataclasses` for structured data
- Prefer pure functions where possible
- No global mutable state

---

## 4. Filesystem Safety Rules

- All filesystem access must be explicit
- All write operations must be guarded by:
  - configuration
  - CLI flags
- Never overwrite files
- Never delete files

---

## 5. Testing Rules

- All logic must be unit-tested
- Filesystem access must be mocked
- No test may modify real user data
- Tests must be deterministic and repeatable
- Use pytest for all tests

---

## 6. Reporting Rules

- Every action must be reportable
- Reports must explain:
  - what was done
  - why it was done
  - with which confidence
- No silent fallbacks

---

## 7. Commit Rules

- One logical change per commit
- Reference PLAN phase in commit message
  Example:

## 8. Forbidden Practices

The following practices are forbidden:

- Hard-coded paths
- Hard-coded filenames
- Hard-coded dates
- Implicit assumptions about user data
- Catch-all exception handling without reporting
- Mixing CLI code with domain logic
