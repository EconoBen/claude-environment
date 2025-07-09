# Example Workflows

This guide demonstrates real-world workflows using the Claude environment system.

## Workflow 1: Starting a New Feature

### Scenario
You want to add a dark mode feature to your React application.

### Steps

```bash
# 1. Create a new project
claude-project new "Add dark mode to React app" --github

# Output:
# ✅ Created project: proj-1234567890 - Add dark mode to React app
# 📁 File: ~/.claude/projects/active/proj-1234567890-Add-dark-mode-to-React-app.md
# 🔗 Created GitHub issue #123
```

### Claude Session

```
You: Let's add dark mode to my React app. I want to use CSS variables and store the preference in localStorage.

Claude: I'll help you add dark mode to your React app. Let me start by examining your current setup.

[Claude uses Read, Edit, Write tools to implement dark mode]
[Context analyzer updates project every 5 actions]
[Hooks run to format code and check for issues]
```

### During Work

```bash
# Claude automatically:
# - Tracks time spent
# - Logs tool usage
# - Updates project context
# - Formats code via hooks

# You can check status anytime:
claude-project status

# Output:
# 📊 Project: Add dark mode to React app
# ⏱️  Time: 1.5 hours (current session: 45 min)
# 🎯 Goal: Implementing CSS variable system
# 📁 Files: 5 modified, 2 created
# 🔗 GitHub: #123
```

### Checkpoint

```bash
# After completing a major part:
claude-project checkpoint

# Automatically:
# ✅ Commits changes to git
# ✅ Updates GitHub issue with progress
# ✅ Saves project state
# ✅ Backs up to remote
```

### Completion

```bash
# When feature is complete:
claude-project archive proj-1234567890 --close-issue

# Creates final summary and closes GitHub issue
```

## Workflow 2: Debugging Production Issue

### Scenario
Users report that the search feature is returning incorrect results.

### Quick Start from Issue

```bash
# Create project from existing GitHub issue
claude-project new --from-issue 456

# Automatically:
# - Creates project with issue details
# - Links to GitHub issue
# - Sets priority based on labels
```

### Investigation Phase

```
You: The search feature is returning wrong results. Help me debug this.

Claude: I'll help you debug the search issue. Let me start by examining the search implementation.

[Uses Grep to find search-related code]
[Uses Read to examine the implementation]
[Context analyzer tracks investigation progress]
```

### Project Updates

The context analyzer automatically updates the project:

```markdown
## Context
**Current Goal**: Investigating search result accuracy issue
**Focus Area**: Search algorithm in /src/utils/search.js
**Last Updated**: 2024-01-15 15:45:00

### Recent Activity
- Examined search algorithm implementation
- Found issue with fuzzy matching threshold
- Identified affected user queries
```

### Fix Implementation

```
Claude: I found the issue. The fuzzy matching threshold is too low. Let me fix it.

[Edits search.js to adjust threshold]
[Updates tests to cover edge case]
[Runs tests via test runner hook]
```

### Resolution

```bash
# Commit the fix
git commit -m "Fix search accuracy by adjusting fuzzy match threshold"
# Hook adds: "Fixes #456"

# Sync and close
claude-project sync --close-issue

# Final GitHub comment includes:
# - Root cause analysis
# - Fix description
# - Test results
# - Total time: 45 minutes
```

## Workflow 3: Multi-Session Feature Development

### Scenario
Building a complex authentication system over multiple days.

### Day 1: Planning and Setup

```bash
# Create project
claude-project new "Implement OAuth2 authentication"

# Initial session with Claude
# - Discuss architecture
# - Set up basic structure
# - Create initial files

# End of day checkpoint
claude-project checkpoint
# Session 1: 2 hours, 15 files created
```

### Day 2: Continue Work

```bash
# Resume project
claude-project continue
# Shows: Last worked on 18 hours ago

# Or use interactive selector
claude-project continue
# Shows fzf picker with all active projects
```

```
You: Let's continue with the OAuth implementation. Where did we leave off?

Claude: Looking at the project context, we completed the basic OAuth flow structure yesterday. The current focus is implementing the token refresh mechanism. Let me check the current state of the code.

[Reads project file for context]
[Continues implementation from where it left off]
```

### Day 3: Integration Testing

```bash
# Check total progress
claude-project status --detailed

# Output:
# 📊 Project: Implement OAuth2 authentication
# ⏱️  Total Time: 5.5 hours
# 📅 Sessions: 3
# 🎯 Progress:
#   ✅ Basic OAuth flow (Day 1)
#   ✅ Token refresh mechanism (Day 2)
#   🔄 Integration testing (Current)
#   ⬜ Documentation
#   ⬜ Error handling improvements
```

### Completion

```bash
# Final checkpoint with summary
claude-project checkpoint --message "OAuth implementation complete"

# Generate summary for PR
claude-project summary proj-* > pr-description.md

# Create PR with project summary
gh pr create --title "Add OAuth2 authentication" --body-file pr-description.md
```

## Workflow 4: Refactoring with Tracking

### Scenario
Refactoring a legacy module to use modern patterns.

### Setup

