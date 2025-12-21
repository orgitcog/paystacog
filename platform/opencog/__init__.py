"""
PaystaCog OpenCog Integration Layer

This module provides the OpenCog-inspired cognitive architecture for the
unified Paystack financial services platform. It implements:

- Atomspace: Unified knowledge representation for all payment features
- PLN (Probabilistic Logic Networks): Reasoning about payment flows
- MOSES: Learning optimal payment processing strategies
- OpenPsi: Goal-directed behavior for autonomous operations
"""

from .atomspace import PaystackAtomspace
from .action_selector import CognitiveActionSelector
from .executor import CognitiveExecutor
from .reporter import CognitiveReporter
from .pln import PaymentLogicNetwork
from .openpsi import PaymentGoalManager

__version__ = "1.0.0"
__all__ = [
    "PaystackAtomspace",
    "CognitiveActionSelector", 
    "CognitiveExecutor",
    "CognitiveReporter",
    "PaymentLogicNetwork",
    "PaymentGoalManager"
]
