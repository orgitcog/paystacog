"""
PaystaCog Agent-Zero Orchestration Layer

This module provides the Agent-Zero inspired orchestration system for
autonomous management of the Paystack financial services platform.

Agent-Zero principles implemented:
- Multi-agent coordination for distributed payment processing
- Autonomous decision making for transaction routing
- Self-healing capabilities for integration failures
- Continuous learning from transaction patterns
"""

from .orchestrator import AgentZeroOrchestrator
from .agents import (
    PaymentAgent,
    IntegrationAgent,
    MonitoringAgent,
    SecurityAgent,
    AnalyticsAgent
)
from .coordinator import AgentCoordinator
from .memory import AgentMemory

__version__ = "1.0.0"
__all__ = [
    "AgentZeroOrchestrator",
    "PaymentAgent",
    "IntegrationAgent", 
    "MonitoringAgent",
    "SecurityAgent",
    "AnalyticsAgent",
    "AgentCoordinator",
    "AgentMemory"
]
