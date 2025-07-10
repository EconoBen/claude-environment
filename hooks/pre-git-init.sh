#!/bin/bash
# Claude hook to prevent git init outside of ~/Documents/GitHub
# This runs before any git init command

OPERATION="$1"
DIRECTORY="$2"
GITHUB_BASE="$HOME/Documents/GitHub"
CLAUDE_PROJECT_FILE="$HOME/.claude/projects/active/proj-*"

# Function to check if current project is marked as work
is_work_project() {
    # Find the most recently modified project file
    local latest_project=$(ls -t $CLAUDE_PROJECT_FILE 2>/dev/null | head -1)
    if [[ -f "$latest_project" ]]; then
        grep -q "type: work" "$latest_project"
        return $?
    fi
    return 1
}

if [[ "$OPERATION" == "git init" ]]; then
    # Check if the directory is in the approved location
    if [[ "$DIRECTORY" != "$GITHUB_BASE"* ]]; then
        echo "ERROR: Git repositories must be created in ~/Documents/GitHub/"
        echo "Current directory: $DIRECTORY"
        echo "Please use one of these locations:"
        echo "  - Personal: $GITHUB_BASE/[project-name]/"
        echo "  - Work: $GITHUB_BASE/monohelix/projects/[project-name]/"
        echo "  - Monohelix tools: $GITHUB_BASE/monohelix/tools/[tool-name]/"
        exit 1
    fi
    
    # Check if this is a work project
    if is_work_project; then
        # Work projects must be in monohelix directory
        if [[ "$DIRECTORY" != "$GITHUB_BASE/monohelix/projects/"* ]] && \
           [[ "$DIRECTORY" != "$GITHUB_BASE/monohelix/tools/"* ]]; then
            echo "ERROR: Work projects must be created in ~/Documents/GitHub/monohelix/projects/"
            echo "Current directory: $DIRECTORY"
            echo "This is marked as a work project. Please use:"
            echo "  - $GITHUB_BASE/monohelix/projects/[project-name]/"
            exit 1
        fi
    fi
fi

# All checks passed
exit 0