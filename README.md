# Photo Archive Tool

A safe, deterministic photo and video organizer for Windows.

## Features

- Normalize year/month folder structures
- Rename files based on capture datetime
- Automatically sort unsorted photos
- Dry-run mode (default)
- Detailed audit reports

## Usage

```bash
photo-tool scan --config config.yaml
photo-tool apply --config config.yaml
Safety
No files are modified unless --apply is provided

No files are deleted

All actions are logged