#!/usr/bin/env python3
"""
PaystaCog Main Entry Point

Main module for running the PaystaCog platform.
"""

import asyncio
import argparse
import logging
import signal
import sys
from typing import Optional
from pathlib import Path

# Add platform to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from platform.core.config import PlatformConfig, load_config, DEFAULT_CONFIG_PATH
from platform.bridges.unified_interface import UnifiedPaystackInterface

logger = logging.getLogger(__name__)


class PaystaCogPlatform:
    """
    Main PaystaCog Platform class.
    
    Provides the primary entry point for running and managing
    the PaystaCog unified financial services platform.
    """
    
    def __init__(self, config: Optional[PlatformConfig] = None):
        self.config = config or load_config()
        self.interface: Optional[UnifiedPaystackInterface] = None
        self.running = False
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.config.logging.level),
            format=self.config.logging.format
        )
        
        if self.config.logging.file_path:
            file_handler = logging.FileHandler(self.config.logging.file_path)
            file_handler.setFormatter(logging.Formatter(self.config.logging.format))
            logging.getLogger().addHandler(file_handler)
    
    async def start(self):
        """Start the platform."""
        logger.info("Starting PaystaCog Platform...")
        
        # Create unified interface
        self.interface = UnifiedPaystackInterface({
            "secret_key": self.config.api.secret_key,
            "public_key": self.config.api.public_key,
            "integrations_path": self.config.integrations_path
        })
        
        # Initialize
        await self.interface.initialize()
        
        self.running = True
        logger.info("PaystaCog Platform started successfully")
        
        # Print platform info
        info = self.interface.get_platform_info()
        logger.info(f"Platform: {info['name']} v{info['version']}")
        logger.info(f"Environment: {self.config.environment}")
        logger.info(f"Capabilities: {len(info['capabilities'])}")
    
    async def stop(self):
        """Stop the platform."""
        logger.info("Stopping PaystaCog Platform...")
        self.running = False
        
        if self.interface and self.interface.orchestrator:
            await self.interface.orchestrator.stop()
        
        logger.info("PaystaCog Platform stopped")
    
    async def run_health_check(self):
        """Run a health check."""
        if not self.interface:
            return {"error": "Platform not initialized"}
        
        return await self.interface.health_check()
    
    async def run_demo(self):
        """Run a demonstration of platform capabilities."""
        if not self.interface:
            await self.start()
        
        print("\n" + "=" * 70)
        print("PaystaCog Platform Demonstration")
        print("=" * 70)
        
        # Platform info
        print("\n[1] Platform Information")
        print("-" * 40)
        info = self.interface.get_platform_info()
        print(f"Name: {info['name']}")
        print(f"Version: {info['version']}")
        print(f"Components: {', '.join(info['components'].keys())}")
        
        # Knowledge query
        print("\n[2] Knowledge Base Query")
        print("-" * 40)
        methods = await self.interface.query_knowledge("payment_methods", {})
        print(f"Payment methods found: {len(methods)}")
        for m in methods[:5]:
            print(f"  - {m['name']}")
        
        # SDK overview
        print("\n[3] SDK Ecosystem")
        print("-" * 40)
        sdks = self.interface.get_all_sdks()
        print(f"Total SDKs: {len(sdks)}")
        for sdk in sdks[:5]:
            print(f"  - {sdk['name']} ({sdk['platform']})")
        
        # Plugin overview
        print("\n[4] Plugin Ecosystem")
        print("-" * 40)
        plugins = self.interface.get_all_plugins()
        print(f"Total Plugins: {len(plugins)}")
        for plugin in plugins[:5]:
            print(f"  - {plugin['name']} ({plugin['platform']})")
        
        # AI recommendation
        print("\n[5] AI-Powered Recommendation")
        print("-" * 40)
        rec = await self.interface.get_recommendation("payment-001", {
            "task_type": "payment.initialize",
            "amount": 50000,
            "currency": "NGN"
        })
        print(f"Recommended action: {rec.get('recommended_action')}")
        print(f"Confidence: {rec.get('confidence', 0):.2%}")
        
        # Available workflows
        print("\n[6] Available Workflows")
        print("-" * 40)
        workflows = self.interface.get_available_workflows()
        for wf in workflows:
            print(f"  - {wf}")
        
        # Health check
        print("\n[7] System Health")
        print("-" * 40)
        health = await self.interface.health_check()
        print(f"Overall Status: {health['status']}")
        
        # Metrics
        print("\n[8] Platform Metrics")
        print("-" * 40)
        metrics = self.interface.get_metrics()
        print(f"Uptime: {metrics['uptime_seconds']:.0f} seconds")
        print(f"Events logged: {metrics['events_logged']}")
        
        print("\n" + "=" * 70)
        print("Demonstration Complete")
        print("=" * 70 + "\n")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="PaystaCog Platform")
    parser.add_argument("--config", "-c", help="Configuration file path",
                       default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--demo", "-d", action="store_true",
                       help="Run demonstration")
    parser.add_argument("--health", "-H", action="store_true",
                       help="Run health check")
    parser.add_argument("--serve", "-s", action="store_true",
                       help="Start platform server")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config if Path(args.config).exists() else None)
    
    # Create platform
    platform = PaystaCogPlatform(config)
    
    # Handle signals
    def signal_handler(sig, frame):
        logger.info("Received shutdown signal")
        asyncio.create_task(platform.stop())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        if args.demo:
            await platform.run_demo()
        elif args.health:
            await platform.start()
            health = await platform.run_health_check()
            import json
            print(json.dumps(health, indent=2, default=str))
        elif args.serve:
            await platform.start()
            logger.info("Platform running. Press Ctrl+C to stop.")
            while platform.running:
                await asyncio.sleep(1)
        else:
            # Default: run demo
            await platform.run_demo()
    finally:
        await platform.stop()


if __name__ == "__main__":
    asyncio.run(main())
