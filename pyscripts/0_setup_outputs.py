#!/usr/bin/env python
# coding: utf-8

"""
Creates a default data folder layout for BrainSec inference.

This script is meant for users who do not want to provide custom paths.
It creates the expected input/output directories under ./data so the
preprocessing and inference scripts can run with their defaults.
"""

import os
from pathlib import Path


def ensure_dir(path: Path) -> None:
    """Create a directory (and parents) if it doesn't already exist."""
    # Using exist_ok=True makes this safe to run multiple times.
    path.mkdir(parents=True, exist_ok=True)


def main() -> None:
    # Base data directory used by pyscripts defaults.
    data_root = Path("data")

    # Input directory for raw WSI files (.svs).
    wsi_dir = data_root / "wsi"

    # Output directory for normalized tiles.
    norm_tiles_dir = data_root / "norm_tiles"

    # Output directories for inference results.
    heatmaps_dir = data_root / "outputs" / "heatmaps"
    brainseg_images_dir = data_root / "brainseg" / "images"
    brainseg_numpy_dir = data_root / "brainseg" / "numpy"

    # Create all required directories.
    for directory in [
        wsi_dir,
        norm_tiles_dir,
        heatmaps_dir,
        brainseg_images_dir,
        brainseg_numpy_dir,
    ]:
        ensure_dir(directory)

    # Summarize the created folder structure for the user.
    print("Created/verified default BrainSec data folders:")
    print(f"- WSI input: {wsi_dir}")
    print(f"- Tiled output: {norm_tiles_dir}")
    print(f"- Plaque heatmaps: {heatmaps_dir}")
    print(f"- BrainSeg images: {brainseg_images_dir}")
    print(f"- BrainSeg numpy: {brainseg_numpy_dir}")


if __name__ == "__main__":
    # Entrypoint for running the script directly.
    main()
