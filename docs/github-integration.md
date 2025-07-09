# GitHub Integration Documentation

The Claude environment provides deep GitHub integration for seamless project tracking, issue management, and progress synchronization.

## Overview

GitHub integration enables:
- Automatic issue creation for projects
- Progress syncing to issue comments
- Commit message enhancement
- Git hook integration
- Automated backups
- Pull request tracking

## Setup

### Prerequisites

1. **GitHub CLI installed and authenticated**:
```bash
# Install GitHub CLI
brew install gh  # macOS
# or
sudo apt install gh  # Ubuntu/Debian

# Authenticate
gh auth login
```

2. **Git configured**:
```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

3. **SSH keys configured** (optional but recommended):
```bash
gh auth login --protocol ssh
```

## Core Features

### 1. Automatic Issue Creation

When creating a new project, optionally create a GitHub issue:

```bash
# Create project with GitHub issue
claude-project new "Add user authentication" --github

# Creates:
# 1. New project file
# 2. GitHub issue with project details
# 3. Links them together
```

**Issue Template**:
```markdown
# Add user authentication

**Project ID**: proj-1234567890
**Type**: personal
**Priority**: high
**Created**: 2024-01-15

## Overview
[Project description from template]

## Goals
- [ ] Goal 1
- [ ] Goal 2

## Progress
Progress updates will be posted automatically.

---
*This issue is linked to Claude project proj-1234567890*
```

### 2. Project Linking

Link existing projects to GitHub issues:

```bash
# Link to existing issue
claude-project link proj-123 github 456

# Link to issue by URL
claude-project link proj-123 github https://github.com/user/repo/issues/456
```

**Metadata Update**:
```yaml
github_issue: 456
github_repo: user/repo
```

### 3. Progress Synchronization

Sync project progress to GitHub issue comments:

```bash
# Manual sync
claude-project sync proj-123

# Auto-sync on checkpoint
claude-project checkpoint  # Syncs if linked
```

**Progress Comment Format**:
```markdown
## Progress Update - 2024-01-15 14:30

### Session 3 Summary
**Duration**: 1.5 hours
**Tools Used**: Edit (12), Write (5), Bash (8)

### Completed
✅ Implemented JWT token generation
✅ Added token validation middleware
✅ Created user authentication endpoints

### Context
**Current Goal**: Complete authentication system
**Focus Area**: Token refresh mechanism

### Files Modified
- `/src/auth/jwt.js`
- `/src/auth/middleware.js`
- `/src/routes/auth.js`

### Next Steps
- Add token refresh endpoint
- Implement logout functionality
- Write authentication tests

---
*Updated by Claude project system*
```

### 4. Git Hook Integration

Install git hooks for automatic issue references:

```bash
# Install hooks for current project
claude-project install-hooks

# Installs prepare-commit-msg hook
```

**Hook Behavior**:
```bash
# Your commit message:
git commit -m "Add JWT validation"

# Becomes:
"Add JWT validation

Ref: #456"
```

### 5. Commit Integration

The project system can create commits with proper references:

```bash
# Checkpoint with commit
claude-project checkpoint --commit "Add authentication module"

# Creates commit with:
# - Your message
# - Issue reference
# - Project ID in metadata
```

## Configuration

### config.yaml Settings

```yaml
# Enable/disable GitHub integration
github_integration: true

# Default repository for new projects
github_default_repo: "username/repo"

# Auto-create issues for new projects
github_auto_create_issue: false

# Issue labels to add
github_issue_labels:
  - "claude-project"
  - "in-progress"

# Sync behavior
github_sync_on_checkpoint: true
github_sync_frequency: "on-change"  # or "hourly", "daily"

# Progress comment style
github_progress_style: "detailed"  # or "summary"
```

### Environment Variables

```bash
# Override default repo
export CLAUDE_GITHUB_REPO="myorg/myrepo"

# Set GitHub token (if not using gh cli)
export GITHUB_TOKEN="ghp_..."

# Enable debug logging
export CLAUDE_GITHUB_DEBUG=1
```

## Advanced Features

### 1. Issue Templates

Create custom issue templates in `~/.claude/templates/github/`:

```markdown
<!-- ~/.claude/templates/github/feature.md -->
## Feature: {{ name }}

**Project**: {{ project_id }}
**Estimated Time**: {{ estimated_hours }}h

### Description
{{ description }}

### Acceptance Criteria
- [ ] Criteria 1
- [ ] Criteria 2

### Technical Notes
{{ technical_notes }}
```

### 2. Bulk Operations

```bash
# Sync all active projects
claude-project sync --all

# Link multiple projects
claude-project link --batch << EOF
proj-123 github 456
proj-789 github 457
EOF

