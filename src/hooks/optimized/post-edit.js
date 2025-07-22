#!/usr/bin/env node

/**
 * Optimized Post-Edit Hook with Claude Flow MCP Integration
 * Features:
 * - Parallel formatting and validation
 * - MCP memory persistence
 * - Neural pattern training from edits
 * - GitHub integration for commits
 * - Performance tracking
 * - Multi-language support
 */

import { spawn } from 'child_process';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class PostEditHook {
  constructor() {
    this.swarmPath = path.join(process.cwd(), '.swarm');
    this.memoryDb = path.join(this.swarmPath, 'memory.db');
    this.sessionId = process.env.CLAUDE_FLOW_SESSION || `session-${Date.now()}`;
    
    // Language-specific formatters
    this.formatters = {
      '.js': 'prettier --write',
      '.jsx': 'prettier --write',
      '.ts': 'prettier --write',
      '.tsx': 'prettier --write',
      '.json': 'prettier --write',
      '.css': 'prettier --write',
      '.scss': 'prettier --write',
      '.html': 'prettier --write',
      '.md': 'prettier --write',
      '.py': 'black',
      '.go': 'gofmt -w',
      '.rs': 'rustfmt',
      '.java': 'google-java-format -i',
      '.cpp': 'clang-format -i',
      '.c': 'clang-format -i',
      '.rb': 'rubocop -a',
      '.php': 'php-cs-fixer fix',
      '.swift': 'swiftformat',
      '.kt': 'ktlint -F'
    };
    
    // Linters
    this.linters = {
      '.js': 'eslint --fix',
      '.jsx': 'eslint --fix',
      '.ts': 'eslint --fix',
      '.tsx': 'eslint --fix',
      '.py': 'pylint',
      '.go': 'golint',
      '.rs': 'cargo clippy',
      '.java': 'checkstyle',
      '.cpp': 'cppcheck',
      '.rb': 'rubocop',
      '.php': 'phpcs'
    };
  }

  /**
   * Execute post-edit hook with full MCP integration
   */
  async execute(options = {}) {
    const {
      file,
      autoFormat = true,
      memoryKey = null,
      trainPatterns = true,
      validateOutput = true,
      updateGithub = true,
      trackPerformance = true
    } = options;

    if (!file) {
      console.error('❌ File path is required');
      return { success: false, error: 'File path is required' };
    }

    console.log('📝 Executing optimized post-edit hook...');
    console.log(`📄 File: ${file}`);
    console.log(`🆔 Session ID: ${this.sessionId}`);

    const startTime = Date.now();
    const results = {
      file,
      formatted: false,
      lintPassed: false,
      memorySaved: false,
      patternsTrained: 0,
      githubUpdated: false,
      performanceTracked: false,
      warnings: [],
      stats: {}
    };

    try {
      // Get file info
      const fileStats = await fs.stat(file);
      const fileContent = await fs.readFile(file, 'utf-8');
      const ext = path.extname(file);
      const lang = this.detectLanguage(ext);
      
      results.stats = {
        size: fileStats.size,
        lines: fileContent.split('\n').length,
        language: lang
      };

      // Execute all post-edit operations in parallel where possible
      const operations = [];

      // 1. Format code (if applicable)
      if (autoFormat && this.formatters[ext]) {
        operations.push(this.formatCode(file, ext));
      }

      // 2. Store edit context in memory
      if (memoryKey || trackPerformance) {
        operations.push(this.storeEditContext(file, memoryKey, fileContent, results.stats));
      }

      // 3. Track performance metrics
      if (trackPerformance) {
        operations.push(this.trackEditPerformance(file, startTime));
      }

      // Execute parallel operations
      const [formatResult, memoryResult, performanceResult] = await Promise.all(operations);

      if (formatResult) {
        results.formatted = formatResult.success;
        results.formatterUsed = formatResult.formatter;
        if (!formatResult.success) {
          results.warnings.push(`Formatting failed: ${formatResult.error}`);
        }
      }

      if (memoryResult) {
        results.memorySaved = memoryResult.success;
        results.memoryKey = memoryResult.key;
      }

      if (performanceResult) {
        results.performanceTracked = performanceResult.success;
        results.stats.editDuration = performanceResult.duration;
      }

      // Sequential operations that depend on formatted code
      
      // 4. Validate/lint code
      if (validateOutput && this.linters[ext]) {
        const lintResult = await this.validateCode(file, ext);
        results.lintPassed = lintResult.success;
        if (!lintResult.success) {
          results.warnings.push(...lintResult.warnings);
        }
      }

      // 5. Train neural patterns
      if (trainPatterns) {
        const trainResult = await this.trainNeuralPatterns(file, fileContent, lang);
        results.patternsTrained = trainResult.patterns;
      }

      // 6. Update GitHub context
      if (updateGithub) {
        const githubResult = await this.updateGithubContext(file);
        results.githubUpdated = githubResult.success;
      }

      // 7. Calculate final stats
      const endContent = await fs.readFile(file, 'utf-8');
      results.stats.linesChanged = Math.abs(endContent.split('\n').length - results.stats.lines);
      results.stats.charactersChanged = Math.abs(endContent.length - fileContent.length);

      // 8. Broadcast completion to other agents
      await this.broadcastEditCompletion(file, results);

      return {
        success: true,
        ...results
      };

    } catch (error) {
      console.error('❌ Post-edit hook error:', error);
      return {
        success: false,
        error: error.message,
        ...results
      };
    }
  }

  /**
   * Detect programming language from file extension
   */
  detectLanguage(ext) {
    const langMap = {
      '.js': 'javascript',
      '.jsx': 'javascript',
      '.ts': 'typescript',
      '.tsx': 'typescript',
      '.py': 'python',
      '.go': 'go',
      '.rs': 'rust',
      '.java': 'java',
      '.cpp': 'cpp',
      '.c': 'c',
      '.rb': 'ruby',
      '.php': 'php',
      '.swift': 'swift',
      '.kt': 'kotlin',
      '.json': 'json',
      '.yaml': 'yaml',
      '.yml': 'yaml',
      '.md': 'markdown',
      '.html': 'html',
      '.css': 'css',
      '.scss': 'scss'
    };
    return langMap[ext] || 'unknown';
  }

  /**
   * Format code using language-specific formatter
   */
  async formatCode(file, ext) {
    const formatter = this.formatters[ext];
    if (!formatter) {
      return { success: true, formatter: 'none' };
    }

    console.log(`🎨 Formatting with ${formatter.split(' ')[0]}...`);
    
    try {
      const command = `${formatter} "${file}"`;
      const result = await this.executeCommand(command);
      
      return {
        success: result.success,
        formatter: formatter.split(' ')[0],
        error: result.error
      };
    } catch (error) {
      return {
        success: false,
        formatter: formatter.split(' ')[0],
        error: error.message
      };
    }
  }

  /**
   * Validate code using language-specific linter
   */
  async validateCode(file, ext) {
    const linter = this.linters[ext];
    if (!linter) {
      return { success: true, warnings: [] };
    }

    console.log(`🔍 Validating with ${linter.split(' ')[0]}...`);
    
    try {
      const command = `${linter} "${file}"`;
      const result = await this.executeCommand(command);
      
      // Parse warnings from linter output
      const warnings = result.output
        .split('\n')
        .filter(line => line.includes('warning') || line.includes('error'))
        .slice(0, 5); // Limit to 5 warnings
      
      return {
        success: result.success || warnings.length === 0,
        warnings
      };
    } catch (error) {
      return {
        success: false,
        warnings: [`Linter error: ${error.message}`]
      };
    }
  }

  /**
   * Store edit context in memory
   */
  async storeEditContext(file, memoryKey, content, stats) {
    console.log('💾 Storing edit context...');
    
    const key = memoryKey || `edit/${this.sessionId}/${path.basename(file)}/${Date.now()}`;
    const context = {
      file,
      timestamp: new Date().toISOString(),
      sessionId: this.sessionId,
      stats,
      contentHash: this.hashContent(content),
      agent: process.env.CLAUDE_FLOW_AGENT || 'unknown'
    };
    
    const command = `npx claude-flow@alpha memory store --key "${key}" --value '${JSON.stringify(context)}'`;
    const result = await this.executeCommand(command);
    
    return {
      success: result.success,
      key
    };
  }

  /**
   * Track edit performance metrics
   */
  async trackEditPerformance(file, startTime) {
    const duration = Date.now() - startTime;
    
    const metrics = {
      file,
      duration,
      timestamp: new Date().toISOString(),
      sessionId: this.sessionId
    };
    
    const command = `npx claude-flow@alpha performance track --metrics '${JSON.stringify(metrics)}'`;
    const result = await this.executeCommand(command);
    
    return {
      success: result.success,
      duration
    };
  }

  /**
   * Train neural patterns from successful edits
   */
  async trainNeuralPatterns(file, content, language) {
    console.log('🧠 Training neural patterns...');
    
    try {
      // Extract patterns from code
      const patterns = this.extractCodePatterns(content, language);
      
      if (patterns.length === 0) {
        return { patterns: 0 };
      }
      
      const command = `npx claude-flow@alpha neural train --patterns '${JSON.stringify(patterns)}' --type edit --language ${language}`;
      const result = await this.executeCommand(command);
      
      return {
        success: result.success,
        patterns: patterns.length
      };
    } catch (error) {
      console.warn('⚠️ Pattern training failed:', error.message);
      return { patterns: 0 };
    }
  }

  /**
   * Extract code patterns for neural training
   */
  extractCodePatterns(content, language) {
    const patterns = [];
    
    // Common patterns across languages
    const commonPatterns = [
      { regex: /async\s+function\s+\w+/g, type: 'async-function' },
      { regex: /class\s+\w+/g, type: 'class-declaration' },
      { regex: /interface\s+\w+/g, type: 'interface' },
      { regex: /import\s+.+from/g, type: 'import' },
      { regex: /export\s+(default\s+)?/g, type: 'export' },
      { regex: /try\s*{[\s\S]*?}\s*catch/g, type: 'try-catch' },
      { regex: /Promise\.(all|race|resolve|reject)/g, type: 'promise-pattern' },
      { regex: /\.map\(|\.filter\(|\.reduce\(/g, type: 'functional-pattern' }
    ];
    
    // Language-specific patterns
    const langPatterns = {
      javascript: [
        { regex: /const\s+\w+\s*=\s*async/g, type: 'async-arrow' },
        { regex: /\.\.\.\w+/g, type: 'spread-operator' },
        { regex: /\?\./g, type: 'optional-chaining' }
      ],
      python: [
        { regex: /def\s+\w+\(/g, type: 'function-def' },
        { regex: /@\w+/g, type: 'decorator' },
        { regex: /with\s+.+\s+as\s+/g, type: 'context-manager' }
      ],
      go: [
        { regex: /func\s+\(\w+\s+\*?\w+\)\s+\w+/g, type: 'method' },
        { regex: /go\s+\w+\(/g, type: 'goroutine' },
        { regex: /defer\s+/g, type: 'defer' }
      ]
    };
    
    // Extract common patterns
    for (const { regex, type } of commonPatterns) {
      const matches = content.match(regex);
      if (matches) {
        patterns.push({ type, count: matches.length, language });
      }
    }
    
    // Extract language-specific patterns
    if (langPatterns[language]) {
      for (const { regex, type } of langPatterns[language]) {
        const matches = content.match(regex);
        if (matches) {
          patterns.push({ type, count: matches.length, language });
        }
      }
    }
    
    return patterns;
  }

  /**
   * Update GitHub context after edit
   */
  async updateGithubContext(file) {
    console.log('🔗 Updating GitHub context...');
    
    try {
      // Check if file is tracked by git
      const gitCheck = await this.executeCommand(`git ls-files --error-unmatch "${file}"`);
      
      if (gitCheck.success) {
        // Get file diff
        const diffResult = await this.executeCommand(`git diff "${file}"`);
        
        if (diffResult.output) {
          // Store diff in memory for later commit
          const command = `npx claude-flow@alpha memory store --key "github/diff/${path.basename(file)}" --value '${JSON.stringify({
            file,
            diff: diffResult.output,
            timestamp: new Date().toISOString()
          })}'`;
          
          await this.executeCommand(command);
          
          return { success: true };
        }
      }
    } catch (error) {
      console.warn('⚠️ GitHub update skipped:', error.message);
    }
    
    return { success: false };
  }

  /**
   * Broadcast edit completion to other agents
   */
  async broadcastEditCompletion(file, results) {
    console.log('📢 Broadcasting edit completion...');
    
    const notification = {
      type: 'edit-complete',
      file,
      sessionId: this.sessionId,
      agent: process.env.CLAUDE_FLOW_AGENT || 'unknown',
      results: {
        formatted: results.formatted,
        lintPassed: results.lintPassed,
        patternsTrained: results.patternsTrained,
        stats: results.stats
      },
      timestamp: new Date().toISOString()
    };
    
    const command = `npx claude-flow@alpha hooks notify --message '${JSON.stringify(notification)}' --level success`;
    await this.executeCommand(command);
  }

  /**
   * Simple content hash for change detection
   */
  hashContent(content) {
    let hash = 0;
    for (let i = 0; i < content.length; i++) {
      const char = content.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return hash.toString(36);
  }

  /**
   * Execute shell command and parse output
   */
  async executeCommand(command) {
    return new Promise((resolve) => {
      const child = spawn(command, [], { shell: true });
      let output = '';
      let error = '';

      child.stdout.on('data', (data) => {
        output += data.toString();
      });

      child.stderr.on('data', (data) => {
        error += data.toString();
      });

      child.on('close', (code) => {
        resolve({
          success: code === 0,
          output,
          error,
          code
        });
      });
    });
  }
}

// CLI execution
if (import.meta.url === `file://${process.argv[1]}`) {
  const hook = new PostEditHook();
  
  // Parse command line arguments
  const args = process.argv.slice(2);
  const options = {};
  
  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--file':
      case '-f':
        options.file = args[++i];
        break;
      case '--auto-format':
        options.autoFormat = args[++i] !== 'false';
        break;
      case '--memory-key':
      case '-m':
        options.memoryKey = args[++i];
        break;
      case '--train-patterns':
        options.trainPatterns = args[++i] !== 'false';
        break;
      case '--validate-output':
        options.validateOutput = args[++i] !== 'false';
        break;
      case '--update-github':
        options.updateGithub = args[++i] !== 'false';
        break;
      case '--track-performance':
        options.trackPerformance = args[++i] !== 'false';
        break;
    }
  }
  
  hook.execute(options).then(result => {
    console.log('\n✅ Post-edit hook completed:', JSON.stringify(result, null, 2));
    process.exit(result.success ? 0 : 1);
  });
}

export default PostEditHook;