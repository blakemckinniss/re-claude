#!/usr/bin/env python3
"""
Enhanced Claude Code UserPromptSubmit Hook - Main Entry Point
Uses the modular prompt analyzer package
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from prompt_analyzer import PromptAnalyzer
from prompt_analyzer.utils.config import Config, load_dotenv


def main():
    """Main entry point for the hook"""
    input_data = {}  # Initialize to avoid unbound variable
    try:
        # Load environment variables
        script_dir = Path(__file__).parent
        env_path = script_dir / '.env'
        if env_path.exists():
            load_dotenv(str(env_path))
        
        # Read input from stdin (Claude Code hook format)
        input_data = json.load(sys.stdin)
        
        # Extract user prompt - UserPromptSubmit hook provides it as 'prompt'
        user_prompt = input_data.get('prompt', '')
        session_id = input_data.get('session_id', '')
        
        if not user_prompt or len(user_prompt.strip()) < 3:
            # Too short to analyze meaningfully - just pass through
            sys.exit(0)
        
        # Load configuration
        config = Config.from_env()
        
        # Create analyzer
        analyzer = PromptAnalyzer(config)
        
        # Analyze the prompt
        formatted_output, analysis_data = analyzer.analyze(user_prompt, session_id)
        
        # Output the formatted analysis (this gets prepended to the user's prompt)
        if formatted_output:
            print(formatted_output)
        
        # Exit successfully
        sys.exit(0)
        
    except Exception as e:
        # Log error but don't block the prompt
        try:
            # Try to log the error
            error_log_dir = Path.home() / ".claude" / "logs"
            error_log_dir.mkdir(parents=True, exist_ok=True)
            error_log_file = error_log_dir / "prompt_analyzer_errors.log"
            
            with open(error_log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n[{datetime.now().isoformat()}] ERROR: {str(e)}\n")
                f.write(f"Type: {type(e).__name__}\n")
                
                # Add input data for debugging
                if 'input_data' in locals():
                    f.write(f"Input: {json.dumps(input_data, indent=2)}\n")
        except:
            # Even logging failed, just continue
            pass
        
        # Exit with 0 to allow prompt to proceed even if analysis fails
        sys.exit(0)


if __name__ == "__main__":
    main()