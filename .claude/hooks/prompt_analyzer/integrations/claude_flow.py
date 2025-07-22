"""
Claude Flow integration for memory and command execution
"""

import subprocess
import json
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path


class ClaudeFlowIntegration:
    """Enhanced integration with claude-flow commands"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.claude_flow_cmd = ["npx", "claude-flow@alpha"]
    
    def run_command(self, cmd: List[str], capture_output: bool = True) -> Tuple[int, str, str]:
        """Run claude-flow command and return exit code, stdout, stderr"""
        try:
            result = subprocess.run(
                cmd, 
                capture_output=capture_output, 
                text=True, 
                timeout=self.timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", f"Command timed out after {self.timeout} seconds"
        except Exception as e:
            return 1, "", str(e)
    
    def memory_store(self, key: str, value: str, ttl: Optional[int] = None, 
                    namespace: Optional[str] = None) -> bool:
        """Store value in claude-flow memory"""
        cmd = self.claude_flow_cmd + ["memory", "store", key, value]
        if ttl:
            cmd.extend(["--ttl", str(ttl)])
        if namespace:
            cmd.extend(["--namespace", namespace])
        exit_code, _, _ = self.run_command(cmd)
        return exit_code == 0
    
    def memory_query(self, pattern: str, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query values from claude-flow memory"""
        cmd = self.claude_flow_cmd + ["memory", "query", pattern]
        if namespace:
            cmd.extend(["--namespace", namespace])
        
        exit_code, stdout, _ = self.run_command(cmd)
        if exit_code == 0 and stdout:
            entries = []
            for line in stdout.strip().split('\n'):
                if line.startswith('{'):
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
            return entries
        return []
    
    def memory_get(self, key: str, namespace: Optional[str] = None) -> Optional[str]:
        """Get a specific value from memory"""
        entries = self.memory_query(key, namespace)
        if entries and len(entries) > 0:
            return entries[0].get("value")
        return None
    
    def hive_mind_spawn(self, objective: str, queen_type: str = "adaptive", 
                       max_workers: int = 8, consensus: str = "weighted") -> bool:
        """Spawn hive mind swarm for complex tasks"""
        cmd = self.claude_flow_cmd + [
            "hive-mind", "spawn", objective,
            "--queen-type", queen_type,
            "--max-workers", str(max_workers),
            "--consensus", consensus,
            "--auto-scale"
        ]
        exit_code, _, _ = self.run_command(cmd)
        return exit_code == 0
    
    def swarm_init(self, topology: str = "mesh", max_agents: int = 5, 
                  strategy: str = "adaptive") -> bool:
        """Initialize swarm with specified topology"""
        cmd = self.claude_flow_cmd + [
            "coordination", "swarm-init",
            "--topology", topology,
            "--max-agents", str(max_agents),
            "--strategy", strategy
        ]
        exit_code, _, _ = self.run_command(cmd)
        return exit_code == 0
    
    def agent_spawn(self, agent_type: str, name: str, 
                   capabilities: str = "task-specific") -> bool:
        """Spawn a new agent"""
        cmd = self.claude_flow_cmd + [
            "coordination", "agent-spawn",
            "--type", agent_type,
            "--name", name,
            "--capabilities", capabilities
        ]
        exit_code, _, _ = self.run_command(cmd)
        return exit_code == 0
    
    def analyze_bottleneck(self, scope: str = "system", 
                          target: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Analyze performance bottlenecks"""
        cmd = self.claude_flow_cmd + [
            "analysis", "bottleneck-detect",
            "--scope", scope
        ]
        if target:
            cmd.extend(["--target", target])
        
        exit_code, stdout, _ = self.run_command(cmd)
        if exit_code == 0 and stdout:
            try:
                return json.loads(stdout)
            except json.JSONDecodeError:
                return None
        return None
    
    def get_session_info(self) -> Optional[Dict[str, Any]]:
        """Get current session information"""
        session_file = Path.home() / ".claude" / "active_session.json"
        if session_file.exists():
            try:
                with open(session_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return None
    
    def create_session(self, session_id: str) -> bool:
        """Create a new session"""
        # Initialize memory namespace for the session
        return self.memory_store(
            "session_initialized",
            datetime.now().isoformat(),
            namespace=f"claude-conversation-{session_id}"
        )