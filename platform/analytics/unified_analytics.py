#!/usr/bin/env python3
"""
Unified Cross-Platform Analytics Engine

This module provides comprehensive analytics across all integrated Paystack
platforms, enabling holistic business insights from a single interface.

Integration Opportunity #1: Unified Cross-Platform Analytics and Customer Insights
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import asyncio
import json
import logging

logger = logging.getLogger(__name__)


class Platform(Enum):
    """Supported platforms for analytics aggregation."""
    WOOCOMMERCE = "woocommerce"
    MAGENTO = "magento"
    PRESTASHOP = "prestashop"
    OPENCART = "opencart"
    WORDPRESS = "wordpress"
    MOBILE_ANDROID = "mobile_android"
    MOBILE_IOS = "mobile_ios"
    FLUTTER = "flutter"
    DIRECT_API = "direct_api"
    INLINE_JS = "inline_js"


class MetricType(Enum):
    """Types of metrics tracked."""
    REVENUE = "revenue"
    TRANSACTIONS = "transactions"
    CUSTOMERS = "customers"
    REFUNDS = "refunds"
    SUBSCRIPTIONS = "subscriptions"
    CONVERSION_RATE = "conversion_rate"
    AVERAGE_ORDER_VALUE = "average_order_value"


@dataclass
class TransactionRecord:
    """Unified transaction record across platforms."""
    transaction_id: str
    platform: Platform
    customer_id: str
    customer_email: str
    amount: int  # In smallest currency unit (kobo, pesewas, cents)
    currency: str
    status: str
    payment_method: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "platform": self.platform.value,
            "customer_id": self.customer_id,
            "customer_email": self.customer_email,
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status,
            "payment_method": self.payment_method,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class CustomerProfile:
    """Unified customer profile across all platforms."""
    customer_id: str
    email: str
    first_seen: datetime
    last_seen: datetime
    total_transactions: int = 0
    total_spent: int = 0
    platforms_used: List[Platform] = field(default_factory=list)
    payment_methods_used: List[str] = field(default_factory=list)
    subscription_status: Optional[str] = None
    lifetime_value: float = 0.0
    risk_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "customer_id": self.customer_id,
            "email": self.email,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "total_transactions": self.total_transactions,
            "total_spent": self.total_spent,
            "platforms_used": [p.value for p in self.platforms_used],
            "payment_methods_used": self.payment_methods_used,
            "subscription_status": self.subscription_status,
            "lifetime_value": self.lifetime_value,
            "risk_score": self.risk_score
        }


@dataclass
class AnalyticsReport:
    """Comprehensive analytics report."""
    report_id: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    metrics: Dict[str, Any] = field(default_factory=dict)
    platform_breakdown: Dict[str, Any] = field(default_factory=dict)
    trends: Dict[str, Any] = field(default_factory=dict)
    insights: List[str] = field(default_factory=list)
    forecasts: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "generated_at": self.generated_at.isoformat(),
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "metrics": self.metrics,
            "platform_breakdown": self.platform_breakdown,
            "trends": self.trends,
            "insights": self.insights,
            "forecasts": self.forecasts
        }


class UnifiedAnalyticsEngine:
    """
    Unified analytics engine for cross-platform insights.
    
    This engine aggregates data from all integrated Paystack platforms
    to provide holistic business intelligence.
    """
    
    def __init__(self):
        self.transactions: List[TransactionRecord] = []
        self.customers: Dict[str, CustomerProfile] = {}
        self.platform_data: Dict[Platform, List[TransactionRecord]] = defaultdict(list)
        self._initialized = False
    
    async def initialize(self):
        """Initialize the analytics engine."""
        logger.info("Initializing Unified Analytics Engine...")
        self._initialized = True
        logger.info("Analytics Engine initialized")
    
    def ingest_transaction(self, transaction: TransactionRecord):
        """Ingest a transaction from any platform."""
        self.transactions.append(transaction)
        self.platform_data[transaction.platform].append(transaction)
        
        # Update customer profile
        self._update_customer_profile(transaction)
        
        logger.debug(f"Ingested transaction {transaction.transaction_id} from {transaction.platform.value}")
    
    def _update_customer_profile(self, transaction: TransactionRecord):
        """Update or create customer profile from transaction."""
        customer_id = transaction.customer_id
        
        if customer_id not in self.customers:
            self.customers[customer_id] = CustomerProfile(
                customer_id=customer_id,
                email=transaction.customer_email,
                first_seen=transaction.timestamp,
                last_seen=transaction.timestamp
            )
        
        profile = self.customers[customer_id]
        profile.last_seen = max(profile.last_seen, transaction.timestamp)
        profile.total_transactions += 1
        
        if transaction.status == "success":
            profile.total_spent += transaction.amount
        
        if transaction.platform not in profile.platforms_used:
            profile.platforms_used.append(transaction.platform)
        
        if transaction.payment_method not in profile.payment_methods_used:
            profile.payment_methods_used.append(transaction.payment_method)
        
        # Calculate lifetime value (simple model)
        profile.lifetime_value = profile.total_spent / 100  # Convert from kobo
    
    async def generate_report(self, 
                             period_start: Optional[datetime] = None,
                             period_end: Optional[datetime] = None,
                             platforms: Optional[List[Platform]] = None) -> AnalyticsReport:
        """Generate a comprehensive analytics report."""
        
        # Default to last 30 days
        if period_end is None:
            period_end = datetime.utcnow()
        if period_start is None:
            period_start = period_end - timedelta(days=30)
        
        # Filter transactions
        filtered_transactions = [
            t for t in self.transactions
            if period_start <= t.timestamp <= period_end
            and (platforms is None or t.platform in platforms)
        ]
        
        # Calculate metrics
        metrics = self._calculate_metrics(filtered_transactions)
        
        # Platform breakdown
        platform_breakdown = self._calculate_platform_breakdown(filtered_transactions)
        
        # Trends
        trends = self._calculate_trends(filtered_transactions, period_start, period_end)
        
        # Generate insights
        insights = self._generate_insights(metrics, platform_breakdown, trends)
        
        # Forecasts
        forecasts = self._generate_forecasts(filtered_transactions)
        
        report = AnalyticsReport(
            report_id=f"report_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            generated_at=datetime.utcnow(),
            period_start=period_start,
            period_end=period_end,
            metrics=metrics,
            platform_breakdown=platform_breakdown,
            trends=trends,
            insights=insights,
            forecasts=forecasts
        )
        
        return report
    
    def _calculate_metrics(self, transactions: List[TransactionRecord]) -> Dict[str, Any]:
        """Calculate key metrics from transactions."""
        successful = [t for t in transactions if t.status == "success"]
        
        total_revenue = sum(t.amount for t in successful)
        total_transactions = len(transactions)
        successful_transactions = len(successful)
        unique_customers = len(set(t.customer_id for t in transactions))
        
        # Calculate by currency
        revenue_by_currency = defaultdict(int)
        for t in successful:
            revenue_by_currency[t.currency] += t.amount
        
        # Payment method breakdown
        payment_methods = defaultdict(int)
        for t in successful:
            payment_methods[t.payment_method] += 1
        
        return {
            "total_revenue": total_revenue,
            "total_revenue_formatted": {
                currency: amount / 100 
                for currency, amount in revenue_by_currency.items()
            },
            "total_transactions": total_transactions,
            "successful_transactions": successful_transactions,
            "failed_transactions": total_transactions - successful_transactions,
            "success_rate": successful_transactions / max(1, total_transactions) * 100,
            "unique_customers": unique_customers,
            "average_order_value": total_revenue / max(1, successful_transactions),
            "payment_methods": dict(payment_methods)
        }
    
    def _calculate_platform_breakdown(self, 
                                     transactions: List[TransactionRecord]) -> Dict[str, Any]:
        """Calculate metrics breakdown by platform."""
        breakdown = {}
        
        for platform in Platform:
            platform_txns = [t for t in transactions if t.platform == platform]
            if not platform_txns:
                continue
            
            successful = [t for t in platform_txns if t.status == "success"]
            
            breakdown[platform.value] = {
                "total_transactions": len(platform_txns),
                "successful_transactions": len(successful),
                "total_revenue": sum(t.amount for t in successful),
                "success_rate": len(successful) / max(1, len(platform_txns)) * 100,
                "unique_customers": len(set(t.customer_id for t in platform_txns)),
                "share_of_revenue": 0  # Calculated below
            }
        
        # Calculate share of revenue
        total_revenue = sum(b["total_revenue"] for b in breakdown.values())
        for platform_data in breakdown.values():
            platform_data["share_of_revenue"] = (
                platform_data["total_revenue"] / max(1, total_revenue) * 100
            )
        
        return breakdown
    
    def _calculate_trends(self, transactions: List[TransactionRecord],
                         period_start: datetime, period_end: datetime) -> Dict[str, Any]:
        """Calculate trends over the period."""
        # Daily aggregation
        daily_data = defaultdict(lambda: {"revenue": 0, "transactions": 0, "customers": set()})
        
        for t in transactions:
            if t.status == "success":
                day = t.timestamp.strftime("%Y-%m-%d")
                daily_data[day]["revenue"] += t.amount
                daily_data[day]["transactions"] += 1
                daily_data[day]["customers"].add(t.customer_id)
        
        # Convert to list
        daily_trend = []
        for day, data in sorted(daily_data.items()):
            daily_trend.append({
                "date": day,
                "revenue": data["revenue"],
                "transactions": data["transactions"],
                "unique_customers": len(data["customers"])
            })
        
        # Calculate growth rates
        if len(daily_trend) >= 2:
            first_half = daily_trend[:len(daily_trend)//2]
            second_half = daily_trend[len(daily_trend)//2:]
            
            first_revenue = sum(d["revenue"] for d in first_half)
            second_revenue = sum(d["revenue"] for d in second_half)
            
            revenue_growth = (second_revenue - first_revenue) / max(1, first_revenue) * 100
        else:
            revenue_growth = 0
        
        return {
            "daily": daily_trend,
            "revenue_growth_rate": revenue_growth,
            "period_days": (period_end - period_start).days
        }
    
    def _generate_insights(self, metrics: Dict, platform_breakdown: Dict,
                          trends: Dict) -> List[str]:
        """Generate actionable insights from the data."""
        insights = []
        
        # Success rate insight
        success_rate = metrics.get("success_rate", 0)
        if success_rate < 90:
            insights.append(
                f"Payment success rate is {success_rate:.1f}%. Consider investigating "
                "failed transactions to improve conversion."
            )
        elif success_rate >= 98:
            insights.append(
                f"Excellent payment success rate of {success_rate:.1f}%! "
                "Your payment infrastructure is performing optimally."
            )
        
        # Platform concentration insight
        if platform_breakdown:
            top_platform = max(platform_breakdown.items(), 
                              key=lambda x: x[1]["share_of_revenue"])
            if top_platform[1]["share_of_revenue"] > 80:
                insights.append(
                    f"{top_platform[0]} accounts for {top_platform[1]['share_of_revenue']:.1f}% "
                    "of revenue. Consider diversifying payment channels."
                )
        
        # Growth insight
        growth_rate = trends.get("revenue_growth_rate", 0)
        if growth_rate > 10:
            insights.append(
                f"Strong revenue growth of {growth_rate:.1f}% in the period. "
                "Business momentum is positive."
            )
        elif growth_rate < -10:
            insights.append(
                f"Revenue declined by {abs(growth_rate):.1f}% in the period. "
                "Review marketing and customer retention strategies."
            )
        
        # Customer insight
        unique_customers = metrics.get("unique_customers", 0)
        total_transactions = metrics.get("total_transactions", 0)
        if unique_customers > 0:
            repeat_rate = (total_transactions - unique_customers) / max(1, total_transactions) * 100
            if repeat_rate > 30:
                insights.append(
                    f"Strong customer loyalty with {repeat_rate:.1f}% repeat transactions. "
                    "Consider implementing a loyalty program."
                )
        
        return insights
    
    def _generate_forecasts(self, transactions: List[TransactionRecord]) -> Dict[str, Any]:
        """Generate revenue forecasts using simple trend analysis."""
        if len(transactions) < 7:
            return {"message": "Insufficient data for forecasting"}
        
        # Simple moving average forecast
        successful = [t for t in transactions if t.status == "success"]
        daily_revenue = defaultdict(int)
        
        for t in successful:
            day = t.timestamp.strftime("%Y-%m-%d")
            daily_revenue[day] += t.amount
        
        if len(daily_revenue) < 7:
            return {"message": "Insufficient daily data for forecasting"}
        
        # Last 7 days average
        recent_days = sorted(daily_revenue.keys())[-7:]
        avg_daily_revenue = sum(daily_revenue[d] for d in recent_days) / 7
        
        # Project next 30 days
        forecasts = {
            "method": "7-day moving average",
            "avg_daily_revenue": avg_daily_revenue,
            "projected_7_day": avg_daily_revenue * 7,
            "projected_30_day": avg_daily_revenue * 30,
            "confidence": "medium",
            "note": "Forecast based on recent transaction patterns"
        }
        
        return forecasts
    
    def get_customer_profile(self, customer_id: str) -> Optional[CustomerProfile]:
        """Get unified customer profile."""
        return self.customers.get(customer_id)
    
    def get_customer_360_view(self, customer_id: str) -> Dict[str, Any]:
        """Get comprehensive 360-degree customer view."""
        profile = self.customers.get(customer_id)
        if not profile:
            return {"error": "Customer not found"}
        
        # Get all customer transactions
        customer_txns = [t for t in self.transactions if t.customer_id == customer_id]
        
        # Transaction history by platform
        platform_history = defaultdict(list)
        for t in customer_txns:
            platform_history[t.platform.value].append(t.to_dict())
        
        # Calculate customer metrics
        successful_txns = [t for t in customer_txns if t.status == "success"]
        
        return {
            "profile": profile.to_dict(),
            "transaction_summary": {
                "total": len(customer_txns),
                "successful": len(successful_txns),
                "total_spent": sum(t.amount for t in successful_txns),
                "average_transaction": sum(t.amount for t in successful_txns) / max(1, len(successful_txns))
            },
            "platform_history": dict(platform_history),
            "recent_transactions": [t.to_dict() for t in sorted(
                customer_txns, key=lambda x: x.timestamp, reverse=True
            )[:10]],
            "engagement_score": self._calculate_engagement_score(profile, customer_txns)
        }
    
    def _calculate_engagement_score(self, profile: CustomerProfile,
                                   transactions: List[TransactionRecord]) -> float:
        """Calculate customer engagement score (0-100)."""
        score = 0
        
        # Platform diversity (up to 20 points)
        score += min(20, len(profile.platforms_used) * 5)
        
        # Transaction frequency (up to 30 points)
        if profile.total_transactions >= 10:
            score += 30
        elif profile.total_transactions >= 5:
            score += 20
        elif profile.total_transactions >= 2:
            score += 10
        
        # Recency (up to 30 points)
        days_since_last = (datetime.utcnow() - profile.last_seen).days
        if days_since_last <= 7:
            score += 30
        elif days_since_last <= 30:
            score += 20
        elif days_since_last <= 90:
            score += 10
        
        # Lifetime value (up to 20 points)
        if profile.lifetime_value >= 100000:
            score += 20
        elif profile.lifetime_value >= 50000:
            score += 15
        elif profile.lifetime_value >= 10000:
            score += 10
        elif profile.lifetime_value >= 1000:
            score += 5
        
        return min(100, score)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get analytics engine statistics."""
        return {
            "total_transactions": len(self.transactions),
            "total_customers": len(self.customers),
            "platforms_active": len([p for p in Platform if self.platform_data[p]]),
            "data_range": {
                "earliest": min((t.timestamp for t in self.transactions), default=None),
                "latest": max((t.timestamp for t in self.transactions), default=None)
            } if self.transactions else None
        }


