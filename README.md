# Claude Environment Reproduction System

A comprehensive guide and toolkit for reproducing Ben's Claude AI development environment, including project management, hooks, context analysis, and GitHub integration.

## Overview

This repository documents and provides tools to replicate a sophisticated Claude AI development environment that includes:

- **Project Management System**: Track work sessions, time, and progress
- **Hook System**: Automated actions triggered by Claude's tool usage
- **Context API**: Intelligent analysis of work context
- **GitHub Integration**: Seamless issue creation and progress tracking
- **Checkpoint & Backup**: Automatic version control and state preservation

## Quick Start

```bash
# Clone this repository
git clone https://github.com/EconoBen/claude-environment.git
cd claude-environment

# Run the installer
./install.sh

# Create your first project
claude-project new "My First Project"
```

## Documentation

- [Installation Guide](docs/installation.md)
- [Project System Documentation](docs/project-system.md)
- [Hook System Guide](docs/hooks.md)
- [Context API Documentation](docs/context-api.md)
- [GitHub Integration](docs/github-integration.md)
- [Example Workflows](docs/examples.md)

## Architecture

```
~/.claude/
├── projects/          # Project storage
│   ├── active/       # Current projects
│   ├── archived/     # Completed projects
│   ├── ideas/        # Project ideas
│   └── trash/        # Deleted projects
├── hooks/            # Hook scripts
├── templates/        # Project templates
├── config.yaml       # Configuration
└── CLAUDE.md         # Claude instructions
```

## Key Features

### Project Management
- Create, track, and archive projects
- Automatic time tracking
- Session management
- Progress checkpoints

### Intelligent Hooks
- Tool usage monitoring
- Automatic code formatting
- Secret detection
- Test running
- Context analysis

### GitHub Integration
- Automatic issue creation
- Progress syncing
- Commit message enhancement
- Issue linking

### Context Awareness
- Analyzes work patterns
- Updates project context
- Maintains session state
- Provides intelligent summaries

## Requirements

- macOS or Linux
- Bash 4.0+
- Python 3.8+
- Git
- GitHub CLI (gh)
- fzf (optional but recommended)

## Contributing

Contributions and feedback are welcome.

## License

MIT License

## Author

Built by [Ben Labaschin](https://econoben.dev) (@EconoBen)
