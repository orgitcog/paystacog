#!/usr/bin/env python3
"""
PaystaCog Configuration Module

Handles platform configuration loading and validation.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import json
import os
import logging

logger = logging.getLogger(__name__)


@dataclass
class APIConfig:
    """API configuration."""
    secret_key: str = ""
    public_key: str = ""
    base_url: str = "https://api.paystack.co"
    timeout_seconds: int = 30
    max_retries: int = 3


@dataclass
class AgentConfig:
    """Agent configuration."""
    max_concurrent_tasks: int = 10
    cycle_interval_ms: int = 100
    health_check_interval_s: int = 60
    auto_recovery: bool = True


@dataclass
class AtomspaceConfig:
    """Atomspace configuration."""
    max_atoms: int = 100000
    decay_rate: float = 0.01
    attention_threshold: float = 0.1


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None


@dataclass
class PlatformConfig:
    """Main platform configuration."""
    api: APIConfig = field(default_factory=APIConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    atomspace: AtomspaceConfig = field(default_factory=AtomspaceConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    integrations_path: str = "/home/ubuntu/paystacog/integrations"
    data_path: str = "/home/ubuntu/paystacog/data"
    environment: str = "development"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "api": {
                "base_url": self.api.base_url,
                "timeout_seconds": self.api.timeout_seconds,
                "max_retries": self.api.max_retries
            },
            "agent": {
                "max_concurrent_tasks": self.agent.max_concurrent_tasks,
                "cycle_interval_ms": self.agent.cycle_interval_ms,
                "health_check_interval_s": self.agent.health_check_interval_s,
                "auto_recovery": self.agent.auto_recovery
            },
            "atomspace": {
                "max_atoms": self.atomspace.max_atoms,
                "decay_rate": self.atomspace.decay_rate,
                "attention_threshold": self.atomspace.attention_threshold
            },
            "logging": {
                "level": self.logging.level,
                "format": self.logging.format,
                "file_path": self.logging.file_path
            },
            "integrations_path": self.integrations_path,
            "data_path": self.data_path,
            "environment": self.environment
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlatformConfig':
        """Create config from dictionary."""
        config = cls()
        
        if "api" in data:
            api_data = data["api"]
            config.api = APIConfig(
                secret_key=api_data.get("secret_key", ""),
                public_key=api_data.get("public_key", ""),
                base_url=api_data.get("base_url", "https://api.paystack.co"),
                timeout_seconds=api_data.get("timeout_seconds", 30),
                max_retries=api_data.get("max_retries", 3)
            )
        
        if "agent" in data:
            agent_data = data["agent"]
            config.agent = AgentConfig(
                max_concurrent_tasks=agent_data.get("max_concurrent_tasks", 10),
                cycle_interval_ms=agent_data.get("cycle_interval_ms", 100),
                health_check_interval_s=agent_data.get("health_check_interval_s", 60),
                auto_recovery=agent_data.get("auto_recovery", True)
            )
        
        if "atomspace" in data:
            atom_data = data["atomspace"]
            config.atomspace = AtomspaceConfig(
                max_atoms=atom_data.get("max_atoms", 100000),
                decay_rate=atom_data.get("decay_rate", 0.01),
                attention_threshold=atom_data.get("attention_threshold", 0.1)
            )
        
        if "logging" in data:
            log_data = data["logging"]
            config.logging = LoggingConfig(
                level=log_data.get("level", "INFO"),
                format=log_data.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
                file_path=log_data.get("file_path")
            )
        
        config.integrations_path = data.get("integrations_path", "/home/ubuntu/paystacog/integrations")
        config.data_path = data.get("data_path", "/home/ubuntu/paystacog/data")
        config.environment = data.get("environment", "development")
        
        return config


def load_config(config_path: Optional[str] = None) -> PlatformConfig:
    """Load configuration from file or environment."""
    config = PlatformConfig()
    
    # Try to load from file
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            data = json.load(f)
            config = PlatformConfig.from_dict(data)
            logger.info(f"Loaded configuration from {config_path}")
    
    # Override with environment variables
    if os.environ.get("PAYSTACK_SECRET_KEY"):
        config.api.secret_key = os.environ["PAYSTACK_SECRET_KEY"]
    
    if os.environ.get("PAYSTACK_PUBLIC_KEY"):
        config.api.public_key = os.environ["PAYSTACK_PUBLIC_KEY"]
    
    if os.environ.get("PAYSTACOG_ENVIRONMENT"):
        config.environment = os.environ["PAYSTACOG_ENVIRONMENT"]
    
    if os.environ.get("PAYSTACOG_LOG_LEVEL"):
        config.logging.level = os.environ["PAYSTACOG_LOG_LEVEL"]
    
    return config


def save_config(config: PlatformConfig, config_path: str):
    """Save configuration to file."""
    Path(config_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config.to_dict(), f, indent=2)
    
    logger.info(f"Saved configuration to {config_path}")


# Default configuration file path
DEFAULT_CONFIG_PATH = "/home/ubuntu/paystacog/config/platform.json"
