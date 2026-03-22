#!/usr/bin/env python3
"""
markdown-file-magic: A CLI utility to combine or flatten Markdown files

This script provides two main modes:
1. combine - Concatenate all .md files into one combined.md file
2. flatten - Copy all .md files to output/ with unique names
"""

import argparse
import os
import shutil
import uuid
from pathlib import Path
from typing import List, Set
import sys


def print_status(message: str, level: str = "info"):
    """Print status messages with formatting."""
    prefixes = {
        "info": "📄",
        "success": "✅", 
        "warning": "⚠️",
        "error": "❌"
    }
    prefix = prefixes.get(level, "ℹ️")
    print(f"{prefix} {message}")


def ensure_directories() -> tuple[Path, Path, Path]:
    """
    Create input/, output/results/, and output/logs/ directories if they don't exist.
    Returns (input_path, results_path, logs_path).
    """
    script_dir = Path(__file__).parent
    input_dir = script_dir / "input"
    output_dir = script_dir / "output"
    results_dir = output_dir / "results"
    logs_dir = output_dir / "logs"
    
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    results_dir.mkdir(exist_ok=True)
    logs_dir.mkdir(exist_ok=True)
    
    return input_dir, results_dir, logs_dir


def get_md_files(root_dir: Path) -> List[Path]:
    """
    Recursively find all .md files in the given directory, excluding README files.
    
    Args:
        root_dir: Root directory to search
        
    Returns:
        List of Path objects for all .md files found
    """
    if not root_dir.exists():
        print_status(f"Directory does not exist: {root_dir}", "error")
        return []
    
    md_files = []
    excluded_names = {'readme.md', 'README.md', 'Readme.md', 'ReadMe.md'}
    
    try:
        # Use rglob to recursively find all .md files
        for md_file in root_dir.rglob("*.md"):
            if md_file.is_file() and md_file.name not in excluded_names:
                md_files.append(md_file)
        
        # Also search for .MD files (case insensitive)
        for md_file in root_dir.rglob("*.MD"):
            if md_file.is_file() and md_file.name not in excluded_names:
                md_files.append(md_file)
                
    except PermissionError as e:
        print_status(f"Permission denied accessing {root_dir}: {e}", "warning")
    except Exception as e:
        print_status(f"Error searching directory {root_dir}: {e}", "error")
    
    # Sort files for consistent order
    md_files.sort()
    
    return md_files


def read_file_safely(file_path: Path) -> str:
    """
    Safely read a file, handling encoding issues.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        File contents as string, or empty string if read failed
    """
    encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                return content
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print_status(f"Error reading {file_path}: {e}", "warning")
            return ""
    
    print_status(f"Could not decode {file_path} with any encoding, skipping", "warning")
    return ""


def combine_md_files(md_files: List[Path], output_file: Path):
    """
    Combine all markdown files into one file.
    
    Args:
        md_files: List of markdown files to combine
        output_file: Path where combined file should be written
    """
    if not md_files:
        print_status("No markdown files found to combine", "warning")
        return
    
    print_status(f"Combining {len(md_files)} markdown files...")
    
    combined_content = []
    files_processed = 0
    
    # Add header
    combined_content.append("# Combined Markdown Files")
    combined_content.append(f"\n*Generated from {len(md_files)} files*\n")
    combined_content.append("---\n")
    
    for md_file in md_files:
        try:
            content = read_file_safely(md_file)
            
            if not content.strip():
                print_status(f"Skipping empty file: {md_file.name}", "warning")
                continue
            
            # Add file header
            relative_path = md_file.relative_to(md_file.parents[len(md_file.parents)-2])
            combined_content.append(f"\n## {relative_path}\n")
            combined_content.append(f"*Source: {md_file}*\n")
            combined_content.append("---\n")
            
            # Add the file content
            combined_content.append(content)
            combined_content.append("\n\n---\n")  # Separator between files
            
            files_processed += 1
            print_status(f"Added: {md_file.name}")
            
        except Exception as e:
            print_status(f"Failed to process {md_file}: {e}", "error")
    
    if files_processed == 0:
        print_status("No files could be processed", "error")
        return
    
    # Write combined file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(combined_content))
        
        print_status(f"Successfully combined {files_processed} files into {output_file}", "success")
        print_status(f"Output size: {output_file.stat().st_size} bytes")
        
    except Exception as e:
        print_status(f"Failed to write combined file: {e}", "error")


