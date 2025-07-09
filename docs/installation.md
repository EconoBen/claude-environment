# Installation Guide

This guide will walk you through setting up the complete Claude Environment system on your machine.

## Prerequisites

### Required Software
- **macOS** or **Linux** (Windows via WSL2)
- **Bash** 4.0 or higher
- **Python** 3.8 or higher
- **Git** 2.0 or higher
- **GitHub CLI** (`gh`) - [Install guide](https://cli.github.com/)

### Recommended Software
- **fzf** - For interactive project selection
- **jq** - For JSON processing
- **ripgrep** (`rg`) - For fast searching

### Claude Desktop App
- Claude Desktop App installed and configured
- Valid Claude API subscription

## Quick Installation

```bash
# Clone the repository
git clone https://github.com/EconoBen/claude-environment.git
cd claude-environment

# Run the installer
./install.sh

# Verify installation
claude-project --version
```

## Manual Installation

### 1. Create Directory Structure

```bash
# Create base directories
mkdir -p ~/.claude/{projects/{active,archived,ideas,trash},hooks,templates}

# Create config directory
mkdir -p ~/.config/claude
```

### 2. Install Core Scripts

```bash
# Copy the main script
cp scripts/claude-project ~/bin/
chmod +x ~/bin/claude-project

# Copy hook scripts
cp hooks/* ~/.claude/hooks/
chmod +x ~/.claude/hooks/*

# Copy templates
cp templates/* ~/.claude/templates/
```

### 3. Configure Environment

```bash
# Add to your shell profile (~/.zshrc or ~/.bashrc)
export PATH="$HOME/bin:$PATH"
export CLAUDE_HOME="$HOME/.claude"

# Source the completions
source ~/.claude/completions/claude-project.zsh  # For Zsh
# OR
source ~/.claude/completions/claude-project.bash # For Bash
```

### 4. Create Configuration File

Create `~/.claude/config.yaml`:

```yaml
# Project defaults
default_project_type: personal
default_priority: medium

# Integration settings
github_integration: true
linear_integration: false
git_auto_commit: true
git_remote_backup: true

# Hook settings
install_hooks_on_create: true
auto_checkpoint_interval: 1800

# UI preferences
use_fzf: true
show_stats_on_list: true

# API settings (optional)
anthropic_api_key: ""  # For context analysis
context_analysis_enabled: false
```

### 5. Initialize Git Repository

```bash
cd ~/.claude
git init
git add .
git commit -m "Initial Claude environment setup"

# Optional: Add remote backup
git remote add origin git@github.com:yourusername/claude-backup.git
git push -u origin main
```

### 6. Configure Claude Desktop Hooks

Add to Claude Desktop settings (Settings → Developer → Hooks):

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "command": "~/.claude/hooks/claude-project-context-analyzer.py",
        "args": ["--transcript", "{transcript_path}"],
        "timeout": 5000
      }
    ],
    "Stop": [
      {
        "command": "claude-project",
        "args": ["checkpoint"],
        "timeout": 10000
      }
    ]
  }
}
```

### 7. Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv ~/.claude/.venv
source ~/.claude/.venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Requirements.txt:
```
anthropic>=0.8.0
pyyaml>=6.0
python-dotenv>=1.0.0
click>=8.0
rich>=13.0
gitpython>=3.1
```

## Post-Installation Setup

### 1. Verify Installation

```bash
# Check claude-project command
claude-project --help

# Create test project
claude-project new "Test Project"

# List projects
claude-project list
```

### 2. Configure GitHub Integration

```bash
# Authenticate GitHub CLI
gh auth login

# Test GitHub integration
claude-project new "GitHub Test"
claude-project link proj-* github 1
```

### 3. Set Up Cron Backup (Optional)

```bash
# Add to crontab
crontab -e

# Add this line for hourly backups
0 * * * * cd ~/.claude && git add -A && git commit -m "Hourly backup" && git push
```

### 4. Install CLAUDE.md (Optional)

```bash
# Copy the Claude instructions
cp examples/CLAUDE.md ~/.claude/

# This provides Claude with awareness of your project system
```

## Customization

### Custom Templates

Create custom project templates in `~/.claude/templates/`:

```bash
# Example: Create a Python project template
cat > ~/.claude/templates/python.md << 'EOF'
---
id: {{ id }}
name: {{ name }}
type: {{ type }}
status: planning
priority: medium
tags: [python]
context_files: [requirements.txt, setup.py, main.py]
---

# {{ name }}

## Overview
Python project for...

## Setup
\`\`\`bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
\`\`\`

## Goals
- [ ] Set up project structure
- [ ] Create main module
- [ ] Add tests
- [ ] Write documentation
EOF
```

### Custom Hooks

Add custom hooks to `~/.claude/hooks/`:

```python
#!/usr/bin/env python3
# ~/.claude/hooks/my-custom-hook.py

import sys
import json

def main():
    # Your hook logic here
    transcript_path = sys.argv[1]
    
    # Process transcript
    with open(transcript_path, 'r') as f:
        data = json.load(f)
    
    # Do something useful
    print("Hook executed successfully")

if __name__ == "__main__":
    main()
```

## Troubleshooting

### Command Not Found

```bash
# Ensure ~/bin is in PATH
echo $PATH | grep -q "$HOME/bin" || echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Permission Denied

```bash
# Fix script permissions
chmod +x ~/bin/claude-project
chmod +x ~/.claude/hooks/*
```

### Hooks Not Running

1. Check Claude Desktop hook configuration
2. Verify hook scripts are executable
3. Check hook logs in Claude Desktop
4. Test hooks manually:
   ```bash
   ~/.claude/hooks/claude-project-context-analyzer.py --test
   ```

### Git Issues

```bash
# Initialize git if needed
cd ~/.claude
git init

# Fix any git problems
git config user.email "you@example.com"
git config user.name "Your Name"
```

## Uninstallation

```bash
# Remove scripts
rm ~/bin/claude-project

# Remove Claude directory (BACKUP FIRST!)
mv ~/.claude ~/.claude.backup

# Remove from shell profile
# Edit ~/.zshrc or ~/.bashrc and remove Claude-related lines

# Remove cron job if configured
crontab -e  # Remove the backup line
```

## Next Steps

1. Read the [Project System Documentation](project-system.md)
2. Learn about [Hooks](hooks.md)
3. Explore [Example Workflows](examples.md)
4. Configure [GitHub Integration](github-integration.md)