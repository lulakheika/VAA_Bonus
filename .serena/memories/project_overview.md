# VAA Bonus Project Overview

## Project Purpose
This repository contains bonus materials from a VAA workshop on Claude Code and RAG systems. The main purpose is to provide two complete tools as bonus content:

1. **Claude Conversation Parser V2** - Converts Claude Code JSONL transcripts to human-readable markdown
2. **Claude Code Status Line** - Real-time status display for Claude Code sessions

## Project Context
The parser component comes from a larger project in development called **ChatTokener**, which is a comprehensive suite for managing AI conversations. The current repository serves to deliver the promised bonus materials while introducing ChatTokener as a future project.

## Repository Structure
```
/
├── Chat_Tokener_Overview.md          # Overview of the larger ChatTokener project
├── Bonus_Code/                       # Main bonus content directory
│   ├── Parser/                       # Claude conversation parser
│   │   ├── claude_parser_v2.py       # Main parser script
│   │   └── PARSER_GUIDE.md           # Complete installation and usage guide
│   ├── Status_Line/                  # Claude Code status line
│   │   ├── main_status_line.py       # Status line implementation
│   │   └── Status_Line_Research_ENG.md # Research and implementation details
│   └── Custom_Slash_Commands_Guide.md # Guide for creating Claude Code custom commands
```

## Key Features
- Parser converts JSONL to SpecStory-compatible markdown
- Status line provides real-time metrics (tokens, cost, performance)
- Both tools are fully documented and ready to use
- Complete guides included for installation and usage