#!/usr/bin/env node

/**
 * Demo script for optimized Claude Flow hooks
 * Shows parallel execution, MCP integration, and performance benefits
 */

import { hookManager } from './index.js';
import { spawn } from 'child_process';

async function executeCommand(command) {
  return new Promise((resolve) => {
    const child = spawn(command, [], { shell: true });
    let output = '';
    child.stdout.on('data', (data) => output += data.toString());
    child.on('close', (code) => resolve({ success: code === 0, output }));
  });
}

async function demonstrateHooks() {
  console.log('🎯 Claude Flow Optimized Hooks Demo\n');
  console.log('=' .repeat(60));
  
  // 1. Demonstrate Pre-Task Hook
  console.log('\n1️⃣ PRE-TASK HOOK DEMO');
  console.log('-'.repeat(40));
  
  const preTaskResult = await hookManager.executeHook('pre-task', {
    description: 'Build a REST API with authentication, database, and testing',
    autoSpawnAgents: true,
    optimizeTopology: true,
    estimateComplexity: true
  });
  
  console.log('Pre-task results:', {
    topology: preTaskResult.topology,
    agentsSpawned: preTaskResult.agentsSpawned,
    complexity: preTaskResult.complexity,
    estimatedMinutes: preTaskResult.estimatedMinutes
  });
  
  // 2. Demonstrate Parallel Hook Execution
  console.log('\n\n2️⃣ PARALLEL HOOK EXECUTION DEMO');
  console.log('-'.repeat(40));
  
  const startTime = Date.now();
  const parallelResults = await hookManager.executeParallelHooks([
    {
      hook: 'pre-command',
      options: {
        command: 'npm install express mongoose jsonwebtoken',
        validateSafety: true,
        predictPerformance: true
      }
    },
    {
      hook: 'pre-command',
      options: {
        command: 'docker-compose up -d',
        validateSafety: true,
        checkDependencies: true
      }
    },
    {
      hook: 'pre-command',
      options: {
        command: 'npm test',
        suggestOptimizations: true
      }
    }
  ]);
  
  const parallelDuration = Date.now() - startTime;
  console.log(`Parallel execution completed in ${parallelDuration}ms`);
  console.log(`Results: ${parallelResults.successful}/${parallelResults.total} successful`);
  
  // 3. Demonstrate Post-Edit Hook with Pattern Training
  console.log('\n\n3️⃣ POST-EDIT HOOK DEMO');
  console.log('-'.repeat(40));
  
  // Create a sample file
  const sampleCode = `
import express from 'express';
import mongoose from 'mongoose';
import jwt from 'jsonwebtoken';

const app = express();

// Async function pattern
async function connectDB() {
  try {
    await mongoose.connect(process.env.MONGO_URI);
    console.log('Database connected');
  } catch (error) {
    console.error('Database connection failed:', error);
    process.exit(1);
  }
}

// REST API pattern
app.get('/api/users', async (req, res) => {
  try {
    const users = await User.find({});
    res.json({ success: true, data: users });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Authentication pattern
function authenticateToken(req, res, next) {
  const token = req.header('Authorization')?.split(' ')[1];
  
  if (!token) {
    return res.status(401).json({ error: 'Access denied' });
  }
  
  try {
    const verified = jwt.verify(token, process.env.JWT_SECRET);
    req.user = verified;
    next();
  } catch (error) {
    res.status(403).json({ error: 'Invalid token' });
  }
}

export default app;
`;

  await executeCommand(`mkdir -p /tmp/claude-flow-demo`);
  await executeCommand(`echo '${sampleCode}' > /tmp/claude-flow-demo/app.js`);
  
  const postEditResult = await hookManager.executeHook('post-edit', {
    file: '/tmp/claude-flow-demo/app.js',
    autoFormat: true,
    trainPatterns: true,
    memoryKey: 'demo/edit'
  });
  
  console.log('Post-edit results:', {
    formatted: postEditResult.formatted,
    patternsTrained: postEditResult.patternsTrained,
    linesChanged: postEditResult.stats?.linesChanged
  });
  
  // 4. Demonstrate Hook Sequence
  console.log('\n\n4️⃣ HOOK SEQUENCE DEMO');
  console.log('-'.repeat(40));
  
  const sequenceResults = await hookManager.executeSequence([
    {
      hook: 'pre-task',
      options: { description: 'Run test suite' },
      stopOnError: true
    },
    {
      hook: 'pre-command',
      options: { command: 'npm test' },
      passDataTo: 2
    },
    {
      hook: 'post-task',
      options: { 
        analyzePerformance: true,
        generateSummary: true 
      }
    }
  ]);
  
  console.log(`Sequence completed: ${sequenceResults.length} hooks executed`);
  
  // 5. Demonstrate Memory Integration
  console.log('\n\n5️⃣ MEMORY INTEGRATION DEMO');
  console.log('-'.repeat(40));
  
  // Store demo results
  await executeCommand(`npx claude-flow@alpha memory store --key "demo/results" --value '${JSON.stringify({
    timestamp: new Date().toISOString(),
    hooks: ['pre-task', 'post-edit', 'pre-command'],
    performance: {
      parallelDuration,
      totalHooks: parallelResults.total
    }
  })}'`);
  
  // Retrieve stored data
  const memoryResult = await executeCommand('npx claude-flow@alpha memory retrieve --key "demo/results"');
  console.log('Retrieved from memory:', memoryResult.output.substring(0, 200) + '...');
  
  // 6. Performance Comparison
  console.log('\n\n6️⃣ PERFORMANCE COMPARISON');
  console.log('-'.repeat(40));
  
  // Sequential execution (for comparison)
  const seqStartTime = Date.now();
  await hookManager.executeHook('pre-command', { command: 'npm install' });
  await hookManager.executeHook('pre-command', { command: 'docker-compose up' });
  await hookManager.executeHook('pre-command', { command: 'npm test' });
  const seqDuration = Date.now() - seqStartTime;
  
  console.log(`Sequential execution: ${seqDuration}ms`);
  console.log(`Parallel execution: ${parallelDuration}ms`);
  console.log(`Performance improvement: ${Math.round((1 - parallelDuration/seqDuration) * 100)}% faster`);
  
  // 7. Session End
  console.log('\n\n7️⃣ SESSION END DEMO');
  console.log('-'.repeat(40));
  
  const sessionEndResult = await hookManager.executeHook('session-end', {
    generateSummary: true,
    exportMetrics: true,
    extractLearnings: true
  });
  
  console.log('Session completed:', {
    reportGenerated: !!sessionEndResult.reportPath,
    metricsExported: !!sessionEndResult.metrics,
    learningsExtracted: !!sessionEndResult.learnings
  });
  
  // Cleanup
  await executeCommand('rm -rf /tmp/claude-flow-demo');
  
  console.log('\n' + '='.repeat(60));
  console.log('✅ Demo completed successfully!');
  console.log('='.repeat(60) + '\n');
}

// Run demo
if (import.meta.url === `file://${process.argv[1]}`) {
  demonstrateHooks().catch(console.error);
}