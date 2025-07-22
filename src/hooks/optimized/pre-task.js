#!/usr/bin/env node

/**
 * Optimized Pre-Task Hook with Claude Flow MCP Integration
 * Features:
 * - Parallel execution patterns
 * - MCP tool integration
 * - Memory persistence
 * - Neural pattern training
 * - GitHub automation
 * - Smart agent spawning
 */

import { spawn } from 'child_process';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class PreTaskHook {
  constructor() {
    this.swarmPath = path.join(process.cwd(), '.swarm');
    this.memoryDb = path.join(this.swarmPath, 'memory.db');
    this.sessionId = `session-${Date.now()}-${Math.random().toString(36).substring(7)}`;
  }

  /**
   * Execute pre-task hook with full MCP integration
   */
  async execute(options = {}) {
    const {
      description = 'Unnamed task',
      autoSpawnAgents = true,
      loadMemory = true,
      optimizeTopology = true,
      estimateComplexity = true,
      useGithubIntegration = false,
      parallelExecution = true
    } = options;

    console.log('🔄 Executing optimized pre-task hook...');
    console.log(`📋 Task: ${description}`);
    console.log(`🆔 Session ID: ${this.sessionId}`);

    try {
      // Ensure .swarm directory exists
      await fs.mkdir(this.swarmPath, { recursive: true });

      // Execute all pre-task operations in parallel
      const operations = [];

      // 1. Estimate task complexity
      if (estimateComplexity) {
        operations.push(this.estimateTaskComplexity(description));
      }

      // 2. Load relevant memory
      if (loadMemory) {
        operations.push(this.loadRelevantMemory(description));
      }

      // 3. Optimize topology selection
      if (optimizeTopology) {
        operations.push(this.selectOptimalTopology(description));
      }

      // 4. GitHub integration check
      if (useGithubIntegration) {
        operations.push(this.initializeGithubContext());
      }

      // Execute all operations in parallel
      const [complexity, memory, topology, githubContext] = await Promise.all(operations);

      // 5. Auto-spawn agents based on analysis
      let agentsSpawned = 0;
      if (autoSpawnAgents && complexity) {
        agentsSpawned = await this.autoSpawnAgents(complexity, topology);
      }

      // 6. Initialize MCP swarm coordination
      const swarmInit = await this.initializeSwarmCoordination(topology, agentsSpawned);

      // 7. Store task context in memory
      await this.storeTaskContext({
        sessionId: this.sessionId,
        description,
        complexity,
        topology,
        agentsSpawned,
        githubContext,
        memoryLoaded: !!memory,
        timestamp: new Date().toISOString()
      });

      // 8. Setup neural pattern training
      if (complexity && complexity.patterns) {
        await this.initializeNeuralTraining(complexity.patterns);
      }

      return {
        continue: true,
        sessionId: this.sessionId,
        topology: topology.type,
        agentsSpawned,
        complexity: complexity.level,
        estimatedMinutes: complexity.estimatedMinutes,
        memoryLoaded: !!memory,
        githubEnabled: !!githubContext,
        parallelMode: parallelExecution,
        swarmInitialized: swarmInit.success
      };

    } catch (error) {
      console.error('❌ Pre-task hook error:', error);
      return {
        continue: false,
        error: error.message
      };
    }
  }

  /**
   * Estimate task complexity using neural patterns
   */
  async estimateTaskComplexity(description) {
    console.log('🧠 Analyzing task complexity...');
    
    // Analyze keywords and patterns
    const complexityIndicators = {
      simple: ['fix', 'update', 'change', 'modify', 'add'],
      medium: ['implement', 'create', 'build', 'develop', 'integrate'],
      complex: ['refactor', 'optimize', 'architect', 'redesign', 'migrate'],
      critical: ['security', 'performance', 'scale', 'distributed', 'real-time']
    };

    let level = 'simple';
    let estimatedMinutes = 15;
    let patterns = [];

    for (const [complexity, keywords] of Object.entries(complexityIndicators)) {
      if (keywords.some(keyword => description.toLowerCase().includes(keyword))) {
        level = complexity;
        patterns.push(...keywords.filter(k => description.toLowerCase().includes(k)));
        
        // Estimate time based on complexity
        switch (complexity) {
          case 'simple': estimatedMinutes = 15; break;
          case 'medium': estimatedMinutes = 45; break;
          case 'complex': estimatedMinutes = 120; break;
          case 'critical': estimatedMinutes = 240; break;
        }
      }
    }

    // Check for multi-component tasks
    const components = ['frontend', 'backend', 'database', 'api', 'auth', 'testing'];
    const detectedComponents = components.filter(c => description.toLowerCase().includes(c));
    if (detectedComponents.length > 2) {
      level = 'complex';
      estimatedMinutes = Math.max(estimatedMinutes, 90);
    }

    return {
      level,
      estimatedMinutes,
      patterns,
      components: detectedComponents,
      requiresCoordination: detectedComponents.length > 1
    };
  }

  /**
   * Load relevant memory from previous sessions
   */
  async loadRelevantMemory(description) {
    console.log('💾 Loading relevant memory...');
    
    try {
      // Use MCP memory tool to search for relevant context
      const searchPatterns = description.split(' ')
        .filter(word => word.length > 3)
        .slice(0, 5);

      const memoryEntries = [];
      
      // Search for each pattern
      for (const pattern of searchPatterns) {
        const command = `npx claude-flow@alpha memory search --pattern "${pattern}" --limit 5`;
        const result = await this.executeCommand(command);
        if (result.success && result.entries) {
          memoryEntries.push(...result.entries);
        }
      }

      // Deduplicate and sort by relevance
      const uniqueEntries = Array.from(
        new Map(memoryEntries.map(e => [e.key, e])).values()
      ).sort((a, b) => b.relevance - a.relevance).slice(0, 10);

      return {
        entries: uniqueEntries,
        totalFound: uniqueEntries.length
      };

    } catch (error) {
      console.warn('⚠️ Memory loading failed:', error.message);
      return null;
    }
  }

  /**
   * Select optimal swarm topology based on task analysis
   */
  async selectOptimalTopology(description) {
    console.log('🔄 Selecting optimal topology...');
    
    const topologies = {
      mesh: {
        suitable: ['collaborative', 'research', 'exploration', 'brainstorm'],
        maxAgents: 6,
        coordination: 'distributed'
      },
      hierarchical: {
        suitable: ['complex', 'multi-layer', 'structured', 'organized'],
        maxAgents: 10,
        coordination: 'centralized'
      },
      ring: {
        suitable: ['sequential', 'pipeline', 'workflow', 'process'],
        maxAgents: 8,
        coordination: 'circular'
      },
      star: {
        suitable: ['centralized', 'focused', 'single-goal', 'simple'],
        maxAgents: 5,
        coordination: 'hub-spoke'
      }
    };

    // Analyze task description for topology hints
    let selectedTopology = 'mesh'; // default
    let maxScore = 0;

    for (const [topology, config] of Object.entries(topologies)) {
      const score = config.suitable.reduce((acc, keyword) => {
        return acc + (description.toLowerCase().includes(keyword) ? 1 : 0);
      }, 0);

      if (score > maxScore) {
        maxScore = score;
        selectedTopology = topology;
      }
    }

    // Check for specific patterns
    if (description.toLowerCase().includes('api') || description.toLowerCase().includes('service')) {
      selectedTopology = 'hierarchical';
    } else if (description.toLowerCase().includes('test') || description.toLowerCase().includes('validate')) {
      selectedTopology = 'ring';
    }

    return {
      type: selectedTopology,
      config: topologies[selectedTopology],
      confidence: maxScore > 0 ? 'high' : 'medium'
    };
  }

  /**
   * Initialize GitHub context if working with repositories
   */
  async initializeGithubContext() {
    console.log('🔗 Initializing GitHub context...');
    
    try {
      // Check if we're in a git repository
      const gitStatus = await this.executeCommand('git status --porcelain');
      const gitRemote = await this.executeCommand('git remote get-url origin');
      
      if (gitRemote.success && gitRemote.output) {
        const repoMatch = gitRemote.output.match(/github\.com[:/](.+)\.git/);
        if (repoMatch) {
          const [owner, repo] = repoMatch[1].split('/');
          
          return {
            enabled: true,
            owner,
            repo,
            hasChanges: gitStatus.output.length > 0,
            branch: await this.getCurrentBranch()
          };
        }
      }
    } catch (error) {
      console.warn('⚠️ GitHub context not available');
    }
    
    return null;
  }

  /**
   * Auto-spawn agents based on complexity analysis
   */
  async autoSpawnAgents(complexity, topology) {
    console.log('🤖 Auto-spawning agents...');
    
    const agentConfigs = {
      simple: [
        { type: 'coder', name: 'Implementation' },
        { type: 'tester', name: 'Validation' }
      ],
      medium: [
        { type: 'architect', name: 'Design' },
        { type: 'coder', name: 'Backend' },
        { type: 'coder', name: 'Frontend' },
        { type: 'tester', name: 'QA' }
      ],
      complex: [
        { type: 'coordinator', name: 'Lead' },
        { type: 'architect', name: 'System Design' },
        { type: 'coder', name: 'Core Implementation' },
        { type: 'coder', name: 'Integration' },
        { type: 'analyst', name: 'Performance' },
        { type: 'tester', name: 'Testing' },
        { type: 'reviewer', name: 'Code Review' }
      ],
      critical: [
        { type: 'coordinator', name: 'Project Manager' },
        { type: 'architect', name: 'Chief Architect' },
        { type: 'researcher', name: 'Tech Research' },
        { type: 'coder', name: 'Senior Dev 1' },
        { type: 'coder', name: 'Senior Dev 2' },
        { type: 'analyst', name: 'Security Analyst' },
        { type: 'optimizer', name: 'Performance Expert' },
        { type: 'tester', name: 'QA Lead' },
        { type: 'documenter', name: 'Tech Writer' },
        { type: 'monitor', name: 'DevOps' }
      ]
    };

    const agents = agentConfigs[complexity.level] || agentConfigs.simple;
    
    // Spawn agents in parallel using MCP tools
    const spawnPromises = agents.map(agent => 
      this.executeCommand(`npx claude-flow@alpha agent spawn --type ${agent.type} --name "${agent.name}"`)
    );
    
    await Promise.all(spawnPromises);
    
    return agents.length;
  }

  /**
   * Initialize swarm coordination with MCP
   */
  async initializeSwarmCoordination(topology, agentCount) {
    console.log('🐝 Initializing swarm coordination...');
    
    const command = `npx claude-flow@alpha swarm init --topology ${topology.type} --max-agents ${agentCount || topology.config.maxAgents} --strategy adaptive`;
    
    return await this.executeCommand(command);
  }

  /**
   * Store task context in memory
   */
  async storeTaskContext(context) {
    console.log('💾 Storing task context...');
    
    const command = `npx claude-flow@alpha memory store --key "task/${this.sessionId}/context" --value '${JSON.stringify(context)}'`;
    
    return await this.executeCommand(command);
  }

  /**
   * Initialize neural pattern training
   */
  async initializeNeuralTraining(patterns) {
    console.log('🧠 Initializing neural training...');
    
    const command = `npx claude-flow@alpha neural train --patterns '${JSON.stringify(patterns)}' --type coordination`;
    
    return await this.executeCommand(command);
  }

  /**
   * Get current git branch
   */
  async getCurrentBranch() {
    const result = await this.executeCommand('git branch --show-current');
    return result.success ? result.output.trim() : 'main';
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
  const hook = new PreTaskHook();
  
  // Parse command line arguments
  const args = process.argv.slice(2);
  const options = {};
  
  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--description':
      case '-d':
        options.description = args[++i];
        break;
      case '--auto-spawn-agents':
        options.autoSpawnAgents = args[++i] !== 'false';
        break;
      case '--load-memory':
        options.loadMemory = true;
        break;
      case '--optimize-topology':
        options.optimizeTopology = true;
        break;
      case '--estimate-complexity':
        options.estimateComplexity = true;
        break;
      case '--github-integration':
        options.useGithubIntegration = true;
        break;
      case '--parallel':
        options.parallelExecution = true;
        break;
    }
  }
  
  hook.execute(options).then(result => {
    console.log('\n✅ Pre-task hook completed:', JSON.stringify(result, null, 2));
    process.exit(result.continue ? 0 : 1);
  });
}

export default PreTaskHook;