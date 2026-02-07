# Photo Archive Tool

A deterministic, offline-only tool to organize photo and video archives
by capture date on Windows systems.

This project is designed to be safe by default and fully auditable.
It is explicitly structured for AI-assisted development (e.g. Microsoft Copilot).

---

## Core Features

- Normalize inconsistent year/month folder structures
- Rename photos and videos based on capture datetime
- Automatically sort unsorted files into the archive
- Handle images and videos consistently
- Dry-run mode by default
- Generate detailed audit reports (Markdown + JSON)

---

## Safety Guarantees

- No files are modified unless `--apply` is explicitly provided
- Files are never deleted

# Plan

Kurzplan für Implementierung, Tests und Release der Photo-Archiver-Toolchain.

## Purpose

Liefern eines deterministischen, daten-sicheren Werkzeugs zum Sortieren,
Umbenennen und Berichtigen von Foto- und Videobibliotheken auf Windows.

## Milestones

1. Project scaffold and basic CLI (done)
2. Core features: scanning, datetime resolution, renaming, sorting
3. Safety and reporting: dry-run, audit logs, JSON/Markdown reports
4. Tests, fixtures and CI configuration
5. Release: package and documentation

## Phases and Tasks

- Setup
  - Provide `pyproject.toml`, example config and docs.
  - Create package skeleton under `src/photo_tool`.

- Core implementation
  - Implement `scanner.py`, `datetime_resolver.py`, `renamer.py`,
    `sorter.py`, and `dedup.py` (detection only).
  - Produce canonical filename and folder logic.

- Safety & reporting
  - Implement `--dry-run` as default behavior.
  - Produce append-only Markdown and JSON reports via `reporter.py`.

- Testing
  - Unit tests for each module; mock filesystem access.
  - Fixtures in `tests/fixtures` for datetime and EXIF cases.

- Release
  - Add packaging metadata and a simple release checklist.

## Quick Usage

Dry-run (default):

```powershell
photo-tool run --config config.yaml
```

Apply changes:

```powershell
photo-tool run --config config.yaml --apply
```

## Configuration

All behavior is controlled via YAML (`config.example.yaml`). See the
repository root for a full example.

## Reporting

- Markdown report (human-readable)
- JSON report (machine-readable)
- Reports include summaries, renames, moves, warnings and errors; they are
  timestamped and append-only.

## Testing & Safety

- No tests may touch real user data; filesystem interactions must be mocked.
- Default mode is dry-run; no destructive operations unless `--apply` is
  specified.

## Next steps

- Finish core modules and add more unit tests for edge cases.
