# Architecture

This repository provides a deterministic, offline-only photo and video
archiver for Windows. The project emphasises data safety, auditability, and
idempotence: every operation should be traceable, testable, and reversible when
possible.

## Design Goals

- Absolute data safety
- Deterministic behavior
- Fully auditable operations and reporting
- Idempotent execution
- Human- and machine-readable outputs
- Configuration-driven behavior

## Core Principles

- Dry-run by default: no filesystem changes unless explicitly enabled.
- Traceability: every decision must record its data source and confidence.
- Non-destructive: do not delete or overwrite user files.
- Offline-only: no network, cloud dependencies, or telemetry.
- Configuration-driven: no hard-coded paths or magic constants.

## High-level Processing Flow

1. Load configuration
2. Scan configured source directories
3. Resolve capture datetime for each file
4. Generate canonical target filenames
5. Determine target year/month directories
6. (Optional) Copy/move files when enabled
7. Produce reports (Markdown + JSON)

Each step must be independently testable and observable.

## Module Responsibilities

- `cli.py`: argument parsing, mode selection, and the lightweight entrypoint.
  No business logic here.
- `config.py`: load, validate, and provide typed access to configuration.
- `scanner.py`: discover supported files and collect metadata (paths, sizes,
  timestamps). Must not modify files.
- `datetime_resolver.py`: determine the best capture datetime from EXIF,
  filename, or filesystem metadata and return a structured result
  (datetime, source, confidence).
- `renamer.py`: produce canonical filenames and handle collisions
  deterministically. Avoid overwrites unless explicitly allowed.
- `sorter.py`: compute target year/month folders and create directories
  only if permitted by configuration.
- `dedup.py`: identify duplicates (by hash/content). Report-only by
  default; never delete user files without explicit user action.
- `reporter.py`: collect actions, warnings, and errors; emit
  timestamped Markdown and JSON reports.
- `models.py`: shared dataclasses/enums used across modules.

## Canonical Naming

Month folders should follow a canonical, human-readable format, for example:

```
01_Januar
02_Februar
12_Dezember
```

Filename canonical format:

```
YYYY-MM-DD_HH-mm-ss_source.ext
```

Examples:

```
2017-05-26_14-32-10_exif.jpg
2021-09-14_20-33-44_filename.mp4
```

## Supported File Types

- Images: `.jpg`, `.jpeg`, `.png`, `.heic`
- Videos: `.mp4`, `.mov`, `.avi`

Unsupported files should be ignored and reported.

## Error Handling

- Errors do not stop processing; they are collected and reported.
- Partial success is allowed; no silent failures.

## Forbidden Behavior

The project strictly forbids:

- Deleting or overwriting user files without explicit consent.
- Making filesystem writes during dry-run.
- Performing filesystem writes outside the designated modules.
- Mixing CLI parsing with domain logic.

## Testing Requirements

- All logic must be unit-tested.
- Filesystem access should be mocked in tests; no test may touch real user
  data.
- Datetime resolution must be verified with fixtures.