# Archive completed projects with issues
claude-project archive --close-issue proj-123
```

### 3. PR Integration

Link projects to pull requests:

```bash
# Link to PR
claude-project link proj-123 pr 789

# Auto-updates PR description with project info
```

**PR Description Update**:
```markdown
## Description
[Original PR description]

---

### Claude Project Details
**Project**: Add user authentication (proj-123)
**Time Spent**: 4.5 hours
**Sessions**: 3

**Completed Goals**:
- ✅ JWT implementation
- ✅ Middleware setup
- ✅ API endpoints

[View full project](link-to-project)
```

### 4. Milestone Tracking

```bash
# Create projects for milestone
claude-project new "Feature A" --github --milestone "v2.0"

# List projects by milestone
claude-project list --milestone "v2.0"
```

### 5. Team Synchronization

Share project state with team:

```bash
# Export project with GitHub metadata
claude-project export proj-123 --with-github

# Import on another machine
claude-project import proj-123.json --preserve-github
```

## Workflows

### Standard Development Flow

```bash
# 1. Create project with issue
claude-project new "Implement search feature" --github

# 2. Work with Claude
# ... (Claude makes changes) ...

# 3. Checkpoint regularly (auto-syncs)
claude-project checkpoint

# 4. Create PR when ready
gh pr create --title "Add search feature" --body "$(claude-project summary)"

# 5. Link PR to project
claude-project link proj-123 pr 234

# 6. Complete and archive
claude-project archive proj-123 --close-issue --merge-pr
```

### Bug Fix Flow

```bash
# 1. Create project from issue
claude-project new --from-issue 567

# 2. Work on fix
# ... (Claude investigates and fixes) ...

# 3. Commit with reference
git commit -m "Fix memory leak in parser"
# Automatically adds "Fixes #567"

# 4. Sync final status
claude-project sync --close-issue
```

### Feature Branch Flow

```bash
# 1. Create project and branch
claude-project new "New feature" --github --branch feature/new-feature

# 2. Work on feature
# ... (development) ...

# 3. Push with tracking
git push -u origin feature/new-feature

# 4. Create PR from project
claude-project create-pr proj-123
```

## API Integration

### Using GitHub API Directly

```python
import subprocess
import json

def get_issue_details(issue_number):
    """Get issue details using gh cli"""
    result = subprocess.run(
        ['gh', 'issue', 'view', str(issue_number), '--json', 'title,body,labels'],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

def update_issue_comment(issue_number, comment):
    """Add comment to issue"""
    subprocess.run([
        'gh', 'issue', 'comment', str(issue_number),
        '--body', comment
    ])
```

### GraphQL Queries

```bash
# Complex queries via gh api
gh api graphql -f query='
  query($owner: String!, $repo: String!, $issue: Int!) {
    repository(owner: $owner, name: $repo) {
      issue(number: $issue) {
        title
        body
        projectCards {
          nodes {
            project {
              name
            }
          }
        }
      }
    }
  }
' -f owner=USER -f repo=REPO -f issue=123
```

## Security Best Practices

### 1. Token Management
- Use `gh auth` instead of raw tokens
- Never commit tokens to projects
- Use environment variables for automation

### 2. Repository Access
- Limit integration to specific repos
- Use fine-grained personal access tokens
- Review webhook permissions

### 3. Privacy
- Don't sync sensitive project details
- Use private repos for confidential work
- Sanitize progress updates

## Troubleshooting

### Authentication Issues

```bash
# Check gh authentication
gh auth status

# Refresh authentication
gh auth refresh

# Test API access
gh api user
```

### Sync Failures

```bash
# Debug sync issues
CLAUDE_GITHUB_DEBUG=1 claude-project sync proj-123

# Check rate limits
gh api rate_limit

# Manual sync via API
gh issue comment 456 --body "Manual progress update..."
```

### Hook Problems

```bash
# Verify hook installation
cat .git/hooks/prepare-commit-msg

# Test hook manually
.git/hooks/prepare-commit-msg .git/COMMIT_EDITMSG message

# Reinstall hooks
claude-project install-hooks --force
```

### Connection Issues

```bash
# Test GitHub connectivity
gh api /repos/owner/repo

# Use SSH instead of HTTPS
git remote set-url origin git@github.com:owner/repo.git

# Check proxy settings
echo $HTTP_PROXY $HTTPS_PROXY
```

## Best Practices

### 1. Issue Organization
- Use labels consistently
- Create milestones for major features
- Link related issues
- Keep descriptions updated

### 2. Progress Updates
- Sync after significant progress
- Include context in updates
- Reference specific commits
- Document blockers

### 3. Commit Messages
- Follow conventional commits
- Reference issues properly
- Include project ID for tracking
- Be descriptive but concise

### 4. Team Collaboration
- Share project templates
- Standardize workflows
- Document integration setup
- Regular synchronization