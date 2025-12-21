#!/usr/bin/env python3
"""
Intelligent Payment and Refund Workflows

This module provides AI-enhanced workflow templates for payment processing,
refunds, and other financial operations with built-in fraud detection,
compliance checking, and intelligent routing.

Integration Opportunity #3: Intelligent, Autonomous Payment and Refund Workflows
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from abc import ABC, abstractmethod
import asyncio
import json
import logging
import hashlib
import random

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REQUIRES_REVIEW = "requires_review"


class StepStatus(Enum):
    """Individual step status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class RiskLevel(Enum):
    """Transaction risk levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class WorkflowStep:
    """A single step in a workflow."""
    step_id: str
    name: str
    status: StepStatus = StepStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "name": self.name,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error
        }


@dataclass
class WorkflowExecution:
    """Represents a workflow execution instance."""
    execution_id: str
    workflow_name: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    steps: List[WorkflowStep] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "workflow_name": self.workflow_name,
            "status": self.status.value,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "steps": [s.to_dict() for s in self.steps],
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata
        }


@dataclass
class FraudCheckResult:
    """Result of fraud detection analysis."""
    risk_level: RiskLevel
    risk_score: float  # 0.0 to 1.0
    risk_factors: List[str]
    recommendation: str
    requires_manual_review: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "risk_level": self.risk_level.value,
            "risk_score": self.risk_score,
            "risk_factors": self.risk_factors,
            "recommendation": self.recommendation,
            "requires_manual_review": self.requires_manual_review
        }


class FraudDetectionEngine:
    """AI-powered fraud detection engine."""
    
    def __init__(self):
        self.known_patterns: List[Dict] = []
        self.velocity_tracker: Dict[str, List[datetime]] = {}
    
    async def analyze_transaction(self, transaction_data: Dict[str, Any]) -> FraudCheckResult:
        """Analyze a transaction for fraud risk."""
        risk_factors = []
        risk_score = 0.0
        
        email = transaction_data.get("email", "")
        amount = transaction_data.get("amount", 0)
        ip_address = transaction_data.get("ip_address", "")
        card_bin = transaction_data.get("card_bin", "")
        
        # Check 1: Amount anomaly
        if amount > 1000000:  # Over 10,000 in major unit
            risk_score += 0.2
            risk_factors.append("High transaction amount")
        
        # Check 2: Velocity check
        if email in self.velocity_tracker:
            recent_txns = [
                t for t in self.velocity_tracker[email]
                if t > datetime.utcnow() - timedelta(hours=1)
            ]
            if len(recent_txns) > 5:
                risk_score += 0.3
                risk_factors.append("High transaction velocity")
        
        # Check 3: New customer with high amount
        if transaction_data.get("is_new_customer", False) and amount > 500000:
            risk_score += 0.15
            risk_factors.append("New customer with high amount")
        
        # Check 4: Suspicious email patterns
        if email and (email.endswith(".temp") or "test" in email.lower()):
            risk_score += 0.1
            risk_factors.append("Suspicious email pattern")
        
        # Check 5: Card BIN analysis (simulated)
        if card_bin and card_bin.startswith("4"):  # Visa
            # Simulated BIN check
            pass
        
        # Track velocity
        if email not in self.velocity_tracker:
            self.velocity_tracker[email] = []
        self.velocity_tracker[email].append(datetime.utcnow())
        
        # Determine risk level
        if risk_score >= 0.7:
            risk_level = RiskLevel.CRITICAL
            recommendation = "Block transaction"
            requires_review = True
        elif risk_score >= 0.5:
            risk_level = RiskLevel.HIGH
            recommendation = "Manual review required"
            requires_review = True
        elif risk_score >= 0.3:
            risk_level = RiskLevel.MEDIUM
            recommendation = "Proceed with caution"
            requires_review = False
        else:
            risk_level = RiskLevel.LOW
            recommendation = "Proceed with transaction"
            requires_review = False
        
        return FraudCheckResult(
            risk_level=risk_level,
            risk_score=risk_score,
            risk_factors=risk_factors,
            recommendation=recommendation,
            requires_manual_review=requires_review
        )


class ComplianceEngine:
    """Compliance checking engine."""
    
    def __init__(self):
        self.rules: List[Dict] = []
        self._initialize_rules()
    
    def _initialize_rules(self):
        """Initialize compliance rules."""
        self.rules = [
            {
                "id": "pci_dss_1",
                "name": "PCI-DSS Card Data",
                "check": lambda d: "full_card_number" not in d,
                "message": "Full card numbers must not be stored"
            },
            {
                "id": "aml_1",
                "name": "AML Threshold",
                "check": lambda d: d.get("amount", 0) < 10000000,  # 100,000 threshold
                "message": "Transaction exceeds AML reporting threshold"
            },
            {
                "id": "kyc_1",
                "name": "KYC Verification",
                "check": lambda d: d.get("customer_verified", True) or d.get("amount", 0) < 500000,
                "message": "Customer KYC required for high-value transactions"
            }
        ]
    
    async def check_compliance(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check transaction compliance."""
        violations = []
        warnings = []
        
        for rule in self.rules:
            try:
                if not rule["check"](transaction_data):
                    violations.append({
                        "rule_id": rule["id"],
                        "rule_name": rule["name"],
                        "message": rule["message"]
                    })
            except Exception as e:
                warnings.append(f"Error checking rule {rule['id']}: {str(e)}")
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "checked_at": datetime.utcnow().isoformat()
        }


