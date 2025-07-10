# Troubleshooting Guide

This guide helps resolve common issues with the Claude Environment system.

## Installation Issues

### Command Not Found: claude-project

**Problem**: After installation, `claude-project` command is not recognized.

**Solutions**:
1. Ensure ~/bin is in your PATH:
   ```bash
   echo $PATH | grep -q "$HOME/bin" || echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

2. Check if script exists and is executable:
   ```bash
   ls -la ~/bin/claude-project
   # If missing:
   cp ~/.claude-environment/scripts/claude-project ~/bin/
   chmod +x ~/bin/claude-project
   ```

3. Reload your shell:
   ```bash
   exec $SHELL
   ```

### Permission Denied Errors

**Problem**: Getting permission errors when running scripts or hooks.

**Solution**:
```bash
# Fix script permissions
chmod +x ~/bin/claude-project
chmod +x ~/.claude/hooks/*.py
chmod +x ~/.claude/hooks/*.sh

# Fix directory permissions
chmod 755 ~/.claude
chmod -R 755 ~/.claude/projects
```

## Hook Issues

### Hooks Not Running

**Problem**: Hooks aren't triggered during Claude sessions.

**Solutions**:

1. **Check Claude Desktop Configuration**:
   - Open Claude Desktop settings
   - Go to Developer → Hooks
   - Verify hooks are configured correctly

2. **Test Hooks Manually**:
   ```bash
   # Test context analyzer
   echo '{"tool_name":"Edit","tool_input":{"file_path":"test.py"}}' | \
   python3 ~/.claude/hooks/claude-project-context-analyzer.py
   
   # Check for errors
   cat ~/.claude/context_analyzer_errors.log
   ```

3. **Verify Python Environment**:
   ```bash
   # Check Python version
   python3 --version  # Should be 3.8+
   
   # Test imports
   python3 -c "import json, sys, pathlib"
   ```

### Context Analyzer Not Updating Projects

**Problem**: Project files aren't being updated with context.

**Solutions**:

1. **Check State File**:
   ```bash
   cat ~/.claude/.context_analyzer_state.json
   # Reset if corrupted:
   rm ~/.claude/.context_analyzer_state.json
   ```

2. **Verify Active Project Exists**:
   ```bash
   ls ~/.claude/projects/active/
   # Create one if missing:
   claude-project new "Test Project"
   ```

3. **Enable Debug Logging**:
   ```bash
   # Check debug log
   tail -f ~/.claude/context_analyzer_debug.log
   ```

4. **API Mode Issues** (if using):
   ```bash
   # Test API key
   export ANTHROPIC_API_KEY="your-key"
   python3 -c "import os; print('API Key set' if os.getenv('ANTHROPIC_API_KEY') else 'No API key')"
   ```

### Secrets Detector False Positives

**Problem**: Getting warnings for non-secret strings.

**Solutions**:
1. Use placeholders in examples:
   ```
   api_key = "<your-api-key-here>"
   token = "${API_TOKEN}"
   ```

2. Add to .gitignore if real secrets:
   ```bash
   echo ".env" >> .gitignore
   echo "config/secrets.json" >> .gitignore
   ```

## Project Management Issues

### Projects Not Saving

**Problem**: Project changes aren't persisting.

**Solutions**:

1. **Check Git Repository**:
   ```bash
   cd ~/.claude
   git status
   # If not initialized:
   git init
   git add .
   git commit -m "Initial setup"
   ```

2. **Manual Checkpoint**:
   ```bash
   claude-project checkpoint
   ```

3. **Fix Git Issues**:
   ```bash
   cd ~/.claude
   git config user.email "you@example.com"
   git config user.name "Your Name"
   ```

### Can't Find Project

**Problem**: `claude-project continue` can't find your project.

**Solutions**:

1. **List All Projects**:
   ```bash
   claude-project list
   # Also check archived:
   ls ~/.claude/projects/archived/
   ```

2. **Search by Partial ID**:
   ```bash
   # If you remember part of the ID
   ls ~/.claude/projects/active/*partial-id*
   ```

3. **Restore from Trash**:
   ```bash
   ls ~/.claude/projects/.trash/
   # Move back to active:
   mv ~/.claude/projects/.trash/proj-* ~/.claude/projects/active/
   ```

## GitHub Integration Issues

### Can't Create Issues

**Problem**: GitHub issue creation fails.

**Solutions**:

1. **Verify GitHub CLI Auth**:
   ```bash
   gh auth status
   # Re-authenticate if needed:
   gh auth login
   ```

2. **Check Repository Access**:
   ```bash
   gh repo view
   # Test issue creation:
   gh issue create --title "Test" --body "Test issue"
   ```

3. **Specify Repository**:
   ```bash
   # If not in a git repo:
   cd ~/Documents/GitHub/your-repo
   claude-project new "Project Name"
   ```

### Sync Not Working

**Problem**: Project progress not syncing to GitHub.

**Solutions**:

1. **Check Issue Link**:
   ```bash
   # Verify project has issue linked
   claude-project status
   # Link manually if missing:
   claude-project link github proj-id issue-number
   ```

2. **Test Sync Manually**:
   ```bash
   claude-project sync proj-id
   ```

3. **Check Rate Limits**:
   ```bash
   gh api rate_limit
   ```

## Performance Issues

### Slow Hook Execution

**Problem**: Hooks causing delays in Claude operations.

**Solutions**:

1. **Disable Non-Essential Hooks**:
   Edit `~/.claude/hooks_config.json`:
   ```json
   {
     "enabled": false
   }
   ```

2. **Increase Analysis Threshold**:
   ```bash
   # In config.yaml
   context_analysis:
     threshold: 10  # Increase from 5
   ```

3. **Use Local Analysis Mode**:
   ```bash
   # Disable API calls
   export CONTEXT_ANALYSIS_MODE=local
   ```

## Common Error Messages

### "Not in a git repository"

**Context**: When running `claude-project install-hooks`

**Solution**:
```bash
cd /path/to/your/project
git init
claude-project install-hooks
```

### "Project not found"

**Context**: When using project commands

**Solution**:
```bash
# Use correct project ID format
claude-project continue proj-1234567890
# Not just: claude-project continue 1234567890
```

### "Could not create GitHub issue"

**Common Causes**:
- Not authenticated with gh
- No repository in current directory
- No permissions to create issues
- API rate limit exceeded

## Debug Mode

Enable comprehensive debugging:

```bash
# Set environment variables
export CLAUDE_DEBUG=1
export CONTEXT_ANALYZER_DEBUG=1

# Check all logs
tail -f ~/.claude/logs/*.log

# Test specific component
~/.claude/hooks/claude-project-context-analyzer.py --test
```

## Recovery Procedures

### Reset Everything

**Last Resort - Back up first!**
```bash
# Backup current setup
cp -r ~/.claude ~/.claude.backup

# Reset to clean state
rm -rf ~/.claude
./install.sh

# Restore projects only
cp -r ~/.claude.backup/projects ~/.claude/
```

### Restore from Git Backup

```bash
cd ~/.claude
git log --oneline | head -20  # Find good commit
git checkout <commit-hash> -- projects/
```

## Getting Help

1. **Check Logs**:
   ```bash
   ls ~/.claude/logs/
   tail -f ~/.claude/logs/hooks.log
   ```

2. **Run Diagnostics**:
   ```bash
   # Create diagnostic script
   ~/.claude/scripts/diagnose.sh
   ```

3. **Report Issues**:
   - Include error messages
   - Share relevant log files
   - Describe what you were doing
   - System information (OS, shell, Python version)

## Preventive Measures

1. **Regular Backups**:
   ```bash
   # Add to crontab
   0 */6 * * * cd ~/.claude && git add -A && git commit -m "Backup" && git push
   ```

2. **Monitor Disk Space**:
   ```bash
   du -sh ~/.claude/*
   ```

3. **Clean Old Files**:
   ```bash
   # Remove old transcripts
   find ~/.claude/transcripts -mtime +30 -delete
   ```

4. **Update Regularly**:
   ```bash
   cd ~/Documents/GitHub/claude-environment
   git pull
   ./install.sh --update
   ```