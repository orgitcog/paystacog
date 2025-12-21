#!/usr/bin/env python3
"""
PaystaCog Atomspace - Unified Knowledge Representation

Implements an OpenCog-inspired Atomspace for representing and reasoning
about Paystack payment features, integrations, and workflows.
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
import hashlib


class AtomType(Enum):
    """Types of atoms in the PaystaCog Atomspace."""
    # Nodes
    CONCEPT = "ConceptNode"
    PREDICATE = "PredicateNode"
    SCHEMA = "SchemaNode"
    VARIABLE = "VariableNode"
    NUMBER = "NumberNode"
    
    # Payment-specific nodes
    PAYMENT_METHOD = "PaymentMethodNode"
    CURRENCY = "CurrencyNode"
    TRANSACTION = "TransactionNode"
    MERCHANT = "MerchantNode"
    CUSTOMER = "CustomerNode"
    
    # Integration nodes
    SDK = "SDKNode"
    PLUGIN = "PluginNode"
    API_ENDPOINT = "APIEndpointNode"
    WEBHOOK = "WebhookNode"
    
    # Links
    INHERITANCE = "InheritanceLink"
    EVALUATION = "EvaluationLink"
    EXECUTION = "ExecutionLink"
    LIST = "ListLink"
    AND = "AndLink"
    OR = "OrLink"
    IMPLICATION = "ImplicationLink"
    EQUIVALENCE = "EquivalenceLink"


@dataclass
class TruthValue:
    """OpenCog-style truth value with strength and confidence."""
    strength: float = 1.0
    confidence: float = 1.0
    
    def __post_init__(self):
        self.strength = max(0.0, min(1.0, self.strength))
        self.confidence = max(0.0, min(1.0, self.confidence))
    
    def merge(self, other: 'TruthValue') -> 'TruthValue':
        """Merge two truth values using revision formula."""
        total_conf = self.confidence + other.confidence
        if total_conf == 0:
            return TruthValue(0.5, 0.0)
        new_strength = (self.strength * self.confidence + 
                       other.strength * other.confidence) / total_conf
        new_conf = min(0.99, total_conf / (1 + total_conf))
        return TruthValue(new_strength, new_conf)


@dataclass
class AttentionValue:
    """OpenCog-style attention value for importance-based processing."""
    sti: float = 0.0  # Short-term importance
    lti: float = 0.0  # Long-term importance
    vlti: bool = False  # Very long-term importance flag


@dataclass
class Atom:
    """Base atom class for the Atomspace."""
    atom_type: AtomType
    name: Optional[str] = None
    outgoing: List['Atom'] = field(default_factory=list)
    truth_value: TruthValue = field(default_factory=TruthValue)
    attention_value: AttentionValue = field(default_factory=AttentionValue)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        self._hash = None
    
    @property
    def handle(self) -> str:
        """Generate unique handle for this atom."""
        if self._hash is None:
            content = f"{self.atom_type.value}:{self.name}:{len(self.outgoing)}"
            self._hash = hashlib.md5(content.encode()).hexdigest()[:16]
        return self._hash
    
    def is_node(self) -> bool:
        """Check if this atom is a node (no outgoing set)."""
        return len(self.outgoing) == 0
    
    def is_link(self) -> bool:
        """Check if this atom is a link (has outgoing set)."""
        return len(self.outgoing) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert atom to dictionary representation."""
        return {
            'handle': self.handle,
            'type': self.atom_type.value,
            'name': self.name,
            'outgoing': [a.handle for a in self.outgoing],
            'truth_value': {
                'strength': self.truth_value.strength,
                'confidence': self.truth_value.confidence
            },
            'attention_value': {
                'sti': self.attention_value.sti,
                'lti': self.attention_value.lti,
                'vlti': self.attention_value.vlti
            },
            'metadata': self.metadata
        }


