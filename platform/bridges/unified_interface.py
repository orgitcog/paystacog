#!/usr/bin/env python3
"""
Unified Paystack Interface - Single Entry Point for All Platform Features

This module provides a unified interface that integrates:
- OpenCog Atomspace for knowledge representation
- Agent-Zero orchestration for autonomous operations
- SDK management for all platforms
- Plugin management for all integrations
- API access for all Paystack services
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import json
import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from opencog.atomspace import PaystackAtomspace, AtomType
from agent_zero.orchestrator import AgentZeroOrchestrator, AgentTask, TaskPriority
from agent_zero.agents import (
    PaymentAgent, IntegrationAgent, MonitoringAgent,
    SecurityAgent, AnalyticsAgent
)
from agent_zero.coordinator import AgentCoordinator

from .cognitive_bridge import CognitiveBridge
from .sdk_bridge import SDKBridge, SDKPlatform, SDKFeature
from .plugin_bridge import PluginBridge, PluginPlatform, PluginCategory
from .api_bridge import APIBridge

logger = logging.getLogger(__name__)


class UnifiedPaystackInterface:
    """
    Unified interface for the PaystaCog platform.
    
    This class provides a single entry point for:
    - Payment processing
    - SDK and plugin management
    - Cognitive operations
    - Agent orchestration
    - Analytics and monitoring
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._initialized = False
        
        # Core components
        self.atomspace: Optional[PaystackAtomspace] = None
        self.orchestrator: Optional[AgentZeroOrchestrator] = None
        self.coordinator: Optional[AgentCoordinator] = None
        
        # Bridges
        self.cognitive_bridge: Optional[CognitiveBridge] = None
        self.sdk_bridge: Optional[SDKBridge] = None
        self.plugin_bridge: Optional[PluginBridge] = None
        self.api_bridge: Optional[APIBridge] = None
        
        # State
        self.start_time: Optional[datetime] = None
        self.event_log: List[Dict] = []
    
    async def initialize(self):
        """Initialize all platform components."""
        if self._initialized:
            return
        
        logger.info("Initializing PaystaCog Unified Interface...")
        self.start_time = datetime.utcnow()
        
        # Initialize OpenCog Atomspace
        self.atomspace = PaystackAtomspace()
        logger.info("Atomspace initialized")
        
        # Initialize Agent-Zero Orchestrator
        self.orchestrator = AgentZeroOrchestrator()
        
        # Register agents
        self.orchestrator.register_agent(PaymentAgent())
        self.orchestrator.register_agent(IntegrationAgent())
        self.orchestrator.register_agent(MonitoringAgent())
        self.orchestrator.register_agent(SecurityAgent())
        self.orchestrator.register_agent(AnalyticsAgent())
        logger.info("Agents registered")
        
        # Initialize Coordinator
        self.coordinator = AgentCoordinator(self.orchestrator)
        logger.info("Coordinator initialized")
        
        # Initialize Bridges
        self.cognitive_bridge = CognitiveBridge(self.atomspace, self.orchestrator)
        self.sdk_bridge = SDKBridge()
        self.plugin_bridge = PluginBridge()
        self.api_bridge = APIBridge(
            secret_key=self.config.get("secret_key", ""),
            public_key=self.config.get("public_key", "")
        )
        logger.info("Bridges initialized")
        
        self._initialized = True
        self._log_event("platform_initialized", {})
        logger.info("PaystaCog Unified Interface initialized successfully")
    
    def _log_event(self, event_type: str, data: Dict):
        """Log a platform event."""
        self.event_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "data": data
        })
    
    # ==================== Payment Operations ====================
    
    async def process_payment(self, email: str, amount: int,
                             currency: str = "NGN", **kwargs) -> Dict[str, Any]:
        """Process a payment through the unified interface."""
        self._ensure_initialized()
        
        # Create workflow for payment processing
        workflow = self.coordinator.create_workflow(
            "payment_processing",
            f"payment_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            context={
                "email": email,
                "amount": amount,
                "currency": currency,
                **kwargs
            }
        )
        
        # Execute workflow
        result = await self.coordinator.execute_workflow(workflow.workflow_id)
        
        # Store experience in cognitive bridge
        await self.cognitive_bridge.store_experience("payment-001", {
            "type": "payment_processed",
            "amount": amount,
            "currency": currency,
            "success": result.get("state") == "completed",
            "importance": 0.8
        })
        
        self._log_event("payment_processed", {
            "amount": amount,
            "currency": currency,
            "result": result.get("state")
        })
        
        return result
    
    async def verify_payment(self, reference: str) -> Dict[str, Any]:
        """Verify a payment."""
        self._ensure_initialized()
        
        # Use API bridge for verification
        response = await self.api_bridge.verify_transaction(reference)
        
        self._log_event("payment_verified", {
            "reference": reference,
            "success": response.success
        })
        
        return response.data
    
    async def process_refund(self, transaction_reference: str,
                            amount: Optional[int] = None) -> Dict[str, Any]:
        """Process a refund."""
        self._ensure_initialized()
        
        # Create refund workflow
        workflow = self.coordinator.create_workflow(
            "refund_processing",
            f"refund_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            context={
                "reference": transaction_reference,
                "amount": amount
            }
        )
        
        result = await self.coordinator.execute_workflow(workflow.workflow_id)
        
        self._log_event("refund_processed", {
            "reference": transaction_reference,
            "result": result.get("state")
        })
        
        return result
    
    # ==================== SDK Operations ====================
    
    def get_sdk_info(self, platform: str) -> Dict[str, Any]:
        """Get SDK information for a platform."""
        self._ensure_initialized()
        
        try:
            sdk_platform = SDKPlatform(platform.lower())
            sdk = self.sdk_bridge.get_sdk(sdk_platform)
            if sdk:
                return sdk.to_dict()
            return {"error": f"SDK not found: {platform}"}
        except ValueError:
            return {"error": f"Invalid platform: {platform}"}
    
    def get_all_sdks(self) -> List[Dict[str, Any]]:
        """Get all SDK information."""
        self._ensure_initialized()
        return [sdk.to_dict() for sdk in self.sdk_bridge.get_all_sdks()]
    
    def get_sdk_recommendation(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Get SDK recommendation based on requirements."""
        self._ensure_initialized()
        
        sdk = self.sdk_bridge.get_recommended_sdk(requirements)
        if sdk:
            return {
                "recommended": sdk.to_dict(),
                "requirements": requirements
            }
        return {"error": "No matching SDK found", "requirements": requirements}
    
    def get_sdk_feature_parity(self) -> Dict[str, Any]:
        """Get SDK feature parity report."""
        self._ensure_initialized()
        return self.sdk_bridge.get_feature_parity_report()
    
    # ==================== Plugin Operations ====================
    
    def get_plugin_info(self, platform: str) -> Dict[str, Any]:
        """Get plugin information for a platform."""
        self._ensure_initialized()
        
        try:
            plugin_platform = PluginPlatform(platform.lower())
            plugin = self.plugin_bridge.get_plugin(plugin_platform)
            if plugin:
                return plugin.to_dict()
            return {"error": f"Plugin not found: {platform}"}
        except ValueError:
            return {"error": f"Invalid platform: {platform}"}
    
    def get_all_plugins(self) -> List[Dict[str, Any]]:
        """Get all plugin information."""
        self._ensure_initialized()
        return [plugin.to_dict() for plugin in self.plugin_bridge.get_all_plugins()]
    
    def get_plugins_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get plugins by category."""
        self._ensure_initialized()
        
        try:
            plugin_category = PluginCategory(category.lower())
            plugins = self.plugin_bridge.get_plugins_by_category(plugin_category)
            return [p.to_dict() for p in plugins]
        except ValueError:
            return []
    
    def check_plugin_compatibility(self, platform: str, version: str,
                                  php_version: Optional[str] = None) -> Dict[str, Any]:
        """Check plugin compatibility."""
        self._ensure_initialized()
        
        try:
            plugin_platform = PluginPlatform(platform.lower())
            return self.plugin_bridge.check_compatibility(
                plugin_platform, version, php_version
            )
        except ValueError:
            return {"error": f"Invalid platform: {platform}"}
    
    def get_plugin_installation_guide(self, platform: str) -> Dict[str, Any]:
        """Get plugin installation guide."""
        self._ensure_initialized()
        
        try:
            plugin_platform = PluginPlatform(platform.lower())
            return self.plugin_bridge.get_installation_guide(plugin_platform)
        except ValueError:
            return {"error": f"Invalid platform: {platform}"}
    
    # ==================== Cognitive Operations ====================
    
    async def query_knowledge(self, query_type: str,
                             parameters: Optional[Dict] = None) -> List[Dict]:
        """Query the knowledge base."""
        self._ensure_initialized()
        return await self.cognitive_bridge.query_knowledge(
            query_type, parameters or {}
        )
    
    async def get_recommendation(self, agent_id: str,
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI-powered recommendation."""
        self._ensure_initialized()
        return await self.cognitive_bridge.get_recommended_action(agent_id, context)
    
    def get_knowledge_tree(self, root_concept: str) -> Dict[str, Any]:
        """Get knowledge inheritance tree."""
        self._ensure_initialized()
        return self.atomspace.get_inheritance_tree(root_concept)
    
    # ==================== Agent Operations ====================
    
    async def dispatch_task(self, task_type: str, payload: Dict[str, Any],
                           priority: str = "medium") -> Dict[str, Any]:
        """Dispatch a task to the agent system."""
        self._ensure_initialized()
        
        priority_map = {
            "critical": TaskPriority.CRITICAL,
            "high": TaskPriority.HIGH,
            "medium": TaskPriority.MEDIUM,
            "low": TaskPriority.LOW,
            "background": TaskPriority.BACKGROUND
        }
        
        task = AgentTask(
            task_id=f"task_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            task_type=task_type,
            payload=payload,
            priority=priority_map.get(priority, TaskPriority.MEDIUM)
        )
        
        await self.orchestrator.dispatch_task(task)
        
        return {
            "task_id": task.task_id,
            "task_type": task_type,
            "status": "dispatched"
        }
    
    async def execute_workflow(self, workflow_name: str,
                              context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a predefined workflow."""
        self._ensure_initialized()
        
        workflow = self.coordinator.create_workflow(
            workflow_name,
            f"{workflow_name}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            context=context
        )
        
        return await self.coordinator.execute_workflow(workflow.workflow_id)
    
    def get_available_workflows(self) -> List[str]:
        """Get list of available workflows."""
        self._ensure_initialized()
        return self.coordinator.list_templates()
    
    # ==================== Health & Monitoring ====================
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        self._ensure_initialized()
        
        # Execute health check workflow
        result = await self.execute_workflow("health_check", {"target": "all"})
        
        # Get component health
        health = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "atomspace": self.atomspace.get_statistics(),
                "orchestrator": self.orchestrator.get_status(),
                "sdk_bridge": self.sdk_bridge.check_all_sdks_health(),
                "api_bridge": self.api_bridge.get_statistics()
            },
            "workflow_result": result
        }
        
        # Determine overall status
        if any(c.get("status") == "unhealthy" for c in health["components"].values() 
               if isinstance(c, dict)):
            health["status"] = "degraded"
        
        self._log_event("health_check", {"status": health["status"]})
        
        return health
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get platform metrics."""
        self._ensure_initialized()
        
        return {
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds() if self.start_time else 0,
            "orchestrator": self.orchestrator.get_metrics(),
            "cognitive_bridge": self.cognitive_bridge.get_statistics(),
            "api_bridge": self.api_bridge.get_statistics(),
            "events_logged": len(self.event_log)
        }
    
    # ==================== Platform Information ====================
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get platform information."""
        return {
            "name": "PaystaCog",
            "version": "1.0.0",
            "description": "Unified Paystack Financial Services Platform with OpenCog Intelligence",
            "components": {
                "opencog_atomspace": "Knowledge representation and reasoning",
                "agent_zero": "Multi-agent orchestration",
                "sdk_bridge": "Unified SDK management",
                "plugin_bridge": "Unified plugin management",
                "api_bridge": "Unified API access"
            },
            "capabilities": [
                "Payment processing",
                "Transaction verification",
                "Refund processing",
                "SDK management",
                "Plugin management",
                "Knowledge-driven decisions",
                "Autonomous agent operations",
                "Health monitoring",
                "Analytics"
            ],
            "supported_sdks": [p.value for p in SDKPlatform],
            "supported_plugins": [p.value for p in PluginPlatform],
            "initialized": self._initialized
        }
    
    def _ensure_initialized(self):
        """Ensure the platform is initialized."""
        if not self._initialized:
            raise RuntimeError("Platform not initialized. Call initialize() first.")