def generate_unique_filename(original_path: Path, output_dir: Path, used_names: Set[str]) -> str:
    """
    Generate a unique filename, handling collisions.
    
    Args:
        original_path: Original file path
        output_dir: Output directory
        used_names: Set of already used filenames
        
    Returns:
        Unique filename string
    """
    base_name = original_path.stem
    extension = original_path.suffix
    
    # First try the original name
    candidate = f"{base_name}{extension}"
    if candidate not in used_names:
        used_names.add(candidate)
        return candidate
    
    # Try adding parent directory name
    parent_name = original_path.parent.name
    if parent_name != "." and parent_name:
        candidate = f"{parent_name}_{base_name}{extension}"
        if candidate not in used_names:
            used_names.add(candidate)
            return candidate
    
    # Try adding full relative path (replacing separators)
    try:
        # Get relative path from input directory
        rel_path = str(original_path.relative_to(original_path.parents[len(original_path.parents)-2]))
        safe_path = rel_path.replace(os.sep, "_").replace("/", "_")
        candidate = safe_path
        if candidate not in used_names:
            used_names.add(candidate)
            return candidate
    except (ValueError, IndexError):
        pass
    
    # Fall back to UUID
    unique_id = str(uuid.uuid4())[:8]
    candidate = f"{base_name}_{unique_id}{extension}"
    used_names.add(candidate)
    return candidate


def copy_md_files(md_files: List[Path], output_dir: Path):
    """
    Copy all markdown files to output directory with unique names.
    
    Args:
        md_files: List of markdown files to copy
        output_dir: Output directory
    """
    if not md_files:
        print_status("No markdown files found to copy", "warning")
        return
    
    print_status(f"Flattening {len(md_files)} markdown files to {output_dir}")
    
    used_names: Set[str] = set()
    files_copied = 0
    
    for md_file in md_files:
        try:
            # Generate unique filename
            unique_name = generate_unique_filename(md_file, output_dir, used_names)
            output_path = output_dir / unique_name
            
            # Copy the file
            shutil.copy2(md_file, output_path)
            
            print_status(f"Copied: {md_file.name} → {unique_name}")
            files_copied += 1
            
        except Exception as e:
            print_status(f"Failed to copy {md_file}: {e}", "error")
    
    if files_copied > 0:
        print_status(f"Successfully flattened {files_copied} files to {output_dir}", "success")
    else:
        print_status("No files were copied", "error")


def combine_mode(input_dir: Path, results_dir: Path):
    """Execute combine mode."""
    print_status("🔄 Running in COMBINE mode")
    print_status(f"Searching for markdown files in: {input_dir}")
    
    md_files = get_md_files(input_dir)
    
    if not md_files:
        print_status(f"No .md files found in {input_dir}", "warning")
        print_status("Place some .md files in the input/ directory first (README files are excluded)")
        return
    
    print_status(f"Found {len(md_files)} markdown files:")
    for f in md_files:
        print(f"  • {f.relative_to(input_dir)}")
    
    output_file = results_dir / "combined.md"
    combine_md_files(md_files, output_file)


def flatten_mode(input_dir: Path, results_dir: Path):
    """Execute flatten mode."""
    print_status("📁 Running in FLATTEN mode")
    print_status(f"Searching for markdown files in: {input_dir}")
    
    md_files = get_md_files(input_dir)
    
    if not md_files:
        print_status(f"No .md files found in {input_dir}", "warning")
        print_status("Place some .md files in the input/ directory first (README files are excluded)")
        return
    
    print_status(f"Found {len(md_files)} markdown files:")
    for f in md_files:
        print(f"  • {f.relative_to(input_dir)}")
    
    copy_md_files(md_files, results_dir)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="markdown-file-magic: Combine or flatten Markdown files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py combine    # Combine all .md files into combined.md
  python main.py flatten    # Copy all .md files to output/ with unique names
  
