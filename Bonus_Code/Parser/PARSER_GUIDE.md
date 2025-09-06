# Claude Conversation Parser V2 - Complete Guide

## Introduction: Bridging Cursor and Claude Code

This parser was born from the need to maintain consistency between two powerful AI coding assistants: Cursor (with its SpecStory extension) and Claude Code. 

### The SpecStory Connection

SpecStory is a popular Cursor extension that automatically captures conversations from Cursor's internal databases and transforms them into markdown files stored in the `.specstory/history` directory. When transitioning from Cursor to Claude Code, maintaining compatibility with existing workflows becomes crucial.

### Why This Parser Exists

When switching from Cursor to Claude Code, the SpecStory extension no longer applies - Claude Code stores its conversations in a different format (JSONL) and location. This parser bridges that gap by:

- **Maintaining Format Compatibility**: Generates markdown files with identical syntax and structure to SpecStory output
- **Preserving Directory Structure**: Uses the same `.specstory/history` folder as the default output location
- **Enabling Seamless Switching**: Whether you use Cursor with SpecStory or Claude Code with this parser, all conversation histories end up in the same location with the same format

This design choice allows developers to switch seamlessly between Cursor and Claude Code without losing conversation history continuity or needing to adapt their workflows.

## Beyond Command Line: Automated Monitoring

While this parser provides powerful command-line functionality, it's designed to be part of a larger ecosystem. The ideal setup includes a file monitor that:

- Continuously watches the Claude Code JSON storage directory
- Detects changes in real-time (triggered with each new message in a conversation)
- Automatically runs the parser to update markdown files
- Maintains up-to-date conversation history without manual intervention

### Part of the ChatTokener Suite

This parser is a core component of **ChatTokener**, a comprehensive suite of tools for managing AI assistant conversations currently in development. ChatTokener will provide:

- Automated conversation monitoring and parsing
- Token usage analytics
- Conversation management utilities
- Cross-platform compatibility

For more information about ChatTokener, contact: **vibecoding@pcok.it**

## Overview

Claude Conversation Parser V2 is a sophisticated Python tool designed to convert Claude Code conversation files (JSONL format) into readable, well-structured Markdown documents. The parser handles complex conversation structures, filters out unnecessary content, and generates SpecStory-compatible output for perfect integration with existing Cursor/SpecStory workflows.

## Key Features

### 1. Intelligent JSONL Processing
- Reads JSON Lines format files containing Claude Code conversations
- Robust error handling for malformed JSON entries
- Line-by-line processing for memory efficiency
- Automatic detection of conversation metadata

### 2. Custom Name Mapping System
The parser supports a powerful name mapping feature through `json_name_match.txt` files:
- Maps UUID-based filenames to human-readable conversation names
- Automatically searches for mapping files in the same directory as JSONL files
- Format: `uuid=Conversation Name`
- Handles spaces, underscores, and special characters gracefully

### 3. Smart Filename Generation
The parser generates filenames following the SpecStory convention:
- Format: `YYYY-MM-DD_HH-MM-conversation-name.md`
- Uses file creation date as primary timestamp source
- Falls back to message timestamps if file metadata unavailable
- Automatically sanitizes names for filesystem compatibility

### 4. Advanced Content Filtering

#### Exit Turn Detection
Automatically filters out exit commands and cleanup patterns:
- Removes `<command-name>exit</command-name>` patterns
- Filters `<local-command-stdout>(no content)</local-command-stdout>`
- Cleans up conversation endings

#### Empty Turn Removal
Intelligently removes turns containing only:
- Tool references without actual content
- JSON metadata
- Empty user prompts with tool-only assistant responses

#### Fake Turn Cleaning
Two-pass cleaning system:
1. First pass: Groups messages into logical turns
2. Second pass: Removes fake turns (empty User → empty Assistant patterns)

### 5. Tool Use Formatting
Special formatting for common Claude Code tools:
- **Read**: `Read file: /path/to/file`
- **Write/Edit**: `Write file: /path/to/file`
- **LS**: Collapsible directory listings in `<details>` tags
- **Other tools**: Formatted JSON representation

### 6. Project Path Intelligence
Automatically determines project location through multiple methods:
- Extracts from `cwd` field in JSON messages
- Decodes `.claude/projects/` directory names
- Handles encoded paths (e.g., `-Users-name-project` → `/Users/name/project`)
- Configurable base folder detection (default: "Python")

### 7. Flexible Output Management
Multiple output strategies:
- Auto-creation of `.specstory/history/` in project directory
- Custom output directory via `-o` flag
- Fallback to `output/` directory when project path unavailable
- Preserves project structure and organization

## Installation & Requirements

### Prerequisites
- Python 3.6 or higher
- No external dependencies (uses only Python standard library)
- Read access to Claude Code conversation files
- Write access to output directories

### File Structure
```
Claude_Conversation_Parser/
├── New_GUI/
│   ├── claude_parser_v2.py     # Main parser script
│   ├── json_name_match.txt     # Name mappings (optional)
│   └── DOCs/
│       └── PARSER_GUIDE.md     # This guide
```

## Usage

### Basic Commands

#### Convert a Single File
```bash
python claude_parser_v2.py /path/to/conversation.jsonl
```

