# Context API Documentation

The Context API is an intelligent system that analyzes your work with Claude and maintains contextual awareness across sessions.

## Overview

The Context API:
- Analyzes conversation transcripts in real-time
- Extracts current goals and focus areas
- Updates project files with context
- Maintains state between hook invocations
- Can use local analysis or Anthropic API

## Architecture

```
Claude Session
    ↓
Transcript Updates
    ↓
Context Analyzer Hook (every 5 actions)
    ↓
Analysis Engine (Local/API)
    ↓
Project Context Update
    ↓
State Persistence
```

## Core Components

### 1. Context Analyzer Hook

**Location**: `~/.claude/hooks/claude-project-context-analyzer.py`

**Key Features**:
- Monitors tool usage (Edit, Write, Bash, Task)
- Triggers analysis every N actions (default: 5)
- Updates active project with context
- Maintains state between invocations

### 2. Analysis Modes

#### Local Analysis Mode
- Fast, privacy-preserving
- Pattern-based extraction
- No external API calls
- Suitable for most use cases

#### API Analysis Mode
- Uses Anthropic Claude API
- More sophisticated understanding
- Requires API key
- Better for complex projects

### 3. State Management

**State File**: `.context_analyzer_state.json`

```json
{
  "action_count": 12,
  "last_analysis": "2024-01-15T10:30:00",
  "last_processed_index": 45,
  "project_contexts": {
    "proj-123": {
      "last_goal": "Implement authentication",
      "last_focus": "JWT token validation",
      "last_update": "2024-01-15T10:30:00"
    }
  }
}
```

## Configuration

### Environment Variables

```bash
# Analysis mode: 'local' or 'api'
export CONTEXT_ANALYSIS_MODE=local

# API key (required for API mode)
export ANTHROPIC_API_KEY=sk-ant-...

# Update frequency (default: 5 actions)
export CONTEXT_UPDATE_FREQUENCY=5

# Enable debug logging
export CONTEXT_ANALYZER_DEBUG=1
```

### Hook Configuration

```json
{
  "PostToolUse": [
    {
      "name": "Context Analyzer",
      "script": "~/.claude/hooks/claude-project-context-analyzer.py",
      "args": ["--transcript", "{transcript_path}"],
      "timeout": 5000,
      "enabled": true
    }
  ]
}
```

## How It Works

### 1. Action Tracking

The analyzer tracks "meaningful actions":
- **Edit**: File modifications
- **Write**: New file creation
- **Bash**: Command execution
- **Task**: Complex operations

### 2. Context Extraction

#### Local Analysis
```python
def extract_context_local(messages):
    """Extract context using pattern matching"""
    
    # Analyze recent file operations
    edited_files = []
    for msg in messages[-10:]:
        for tool_use in get_tool_uses(msg):
            if tool_use['name'] in ['Edit', 'Write']:
                edited_files.append(tool_use['input']['file_path'])
    
    # Determine focus from file patterns
    if any('auth' in f for f in edited_files):
        focus = "Authentication implementation"
    elif any('test' in f for f in edited_files):
        focus = "Test development"
    else:
        focus = "General development"
    
    # Extract goal from bash commands
    commands = extract_bash_commands(messages)
    if 'npm test' in commands:
        goal = "Ensuring tests pass"
    elif 'git commit' in commands:
        goal = "Committing changes"
    else:
        goal = "Development work"
    
    return {
        'current_goal': goal,
        'focus_area': focus,
        'recent_files': edited_files[-5:]
    }
```

#### API Analysis
```python
def extract_context_api(messages):
    """Extract context using Claude API"""
    
    # Prepare conversation for analysis
    conversation = format_messages_for_api(messages[-20:])
    
    # Query Claude for context
    response = anthropic.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": f"""Analyze this conversation and extract:
            1. Current goal (one line)
            2. Current focus area (one line)
            3. Key context points (2-3 bullets)
            
            Conversation:
            {conversation}
            """
        }]
    )
    
    return parse_api_response(response)
```

### 3. Project Update

The analyzer updates the active project file:

```markdown
## Context
**Current Goal**: Implement user authentication with JWT tokens
**Focus Area**: Token validation and refresh logic
**Last Updated**: 2024-01-15 10:30:00

### Recent Activity
- Modified `/src/auth/jwt.js` - Added token validation
- Created `/src/auth/middleware.js` - Auth middleware
- Ran tests for authentication module

### Git Changes
```diff
+ function validateToken(token) {
+   // Token validation logic
+ }
```
```

### 4. State Persistence

State is preserved between hook invocations:

```python
class ContextState:
    def __init__(self):
        self.state_file = Path.home() / '.claude' / '.context_analyzer_state.json'
        self.state = self.load_state()
    
    def should_analyze(self, project_id):
        """Check if analysis is needed"""
        action_count = self.state.get('action_count', 0)
        return action_count >= CONTEXT_UPDATE_FREQUENCY
    
    def update_project_context(self, project_id, context):
        """Update project-specific context"""
        if 'project_contexts' not in self.state:
            self.state['project_contexts'] = {}
        
        self.state['project_contexts'][project_id] = {
            'last_goal': context['current_goal'],
            'last_focus': context['focus_area'],
            'last_update': datetime.now().isoformat()
        }
        self.save_state()
```

