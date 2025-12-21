"""
PaystaCog Unified Analytics Module

Provides cross-platform analytics and customer insights.
"""

from .unified_analytics import (
    UnifiedAnalyticsEngine,
    TransactionRecord,
    CustomerProfile,
    AnalyticsReport,
    Platform,
    MetricType,
    create_analytics_engine
)

__all__ = [
    'UnifiedAnalyticsEngine',
    'TransactionRecord',
    'CustomerProfile',
    'AnalyticsReport',
    'Platform',
    'MetricType',
    'create_analytics_engine'
]
