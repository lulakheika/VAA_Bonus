# Development Workflow

## Code Style and Conventions

### Python Code Style
- Standard Python conventions (PEP 8)
- Clear function and variable names
- Comprehensive docstrings for complex functions
- Type hints where applicable
- Error handling with try-catch blocks

### File Organization
- Self-contained modules with clear responsibilities
- Separate configuration from implementation
- Comprehensive documentation files alongside code

## Testing and Validation

### Parser Testing
- Test with various JSONL file formats
- Verify output markdown structure
- Check handling of malformed JSON
- Test directory processing
- Validate name mapping functionality

### Status Line Testing  
- Test transcript parsing
- Verify token calculations
- Check Git integration
- Test cross-platform compatibility

## Development Commands

### Code Quality
```bash
# Code formatting (if using)
python -m black *.py

# Linting (if configured)
python -m flake8 *.py

# Type checking (if using mypy)
python -m mypy *.py
```

### Testing
```bash
# Test parser with sample files
python claude_parser_v2.py sample.jsonl -o test_output/

# Test status line functionality
python main_status_line.py
```

## When Task is Completed

1. **Test functionality** - Run both tools with sample data
2. **Check documentation** - Ensure guides are accurate and complete  
3. **Verify compatibility** - Test on different systems if possible
4. **Update README** - Reflect any changes in main documentation

## Project Maintenance

### Regular Tasks
- Update documentation as features evolve
- Test compatibility with new Claude Code versions
- Monitor for changes in JSONL format
- Keep ChatTokener references current

### Version Control
- Maintain clean commit history
- Use descriptive commit messages
- Tag releases appropriately
- Keep main branch stable