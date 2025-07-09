# Claude Project System Documentation

The claude-project system is a comprehensive project management framework designed specifically for tracking work done with Claude AI.

## Core Concepts

### Projects
A project represents a discrete unit of work with Claude. Each project has:
- Unique ID (timestamp-based)
- Name and description
- Type (personal/work)
- Status (planning/active/on-hold/completed/archived)
- Priority (low/medium/high)
- Time tracking
- Session history
- File tracking
- Integration links

### Project Lifecycle

```
Idea → Active Project → Checkpoint → Archive
         ↓                ↓
      On Hold        Sync to GitHub
```

## Command Reference

### Basic Commands

```bash
# Create a new project
claude-project new "Project Name"

# List all active projects
claude-project list

# Show current project status
claude-project status

# Continue working on a project
claude-project continue [project-id]

# Create a checkpoint
claude-project checkpoint

# Archive a completed project
claude-project archive [project-id]
```

### Advanced Commands

```bash
# Link project to GitHub issue
claude-project link [project-id] github [issue-number]

# Sync project progress to GitHub
claude-project sync [project-id]

# Install git hooks for a project
claude-project install-hooks [project-id]

# Delete a project (moves to trash)
claude-project delete [project-id]

# Convert an idea to active project
claude-project promote [idea-id]
```

## Project Structure

### Project File Format

```yaml
---
id: proj-1752101196
name: Claude Environment Reproduction System
type: personal
status: active
priority: high
created: 2024-01-15 10:30:00
updated: 2024-01-15 14:45:00
tags: [meta, documentation, tooling]
context_files: []
github_issue: 
linear_ticket: 
tracking:
  total_time: 4.5
  sessions: 3
  last_checkpoint: 2024-01-15 14:45:00
  files_modified: 12
  files_created: 8
---

# Claude Environment Reproduction System

## Overview
A comprehensive guide and toolkit for reproducing Ben's Claude AI development environment.

## Goals
- [ ] Document all components of the Claude environment
- [ ] Create installation scripts
- [ ] Package for distribution
- [x] Create GitHub repository

## Progress Log

### 2024-01-15 10:30 (Session 1)
#### Started
- Created project structure
- Initial documentation planning
#### Tools Used
- Task: 2 times
- Write: 5 times
#### Duration: 1.5 hours

## Context
Current focus: Creating comprehensive documentation
Last action: Set up initial project structure

## Next Steps
- Complete installation guide
- Document hook system in detail
- Create example workflows
```

### Directory Structure

```
~/.claude/projects/
├── active/         # Currently active projects
├── archived/       # Completed projects (read-only)
├── ideas/          # Project ideas and plans
└── trash/          # Deleted projects (30-day retention)
```

## Features

### Automatic Time Tracking
- Tracks time per session
- Calculates total project time
- Shows time since last checkpoint

### Session Management
- Each work session is logged
- Tools used are tracked
- Files modified are recorded
- Progress is documented

### Git Integration
- Automatic commits on checkpoint
- Optional remote backup
- Git hooks for commit messages
- Issue reference injection

### Context Preservation
- Links to relevant files
- Maintains project context
- Tracks current focus area
- Preserves work continuity

## Configuration

### config.yaml Options

```yaml
# Project defaults
default_project_type: personal  # or work
default_priority: medium       # low/medium/high

# Integration settings
github_integration: true
linear_integration: false
git_auto_commit: true
git_remote_backup: true

# Hook settings
install_hooks_on_create: true
auto_checkpoint_interval: 1800  # 30 minutes

# UI preferences
use_fzf: true
show_stats_on_list: true
```

### Environment Variables

```bash
# Override config file location
export CLAUDE_CONFIG_PATH="$HOME/.claude/config.yaml"

# Set default project directory
export CLAUDE_PROJECT_DIR="$HOME/.claude/projects"

# Enable debug output
export CLAUDE_DEBUG=1
```

## Best Practices

### Project Naming
- Use descriptive names
- Include technology/framework if relevant
- Avoid special characters
- Keep under 50 characters

### Checkpoint Frequency
- After completing major features
- Before starting new components
- At natural break points
- Every 30-60 minutes of work

### Progress Documentation
- Be specific about changes
- Include tool usage stats
- Document decisions made
- Note any blockers

### File Tracking
- Use context_files for key files
- Update when focus changes
- Include configuration files
- Track test files

## Troubleshooting

### Common Issues

**Project not found**
```bash
# Check if project exists
claude-project list --all

# Search in archived
ls ~/.claude/projects/archived/
```

**Checkpoint fails**
```bash
# Check git status
cd ~/.claude && git status

# Manual checkpoint
cd ~/.claude && git add -A && git commit -m "Manual checkpoint"
```

**Sync not working**
```bash
# Verify GitHub CLI auth
gh auth status

# Check project has issue linked
claude-project status
```

## Integration Examples

### With Git Commits
```bash
# Git hook adds "Ref: #123" to commits
git commit -m "Add new feature"
# Becomes: "Add new feature Ref: #123"
```

### With GitHub Issues
```bash
# Link and sync
claude-project link proj-123 github 456
claude-project sync proj-123

# Issue comment added:
# "Progress Update: Completed authentication module..."
```

### With Claude Sessions
```bash
# At session start
claude-project continue

# During work (automatic via hooks)
# - Time tracking updates
# - File modifications logged
# - Context preserved

# At session end
claude-project checkpoint
```