## Integration Examples

### 1. With Project System

```python
# Get active project
project = get_active_project()
if not project:
    return

# Extract context
context = extract_context(transcript)

# Update project file
update_project_context(project['id'], context)

# Trigger checkpoint if significant
if is_significant_change(context):
    subprocess.run(['claude-project', 'checkpoint'])
```

### 2. With Git Integration

```python
# Get git diff for context
git_diff = get_recent_git_diff()

# Include in context
context['git_changes'] = git_diff

# Add to project update
if git_diff:
    context['change_summary'] = summarize_changes(git_diff)
```

### 3. With External Services

```python
# Update Linear ticket
if project.get('linear_ticket'):
    update_linear_comment(
        project['linear_ticket'],
        f"Context Update: {context['current_goal']}"
    )

# Send Slack notification
if significant_milestone_reached(context):
    notify_slack(f"Milestone: {context['current_goal']}")
```

## Advanced Features

### 1. Smart Context Merging

```python
def merge_contexts(old_context, new_context):
    """Intelligently merge contexts"""
    
    # Keep goal if still relevant
    if is_goal_still_relevant(old_context['goal'], new_context):
        merged_goal = old_context['goal']
    else:
        merged_goal = new_context['current_goal']
    
    # Combine focus areas
    merged_focus = combine_focus_areas(
        old_context.get('focus'),
        new_context['focus_area']
    )
    
    return {
        'current_goal': merged_goal,
        'focus_area': merged_focus,
        'previous_goal': old_context.get('goal')
    }
```

### 2. Context History

```python
def maintain_context_history(project_id, context):
    """Keep history of context changes"""
    
    history_file = Path.home() / '.claude' / 'context_history' / f"{project_id}.json"
    
    history = []
    if history_file.exists():
        history = json.loads(history_file.read_text())
    
    history.append({
        'timestamp': datetime.now().isoformat(),
        'context': context
    })
    
    # Keep last 50 entries
    history = history[-50:]
    
    history_file.parent.mkdir(exist_ok=True)
    history_file.write_text(json.dumps(history, indent=2))
```

### 3. Context Triggers

```python
CONTEXT_TRIGGERS = {
    'test_failure': lambda ctx: 'test' in ctx['focus_area'] and 'failing' in ctx['current_goal'],
    'major_refactor': lambda ctx: 'refactor' in ctx['current_goal'].lower(),
    'new_feature': lambda ctx: 'implement' in ctx['current_goal'] or 'add' in ctx['current_goal'],
    'bug_fix': lambda ctx: 'fix' in ctx['current_goal'] or 'bug' in ctx['focus_area']
}

def check_triggers(context):
    """Check if any special triggers are met"""
    
    for trigger_name, condition in CONTEXT_TRIGGERS.items():
        if condition(context):
            handle_trigger(trigger_name, context)
```

## API Reference

### Command Line Usage

```bash
# Test the analyzer
~/.claude/hooks/claude-project-context-analyzer.py --test

# Analyze specific transcript
~/.claude/hooks/claude-project-context-analyzer.py --transcript /path/to/transcript.json

# Force analysis (ignore frequency)
~/.claude/hooks/claude-project-context-analyzer.py --force --transcript /path/to/transcript.json

# Debug mode
CONTEXT_ANALYZER_DEBUG=1 ~/.claude/hooks/claude-project-context-analyzer.py --transcript /path/to/transcript.json
```

### Python API

```python
from claude_context import ContextAnalyzer

# Initialize analyzer
analyzer = ContextAnalyzer(mode='local')

# Analyze transcript
context = analyzer.analyze_transcript(transcript_path)

# Update project
analyzer.update_project_context(project_id, context)

# Get context history
history = analyzer.get_context_history(project_id)
```

## Best Practices

### 1. Frequency Tuning
- Default 5 actions works well for most projects
- Increase for long-running tasks
- Decrease for rapid prototyping

### 2. Context Quality
- Use API mode for complex projects
- Local mode for privacy/speed
- Hybrid approach possible

### 3. State Management
- Don't delete state file during sessions
- Backup state periodically
- Reset state if corrupted

### 4. Performance
- Keep transcript analysis window reasonable (last 20-50 messages)
- Cache analysis results when possible
- Use async processing for API calls

## Troubleshooting

### Context Not Updating

1. Check action count in state file
2. Verify hook is enabled and running
3. Look for errors in logs
4. Test with `--force` flag

### Incorrect Context

1. Increase analysis window
2. Switch to API mode for better accuracy
3. Check for conflicting goals in transcript
4. Manually correct and save

### Performance Issues

1. Reduce update frequency
2. Use local mode instead of API
3. Limit transcript analysis window
4. Check for state file growth

### API Errors

1. Verify API key is set
2. Check API rate limits
3. Fall back to local mode
4. Check network connectivity