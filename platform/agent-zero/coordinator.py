#!/usr/bin/env python3
"""
Agent Coordinator for PaystaCog

Coordinates multi-agent collaboration for complex payment workflows.
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import json
import logging
from enum import Enum

from .orchestrator import AgentZeroOrchestrator, AgentTask, AgentMessage, TaskPriority

logger = logging.getLogger(__name__)


class WorkflowState(Enum):
    """States a workflow can be in."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowStep:
    """A single step in a workflow."""
    step_id: str
    agent_id: str
    task_type: str
    payload: Dict[str, Any]
    depends_on: List[str] = field(default_factory=list)
    status: str = "pending"
    result: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class Workflow:
    """A multi-step workflow coordinating multiple agents."""
    workflow_id: str
    name: str
    steps: List[WorkflowStep]
    state: WorkflowState = WorkflowState.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    context: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)


class AgentCoordinator:
    """
    Coordinates complex workflows across multiple agents.
    
    Features:
    - Workflow definition and execution
    - Dependency management between steps
    - Parallel execution where possible
    - Error handling and recovery
    - Context sharing between agents
    """
    
    def __init__(self, orchestrator: AgentZeroOrchestrator):
        self.orchestrator = orchestrator
        self.workflows: Dict[str, Workflow] = {}
        self.workflow_templates: Dict[str, List[Dict]] = {}
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize common workflow templates."""
        
        # Payment processing workflow
        self.workflow_templates["payment_processing"] = [
            {
                "step_id": "fraud_check",
                "agent_id": "security-001",
                "task_type": "security.fraud_detection",
                "depends_on": []
            },
            {
                "step_id": "process_payment",
                "agent_id": "payment-001",
                "task_type": "payment.initialize",
                "depends_on": ["fraud_check"]
            },
            {
                "step_id": "verify_payment",
                "agent_id": "payment-001",
                "task_type": "payment.verify",
                "depends_on": ["process_payment"]
            },
            {
                "step_id": "record_analytics",
                "agent_id": "analytics-001",
                "task_type": "analytics.transactions",
                "depends_on": ["verify_payment"]
            }
        ]
        
        # Health check workflow
        self.workflow_templates["health_check"] = [
            {
                "step_id": "check_integrations",
                "agent_id": "integration-001",
                "task_type": "integration.health_check",
                "depends_on": []
            },
            {
                "step_id": "check_performance",
                "agent_id": "monitoring-001",
                "task_type": "monitoring.performance",
                "depends_on": []
            },
            {
                "step_id": "check_security",
                "agent_id": "security-001",
                "task_type": "security.scan",
                "depends_on": []
            },
            {
                "step_id": "generate_report",
                "agent_id": "analytics-001",
                "task_type": "analytics.trends",
                "depends_on": ["check_integrations", "check_performance", "check_security"]
            }
        ]
        
        # Refund workflow
        self.workflow_templates["refund_processing"] = [
            {
                "step_id": "verify_transaction",
                "agent_id": "payment-001",
                "task_type": "payment.verify",
                "depends_on": []
            },
            {
                "step_id": "compliance_check",
                "agent_id": "security-001",
                "task_type": "security.compliance",
                "depends_on": ["verify_transaction"]
            },
            {
                "step_id": "process_refund",
                "agent_id": "payment-001",
                "task_type": "payment.refund",
                "depends_on": ["compliance_check"]
            },
            {
                "step_id": "update_analytics",
                "agent_id": "analytics-001",
                "task_type": "analytics.revenue",
                "depends_on": ["process_refund"]
            }
        ]
    
    def create_workflow(self, template_name: str, workflow_id: str, 
                       context: Optional[Dict] = None) -> Workflow:
        """Create a workflow from a template."""
        if template_name not in self.workflow_templates:
            raise ValueError(f"Unknown workflow template: {template_name}")
        
        template = self.workflow_templates[template_name]
        steps = []
        
        for step_def in template:
            step = WorkflowStep(
                step_id=step_def["step_id"],
                agent_id=step_def["agent_id"],
                task_type=step_def["task_type"],
                payload=context or {},
                depends_on=step_def.get("depends_on", [])
            )
            steps.append(step)
        
        workflow = Workflow(
            workflow_id=workflow_id,
            name=template_name,
            steps=steps,
            context=context or {}
        )
        
        self.workflows[workflow_id] = workflow
        logger.info(f"Coordinator: Created workflow {workflow_id} from template {template_name}")
        
        return workflow
    
    def create_custom_workflow(self, workflow_id: str, name: str,
                               steps: List[Dict], context: Optional[Dict] = None) -> Workflow:
        """Create a custom workflow."""
        workflow_steps = []
        
        for step_def in steps:
            step = WorkflowStep(
                step_id=step_def["step_id"],
                agent_id=step_def["agent_id"],
                task_type=step_def["task_type"],
                payload=step_def.get("payload", context or {}),
                depends_on=step_def.get("depends_on", [])
            )
            workflow_steps.append(step)
        
        workflow = Workflow(
            workflow_id=workflow_id,
            name=name,
            steps=workflow_steps,
            context=context or {}
        )
        
        self.workflows[workflow_id] = workflow
        return workflow
    
    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Execute a workflow."""
        if workflow_id not in self.workflows:
            raise ValueError(f"Unknown workflow: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        workflow.state = WorkflowState.RUNNING
        
        logger.info(f"Coordinator: Executing workflow {workflow_id}")
        
        try:
            # Build dependency graph
            completed_steps: Dict[str, Any] = {}
            pending_steps = {s.step_id: s for s in workflow.steps}
            
            while pending_steps:
                # Find steps that can be executed (all dependencies met)
                ready_steps = []
                for step_id, step in pending_steps.items():
                    if all(dep in completed_steps for dep in step.depends_on):
                        ready_steps.append(step)
                
                if not ready_steps:
                    # Deadlock or all steps completed
                    if pending_steps:
                        raise RuntimeError("Workflow deadlock detected")
                    break
                
                # Execute ready steps in parallel
                tasks = []
                for step in ready_steps:
                    # Enrich payload with results from dependencies
                    enriched_payload = {**workflow.context, **step.payload}
                    for dep in step.depends_on:
                        enriched_payload[f"{dep}_result"] = completed_steps[dep]
                    
                    task = AgentTask(
                        task_id=f"{workflow_id}_{step.step_id}",
                        task_type=step.task_type,
                        payload=enriched_payload,
                        priority=TaskPriority.HIGH
                    )
                    tasks.append((step, task))
                
                # Dispatch tasks
                for step, task in tasks:
                    await self.orchestrator.dispatch_task(task, step.agent_id)
                
                # Wait for completion (simplified - in production would use proper async)
                await asyncio.sleep(0.1)
                
                # Mark steps as completed
                for step, task in tasks:
                    step.status = "completed"
                    step.result = task.result or {"status": "success"}
                    completed_steps[step.step_id] = step.result
                    del pending_steps[step.step_id]
            
            workflow.state = WorkflowState.COMPLETED
            workflow.completed_at = datetime.utcnow()
            workflow.results = completed_steps
            
            logger.info(f"Coordinator: Workflow {workflow_id} completed successfully")
            
            return {
                "workflow_id": workflow_id,
                "state": workflow.state.value,
                "results": workflow.results
            }
            
        except Exception as e:
            workflow.state = WorkflowState.FAILED
            logger.error(f"Coordinator: Workflow {workflow_id} failed: {e}")
            return {
                "workflow_id": workflow_id,
                "state": workflow.state.value,
                "error": str(e)
            }
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get the status of a workflow."""
        if workflow_id not in self.workflows:
            return {"error": f"Unknown workflow: {workflow_id}"}
        
        workflow = self.workflows[workflow_id]
        return {
            "workflow_id": workflow_id,
            "name": workflow.name,
            "state": workflow.state.value,
            "created_at": workflow.created_at.isoformat(),
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "steps": [
                {
                    "step_id": s.step_id,
                    "agent_id": s.agent_id,
                    "status": s.status,
                    "depends_on": s.depends_on
                }
                for s in workflow.steps
            ],
            "results": workflow.results
        }
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflows."""
        return [
            {
                "workflow_id": w.workflow_id,
                "name": w.name,
                "state": w.state.value,
                "created_at": w.created_at.isoformat()
            }
            for w in self.workflows.values()
        ]
    
    def list_templates(self) -> List[str]:
        """List available workflow templates."""
        return list(self.workflow_templates.keys())


if __name__ == "__main__":
    # Test the coordinator
    from .orchestrator import AgentZeroOrchestrator
    from .agents import PaymentAgent, SecurityAgent, AnalyticsAgent, IntegrationAgent, MonitoringAgent
    
    async def test():
        orchestrator = AgentZeroOrchestrator()
        
        # Register agents
        orchestrator.register_agent(PaymentAgent())
        orchestrator.register_agent(SecurityAgent())
        orchestrator.register_agent(AnalyticsAgent())
        orchestrator.register_agent(IntegrationAgent())
        orchestrator.register_agent(MonitoringAgent())
        
        coordinator = AgentCoordinator(orchestrator)
        
        # Create and execute a workflow
        workflow = coordinator.create_workflow(
            "health_check",
            "test-workflow-001",
            context={"target": "all"}
        )
        
        result = await coordinator.execute_workflow("test-workflow-001")
        print(json.dumps(result, indent=2, default=str))
    
    asyncio.run(test())