```bash
# Create project with high priority
claude-project new "Refactor payment processing module" --priority high

# Link to existing issue
claude-project link proj-* github 789
```

### Systematic Refactoring

```
You: I need to refactor the payment module from callbacks to async/await. Let's be systematic about this.

Claude: I'll help you refactor the payment module systematically. Let me first analyze the current structure.

[Claude creates TodoWrite list for refactoring steps]
[Uses Task tool to find all callback patterns]
[Systematically refactors each file]
```

### Hook Integration

During refactoring:
- **Code formatter hook**: Ensures consistent style
- **Test runner hook**: Runs tests after each change
- **Context analyzer**: Tracks refactoring progress
- **Secrets detector**: Ensures no credentials exposed

### Progress Tracking

```bash
# Mid-refactoring status
claude-project status

# GitHub issue automatically updated with:
# - Files refactored: 12/18
# - Tests passing: ✅
# - Callback patterns remaining: 6
# - Estimated completion: 1 hour
```

## Workflow 5: Learning and Documentation

### Scenario
Learning a new framework and documenting the process.

### Project Setup

```bash
# Create learning project
claude-project new "Learn and document Svelte framework"

# This creates a project optimized for learning:
# - Emphasis on documentation
# - Example code organization
# - Progress tracking by concepts
```

### Learning Session

```
You: I want to learn Svelte. Can you help me understand the basics and create some examples?

Claude: I'll help you learn Svelte step by step. Let me create a structured learning path with examples.

[Creates example files with extensive comments]
[Builds progressively complex examples]
[Documents key concepts in project file]
```

### Project Evolution

The project file becomes a learning resource:

```markdown
# Learn and document Svelte framework

## Concepts Learned

### ✅ Day 1: Basics
- Component structure
- Reactive declarations ($:)
- Props and events
- [Example: TodoList component]

### ✅ Day 2: Advanced Features
- Stores (writable, readable, derived)
- Transitions and animations
- Slot composition
- [Example: Modal system]

### 🔄 Day 3: Real App
- SvelteKit setup
- Routing
- Server-side rendering
- [Example: Blog platform]

## Key Insights
- Svelte compiles away, no runtime
- Reactive statements are powerful
- Less boilerplate than React
- Built-in transitions are smooth

## Resources Created
- `/examples/basics/` - First components
- `/examples/stores/` - State management
- `/examples/sveltekit-blog/` - Full app
```

## Workflow 6: Team Collaboration

### Scenario
Working on a feature with team members.

### Shared Project Setup

```bash
# Create project with team metadata
claude-project new "Implement real-time chat" --github --team

# Export for team member
claude-project export proj-* --with-github > chat-project.json

# Team member imports
claude-project import chat-project.json
```

### Collaborative Development

```bash
# Your session:
# Implement WebSocket connection
# Create message components
claude-project checkpoint --message "WebSocket foundation complete"

# Team member continues:
claude-project continue proj-*
# Sees your progress and context
# Implements UI components

# Sync progress
claude-project sync
```

### Integration

```bash
# Both push to feature branch
git push origin feature/real-time-chat

# Project summary for PR
claude-project summary --all-sessions > pr-summary.md

# Shows:
# - Total time: 8 hours (You: 5h, Team: 3h)
# - Sessions: 5
# - Complete implementation
```

## Advanced Patterns

### Pattern 1: Project Templates

```bash
# Create custom template
cat > ~/.claude/templates/api.md << 'EOF'
---
tags: [api, backend]
context_files: [src/api/**, tests/api/**]
---

# {{ name }}

## API Endpoints
- [ ] GET /api/resource
- [ ] POST /api/resource
- [ ] PUT /api/resource/:id
- [ ] DELETE /api/resource/:id

## Implementation Plan
1. Define schemas
2. Create routes
3. Add middleware
4. Write tests
5. Document API
EOF

# Use template
claude-project new "User API" --template api
```

### Pattern 2: Bulk Operations

```bash
# Archive completed projects
claude-project list --status completed | while read proj; do
  claude-project archive "$proj" --close-issue
done

# Sync all active projects
claude-project sync --all

# Generate team report
claude-project report --format markdown > team-report.md
```

### Pattern 3: Integration Chains

```bash
# Full automation
claude-project new "Feature X" \
  --github \
  --branch feature/x \
  --milestone v2.0 \
  --assign @teammate

# Creates:
# - Project with tracking
# - GitHub issue with milestone
# - Feature branch
# - Assignment notification
```

## Tips and Best Practices

### 1. Checkpoint Frequency
- After completing logical units of work
- Before context switches
- At natural break points
- End of each session

### 2. Context Quality
- Use descriptive goals
- Update focus area when switching tasks
- Include relevant files in context_files
- Document decisions in progress log

### 3. Git Integration
- Commit messages reference issues
- Checkpoints create meaningful commits
- Use branches for features
- Regular pushes for backup

### 4. Team Collaboration
- Export/import for handoffs
- Consistent project naming
- Regular synchronization
- Clear session summaries

### 5. Long-Running Projects
- Break into milestones
- Regular status reviews
- Archive completed phases
- Maintain momentum with goals