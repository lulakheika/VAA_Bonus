# Suggested Commands for Development

## Essential Commands

### Testing the Parser
```bash
# Test parser with single file
python Bonus_Code/Parser/claude_parser_v2.py sample.jsonl

# Test parser with directory
python Bonus_Code/Parser/claude_parser_v2.py ~/.claude/projects/project-name/

# Test with custom output
python Bonus_Code/Parser/claude_parser_v2.py sample.jsonl -o test_output/
```

### Testing the Status Line
```bash
# Run status line
python Bonus_Code/Status_Line/main_status_line.py

# Test with specific transcript (if supported)
python Bonus_Code/Status_Line/main_status_line.py transcript.jsonl
```

### File Management
```bash
# List project structure
ls -la
tree  # if available

# Find JSONL files
find . -name "*.jsonl" -type f

# Check Python version
python --version
python3 --version
```

### Documentation
```bash
# Read parser guide
cat Bonus_Code/Parser/PARSER_GUIDE.md

# Read status line research
cat Bonus_Code/Status_Line/Status_Line_Research_ENG.md

# Read project overview
cat Chat_Tokener_Overview.md
```

### Development Utilities
```bash
# Check code structure
wc -l Bonus_Code/Parser/claude_parser_v2.py
wc -l Bonus_Code/Status_Line/main_status_line.py

# Search for specific patterns
grep -r "def " Bonus_Code/
grep -r "class " Bonus_Code/
```

### Git Operations
```bash
# Check repository status
git status
git log --oneline -10
git branch

# Standard workflow
git add .
git commit -m "Description"
git push
```

## Utility Commands (Darwin/macOS)

### System Information
```bash
# System version
sw_vers

# Python installations
which python
which python3
ls -la /usr/bin/python*
```

### File Operations
```bash
# Find files by name
find . -name "*.py" -exec ls -la {} \;

# Show file sizes
du -h Bonus_Code/
ls -lah Bonus_Code/*/
```

## Debugging Commands

### Parser Debugging
```bash
# Verbose output (if supported)
python Bonus_Code/Parser/claude_parser_v2.py sample.jsonl --verbose

# Check JSON validity
python -m json.tool sample.jsonl

# Test specific features
head -5 sample.jsonl
tail -5 sample.jsonl
```

### Status Line Debugging
```bash
# Check dependencies
python -c "import json, os, datetime; print('All imports successful')"

# Test specific functions (if main supports it)
python -c "from Bonus_Code.Status_Line.main_status_line import get_git_branch; print(get_git_branch())"
```