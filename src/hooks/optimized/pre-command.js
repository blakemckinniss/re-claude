#!/usr/bin/env node

/**
 * Optimized Pre-Command Hook with Claude Flow MCP Integration
 * Features:
 * - Command safety validation
 * - Resource preparation
 * - Parallel dependency checking
 * - Command optimization suggestions
 * - Security scanning
 * - Performance prediction
 */

import { spawn } from 'child_process';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class PreCommandHook {
  constructor() {
    this.swarmPath = path.join(process.cwd(), '.swarm');
    this.sessionId = process.env.CLAUDE_FLOW_SESSION || `session-${Date.now()}`;
    
    // Dangerous commands that need validation
    this.dangerousCommands = [
      'rm -rf',
      'dd if=',
      'mkfs',
      'format',
      ':(){ :|:& };:',  // Fork bomb
      'chmod -R 777',
      'chown -R',
      '> /dev/sda',
      'mv /* ',
      'wget -O - | sh',
      'curl | bash'
    ];
    
    // Resource-intensive commands
    this.resourceIntensive = [
      'find /',
      'grep -r /',
      'npm install',
      'yarn install',
      'docker build',
      'make -j',
      'cargo build',
      'go build'
    ];
  }

  /**
   * Execute pre-command hook with safety validation
   */
  async execute(options = {}) {
    const {
      command,
      validateSafety = true,
      prepareResources = true,
      checkDependencies = true,
      suggestOptimizations = true,
      predictPerformance = true
    } = options;

    if (!command) {
      console.error('❌ Command is required');
      return { continue: false, error: 'Command is required' };
    }

    console.log('🔍 Executing pre-command hook...');
    console.log(`📟 Command: ${command}`);

    const startTime = Date.now();
    const results = {
      command,
      continue: true,
      safe: true,
      optimizations: [],
      warnings: [],
      resources: null,
      performance: null
    };

    try {
      // Execute validation checks in parallel
      const operations = [];

      // 1. Validate command safety
      if (validateSafety) {
        operations.push(this.validateCommandSafety(command));
      }

      // 2. Check dependencies
      if (checkDependencies) {
        operations.push(this.checkCommandDependencies(command));
      }

      // 3. Predict performance impact
      if (predictPerformance) {
        operations.push(this.predictCommandPerformance(command));
      }

      // Execute parallel operations
      const [safety, dependencies, performance] = await Promise.all(operations);

      // Process safety validation
      if (safety && !safety.safe) {
        results.safe = false;
        results.continue = false;
        results.warnings.push(...safety.warnings);
        console.error('🚫 Command blocked for safety reasons');
        return results;
      }

      results.warnings.push(...(safety?.warnings || []));
      results.performance = performance;

      // Sequential operations
      
      // 4. Prepare resources if needed
      if (prepareResources && dependencies?.requirements) {
        results.resources = await this.prepareCommandResources(command, dependencies.requirements);
      }

      // 5. Suggest optimizations
      if (suggestOptimizations) {
        results.optimizations = await this.suggestCommandOptimizations(command, performance);
      }

      // 6. Log command intent
      await this.logCommandIntent(command, results);

      // Display summary
      this.displayPreCommandSummary(results);

      return results;

    } catch (error) {
      console.error('❌ Pre-command hook error:', error);
      return {
        ...results,
        continue: false,
        error: error.message
      };
    }
  }

  /**
   * Validate command safety
   */
  async validateCommandSafety(command) {
    console.log('🛡️ Validating command safety...');
    
    const result = {
      safe: true,
      warnings: [],
      riskLevel: 'low'
    };

    // Check for dangerous patterns
    for (const dangerous of this.dangerousCommands) {
      if (command.includes(dangerous)) {
        result.safe = false;
        result.riskLevel = 'critical';
        result.warnings.push(`Dangerous command pattern detected: ${dangerous}`);
      }
    }

    // Check for sudo/admin commands
    if (command.startsWith('sudo') || command.includes('| sudo')) {
      result.warnings.push('Command requires elevated privileges');
      result.riskLevel = 'high';
    }

    // Check for file system operations
    if (command.match(/rm\s|del\s|rmdir|mv\s|cp\s/)) {
      result.warnings.push('Command performs file system operations');
      if (!result.riskLevel || result.riskLevel === 'low') {
        result.riskLevel = 'medium';
      }
    }

    // Check for network operations
    if (command.match(/wget|curl|nc|telnet|ssh|scp/)) {
      result.warnings.push('Command performs network operations');
      if (!result.riskLevel || result.riskLevel === 'low') {
        result.riskLevel = 'medium';
      }
    }

    // Check for script execution
    if (command.match(/\|\s*(bash|sh|python|node|ruby)/)) {
      result.warnings.push('Command pipes to script interpreter');
      result.riskLevel = 'high';
    }

    // Validate paths
    if (command.includes('..') || command.includes('~')) {
      const expandedCommand = await this.expandPaths(command);
      if (expandedCommand.includes('/etc/') || expandedCommand.includes('/sys/') || expandedCommand.includes('/proc/')) {
        result.warnings.push('Command accesses system directories');
        result.riskLevel = 'high';
      }
    }

    return result;
  }

  /**
   * Check command dependencies
   */
  async checkCommandDependencies(command) {
    console.log('📦 Checking command dependencies...');
    
    const dependencies = {
      available: true,
      missing: [],
      requirements: []
    };

    // Extract primary command
    const primaryCommand = command.split(/\s+/)[0].replace(/^sudo\s+/, '');
    
    // Check if command exists
    const checkCommand = `which ${primaryCommand} 2>/dev/null`;
    const result = await this.executeCommand(checkCommand);
    
    if (!result.success || !result.output.trim()) {
      dependencies.available = false;
      dependencies.missing.push(primaryCommand);
    }

    // Check for common dependency patterns
    if (command.includes('npm ')) {
      dependencies.requirements.push('node', 'npm');
      if (await this.fileExists('package.json')) {
        dependencies.requirements.push('package.json');
      }
    }

    if (command.includes('pip ') || command.includes('python ')) {
      dependencies.requirements.push('python');
      if (await this.fileExists('requirements.txt')) {
        dependencies.requirements.push('requirements.txt');
      }
    }

    if (command.includes('docker ')) {
      dependencies.requirements.push('docker');
      const dockerCheck = await this.executeCommand('docker info 2>/dev/null');
      if (!dockerCheck.success) {
        dependencies.missing.push('docker-daemon');
      }
    }

    if (command.includes('git ')) {
      dependencies.requirements.push('git');
      if (!await this.fileExists('.git')) {
        dependencies.missing.push('git-repository');
      }
    }

    return dependencies;
  }

  /**
   * Predict command performance impact
   */
  async predictCommandPerformance(command) {
    console.log('⚡ Predicting performance impact...');
    
    const prediction = {
      estimatedDuration: 'fast',
      cpuIntensive: false,
      memoryIntensive: false,
      diskIntensive: false,
      networkIntensive: false,
      recommendations: []
    };

    // Check for resource-intensive patterns
    for (const intensive of this.resourceIntensive) {
      if (command.includes(intensive)) {
        prediction.estimatedDuration = 'slow';
        
        if (intensive.includes('find') || intensive.includes('grep')) {
          prediction.cpuIntensive = true;
          prediction.diskIntensive = true;
        }
        
        if (intensive.includes('install') || intensive.includes('build')) {
          prediction.networkIntensive = true;
          prediction.diskIntensive = true;
        }
      }
    }

    // Analyze specific commands
    if (command.includes('npm install') || command.includes('yarn install')) {
      prediction.estimatedDuration = 'slow';
      prediction.networkIntensive = true;
      prediction.recommendations.push('Consider using npm ci for faster installs');
      prediction.recommendations.push('Enable npm cache for improved performance');
    }

    if (command.includes('docker build')) {
      prediction.estimatedDuration = 'slow';
      prediction.cpuIntensive = true;
      prediction.diskIntensive = true;
      prediction.recommendations.push('Use docker build cache effectively');
      prediction.recommendations.push('Consider multi-stage builds for smaller images');
    }

    if (command.match(/find .* -name/)) {
      prediction.diskIntensive = true;
      prediction.recommendations.push('Consider using fd or locate for faster file searches');
      prediction.recommendations.push('Limit search scope to specific directories');
    }

    if (command.includes('grep -r')) {
      prediction.cpuIntensive = true;
      prediction.diskIntensive = true;
      prediction.recommendations.push('Use ripgrep (rg) for faster recursive searches');
      prediction.recommendations.push('Consider using --include patterns to limit file types');
    }

    // Estimate duration based on indicators
    const intensiveCount = [
      prediction.cpuIntensive,
      prediction.memoryIntensive,
      prediction.diskIntensive,
      prediction.networkIntensive
    ].filter(Boolean).length;

    if (intensiveCount >= 3) {
      prediction.estimatedDuration = 'very slow';
    } else if (intensiveCount >= 2) {
      prediction.estimatedDuration = 'slow';
    } else if (intensiveCount >= 1) {
      prediction.estimatedDuration = 'moderate';
    }

    return prediction;
  }

  /**
   * Prepare resources for command execution
   */
  async prepareCommandResources(command, requirements) {
    console.log('🔧 Preparing command resources...');
    
    const prepared = {
      ready: true,
      actions: []
    };

    // Create necessary directories
    if (command.includes('mkdir') || command.includes('> ')) {
      const dirMatch = command.match(/(?:mkdir\s+-p\s+|>\s*)([^\s]+)/);
      if (dirMatch) {
        const dir = path.dirname(dirMatch[1]);
        if (dir && dir !== '.' && !await this.fileExists(dir)) {
          await fs.mkdir(dir, { recursive: true });
          prepared.actions.push(`Created directory: ${dir}`);
        }
      }
    }

    // Check disk space for intensive operations
    if (requirements.includes('docker') || command.includes('install')) {
      const diskSpace = await this.checkDiskSpace();
      if (diskSpace.available < 1000) { // Less than 1GB
        prepared.ready = false;
        prepared.actions.push('Warning: Low disk space available');
      }
    }

    // Ensure git is clean for git operations
    if (requirements.includes('git') && command.includes('git pull')) {
      const gitStatus = await this.executeCommand('git status --porcelain');
      if (gitStatus.output.trim()) {
        prepared.actions.push('Warning: Uncommitted changes in git repository');
      }
    }

    return prepared;
  }

  /**
   * Suggest command optimizations
   */
  async suggestCommandOptimizations(command, performance) {
    console.log('💡 Analyzing optimization opportunities...');
    
    const optimizations = [];

    // Parallel execution opportunities
    if (command.includes('&&')) {
      const sequential = command.split('&&').map(c => c.trim());
      const parallelizable = this.identifyParallelizable(sequential);
      if (parallelizable.length > 1) {
        optimizations.push({
          type: 'parallel',
          suggestion: 'These commands can run in parallel',
          commands: parallelizable,
          impact: 'Could reduce execution time by 40-60%'
        });
      }
    }

    // Command alternatives
    const alternatives = {
      'rm -rf': 'Consider using trash-cli for safer deletions',
      'find .': 'Use fd for faster file finding',
      'grep -r': 'Use ripgrep (rg) for faster searching',
      'cat * | grep': 'Use grep directly on files',
      'ps aux | grep': 'Use pgrep or pidof',
      'npm install': 'Use npm ci for reproducible installs',
      'yarn install': 'Use yarn install --frozen-lockfile'
    };

    for (const [pattern, suggestion] of Object.entries(alternatives)) {
      if (command.includes(pattern)) {
        optimizations.push({
          type: 'alternative',
          suggestion,
          pattern,
          impact: 'Improved performance and safety'
        });
      }
    }

    // Resource optimization based on performance prediction
    if (performance) {
      if (performance.cpuIntensive) {
        optimizations.push({
          type: 'resource',
          suggestion: 'Consider limiting CPU usage with nice or cpulimit',
          impact: 'Prevents system slowdown during execution'
        });
      }

      if (performance.memoryIntensive) {
        optimizations.push({
          type: 'resource',
          suggestion: 'Monitor memory usage and consider using ulimit',
          impact: 'Prevents out-of-memory errors'
        });
      }

      performance.recommendations?.forEach(rec => {
        optimizations.push({
          type: 'performance',
          suggestion: rec,
          impact: 'Optimized execution'
        });
      });
    }

    return optimizations;
  }

  /**
   * Log command intent for tracking
   */
  async logCommandIntent(command, results) {
    console.log('📝 Logging command intent...');
    
    const intent = {
      command,
      timestamp: new Date().toISOString(),
      sessionId: this.sessionId,
      agent: process.env.CLAUDE_FLOW_AGENT || 'unknown',
      safety: results.safe,
      riskLevel: results.warnings.length > 0 ? 'medium' : 'low',
      performance: results.performance?.estimatedDuration || 'unknown',
      optimizations: results.optimizations.length
    };

    const logCommand = `npx claude-flow@alpha memory store --key "command/${this.sessionId}/${Date.now()}" --value '${JSON.stringify(intent)}'`;
    await this.executeCommand(logCommand);

    // Also use notification hook for real-time tracking
    if (results.warnings.length > 0) {
      const notifyCommand = `npx claude-flow@alpha hooks notify --message "Pre-command validation: ${command.substring(0, 50)}..." --level warning`;
      await this.executeCommand(notifyCommand);
    }
  }

  /**
   * Display pre-command summary
   */
  displayPreCommandSummary(results) {
    console.log('\n' + '─'.repeat(60));
    
    if (!results.safe) {
      console.log('🚫 COMMAND BLOCKED');
      console.log('─'.repeat(60));
      console.log('Security violations detected:');
      results.warnings.forEach(warning => {
        console.log(`  ⚠️  ${warning}`);
      });
      return;
    }

    console.log('✅ Command validated');
    
    if (results.warnings.length > 0) {
      console.log('\n⚠️  Warnings:');
      results.warnings.forEach(warning => {
        console.log(`  • ${warning}`);
      });
    }

    if (results.performance) {
      console.log(`\n⚡ Performance: ${results.performance.estimatedDuration}`);
      const intensive = [];
      if (results.performance.cpuIntensive) intensive.push('CPU');
      if (results.performance.memoryIntensive) intensive.push('Memory');
      if (results.performance.diskIntensive) intensive.push('Disk');
      if (results.performance.networkIntensive) intensive.push('Network');
      if (intensive.length > 0) {
        console.log(`  Resource intensive: ${intensive.join(', ')}`);
      }
    }

    if (results.optimizations.length > 0) {
      console.log('\n💡 Optimization suggestions:');
      results.optimizations.forEach((opt, i) => {
        console.log(`  ${i + 1}. ${opt.suggestion}`);
        if (opt.impact) {
          console.log(`     Impact: ${opt.impact}`);
        }
      });
    }

    console.log('─'.repeat(60) + '\n');
  }

  // Helper methods

  identifyParallelizable(commands) {
    const parallelizable = [];
    const dependencies = new Set();

    for (const cmd of commands) {
      // Simple heuristic: commands that don't share files/resources can run in parallel
      const isIndependent = !cmd.includes('>') || 
                           !Array.from(dependencies).some(dep => cmd.includes(dep));
      
      if (isIndependent) {
        parallelizable.push(cmd);
      }

      // Track potential dependencies (output files, etc.)
      const outputMatch = cmd.match(/>\s*([^\s]+)/);
      if (outputMatch) {
        dependencies.add(outputMatch[1]);
      }
    }

    return parallelizable;
  }

  async expandPaths(command) {
    // Simple path expansion (in real implementation, would be more sophisticated)
    let expanded = command;
    if (command.includes('~')) {
      const home = process.env.HOME || process.env.USERPROFILE;
      expanded = expanded.replace(/~/g, home);
    }
    return expanded;
  }

  async fileExists(filePath) {
    try {
      await fs.access(filePath);
      return true;
    } catch {
      return false;
    }
  }

  async checkDiskSpace() {
    try {
      const result = await this.executeCommand('df -BM . | tail -1');
      const match = result.output.match(/(\d+)M\s+(\d+)M\s+(\d+)M/);
      if (match) {
        return {
          total: parseInt(match[1]),
          used: parseInt(match[2]),
          available: parseInt(match[3])
        };
      }
    } catch (error) {
      // Fallback
    }
    return { total: 0, used: 0, available: 10000 }; // Assume 10GB available
  }

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
  const hook = new PreCommandHook();
  
  // Parse command line arguments
  const args = process.argv.slice(2);
  const options = {};
  
  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--command':
      case '-c':
        options.command = args[++i];
        break;
      case '--validate-safety':
        options.validateSafety = args[++i] !== 'false';
        break;
      case '--prepare-resources':
        options.prepareResources = args[++i] !== 'false';
        break;
      case '--check-dependencies':
        options.checkDependencies = args[++i] !== 'false';
        break;
      case '--suggest-optimizations':
        options.suggestOptimizations = args[++i] !== 'false';
        break;
      case '--predict-performance':
        options.predictPerformance = args[++i] !== 'false';
        break;
    }
  }
  
  hook.execute(options).then(result => {
    process.exit(result.continue ? 0 : 1);
  });
}

export default PreCommandHook;