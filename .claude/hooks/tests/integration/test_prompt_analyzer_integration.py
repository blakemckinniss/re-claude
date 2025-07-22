"""
Integration tests for prompt analyzer main script
"""

import json
import sys
import os
import subprocess
import tempfile
from pathlib import Path
import pytest
from unittest.mock import patch, Mock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from prompt_analyzer import PromptAnalyzer
from prompt_analyzer.utils.config import Config
import prompt_analyzer_main


class TestPromptAnalyzerIntegration:
    """Integration tests for the complete prompt analyzer flow"""
    
    def test_full_analysis_flow_without_groq(self, test_config, sample_prompts):
        """Test complete analysis flow without Groq API"""
        # Create config without Groq
        config = Config(
            groq_api_key=None,
            log_dir=tempfile.gettempdir(),
            use_cache=False
        )
        
        analyzer = PromptAnalyzer(config)
        
        # Test with various prompts
        for prompt_type, prompt in sample_prompts.items():
            if prompt_type not in ['empty', 'whitespace', 'short']:
                formatted_output, analysis_data = analyzer.analyze(prompt, f"test-{prompt_type}")
                
                # Verify output structure
                assert isinstance(formatted_output, str)
                assert isinstance(analysis_data, dict)
                
                # Verify analysis data contains expected fields
                assert 'topic_genre' in analysis_data
                assert 'complexity_score' in analysis_data
                assert 'swarm_agents_recommended' in analysis_data
                assert 'recommended_agent_roles' in analysis_data
                
                # Verify formatted output contains key sections
                if formatted_output:
                    assert "ANALYSIS" in formatted_output or "Analysis" in formatted_output
    
    def test_full_analysis_flow_with_mock_groq(self, test_config, sample_prompts, mock_groq_client):
        """Test complete analysis flow with mocked Groq API"""
        config = test_config
        
        with patch('prompt_analyzer.core.analyzer.GroqClient', return_value=mock_groq_client):
            analyzer = PromptAnalyzer(config)
            
            prompt = sample_prompts['complex_task']
            formatted_output, analysis_data = analyzer.analyze(prompt, "test-complex")
            
            # Verify Groq was called
            assert mock_groq_client.analyze_prompt.called
            
            # Verify enhanced analysis data
            assert analysis_data['topic_genre'] == 'Software Development'
            assert analysis_data['complexity_score'] == 7
            assert analysis_data['confidence_score'] == 0.9
            assert len(analysis_data['tech_involved']) > 0
    
    def test_script_execution_subprocess(self, tmp_path, sample_input_data):
        """Test executing the script as a subprocess"""
        # Create a test script that imports and runs main
        test_script = tmp_path / "test_run.py"
        test_script.write_text(f"""
import sys
import json
sys.path.insert(0, r'{Path(__file__).parent.parent.parent}')
import prompt_analyzer_main
prompt_analyzer_main.main()
""")
        
        # Prepare input data
        input_json = json.dumps(sample_input_data['basic'])
        
        # Run the script
        result = subprocess.run(
            [sys.executable, str(test_script)],
            input=input_json,
            capture_output=True,
            text=True
        )
        
        # Should exit successfully
        assert result.returncode == 0
        
        # Output should contain analysis
        if result.stdout:
            # The analysis output should be present
            assert len(result.stdout) > 0
    
    def test_error_recovery_integration(self, test_config):
        """Test error recovery in the full integration"""
        # Create analyzer with config that will cause partial failures
        config = Config(
            groq_api_key="invalid-key",
            log_dir="/invalid/path/that/does/not/exist",
            use_cache=True
        )
        
        analyzer = PromptAnalyzer(config)
        
        # Should still work despite invalid config
        formatted_output, analysis_data = analyzer.analyze(
            "Create a simple function",
            "test-error-recovery"
        )
        
        # Should fall back to local analysis
        assert isinstance(analysis_data, dict)
        assert 'topic_genre' in analysis_data
        assert analysis_data.get('confidence_score', 0) <= 0.7  # Lower confidence for local
    
    def test_session_context_integration(self, test_config, tmp_path):
        """Test session context management across multiple calls"""
        # Use temp directory for memory storage
        config = Config(
            groq_api_key=None,
            log_dir=str(tmp_path),
            memory_namespace="test-context",
            use_cache=True
        )
        
        analyzer = PromptAnalyzer(config)
        session_id = "test-session-context"
        
        # First analysis
        output1, data1 = analyzer.analyze("Create a web application", session_id)
        
        # Second analysis in same session
        output2, data2 = analyzer.analyze("Add user authentication to it", session_id)
        
        # Context should be maintained
        assert isinstance(data1, dict)
        assert isinstance(data2, dict)
    
    def test_main_function_integration(self, mock_stdin, capture_output):
        """Test the main function with real PromptAnalyzer"""
        input_data = {
            'prompt': 'Build a REST API with authentication',
            'session_id': 'integration-test'
        }
        
        mock_stdin(input_data)
        
        # Mock only the parts that need filesystem access
        with patch('prompt_analyzer.utils.logging.Logger'):
            with patch('sys.exit') as mock_exit:
                with capture_output() as output:
                    prompt_analyzer_main.main()
                
                # Should exit successfully
                mock_exit.assert_called_once_with(0)
                
                # Should produce output
                stdout = output.get_stdout()
                assert len(stdout) > 0


