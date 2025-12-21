#!/usr/bin/env python3
"""
Cognitive Bridge - Connects OpenCog Atomspace with Agent-Zero Orchestration

This bridge enables:
- Knowledge-driven agent decision making
- Atomspace queries from agents
- Agent experiences stored in Atomspace
- Unified cognitive-agent architecture
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from opencog.atomspace import PaystackAtomspace, AtomType, TruthValue, Atom
from agent_zero.orchestrator import AgentZeroOrchestrator, AgentTask, TaskPriority
from agent_zero.memory import AgentMemory, MemoryType

logger = logging.getLogger(__name__)


class CognitiveBridge:
    """
    Bridge between OpenCog Atomspace and Agent-Zero Orchestration.
    
    This bridge enables:
    - Agents to query the Atomspace for knowledge
    - Experiences to be stored as atoms
    - Goal-directed behavior based on Atomspace state
    - Learning from agent outcomes
    """
    
    def __init__(self, atomspace: PaystackAtomspace, 
                 orchestrator: AgentZeroOrchestrator):
        self.atomspace = atomspace
        self.orchestrator = orchestrator
        self.memories: Dict[str, AgentMemory] = {}
        self.event_log: List[Dict] = []
        self._initialize_cognitive_atoms()
    
    def _initialize_cognitive_atoms(self):
        """Initialize cognitive concepts in the Atomspace."""
        # Agent concepts
        agent_root = self.atomspace.add_node(AtomType.CONCEPT, "Agent")
        
        agent_types = ["PaymentAgent", "IntegrationAgent", "MonitoringAgent", 
                      "SecurityAgent", "AnalyticsAgent"]
        for agent_type in agent_types:
            agent_node = self.atomspace.add_node(AtomType.CONCEPT, agent_type)
            self.atomspace.add_link(AtomType.INHERITANCE, [agent_node, agent_root])
        
        # Goal concepts
        goal_root = self.atomspace.add_node(AtomType.CONCEPT, "Goal")
        goals = ["ProcessPayment", "EnsureSecurity", "MonitorHealth", 
                "GenerateAnalytics", "MaintainIntegrations"]
        for goal in goals:
            goal_node = self.atomspace.add_node(AtomType.CONCEPT, goal)
            self.atomspace.add_link(AtomType.INHERITANCE, [goal_node, goal_root])
        
        # Action concepts
        action_root = self.atomspace.add_node(AtomType.CONCEPT, "Action")
        actions = ["Initialize", "Verify", "Charge", "Refund", "Scan", 
                  "Monitor", "Report", "Alert"]
        for action in actions:
            action_node = self.atomspace.add_node(AtomType.SCHEMA, action)
            self.atomspace.add_link(AtomType.INHERITANCE, [action_node, action_root])
    
    def get_agent_memory(self, agent_id: str) -> AgentMemory:
        """Get or create memory for an agent."""
        if agent_id not in self.memories:
            self.memories[agent_id] = AgentMemory(agent_id)
        return self.memories[agent_id]
    
    async def query_knowledge(self, query_type: str, 
                             parameters: Dict[str, Any]) -> List[Dict]:
        """Query the Atomspace for knowledge."""
        results = []
        
        if query_type == "payment_methods":
            # Get all payment methods
            atoms = self.atomspace.get_atoms_by_type(AtomType.PAYMENT_METHOD)
            results = [{"name": a.name, "confidence": a.truth_value.confidence} 
                      for a in atoms]
        
        elif query_type == "sdk_capabilities":
            # Get SDK information
            atoms = self.atomspace.get_atoms_by_type(AtomType.SDK)
            results = [{"sdk": a.name, "metadata": a.metadata} for a in atoms]
        
        elif query_type == "plugin_integrations":
            # Get plugin information
            atoms = self.atomspace.get_atoms_by_type(AtomType.PLUGIN)
            results = [{"plugin": a.name, "metadata": a.metadata} for a in atoms]
        
        elif query_type == "api_endpoints":
            # Get API endpoints
            atoms = self.atomspace.get_atoms_by_type(AtomType.API_ENDPOINT)
            results = [{"endpoint": a.name, "metadata": a.metadata} for a in atoms]
        
        elif query_type == "inheritance_tree":
            # Get inheritance tree for a concept
            root_name = parameters.get("root", "PaymentMethod")
            tree = self.atomspace.get_inheritance_tree(root_name)
            results = [tree]
        
        elif query_type == "pattern_match":
            # Pattern matching query
            atom_type = AtomType[parameters.get("type", "CONCEPT")]
            constraints = parameters.get("constraints", {})
            atoms = self.atomspace.pattern_match(atom_type, constraints)
            results = [a.to_dict() for a in atoms]
        
        # Log the query
        self._log_event("knowledge_query", {
            "query_type": query_type,
            "parameters": parameters,
            "result_count": len(results)
        })
        
        return results
    
    async def store_experience(self, agent_id: str, experience: Dict[str, Any]):
        """Store an agent's experience in both memory and Atomspace."""
        memory = self.get_agent_memory(agent_id)
        
        # Store in agent memory
        memory_id = memory.store(
            MemoryType.EPISODIC,
            experience,
            importance=experience.get("importance", 0.5),
            tags=experience.get("tags", [])
        )
        
        # Create atoms for the experience
        exp_type = experience.get("type", "Experience")
        exp_node = self.atomspace.add_node(
            AtomType.CONCEPT,
            f"{agent_id}_{exp_type}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            metadata=experience
        )
        
        # Link to agent
        agent_atoms = self.atomspace.get_atoms_by_name(agent_id.split("-")[0].title() + "Agent")
        if agent_atoms:
            self.atomspace.add_link(
                AtomType.EVALUATION,
                [agent_atoms[0], exp_node],
                TruthValue(experience.get("success_rate", 0.5), 0.8)
            )
        
        self._log_event("experience_stored", {
            "agent_id": agent_id,
            "memory_id": memory_id,
            "experience_type": exp_type
        })
        
        return memory_id
    
    async def get_recommended_action(self, agent_id: str, 
                                    context: Dict[str, Any]) -> Dict[str, Any]:
        """Get recommended action based on knowledge and experience."""
        memory = self.get_agent_memory(agent_id)
        
        # Search for similar past experiences
        similar_experiences = memory.search(context, limit=5)
        
        # Query relevant knowledge
        task_type = context.get("task_type", "")
        relevant_knowledge = []
        
        if "payment" in task_type.lower():
            relevant_knowledge = await self.query_knowledge("payment_methods", {})
        elif "integration" in task_type.lower():
            relevant_knowledge = await self.query_knowledge("sdk_capabilities", {})
        elif "security" in task_type.lower():
            relevant_knowledge = await self.query_knowledge("api_endpoints", {})
        
        # Generate recommendation
        recommendation = {
            "agent_id": agent_id,
            "context": context,
            "based_on": {
                "similar_experiences": len(similar_experiences),
                "relevant_knowledge": len(relevant_knowledge)
            },
            "recommended_action": self._determine_best_action(
                context, similar_experiences, relevant_knowledge
            ),
            "confidence": self._calculate_confidence(similar_experiences)
        }
        
        return recommendation
    
    def _determine_best_action(self, context: Dict, experiences: List, 
                               knowledge: List) -> str:
        """Determine the best action based on context and knowledge."""
        task_type = context.get("task_type", "")
        
        # Simple rule-based action selection
        if "initialize" in task_type.lower():
            return "proceed_with_initialization"
        elif "verify" in task_type.lower():
            return "verify_and_confirm"
        elif "security" in task_type.lower():
            return "run_security_check"
        elif "monitor" in task_type.lower():
            return "collect_metrics"
        else:
            return "analyze_and_report"
    
    def _calculate_confidence(self, experiences: List) -> float:
        """Calculate confidence based on past experiences."""
        if not experiences:
            return 0.5
        
        avg_importance = sum(e.importance for e in experiences) / len(experiences)
        return min(0.95, 0.5 + avg_importance * 0.5)
    
    async def learn_from_outcome(self, agent_id: str, task_id: str,
                                outcome: Dict[str, Any]):
        """Learn from a task outcome."""
        memory = self.get_agent_memory(agent_id)
        
        # Store the outcome
        memory.store(
            MemoryType.EPISODIC,
            {
                "task_id": task_id,
                "outcome": outcome,
                "timestamp": datetime.utcnow().isoformat()
            },
            importance=0.8 if outcome.get("success") else 0.6,
            tags=["outcome", "learning"]
        )
        
        # Update patterns if we have enough data
        outcomes = memory.recall_by_tag("outcome", limit=100)
        if len(outcomes) >= 10:
            success_outcomes = [
                o.content["outcome"] for o in outcomes 
                if o.content.get("outcome", {}).get("success")
            ]
            if success_outcomes:
                memory.learn_pattern("successful_outcome", success_outcomes)
        
        # Update Atomspace truth values based on outcome
        success = outcome.get("success", False)
        agent_atoms = self.atomspace.get_atoms_by_name(
            agent_id.split("-")[0].title() + "Agent"
        )
        if agent_atoms:
            agent_atom = agent_atoms[0]
            # Adjust truth value based on outcome
            current_tv = agent_atom.truth_value
            if success:
                new_strength = min(1.0, current_tv.strength + 0.01)
            else:
                new_strength = max(0.0, current_tv.strength - 0.01)
            agent_atom.truth_value = TruthValue(new_strength, 
                                                min(0.99, current_tv.confidence + 0.001))
        
        self._log_event("learning_update", {
            "agent_id": agent_id,
            "task_id": task_id,
            "success": success
        })
    
    async def synchronize_knowledge(self):
        """Synchronize knowledge between Atomspace and agent memories."""
        # Export semantic knowledge to all agent memories
        semantic_atoms = self.atomspace.get_atoms_by_type(AtomType.CONCEPT)
        
        for agent_id, memory in self.memories.items():
            for atom in semantic_atoms[:100]:  # Limit to prevent overflow
                memory.store(
                    MemoryType.SEMANTIC,
                    {"concept": atom.name, "type": atom.atom_type.value},
                    importance=atom.truth_value.strength,
                    tags=["atomspace", "concept"]
                )
        
        self._log_event("knowledge_sync", {
            "atoms_synced": len(semantic_atoms),
            "agents_updated": len(self.memories)
        })
    
    def _log_event(self, event_type: str, data: Dict):
        """Log a bridge event."""
        self.event_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "data": data
        })
        
        # Keep only recent events
        if len(self.event_log) > 1000:
            self.event_log = self.event_log[-500:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get bridge statistics."""
        return {
            "atomspace_stats": self.atomspace.get_statistics(),
            "agent_memories": {
                aid: mem.get_statistics() 
                for aid, mem in self.memories.items()
            },
            "event_log_size": len(self.event_log),
            "recent_events": self.event_log[-10:]
        }


# Factory function for creating a fully connected cognitive system
def create_cognitive_system() -> CognitiveBridge:
    """Create a fully initialized cognitive system."""
    from agent_zero.orchestrator import AgentZeroOrchestrator
    from agent_zero.agents import (
        PaymentAgent, IntegrationAgent, MonitoringAgent,
        SecurityAgent, AnalyticsAgent
    )
    
    # Create components
    atomspace = PaystackAtomspace()
    orchestrator = AgentZeroOrchestrator()
    
    # Register agents
    orchestrator.register_agent(PaymentAgent())
    orchestrator.register_agent(IntegrationAgent())
    orchestrator.register_agent(MonitoringAgent())
    orchestrator.register_agent(SecurityAgent())
    orchestrator.register_agent(AnalyticsAgent())
    
    # Create bridge
    bridge = CognitiveBridge(atomspace, orchestrator)
    
    return bridge


if __name__ == "__main__":
    import json
    
    # Test the cognitive bridge
    async def test():
        bridge = create_cognitive_system()
        
        # Query knowledge
        payment_methods = await bridge.query_knowledge("payment_methods", {})
        print("Payment Methods:")
        print(json.dumps(payment_methods, indent=2))
        
        # Store experience
        await bridge.store_experience("payment-001", {
            "type": "transaction",
            "amount": 10000,
            "status": "success",
            "importance": 0.8,
            "tags": ["transaction", "success"]
        })
        
        # Get recommendation
        recommendation = await bridge.get_recommended_action("payment-001", {
            "task_type": "payment.initialize",
            "amount": 5000
        })
        print("\nRecommendation:")
        print(json.dumps(recommendation, indent=2))
        
        # Learn from outcome
        await bridge.learn_from_outcome("payment-001", "task-001", {
            "success": True,
            "duration_ms": 150
        })
        
        print("\nBridge Statistics:")
        print(json.dumps(bridge.get_statistics(), indent=2, default=str))
    
    asyncio.run(test())
