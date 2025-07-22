#!/usr/bin/env node

/**
 * Optimized Hooks Index with Claude Flow MCP Integration
 * Central entry point for all optimized hooks
 * Features:
 * - Dynamic hook loading
 * - Parallel execution support
 * - Memory persistence integration
 * - Performance monitoring
 * - Error recovery
 */

import PreTaskHook from './pre-task.js';
import PostTaskHook from './post-task.js';
import PreCommandHook from './pre-command.js';
import PostEditHook from './post-edit.js';
import SessionEndHook from './session-end.js';
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class HookManager {
  constructor() {
    this.hooks = {
      'pre-task': PreTaskHook,
      'post-task': PostTaskHook,
      'pre-command': PreCommandHook,
      'pre-bash': PreCommandHook, // Alias
      'post-edit': PostEditHook,
      'session-end': SessionEndHook
    };
    
    this.sessionId = process.env.CLAUDE_FLOW_SESSION || `session-${Date.now()}`;
  }

  /**
   * Execute a specific hook
   */
  async executeHook(hookName, options = {}) {
    const HookClass = this.hooks[hookName];
    
    if (!HookClass) {
      console.error(`❌ Unknown hook: ${hookName}`);
      console.log('Available hooks:', Object.keys(this.hooks).join(', '));
      return { success: false, error: `Unknown hook: ${hookName}` };
    }

    try {
      console.log(`\n🪝 Executing ${hookName} hook...`);
      
      // Create hook instance
      const hook = new HookClass();
      
      // Add session context
      process.env.CLAUDE_FLOW_SESSION = this.sessionId;
      
      // Execute with performance tracking
      const startTime = Date.now();
      const result = await hook.execute(options);
      const duration = Date.now() - startTime;
      
      // Track hook performance
      await this.trackHookPerformance(hookName, duration, result.success);
      
      return result;
      
    } catch (error) {
      console.error(`❌ Hook execution failed: ${error.message}`);
      
      // Log error to memory
      await this.logHookError(hookName, error);
      
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Execute multiple hooks in parallel
   */
  async executeParallelHooks(hookConfigs) {
    console.log(`\n🚀 Executing ${hookConfigs.length} hooks in parallel...`);
    
    const promises = hookConfigs.map(config => 
      this.executeHook(config.hook, config.options)
    );
    
    const results = await Promise.allSettled(promises);
    
    // Process results
    const summary = {
      total: results.length,
      successful: 0,
      failed: 0,
      results: []
    };
    
    results.forEach((result, index) => {
      const config = hookConfigs[index];
      if (result.status === 'fulfilled' && result.value.success) {
        summary.successful++;
        summary.results.push({
          hook: config.hook,
          success: true,
          data: result.value
        });
      } else {
        summary.failed++;
        summary.results.push({
          hook: config.hook,
          success: false,
          error: result.reason || result.value?.error
        });
      }
    });
    
    console.log(`\n✅ Parallel execution complete: ${summary.successful}/${summary.total} successful`);
    
    return summary;
  }

  /**
   * Execute hooks in a specific sequence
   */
  async executeSequence(sequence) {
    console.log(`\n📋 Executing hook sequence: ${sequence.map(s => s.hook).join(' → ')}`);
    
    const results = [];
    
    for (const step of sequence) {
      const result = await this.executeHook(step.hook, step.options);
      results.push({
        hook: step.hook,
        ...result
      });
      
      // Check if we should continue
      if (step.stopOnError && !result.success) {
        console.log(`⛔ Sequence stopped due to error in ${step.hook}`);
        break;
      }
      
      // Pass data to next hook if specified
      if (step.passDataTo && sequence[step.passDataTo]) {
        sequence[step.passDataTo].options = {
          ...sequence[step.passDataTo].options,
          previousResult: result
        };
      }
    }
    
    return results;
  }

  /**
   * Track hook performance metrics
   */
  async trackHookPerformance(hookName, duration, success) {
    try {
      const metrics = {
        hook: hookName,
        duration,
        success,
        timestamp: new Date().toISOString(),
        sessionId: this.sessionId
      };
      
      const command = `npx claude-flow@alpha memory store --key "metrics/hooks/${hookName}/${Date.now()}" --value '${JSON.stringify(metrics)}'`;
      await this.executeCommand(command);
      
    } catch (error) {
      // Silent fail for metrics
    }
  }

  /**
   * Log hook errors for debugging
   */
  async logHookError(hookName, error) {
    try {
      const errorLog = {
        hook: hookName,
        error: error.message,
        stack: error.stack,
        timestamp: new Date().toISOString(),
        sessionId: this.sessionId
      };
      
      const command = `npx claude-flow@alpha memory store --key "errors/hooks/${hookName}/${Date.now()}" --value '${JSON.stringify(errorLog)}'`;
      await this.executeCommand(command);
      
    } catch (err) {
      // Silent fail for error logging
    }
  }

  /**
   * Register custom hooks
   */
  registerHook(name, HookClass) {
    if (this.hooks[name]) {
      console.warn(`⚠️ Overriding existing hook: ${name}`);
    }
    
    this.hooks[name] = HookClass;
    console.log(`✅ Registered hook: ${name}`);
  }

  /**
   * List all available hooks
   */
  listHooks() {
    console.log('\n📋 Available Hooks:');
    console.log('─'.repeat(40));
    
    Object.keys(this.hooks).forEach(name => {
      console.log(`  • ${name}`);
    });
    
    console.log('─'.repeat(40));
    console.log(`Total: ${Object.keys(this.hooks).length} hooks\n`);
  }

  /**
   * Execute shell command
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

// Singleton instance
const hookManager = new HookManager();

// CLI interface
if (import.meta.url === `file://${process.argv[1]}`) {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    console.log('Claude Flow Optimized Hooks');
    console.log('Usage: hooks [hook-name] [options]');
    console.log('\nExamples:');
    console.log('  hooks pre-task --description "Build API"');
    console.log('  hooks post-edit --file "src/app.js"');
    console.log('  hooks session-end --generate-report');
    console.log('  hooks list');
    process.exit(0);
  }
  
  if (args[0] === 'list') {
    hookManager.listHooks();
    process.exit(0);
  }
  
  // Parse hook name and options
  const hookName = args[0];
  const options = {};
  
  for (let i = 1; i < args.length; i++) {
    if (args[i].startsWith('--')) {
      const key = args[i].substring(2).replace(/-/g, '');
      const value = args[i + 1] && !args[i + 1].startsWith('--') ? args[++i] : true;
      options[key] = value;
    }
  }
  
  // Execute hook
  hookManager.executeHook(hookName, options).then(result => {
    process.exit(result.success ? 0 : 1);
  });
}

export { hookManager, HookManager };