# Factory function
def create_analytics_engine() -> UnifiedAnalyticsEngine:
    """Create a new analytics engine instance."""
    return UnifiedAnalyticsEngine()


if __name__ == "__main__":
    import random
    
    async def demo():
        engine = create_analytics_engine()
        await engine.initialize()
        
        # Generate sample data
        platforms = list(Platform)
        payment_methods = ["card", "bank_transfer", "ussd", "mobile_money"]
        currencies = ["NGN", "GHS", "ZAR"]
        
        print("Generating sample transaction data...")
        
        for i in range(100):
            transaction = TransactionRecord(
                transaction_id=f"txn_{i:04d}",
                platform=random.choice(platforms),
                customer_id=f"cust_{random.randint(1, 20):03d}",
                customer_email=f"customer{random.randint(1, 20)}@example.com",
                amount=random.randint(1000, 100000),
                currency=random.choice(currencies),
                status=random.choices(["success", "failed"], weights=[95, 5])[0],
                payment_method=random.choice(payment_methods),
                timestamp=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            engine.ingest_transaction(transaction)
        
        print(f"\nIngested {len(engine.transactions)} transactions")
        print(f"Unique customers: {len(engine.customers)}")
        
        # Generate report
        print("\n" + "=" * 60)
        print("UNIFIED ANALYTICS REPORT")
        print("=" * 60)
        
        report = await engine.generate_report()
        
        print(f"\nReport ID: {report.report_id}")
        print(f"Period: {report.period_start.date()} to {report.period_end.date()}")
        
        print("\n--- Key Metrics ---")
        metrics = report.metrics
        print(f"Total Revenue: {metrics['total_revenue']:,} (smallest unit)")
        print(f"Total Transactions: {metrics['total_transactions']}")
        print(f"Success Rate: {metrics['success_rate']:.1f}%")
        print(f"Unique Customers: {metrics['unique_customers']}")
        print(f"Average Order Value: {metrics['average_order_value']:,.0f}")
        
        print("\n--- Platform Breakdown ---")
        for platform, data in report.platform_breakdown.items():
            print(f"  {platform}: {data['share_of_revenue']:.1f}% of revenue")
        
        print("\n--- Insights ---")
        for insight in report.insights:
            print(f"  • {insight}")
        
        print("\n--- Forecasts ---")
        forecasts = report.forecasts
        if "projected_30_day" in forecasts:
            print(f"  Projected 30-day revenue: {forecasts['projected_30_day']:,.0f}")
        
        # Customer 360 view
        print("\n" + "=" * 60)
        print("CUSTOMER 360 VIEW (Sample)")
        print("=" * 60)
        
        sample_customer = list(engine.customers.keys())[0]
        view = engine.get_customer_360_view(sample_customer)
        
        print(f"\nCustomer: {view['profile']['email']}")
        print(f"Total Spent: {view['transaction_summary']['total_spent']:,}")
        print(f"Platforms Used: {', '.join(view['profile']['platforms_used'])}")
        print(f"Engagement Score: {view['engagement_score']:.0f}/100")
    
    asyncio.run(demo())
