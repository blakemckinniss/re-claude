"""
Unit tests for prompt_analyzer_main.py
"""

import json
import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
from pathlib import Path
from io import StringIO

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import prompt_analyzer_main


class TestMain:
    """Test cases for the main() function"""
    
    def test_main_with_valid_input(self, mock_stdin, capture_output, mock_prompt_analyzer):
        """Test main function with valid input data"""
        input_data = {
            'prompt': 'Create a Python web application',
            'session_id': 'test-session-123'
        }
        
        mock_stdin(input_data)
        
        with patch('prompt_analyzer_main.PromptAnalyzer', return_value=mock_prompt_analyzer):
            with patch('sys.exit') as mock_exit:
                with capture_output() as output:
                    prompt_analyzer_main.main()
                
                # Verify successful exit
                mock_exit.assert_called_once_with(0)
                
                # Verify analyzer was called
                mock_prompt_analyzer.analyze.assert_called_once_with(
                    'Create a Python web application',
                    'test-session-123'
                )
                
                # Verify output was printed
                stdout = output.get_stdout()
                assert "Analysis Output" in stdout
    
    def test_main_with_no_session_id(self, mock_stdin, mock_prompt_analyzer):
        """Test main function without session_id"""
        input_data = {
            'prompt': 'Build a REST API'
        }
        
        mock_stdin(input_data)
        
        with patch('prompt_analyzer_main.PromptAnalyzer', return_value=mock_prompt_analyzer):
            with patch('sys.exit') as mock_exit:
                prompt_analyzer_main.main()
                
                # Verify analyzer was called with prompt and empty session_id
                mock_prompt_analyzer.analyze.assert_called_once()
                call_args = mock_prompt_analyzer.analyze.call_args[0]
                assert call_args[0] == 'Build a REST API'
                assert call_args[1] == ''
    
    def test_main_with_empty_prompt(self, mock_stdin):
        """Test main function with empty prompt"""
        input_data = {
            'prompt': '',
            'session_id': 'test-session'
        }
        
        mock_stdin(input_data)
        
        with patch('sys.exit') as mock_exit:
            prompt_analyzer_main.main()
            
            # Should exit without analyzing
            mock_exit.assert_called_once_with(0)
    
    def test_main_with_short_prompt(self, mock_stdin):
        """Test main function with prompt too short to analyze"""
        input_data = {
            'prompt': 'Hi',
            'session_id': 'test-session'
        }
        
        mock_stdin(input_data)
        
        with patch('sys.exit') as mock_exit:
            prompt_analyzer_main.main()
            
            # Should exit without analyzing
            mock_exit.assert_called_once_with(0)
    
    def test_main_with_whitespace_prompt(self, mock_stdin):
        """Test main function with whitespace-only prompt"""
        input_data = {
            'prompt': '   \n\t  ',
            'session_id': 'test-session'
        }
        
        mock_stdin(input_data)
        
        with patch('sys.exit') as mock_exit:
            prompt_analyzer_main.main()
            
            # Should exit without analyzing
            mock_exit.assert_called_once_with(0)
    
    def test_main_loads_env_file(self, mock_stdin, temp_env_file, mock_prompt_analyzer):
        """Test that main loads .env file if it exists"""
        input_data = {
            'prompt': 'Create a function',
            'session_id': 'test-session'
        }
        
        mock_stdin(input_data)
        
        # Mock the script directory to point to temp directory
        with patch('prompt_analyzer_main.Path') as mock_path:
            mock_path.return_value.parent = temp_env_file.parent
            
            with patch('prompt_analyzer_main.load_dotenv') as mock_load_dotenv:
                with patch('prompt_analyzer_main.PromptAnalyzer', return_value=mock_prompt_analyzer):
                    with patch('sys.exit'):
                        prompt_analyzer_main.main()
                
                # Verify dotenv was called with the env file path
                mock_load_dotenv.assert_called_once()
                call_arg = mock_load_dotenv.call_args[0][0]
                assert call_arg.endswith('.env')
    
    def test_main_handles_json_decode_error(self, monkeypatch, mock_file_system):
        """Test main handles invalid JSON input"""
        monkeypatch.setattr('sys.stdin', StringIO('invalid json'))
        
        with patch('pathlib.Path.home', return_value=mock_file_system['root']):
            with patch('sys.exit') as mock_exit:
                prompt_analyzer_main.main()
                
                # Should exit gracefully
                mock_exit.assert_called_once_with(0)
                
                # Check error was logged
                error_log = mock_file_system['error_log_file']
                assert error_log.exists()
                content = error_log.read_text()
                assert "ERROR" in content
                assert "JSONDecodeError" in content
    
    def test_main_handles_analyzer_exception(self, mock_stdin, mock_file_system):
        """Test main handles exception from analyzer"""
        input_data = {
            'prompt': 'Test prompt',
            'session_id': 'test-session'
        }
        
        mock_stdin(input_data)
        
        # Create analyzer that raises exception
        mock_analyzer = Mock()
        mock_analyzer.analyze.side_effect = RuntimeError("Test error")
        
        with patch('prompt_analyzer_main.PromptAnalyzer', return_value=mock_analyzer):
            with patch('pathlib.Path.home', return_value=mock_file_system['root']):
                with patch('sys.exit') as mock_exit:
                    prompt_analyzer_main.main()
                    
                    # Should exit gracefully
                    mock_exit.assert_called_once_with(0)
                    
                    # Check error was logged
                    error_log = mock_file_system['error_log_file']
                    assert error_log.exists()
                    content = error_log.read_text()
                    assert "ERROR: Test error" in content
                    assert "RuntimeError" in content
    
    def test_main_handles_logging_failure(self, mock_stdin):
        """Test main continues even if error logging fails"""
        input_data = {
            'prompt': 'Test prompt',
            'session_id': 'test-session'
        }
        
        mock_stdin(input_data)
        
        # Create analyzer that raises exception
        mock_analyzer = Mock()
        mock_analyzer.analyze.side_effect = RuntimeError("Test error")
        
        with patch('prompt_analyzer_main.PromptAnalyzer', return_value=mock_analyzer):
            # Make Path.home() raise exception to simulate logging failure
            with patch('pathlib.Path.home', side_effect=Exception("Home dir error")):
                with patch('sys.exit') as mock_exit:
                    prompt_analyzer_main.main()
                    
                    # Should still exit gracefully
                    mock_exit.assert_called_once_with(0)
    
    def test_main_with_config_from_env(self, mock_stdin, mock_env_vars, mock_prompt_analyzer):
        """Test main uses Config.from_env()"""
        input_data = {
            'prompt': 'Create a web app',
            'session_id': 'test-session'
        }
        
        mock_stdin(input_data)
        
        with patch('prompt_analyzer_main.Config.from_env') as mock_config_from_env:
            mock_config = Mock()
            mock_config_from_env.return_value = mock_config
            
            with patch('prompt_analyzer_main.PromptAnalyzer') as mock_analyzer_class:
                mock_analyzer_class.return_value = mock_prompt_analyzer
                
                with patch('sys.exit'):
                    prompt_analyzer_main.main()
                
                # Verify Config.from_env was called
                mock_config_from_env.assert_called_once()
                
                # Verify PromptAnalyzer was created with config
                mock_analyzer_class.assert_called_once_with(mock_config)
    
    def test_main_prints_formatted_output(self, mock_stdin, capture_output):
        """Test main prints the formatted output from analyzer"""
        input_data = {
            'prompt': 'Build a calculator',
            'session_id': 'test-session'
        }
        
        mock_stdin(input_data)
        
        # Create analyzer with specific output
        mock_analyzer = Mock()
        formatted_output = "## ENHANCED PROMPT ANALYSIS\nTest output with analysis"
        mock_analyzer.analyze.return_value = (formatted_output, {'test': 'data'})
        
        with patch('prompt_analyzer_main.PromptAnalyzer', return_value=mock_analyzer):
            with patch('sys.exit'):
                with capture_output() as output:
                    prompt_analyzer_main.main()
                
                stdout = output.get_stdout()
                assert formatted_output in stdout
    
    def test_main_handles_empty_formatted_output(self, mock_stdin, capture_output):
        """Test main handles empty formatted output gracefully"""
        input_data = {
            'prompt': 'Test prompt',
            'session_id': 'test-session'
        }
        
        mock_stdin(input_data)
        
        # Create analyzer that returns empty output
        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = ("", {'test': 'data'})
        
        with patch('prompt_analyzer_main.PromptAnalyzer', return_value=mock_analyzer):
            with patch('sys.exit') as mock_exit:
                with capture_output() as output:
                    prompt_analyzer_main.main()
                
                # Should exit successfully
                mock_exit.assert_called_once_with(0)
                
                # No output should be printed
                stdout = output.get_stdout()
                assert stdout == ""


class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_logs_input_data_on_error(self, mock_stdin, mock_file_system):
        """Test that input data is logged when an error occurs"""
        input_data = {
            'prompt': 'Test prompt with error',
            'session_id': 'error-session',
            'extra_field': 'extra_value'
        }
        
        mock_stdin(input_data)
        
        # Create analyzer that raises exception
        mock_analyzer = Mock()
        mock_analyzer.analyze.side_effect = ValueError("Invalid value")
        
        with patch('prompt_analyzer_main.PromptAnalyzer', return_value=mock_analyzer):
            with patch('pathlib.Path.home', return_value=mock_file_system['root']):
                with patch('sys.exit'):
                    prompt_analyzer_main.main()
                    
                    # Check error log contains input data
                    error_log = mock_file_system['error_log_file']
                    content = error_log.read_text()
                    assert "Input:" in content
                    assert '"prompt": "Test prompt with error"' in content
                    assert '"session_id": "error-session"' in content
                    assert '"extra_field": "extra_value"' in content