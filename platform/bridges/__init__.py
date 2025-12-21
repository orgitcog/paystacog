"""
PaystaCog Bridges - Integration Layer

This module provides bridges connecting:
- OpenCog Atomspace with Agent-Zero orchestration
- SDK integrations with the cognitive layer
- Plugin systems with the agent framework
- External APIs with internal knowledge representation
"""

from .cognitive_bridge import CognitiveBridge
from .sdk_bridge import SDKBridge
from .plugin_bridge import PluginBridge
from .api_bridge import APIBridge
from .unified_interface import UnifiedPaystackInterface

__version__ = "1.0.0"
__all__ = [
    "CognitiveBridge",
    "SDKBridge",
    "PluginBridge",
    "APIBridge",
    "UnifiedPaystackInterface"
]
