# Technology Stack

## Language
- **Python 3.6+** - Primary language for both tools

## Dependencies
- **Parser**: Zero external dependencies (uses only Python standard library)
- **Status Line**: May use standard library or lightweight dependencies

## File Formats
- **Input**: JSONL (JSON Lines) from Claude Code conversations  
- **Output**: Markdown files compatible with SpecStory format
- **Configuration**: Text files (json_name_match.txt for parser)

## Integration Points
- **Claude Code**: Direct integration with conversation storage
- **SpecStory**: Compatible output format for Cursor extension
- **Git**: Status line shows Git branch and repository context
- **File System**: Automatic detection of project paths and structure

## Key Libraries Used
- `json` - JSON parsing
- `os`, `pathlib` - File system operations  
- `datetime` - Timestamp handling
- `argparse` - Command line interface
- `re` - Text processing and filtering

## Compatibility
- Cross-platform (macOS, Linux, Windows)
- No external dependencies required
- Standalone executables