The script will search input/ directory and all subdirectories for .md files.
        """
    )
    
    subparsers = parser.add_subparsers(
        dest='mode', 
        help='Operation mode',
        required=True
    )
    
    # Combine subcommand
    combine_parser = subparsers.add_parser(
        'combine',
        help='Combine all .md files into one combined.md file'
    )
    combine_parser.add_argument('--input', '-i', help='Input directory (default: input/)')
    combine_parser.add_argument('--output', '-o', help='Output file path (default: output/results/combined.md)')

    # Flatten subcommand
    flatten_parser = subparsers.add_parser(
        'flatten',
        help='Copy all .md files to output/ with unique names'
    )
    flatten_parser.add_argument('--input', '-i', help='Input directory (default: input/)')
    flatten_parser.add_argument('--output', '-o', help='Output directory (default: output/results/)')
    
    args = parser.parse_args()
    
    # Use custom paths if provided, otherwise fall back to default directories
    custom_input = getattr(args, 'input', None)
    custom_output = getattr(args, 'output', None)

    if custom_input:
        input_dir = Path(custom_input).resolve()
        if not input_dir.is_dir():
            print_status(f"Input directory does not exist: {input_dir}", "error")
            sys.exit(1)
    else:
        input_dir = None

    if custom_output:
        output_target = Path(custom_output).resolve()
    else:
        output_target = None

    # Ensure default directories exist (always needed as fallback)
    try:
        default_input, default_results, logs_dir = ensure_directories()
    except Exception as e:
        print_status(f"Failed to create directories: {e}", "error")
        sys.exit(1)

    if input_dir is None:
        input_dir = default_input

    print_status(f"markdown-file-magic starting...")
    print_status(f"Input directory: {input_dir}")
    if output_target:
        print_status(f"Output: {output_target}")
    else:
        print_status(f"Results directory: {default_results}")
    print("")

    try:
        if args.mode == 'combine':
            results_dir = output_target.parent if output_target else default_results
            results_dir.mkdir(parents=True, exist_ok=True)
            if output_target:
                # Use custom output file path
                md_files = get_md_files(input_dir)
                if md_files:
                    print_status(f"🔄 Running in COMBINE mode")
                    print_status(f"Found {len(md_files)} markdown files:")
                    for f in md_files:
                        try:
                            print(f"  • {f.relative_to(input_dir)}")
                        except ValueError:
                            print(f"  • {f.name}")
                    combine_md_files(md_files, output_target)
                else:
                    print_status(f"No .md files found in {input_dir}", "warning")
            else:
                combine_mode(input_dir, default_results)
        elif args.mode == 'flatten':
            out_dir = output_target if output_target else default_results
            out_dir.mkdir(parents=True, exist_ok=True)
            if custom_input or custom_output:
                md_files = get_md_files(input_dir)
                if md_files:
                    print_status(f"📁 Running in FLATTEN mode")
                    print_status(f"Found {len(md_files)} markdown files:")
                    for f in md_files:
                        try:
                            print(f"  • {f.relative_to(input_dir)}")
                        except ValueError:
                            print(f"  • {f.name}")
                    copy_md_files(md_files, out_dir)
                else:
                    print_status(f"No .md files found in {input_dir}", "warning")
            else:
                flatten_mode(input_dir, default_results)
    except KeyboardInterrupt:
        print_status("Operation cancelled by user", "warning")
        sys.exit(1)
    except Exception as e:
        print_status(f"Unexpected error: {e}", "error")
        sys.exit(1)
    
    print("")
    print_status("Operation completed! 🎉")


if __name__ == "__main__":
    main()