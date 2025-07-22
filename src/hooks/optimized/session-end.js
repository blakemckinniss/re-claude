#!/usr/bin/env node

/**
 * Optimized Session-End Hook with Claude Flow MCP Integration
 * Features:
 * - Comprehensive session summary generation
 * - Performance metrics aggregation
 * - Knowledge persistence across sessions
 * - Automated reporting
 * - Resource cleanup
 * - Learning extraction
 */

import { spawn } from 'child_process';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class SessionEndHook {
  constructor() {
    this.swarmPath = path.join(process.cwd(), '.swarm');
    this.reportsPath = path.join(this.swarmPath, 'reports');
    this.sessionId = process.env.CLAUDE_FLOW_SESSION || `session-${Date.now()}`;
  }

  /**
   * Execute session-end hook with full MCP integration
   */
  async execute(options = {}) {
    const {
      generateSummary = true,
      persistState = true,
      exportMetrics = true,
      generateReport = true,
      cleanupResources = false,
      extractLearnings = true
    } = options;

    console.log('🏁 Executing session-end hook...');
    console.log(`🆔 Session ID: ${this.sessionId}`);
    console.log(`📅 End Time: ${new Date().toISOString()}`);

    const results = {
      sessionId: this.sessionId,
      summary: null,
      metrics: null,
      learnings: null,
      reportPath: null,
      statePersisted: false,
      resourcesCleaned: false
    };

    try {
      // Execute session-end operations in parallel where possible
      const operations = [];

      // 1. Generate session summary
      if (generateSummary) {
        operations.push(this.generateSessionSummary());
      }

      // 2. Collect and aggregate metrics
      if (exportMetrics) {
        operations.push(this.aggregateSessionMetrics());
      }

      // 3. Extract learnings and patterns
      if (extractLearnings) {
        operations.push(this.extractSessionLearnings());
      }

      // Execute parallel operations
      const [summary, metrics, learnings] = await Promise.all(operations);

      results.summary = summary;
      results.metrics = metrics;
      results.learnings = learnings;

      // Sequential operations
      
      // 4. Generate comprehensive report
      if (generateReport) {
        results.reportPath = await this.generateSessionReport(results);
      }

      // 5. Persist session state
      if (persistState) {
        results.statePersisted = await this.persistFullSessionState(results);
      }

      // 6. Cleanup resources if requested
      if (cleanupResources) {
        results.resourcesCleaned = await this.cleanupSessionResources();
      }

      // 7. Display session summary
      this.displaySessionSummary(results);

      return {
        success: true,
        ...results
      };

    } catch (error) {
      console.error('❌ Session-end hook error:', error);
      return {
        success: false,
        error: error.message,
        ...results
      };
    }
  }

  /**
   * Generate comprehensive session summary
   */
  async generateSessionSummary() {
    console.log('📝 Generating session summary...');
    
    try {
      // Retrieve session start context
      const contextResult = await this.executeCommand(`npx claude-flow@alpha memory search --pattern "task/${this.sessionId}" --limit 100`);
      const tasks = this.parseJsonOutput(contextResult.output);

      // Retrieve all edits
      const editsResult = await this.executeCommand(`npx claude-flow@alpha memory search --pattern "edit/${this.sessionId}" --limit 500`);
      const edits = this.parseJsonOutput(editsResult.output);

      // Retrieve decisions and notifications
      const decisionsResult = await this.executeCommand(`npx claude-flow@alpha memory search --pattern "decision" --limit 50`);
      const decisions = this.parseJsonOutput(decisionsResult.output);

      // Calculate session statistics
      const uniqueFiles = new Set();
      const fileTypes = {};
      let totalLines = 0;

      if (edits?.entries) {
        edits.entries.forEach(edit => {
          if (edit.value?.file) {
            uniqueFiles.add(edit.value.file);
            const ext = path.extname(edit.value.file);
            fileTypes[ext] = (fileTypes[ext] || 0) + 1;
            totalLines += edit.value.stats?.linesChanged || 0;
          }
        });
      }

      // Build summary
      const summary = {
        sessionId: this.sessionId,
        startTime: tasks?.entries?.[0]?.timestamp || 'unknown',
        endTime: new Date().toISOString(),
        duration: this.calculateSessionDuration(tasks?.entries?.[0]?.timestamp),
        
        tasksCompleted: tasks?.entries?.length || 0,
        filesModified: uniqueFiles.size,
        totalEdits: edits?.entries?.length || 0,
        linesChanged: totalLines,
        
        fileTypes: Object.entries(fileTypes)
          .sort((a, b) => b[1] - a[1])
          .slice(0, 5)
          .map(([type, count]) => ({ type, count })),
        
        keyActivities: this.extractKeyActivities(tasks, edits, decisions),
        
        topFiles: this.getTopModifiedFiles(edits),
        
        agentsUsed: this.extractAgentUsage(tasks)
      };

      return summary;

    } catch (error) {
      console.warn('⚠️ Summary generation failed:', error.message);
      return null;
    }
  }

  /**
   * Aggregate all session metrics
   */
  async aggregateSessionMetrics() {
    console.log('📊 Aggregating session metrics...');
    
    try {
      // Collect various metrics
      const metricsPromises = [
        this.executeCommand('npx claude-flow@alpha performance report --timeframe session --format json'),
        this.executeCommand('npx claude-flow@alpha token usage --timeframe session --format json'),
        this.executeCommand('npx claude-flow@alpha agent metrics --format json'),
        this.executeCommand('npx claude-flow@alpha bottleneck analyze --format json')
      ];

      const [performance, tokens, agents, bottlenecks] = await Promise.all(metricsPromises);

      const metrics = {
        performance: this.parseJsonOutput(performance.output) || {},
        tokens: this.parseJsonOutput(tokens.output) || {},
        agents: this.parseJsonOutput(agents.output) || {},
        bottlenecks: this.parseJsonOutput(bottlenecks.output) || {},
        
        aggregated: {
          totalTokens: 0,
          avgResponseTime: 0,
          taskCompletionRate: 0,
          coordinationEfficiency: 0
        }
      };

      // Calculate aggregated metrics
      if (metrics.tokens.total) {
        metrics.aggregated.totalTokens = metrics.tokens.total;
      }

      if (metrics.performance.avgResponseTime) {
        metrics.aggregated.avgResponseTime = metrics.performance.avgResponseTime;
      }

      if (metrics.agents.length > 0) {
        const totalTasks = metrics.agents.reduce((sum, a) => sum + (a.tasksAssigned || 0), 0);
        const completedTasks = metrics.agents.reduce((sum, a) => sum + (a.tasksCompleted || 0), 0);
        metrics.aggregated.taskCompletionRate = totalTasks > 0 ? completedTasks / totalTasks : 0;
        
        const totalEfficiency = metrics.agents.reduce((sum, a) => sum + (a.efficiency || 0), 0);
        metrics.aggregated.coordinationEfficiency = totalEfficiency / metrics.agents.length;
      }

      return metrics;

    } catch (error) {
      console.warn('⚠️ Metrics aggregation failed:', error.message);
      return null;
    }
  }

  /**
   * Extract learnings and patterns from session
   */
  async extractSessionLearnings() {
    console.log('🧠 Extracting session learnings...');
    
    try {
      // Analyze neural patterns
      const patternsResult = await this.executeCommand('npx claude-flow@alpha neural patterns --action analyze --format json');
      const patterns = this.parseJsonOutput(patternsResult.output);

      // Analyze successful vs failed operations
      const successResult = await this.executeCommand(`npx claude-flow@alpha memory search --pattern "success" --limit 50`);
      const failureResult = await this.executeCommand(`npx claude-flow@alpha memory search --pattern "error" --limit 50`);
      
      const successes = this.parseJsonOutput(successResult.output);
      const failures = this.parseJsonOutput(failureResult.output);

      const learnings = {
        patterns: {
          identified: patterns?.patterns?.length || 0,
          topPatterns: patterns?.patterns?.slice(0, 5) || []
        },
        
        successRate: this.calculateSuccessRate(successes, failures),
        
        effectiveStrategies: this.identifyEffectiveStrategies(successes),
        
        commonIssues: this.identifyCommonIssues(failures),
        
        recommendations: this.generateLearningRecommendations(patterns, successes, failures)
      };

      // Train neural network with session learnings
      if (learnings.effectiveStrategies.length > 0) {
        await this.trainSessionPatterns(learnings);
      }

      return learnings;

    } catch (error) {
      console.warn('⚠️ Learning extraction failed:', error.message);
      return null;
    }
  }

  /**
   * Generate comprehensive session report
   */
  async generateSessionReport(results) {
    console.log('📄 Generating session report...');
    
    try {
      await fs.mkdir(this.reportsPath, { recursive: true });
      
      const reportPath = path.join(this.reportsPath, `session-${this.sessionId}.md`);
      
      const report = this.formatMarkdownReport(results);
      
      await fs.writeFile(reportPath, report);
      
      console.log(`✅ Report saved to: ${reportPath}`);
      
      // Also save JSON version
      const jsonPath = path.join(this.reportsPath, `session-${this.sessionId}.json`);
      await fs.writeFile(jsonPath, JSON.stringify(results, null, 2));
      
      return reportPath;

    } catch (error) {
      console.warn('⚠️ Report generation failed:', error.message);
      return null;
    }
  }

  /**
   * Format markdown report
   */
  formatMarkdownReport(results) {
    const { summary, metrics, learnings } = results;
    
    let report = `# Claude Flow Session Report\n\n`;
    report += `**Session ID:** ${this.sessionId}\n`;
    report += `**Date:** ${new Date().toLocaleDateString()}\n`;
    report += `**Duration:** ${summary?.duration || 'unknown'}\n\n`;
    
    // Executive Summary
    report += `## Executive Summary\n\n`;
    report += `- **Tasks Completed:** ${summary?.tasksCompleted || 0}\n`;
    report += `- **Files Modified:** ${summary?.filesModified || 0}\n`;
    report += `- **Total Edits:** ${summary?.totalEdits || 0}\n`;
    report += `- **Lines Changed:** ${summary?.linesChanged || 0}\n`;
    report += `- **Success Rate:** ${(learnings?.successRate || 0) * 100}%\n\n`;
    
    // Key Activities
    if (summary?.keyActivities?.length > 0) {
      report += `## Key Activities\n\n`;
      summary.keyActivities.forEach((activity, i) => {
        report += `${i + 1}. ${activity}\n`;
      });
      report += '\n';
    }
    
    // Performance Metrics
    report += `## Performance Metrics\n\n`;
    report += `- **Total Tokens Used:** ${metrics?.aggregated?.totalTokens || 0}\n`;
    report += `- **Avg Response Time:** ${metrics?.aggregated?.avgResponseTime || 0}ms\n`;
    report += `- **Task Completion Rate:** ${(metrics?.aggregated?.taskCompletionRate || 0) * 100}%\n`;
    report += `- **Coordination Efficiency:** ${(metrics?.aggregated?.coordinationEfficiency || 0) * 100}%\n\n`;
    
    // File Statistics
    if (summary?.fileTypes?.length > 0) {
      report += `## File Type Distribution\n\n`;
      report += '| File Type | Count |\n';
      report += '|-----------|-------|\n';
      summary.fileTypes.forEach(({ type, count }) => {
        report += `| ${type} | ${count} |\n`;
      });
      report += '\n';
    }
    
    // Learnings
    if (learnings) {
      report += `## Session Learnings\n\n`;
      
      if (learnings.effectiveStrategies?.length > 0) {
        report += `### Effective Strategies\n\n`;
        learnings.effectiveStrategies.forEach((strategy, i) => {
          report += `${i + 1}. ${strategy}\n`;
        });
        report += '\n';
      }
      
      if (learnings.commonIssues?.length > 0) {
        report += `### Common Issues\n\n`;
        learnings.commonIssues.forEach((issue, i) => {
          report += `${i + 1}. ${issue}\n`;
        });
        report += '\n';
      }
      
      if (learnings.recommendations?.length > 0) {
        report += `### Recommendations\n\n`;
        learnings.recommendations.forEach((rec, i) => {
          report += `${i + 1}. ${rec}\n`;
        });
        report += '\n';
      }
    }
    
    // Bottlenecks
    if (metrics?.bottlenecks?.bottlenecks?.length > 0) {
      report += `## Identified Bottlenecks\n\n`;
      metrics.bottlenecks.bottlenecks.forEach((bottleneck, i) => {
        report += `${i + 1}. **${bottleneck.type}** - ${bottleneck.description || 'No description'}\n`;
        report += `   - Severity: ${bottleneck.severity}\n`;
        report += `   - Impact: ${bottleneck.impact || 'Unknown'}\n\n`;
      });
    }
    
    // Agent Performance
    if (metrics?.agents?.length > 0) {
      report += `## Agent Performance\n\n`;
      report += '| Agent | Type | Tasks | Efficiency |\n';
      report += '|-------|------|-------|------------|\n';
      metrics.agents.forEach(agent => {
        report += `| ${agent.name} | ${agent.type} | ${agent.tasksCompleted || 0} | ${(agent.efficiency || 0) * 100}% |\n`;
      });
      report += '\n';
    }
    
    report += `---\n\n`;
    report += `*Report generated by Claude Flow v2.0.0*\n`;
    
    return report;
  }

  /**
   * Persist full session state
   */
  async persistFullSessionState(results) {
    console.log('💾 Persisting session state...');
    
    try {
      const state = {
        sessionId: this.sessionId,
        endTime: new Date().toISOString(),
        results,
        version: '2.0.0'
      };

      const command = `npx claude-flow@alpha memory persist --session-id "${this.sessionId}" --data '${JSON.stringify(state)}'`;
      const result = await this.executeCommand(command);
      
      if (result.success) {
        console.log('✅ Session state persisted successfully');
        return true;
      }

    } catch (error) {
      console.warn('⚠️ State persistence failed:', error.message);
    }
    
    return false;
  }

  /**
   * Cleanup session resources
   */
  async cleanupSessionResources() {
    console.log('🧹 Cleaning up session resources...');
    
    try {
      // Keep reports and memory, only clean temporary files
      const tempPath = path.join(this.swarmPath, 'temp');
      
      if (await this.pathExists(tempPath)) {
        await fs.rm(tempPath, { recursive: true, force: true });
      }
      
      console.log('✅ Temporary resources cleaned');
      return true;

    } catch (error) {
      console.warn('⚠️ Resource cleanup failed:', error.message);
      return false;
    }
  }

  /**
   * Display session summary in console
   */
  displaySessionSummary(results) {
    const { summary, metrics, learnings } = results;
    
    console.log('\n' + '='.repeat(70));
    console.log('🎯 SESSION SUMMARY');
    console.log('='.repeat(70));
    
    console.log(`\n📊 Overview:`);
    console.log(`   Session ID: ${this.sessionId}`);
    console.log(`   Duration: ${summary?.duration || 'unknown'}`);
    console.log(`   Tasks Completed: ${summary?.tasksCompleted || 0}`);
    console.log(`   Files Modified: ${summary?.filesModified || 0}`);
    console.log(`   Success Rate: ${Math.round((learnings?.successRate || 0) * 100)}%`);
    
    if (metrics?.aggregated) {
      console.log(`\n⚡ Performance:`);
      console.log(`   Total Tokens: ${metrics.aggregated.totalTokens}`);
      console.log(`   Avg Response Time: ${metrics.aggregated.avgResponseTime}ms`);
      console.log(`   Coordination Efficiency: ${Math.round(metrics.aggregated.coordinationEfficiency * 100)}%`);
    }
    
    if (summary?.keyActivities?.length > 0) {
      console.log(`\n🎯 Key Activities:`);
      summary.keyActivities.slice(0, 3).forEach((activity, i) => {
        console.log(`   ${i + 1}. ${activity}`);
      });
    }
    
    if (learnings?.recommendations?.length > 0) {
      console.log(`\n💡 Top Recommendations:`);
      learnings.recommendations.slice(0, 3).forEach((rec, i) => {
        console.log(`   ${i + 1}. ${rec}`);
      });
    }
    
    if (results.reportPath) {
      console.log(`\n📄 Full report saved to: ${results.reportPath}`);
    }
    
    console.log('\n' + '='.repeat(70));
    console.log('Thank you for using Claude Flow! 🚀');
    console.log('='.repeat(70) + '\n');
  }

  // Helper methods

  calculateSessionDuration(startTime) {
    if (!startTime) return 'unknown';
    
    const start = new Date(startTime);
    const end = new Date();
    const durationMs = end - start;
    
    const hours = Math.floor(durationMs / 3600000);
    const minutes = Math.floor((durationMs % 3600000) / 60000);
    const seconds = Math.floor((durationMs % 60000) / 1000);
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${seconds}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds}s`;
    } else {
      return `${seconds}s`;
    }
  }

  extractKeyActivities(tasks, edits, decisions) {
    const activities = [];
    
    if (tasks?.entries) {
      tasks.entries.slice(0, 5).forEach(task => {
        if (task.value?.description) {
          activities.push(task.value.description);
        }
      });
    }
    
    return activities;
  }

  getTopModifiedFiles(edits) {
    if (!edits?.entries) return [];
    
    const fileCounts = {};
    edits.entries.forEach(edit => {
      if (edit.value?.file) {
        fileCounts[edit.value.file] = (fileCounts[edit.value.file] || 0) + 1;
      }
    });
    
    return Object.entries(fileCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([file, count]) => ({ file, edits: count }));
  }

  extractAgentUsage(tasks) {
    const agents = new Set();
    
    if (tasks?.entries) {
      tasks.entries.forEach(task => {
        if (task.value?.agentsSpawned) {
          // Extract agent count
          agents.add(task.value.agentsSpawned);
        }
      });
    }
    
    return Array.from(agents);
  }

  calculateSuccessRate(successes, failures) {
    const successCount = successes?.entries?.length || 0;
    const failureCount = failures?.entries?.length || 0;
    const total = successCount + failureCount;
    
    return total > 0 ? successCount / total : 0;
  }

  identifyEffectiveStrategies(successes) {
    const strategies = [];
    
    if (successes?.entries) {
      // Analyze successful patterns
      const patterns = {};
      successes.entries.forEach(entry => {
        if (entry.value?.strategy || entry.value?.pattern) {
          const key = entry.value.strategy || entry.value.pattern;
          patterns[key] = (patterns[key] || 0) + 1;
        }
      });
      
      // Get top strategies
      Object.entries(patterns)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
        .forEach(([strategy, count]) => {
          strategies.push(`${strategy} (used ${count} times)`);
        });
    }
    
    return strategies;
  }

  identifyCommonIssues(failures) {
    const issues = [];
    
    if (failures?.entries) {
      const errorTypes = {};
      failures.entries.forEach(entry => {
        if (entry.value?.error || entry.value?.issue) {
          const key = entry.value.error || entry.value.issue;
          errorTypes[key] = (errorTypes[key] || 0) + 1;
        }
      });
      
      Object.entries(errorTypes)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
        .forEach(([issue, count]) => {
          issues.push(`${issue} (occurred ${count} times)`);
        });
    }
    
    return issues;
  }

  generateLearningRecommendations(patterns, successes, failures) {
    const recommendations = [];
    
    // Based on patterns
    if (patterns?.patterns?.length > 5) {
      recommendations.push('Consider creating reusable templates for frequently used patterns');
    }
    
    // Based on success rate
    const successRate = this.calculateSuccessRate(successes, failures);
    if (successRate < 0.8) {
      recommendations.push('Implement more robust error handling and recovery mechanisms');
    }
    
    // Based on common issues
    if (failures?.entries?.length > 10) {
      recommendations.push('Review and address recurring failure patterns to improve reliability');
    }
    
    // General recommendations
    if (recommendations.length === 0) {
      recommendations.push('Continue monitoring performance metrics for optimization opportunities');
      recommendations.push('Consider documenting successful strategies for team knowledge sharing');
    }
    
    return recommendations;
  }

  async trainSessionPatterns(learnings) {
    try {
      const patterns = {
        effective: learnings.effectiveStrategies,
        issues: learnings.commonIssues,
        successRate: learnings.successRate
      };
      
      const command = `npx claude-flow@alpha neural train --patterns '${JSON.stringify(patterns)}' --type session-learning`;
      await this.executeCommand(command);
      
    } catch (error) {
      console.warn('⚠️ Pattern training failed:', error.message);
    }
  }

  async pathExists(path) {
    try {
      await fs.access(path);
      return true;
    } catch {
      return false;
    }
  }

  parseJsonOutput(output) {
    try {
      const jsonMatch = output.match(/\{[\s\S]*\}|\[[\s\S]*\]/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
    } catch (error) {
      // Silent fail
    }
    return null;
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
  const hook = new SessionEndHook();
  
  // Parse command line arguments
  const args = process.argv.slice(2);
  const options = {};
  
  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--generate-summary':
        options.generateSummary = args[++i] !== 'false';
        break;
      case '--persist-state':
        options.persistState = args[++i] !== 'false';
        break;
      case '--export-metrics':
        options.exportMetrics = args[++i] !== 'false';
        break;
      case '--generate-report':
        options.generateReport = args[++i] !== 'false';
        break;
      case '--cleanup-resources':
        options.cleanupResources = true;
        break;
      case '--extract-learnings':
        options.extractLearnings = args[++i] !== 'false';
        break;
    }
  }
  
  hook.execute(options).then(result => {
    process.exit(result.success ? 0 : 1);
  });
}

export default SessionEndHook;