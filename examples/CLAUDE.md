# Claude Environment Instructions Example

This is an example CLAUDE.md file that demonstrates how to configure Claude's behavior for your projects.

## Project Tracking

You have a project management system installed. Use these commands:

- `claude-project new "Project Name"` - Create new project
- `claude-project list` - Show active projects  
- `claude-project checkpoint` - Save progress
- `claude-project continue <id>` - Resume work

IMPORTANT: Always create or continue a project when starting work.

## Code Style Guidelines

### Python
- Use type hints for all functions
- Follow PEP 8 style guide
- Prefer f-strings over .format()
- Use `pathlib` for file operations

### JavaScript/TypeScript
- Use TypeScript when possible
- Prefer const over let
- Use async/await over promises
- Follow Airbnb style guide

### Git Commits
- Use conventional commits: feat:, fix:, docs:, etc.
- Keep commits atomic and focused
- Write clear, imperative mood messages

## Project Structure

All GitHub projects MUST be created in:
- Personal: `~/Documents/GitHub/[project-name]/`
- Work: `~/Documents/GitHub/[company]/[project-name]/`

## Testing Requirements

- Write tests for all new functions
- Maintain >80% code coverage
- Run tests before committing
- Use pytest for Python, Jest for JS

## Security

- Never commit secrets or API keys
- Use environment variables for sensitive data
- The secrets detector hook will warn you

## Hooks Active

The following hooks are monitoring your work:
1. **Context Analyzer** - Tracks project progress
2. **Secrets Detector** - Prevents credential leaks
3. **Git Location Enforcer** - Ensures proper project placement

## Communication Style

- Be concise and direct
- Explain complex changes
- Ask for clarification when needed
- Suggest improvements when you see them

## Remember

- Quality over speed
- Test everything
- Document as you go
- Ask if unsure