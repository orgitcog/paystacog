#!/usr/bin/env python3
"""
Agent Memory System for PaystaCog

Implements persistent memory and learning capabilities for agents.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import hashlib
from collections import defaultdict
from enum import Enum


class MemoryType(Enum):
    """Types of memory storage."""
    EPISODIC = "episodic"      # Specific events and experiences
    SEMANTIC = "semantic"      # General knowledge and facts
    PROCEDURAL = "procedural"  # How to do things
    WORKING = "working"        # Current context and goals


@dataclass
class MemoryEntry:
    """A single memory entry."""
    memory_id: str
    memory_type: MemoryType
    content: Dict[str, Any]
    importance: float = 0.5
    access_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    associations: List[str] = field(default_factory=list)
    
    def decay_importance(self, decay_rate: float = 0.01):
        """Apply time-based decay to importance."""
        hours_since_access = (datetime.utcnow() - self.last_accessed).total_seconds() / 3600
        self.importance *= (1 - decay_rate) ** hours_since_access
    
    def boost_importance(self, boost: float = 0.1):
        """Boost importance when accessed."""
        self.importance = min(1.0, self.importance + boost)
        self.access_count += 1
        self.last_accessed = datetime.utcnow()


class AgentMemory:
    """
    Memory system for PaystaCog agents.
    
    Features:
    - Multiple memory types (episodic, semantic, procedural, working)
    - Importance-based retrieval
    - Time-based decay
    - Associative memory linking
    - Pattern learning
    """
    
    def __init__(self, agent_id: str, max_memories: int = 10000):
        self.agent_id = agent_id
        self.max_memories = max_memories
        self.memories: Dict[str, MemoryEntry] = {}
        self.type_index: Dict[MemoryType, List[str]] = {t: [] for t in MemoryType}
        self.tag_index: Dict[str, List[str]] = defaultdict(list)
        self.patterns: Dict[str, Dict] = {}
        self.learning_rate = 0.1
    
    def _generate_id(self, content: Dict) -> str:
        """Generate unique memory ID."""
        content_str = json.dumps(content, sort_keys=True, default=str)
        return hashlib.md5(content_str.encode()).hexdigest()[:16]
    
    def store(self, memory_type: MemoryType, content: Dict[str, Any],
              importance: float = 0.5, tags: Optional[List[str]] = None,
              ttl_hours: Optional[int] = None) -> str:
        """Store a new memory."""
        memory_id = self._generate_id(content)
        
        # Check for existing memory
        if memory_id in self.memories:
            existing = self.memories[memory_id]
            existing.boost_importance()
            return memory_id
        
        # Create new memory
        expires_at = None
        if ttl_hours:
            expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
        
        memory = MemoryEntry(
            memory_id=memory_id,
            memory_type=memory_type,
            content=content,
            importance=importance,
            tags=tags or [],
            expires_at=expires_at
        )
        
        # Store and index
        self.memories[memory_id] = memory
        self.type_index[memory_type].append(memory_id)
        
        for tag in memory.tags:
            self.tag_index[tag].append(memory_id)
        
        # Enforce memory limit
        if len(self.memories) > self.max_memories:
            self._forget_least_important()
        
        return memory_id
    
    def recall(self, memory_id: str) -> Optional[MemoryEntry]:
        """Recall a specific memory."""
        if memory_id in self.memories:
            memory = self.memories[memory_id]
            memory.boost_importance()
            return memory
        return None
    
    def recall_by_type(self, memory_type: MemoryType, 
                       limit: int = 10) -> List[MemoryEntry]:
        """Recall memories of a specific type."""
        memory_ids = self.type_index.get(memory_type, [])
        memories = [self.memories[mid] for mid in memory_ids if mid in self.memories]
        
        # Sort by importance
        memories.sort(key=lambda m: m.importance, reverse=True)
        
        # Boost accessed memories
        for m in memories[:limit]:
            m.boost_importance(0.05)
        
        return memories[:limit]
    
    def recall_by_tag(self, tag: str, limit: int = 10) -> List[MemoryEntry]:
        """Recall memories with a specific tag."""
        memory_ids = self.tag_index.get(tag, [])
        memories = [self.memories[mid] for mid in memory_ids if mid in self.memories]
        memories.sort(key=lambda m: m.importance, reverse=True)
        return memories[:limit]
    
    def search(self, query: Dict[str, Any], limit: int = 10) -> List[MemoryEntry]:
        """Search memories by content similarity."""
        results = []
        
        for memory in self.memories.values():
            score = self._calculate_similarity(query, memory.content)
            if score > 0.3:  # Threshold
                results.append((memory, score))
        
        # Sort by score * importance
        results.sort(key=lambda x: x[1] * x[0].importance, reverse=True)
        
        return [m for m, _ in results[:limit]]
    
    def _calculate_similarity(self, query: Dict, content: Dict) -> float:
        """Calculate similarity between query and content."""
        query_keys = set(query.keys())
        content_keys = set(content.keys())
        
        if not query_keys:
            return 0.0
        
        # Key overlap
        common_keys = query_keys & content_keys
        key_score = len(common_keys) / len(query_keys)
        
        # Value matching
        value_matches = 0
        for key in common_keys:
            if query[key] == content[key]:
                value_matches += 1
            elif isinstance(query[key], str) and isinstance(content[key], str):
                if query[key].lower() in content[key].lower():
                    value_matches += 0.5
        
        value_score = value_matches / len(query_keys) if query_keys else 0
        
        return (key_score + value_score) / 2
    
    def associate(self, memory_id1: str, memory_id2: str):
        """Create an association between two memories."""
        if memory_id1 in self.memories and memory_id2 in self.memories:
            m1 = self.memories[memory_id1]
            m2 = self.memories[memory_id2]
            
            if memory_id2 not in m1.associations:
                m1.associations.append(memory_id2)
            if memory_id1 not in m2.associations:
                m2.associations.append(memory_id1)
    
    def get_associations(self, memory_id: str) -> List[MemoryEntry]:
        """Get all memories associated with a given memory."""
        if memory_id not in self.memories:
            return []
        
        memory = self.memories[memory_id]
        return [self.memories[aid] for aid in memory.associations 
                if aid in self.memories]
    
    def learn_pattern(self, pattern_name: str, examples: List[Dict]):
        """Learn a pattern from examples."""
        if not examples:
            return
        
        # Extract common features
        common_keys = set(examples[0].keys())
        for example in examples[1:]:
            common_keys &= set(example.keys())
        
        # Calculate value distributions
        value_distributions = {}
        for key in common_keys:
            values = [ex[key] for ex in examples]
            if all(isinstance(v, (int, float)) for v in values):
                value_distributions[key] = {
                    "type": "numeric",
                    "min": min(values),
                    "max": max(values),
                    "mean": sum(values) / len(values)
                }
            else:
                unique_values = list(set(str(v) for v in values))
                value_distributions[key] = {
                    "type": "categorical",
                    "values": unique_values,
                    "most_common": max(set(values), key=values.count)
                }
        
        self.patterns[pattern_name] = {
            "keys": list(common_keys),
            "distributions": value_distributions,
            "example_count": len(examples),
            "learned_at": datetime.utcnow().isoformat()
        }
    
    def match_pattern(self, pattern_name: str, data: Dict) -> float:
        """Check how well data matches a learned pattern."""
        if pattern_name not in self.patterns:
            return 0.0
        
        pattern = self.patterns[pattern_name]
        score = 0.0
        total_keys = len(pattern["keys"])
        
        if total_keys == 0:
            return 0.0
        
        for key in pattern["keys"]:
            if key not in data:
                continue
            
            dist = pattern["distributions"].get(key, {})
            value = data[key]
            
            if dist.get("type") == "numeric":
                if dist["min"] <= value <= dist["max"]:
                    score += 1.0
                else:
                    # Partial score for close values
                    range_size = dist["max"] - dist["min"]
                    if range_size > 0:
                        distance = min(abs(value - dist["min"]), abs(value - dist["max"]))
                        score += max(0, 1 - distance / range_size)
            elif dist.get("type") == "categorical":
                if str(value) in dist.get("values", []):
                    score += 1.0
        
        return score / total_keys
    
    def _forget_least_important(self):
        """Remove the least important memory."""
        if not self.memories:
            return
        
        # Apply decay to all memories
        for memory in self.memories.values():
            memory.decay_importance()
        
        # Find least important
        least_important = min(self.memories.values(), key=lambda m: m.importance)
        
        # Remove from indices
        self.type_index[least_important.memory_type].remove(least_important.memory_id)
        for tag in least_important.tags:
            if least_important.memory_id in self.tag_index[tag]:
                self.tag_index[tag].remove(least_important.memory_id)
        
        # Remove memory
        del self.memories[least_important.memory_id]
    
    def cleanup_expired(self):
        """Remove expired memories."""
        now = datetime.utcnow()
        expired = [
            mid for mid, m in self.memories.items()
            if m.expires_at and m.expires_at < now
        ]
        
        for memory_id in expired:
            memory = self.memories[memory_id]
            self.type_index[memory.memory_type].remove(memory_id)
            for tag in memory.tags:
                if memory_id in self.tag_index[tag]:
                    self.tag_index[tag].remove(memory_id)
            del self.memories[memory_id]
        
        return len(expired)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            "agent_id": self.agent_id,
            "total_memories": len(self.memories),
            "by_type": {t.value: len(ids) for t, ids in self.type_index.items()},
            "patterns_learned": len(self.patterns),
            "average_importance": sum(m.importance for m in self.memories.values()) / len(self.memories) if self.memories else 0,
            "total_access_count": sum(m.access_count for m in self.memories.values())
        }
    
    def export_to_json(self) -> str:
        """Export memory to JSON."""
        data = {
            "agent_id": self.agent_id,
            "memories": [
                {
                    "memory_id": m.memory_id,
                    "type": m.memory_type.value,
                    "content": m.content,
                    "importance": m.importance,
                    "tags": m.tags,
                    "created_at": m.created_at.isoformat()
                }
                for m in self.memories.values()
            ],
            "patterns": self.patterns,
            "statistics": self.get_statistics()
        }
        return json.dumps(data, indent=2, default=str)
    
    def import_from_json(self, json_str: str):
        """Import memory from JSON."""
        data = json.loads(json_str)
        
        for mem_data in data.get("memories", []):
            self.store(
                memory_type=MemoryType(mem_data["type"]),
                content=mem_data["content"],
                importance=mem_data.get("importance", 0.5),
                tags=mem_data.get("tags", [])
            )
        
        self.patterns = data.get("patterns", {})


if __name__ == "__main__":
    # Test the memory system
    memory = AgentMemory("test-agent")
    
    # Store some memories
    memory.store(
        MemoryType.EPISODIC,
        {"event": "transaction", "amount": 10000, "status": "success"},
        importance=0.8,
        tags=["transaction", "success"]
    )
    
    memory.store(
        MemoryType.SEMANTIC,
        {"fact": "NGN is Nigerian Naira", "currency_code": "NGN"},
        importance=0.9,
        tags=["currency", "knowledge"]
    )
    
    memory.store(
        MemoryType.PROCEDURAL,
        {"procedure": "verify_transaction", "steps": ["check_reference", "validate_amount", "confirm_status"]},
        importance=0.95,
        tags=["procedure", "verification"]
    )
    
    # Learn a pattern
    memory.learn_pattern("successful_transaction", [
        {"amount": 5000, "status": "success", "method": "card"},
        {"amount": 10000, "status": "success", "method": "card"},
        {"amount": 7500, "status": "success", "method": "bank"}
    ])
    
    print("Memory Statistics:")
    print(json.dumps(memory.get_statistics(), indent=2))
    
    print("\nRecall by type (EPISODIC):")
    for m in memory.recall_by_type(MemoryType.EPISODIC):
        print(f"  - {m.content}")
    
    print("\nPattern match test:")
    test_data = {"amount": 8000, "status": "success", "method": "card"}
    score = memory.match_pattern("successful_transaction", test_data)
    print(f"  Match score: {score}")
