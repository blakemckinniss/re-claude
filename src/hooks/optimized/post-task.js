#!/usr/bin/env node

/**
 * Optimized Post-Task Hook with Claude Flow MCP Integration
 * Features:
 * - Comprehensive task summary generation
 * - Performance analytics and bottleneck detection
 * - Neural pattern analysis and training
 * - Memory persistence and knowledge sharing
 * - GitHub integration for automated commits
 * - Swarm coordination metrics
 */

import { spawn } from 'child_process';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class PostTaskHook {
  constructor() {
    this.swarmPath = path.join(process.cwd(), '.swarm');
    this.memoryDb = path.join(this.swarmPath, 'memory.db');
    this.sessionId = process.env.CLAUDE_FLOW_SESSION || `session-${Date.now()}`;
  }

  /**
   * Execute post-task hook with full MCP integration
   */
  async execute(options = {}) {
    const {
      taskId = `task-${Date.now()}`,
      analyzePerformance = true,
      generateSummary = true,
      persistState = true,
      exportMetrics = true,
      trainNeural = true,
      createGithubCommit = false,
      cleanupSwarm = false
    } = options;

    console.log('🏁 Executing optimized post-task hook...');
    console.log(`📋 Task ID: ${taskId}`);
    console.log(`🆔 Session ID: ${this.sessionId}`);

    const startTime = Date.now();
    const results = {
      taskId,
      sessionId: this.sessionId,
      summary: null,
      performance: null,
      metrics: null,
      neuralInsights: null,
      statePersisted: false,
      githubCommit: null,
      swarmCleaned: false,
      recommendations: []
    };

    try {
      // Execute all post-task operations
      const operations = [];

      // 1. Collect comprehensive metrics
      if (exportMetrics || analyzePerformance) {
        operations.push(this.collectComprehensiveMetrics(taskId));
      }

      // 2. Analyze swarm performance
      if (analyzePerformance) {
        operations.push(this.analyzeSwarmPerformance());
      }

      // 3. Generate task summary
      if (generateSummary) {
        operations.push(this.generateTaskSummary(taskId));
      }

      // Execute parallel operations
      const [metrics, performance, summary] = await Promise.all(operations);

      results.metrics = metrics;
      results.performance = performance;
      results.summary = summary;

      // Sequential operations that depend on collected data
      
      // 4. Detect bottlenecks and generate recommendations
      if (performance) {
        const bottlenecks = await this.detectBottlenecks(performance);
        results.recommendations = this.generateRecommendations(bottlenecks);
      }

      // 5. Train neural patterns from task execution
      if (trainNeural && metrics) {
        results.neuralInsights = await this.trainNeuralPatterns(metrics, performance);
      }

      // 6. Persist session state
      if (persistState) {
        results.statePersisted = await this.persistSessionState(results);
      }

      // 7. Export detailed metrics
      if (exportMetrics) {
        await this.exportDetailedMetrics(results);
      }

      // 8. Create GitHub commit if requested
      if (createGithubCommit) {
        results.githubCommit = await this.createAutomatedCommit(summary);
      }

      // 9. Cleanup swarm resources
      if (cleanupSwarm) {
        results.swarmCleaned = await this.cleanupSwarmResources();
      }

      // 10. Generate final report
      const report = await this.generateFinalReport(results);
      
      // Display summary
      this.displayTaskSummary(report);

      return {
        success: true,
        taskId,
        sessionId: this.sessionId,
        duration: Date.now() - startTime,
        report
      };

    } catch (error) {
      console.error('❌ Post-task hook error:', error);
      return {
        success: false,
        error: error.message,
        ...results
      };
    }
  }

  /**
   * Collect comprehensive metrics from the task execution
   */
  async collectComprehensiveMetrics(taskId) {
    console.log('📊 Collecting comprehensive metrics...');
    
    try {
      // Collect various metrics in parallel
      const metricsPromises = [
        this.executeCommand('npx claude-flow@alpha agent metrics --format json'),
        this.executeCommand('npx claude-flow@alpha performance report --format json'),
        this.executeCommand('npx claude-flow@alpha token usage --format json'),
        this.executeCommand('npx claude-flow@alpha memory usage --action list --format json')
      ];

      const [agentMetrics, performanceReport, tokenUsage, memoryUsage] = await Promise.all(metricsPromises);

      // Parse and combine metrics
      const metrics = {
        agents: this.parseJsonOutput(agentMetrics.output),
        performance: this.parseJsonOutput(performanceReport.output),
        tokens: this.parseJsonOutput(tokenUsage.output),
        memory: this.parseJsonOutput(memoryUsage.output),
        timestamp: new Date().toISOString()
      };

      // Calculate aggregated stats
      metrics.aggregated = {
        totalAgents: metrics.agents?.length || 0,
        totalTokens: metrics.tokens?.total || 0,
        avgResponseTime: metrics.performance?.avgResponseTime || 0,
        memoryEntries: metrics.memory?.count || 0
      };

      return metrics;

    } catch (error) {
      console.warn('⚠️ Metrics collection partially failed:', error.message);
      return null;
    }
  }

  /**
   * Analyze swarm performance and coordination efficiency
   */
  async analyzeSwarmPerformance() {
    console.log('🐝 Analyzing swarm performance...');
    
    try {
      const result = await this.executeCommand('npx claude-flow@alpha swarm monitor --duration 1 --format json');
      const swarmData = this.parseJsonOutput(result.output);

      if (!swarmData) return null;

      // Calculate performance metrics
      const performance = {
        topology: swarmData.topology,
        efficiency: this.calculateEfficiency(swarmData),
        coordination: {
          messagesPassed: swarmData.messages?.total || 0,
          avgLatency: swarmData.messages?.avgLatency || 0,
          syncRate: swarmData.sync?.rate || 0
        },
        agents: swarmData.agents?.map(agent => ({
          name: agent.name,
          type: agent.type,
          tasksCompleted: agent.tasks?.completed || 0,
          efficiency: agent.efficiency || 0,
          status: agent.status
        })),
        bottlenecks: []
      };

      // Identify bottlenecks
      if (swarmData.agents) {
        performance.bottlenecks = swarmData.agents
          .filter(agent => agent.efficiency < 0.7 || agent.waitTime > 5000)
          .map(agent => ({
            agent: agent.name,
            issue: agent.efficiency < 0.7 ? 'low-efficiency' : 'high-wait-time',
            impact: 'medium'
          }));
      }

      return performance;

    } catch (error) {
      console.warn('⚠️ Swarm analysis failed:', error.message);
      return null;
    }
  }

  /**
   * Generate comprehensive task summary
   */
  async generateTaskSummary(taskId) {
    console.log('📝 Generating task summary...');
    
    try {
      // Retrieve task context and history
      const contextResult = await this.executeCommand(`npx claude-flow@alpha memory retrieve --key "task/${this.sessionId}/context"`);
      const context = this.parseJsonOutput(contextResult.output);

      // Retrieve edit history
      const editsResult = await this.executeCommand(`npx claude-flow@alpha memory search --pattern "edit/${this.sessionId}" --limit 50`);
      const edits = this.parseJsonOutput(editsResult.output);

      // Generate summary
      const summary = {
        taskId,
        description: context?.description || 'Unknown task',
        startTime: context?.timestamp,
        endTime: new Date().toISOString(),
        duration: this.calculateDuration(context?.timestamp),
        
        statistics: {
          filesEdited: new Set(edits?.entries?.map(e => e.value?.file) || []).size,
          totalEdits: edits?.entries?.length || 0,
          agentsUsed: context?.agentsSpawned || 0,
          topology: context?.topology || 'unknown'
        },
        
        filesModified: [...new Set(edits?.entries?.map(e => e.value?.file) || [])],
        
        keyDecisions: [],
        achievements: [],
        challenges: []
      };

      // Extract key decisions from memory
      const decisionsResult = await this.executeCommand(`npx claude-flow@alpha memory search --pattern "decision" --limit 10`);
      const decisions = this.parseJsonOutput(decisionsResult.output);
      
      if (decisions?.entries) {
        summary.keyDecisions = decisions.entries.map(d => ({
          timestamp: d.timestamp,
          decision: d.value?.decision || d.value?.message || 'Unknown decision'
        }));
      }

      return summary;

    } catch (error) {
      console.warn('⚠️ Summary generation failed:', error.message);
      return null;
    }
  }

  /**
   * Detect performance bottlenecks
   */
  async detectBottlenecks(performance) {
    console.log('🔍 Detecting bottlenecks...');
    
    const bottlenecks = [];

    // Agent-level bottlenecks
    if (performance.agents) {
      performance.agents.forEach(agent => {
        if (agent.efficiency < 0.6) {
          bottlenecks.push({
            type: 'agent-efficiency',
            component: agent.name,
            severity: 'high',
            metric: agent.efficiency,
            threshold: 0.6
          });
        }
      });
    }

    // Coordination bottlenecks
    if (performance.coordination) {
      if (performance.coordination.avgLatency > 1000) {
        bottlenecks.push({
          type: 'coordination-latency',
          component: 'swarm-messaging',
          severity: 'medium',
          metric: performance.coordination.avgLatency,
          threshold: 1000
        });
      }

      if (performance.coordination.syncRate < 0.8) {
        bottlenecks.push({
          type: 'sync-rate',
          component: 'swarm-synchronization',
          severity: 'medium',
          metric: performance.coordination.syncRate,
          threshold: 0.8
        });
      }
    }

    // Use MCP bottleneck detection
    try {
      const result = await this.executeCommand('npx claude-flow@alpha bottleneck detect --format json');
      const detected = this.parseJsonOutput(result.output);
      
      if (detected?.bottlenecks) {
        bottlenecks.push(...detected.bottlenecks);
      }
    } catch (error) {
      console.warn('⚠️ MCP bottleneck detection failed:', error.message);
    }

    return bottlenecks;
  }

  /**
   * Generate recommendations based on bottlenecks
   */
  generateRecommendations(bottlenecks) {
    const recommendations = [];

    bottlenecks.forEach(bottleneck => {
      switch (bottleneck.type) {
        case 'agent-efficiency':
          recommendations.push({
            category: 'performance',
            priority: 'high',
            suggestion: `Optimize ${bottleneck.component} agent: Consider reducing task complexity or spawning additional specialized agents`,
            impact: 'Could improve overall task completion time by 20-30%'
          });
          break;

        case 'coordination-latency':
          recommendations.push({
            category: 'architecture',
            priority: 'medium',
            suggestion: 'High coordination latency detected: Consider switching to a more efficient topology (e.g., from mesh to hierarchical)',
            impact: 'Could reduce message passing overhead by 40%'
          });
          break;

        case 'sync-rate':
          recommendations.push({
            category: 'coordination',
            priority: 'medium',
            suggestion: 'Low synchronization rate: Implement more frequent checkpoints or use event-driven coordination',
            impact: 'Could improve agent coordination efficiency by 25%'
          });
          break;

        case 'memory-usage':
          recommendations.push({
            category: 'resource',
            priority: 'low',
            suggestion: 'High memory usage detected: Implement periodic memory cleanup or use more efficient data structures',
            impact: 'Could reduce memory footprint by 30-40%'
          });
          break;
      }
    });

    // Add general recommendations
    if (recommendations.length === 0) {
      recommendations.push({
        category: 'general',
        priority: 'low',
        suggestion: 'Task completed efficiently. Consider documenting successful patterns for future reuse.',
        impact: 'Could improve future task execution by 10-15%'
      });
    }

    return recommendations;
  }

  /**
   * Train neural patterns from task execution
   */
  async trainNeuralPatterns(metrics, performance) {
    console.log('🧠 Training neural patterns...');
    
    try {
      const patterns = {
        taskPattern: {
          topology: performance?.topology,
          agentCount: metrics?.aggregated?.totalAgents,
          efficiency: performance?.efficiency,
          duration: metrics?.performance?.totalDuration
        },
        successPatterns: [],
        failurePatterns: []
      };

      // Identify successful patterns
      if (performance?.agents) {
        patterns.successPatterns = performance.agents
          .filter(a => a.efficiency > 0.8)
          .map(a => ({
            agentType: a.type,
            taskType: 'unknown', // Would need task classification
            efficiency: a.efficiency
          }));
      }

      // Train the neural network
      const result = await this.executeCommand(`npx claude-flow@alpha neural train --patterns '${JSON.stringify(patterns)}' --type task-completion`);
      
      if (result.success) {
        const trainResult = this.parseJsonOutput(result.output);
        return {
          patternsTrained: patterns.successPatterns.length + patterns.failurePatterns.length,
          accuracy: trainResult?.accuracy || 'unknown',
          insights: trainResult?.insights || []
        };
      }

    } catch (error) {
      console.warn('⚠️ Neural training failed:', error.message);
    }

    return null;
  }

  /**
   * Persist session state for future reference
   */
  async persistSessionState(results) {
    console.log('💾 Persisting session state...');
    
    try {
      const state = {
        sessionId: this.sessionId,
        taskId: results.taskId,
        timestamp: new Date().toISOString(),
        summary: results.summary,
        performance: results.performance,
        metrics: results.metrics,
        recommendations: results.recommendations,
        neuralInsights: results.neuralInsights
      };

      const command = `npx claude-flow@alpha memory persist --session-id "${this.sessionId}" --data '${JSON.stringify(state)}'`;
      const result = await this.executeCommand(command);
      
      return result.success;

    } catch (error) {
      console.warn('⚠️ State persistence failed:', error.message);
      return false;
    }
  }

  /**
   * Export detailed metrics for analysis
   */
  async exportDetailedMetrics(results) {
    console.log('📊 Exporting detailed metrics...');
    
    try {
      const exportPath = path.join(this.swarmPath, 'metrics', `${results.taskId}.json`);
      await fs.mkdir(path.dirname(exportPath), { recursive: true });
      
      const metricsData = {
        ...results,
        exportTime: new Date().toISOString(),
        version: '2.0.0'
      };

      await fs.writeFile(exportPath, JSON.stringify(metricsData, null, 2));
      console.log(`✅ Metrics exported to: ${exportPath}`);

    } catch (error) {
      console.warn('⚠️ Metrics export failed:', error.message);
    }
  }

  /**
   * Create automated GitHub commit
   */
  async createAutomatedCommit(summary) {
    console.log('🔗 Creating automated GitHub commit...');
    
    try {
      // Check for uncommitted changes
      const statusResult = await this.executeCommand('git status --porcelain');
      
      if (!statusResult.output.trim()) {
        console.log('ℹ️ No changes to commit');
        return null;
      }

      // Generate commit message
      const commitMessage = this.generateCommitMessage(summary);
      
      // Stage all changes
      await this.executeCommand('git add -A');
      
      // Create commit
      const commitCommand = `git commit -m "${commitMessage}" -m "🤖 Automated commit by Claude Flow\n\nSession: ${this.sessionId}"`;
      const commitResult = await this.executeCommand(commitCommand);
      
      if (commitResult.success) {
        // Get commit hash
        const hashResult = await this.executeCommand('git rev-parse HEAD');
        return {
          success: true,
          hash: hashResult.output.trim(),
          message: commitMessage
        };
      }

    } catch (error) {
      console.warn('⚠️ Automated commit failed:', error.message);
    }

    return null;
  }

  /**
   * Generate commit message from task summary
   */
  generateCommitMessage(summary) {
    if (!summary) {
      return `chore: Complete task ${this.sessionId}`;
    }

    const action = summary.description.toLowerCase().includes('fix') ? 'fix' :
                  summary.description.toLowerCase().includes('feat') ? 'feat' :
                  summary.description.toLowerCase().includes('refactor') ? 'refactor' :
                  'chore';

    const scope = summary.filesModified?.length > 0 ? 
      path.dirname(summary.filesModified[0]).split('/').pop() : 
      'general';

    const description = summary.description.length > 50 ? 
      summary.description.substring(0, 47) + '...' : 
      summary.description;

    return `${action}(${scope}): ${description}`;
  }

  /**
   * Cleanup swarm resources
   */
  async cleanupSwarmResources() {
    console.log('🧹 Cleaning up swarm resources...');
    
    try {
      const result = await this.executeCommand('npx claude-flow@alpha swarm destroy --force');
      return result.success;
    } catch (error) {
      console.warn('⚠️ Swarm cleanup failed:', error.message);
      return false;
    }
  }

  /**
   * Generate final report
   */
  async generateFinalReport(results) {
    const report = {
      overview: {
        taskId: results.taskId,
        sessionId: results.sessionId,
        success: true,
        duration: results.summary?.duration || 'unknown'
      },
      
      summary: results.summary,
      
      performance: {
        overall: results.performance?.efficiency || 'unknown',
        bottlenecks: results.performance?.bottlenecks?.length || 0,
        recommendations: results.recommendations.length
      },
      
      metrics: {
        totalAgents: results.metrics?.aggregated?.totalAgents || 0,
        totalTokens: results.metrics?.aggregated?.totalTokens || 0,
        filesModified: results.summary?.statistics?.filesEdited || 0,
        totalEdits: results.summary?.statistics?.totalEdits || 0
      },
      
      outcomes: {
        neuralPatternsTrained: results.neuralInsights?.patternsTrained || 0,
        statePersisted: results.statePersisted,
        githubCommit: results.githubCommit?.hash || null
      }
    };

    return report;
  }

  /**
   * Display task summary in console
   */
  displayTaskSummary(report) {
    console.log('\n' + '='.repeat(60));
    console.log('📊 TASK COMPLETION SUMMARY');
    console.log('='.repeat(60));
    
    console.log(`\n📋 Task: ${report.summary?.description || 'Unknown'}`);
    console.log(`⏱️  Duration: ${report.overview.duration}`);
    console.log(`🆔 Session: ${report.overview.sessionId}`);
    
    console.log('\n📈 Performance Metrics:');
    console.log(`   • Overall Efficiency: ${report.performance.overall}`);
    console.log(`   • Bottlenecks Found: ${report.performance.bottlenecks}`);
    console.log(`   • Recommendations: ${report.performance.recommendations}`);
    
    console.log('\n📊 Task Statistics:');
    console.log(`   • Agents Used: ${report.metrics.totalAgents}`);
    console.log(`   • Tokens Consumed: ${report.metrics.totalTokens}`);
    console.log(`   • Files Modified: ${report.metrics.filesModified}`);
    console.log(`   • Total Edits: ${report.metrics.totalEdits}`);
    
    console.log('\n🎯 Outcomes:');
    console.log(`   • Neural Patterns Trained: ${report.outcomes.neuralPatternsTrained}`);
    console.log(`   • State Persisted: ${report.outcomes.statePersisted ? '✅' : '❌'}`);
    console.log(`   • GitHub Commit: ${report.outcomes.githubCommit || 'None'}`);
    
    if (report.summary?.keyDecisions?.length > 0) {
      console.log('\n🔑 Key Decisions:');
      report.summary.keyDecisions.slice(0, 3).forEach((d, i) => {
        console.log(`   ${i + 1}. ${d.decision}`);
      });
    }
    
    console.log('\n' + '='.repeat(60));
  }

  /**
   * Helper: Parse JSON output safely
   */
  parseJsonOutput(output) {
    try {
      // Find JSON in output (might have other text)
      const jsonMatch = output.match(/\{[\s\S]*\}|\[[\s\S]*\]/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
    } catch (error) {
      // Silent fail
    }
    return null;
  }

  /**
   * Helper: Calculate efficiency score
   */
  calculateEfficiency(swarmData) {
    if (!swarmData.agents || swarmData.agents.length === 0) return 0;
    
    const totalEfficiency = swarmData.agents.reduce((sum, agent) => 
      sum + (agent.efficiency || 0), 0
    );
    
    return totalEfficiency / swarmData.agents.length;
  }

  /**
   * Helper: Calculate duration from timestamp
   */
  calculateDuration(startTime) {
    if (!startTime) return 'unknown';
    
    const start = new Date(startTime);
    const end = new Date();
    const durationMs = end - start;
    
    const minutes = Math.floor(durationMs / 60000);
    const seconds = Math.floor((durationMs % 60000) / 1000);
    
    return `${minutes}m ${seconds}s`;
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
  const hook = new PostTaskHook();
  
  // Parse command line arguments
  const args = process.argv.slice(2);
  const options = {};
  
  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--task-id':
        options.taskId = args[++i];
        break;
      case '--analyze-performance':
        options.analyzePerformance = args[++i] !== 'false';
        break;
      case '--generate-summary':
        options.generateSummary = args[++i] !== 'false';
        break;
      case '--persist-state':
        options.persistState = args[++i] !== 'false';
        break;
      case '--export-metrics':
        options.exportMetrics = args[++i] !== 'false';
        break;
      case '--train-neural':
        options.trainNeural = args[++i] !== 'false';
        break;
      case '--github-commit':
        options.createGithubCommit = true;
        break;
      case '--cleanup-swarm':
        options.cleanupSwarm = true;
        break;
    }
  }
  
  hook.execute(options).then(result => {
    console.log('\n✅ Post-task hook completed');
    process.exit(result.success ? 0 : 1);
  });
}

export default PostTaskHook;