# Claude Hook System Documentation

The hook system provides automated actions triggered by Claude's tool usage, enabling powerful workflows and maintaining project context.

## Overview

Hooks are scripts that run automatically when certain events occur during your Claude session. They can:
- Track project progress
- Analyze context
- Format code
- Run tests
- Detect secrets
- Create checkpoints
- Update documentation

## Hook Types

### 1. PostToolUse Hooks
Triggered after Claude uses specific tools (Edit, Write, Bash, etc.)

### 2. Stop Hooks  
Triggered when a Claude session ends

### 3. SubagentStop Hooks
Triggered when a sub-agent completes its task

### 4. PreToolUse Hooks
Triggered before Claude uses a tool (less common)

## Configuration

### hooks_config.json Structure

```json
{
  "PostToolUse": [
    {
      "name": "Context Analyzer",
      "script": "~/.claude/hooks/claude-project-context-analyzer.py",
      "triggers": ["Edit", "Write", "Bash", "Task"],
      "frequency": 5,
      "enabled": true
    },
    {
      "name": "Code Formatter",
      "script": "~/.claude/hooks/claude-code-formatter.py",
      "triggers": ["Edit", "Write"],
      "patterns": ["*.py", "*.js", "*.ts"],
      "enabled": true
    }
  ],
  "Stop": [
    {
      "name": "Project Checkpoint",
      "command": "claude-project checkpoint",
      "enabled": true
    }
  ]
}
```

### Enabling Hooks in Claude Desktop

1. Open Claude Desktop
2. Go to Settings → Developer → Hooks
3. Add hook configuration
4. Restart Claude Desktop

## Core Hooks

### 1. Context Analyzer Hook

**File**: `claude-project-context-analyzer.py`

**Purpose**: Analyzes work context and updates project files automatically

**Features**:
- Tracks meaningful actions (Edit, Write, Bash, Task)
- Updates project context every 5 actions
- Can use Anthropic API or local analysis
- Maintains session state
- Adds git diff information

**Configuration**:
```python
# Environment variables
ANTHROPIC_API_KEY=sk-ant-...
CONTEXT_ANALYSIS_MODE=local  # or 'api'
CONTEXT_UPDATE_FREQUENCY=5
```

**How it works**:
1. Monitors transcript file for changes
2. Counts meaningful actions
3. Every 5 actions, analyzes recent work
4. Updates active project with context
5. Preserves state between invocations

### 2. UV Enforcer Hook

**File**: `claude-uv-enforcer.py`

**Purpose**: Ensures Python projects use `uv` package manager

**Triggers on**:
- Creating requirements.txt
- Running pip commands
- Python project initialization

**Actions**:
- Converts pip commands to uv
- Creates uv.lock files
- Suggests uv alternatives

### 3. Secrets Detector Hook

**File**: `claude-secrets-detector.py`

**Purpose**: Prevents accidental commit of secrets

**Detects**:
- API keys
- Passwords
- Private keys
- Environment variables
- AWS credentials
- Database URLs

**Actions**:
- Warns about detected secrets
- Suggests .gitignore updates
- Can block operations

### 4. Code Formatter Hook

**File**: `claude-code-formatter.py`

**Purpose**: Automatically formats code after edits

**Supports**:
- Python (black, ruff)
- JavaScript/TypeScript (prettier)
- Go (gofmt)
- Rust (rustfmt)

**Configuration**:
```json
{
  "python": {
    "formatter": "black",
    "args": ["--line-length", "88"]
  },
  "javascript": {
    "formatter": "prettier",
    "config": ".prettierrc"
  }
}
```

### 5. Test Runner Hook

**File**: `claude-test-runner.py`

**Purpose**: Runs tests after code changes

**Features**:
- Detects test framework
- Runs relevant tests only
- Reports results
- Can block on failure

**Supported frameworks**:
- Python: pytest, unittest
- JavaScript: jest, mocha
- Go: go test
- Rust: cargo test

### 6. Pre-Git-Init Hook

**File**: `pre-git-init.sh`

**Purpose**: Enforces project location rules

**Rules**:
- GitHub projects must be in ~/Documents/GitHub/
- Prevents creation in wrong directories
- Suggests correct location

## Creating Custom Hooks

### Hook Template (Python)

```python
#!/usr/bin/env python3
"""Custom hook for Claude"""

import sys
import json
import os
from pathlib import Path

def main():
    # Get transcript path from command line
    if len(sys.argv) < 2:
        print("Usage: hook.py <transcript_path>")
        sys.exit(1)
    
    transcript_path = sys.argv[1]
    
    # Read transcript
    with open(transcript_path, 'r') as f:
        transcript = json.load(f)
    
    # Get recent messages
    messages = transcript.get('messages', [])
    
    # Find tool uses
    for msg in messages:
        if msg.get('role') == 'assistant':
            for content in msg.get('content', []):
                if content.get('type') == 'tool_use':
                    tool_name = content.get('name')
                    tool_input = content.get('input', {})
                    
                    # Your logic here
                    process_tool_use(tool_name, tool_input)
    
    return 0

def process_tool_use(tool_name, tool_input):
    """Process specific tool usage"""
    if tool_name == 'Edit':
        file_path = tool_input.get('file_path')
        print(f"File edited: {file_path}")
        # Add your custom logic

if __name__ == "__main__":
    sys.exit(main())
```