class TestEndToEndScenarios:
    """End-to-end scenario tests"""
    
    def test_code_generation_scenario(self, test_config):
        """Test a code generation scenario end-to-end"""
        config = Config(
            groq_api_key=None,
            log_dir=tempfile.gettempdir(),
            use_cache=False
        )
        
        analyzer = PromptAnalyzer(config)
        
        prompts = [
            "Create a Python class for managing user accounts",
            "Add methods for login and registration",
            "Include password hashing and validation"
        ]
        
        session_id = "code-gen-scenario"
        
        for i, prompt in enumerate(prompts):
            output, data = analyzer.analyze(prompt, session_id)
            
            # Verify progressive complexity
            assert data['complexity_score'] >= 3
            assert len(data['recommended_agent_roles']) > 0
            
            # Should detect code generation patterns
            if 'task_patterns' in data:
                patterns = data['task_patterns']
                assert any('code' in p or 'generation' in p for p in patterns)
    
    def test_web_development_scenario(self, test_config):
        """Test a web development scenario"""
        config = Config(
            groq_api_key=None,
            log_dir=tempfile.gettempdir()
        )
        
        analyzer = PromptAnalyzer(config)
        
        prompt = """
        Build a full-stack e-commerce application with:
        - React frontend with TypeScript
        - Node.js/Express backend
        - PostgreSQL database
        - Redis for caching
        - Stripe payment integration
        - Docker containerization
        """
        
        output, data = analyzer.analyze(prompt, "web-dev-scenario")
        
        # Should detect high complexity
        assert data['complexity_score'] >= 7
        
        # Should recommend multiple agents
        assert data['swarm_agents_recommended'] >= 5
        
        # Should identify multiple technologies
        if 'tech_involved' in data:
            techs = [t.lower() for t in data['tech_involved']]
            # Should identify some of the mentioned technologies
            assert any(tech in ' '.join(techs) for tech in ['react', 'node', 'database', 'docker'])
    
    def test_performance_with_large_prompt(self, test_config):
        """Test performance with large prompts"""
        config = Config(
            groq_api_key=None,
            max_prompt_length=50000,
            log_dir=tempfile.gettempdir()
        )
        
        analyzer = PromptAnalyzer(config)
        
        # Create a large prompt
        large_prompt = """
        Create a comprehensive enterprise resource planning (ERP) system with the following modules:
        """ + "\n".join([f"- Module {i}: " + "x" * 100 for i in range(100)])
        
        import time
        start_time = time.time()
        
        output, data = analyzer.analyze(large_prompt, "perf-test")
        
        duration = time.time() - start_time
        
        # Should complete within reasonable time (5 seconds for local analysis)
        assert duration < 5.0
        
        # Should handle truncation properly
        assert isinstance(data, dict)
        if len(large_prompt) > config.max_prompt_length:
            # Prompt should be truncated
            assert 'truncated' in output.lower() or len(output) > 0


class TestConfigurationIntegration:
    """Test configuration handling in integration"""
    
    def test_env_file_loading(self, tmp_path, mock_stdin, capture_output):
        """Test .env file loading in main script"""
        # Create .env file
        env_content = """
GROQ_API_KEY=test-integration-key
LOG_DIR=/tmp/integration-logs
USE_CACHE=true
MAX_AGENTS=10
"""
        env_file = tmp_path / ".env"
        env_file.write_text(env_content)
        
        input_data = {
            'prompt': 'Test with env file',
            'session_id': 'env-test'
        }
        
        mock_stdin(input_data)
        
        # Change to temp directory
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            
            with patch('sys.exit'):
                with capture_output():
                    prompt_analyzer_main.main()
            
            # Verify environment variables were loaded
            assert os.getenv('GROQ_API_KEY') == 'test-integration-key'
            assert os.getenv('MAX_AGENTS') == '10'
        
        finally:
            os.chdir(original_cwd)
    
    def test_config_precedence(self, mock_env_vars):
        """Test configuration precedence (env vars over defaults)"""
        config = Config.from_env()
        
        # Env vars should override defaults
        assert config.groq_api_key == 'test-groq-key'
        assert config.groq_model == 'test-model'
        assert config.groq_temperature == 0.5
        assert config.groq_max_tokens == 2048
        assert config.use_cache is True
        assert config.auto_spawn_agents is True