class IntelligentWorkflowEngine:
    """
    Intelligent workflow engine for payment operations.
    
    Provides AI-enhanced workflows with built-in fraud detection,
    compliance checking, and intelligent routing.
    """
    
    def __init__(self):
        self.fraud_engine = FraudDetectionEngine()
        self.compliance_engine = ComplianceEngine()
        self.executions: Dict[str, WorkflowExecution] = {}
        self.workflow_handlers: Dict[str, Callable] = {}
        self._register_default_workflows()
    
    def _register_default_workflows(self):
        """Register default workflow handlers."""
        self.workflow_handlers["payment_processing"] = self._execute_payment_workflow
        self.workflow_handlers["refund_processing"] = self._execute_refund_workflow
        self.workflow_handlers["subscription_creation"] = self._execute_subscription_workflow
        self.workflow_handlers["transfer_processing"] = self._execute_transfer_workflow
    
    def _generate_execution_id(self) -> str:
        """Generate a unique execution ID."""
        return f"exec_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{hashlib.md5(str(random.random()).encode()).hexdigest()[:8]}"
    
    async def execute_workflow(self, workflow_name: str, 
                              input_data: Dict[str, Any]) -> WorkflowExecution:
        """Execute a workflow."""
        if workflow_name not in self.workflow_handlers:
            raise ValueError(f"Unknown workflow: {workflow_name}")
        
        # Create execution
        execution = WorkflowExecution(
            execution_id=self._generate_execution_id(),
            workflow_name=workflow_name,
            input_data=input_data,
            started_at=datetime.utcnow()
        )
        
        self.executions[execution.execution_id] = execution
        
        # Execute workflow
        try:
            execution.status = WorkflowStatus.RUNNING
            handler = self.workflow_handlers[workflow_name]
            await handler(execution)
            
            if execution.status == WorkflowStatus.RUNNING:
                execution.status = WorkflowStatus.COMPLETED
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.output_data["error"] = str(e)
            logger.error(f"Workflow {workflow_name} failed: {e}")
        
        execution.completed_at = datetime.utcnow()
        return execution
    
    async def _execute_step(self, execution: WorkflowExecution, 
                           step_id: str, step_name: str,
                           handler: Callable) -> Dict[str, Any]:
        """Execute a single workflow step."""
        step = WorkflowStep(step_id=step_id, name=step_name)
        execution.steps.append(step)
        
        step.status = StepStatus.RUNNING
        step.started_at = datetime.utcnow()
        
        try:
            result = await handler()
            step.result = result
            step.status = StepStatus.COMPLETED
        except Exception as e:
            step.error = str(e)
            step.status = StepStatus.FAILED
            raise
        finally:
            step.completed_at = datetime.utcnow()
        
        return result
    
    async def _execute_payment_workflow(self, execution: WorkflowExecution):
        """Execute the payment processing workflow."""
        input_data = execution.input_data
        
        # Step 1: Validate Input
        async def validate_input():
            required_fields = ["email", "amount"]
            missing = [f for f in required_fields if f not in input_data]
            if missing:
                raise ValueError(f"Missing required fields: {missing}")
            return {"valid": True, "fields_validated": required_fields}
        
        await self._execute_step(execution, "step_1", "Validate Input", validate_input)
        
        # Step 2: Fraud Detection
        async def check_fraud():
            result = await self.fraud_engine.analyze_transaction(input_data)
            if result.risk_level == RiskLevel.CRITICAL:
                execution.status = WorkflowStatus.FAILED
                raise ValueError(f"Transaction blocked: {result.recommendation}")
            return result.to_dict()
        
        fraud_result = await self._execute_step(execution, "step_2", "Fraud Detection", check_fraud)
        
        # Step 3: Compliance Check
        async def check_compliance():
            result = await self.compliance_engine.check_compliance(input_data)
            if not result["compliant"]:
                execution.status = WorkflowStatus.REQUIRES_REVIEW
                return result
            return result
        
        compliance_result = await self._execute_step(execution, "step_3", "Compliance Check", check_compliance)
        
        # Check if manual review required
        if fraud_result.get("requires_manual_review") or not compliance_result.get("compliant"):
            execution.status = WorkflowStatus.REQUIRES_REVIEW
            execution.output_data = {
                "status": "requires_review",
                "fraud_check": fraud_result,
                "compliance_check": compliance_result
            }
            return
        
        # Step 4: Initialize Transaction
        async def initialize_transaction():
            # Simulated transaction initialization
            reference = f"txn_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"
            return {
                "reference": reference,
                "authorization_url": f"https://checkout.paystack.com/{reference}",
                "access_code": hashlib.md5(reference.encode()).hexdigest()[:20]
            }
        
        init_result = await self._execute_step(execution, "step_4", "Initialize Transaction", initialize_transaction)
        
        # Step 5: Process Payment (simulated)
        async def process_payment():
            # Simulated payment processing
            await asyncio.sleep(0.1)  # Simulate processing time
            return {
                "status": "success",
                "reference": init_result["reference"],
                "amount": input_data["amount"],
                "currency": input_data.get("currency", "NGN"),
                "paid_at": datetime.utcnow().isoformat()
            }
        
        payment_result = await self._execute_step(execution, "step_5", "Process Payment", process_payment)
        
        # Step 6: Verify and Finalize
        async def verify_and_finalize():
            return {
                "verified": True,
                "transaction_id": f"T{random.randint(100000, 999999)}",
                "receipt_number": f"RCP{datetime.utcnow().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
            }
        
        final_result = await self._execute_step(execution, "step_6", "Verify and Finalize", verify_and_finalize)
        
        # Set output
        execution.output_data = {
            "status": "success",
            "transaction": {
                **payment_result,
                **final_result
            },
            "fraud_check": fraud_result,
            "compliance_check": compliance_result
        }
    
    async def _execute_refund_workflow(self, execution: WorkflowExecution):
        """Execute the refund processing workflow."""
        input_data = execution.input_data
        
        # Step 1: Verify Original Transaction
        async def verify_original():
            transaction_ref = input_data.get("transaction_reference")
            if not transaction_ref:
                raise ValueError("Transaction reference required")
            # Simulated verification
            return {
                "original_found": True,
                "original_amount": input_data.get("original_amount", 10000),
                "original_date": (datetime.utcnow() - timedelta(days=5)).isoformat(),
                "refundable": True
            }
        
        original = await self._execute_step(execution, "step_1", "Verify Original Transaction", verify_original)
        
        # Step 2: Check Refund Eligibility
        async def check_eligibility():
            refund_amount = input_data.get("amount", original["original_amount"])
            if refund_amount > original["original_amount"]:
                raise ValueError("Refund amount exceeds original transaction")
            
            # Check refund window (30 days)
            original_date = datetime.fromisoformat(original["original_date"])
            if (datetime.utcnow() - original_date).days > 30:
                return {
                    "eligible": False,
                    "reason": "Refund window expired (30 days)"
                }
            
            return {
                "eligible": True,
                "refund_amount": refund_amount,
                "refund_type": "full" if refund_amount == original["original_amount"] else "partial"
            }
        
        eligibility = await self._execute_step(execution, "step_2", "Check Refund Eligibility", check_eligibility)
        
        if not eligibility.get("eligible"):
            execution.status = WorkflowStatus.FAILED
            execution.output_data = {
                "status": "failed",
                "reason": eligibility.get("reason")
            }
            return
        
        # Step 3: Compliance Check
        async def compliance_check():
            return await self.compliance_engine.check_compliance({
                **input_data,
                "transaction_type": "refund"
            })
        
        await self._execute_step(execution, "step_3", "Compliance Check", compliance_check)
        
        # Step 4: Process Refund
        async def process_refund():
            await asyncio.sleep(0.1)
            return {
                "refund_reference": f"ref_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "amount": eligibility["refund_amount"],
                "status": "processed",
                "processed_at": datetime.utcnow().isoformat()
            }
        
        refund_result = await self._execute_step(execution, "step_4", "Process Refund", process_refund)
        
        # Step 5: Update Records and Notify
        async def update_and_notify():
            return {
                "records_updated": True,
                "customer_notified": True,
                "notification_channel": "email"
            }
        
        await self._execute_step(execution, "step_5", "Update Records and Notify", update_and_notify)
        
        execution.output_data = {
            "status": "success",
            "refund": refund_result,
            "original_transaction": original
        }
    
    async def _execute_subscription_workflow(self, execution: WorkflowExecution):
        """Execute subscription creation workflow."""
        input_data = execution.input_data
        
        # Step 1: Validate Plan
        async def validate_plan():
            plan_code = input_data.get("plan_code")
            if not plan_code:
                raise ValueError("Plan code required")
            return {
                "plan_valid": True,
                "plan_code": plan_code,
                "plan_amount": input_data.get("amount", 5000),
                "interval": input_data.get("interval", "monthly")
            }
        
        plan = await self._execute_step(execution, "step_1", "Validate Plan", validate_plan)
        
        # Step 2: Verify Customer
        async def verify_customer():
            return {
                "customer_verified": True,
                "customer_code": input_data.get("customer_code", f"CUS_{random.randint(10000, 99999)}"),
                "has_authorization": True
            }
        
        customer = await self._execute_step(execution, "step_2", "Verify Customer", verify_customer)
        
        # Step 3: Create Subscription
        async def create_subscription():
            return {
                "subscription_code": f"SUB_{random.randint(100000, 999999)}",
                "status": "active",
                "next_payment_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "created_at": datetime.utcnow().isoformat()
            }
        
        subscription = await self._execute_step(execution, "step_3", "Create Subscription", create_subscription)
        
        execution.output_data = {
            "status": "success",
            "subscription": subscription,
            "plan": plan,
            "customer": customer
        }
    
    async def _execute_transfer_workflow(self, execution: WorkflowExecution):
        """Execute transfer processing workflow."""
        input_data = execution.input_data
        
        # Step 1: Validate Recipient
        async def validate_recipient():
            recipient_code = input_data.get("recipient_code")
            if not recipient_code:
                raise ValueError("Recipient code required")
            return {
                "recipient_valid": True,
                "recipient_code": recipient_code,
                "account_name": input_data.get("account_name", "John Doe")
            }
        
        recipient = await self._execute_step(execution, "step_1", "Validate Recipient", validate_recipient)
        
        # Step 2: Check Balance
        async def check_balance():
            amount = input_data.get("amount", 0)
            # Simulated balance check
            return {
                "sufficient_balance": True,
                "available_balance": 1000000,
                "transfer_amount": amount
            }
        
        balance = await self._execute_step(execution, "step_2", "Check Balance", check_balance)
        
        # Step 3: Fraud Check
        async def fraud_check():
            result = await self.fraud_engine.analyze_transaction({
                **input_data,
                "transaction_type": "transfer"
            })
            return result.to_dict()
        
        await self._execute_step(execution, "step_3", "Fraud Check", fraud_check)
        
        # Step 4: Initiate Transfer
        async def initiate_transfer():
            return {
                "transfer_code": f"TRF_{random.randint(100000, 999999)}",
                "reference": f"ref_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "status": "pending",
                "initiated_at": datetime.utcnow().isoformat()
            }
        
        transfer = await self._execute_step(execution, "step_4", "Initiate Transfer", initiate_transfer)
        
        # Step 5: Verify Transfer
        async def verify_transfer():
            await asyncio.sleep(0.1)
            return {
                "status": "success",
                "completed_at": datetime.utcnow().isoformat()
            }
        
        verification = await self._execute_step(execution, "step_5", "Verify Transfer", verify_transfer)
        
        execution.output_data = {
            "status": "success",
            "transfer": {**transfer, **verification},
            "recipient": recipient,
            "balance_after": balance["available_balance"] - balance["transfer_amount"]
        }
    
    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get a workflow execution by ID."""
        return self.executions.get(execution_id)
    
    def list_executions(self, 
                       workflow_name: Optional[str] = None,
                       status: Optional[WorkflowStatus] = None,
                       limit: int = 100) -> List[WorkflowExecution]:
        """List workflow executions with optional filtering."""
        executions = list(self.executions.values())
        
        if workflow_name:
            executions = [e for e in executions if e.workflow_name == workflow_name]
        
        if status:
            executions = [e for e in executions if e.status == status]
        
        return sorted(executions, key=lambda e: e.started_at or datetime.min, reverse=True)[:limit]
    
    def get_available_workflows(self) -> List[Dict[str, Any]]:
        """Get list of available workflows."""
        workflows = [
            {
                "name": "payment_processing",
                "description": "Complete payment flow with fraud detection and compliance checking",
                "steps": ["Validate Input", "Fraud Detection", "Compliance Check", 
                         "Initialize Transaction", "Process Payment", "Verify and Finalize"]
            },
            {
                "name": "refund_processing",
                "description": "Refund processing with eligibility verification",
                "steps": ["Verify Original Transaction", "Check Refund Eligibility",
                         "Compliance Check", "Process Refund", "Update Records and Notify"]
            },
            {
                "name": "subscription_creation",
                "description": "Create and activate subscriptions",
                "steps": ["Validate Plan", "Verify Customer", "Create Subscription"]
            },
            {
                "name": "transfer_processing",
                "description": "Process transfers with fraud detection",
                "steps": ["Validate Recipient", "Check Balance", "Fraud Check",
                         "Initiate Transfer", "Verify Transfer"]
            }
        ]
        return workflows
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get workflow engine statistics."""
        executions = list(self.executions.values())
        
        return {
            "total_executions": len(executions),
            "by_status": {
                status.value: sum(1 for e in executions if e.status == status)
                for status in WorkflowStatus
            },
            "by_workflow": {
                name: sum(1 for e in executions if e.workflow_name == name)
                for name in self.workflow_handlers.keys()
            },
            "success_rate": sum(1 for e in executions if e.status == WorkflowStatus.COMPLETED) / max(1, len(executions)) * 100
        }


