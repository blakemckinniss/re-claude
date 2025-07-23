"""
Local memory store for claude-flow enforcement
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional


class LocalMemoryStore:
    """Simple local memory store for session tracking"""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path(__file__).parent / "memory-store.json"
        self.memory = self._load_memory()
        self.ttl_cache = {}
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from disk"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_memory(self):
        """Save memory to disk"""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception:
            pass
    
    def store(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Store value with optional TTL"""
        self.memory[key] = value
        
        if ttl:
            expiry = time.time() + ttl
            self.ttl_cache[key] = expiry
        
        self._save_memory()
        return True
    
    def query(self, key: str) -> Optional[str]:
        """Query value, respecting TTL"""
        # Check TTL
        if key in self.ttl_cache:
            if time.time() > self.ttl_cache[key]:
                # Expired
                del self.memory[key]
                del self.ttl_cache[key]
                self._save_memory()
                return None
        
        return self.memory.get(key)
    
    def delete(self, key: str) -> bool:
        """Delete a key"""
        if key in self.memory:
            del self.memory[key]
            if key in self.ttl_cache:
                del self.ttl_cache[key]
            self._save_memory()
            return True
        return False
    
    def search(self, pattern: str) -> Dict[str, str]:
        """Search for keys matching pattern"""
        results = {}
        for key, value in self.memory.items():
            if pattern in key:
                # Check TTL
                if key in self.ttl_cache and time.time() > self.ttl_cache[key]:
                    continue
                results[key] = value
        return results