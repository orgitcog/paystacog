#!/usr/bin/env python3
"""
Agent-Zero Orchestrator for PaystaCog

Implements a multi-agent orchestration system for autonomous management
of the Paystack financial services platform.
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import asyncio
import json
import logging
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentState(Enum):
    """States an agent can be in."""
    IDLE = "idle"
    ACTIVE = "active"
    PROCESSING = "processing"
    WAITING = "waiting"
    ERROR = "error"
    TERMINATED = "terminated"


class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
class AgentTask:
    """Represents a task to be executed by an agent."""
    task_id: str
    task_type: str
    payload: Dict[str, Any]
    priority: TaskPriority = TaskPriority.MEDIUM
    created_at: datetime = field(default_factory=datetime.utcnow)
    deadline: Optional[datetime] = None
    retries: int = 0
    max_retries: int = 3
    result: Optional[Any] = None
    error: Optional[str] = None
    status: str = "pending"


@dataclass
class AgentMessage:
    """Message passed between agents."""
    sender: str
    receiver: str
    message_type: str
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None


class BaseAgent(ABC):
    """Base class for all PaystaCog agents."""
    
    def __init__(self, agent_id: str, name: str):
        self.agent_id = agent_id
        self.name = name
        self.state = AgentState.IDLE
        self.task_queue: List[AgentTask] = []
        self.message_inbox: List[AgentMessage] = []
        self.capabilities: List[str] = []
        self.metrics: Dict[str, Any] = {
            'tasks_completed': 0,
            'tasks_failed': 0,
            'messages_sent': 0,
            'messages_received': 0,
            'uptime_start': datetime.utcnow()
        }
    
    @abstractmethod
    async def process_task(self, task: AgentTask) -> Any:
        """Process a task. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle an incoming message. Must be implemented by subclasses."""
        pass
    
    async def enqueue_task(self, task: AgentTask):
        """Add a task to the agent's queue."""
        self.task_queue.append(task)
        self.task_queue.sort(key=lambda t: t.priority.value)
        logger.info(f"Agent {self.name}: Task {task.task_id} enqueued")
    
    async def receive_message(self, message: AgentMessage):
        """Receive a message from another agent."""
        self.message_inbox.append(message)
        self.metrics['messages_received'] += 1
        logger.info(f"Agent {self.name}: Received message from {message.sender}")
    
    async def run_cycle(self) -> Optional[Any]:
        """Run one processing cycle."""
        # Process messages first
        while self.message_inbox:
            message = self.message_inbox.pop(0)
            response = await self.handle_message(message)
            if response:
                return response
        
        # Then process tasks
        if self.task_queue:
            task = self.task_queue.pop(0)
            self.state = AgentState.PROCESSING
            try:
                result = await self.process_task(task)
                task.result = result
                task.status = "completed"
                self.metrics['tasks_completed'] += 1
                return result
            except Exception as e:
                task.error = str(e)
                task.retries += 1
                if task.retries < task.max_retries:
                    self.task_queue.append(task)
                else:
                    task.status = "failed"
                    self.metrics['tasks_failed'] += 1
                logger.error(f"Agent {self.name}: Task {task.task_id} failed: {e}")
            finally:
                self.state = AgentState.IDLE
        
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status."""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'state': self.state.value,
            'pending_tasks': len(self.task_queue),
            'pending_messages': len(self.message_inbox),
            'capabilities': self.capabilities,
            'metrics': self.metrics
        }


class AgentZeroOrchestrator:
    """
    Main orchestrator for the PaystaCog agent system.
    
    Coordinates multiple specialized agents to manage:
    - Payment processing and routing
    - Integration health monitoring
    - Security scanning and compliance
    - Analytics and reporting
    - Self-healing and recovery
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.message_bus: List[AgentMessage] = []
        self.task_registry: Dict[str, AgentTask] = {}
        self.running = False
        self.cycle_count = 0
        self.config = {
            'max_concurrent_tasks': 10,
            'cycle_interval_ms': 100,
            'health_check_interval_s': 60,
            'auto_recovery': True
        }
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {}
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator."""
        self.agents[agent.agent_id] = agent
        logger.info(f"Orchestrator: Registered agent {agent.name} ({agent.agent_id})")
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent from the orchestrator."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Orchestrator: Unregistered agent {agent_id}")
    
    async def dispatch_task(self, task: AgentTask, agent_id: Optional[str] = None):
        """Dispatch a task to an appropriate agent."""
        self.task_registry[task.task_id] = task
        
        if agent_id and agent_id in self.agents:
            await self.agents[agent_id].enqueue_task(task)
            return
        
        # Find best agent for task type
        best_agent = self._find_best_agent(task)
        if best_agent:
            await best_agent.enqueue_task(task)
        else:
            logger.warning(f"Orchestrator: No suitable agent for task {task.task_id}")
    
    def _find_best_agent(self, task: AgentTask) -> Optional[BaseAgent]:
        """Find the best agent to handle a task."""
        candidates = []
        for agent in self.agents.values():
            if task.task_type in agent.capabilities:
                candidates.append(agent)
        
        if not candidates:
            return None
        
        # Select agent with shortest queue
        return min(candidates, key=lambda a: len(a.task_queue))
    
    async def send_message(self, message: AgentMessage):
        """Send a message between agents."""
        if message.receiver in self.agents:
            await self.agents[message.receiver].receive_message(message)
            self.message_bus.append(message)
        elif message.receiver == "broadcast":
            for agent in self.agents.values():
                if agent.agent_id != message.sender:
                    await agent.receive_message(message)
            self.message_bus.append(message)
    
    async def run_orchestration_cycle(self):
        """Run one orchestration cycle across all agents."""
        self.cycle_count += 1
        
        # Run each agent's cycle
        results = []
        for agent in self.agents.values():
            try:
                result = await agent.run_cycle()
                if result:
                    results.append((agent.agent_id, result))
            except Exception as e:
                logger.error(f"Orchestrator: Agent {agent.name} cycle failed: {e}")
                if self.config['auto_recovery']:
                    await self._recover_agent(agent)
        
        # Emit cycle complete event
        await self._emit_event('cycle_complete', {
            'cycle': self.cycle_count,
            'results': results
        })
        
        return results
    
    async def _recover_agent(self, agent: BaseAgent):
        """Attempt to recover a failed agent."""
        logger.info(f"Orchestrator: Attempting recovery for {agent.name}")
        agent.state = AgentState.IDLE
        agent.message_inbox.clear()
        # Re-queue failed tasks with lower priority
        for task in agent.task_queue:
            task.priority = TaskPriority.LOW
    
    async def start(self):
        """Start the orchestrator."""
        self.running = True
        logger.info("Orchestrator: Starting...")
        
        while self.running:
            await self.run_orchestration_cycle()
            await asyncio.sleep(self.config['cycle_interval_ms'] / 1000)
    
    async def stop(self):
        """Stop the orchestrator."""
        self.running = False
        logger.info("Orchestrator: Stopping...")
        
        # Graceful shutdown
        for agent in self.agents.values():
            agent.state = AgentState.TERMINATED
    
    def on_event(self, event_type: str, handler: Callable):
        """Register an event handler."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit an event to all registered handlers."""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                except Exception as e:
                    logger.error(f"Orchestrator: Event handler failed: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status."""
        return {
            'running': self.running,
            'cycle_count': self.cycle_count,
            'agents': {aid: agent.get_status() for aid, agent in self.agents.items()},
            'pending_tasks': len(self.task_registry),
            'message_bus_size': len(self.message_bus),
            'config': self.config
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics from all agents."""
        total_tasks = sum(a.metrics['tasks_completed'] for a in self.agents.values())
        total_failed = sum(a.metrics['tasks_failed'] for a in self.agents.values())
        total_messages = sum(a.metrics['messages_sent'] for a in self.agents.values())
        
        return {
            'total_tasks_completed': total_tasks,
            'total_tasks_failed': total_failed,
            'total_messages_exchanged': total_messages,
            'success_rate': total_tasks / (total_tasks + total_failed) if (total_tasks + total_failed) > 0 else 1.0,
            'agents_active': sum(1 for a in self.agents.values() if a.state == AgentState.ACTIVE),
            'agents_idle': sum(1 for a in self.agents.values() if a.state == AgentState.IDLE)
        }


# Singleton instance
_orchestrator_instance = None

def get_orchestrator() -> AgentZeroOrchestrator:
    """Get the singleton orchestrator instance."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = AgentZeroOrchestrator()
    return _orchestrator_instance


if __name__ == "__main__":
    # Test the orchestrator
    orchestrator = AgentZeroOrchestrator()
    print("Orchestrator Status:")
    print(json.dumps(orchestrator.get_status(), indent=2, default=str))