class PaystackAtomspace:
    """
    OpenCog-inspired Atomspace for Paystack knowledge representation.
    
    This Atomspace stores and manages knowledge about:
    - Payment methods and flows
    - SDK and plugin capabilities
    - API endpoints and webhooks
    - Transaction patterns and analytics
    - Integration relationships
    """
    
    def __init__(self):
        self.atoms: Dict[str, Atom] = {}
        self.type_index: Dict[AtomType, Set[str]] = {t: set() for t in AtomType}
        self.name_index: Dict[str, Set[str]] = {}
        self._initialize_core_concepts()
    
    def _initialize_core_concepts(self):
        """Initialize core payment concepts in the Atomspace."""
        # Payment method hierarchy
        payment_root = self.add_node(AtomType.CONCEPT, "PaymentMethod")
        
        methods = ["Card", "BankTransfer", "USSD", "MobileMoney", "QR", "ApplePay"]
        for method in methods:
            method_node = self.add_node(AtomType.PAYMENT_METHOD, method)
            self.add_link(AtomType.INHERITANCE, [method_node, payment_root])
        
        # Currency concepts
        currency_root = self.add_node(AtomType.CONCEPT, "Currency")
        currencies = ["NGN", "GHS", "ZAR", "KES", "USD"]
        for curr in currencies:
            curr_node = self.add_node(AtomType.CURRENCY, curr)
            self.add_link(AtomType.INHERITANCE, [curr_node, currency_root])
        
        # SDK hierarchy
        sdk_root = self.add_node(AtomType.CONCEPT, "SDK")
        sdk_platforms = {
            "Mobile": ["Android", "iOS", "Flutter", "ReactNative"],
            "Backend": ["Python", "Node", "PHP"],
            "Frontend": ["JavaScript", "Vue", "React"]
        }
        
        for platform, sdks in sdk_platforms.items():
            platform_node = self.add_node(AtomType.CONCEPT, f"{platform}SDK")
            self.add_link(AtomType.INHERITANCE, [platform_node, sdk_root])
            for sdk in sdks:
                sdk_node = self.add_node(AtomType.SDK, f"paystack-{sdk.lower()}")
                self.add_link(AtomType.INHERITANCE, [sdk_node, platform_node])
        
        # Plugin hierarchy
        plugin_root = self.add_node(AtomType.CONCEPT, "Plugin")
        plugin_categories = {
            "Ecommerce": ["WooCommerce", "Magento", "PrestaShop", "OpenCart"],
            "CMS": ["WordPress", "Joomla"],
            "LMS": ["Moodle", "LearnPress"],
            "Membership": ["MemberPress", "PaidMembershipPro"]
        }
        
        for category, plugins in plugin_categories.items():
            cat_node = self.add_node(AtomType.CONCEPT, f"{category}Plugin")
            self.add_link(AtomType.INHERITANCE, [cat_node, plugin_root])
            for plugin in plugins:
                plugin_node = self.add_node(AtomType.PLUGIN, f"plugin-{plugin.lower()}")
                self.add_link(AtomType.INHERITANCE, [plugin_node, cat_node])
        
        # Core API endpoints
        api_root = self.add_node(AtomType.CONCEPT, "APIEndpoint")
        endpoints = [
            "transaction/initialize",
            "transaction/verify",
            "transaction/charge_authorization",
            "customer/create",
            "customer/list",
            "plan/create",
            "subscription/create",
            "transfer/initiate",
            "refund/create"
        ]
        
        for endpoint in endpoints:
            ep_node = self.add_node(AtomType.API_ENDPOINT, endpoint)
            self.add_link(AtomType.INHERITANCE, [ep_node, api_root])
    
    def add_node(self, atom_type: AtomType, name: str, 
                 truth_value: Optional[TruthValue] = None,
                 metadata: Optional[Dict] = None) -> Atom:
        """Add a node to the Atomspace."""
        atom = Atom(
            atom_type=atom_type,
            name=name,
            truth_value=truth_value or TruthValue(),
            metadata=metadata or {}
        )
        
        self.atoms[atom.handle] = atom
        self.type_index[atom_type].add(atom.handle)
        
        if name not in self.name_index:
            self.name_index[name] = set()
        self.name_index[name].add(atom.handle)
        
        return atom
    
    def add_link(self, atom_type: AtomType, outgoing: List[Atom],
                 truth_value: Optional[TruthValue] = None,
                 metadata: Optional[Dict] = None) -> Atom:
        """Add a link to the Atomspace."""
        atom = Atom(
            atom_type=atom_type,
            outgoing=outgoing,
            truth_value=truth_value or TruthValue(),
            metadata=metadata or {}
        )
        
        self.atoms[atom.handle] = atom
        self.type_index[atom_type].add(atom.handle)
        
        return atom
    
    def get_atom(self, handle: str) -> Optional[Atom]:
        """Retrieve an atom by its handle."""
        return self.atoms.get(handle)
    
    def get_atoms_by_type(self, atom_type: AtomType) -> List[Atom]:
        """Get all atoms of a specific type."""
        return [self.atoms[h] for h in self.type_index.get(atom_type, set())]
    
    def get_atoms_by_name(self, name: str) -> List[Atom]:
        """Get all atoms with a specific name."""
        return [self.atoms[h] for h in self.name_index.get(name, set())]
    
    def get_incoming(self, atom: Atom) -> List[Atom]:
        """Get all links that have this atom in their outgoing set."""
        incoming = []
        for a in self.atoms.values():
            if a.is_link() and atom in a.outgoing:
                incoming.append(a)
        return incoming
    
    def pattern_match(self, pattern_type: AtomType, 
                     constraints: Optional[Dict] = None) -> List[Atom]:
        """Simple pattern matching on the Atomspace."""
        results = []
        candidates = self.get_atoms_by_type(pattern_type)
        
        if constraints is None:
            return candidates
        
        for atom in candidates:
            match = True
            for key, value in constraints.items():
                if key == 'name' and atom.name != value:
                    match = False
                    break
                if key == 'min_strength' and atom.truth_value.strength < value:
                    match = False
                    break
                if key == 'min_confidence' and atom.truth_value.confidence < value:
                    match = False
                    break
            if match:
                results.append(atom)
        
        return results
    
    def get_inheritance_tree(self, root_name: str) -> Dict[str, Any]:
        """Get the inheritance tree starting from a root concept."""
        root_atoms = self.get_atoms_by_name(root_name)
        if not root_atoms:
            return {}
        
        root = root_atoms[0]
        tree = {'name': root.name, 'type': root.atom_type.value, 'children': []}
        
        # Find all inheritance links where root is the second element
        for link in self.get_atoms_by_type(AtomType.INHERITANCE):
            if len(link.outgoing) == 2 and link.outgoing[1] == root:
                child = link.outgoing[0]
                child_tree = self.get_inheritance_tree(child.name)
                if child_tree:
                    tree['children'].append(child_tree)
        
        return tree
    
    def export_to_json(self) -> str:
        """Export the entire Atomspace to JSON."""
        data = {
            'atoms': [a.to_dict() for a in self.atoms.values()],
            'statistics': {
                'total_atoms': len(self.atoms),
                'nodes': sum(1 for a in self.atoms.values() if a.is_node()),
                'links': sum(1 for a in self.atoms.values() if a.is_link()),
                'by_type': {t.value: len(handles) 
                           for t, handles in self.type_index.items() if handles}
            }
        }
        return json.dumps(data, indent=2, default=str)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get Atomspace statistics."""
        return {
            'total_atoms': len(self.atoms),
            'nodes': sum(1 for a in self.atoms.values() if a.is_node()),
            'links': sum(1 for a in self.atoms.values() if a.is_link()),
            'by_type': {t.value: len(handles) 
                       for t, handles in self.type_index.items() if handles}
        }


# Singleton instance
_atomspace_instance = None

def get_atomspace() -> PaystackAtomspace:
    """Get the singleton Atomspace instance."""
    global _atomspace_instance
    if _atomspace_instance is None:
        _atomspace_instance = PaystackAtomspace()
    return _atomspace_instance


if __name__ == "__main__":
    # Test the Atomspace
    atomspace = PaystackAtomspace()
    print("Atomspace Statistics:")
    print(json.dumps(atomspace.get_statistics(), indent=2))
    
    print("\nPayment Method Tree:")
    print(json.dumps(atomspace.get_inheritance_tree("PaymentMethod"), indent=2))
    
    print("\nSDK Tree:")
    print(json.dumps(atomspace.get_inheritance_tree("SDK"), indent=2))