# Factory function
def create_platform(config: Optional[Dict[str, Any]] = None) -> UnifiedPaystackInterface:
    """Create a new PaystaCog platform instance."""
    return UnifiedPaystackInterface(config)


# Async factory function
async def create_and_initialize_platform(
    config: Optional[Dict[str, Any]] = None
) -> UnifiedPaystackInterface:
    """Create and initialize a new PaystaCog platform instance."""
    platform = UnifiedPaystackInterface(config)
    await platform.initialize()
    return platform


if __name__ == "__main__":
    async def demo():
        # Create and initialize platform
        platform = await create_and_initialize_platform({
            "secret_key": "sk_test_xxx",
            "public_key": "pk_test_xxx"
        })
        
        print("=" * 60)
        print("PaystaCog Unified Interface Demo")
        print("=" * 60)
        
        # Get platform info
        print("\nPlatform Info:")
        info = platform.get_platform_info()
        print(f"  Name: {info['name']}")
        print(f"  Version: {info['version']}")
        print(f"  Capabilities: {len(info['capabilities'])}")
        
        # Query knowledge
        print("\nKnowledge Query - Payment Methods:")
        methods = await platform.query_knowledge("payment_methods", {})
        for m in methods[:5]:
            print(f"  - {m['name']}")
        
        # Get SDK info
        print("\nSDK Information - Node.js:")
        sdk_info = platform.get_sdk_info("node")
        print(f"  Name: {sdk_info.get('name')}")
        print(f"  Features: {sdk_info.get('features', [])[:3]}")
        
        # Get plugin info
        print("\nPlugin Information - WooCommerce:")
        plugin_info = platform.get_plugin_info("woocommerce")
        print(f"  Name: {plugin_info.get('name')}")
        print(f"  Features: {plugin_info.get('features', [])[:3]}")
        
        # Get recommendation
        print("\nAI Recommendation for payment task:")
        rec = await platform.get_recommendation("payment-001", {
            "task_type": "payment.initialize",
            "amount": 10000
        })
        print(f"  Recommended: {rec.get('recommended_action')}")
        print(f"  Confidence: {rec.get('confidence', 0):.2f}")
        
        # Health check
        print("\nHealth Check:")
        health = await platform.health_check()
        print(f"  Status: {health['status']}")
        
        # Metrics
        print("\nPlatform Metrics:")
        metrics = platform.get_metrics()
        print(f"  Uptime: {metrics['uptime_seconds']:.0f}s")
        print(f"  Events logged: {metrics['events_logged']}")
        
        print("\n" + "=" * 60)
        print("Demo Complete")
        print("=" * 60)
    
    asyncio.run(demo())
