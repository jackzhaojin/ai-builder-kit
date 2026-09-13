#!/usr/bin/env python3
"""
Clean up Excalidraw files by removing elements with isDeleted: true
This helps reduce file size and improve performance.
"""
import json
import sys
from pathlib import Path


def cleanup_excalidraw(file_path):
    """
    Remove deleted elements from an Excalidraw JSON file.

    Args:
        file_path: Path to the .excalidraw file
    """
    file_path = Path(file_path)

    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    # Read the JSON file
    print(f"Reading {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Count elements before cleanup
    original_count = len(data.get('elements', []))

    # Filter out deleted elements
    if 'elements' in data:
        data['elements'] = [
            element for element in data['elements']
            if not element.get('isDeleted', False)
        ]

    # Count elements after cleanup
    cleaned_count = len(data.get('elements', []))
    removed_count = original_count - cleaned_count

    # Write back to file with proper formatting
    print(f"Writing cleaned data back to {file_path}...")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Print summary
    print(f"\n✓ Cleanup complete!")
    print(f"  Original elements: {original_count}")
    print(f"  Removed (isDeleted=true): {removed_count}")
    print(f"  Remaining elements: {cleaned_count}")

    # Show file size reduction
    file_size_mb = file_path.stat().st_size / (1024 * 1024)
    print(f"  New file size: {file_size_mb:.2f} MB")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python cleanup_excalidraw.py <path-to-excalidraw-file>")
        sys.exit(1)

    cleanup_excalidraw(sys.argv[1])
