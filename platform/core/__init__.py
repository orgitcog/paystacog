"""
PaystaCog Core - Central Platform Module

This module provides the core functionality for the PaystaCog platform,
including configuration, initialization, and main entry points.
"""

from .config import PlatformConfig, load_config
from .main import PaystaCogPlatform, main

__version__ = "1.0.0"
__all__ = [
    "PlatformConfig",
    "load_config",
    "PaystaCogPlatform",
    "main"
]
