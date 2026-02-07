# Photo Archive Tool

Deterministic, offline-only tooling to organize photo and video archives by
capture date on Windows. The project emphasizes safety, auditability, and
reproducibility and follows a strict, phase-based architecture.

## What This Tool Does

- Normalizes inconsistent year/month folder structures
- Renames photos and videos based on capture datetime
- Sorts unsorted files into the correct archive location
- Supports images and videos
- Runs in dry-run mode by default
- Generates detailed audit reports (Markdown + JSON)

## What This Tool Does NOT Do

- It never deletes files
- It never overwrites files
- It never uploads data
- It never accesses the network
- It never modifies files unless explicitly instructed

## Safety Model

- Dry-run is the default execution mode
- All filesystem modifications require explicit confirmation
- All decisions are logged and reproducible
- Re-running the tool is safe (idempotent behavior)

## Supported File Types

- Images: `.jpg`, `.jpeg`, `.png`, `.heic`
- Videos: `.mp4`, `.mov`, `.avi`

Unsupported files are ignored and reported.

## Requirements

- Windows
- Python 3.11 or newer
- No external services required

## Development Setup (Recommended)

This project uses a local virtual environment.

1) Create a virtual environment

```powershell
python -m venv .venv
```

2) Activate it

```powershell
.venv\Scripts\activate
```

3) Install dependencies

```powershell
pip install -e .[dev]
```

## Usage

Dry-run (default):

```powershell
photo-tool run --config config.yaml
```

Apply changes:

```powershell
photo-tool run --config config.yaml --apply
```

## Configuration

All behavior is controlled via a YAML configuration file. See the example:

- [config.example.yaml](config.example.yaml)

## Reports

Each run generates:

- Markdown report (human-readable)
- JSON report (machine-readable)

Reports include:

- Summary
- Folder normalization actions
- File renames
- File moves or copies
- Warnings
- Errors

Reports are timestamped and append-only.

## Project Structure

- [ARCHITECTURE.md](ARCHITECTURE.md) — normative architecture rules
- [PLAN.md](PLAN.md) — strict development order
- [CONTRIBUTING.md](CONTRIBUTING.md) — contribution and safety rules
- [tests](tests) — unit tests and fixtures
- [src/photo_tool](src/photo_tool) — implementation

These documents are binding.

## Development Rules (Important)

- Follow [ARCHITECTURE.md](ARCHITECTURE.md) strictly
- Follow the order in [PLAN.md](PLAN.md)
- No filesystem writes outside approved phases
- All logic must be unit-tested
- All behavior must be deterministic

## License

Private / internal use
