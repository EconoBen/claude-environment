#!/bin/bash
# Claude Environment Installation Script
# This script sets up the complete Claude project management system

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "\n${BLUE}==== $1 ====${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        print_success "$1 is installed"
        return 0
    else
        print_error "$1 is not installed"
        return 1
    fi
}

# Header
echo -e "${BLUE}"
echo "  ____ _                 _        _____            "
echo " / ___| | __ _ _   _  __| | ___  | ____|_ ____   __"
echo "| |   | |/ _\` | | | |/ _\` |/ _ \\ |  _| | '_ \\ \\ / /"
echo "| |___| | (_| | |_| | (_| |  __/ | |___| | | \\ V / "
echo " \\____|_|\\__,_|\\__,_|\\__,_|\\___| |_____|_| |_|\\_/  "
echo -e "${NC}"
echo "Claude Environment Installation Script v1.0"
echo "=========================================="

# Check prerequisites
print_header "Checking Prerequisites"

MISSING_PREREQS=0

# Check OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    print_success "macOS detected"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    print_success "Linux detected"
else
    print_error "Unsupported OS: $OSTYPE"
    exit 1
fi

# Check required commands
for cmd in bash git python3 pip3; do
    if ! check_command "$cmd"; then
        MISSING_PREREQS=1
    fi
done

# Check optional but recommended commands
print_header "Checking Optional Dependencies"
for cmd in gh fzf jq rg; do
    if ! check_command "$cmd"; then
        print_warning "$cmd is not installed (optional but recommended)"
    fi
done

if [ $MISSING_PREREQS -eq 1 ]; then
    print_error "Missing required prerequisites. Please install them first."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then 
    print_success "Python $PYTHON_VERSION meets minimum requirement ($REQUIRED_VERSION)"
else
    print_error "Python $PYTHON_VERSION is below minimum requirement ($REQUIRED_VERSION)"
    exit 1
fi

# Create directory structure
print_header "Creating Directory Structure"

CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"
mkdir -p "$CLAUDE_HOME"/{projects/{active,archived,ideas,trash},hooks,templates,logs}
mkdir -p "$HOME/bin"
mkdir -p "$HOME/.config/claude"

print_success "Created directory structure at $CLAUDE_HOME"

# Copy scripts
print_header "Installing Scripts"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Copy main script
if [ -f "$SCRIPT_DIR/scripts/claude-project" ]; then
    cp "$SCRIPT_DIR/scripts/claude-project" "$HOME/bin/"
    chmod +x "$HOME/bin/claude-project"
    print_success "Installed claude-project command"
else
    print_warning "claude-project script not found in scripts/ - will create from embedded version"
    # We'll handle this in the next steps
fi

# Copy hooks
if [ -d "$SCRIPT_DIR/hooks" ]; then
    cp -r "$SCRIPT_DIR/hooks/"* "$CLAUDE_HOME/hooks/" 2>/dev/null || true
    chmod +x "$CLAUDE_HOME/hooks/"*.py "$CLAUDE_HOME/hooks/"*.sh 2>/dev/null || true
    print_success "Installed hook scripts"
else
    print_warning "Hook scripts not found in hooks/ - will create from embedded versions"
fi

# Copy templates
if [ -d "$SCRIPT_DIR/templates" ]; then
    cp -r "$SCRIPT_DIR/templates/"* "$CLAUDE_HOME/templates/" 2>/dev/null || true
    print_success "Installed project templates"
else
    print_warning "Templates not found - creating defaults"
    # Create default template
    cat > "$CLAUDE_HOME/templates/default.md" << 'EOF'
---
id: {{ id }}
name: {{ name }}
type: {{ type }}
status: planning
priority: medium
created: {{ created }}
updated: {{ updated }}
tags: []
context_files: []
github_issue: 
linear_ticket: 
tracking:
  total_time: 0
  sessions: 0
  last_checkpoint: 
  files_modified: 0
  files_created: 0
---

# {{ name }}

## Overview
[Project description]

## Goals
- [ ] Goal 1
- [ ] Goal 2
- [ ] Goal 3

## Progress Log

### {{ created }} (Session 1)
#### Started
- Project initialization
#### Tools Used
- None yet
#### Duration: 0 minutes

## Context
Current focus: Planning phase

## Next Steps
- Define project scope
- Break down into tasks
- Begin implementation
EOF
    print_success "Created default template"
fi

