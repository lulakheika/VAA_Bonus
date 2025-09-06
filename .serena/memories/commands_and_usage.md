# Commands and Usage

## Parser Commands

### Basic Usage
```bash
# Convert single file
python claude_parser_v2.py /path/to/conversation.jsonl

# Process directory
python claude_parser_v2.py ~/.claude/projects/project-name/

# Custom output directory
python claude_parser_v2.py input.jsonl -o /custom/output/path/

# Change base folder detection
python claude_parser_v2.py input.jsonl -b JavaScript
```

### Command Line Arguments
- `input_path` - Required: Path to JSONL file or directory
- `-o, --output` - Optional: Custom output directory (default: `.specstory/history/`)
- `-b, --base-folder` - Optional: Base folder for project detection (default: `Python`)

## Status Line Commands

### Basic Usage
```bash
# Run status line (typically integrated with shell prompt)
python main_status_line.py
```

## Configuration Files

### Parser Configuration
- `json_name_match.txt` - Maps UUIDs to human-readable conversation names
- Format: `uuid=Conversation Name`

### Status Line Configuration
- Reads Claude Code transcript files automatically
- Detects project context from file system
- No additional configuration required

## File Locations

### Claude Code Files
- Conversations: `~/.claude/projects/project-name/`
- Format: JSONL files with UUID names

### Output Locations
- Default: `.specstory/history/` in project directory
- Custom: Specified via `-o` flag
- Fallback: `output/` directory