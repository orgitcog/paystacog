#!/usr/bin/env python3
"""
Automated Integration Health and Compatibility Monitoring System

This module provides proactive monitoring of all Paystack integrations,
including SDKs, plugins, and API endpoints.

Integration Opportunity #2: Automated Integration Health and Compatibility Monitoring
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json
import logging
import re

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ComponentType(Enum):
    """Types of monitored components."""
    SDK = "sdk"
    PLUGIN = "plugin"
    API_ENDPOINT = "api_endpoint"
    WEBHOOK = "webhook"
    DATABASE = "database"


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class HealthCheck:
    """Result of a health check."""
    component_id: str
    component_type: ComponentType
    status: HealthStatus
    timestamp: datetime
    response_time_ms: Optional[float] = None
    details: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "component_id": self.component_id,
            "component_type": self.component_type.value,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "response_time_ms": self.response_time_ms,
            "details": self.details,
            "recommendations": self.recommendations
        }


@dataclass
class CompatibilityCheck:
    """Result of a compatibility check."""
    component_id: str
    platform_version: str
    dependency_versions: Dict[str, str]
    is_compatible: bool
    issues: List[str] = field(default_factory=list)
    upgrade_path: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "component_id": self.component_id,
            "platform_version": self.platform_version,
            "dependency_versions": self.dependency_versions,
            "is_compatible": self.is_compatible,
            "issues": self.issues,
            "upgrade_path": self.upgrade_path
        }


@dataclass
class Alert:
    """System alert."""
    alert_id: str
    severity: AlertSeverity
    component_id: str
    message: str
    timestamp: datetime
    acknowledged: bool = False
    resolved: bool = False
    resolution_notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "severity": self.severity.value,
            "component_id": self.component_id,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "acknowledged": self.acknowledged,
            "resolved": self.resolved,
            "resolution_notes": self.resolution_notes
        }


@dataclass
class MonitoredComponent:
    """A component being monitored."""
    component_id: str
    component_type: ComponentType
    name: str
    version: str
    platform: Optional[str] = None
    min_supported_version: Optional[str] = None
    max_supported_version: Optional[str] = None
    dependencies: Dict[str, str] = field(default_factory=dict)
    health_endpoint: Optional[str] = None
    last_check: Optional[datetime] = None
    current_status: HealthStatus = HealthStatus.UNKNOWN
    check_interval_seconds: int = 300  # 5 minutes default
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "component_id": self.component_id,
            "component_type": self.component_type.value,
            "name": self.name,
            "version": self.version,
            "platform": self.platform,
            "min_supported_version": self.min_supported_version,
            "max_supported_version": self.max_supported_version,
            "dependencies": self.dependencies,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "current_status": self.current_status.value,
            "check_interval_seconds": self.check_interval_seconds
        }


class HealthMonitor:
    """
    Automated health and compatibility monitoring system.
    
    This system proactively monitors all Paystack integrations and
    provides alerts and recommendations for maintaining optimal operation.
    """
    
    def __init__(self):
        self.components: Dict[str, MonitoredComponent] = {}
        self.health_history: Dict[str, List[HealthCheck]] = {}
        self.alerts: List[Alert] = []
        self.alert_handlers: List[Callable[[Alert], None]] = []
        self._running = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._initialize_default_components()
    
    def _initialize_default_components(self):
        """Initialize default monitored components."""
        
        # SDKs
        sdks = [
            ("sdk_android", "paystack-android", "3.1.0", "android"),
            ("sdk_ios", "paystack-ios", "5.0.0", "ios"),
            ("sdk_flutter", "paystack_flutter", "1.0.0", "flutter"),
            ("sdk_node", "paystack-node", "2.0.0", "node"),
            ("sdk_python", "paystack-python", "2.0.0", "python"),
            ("sdk_php", "omnipay-paystack", "1.0.0", "php"),
        ]
        
        for sdk_id, name, version, platform in sdks:
            self.components[sdk_id] = MonitoredComponent(
                component_id=sdk_id,
                component_type=ComponentType.SDK,
                name=name,
                version=version,
                platform=platform,
                check_interval_seconds=3600  # Check hourly
            )
        
        # Plugins
        plugins = [
            ("plugin_woocommerce", "Paystack WooCommerce", "5.8.0", "wordpress", {"woocommerce": "3.0.0", "php": "7.2"}),
            ("plugin_magento2", "Paystack Magento 2", "2.0.0", "magento2", {"magento": "2.0.0", "php": "7.2"}),
            ("plugin_prestashop", "Paystack PrestaShop", "1.0.0", "prestashop", {"prestashop": "1.7.0", "php": "7.2"}),
            ("plugin_memberpress", "Paystack MemberPress", "1.0.0", "wordpress", {"memberpress": "1.9.0", "php": "7.2"}),
            ("plugin_moodle", "Paystack Moodle", "1.0.0", "moodle", {"moodle": "3.0.0", "php": "7.2"}),
        ]
        
        for plugin_id, name, version, platform, deps in plugins:
            self.components[plugin_id] = MonitoredComponent(
                component_id=plugin_id,
                component_type=ComponentType.PLUGIN,
                name=name,
                version=version,
                platform=platform,
                dependencies=deps,
                check_interval_seconds=3600
            )
        
        # API Endpoints
        api_endpoints = [
            ("api_transaction", "Transaction API", "/transaction"),
            ("api_customer", "Customer API", "/customer"),
            ("api_plan", "Plan API", "/plan"),
            ("api_subscription", "Subscription API", "/subscription"),
            ("api_transfer", "Transfer API", "/transfer"),
        ]
        
        for api_id, name, endpoint in api_endpoints:
            self.components[api_id] = MonitoredComponent(
                component_id=api_id,
                component_type=ComponentType.API_ENDPOINT,
                name=name,
                version="v1",
                health_endpoint=f"https://api.paystack.co{endpoint}",
                check_interval_seconds=60  # Check every minute
            )
    
    def register_component(self, component: MonitoredComponent):
        """Register a component for monitoring."""
        self.components[component.component_id] = component
        self.health_history[component.component_id] = []
        logger.info(f"Registered component for monitoring: {component.name}")
    
    def register_alert_handler(self, handler: Callable[[Alert], None]):
        """Register a handler for alerts."""
        self.alert_handlers.append(handler)
    
    async def start_monitoring(self):
        """Start the monitoring loop."""
        if self._running:
            return
        
        self._running = True
        self._monitor_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Health monitoring started")
    
    async def stop_monitoring(self):
        """Stop the monitoring loop."""
        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Health monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self._running:
            try:
                for component_id, component in self.components.items():
                    # Check if it's time to check this component
                    if component.last_check:
                        elapsed = (datetime.utcnow() - component.last_check).total_seconds()
                        if elapsed < component.check_interval_seconds:
                            continue
                    
                    # Perform health check
                    health_check = await self.check_component_health(component_id)
                    
                    # Check for status changes
                    if component.current_status != health_check.status:
                        await self._handle_status_change(component, health_check)
                
                # Sleep before next iteration
                await asyncio.sleep(10)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(30)
    
    async def check_component_health(self, component_id: str) -> HealthCheck:
        """Check the health of a specific component."""
        component = self.components.get(component_id)
        if not component:
            return HealthCheck(
                component_id=component_id,
                component_type=ComponentType.SDK,
                status=HealthStatus.UNKNOWN,
                timestamp=datetime.utcnow(),
                details={"error": "Component not found"}
            )
        
        start_time = datetime.utcnow()
        
        # Perform type-specific health check
        if component.component_type == ComponentType.SDK:
            health_check = await self._check_sdk_health(component)
        elif component.component_type == ComponentType.PLUGIN:
            health_check = await self._check_plugin_health(component)
        elif component.component_type == ComponentType.API_ENDPOINT:
            health_check = await self._check_api_health(component)
        else:
            health_check = HealthCheck(
                component_id=component_id,
                component_type=component.component_type,
                status=HealthStatus.UNKNOWN,
                timestamp=datetime.utcnow()
            )
        
        # Calculate response time
        health_check.response_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Update component status
        component.last_check = datetime.utcnow()
        component.current_status = health_check.status
        
        # Store in history
        if component_id not in self.health_history:
            self.health_history[component_id] = []
        self.health_history[component_id].append(health_check)
        
        # Keep only last 100 checks
        if len(self.health_history[component_id]) > 100:
            self.health_history[component_id] = self.health_history[component_id][-100:]
        
        return health_check
    
    async def _check_sdk_health(self, component: MonitoredComponent) -> HealthCheck:
        """Check SDK health."""
        details = {
            "name": component.name,
            "version": component.version,
            "platform": component.platform
        }
        
        recommendations = []
        status = HealthStatus.HEALTHY
        
        # Check version currency (simulated)
        # In production, this would check against latest releases
        version_parts = component.version.split(".")
        if len(version_parts) >= 1:
            major = int(version_parts[0])
            if major < 2:
                status = HealthStatus.WARNING
                recommendations.append(
                    f"SDK version {component.version} may be outdated. "
                    "Consider upgrading to the latest version."
                )
        
        details["version_status"] = "current" if status == HealthStatus.HEALTHY else "outdated"
        
        return HealthCheck(
            component_id=component.component_id,
            component_type=ComponentType.SDK,
            status=status,
            timestamp=datetime.utcnow(),
            details=details,
            recommendations=recommendations
        )
    
    async def _check_plugin_health(self, component: MonitoredComponent) -> HealthCheck:
        """Check plugin health."""
        details = {
            "name": component.name,
            "version": component.version,
            "platform": component.platform,
            "dependencies": component.dependencies
        }
        
        recommendations = []
        status = HealthStatus.HEALTHY
        
        # Check dependencies (simulated compatibility check)
        for dep_name, min_version in component.dependencies.items():
            # Simulate dependency check
            details[f"{dep_name}_compatible"] = True
        
        # Check for known issues (simulated)
        if "woocommerce" in component.component_id:
            details["webhook_configured"] = True
            details["ssl_enabled"] = True
        
        return HealthCheck(
            component_id=component.component_id,
            component_type=ComponentType.PLUGIN,
            status=status,
            timestamp=datetime.utcnow(),
            details=details,
            recommendations=recommendations
        )
    
    async def _check_api_health(self, component: MonitoredComponent) -> HealthCheck:
        """Check API endpoint health."""
        details = {
            "endpoint": component.health_endpoint,
            "version": component.version
        }
        
        # Simulate API health check
        # In production, this would make actual HTTP requests
        status = HealthStatus.HEALTHY
        details["reachable"] = True
        details["response_code"] = 200
        
        return HealthCheck(
            component_id=component.component_id,
            component_type=ComponentType.API_ENDPOINT,
            status=status,
            timestamp=datetime.utcnow(),
            details=details,
            recommendations=[]
        )
    
    async def _handle_status_change(self, component: MonitoredComponent, 
                                   health_check: HealthCheck):
        """Handle a status change for a component."""
        old_status = component.current_status
        new_status = health_check.status
        
        # Determine alert severity
        if new_status == HealthStatus.CRITICAL:
            severity = AlertSeverity.CRITICAL
        elif new_status == HealthStatus.WARNING:
            severity = AlertSeverity.WARNING
        elif old_status in [HealthStatus.CRITICAL, HealthStatus.WARNING] and new_status == HealthStatus.HEALTHY:
            severity = AlertSeverity.INFO
        else:
            severity = AlertSeverity.INFO
        
        # Create alert
        alert = Alert(
            alert_id=f"alert_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{component.component_id}",
            severity=severity,
            component_id=component.component_id,
            message=f"{component.name} status changed from {old_status.value} to {new_status.value}",
            timestamp=datetime.utcnow()
        )
        
        self.alerts.append(alert)
        
        # Notify handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")
        
        logger.info(f"Alert created: {alert.message}")
    
    def check_compatibility(self, component_id: str, 
                           platform_version: str,
                           dependency_versions: Optional[Dict[str, str]] = None) -> CompatibilityCheck:
        """Check compatibility of a component with given versions."""
        component = self.components.get(component_id)
        if not component:
            return CompatibilityCheck(
                component_id=component_id,
                platform_version=platform_version,
                dependency_versions=dependency_versions or {},
                is_compatible=False,
                issues=["Component not found"]
            )
        
        issues = []
        is_compatible = True
        
        # Check platform version
        if component.min_supported_version:
            if self._compare_versions(platform_version, component.min_supported_version) < 0:
                is_compatible = False
                issues.append(
                    f"Platform version {platform_version} is below minimum "
                    f"supported version {component.min_supported_version}"
                )
        
        if component.max_supported_version:
            if self._compare_versions(platform_version, component.max_supported_version) > 0:
                is_compatible = False
                issues.append(
                    f"Platform version {platform_version} is above maximum "
                    f"supported version {component.max_supported_version}"
                )
        
        # Check dependencies
        if dependency_versions:
            for dep_name, required_version in component.dependencies.items():
                if dep_name in dependency_versions:
                    actual_version = dependency_versions[dep_name]
                    if self._compare_versions(actual_version, required_version) < 0:
                        is_compatible = False
                        issues.append(
                            f"{dep_name} version {actual_version} is below "
                            f"required version {required_version}"
                        )
        
        # Generate upgrade path if incompatible
        upgrade_path = None
        if not is_compatible:
            upgrade_path = f"Upgrade to {component.name} version {component.version} or later"
        
        return CompatibilityCheck(
            component_id=component_id,
            platform_version=platform_version,
            dependency_versions=dependency_versions or {},
            is_compatible=is_compatible,
            issues=issues,
            upgrade_path=upgrade_path
        )
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """Compare two version strings."""
        def normalize(v):
            return [int(x) for x in re.findall(r'\d+', v)]
        
        n1, n2 = normalize(v1), normalize(v2)
        
        while len(n1) < len(n2):
            n1.append(0)
        while len(n2) < len(n1):
            n2.append(0)
        
        for a, b in zip(n1, n2):
            if a < b:
                return -1
            elif a > b:
                return 1
        return 0
    
    async def run_full_health_check(self) -> Dict[str, Any]:
        """Run a full health check on all components."""
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": HealthStatus.HEALTHY.value,
            "components": {},
            "summary": {
                "total": len(self.components),
                "healthy": 0,
                "warning": 0,
                "critical": 0,
                "unknown": 0
            }
        }
        
        for component_id in self.components:
            health_check = await self.check_component_health(component_id)
            results["components"][component_id] = health_check.to_dict()
            
            # Update summary
            status_key = health_check.status.value
            if status_key in results["summary"]:
                results["summary"][status_key] += 1
        
        # Determine overall status
        if results["summary"]["critical"] > 0:
            results["overall_status"] = HealthStatus.CRITICAL.value
        elif results["summary"]["warning"] > 0:
            results["overall_status"] = HealthStatus.WARNING.value
        elif results["summary"]["unknown"] > 0:
            results["overall_status"] = HealthStatus.UNKNOWN.value
        
        return results
    
    def get_alerts(self, 
                  severity: Optional[AlertSeverity] = None,
                  unresolved_only: bool = False,
                  limit: int = 100) -> List[Alert]:
        """Get alerts with optional filtering."""
        alerts = self.alerts
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        if unresolved_only:
            alerts = [a for a in alerts if not a.resolved]
        
        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)[:limit]
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return True
        return False
    
    def resolve_alert(self, alert_id: str, notes: Optional[str] = None) -> bool:
        """Resolve an alert."""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                alert.resolution_notes = notes
                return True
        return False
    
    def get_component_history(self, component_id: str, 
                             limit: int = 50) -> List[HealthCheck]:
        """Get health check history for a component."""
        history = self.health_history.get(component_id, [])
        return sorted(history, key=lambda h: h.timestamp, reverse=True)[:limit]
    
    def get_uptime_report(self, component_id: str, 
                         period_hours: int = 24) -> Dict[str, Any]:
        """Get uptime report for a component."""
        history = self.health_history.get(component_id, [])
        
        cutoff = datetime.utcnow() - timedelta(hours=period_hours)
        recent_checks = [h for h in history if h.timestamp >= cutoff]
        
        if not recent_checks:
            return {
                "component_id": component_id,
                "period_hours": period_hours,
                "uptime_percentage": None,
                "message": "No health checks in the specified period"
            }
        
        healthy_checks = sum(1 for h in recent_checks if h.status == HealthStatus.HEALTHY)
        uptime = healthy_checks / len(recent_checks) * 100
        
        return {
            "component_id": component_id,
            "period_hours": period_hours,
            "total_checks": len(recent_checks),
            "healthy_checks": healthy_checks,
            "uptime_percentage": uptime,
            "average_response_time_ms": sum(
                h.response_time_ms or 0 for h in recent_checks
            ) / len(recent_checks)
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        return {
            "total_components": len(self.components),
            "components_by_type": {
                ct.value: sum(1 for c in self.components.values() if c.component_type == ct)
                for ct in ComponentType
            },
            "current_status_summary": {
                hs.value: sum(1 for c in self.components.values() if c.current_status == hs)
                for hs in HealthStatus
            },
            "total_alerts": len(self.alerts),
            "unresolved_alerts": sum(1 for a in self.alerts if not a.resolved),
            "monitoring_active": self._running
        }


# Factory function
def create_health_monitor() -> HealthMonitor:
    """Create a new health monitor instance."""
    return HealthMonitor()


if __name__ == "__main__":
    async def demo():
        monitor = create_health_monitor()
        
        # Register alert handler
        def alert_handler(alert: Alert):
            print(f"[ALERT] {alert.severity.value.upper()}: {alert.message}")
        
        monitor.register_alert_handler(alert_handler)
        
        print("=" * 60)
        print("AUTOMATED HEALTH MONITORING SYSTEM")
        print("=" * 60)
        
        # Run full health check
        print("\n--- Running Full Health Check ---")
        results = await monitor.run_full_health_check()
        
        print(f"\nOverall Status: {results['overall_status'].upper()}")
        print(f"Total Components: {results['summary']['total']}")
        print(f"  Healthy: {results['summary']['healthy']}")
        print(f"  Warning: {results['summary']['warning']}")
        print(f"  Critical: {results['summary']['critical']}")
        
        # Check specific component
        print("\n--- SDK Health Check ---")
        sdk_health = await monitor.check_component_health("sdk_node")
        print(f"Component: {sdk_health.component_id}")
        print(f"Status: {sdk_health.status.value}")
        print(f"Response Time: {sdk_health.response_time_ms:.2f}ms")
        
        # Compatibility check
        print("\n--- Compatibility Check ---")
        compat = monitor.check_compatibility(
            "plugin_woocommerce",
            platform_version="5.0.0",
            dependency_versions={"woocommerce": "4.0.0", "php": "7.4"}
        )
        print(f"Component: {compat.component_id}")
        print(f"Compatible: {compat.is_compatible}")
        if compat.issues:
            print(f"Issues: {', '.join(compat.issues)}")
        
        # Get statistics
        print("\n--- Monitoring Statistics ---")
        stats = monitor.get_statistics()
        print(f"Total Components: {stats['total_components']}")
        print(f"Components by Type:")
        for ctype, count in stats['components_by_type'].items():
            if count > 0:
                print(f"  {ctype}: {count}")
        
        print("\n" + "=" * 60)
        print("Demo Complete")
        print("=" * 60)
    
    asyncio.run(demo())
