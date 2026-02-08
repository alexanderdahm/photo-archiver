# Media Archiver

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

1. Create a virtual environment

```powershell
python -m venv .venv
```

2. Activate it

```powershell
del
```

3. Install the project (including CLI)

```powershell
pip install -e .
```

Optional dev dependencies (tests, tooling):

```powershell
pip install -e .[dev]
```

## Build Executable (PyInstaller)

Build a single-file Windows executable using the dedicated `.venv-build` environment:

1. Create and activate the build venv

```powershell
python -m venv .venv-build
.venv-build\Scripts\activate
```

2. Install build dependencies

```powershell
pip install -e .
pip install pyinstaller
```

3. Build the executable

```powershell
pyinstaller --onefile --name media-archiver --console bootstrap_media_archiver.py
```

The executable is written to:

- `dist/media-archiver.exe`

For running the executable without `--config`, place `config.yaml` next to the
EXE or in the current working directory.

## Usage

After installing the project, the CLI is available as `media-archiver`.

### Dry-Run (default, recommended)

```powershell
media-archiver --config config.yaml
```

This will scan, analyze, and report all actions without modifying any files.

### Apply changes

```powershell
media-archiver --config config.yaml --apply
```

Changes are only applied if:

- `--apply` is provided AND
- `behavior.dry_run` is set to `false` in the config

---

## 🧠 Entwickler-Hinweis (sehr empfohlen)

### Development Usage

During development, the CLI can also be invoked via:

```powershell
python -m media_archiver.cli --config config.yaml
```

Both commands execute the same code path.

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

## Sorting Logic (How files are placed)

The tool processes files through a deterministic pipeline and applies the same
decisions for dry-run and apply runs. In short:

1. Scan supported files from the configured `unsorted` folder.
2. Resolve the capture datetime in this order:
   - EXIF DateTimeOriginal
   - Datetime parsed from filename
   - Filesystem modified timestamp (fallback)
3. Normalize the month folder name to the canonical German format.
4. Generate the canonical filename:
   `YYYY-MM-DD_HH-mm-ss.ext`
5. Build the target path as:
   `<archive_root>/<YYYY>/<MM_MonthName>/<canonical_filename>`
6. Handle collisions deterministically by appending `_01`, `_02`, ...
7. Execute copy/move only when `--apply` is used and `behavior.dry_run` is false.

Dry-run runs the same logic but never writes files; it only generates reports.

## Project Structure

- [ARCHITECTURE.md](ARCHITECTURE.md) — normative architecture rules
- [PLAN.md](PLAN.md) — strict development order
- [CONTRIBUTING.md](CONTRIBUTING.md) — contribution and safety rules
- [tests](tests) — unit tests and fixtures
- [src/media_archiver](src/media_archiver) — implementation

These documents are binding.

## Development Rules (Important)

- Follow [ARCHITECTURE.md](ARCHITECTURE.md) strictly
- Follow the order in [PLAN.md](PLAN.md)
- No filesystem writes outside approved phases
- All logic must be unit-tested
- All behavior must be deterministic

## License

Private / internal use
