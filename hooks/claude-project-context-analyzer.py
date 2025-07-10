#!/usr/bin/env python3
"""
Claude Project Context Analyzer
Uses Claude to analyze actual work context and maintain intelligent project tracking
"""

import json
import sys
import os
import subprocess
from datetime import datetime
from pathlib import Path
import tempfile
import urllib.request
import urllib.error

# Configuration
ANALYSIS_THRESHOLD = 5  # Analyze context every N meaningful actions
PROJECTS_DIR = Path.home() / ".claude" / "projects"
ACTIVE_DIR = PROJECTS_DIR / "active"
TRANSCRIPT_DIR = PROJECTS_DIR / "transcripts"
STATE_FILE = PROJECTS_DIR / ".context_analyzer_state.json"

class ClaudeContextAnalyzer:
    def __init__(self):
        self.state = self.load_state()
        self.ensure_directories()
        self.transcript_path = None
        
    def ensure_directories(self):
        """Ensure all directories exist"""
        ACTIVE_DIR.mkdir(parents=True, exist_ok=True)
        TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
        
    def load_state(self):
        """Load state from file"""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "action_count": 0,
            "current_project": None,
            "session_id": None,
            "last_analysis": None,
            "context_cache": []
        }
    
    def save_state(self):
        """Save state to file"""
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def get_transcript_content(self, transcript_path):
        """Read recent transcript content"""
        if not transcript_path or not Path(transcript_path).exists():
            return None
            
        try:
            with open(transcript_path, 'r') as f:
                lines = f.readlines()
                
            # Get last N meaningful interactions
            recent_content = []
            for line in lines[-50:]:  # Last 50 entries
                try:
                    entry = json.loads(line)
                    # Filter for meaningful content
                    if entry.get("type") in ["user_message", "assistant_message", "tool_use"]:
                        recent_content.append(entry)
                except:
                    continue
                    
            return recent_content
        except:
            return None
    
    def create_analysis_prompt(self, transcript_content, tool_data):
        """Create a prompt for Claude to analyze the context"""
        prompt = """Analyze this recent Claude Code session and provide a concise context summary.

Recent activity:
"""
        
        # Add transcript content
        for entry in transcript_content[-10:]:  # Last 10 interactions
            if entry.get("type") == "user_message":
                prompt += f"\nUser: {entry.get('content', '')[:200]}..."
            elif entry.get("type") == "assistant_message":
                prompt += f"\nAssistant: {entry.get('content', '')[:200]}..."
            elif entry.get("type") == "tool_use":
                tool_name = entry.get("tool_name", "")
                if tool_name in ["Edit", "Write", "MultiEdit"]:
                    prompt += f"\nTool: {tool_name} on {entry.get('tool_input', {}).get('file_path', 'unknown')}"
                elif tool_name == "Bash":
                    prompt += f"\nTool: Executed `{entry.get('tool_input', {}).get('command', '')}`"
        
        prompt += """

Current action: """ + json.dumps(tool_data, indent=2)[:500] + """

Based on this context, provide a brief summary (2-3 sentences) that captures:
1. What the user is trying to accomplish
2. The current focus area (e.g., "implementing authentication", "fixing test failures", "refactoring API")
3. Key files or systems being modified

Format your response as:
GOAL: [one sentence describing the overall objective]
FOCUS: [current specific task or area]
CONTEXT: [relevant details about approach or changes]

Keep it concise and actionable. Don't include pleasantries or meta-commentary."""
        
        return prompt
    
    def analyze_with_claude(self, transcript_content, tool_data):
        """Use Claude to analyze the context"""
        # Check for API key in environment or config
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            # Try to read from Claude config
            config_file = Path.home() / '.claude' / 'claude_api.json'
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                        api_key = config.get('api_key')
                except:
                    pass
        
        if not api_key:
            # Fall back to simpler local analysis
            return self.simple_context_analysis(transcript_content, tool_data)
        
        prompt = self.create_analysis_prompt(transcript_content, tool_data)
        
        try:
            req_data = json.dumps({
                'model': 'claude-3-haiku-20240307',  # Fast, cheap model for analysis
                'max_tokens': 300,
                'messages': [{
                    'role': 'user',
                    'content': prompt
                }],
                'temperature': 0.3
            }).encode('utf-8')
            
            req = urllib.request.Request(
                'https://api.anthropic.com/v1/messages',
                data=req_data,
                headers={
                    'x-api-key': api_key,
                    'anthropic-version': '2023-06-01',
                    'content-type': 'application/json'
                }
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    result = json.loads(response.read().decode('utf-8'))
                    return result['content'][0]['text'].strip()
                else:
                    return self.simple_context_analysis(transcript_content, tool_data)
                
        except Exception as e:
            # Fall back to simple analysis
            return self.simple_context_analysis(transcript_content, tool_data)
    
    def simple_context_analysis(self, transcript_content, tool_data):
        """Simple context analysis without Claude API"""
        # Analyze recent actions
        recent_files = set()
        recent_commands = []
        user_goals = []
        
        for entry in transcript_content[-20:]:
            if entry.get("type") == "user_message":
                content = entry.get("content", "").lower()
                # Extract intent keywords
                if any(kw in content for kw in ["implement", "create", "build", "add"]):
                    user_goals.append("implementing new features")
                elif any(kw in content for kw in ["fix", "debug", "error", "issue"]):
                    user_goals.append("fixing issues")
                elif any(kw in content for kw in ["refactor", "improve", "optimize"]):
                    user_goals.append("refactoring code")
                elif any(kw in content for kw in ["test", "verify", "check"]):
                    user_goals.append("testing")
                    
            elif entry.get("type") == "tool_use":
                tool_input = entry.get("tool_input", {})
                if "file_path" in tool_input:
                    recent_files.add(tool_input["file_path"])
                if "command" in tool_input:
                    recent_commands.append(tool_input["command"])
        
        # Determine focus from files
        focus = "general development"
        if recent_files:
            file_list = list(recent_files)
            if any("test" in f for f in file_list):
                focus = "working on tests"
            elif any("component" in f for f in file_list):
                focus = "UI component development"
            elif any("api" in f or "route" in f for f in file_list):
                focus = "API development"
            elif any("hook" in f for f in file_list):
                focus = "hooks/automation development"
        
        # Build analysis
        goal = user_goals[0] if user_goals else "working on project"
        context_parts = []
        
        if recent_files:
            context_parts.append(f"modifying {len(recent_files)} files")
        if any("npm" in cmd for cmd in recent_commands):
            context_parts.append("managing dependencies")
        if any("git" in cmd for cmd in recent_commands):
            context_parts.append("version control operations")
            
        context = ", ".join(context_parts) if context_parts else "making code changes"
        
        return f"GOAL: Currently {goal}\nFOCUS: {focus}\nCONTEXT: Activity includes {context}"
    
    def extract_git_context(self):
        """Extract context from git if available"""
        try:
            # Check if in git repo
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return None
                
            # Get recent changes
            diff_result = subprocess.run(
                ["git", "diff", "--stat", "--cached"],
                capture_output=True,
                text=True
            )
            
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True
            )
            
            return {
                "staged_changes": diff_result.stdout,
                "working_changes": status_result.stdout
            }
        except:
            return None
    
    def update_project_with_analysis(self, project_path, analysis):
        """Update project file with Claude's analysis"""
        if not analysis:
            return
            
        # Read current project
        with open(project_path, 'r') as f:
            content = f.read()
        
        # Ensure Context section exists
        if "## Context & Progress" not in content:
            if "## Progress Log" in content:
                content = content.replace("## Progress Log", "## Context & Progress")
            else:
                content += "\n\n## Context & Progress\n"
        
        # Parse Claude's analysis
        lines = analysis.split('\n')
        goal = ""
        focus = ""
        context = ""
        
        for line in lines:
            if line.startswith("GOAL:"):
                goal = line[5:].strip()
            elif line.startswith("FOCUS:"):
                focus = line[6:].strip()
            elif line.startswith("CONTEXT:"):
                context = line[8:].strip()
        
        # Create entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = f"\n### {timestamp}\n"
        
        if goal:
            entry += f"**Goal:** {goal}\n"
        if focus:
            entry += f"**Current Focus:** {focus}\n"
        if context:
            entry += f"**Context:** {context}\n"
            
        # Add git context if available
        git_context = self.extract_git_context()
        if git_context and git_context["working_changes"]:
            entry += f"\n**Files in progress:**\n```\n{git_context['working_changes']}```\n"
        
        # Insert after header
        insert_pos = content.find("## Context & Progress") + len("## Context & Progress\n")
        content = content[:insert_pos] + entry + content[insert_pos:]
        
        # Write back
        with open(project_path, 'w') as f:
            f.write(content)
    
    def get_active_project(self):
        """Get or create active project"""
        if self.state["current_project"]:
            project = Path(self.state["current_project"])
            if project.exists():
                return project
                
        # Find most recent
        projects = list(ACTIVE_DIR.glob("proj-*.md"))
        if projects:
            project = max(projects, key=lambda p: p.stat().st_mtime)
            self.state["current_project"] = str(project)
            return project
            
        return None
    
    def should_analyze(self, tool_data):
        """Determine if we should run analysis"""
        tool_name = tool_data.get("tool_name", "")
        
        # Always count meaningful tools
        if tool_name in ["Edit", "MultiEdit", "Write", "Bash", "Task"]:
            self.state["action_count"] += 1
            
        # Analyze at threshold
        if self.state["action_count"] >= ANALYSIS_THRESHOLD:
            self.state["action_count"] = 0
            return True
            
        # Analyze on significant events
        if tool_name == "Task":  # Major research/analysis completed
            return True
            
        if tool_name == "Bash":
            command = tool_data.get("tool_input", {}).get("command", "")
            if any(kw in command for kw in ["git commit", "npm test", "npm run build"]):
                return True
                
        return False
    
    def process_tool_use(self, tool_data):
        """Process tool use and potentially analyze context"""
        # Get transcript path from input
        input_data = tool_data
        self.transcript_path = input_data.get("transcript_path")
        session_id = input_data.get("session_id")
        
        # Debug log
        debug_log = Path.home() / ".claude" / "context_analyzer_debug.log"
        with open(debug_log, 'a') as f:
            f.write(f"\n{datetime.now().isoformat()} - Processing tool: {input_data.get('tool_name')}\n")
            f.write(f"  Transcript path: {self.transcript_path}\n")
            f.write(f"  Session ID: {session_id}\n")
            f.write(f"  Action count: {self.state['action_count']}\n")
        
        if session_id:
            self.state["session_id"] = session_id
            
        # Check if we should analyze
        if self.should_analyze(tool_data):
            # Get transcript content
            transcript_content = self.get_transcript_content(self.transcript_path)
            if transcript_content:
                # Run Claude analysis
                analysis = self.analyze_with_claude(transcript_content, tool_data)
                
                if analysis:
                    # Update project
                    project = self.get_active_project()
                    if project:
                        self.update_project_with_analysis(project, analysis)
                        self.state["last_analysis"] = datetime.now().isoformat()
        
        # Save state
        self.save_state()

def main():
    try:
        input_data = json.load(sys.stdin)
        analyzer = ClaudeContextAnalyzer()
        analyzer.process_tool_use(input_data)
        sys.exit(0)
    except Exception as e:
        # Log errors
        error_log = Path.home() / ".claude" / "context_analyzer_errors.log"
        with open(error_log, 'a') as f:
            f.write(f"{datetime.now().isoformat()} - Error: {str(e)}\n")
            import traceback
            f.write(traceback.format_exc())
        sys.exit(0)

if __name__ == "__main__":
    main()