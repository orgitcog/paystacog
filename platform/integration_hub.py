#!/usr/bin/env python3
"""
PaystaCog Integration Hub

This module serves as the central entry point for all integration opportunities,
combining unified analytics, health monitoring, and intelligent workflows into
a single cohesive interface for existing Paystack users.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio
import logging

# Import integration modules
from analytics.unified_analytics import (
    UnifiedAnalyticsEngine, 
    TransactionRecord, 
    Platform,
    create_analytics_engine
)
from monitoring.health_monitor import (
    HealthMonitor,
    HealthStatus,
    create_health_monitor
)
from workflows.intelligent_workflows import (
    IntelligentWorkflowEngine,
    WorkflowStatus,
    create_workflow_engine
)

logger = logging.getLogger(__name__)


@dataclass
class IntegrationStatus:
    """Status of the integration hub."""
    analytics_ready: bool = False
    monitoring_ready: bool = False
    workflows_ready: bool = False
    overall_health: str = "unknown"
    last_updated: Optional[datetime] = None


class PaystaCogIntegrationHub:
    """
    Central integration hub for PaystaCog platform.
    
    This hub provides a unified interface to:
    1. Unified Cross-Platform Analytics
    2. Automated Health Monitoring
    3. Intelligent Payment Workflows
    
    Designed for seamless adoption by existing Paystack users.
    """
    
    def __init__(self):
        self.analytics: Optional[UnifiedAnalyticsEngine] = None
        self.monitor: Optional[HealthMonitor] = None
        self.workflows: Optional[IntelligentWorkflowEngine] = None
        self._initialized = False
        self._status = IntegrationStatus()
    
    async def initialize(self):
        """Initialize all integration components."""
        logger.info("Initializing PaystaCog Integration Hub...")
        
        # Initialize Analytics Engine
        try:
            self.analytics = create_analytics_engine()
            await self.analytics.initialize()
            self._status.analytics_ready = True
            logger.info("Analytics Engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Analytics Engine: {e}")
        
        # Initialize Health Monitor
        try:
            self.monitor = create_health_monitor()
            self._status.monitoring_ready = True
            logger.info("Health Monitor initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Health Monitor: {e}")
        
        # Initialize Workflow Engine
        try:
            self.workflows = create_workflow_engine()
            self._status.workflows_ready = True
            logger.info("Workflow Engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Workflow Engine: {e}")
        
        self._initialized = True
        self._status.last_updated = datetime.utcnow()
        self._update_overall_health()
        
        logger.info("PaystaCog Integration Hub initialized successfully")
    
    def _update_overall_health(self):
        """Update overall health status."""
        ready_count = sum([
            self._status.analytics_ready,
            self._status.monitoring_ready,
            self._status.workflows_ready
        ])
        
        if ready_count == 3:
            self._status.overall_health = "healthy"
        elif ready_count >= 2:
            self._status.overall_health = "degraded"
        elif ready_count >= 1:
            self._status.overall_health = "critical"
        else:
            self._status.overall_health = "offline"
    
    def get_status(self) -> Dict[str, Any]:
        """Get current integration hub status."""
        return {
            "initialized": self._initialized,
            "analytics_ready": self._status.analytics_ready,
            "monitoring_ready": self._status.monitoring_ready,
            "workflows_ready": self._status.workflows_ready,
            "overall_health": self._status.overall_health,
            "last_updated": self._status.last_updated.isoformat() if self._status.last_updated else None
        }
    
    # ==================== ANALYTICS INTERFACE ====================
    
    def track_transaction(self, 
                         transaction_id: str,
                         platform: str,
                         customer_id: str,
                         customer_email: str,
                         amount: int,
                         currency: str,
                         status: str,
                         payment_method: str,
                         metadata: Optional[Dict] = None):
        """
        Track a transaction from any platform.
        
        This is the primary method for feeding data into the unified analytics system.
        Call this after every successful transaction across all your platforms.
        
        Args:
            transaction_id: Unique transaction identifier
            platform: Source platform (woocommerce, mobile_android, etc.)
            customer_id: Customer identifier
            customer_email: Customer email
            amount: Amount in smallest currency unit (kobo, pesewas, cents)
            currency: Currency code (NGN, GHS, ZAR, USD)
            status: Transaction status (success, failed, pending)
            payment_method: Payment method used (card, bank_transfer, ussd, etc.)
            metadata: Optional additional data
        """
        if not self._status.analytics_ready:
            raise RuntimeError("Analytics engine not initialized")
        
        # Convert platform string to enum
        try:
            platform_enum = Platform(platform.lower())
        except ValueError:
            platform_enum = Platform.DIRECT_API
        
        record = TransactionRecord(
            transaction_id=transaction_id,
            platform=platform_enum,
            customer_id=customer_id,
            customer_email=customer_email,
            amount=amount,
            currency=currency,
            status=status,
            payment_method=payment_method,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        self.analytics.ingest_transaction(record)
    
    async def get_analytics_report(self, 
                                   days: int = 30,
                                   platforms: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate a unified analytics report.
        
        Args:
            days: Number of days to include in report
            platforms: Optional list of platforms to filter by
        
        Returns:
            Comprehensive analytics report with metrics, trends, and insights
        """
        if not self._status.analytics_ready:
            raise RuntimeError("Analytics engine not initialized")
        
        platform_enums = None
        if platforms:
            platform_enums = [Platform(p.lower()) for p in platforms]
        
        report = await self.analytics.generate_report(platforms=platform_enums)
        return report.to_dict()
    
    def get_customer_360(self, customer_id: str) -> Dict[str, Any]:
        """
        Get 360-degree view of a customer across all platforms.
        
        Args:
            customer_id: Customer identifier
        
        Returns:
            Comprehensive customer profile with transaction history and engagement metrics
        """
        if not self._status.analytics_ready:
            raise RuntimeError("Analytics engine not initialized")
        
        return self.analytics.get_customer_360_view(customer_id)
    
    # ==================== MONITORING INTERFACE ====================
    
    async def run_health_check(self) -> Dict[str, Any]:
        """
        Run a full health check on all integrations.
        
        Returns:
            Health check results for all monitored components
        """
        if not self._status.monitoring_ready:
            raise RuntimeError("Health monitor not initialized")
        
        return await self.monitor.run_full_health_check()
    
    def check_compatibility(self, 
                           component: str,
                           platform_version: str,
                           dependencies: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Check compatibility of a component with given versions.
        
        Args:
            component: Component ID (e.g., plugin_woocommerce, sdk_node)
            platform_version: Version of the platform
            dependencies: Dictionary of dependency versions
        
        Returns:
            Compatibility check result with issues and upgrade path
        """
        if not self._status.monitoring_ready:
            raise RuntimeError("Health monitor not initialized")
        
        result = self.monitor.check_compatibility(
            component,
            platform_version,
            dependencies
        )
        return result.to_dict()
    
    def get_alerts(self, unresolved_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get system alerts.
        
        Args:
            unresolved_only: If True, only return unresolved alerts
        
        Returns:
            List of alerts
        """
        if not self._status.monitoring_ready:
            raise RuntimeError("Health monitor not initialized")
        
        alerts = self.monitor.get_alerts(unresolved_only=unresolved_only)
        return [a.to_dict() for a in alerts]
    
    async def start_monitoring(self):
        """Start continuous health monitoring."""
        if not self._status.monitoring_ready:
            raise RuntimeError("Health monitor not initialized")
        
        await self.monitor.start_monitoring()
    
    async def stop_monitoring(self):
        """Stop continuous health monitoring."""
        if self.monitor:
            await self.monitor.stop_monitoring()
    
    # ==================== WORKFLOW INTERFACE ====================
    
    async def process_payment(self, 
                             email: str,
                             amount: int,
                             currency: str = "NGN",
                             **kwargs) -> Dict[str, Any]:
        """
        Process a payment using the intelligent workflow.
        
        This method provides AI-enhanced payment processing with built-in
        fraud detection, compliance checking, and intelligent routing.
        
        Args:
            email: Customer email
            amount: Amount in smallest currency unit
            currency: Currency code
            **kwargs: Additional transaction data
        
        Returns:
            Workflow execution result with transaction details
        """
        if not self._status.workflows_ready:
            raise RuntimeError("Workflow engine not initialized")
        
        execution = await self.workflows.execute_workflow("payment_processing", {
            "email": email,
            "amount": amount,
            "currency": currency,
            **kwargs
        })
        
        # Track in analytics if successful
        if execution.status == WorkflowStatus.COMPLETED and self._status.analytics_ready:
            txn = execution.output_data.get("transaction", {})
            self.track_transaction(
                transaction_id=txn.get("reference", ""),
                platform="direct_api",
                customer_id=kwargs.get("customer_id", email),
                customer_email=email,
                amount=amount,
                currency=currency,
                status="success",
                payment_method=kwargs.get("payment_method", "card")
            )
        
        return execution.to_dict()
    
    async def process_refund(self,
                            transaction_reference: str,
                            amount: Optional[int] = None,
                            reason: str = "Customer request") -> Dict[str, Any]:
        """
        Process a refund using the intelligent workflow.
        
        Args:
            transaction_reference: Original transaction reference
            amount: Refund amount (full refund if not specified)
            reason: Reason for refund
        
        Returns:
            Workflow execution result with refund details
        """
        if not self._status.workflows_ready:
            raise RuntimeError("Workflow engine not initialized")
        
        input_data = {
            "transaction_reference": transaction_reference,
            "reason": reason
        }
        if amount:
            input_data["amount"] = amount
        
        execution = await self.workflows.execute_workflow("refund_processing", input_data)
        return execution.to_dict()
    
    async def create_subscription(self,
                                 plan_code: str,
                                 customer_code: str,
                                 **kwargs) -> Dict[str, Any]:
        """
        Create a subscription using the intelligent workflow.
        
        Args:
            plan_code: Subscription plan code
            customer_code: Customer code
            **kwargs: Additional subscription data
        
        Returns:
            Workflow execution result with subscription details
        """
        if not self._status.workflows_ready:
            raise RuntimeError("Workflow engine not initialized")
        
        execution = await self.workflows.execute_workflow("subscription_creation", {
            "plan_code": plan_code,
            "customer_code": customer_code,
            **kwargs
        })
        return execution.to_dict()
    
    async def process_transfer(self,
                              recipient_code: str,
                              amount: int,
                              reason: str = "Transfer",
                              **kwargs) -> Dict[str, Any]:
        """
        Process a transfer using the intelligent workflow.
        
        Args:
            recipient_code: Recipient code
            amount: Transfer amount
            reason: Transfer reason
            **kwargs: Additional transfer data
        
        Returns:
            Workflow execution result with transfer details
        """
        if not self._status.workflows_ready:
            raise RuntimeError("Workflow engine not initialized")
        
        execution = await self.workflows.execute_workflow("transfer_processing", {
            "recipient_code": recipient_code,
            "amount": amount,
            "reason": reason,
            **kwargs
        })
        return execution.to_dict()
    
    def get_workflow_history(self, 
                            workflow_name: Optional[str] = None,
                            limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get workflow execution history.
        
        Args:
            workflow_name: Optional workflow name filter
            limit: Maximum number of results
        
        Returns:
            List of workflow executions
        """
        if not self._status.workflows_ready:
            raise RuntimeError("Workflow engine not initialized")
        
        executions = self.workflows.list_executions(
            workflow_name=workflow_name,
            limit=limit
        )
        return [e.to_dict() for e in executions]
    
    # ==================== DASHBOARD ====================
    
    async def get_dashboard(self) -> Dict[str, Any]:
        """
        Get a comprehensive dashboard view.
        
        Returns:
            Dashboard data including analytics summary, health status, and recent activity
        """
        dashboard = {
            "generated_at": datetime.utcnow().isoformat(),
            "hub_status": self.get_status()
        }
        
        # Analytics summary
        if self._status.analytics_ready:
            dashboard["analytics"] = {
                "statistics": self.analytics.get_statistics()
            }
            try:
                report = await self.analytics.generate_report()
                dashboard["analytics"]["summary"] = {
                    "total_revenue": report.metrics.get("total_revenue"),
                    "total_transactions": report.metrics.get("total_transactions"),
                    "success_rate": report.metrics.get("success_rate"),
                    "unique_customers": report.metrics.get("unique_customers")
                }
                dashboard["analytics"]["insights"] = report.insights[:3]
            except Exception as e:
                dashboard["analytics"]["error"] = str(e)
        
        # Health summary
        if self._status.monitoring_ready:
            try:
                health = await self.monitor.run_full_health_check()
                dashboard["health"] = {
                    "overall_status": health["overall_status"],
                    "summary": health["summary"]
                }
                dashboard["alerts"] = [a.to_dict() for a in self.monitor.get_alerts(unresolved_only=True)[:5]]
            except Exception as e:
                dashboard["health"] = {"error": str(e)}
        
        # Workflow summary
        if self._status.workflows_ready:
            dashboard["workflows"] = {
                "statistics": self.workflows.get_statistics(),
                "recent": [e.to_dict() for e in self.workflows.list_executions(limit=5)]
            }
        
        return dashboard


# Factory function
def create_integration_hub() -> PaystaCogIntegrationHub:
    """Create a new integration hub instance."""
    return PaystaCogIntegrationHub()


# Quick start function
async def quick_start() -> PaystaCogIntegrationHub:
    """Create and initialize an integration hub."""
    hub = create_integration_hub()
    await hub.initialize()
    return hub


if __name__ == "__main__":
    async def demo():
        print("=" * 70)
        print("PAYSTACOG INTEGRATION HUB - QUICK START DEMO")
        print("=" * 70)
        
        # Initialize hub
        print("\n1. Initializing Integration Hub...")
        hub = await quick_start()
        
        status = hub.get_status()
        print(f"   Status: {status['overall_health'].upper()}")
        print(f"   Analytics: {'✓' if status['analytics_ready'] else '✗'}")
        print(f"   Monitoring: {'✓' if status['monitoring_ready'] else '✗'}")
        print(f"   Workflows: {'✓' if status['workflows_ready'] else '✗'}")
        
        # Track some transactions
        print("\n2. Tracking Sample Transactions...")
        platforms = ["woocommerce", "mobile_android", "inline_js"]
        for i, platform in enumerate(platforms):
            hub.track_transaction(
                transaction_id=f"txn_{i+1:04d}",
                platform=platform,
                customer_id=f"cust_{(i % 3) + 1:03d}",
                customer_email=f"customer{(i % 3) + 1}@example.com",
                amount=(i + 1) * 10000,
                currency="NGN",
                status="success",
                payment_method="card"
            )
        print(f"   Tracked {len(platforms)} transactions")
        
        # Process a payment
        print("\n3. Processing Payment via Intelligent Workflow...")
        payment = await hub.process_payment(
            email="newcustomer@example.com",
            amount=75000,
            currency="NGN",
            customer_verified=True
        )
        print(f"   Status: {payment['status']}")
        if payment['output_data'].get('transaction'):
            print(f"   Reference: {payment['output_data']['transaction'].get('reference')}")
        
        # Run health check
        print("\n4. Running Health Check...")
        health = await hub.run_health_check()
        print(f"   Overall: {health['overall_status'].upper()}")
        print(f"   Components: {health['summary']['total']} total, {health['summary']['healthy']} healthy")
        
        # Get dashboard
        print("\n5. Generating Dashboard...")
        dashboard = await hub.get_dashboard()
        
        if 'analytics' in dashboard and 'summary' in dashboard['analytics']:
            summary = dashboard['analytics']['summary']
            print(f"   Total Transactions: {summary.get('total_transactions', 0)}")
            print(f"   Success Rate: {summary.get('success_rate', 0):.1f}%")
        
        if 'workflows' in dashboard:
            wf_stats = dashboard['workflows']['statistics']
            print(f"   Workflow Executions: {wf_stats.get('total_executions', 0)}")
        
        print("\n" + "=" * 70)
        print("INTEGRATION HUB READY FOR USE")
        print("=" * 70)
        print("\nQuick Reference:")
        print("  hub.track_transaction(...)     - Track transactions for analytics")
        print("  hub.get_analytics_report()     - Generate analytics report")
        print("  hub.get_customer_360(id)       - Get customer 360 view")
        print("  hub.run_health_check()         - Check integration health")
        print("  hub.check_compatibility(...)   - Check version compatibility")
        print("  hub.process_payment(...)       - Process payment with AI")
        print("  hub.process_refund(...)        - Process refund with validation")
        print("  hub.get_dashboard()            - Get comprehensive dashboard")
    
    asyncio.run(demo())