### Hook Template (Bash)

```bash
#!/bin/bash
# Custom bash hook for Claude

# Get transcript path
TRANSCRIPT_PATH="$1"

# Check if transcript exists
if [ ! -f "$TRANSCRIPT_PATH" ]; then
    echo "Transcript not found: $TRANSCRIPT_PATH"
    exit 1
fi

# Parse transcript (requires jq)
TOOL_USES=$(jq -r '.messages[] | select(.role=="assistant") | .content[] | select(.type=="tool_use") | .name' "$TRANSCRIPT_PATH")

# Process tool uses
while IFS= read -r tool; do
    case "$tool" in
        "Bash")
            echo "Bash command executed"
            # Your logic here
            ;;
        "Edit")
            echo "File edited"
            # Your logic here
            ;;
    esac
done <<< "$TOOL_USES"

exit 0
```

### Hook Best Practices

1. **Fast Execution**: Hooks should complete quickly (< 5 seconds)
2. **Error Handling**: Always handle errors gracefully
3. **Logging**: Log to ~/.claude/logs/ for debugging
4. **State Management**: Use state files for persistence
5. **Idempotency**: Hooks may run multiple times

## Hook Execution Flow

```
Claude Action
    ↓
Transcript Updated
    ↓
Hook Triggered
    ↓
Read Transcript
    ↓
Process Action
    ↓
Update State/Files
    ↓
Return Result
```

## Debugging Hooks

### Enable Debug Mode

```bash
export CLAUDE_HOOK_DEBUG=1
```

### Test Hooks Manually

```bash
# Create test transcript
cat > test-transcript.json << 'EOF'
{
  "messages": [
    {
      "role": "assistant",
      "content": [
        {
          "type": "tool_use",
          "name": "Edit",
          "input": {
            "file_path": "/tmp/test.py",
            "old_string": "hello",
            "new_string": "world"
          }
        }
      ]
    }
  ]
}
EOF

# Run hook
~/.claude/hooks/my-hook.py test-transcript.json
```

### View Hook Logs

```bash
# Hook logs location
tail -f ~/.claude/logs/hooks.log

# Individual hook logs
tail -f ~/.claude/logs/context-analyzer.log
```

## Advanced Hook Features

### State Persistence

```python
import json
from pathlib import Path

class HookState:
    def __init__(self, state_file):
        self.state_file = Path(state_file)
        self.state = self.load()
    
    def load(self):
        if self.state_file.exists():
            return json.loads(self.state_file.read_text())
        return {}
    
    def save(self):
        self.state_file.write_text(json.dumps(self.state, indent=2))
    
    def get(self, key, default=None):
        return self.state.get(key, default)
    
    def set(self, key, value):
        self.state[key] = value
        self.save()

# Usage
state = HookState("~/.claude/.my_hook_state.json")
count = state.get('action_count', 0)
state.set('action_count', count + 1)
```

### Conditional Execution

```python
def should_run_hook(transcript):
    """Determine if hook should run based on conditions"""
    
    # Check for specific project type
    project = get_active_project()
    if project and project.get('type') == 'work':
        return False
    
    # Check for specific file patterns
    edited_files = get_edited_files(transcript)
    if any(f.endswith('.test.js') for f in edited_files):
        return False
    
    # Check time-based conditions
    last_run = state.get('last_run', 0)
    if time.time() - last_run < 300:  # 5 minutes
        return False
    
    return True
```

### Integration with External Services

```python
import requests

def notify_slack(message):
    """Send notification to Slack"""
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    if webhook_url:
        requests.post(webhook_url, json={'text': message})

def update_linear_ticket(ticket_id, comment):
    """Update Linear ticket with progress"""
    api_key = os.environ.get('LINEAR_API_KEY')
    if api_key:
        # Linear API call
        pass
```

## Troubleshooting

### Hook Not Firing

1. Check hook is enabled in config
2. Verify Claude Desktop settings
3. Check file permissions (must be executable)
4. Look for errors in Claude Desktop logs
5. Test hook manually with sample transcript

### Hook Errors

1. Check hook logs in ~/.claude/logs/
2. Run hook manually to see errors
3. Verify Python/bash environment
4. Check for missing dependencies

### Performance Issues

1. Profile hook execution time
2. Use state files to avoid repeated work
3. Consider frequency settings
4. Implement caching where appropriate

## Security Considerations

1. **Never log sensitive data** in hooks
2. **Validate all inputs** from transcripts
3. **Use environment variables** for secrets
4. **Restrict file system access** appropriately
5. **Be careful with external API calls**