# Factory function
def create_workflow_engine() -> IntelligentWorkflowEngine:
    """Create a new workflow engine instance."""
    return IntelligentWorkflowEngine()


if __name__ == "__main__":
    async def demo():
        engine = create_workflow_engine()
        
        print("=" * 60)
        print("INTELLIGENT WORKFLOW ENGINE DEMO")
        print("=" * 60)
        
        # List available workflows
        print("\n--- Available Workflows ---")
        for wf in engine.get_available_workflows():
            print(f"\n{wf['name']}:")
            print(f"  {wf['description']}")
            print(f"  Steps: {' → '.join(wf['steps'])}")
        
        # Execute payment workflow
        print("\n" + "=" * 60)
        print("EXECUTING PAYMENT WORKFLOW")
        print("=" * 60)
        
        payment_result = await engine.execute_workflow("payment_processing", {
            "email": "customer@example.com",
            "amount": 50000,
            "currency": "NGN",
            "customer_verified": True
        })
        
        print(f"\nExecution ID: {payment_result.execution_id}")
        print(f"Status: {payment_result.status.value}")
        print("\nSteps:")
        for step in payment_result.steps:
            status_icon = "✓" if step.status == StepStatus.COMPLETED else "✗"
            print(f"  {status_icon} {step.name}: {step.status.value}")
        
        if payment_result.output_data.get("transaction"):
            print(f"\nTransaction Reference: {payment_result.output_data['transaction'].get('reference')}")
        
        # Execute refund workflow
        print("\n" + "=" * 60)
        print("EXECUTING REFUND WORKFLOW")
        print("=" * 60)
        
        refund_result = await engine.execute_workflow("refund_processing", {
            "transaction_reference": "txn_20231215_1234",
            "amount": 25000,
            "original_amount": 50000,
            "reason": "Customer request"
        })
        
        print(f"\nExecution ID: {refund_result.execution_id}")
        print(f"Status: {refund_result.status.value}")
        print("\nSteps:")
        for step in refund_result.steps:
            status_icon = "✓" if step.status == StepStatus.COMPLETED else "✗"
            print(f"  {status_icon} {step.name}: {step.status.value}")
        
        # Test fraud detection
        print("\n" + "=" * 60)
        print("TESTING FRAUD DETECTION (High-Risk Transaction)")
        print("=" * 60)
        
        high_risk_result = await engine.execute_workflow("payment_processing", {
            "email": "suspicious@test.temp",
            "amount": 5000000,  # Very high amount
            "is_new_customer": True
        })
        
        print(f"\nExecution ID: {high_risk_result.execution_id}")
        print(f"Status: {high_risk_result.status.value}")
        if high_risk_result.output_data.get("fraud_check"):
            fraud = high_risk_result.output_data["fraud_check"]
            print(f"Risk Level: {fraud.get('risk_level')}")
            print(f"Risk Score: {fraud.get('risk_score'):.2f}")
            print(f"Risk Factors: {', '.join(fraud.get('risk_factors', []))}")
        
        # Statistics
        print("\n" + "=" * 60)
        print("WORKFLOW STATISTICS")
        print("=" * 60)
        stats = engine.get_statistics()
        print(f"\nTotal Executions: {stats['total_executions']}")
        print(f"Success Rate: {stats['success_rate']:.1f}%")
        print("By Status:")
        for status, count in stats['by_status'].items():
            if count > 0:
                print(f"  {status}: {count}")
        
        print("\n" + "=" * 60)
        print("Demo Complete")
        print("=" * 60)
    
    asyncio.run(demo())
