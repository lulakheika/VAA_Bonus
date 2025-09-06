# Claude Code Custom Slash Commands: Complete Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Basic Structure](#basic-structure)
3. [Single Arguments](#single-arguments)
4. [Multiple Arguments (Advanced)](#multiple-arguments-advanced)
5. [Configuration Options](#configuration-options)
6. [Practical Examples](#practical-examples)
7. [Best Practices](#best-practices)

## Introduction

Custom slash commands in Claude Code allow you to create reusable prompts and workflows that can be invoked with simple commands. These commands can accept arguments, making them dynamic and flexible for various use cases.

## Basic Structure

### File Location
Custom slash commands are Markdown files stored in:
- **Project-specific commands**: `.claude/commands/` (within your project directory)
- **Personal commands**: `~/.claude/commands/` (in your home directory)

### Basic Command Format
```markdown
---
description: Brief description of what the command does
argument-hint: usage hint for arguments
---

Your prompt text here
```

### Naming Convention
- The command name is derived from the filename
- Example: `fix-bug.md` becomes `/fix-bug`
- Supports subdirectories for namespacing: `review/code.md` becomes `/review/code`

## Single Arguments

### Using $ARGUMENTS (Global Capture)

The `$ARGUMENTS` variable captures all provided arguments as a single string.

#### Example: Simple Bug Fix Command
**File**: `.claude/commands/fix-bug.md`
```markdown
---
description: Fix a bug with proper documentation
argument-hint: <bug-description>
---

Please fix the following bug: $ARGUMENTS

Ensure you:
- Identify the root cause
- Apply the fix
- Add tests if needed
- Update documentation
```

**Usage**:
```
/fix-bug user authentication fails when password contains special characters
```

The entire string "user authentication fails when password contains special characters" is captured in `$ARGUMENTS`.

## Multiple Arguments (Advanced)

### Positional Arguments ($1, $2, $3, ...)

For structured commands requiring multiple distinct parameters, use positional arguments.

#### Example 1: Code Review Command
**File**: `.claude/commands/review-pr.md`
```markdown
---
description: Review a pull request with specific focus areas
argument-hint: <pr-number> <priority> <reviewer>
---

Review pull request #$1 with $2 priority.

Focus areas:
- Code quality and standards
- Performance implications
- Security considerations

Assign review to: $3

${4:-No additional notes provided}
```

**Usage**:
```
/review-pr 456 high alice "Check for SQL injection vulnerabilities"
```

- `$1` = "456" (PR number)
- `$2` = "high" (priority)
- `$3` = "alice" (reviewer)
- `$4` = "Check for SQL injection vulnerabilities" (additional notes)

#### Example 2: Database Migration Command
**File**: `.claude/commands/db-migrate.md`
```markdown
---
description: Create and run database migration
argument-hint: <action> <table-name> [columns...]
allowed-tools: Read, Write, Bash
---

Database Migration Request:
- Action: $1
- Table: $2
- Additional parameters: ${@:3}

!echo "Generating migration for $1 on table $2"

Create a migration that will $1 the $2 table.
${3:+Columns/Fields involved: ${@:3}}

Follow our migration standards:
- Include rollback procedures
- Add appropriate indexes
- Consider data integrity
```

**Usage Examples**:
```
/db-migrate create users "id:uuid name:string email:string created_at:timestamp"
/db-migrate alter products "add column price:decimal"
/db-migrate drop temp_data
```

#### Example 3: API Endpoint Generator
**File**: `.claude/commands/create-endpoint.md`
```markdown
---
description: Generate a complete API endpoint
argument-hint: <method> <path> <resource> [auth-required]
model: claude-3-5-sonnet-20241022
---

Generate a $1 endpoint at path $2 for resource $3.

Authentication required: ${4:-false}

Implementation requirements:
- RESTful conventions
- Input validation
- Error handling
- Response formatting
- ${4:+JWT authentication middleware}
- Logging
- Rate limiting

Create the following:
1. Route handler
2. Controller logic
3. Service layer
4. Tests
5. API documentation
```

**Usage**:
```
/create-endpoint POST /api/v1/users User true
/create-endpoint GET /api/v1/products Product
```

### Advanced Argument Patterns

#### Default Values with Parameter Expansion
```markdown
${1:-default_value}  # Use default if $1 is not provided
${2:+text_if_present}  # Include text only if $2 exists
${@:2}  # All arguments from position 2 onwards
```

#### Example 4: Complex Deployment Command
**File**: `.claude/commands/deploy.md`
```markdown
---
description: Deploy application to specified environment
argument-hint: <environment> [version] [--flags]
allowed-tools: Bash, Read, Write
---

Deployment Configuration:
- Target Environment: $1
- Version: ${2:-latest}
- Additional Flags: ${@:3}

!echo "Preparing deployment to $1 environment"

Steps to execute:
1. Validate environment: $1
2. Check version availability: ${2:-latest}
3. ${3:+Apply deployment flags: ${@:3}}
4. Run pre-deployment checks
5. Execute deployment
6. Verify deployment success
7. ${3:+Apply post-deployment configuration based on flags}

Environment-specific considerations for $1:
${1:production:+- Enable monitoring and alerts}
${1:staging:+- Run smoke tests}
${1:development:+- Skip certain validations}
```

**Usage Variations**:
```
/deploy production
/deploy staging v2.3.1
/deploy production v2.3.1 --skip-cache --verbose --notify-slack
```

## Configuration Options

### Frontmatter Configuration
```yaml
---
description: Command description shown in help
argument-hint: Usage pattern for arguments
allowed-tools: Comma-separated list of allowed tools
model: Specific AI model to use
---
```

### Tools Restriction Example
```markdown
---
description: Analyze code without making changes
argument-hint: <file-pattern>
allowed-tools: Read, Grep, WebSearch
---

Analyze all files matching pattern: $1
Do not make any modifications.
```

## Practical Examples

### Example 5: Multi-Stage Refactoring Command
**File**: `.claude/commands/refactor-advanced.md`
```markdown
---
description: Perform multi-stage refactoring with validation
argument-hint: <target> <refactor-type> [safety-level] [test-coverage]
allowed-tools: Read, Write, Edit, Bash
---

Refactoring Request:
- Target: $1
- Refactoring Type: $2
- Safety Level: ${3:-standard}
- Required Test Coverage: ${4:-80}%

Stage 1: Analysis
- Identify all usages of $1
- Assess impact radius
- ${3:strict:+Create comprehensive backup}

Stage 2: Implementation
- Apply $2 refactoring to $1
- ${3:strict:+Implement gradual migration path}
- Maintain backward compatibility: ${3:strict:+mandatory}${3:standard:+where possible}

Stage 3: Validation
- Run existing tests
- ${4:+Ensure test coverage ≥ $4%}
- ${3:strict:+Perform manual review checklist}

Stage 4: Documentation
- Update code documentation
- ${3:strict:+Create migration guide}
- Log changes in CHANGELOG
```

### Example 6: Conditional Feature Development
**File**: `.claude/commands/feature.md`
```markdown
---
description: Develop a new feature with conditional requirements
argument-hint: <feature-name> <type> [frontend] [backend] [database]
---

Feature Development: $1
Type: $2

Components to implement:
${3:+Frontend ($3):
  - UI components
  - State management
  - API integration
  - Responsive design}

${4:+Backend ($4):
  - API endpoints
  - Business logic
  - Authentication/Authorization
  - Data validation}

${5:+Database ($5):
  - Schema changes
  - Migrations
  - Indexes
  - Data seeding}

Integration requirements:
${3:+${4:+- Frontend-Backend API contract}}
${4:+${5:+- Backend-Database ORM mapping}}
${3:+${5:+- End-to-end data flow}}
```

**Usage Examples**:
```
/feature user-profile basic react nodejs postgres
/feature search-system advanced vue
/feature notification-service standard "" python redis
```

## Best Practices

### 1. Argument Validation
Always provide clear `argument-hint` to guide users:
```markdown
---
argument-hint: <required> [optional] [--flags]
---
```

### 2. Defensive Programming with Arguments
Use parameter expansion for robustness:
```markdown
Target file: ${1:?Error: filename required}
Priority: ${2:-normal}
${3:+Additional context: $3}
```

### 3. Combining Global and Positional Arguments
```markdown
---
description: Flexible command supporting both styles
argument-hint: <action> [specifics...]
---

Action: $1
Full command: $ARGUMENTS
Remaining args: ${@:2}

# Allows both:
# /cmd simple-usage
# /cmd complex arg1 arg2 arg3
```

### 4. Testing Multiple Argument Scenarios
Create test commands to validate argument handling:
```markdown
---
description: Test argument parsing
---

Test Results:
- All args: $ARGUMENTS
- First: ${1:-missing}
- Second: ${2:-missing}
- Third: ${3:-missing}
- Rest: ${@:4}
- Count: $#
```

### 5. Documentation Within Commands
Include inline documentation for complex commands:
```markdown
# This command accepts 3-5 arguments:
# $1: (required) target resource
# $2: (required) action type
# $3: (optional) configuration file
# $4: (optional) environment
# $5: (optional) dry-run flag
```

### 6. Error Handling
Implement validation messages:
```markdown
${1:?❌ Error: Missing required argument - please specify the target file}
${2:?❌ Error: Missing required argument - please specify the operation type}

✅ Processing $1 with operation $2...
```

## Advanced Techniques

### Variadic Arguments
Handle variable number of arguments:
```markdown
---
description: Process multiple files
argument-hint: <action> <files...>
---

Action: $1
Files to process: ${@:2}

!for file in ${@:2}; do
  echo "Processing: $file"
done
```

### Conditional Logic Based on Argument Count
```markdown
${2:+Two or more arguments provided}
${3:+Three or more arguments provided}
${4:+Four or more arguments provided}

${2:-Only one argument provided}
```

### Named Parameter Simulation
While not native, you can simulate named parameters:
```markdown
---
description: Simulate named parameters
argument-hint: "key1=value1 key2=value2"
---

Parse the following configuration: $ARGUMENTS

Extract and process:
- Database settings if "db=" is present
- API keys if "api=" is present
- Feature flags if "flags=" is present
```

---

**Author**: Russo Davide (The DaveEloper)  
**Email**: vibecoding@pcok.it  
**Project**: ChatTokener Suite  
**Component**: VAA Bonus - Custom Slash Commands Guide

This comprehensive guide covers all aspects of using arguments in Claude Code custom slash commands, with special emphasis on handling multiple arguments effectively.