# Create configuration
print_header "Creating Configuration"

CONFIG_FILE="$CLAUDE_HOME/config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    cat > "$CONFIG_FILE" << 'EOF'
# Claude Environment Configuration

# Project defaults
default_project_type: personal  # personal or work
default_priority: medium       # low, medium, high

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

# API settings (optional)
anthropic_api_key: ""  # For context analysis
context_analysis_enabled: false
EOF
    print_success "Created default configuration"
else
    print_warning "Configuration already exists at $CONFIG_FILE"
fi

# Initialize git repository
print_header "Initializing Git Repository"

cd "$CLAUDE_HOME"
if [ ! -d .git ]; then
    git init
    git add .
    git commit -m "Initial Claude environment setup" || true
    print_success "Initialized git repository"
else
    print_warning "Git repository already initialized"
fi

# Set up Python environment
print_header "Setting Up Python Environment"

if [ ! -d "$CLAUDE_HOME/.venv" ]; then
    python3 -m venv "$CLAUDE_HOME/.venv"
    print_success "Created Python virtual environment"
else
    print_warning "Python virtual environment already exists"
fi

# Install Python dependencies
source "$CLAUDE_HOME/.venv/bin/activate"

# Create requirements file if not present
if [ ! -f "$SCRIPT_DIR/requirements.txt" ]; then
    cat > /tmp/claude-requirements.txt << 'EOF'
anthropic>=0.8.0
pyyaml>=6.0
python-dotenv>=1.0.0
click>=8.0
rich>=13.0
gitpython>=3.1
requests>=2.25.0
EOF
    pip install -r /tmp/claude-requirements.txt
    rm /tmp/claude-requirements.txt
else
    pip install -r "$SCRIPT_DIR/requirements.txt"
fi
print_success "Installed Python dependencies"

deactivate

# Shell configuration
print_header "Configuring Shell"

# Detect shell
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
    SHELL_NAME="zsh"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
    SHELL_NAME="bash"
else
    SHELL_RC="$HOME/.profile"
    SHELL_NAME="sh"
fi

# Add to PATH
if ! grep -q "export PATH=\"\$HOME/bin:\$PATH\"" "$SHELL_RC"; then
    echo "" >> "$SHELL_RC"
    echo "# Claude Environment" >> "$SHELL_RC"
    echo "export PATH=\"\$HOME/bin:\$PATH\"" >> "$SHELL_RC"
    echo "export CLAUDE_HOME=\"$CLAUDE_HOME\"" >> "$SHELL_RC"
    print_success "Added Claude to PATH in $SHELL_RC"
else
    print_warning "PATH already configured"
fi

# Verify installation
print_header "Verifying Installation"

export PATH="$HOME/bin:$PATH"

if command -v claude-project &> /dev/null; then
    print_success "claude-project command is available"
    
    # Test creating a project
    if claude-project new "Test Project" &> /dev/null; then
        print_success "Successfully created test project"
        # Clean up test project
        rm -f "$CLAUDE_HOME/projects/active/proj-"*Test-Project* 2>/dev/null
    else
        print_warning "Could not create test project"
    fi
else
    print_error "claude-project command not found"
fi

# Final instructions
print_header "Installation Complete!"

echo "Next steps:"
echo "1. Reload your shell configuration:"
echo "   source $SHELL_RC"
echo ""
echo "2. Verify the installation:"
echo "   claude-project --help"
echo ""
echo "3. Create your first project:"
echo "   claude-project new \"My First Project\""
echo ""

if ! command -v gh &> /dev/null; then
    echo "4. Install GitHub CLI for GitHub integration:"
    echo "   https://cli.github.com/"
    echo ""
fi

if ! command -v fzf &> /dev/null; then
    echo "5. Install fzf for interactive project selection:"
    echo "   https://github.com/junegunn/fzf"
    echo ""
fi

echo "Configuration file: $CLAUDE_HOME/config.yaml"
echo "Project directory: $CLAUDE_HOME/projects/"
echo ""
echo "For more information, see the documentation at:"
echo "https://github.com/EconoBen/claude-environment"

# Check if we need to create the claude-project script
if [ ! -f "$HOME/bin/claude-project" ]; then
    print_warning ""
    print_warning "The claude-project script was not found in the scripts directory."
    print_warning "Please run: ./install.sh --create-scripts"
    print_warning "to generate the scripts from the embedded versions."
fi