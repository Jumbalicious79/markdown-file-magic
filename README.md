# Markdown File Magic

A CLI utility to combine or flatten Markdown files with intelligent handling of subdirectories and filename collisions.

## 🚀 Quick Start

1. **Place your .md files** in the `input/` directory (including subdirectories)
2. **Choose your mode:**
   - `python main.py combine` - Creates one `combined.md` file in `output/results/`
   - `python main.py flatten` - Copies all files to `output/results/` with unique names

**Note:** README.md files are automatically excluded from processing.

## Features

- 📁 **Recursive directory search** - finds all .md files in subdirectories
- 🔄 **Two operation modes**: combine or flatten
- 🏷️ **Smart collision handling** - generates unique names when files conflict
- 📄 **Safe file reading** - handles multiple text encodings
- ✨ **Clean output formatting** - preserves markdown structure
- 🚫 **README exclusion** - automatically skips README.md files in input

## Usage

### Combine Mode
Concatenates all .md files into one `output/results/combined.md` file:

```bash
python main.py combine
```

**Example output structure:**
```markdown
# Combined Markdown Files
*Generated from 5 files*

## folder1/readme.md
*Source: /path/to/folder1/readme.md*
---
[Original content here]

## folder2/notes.md  
*Source: /path/to/folder2/notes.md*
---
[Original content here]
```

### Flatten Mode
Copies all .md files to `output/results/` directory with unique filenames:

```bash
python main.py flatten
```

**Collision handling:**
- `readme.md` → `readme.md`
- `docs/readme.md` → `docs_readme.md`
- `project/docs/readme.md` → `project_docs_readme.md`
- If still conflicts → `readme_a1b2c3d4.md` (with UUID)

## Project Structure

```
markdown-file-magic/
├── main.py           # CLI utility script
├── input/            # Place your .md files here (README files excluded)
│   ├── docs/
│   ├── notes/
│   └── projects/
└── output/           # Output directory
    ├── results/      # Generated markdown files
    │   ├── combined.md   # (combine mode)
    │   └── *.md          # (flatten mode)  
    └── logs/         # Log files (future use)
```

## Command Line Options

```bash
python main.py --help

# Available subcommands:
python main.py combine    # Combine all files into one
python main.py flatten    # Copy files with unique names
```

## Examples

### Directory Structure Example
```
input/
├── project-a/
│   ├── readme.md
│   └── notes.md
├── project-b/
│   ├── readme.md
│   └── docs/
│       └── api.md
└── standalone.md
```

**After `python main.py flatten`:**
```
output/results/
├── readme.md
├── project-b_readme.md
├── notes.md
├── api.md
└── standalone.md
```

**After `python main.py combine`:**
```
output/results/
└── combined.md  # Contains all files with headers
```

## Features in Detail

### Smart Filename Generation
1. **Try original name** first
2. **Add parent directory** if conflict
3. **Use full path** (sanitized) if still conflict  
4. **Generate UUID** as final fallback

### Encoding Support
Automatically tries multiple encodings:
- UTF-8 (most common)
- UTF-16 (Windows)
- Latin-1 (legacy)
- CP1252 (Windows legacy)

### Error Handling
- Graceful handling of permission errors
- Skips empty or unreadable files
- Provides clear status messages with emojis

## Requirements

- Python 3.7+
- No external dependencies (uses standard library only)

## Use Cases

- **Documentation consolidation** - combine scattered .md files
- **File organization** - flatten complex directory structures  
- **Content preparation** - merge multiple markdown files for publishing
- **Archive processing** - extract markdown from nested folders

---

*Created: 2025-08-08*
