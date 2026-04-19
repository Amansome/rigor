"""CLI entry point for the rigor command."""

import typer

app = typer.Typer()

# TODO: Add CLI commands for running eval configs (section 4/8 of SPEC.md):
#   - `rigor run <config.yaml>` — load YAML config, create a run per model, kick off runner
#   - `rigor runs list` — pretty-print recent runs and their statuses
#   - `rigor runs show <run_id>` — show run detail and per-example results