#### Process All Files in Directory
```bash
python claude_parser_v2.py ~/.claude/projects/project-name/
```

#### Specify Custom Output Directory
```bash
python claude_parser_v2.py input.jsonl -o /custom/output/path/
```

#### Change Base Folder Detection
```bash
python claude_parser_v2.py input.jsonl -b JavaScript
```

### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `input_path` | Path to JSONL file or directory | Required |
| `-o, --output` | Custom output directory | `.specstory/history/` in project |
| `-b, --base-folder` | Base folder for project detection | `Python` |

## Name Mapping Configuration

Create a `json_name_match.txt` file in the same directory as your JSONL files:

```text
550e8400-e29b-41d4-a716-446655440000=OAuth Implementation Discussion
660e8400-e29b-41d4-a716-446655440001=Database Schema Design
770e8400-e29b-41d4-a716-446655440002=API Endpoint Planning
```

The parser will automatically use these names instead of generic project names.

## Output Format

### SpecStory-Compatible Markdown
```markdown
<!-- Generated by SpecStory -->

Source: 550e8400-e29b-41d4-a716-446655440000.jsonl

# Project_Name (2024-01-15 10:30:00)

_**User**_

User's message content here...

---

_**Assistant**_

Assistant's response content here...

---
```

### Turn Structure
Each conversation turn consists of:
1. User prompt (with `_**User**_` header)
2. Separator (`---`)
3. Assistant response (with `_**Assistant**_` header)
4. Tool results (if applicable)
5. Final separator

## Advanced Features

### Multi-Pass Cleaning Algorithm
The parser uses a sophisticated two-pass cleaning system:

1. **First Pass**: Groups messages into logical turns
   - Combines user messages with corresponding assistant responses
   - Attaches tool results to appropriate turns
   - Handles multiple assistant messages per turn

2. **Second Pass**: Removes fake/empty turns
   - Identifies patterns of empty user → empty assistant
   - Filters tool-only references without content
   - Preserves meaningful conversation flow

### Timestamp Priority System
1. File creation date (`st_birthtime` on macOS)
2. File change time (`st_ctime` as fallback)
3. First message timestamp from JSON
4. Current date/time (last resort)

### Project Path Resolution
The parser attempts multiple strategies to find the project path:
1. Decode from `.claude/projects/` folder name
2. Extract from `cwd` field in first message
3. Use user-specified output directory
4. Fall back to default `output/` directory

## Troubleshooting

### Common Issues

#### No Output Generated
- **Cause**: Empty or malformed JSONL file
- **Solution**: Verify file contains valid JSON Lines format
- **Debug**: Check console output for parsing errors

#### Wrong Project Path Detected
- **Cause**: Encoded path doesn't match actual project location
- **Solution**: Use `-o` flag to specify output directory manually
- **Alternative**: Ensure base folder name matches your project structure

#### Missing Conversations in Output
- **Cause**: Aggressive filtering removing valid content
- **Solution**: Check if conversations contain only tool uses
- **Workaround**: Review filtering patterns in code if needed

#### Filename Conflicts
- **Cause**: Multiple conversations at same timestamp
- **Solution**: Parser auto-increments counter (_1, _2, etc.)
- **Alternative**: Use name mapping file for unique names

### Debug Mode
The parser provides detailed console output:
- File processing status
- Path detection attempts
- Turn count before/after cleaning
- Mapping file detection
- Output file locations

### Performance Considerations
- **Large Files**: Parser processes line-by-line for memory efficiency
- **Batch Processing**: Processes all JSONL files in directory sequentially
- **Cleaning Passes**: Two-pass system may take longer for very large conversations

## Best Practices

### Organizing Conversations
1. Keep related JSONL files in same directory
2. Use meaningful names in `json_name_match.txt`
3. Maintain consistent base folder structure
4. Regular cleanup of old conversations

### Name Mapping Tips
- Use descriptive names that indicate conversation purpose
- Include dates in names for chronological sorting
- Avoid special characters that might cause filesystem issues
- Keep mapping file updated as new conversations are added

### Output Management
- Let parser auto-detect project paths when possible
- Use `.specstory/history/` structure for SpecStory compatibility
- Create separate output directories for different projects
- Regular backups of important conversations

## Integration with SpecStory

The parser generates SpecStory-compatible markdown with:
- Proper header comments
- Source file tracking
- Consistent formatting
- Turn-based structure
- Metadata preservation

This allows seamless integration with SpecStory workflows and tools.

## Version History

### V2 Features
- Enhanced turn filtering algorithm
- Two-pass cleaning system
- Improved project path detection
- Better handling of tool results
- SpecStory compatibility
- Name mapping support

### Future Enhancements
- Configuration file support
- Custom filtering rules
- Export to additional formats
- Conversation merging capabilities
- Statistical analysis features

## Support & Contribution

For issues, questions, or contributions:
- Review the source code in `claude_parser_v2.py`
- Check existing patterns in filtering logic
- Test with sample JSONL files
- Maintain backward compatibility

## License

This parser is part of the Claude Conversation Parser project and follows the project's licensing terms.

---

**Author**: Russo Davide (The DaveEloper)  
**Contact**: vibecoding@pcok.it  
**Project**: ChatTokener Suite - Claude Conversation Parser V2