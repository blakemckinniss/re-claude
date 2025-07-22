"""
Pytest configuration and shared fixtures for prompt analyzer tests
"""

import os
import sys
import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from prompt_analyzer.utils.config import Config
from prompt_analyzer.models.analysis import AnalysisResult, TaskComplexity
from prompt_analyzer.models.patterns import TaskPattern


@pytest.fixture
def test_config():
    """Create a test configuration"""
    return Config(
        groq_api_key="test-api-key",
        groq_model="test-model",
        groq_temperature=0.3,
        groq_max_tokens=1024,
        groq_timeout=5,
        claude_flow_timeout=5,
        memory_namespace="test-namespace",
        session_ttl=3600,
        max_prompt_length=1000,
        max_patterns=5,
        max_agents=12,
        max_tools=15,
        log_dir="/tmp/test-logs",
        log_level="DEBUG",
        log_to_stderr=False,
        cache_duration=60,
        use_cache=True,
        use_groq_summary=True,
        groq_summary_threshold=10,
        groq_summary_interval=5,
        auto_spawn_agents=True,
        enable_hive_mind=True
    )


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables"""
    env_vars = {
        'GROQ_API_KEY': 'test-groq-key',
        'GROQ_MODEL': 'test-model',
        'GROQ_TEMPERATURE': '0.5',
        'GROQ_MAX_TOKENS': '2048',
        'LOG_DIR': '/tmp/test-logs',
        'USE_CACHE': 'true',
        'AUTO_SPAWN_AGENTS': 'true'
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars


@pytest.fixture
def sample_prompts():
    """Sample prompts for testing"""
    return {
        'simple': "Hello, how are you?",
        'code_generation': "Create a Python function to calculate fibonacci numbers",
        'complex_task': "Build a full-stack web application with React frontend, Node.js backend, PostgreSQL database, implementing user authentication, real-time chat, and payment processing",
        'short': "Hi",
        'empty': "",
        'whitespace': "   ",
        'very_long': "x" * 20000,
        'with_special_chars': "Create a function that handles @#$%^&*() special characters",
        'multi_line': """Create a REST API with the following endpoints:
        - GET /users
        - POST /users
        - PUT /users/:id
        - DELETE /users/:id
        
        Include authentication and validation."""
    }


@pytest.fixture
def sample_input_data():
    """Sample input data for the main function"""
    return {
        'basic': {
            'prompt': 'Create a simple calculator app',
            'session_id': 'test-session-123'
        },
        'no_session': {
            'prompt': 'Build a todo list application'
        },
        'empty_prompt': {
            'prompt': '',
            'session_id': 'test-session-456'
        },
        'complex': {
            'prompt': 'Develop a microservices architecture with Docker, Kubernetes, and implement CI/CD pipeline',
            'session_id': 'test-session-789'
        }
    }


@pytest.fixture
def mock_stdin(monkeypatch):
    """Mock stdin for testing main function"""
    def _mock_stdin(data):
        monkeypatch.setattr('sys.stdin', StringIO(json.dumps(data)))
    return _mock_stdin


@pytest.fixture
def mock_groq_client():
    """Mock Groq client"""
    client = Mock()
    client.is_available = True
    client.analyze_prompt = Mock(return_value={
        'topic_genre': 'Software Development',
        'complexity_score': 7,
        'tech_involved': ['Python', 'API', 'Database'],
        'analysis_notes': 'Complex multi-component system',
        'swarm_agents_recommended': 5,
        'recommended_agent_roles': ['Backend Developer', 'Frontend Developer', 'DevOps'],
        'recommended_mcp_tools': ['database', 'api-testing'],
        'confidence_score': 0.9
    })
    return client


@pytest.fixture
def mock_claude_flow():
    """Mock Claude Flow integration"""
    flow = Mock()
    flow.timeout = 5
    return flow


@pytest.fixture
def sample_analysis_result():
    """Sample analysis result"""
    return AnalysisResult(
        topic_genre="Web Development",
        complexity_score=6,
        complexity_level=TaskComplexity.MODERATE,
        tech_involved=["React", "Node.js", "PostgreSQL"],
        analysis_notes="Full-stack application with multiple components",
        swarm_agents_recommended=4,
        recommended_agent_roles=["Frontend Dev", "Backend Dev", "Database Admin", "DevOps"],
        recommended_mcp_tools=["webpack", "eslint", "postgres"],
        task_patterns=["code_generation", "web_development", "database_design"],
        confidence_score=0.85
    )


@pytest.fixture
def sample_patterns():
    """Sample task patterns"""
    return [
        TaskPattern(
            name="code_generation",
            keywords=["create", "build", "generate", "function", "class"],
            regex_patterns=[r"(create|build|generate).*(function|class|code)"],
            required_agents=["coordinator", "coder", "architect"],
            suggested_tools=["editor", "linter"],
            complexity_modifier=1,
            description="Code generation tasks"
        ),
        TaskPattern(
            name="web_development",
            keywords=["web", "frontend", "backend", "react", "node"],
            regex_patterns=[r"(create|build).*(web|app|frontend|backend)"],
            required_agents=["coordinator", "frontend_dev", "backend_dev"],
            suggested_tools=["webpack", "npm"],
            complexity_modifier=2,
            description="Web development tasks"
        )
    ]


@pytest.fixture
def capture_output():
    """Capture stdout and stderr"""
    class OutputCapture:
        def __init__(self):
            self.stdout = StringIO()
            self.stderr = StringIO()
            self.original_stdout = sys.stdout
            self.original_stderr = sys.stderr
        
        def __enter__(self):
            sys.stdout = self.stdout
            sys.stderr = self.stderr
            return self
        
        def __exit__(self, *args):
            sys.stdout = self.original_stdout
            sys.stderr = self.original_stderr
        
        def get_stdout(self):
            return self.stdout.getvalue()
        
        def get_stderr(self):
            return self.stderr.getvalue()
    
    return OutputCapture


@pytest.fixture
def temp_env_file(tmp_path):
    """Create a temporary .env file"""
    env_content = """
GROQ_API_KEY=test-key-from-env
GROQ_MODEL=llama-test
LOG_DIR=/tmp/test-env-logs
USE_CACHE=false
AUTO_SPAWN_AGENTS=true
"""
    env_file = tmp_path / ".env"
    env_file.write_text(env_content.strip())
    return env_file


@pytest.fixture
def mock_file_system(tmp_path):
    """Mock file system for testing"""
    # Create test directories
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    
    error_log_dir = tmp_path / ".claude" / "logs"
    error_log_dir.mkdir(parents=True)
    
    return {
        'root': tmp_path,
        'log_dir': log_dir,
        'error_log_dir': error_log_dir,
        'error_log_file': error_log_dir / "prompt_analyzer_errors.log"
    }


@pytest.fixture(autouse=True)
def cleanup_env_vars():
    """Clean up environment variables after each test"""
    original_env = os.environ.copy()
    yield
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_prompt_analyzer():
    """Mock PromptAnalyzer class"""
    analyzer = Mock()
    analyzer.analyze = Mock(return_value=(
        "## Analysis Output\nTest analysis output",
        {
            'topic_genre': 'Test Topic',
            'complexity_score': 5,
            'swarm_agents_recommended': 3
        }
    ))
    return analyzer