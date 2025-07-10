# Claude Hooks

This directory contains hooks that enhance Claude's functionality with automated checks and actions.

## Available Hooks

### claude-project-context-analyzer.py
**Trigger**: Every 5 Edit/Write/Bash/Task operations  
**Purpose**: Analyzes work context and updates project files with AI-generated insights
**Config**: Can use Claude API or local pattern matching

### claude-secrets-detector.py
**Trigger**: Write, Edit, MultiEdit operations  
**Purpose**: Detects potential secrets, API keys, and credentials
**Features**: Smart false-positive detection, severity levels

### pre-git-init.sh
**Trigger**: Before `git init` commands  
**Purpose**: Enforces project location rules (must be in ~/Documents/GitHub/)

### claude-uv-enforcer.py (optional)
**Trigger**: Bash commands with pip/requirements.txt  
**Purpose**: Suggests modern Python packaging with `uv`

### claude-code-formatter.py (optional)
**Trigger**: Edit/Write on code files  
**Purpose**: Checks code formatting and suggests fixes

### claude-test-runner.py (optional)
**Trigger**: Edit/Write on code files  
**Purpose**: Suggests relevant tests to run

## Installation

Hooks are installed automatically by the install.sh script. To manually install:

1. Copy hooks to ~/.claude/hooks/
2. Make them executable: `chmod +x ~/.claude/hooks/*.py`
3. Configure in Claude Desktop settings

## Configuration

Edit `~/.claude/hooks_config.json` to enable/disable hooks and adjust settings.

## Creating Custom Hooks

See the documentation for examples of creating your own hooks. Basic template:

```python
#!/usr/bin/env python3
import json
import sys

def main():
    if len(sys.argv) < 2:
        sys.exit(0)
    
    tool_data = json.loads(sys.argv[1])
    # Your logic here
    
if __name__ == "__main__":
    main()
```