#!/usr/bin/env python3
"""
Main script for markdown-file-magic.

A CLI utility to combine or flatten Markdown files from directory structures
"""

import os
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent / "utils"))

def main():
    """Main processing function."""
    print("🚀 Starting markdown-file-magic")
    
    # Your code here
    print("✅ Processing complete!")
    
    # Example: Read from input, process, save to output
    # input_file = Path(__file__).parent.parent / "input" / "data.csv"
    # output_file = Path(__file__).parent.parent / "output" / "results.csv"
    
if __name__ == "__main__":
    main()
