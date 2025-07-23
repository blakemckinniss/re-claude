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

# Debug logging - write immediately to see if script is called
debug_log_path = Path(__file__).parent / "prompt_analyzer" / "logs" / "debug.log"
debug_log_path.parent.mkdir(parents=True, exist_ok=True)
with open(debug_log_path, 'a') as f:
    f.write(f"\n[{datetime.now().isoformat()}] Script started\n")
    f.write(f"Python: {sys.executable}\n")
    f.write(f"Args: {sys.argv}\n")

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from prompt_analyzer import PromptAnalyzer
from prompt_analyzer.utils.config import Config, load_dotenv


def main():
    """Main entry point for the hook"""
    input_data = {}  # Initialize to avoid unbound variable
    
    # Debug log - entering main
    with open(debug_log_path, 'a') as f:
        f.write(f"[{datetime.now().isoformat()}] Entering main()\n")
    
    try:
        # Load environment variables
        script_dir = Path(__file__).parent
        env_path = script_dir / '.env'
        if env_path.exists():
            load_dotenv(str(env_path))
        
        # Read input from stdin (Claude Code hook format)
        input_data = json.load(sys.stdin)
        
        # Debug log - input received
        with open(debug_log_path, 'a') as f:
            f.write(f"[{datetime.now().isoformat()}] Input received: {json.dumps(input_data, indent=2)}\n")
        
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
        
        # Log the final enhanced prompt
        try:
            # Create log directory
            log_dir = script_dir / "prompt_analyzer" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Create log file with timestamp
            log_file = log_dir / "enhanced_prompts.log"
            
            # Build the final prompt (original + enhancements)
            final_prompt = ""
            if formatted_output:
                final_prompt = formatted_output + "\n\n" + user_prompt
            else:
                final_prompt = user_prompt
            
            # Log entry
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id,
                "original_prompt": user_prompt,
                "enhanced_output": formatted_output,
                "final_prompt": final_prompt,
                "analysis_data": analysis_data
            }
            
            # Append to log file
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, indent=2) + "\n" + "="*80 + "\n")
            
        except Exception as e:
            # Don't fail the hook if logging fails
            pass
        
        # Output the formatted analysis (this gets prepended to the user's prompt)
        if formatted_output:
            print(formatted_output)
        
        # Exit successfully
        sys.exit(0)
        
    except Exception as e:
        # Log error but don't block the prompt
        try:
            # Try to log the error to the same logs folder
            error_log_dir = script_dir / "prompt_analyzer" / "logs"
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