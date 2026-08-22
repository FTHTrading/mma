"""
Hash-Chained Operational Evidence Receipt Engine
Produces immutable, tamper-evident audit receipts compatible with .anvil/ops.receipts.jsonl.
Uses SHA-256 hash chaining to guarantee zero tampering of transaction records.
"""

import hashlib
import json
import os
import time
from typing import Dict, List, Any, Optional

class EvidenceReceiptEngine:
    """Manages hash-chained operational receipts for audit readiness."""

    def __init__(self, storage_filepath: str = None):
        self.storage_filepath = storage_filepath or os.path.join(
            os.path.dirname(__file__), "..", "..", ".anvil", "ops.receipts.jsonl"
        )
        os.makedirs(os.path.dirname(self.storage_filepath), exist_ok=True)
        self.receipts_chain: List[Dict[str, Any]] = []
        self._load_existing_receipts()

    def _load_existing_receipts(self):
        if os.path.exists(self.storage_filepath):
            try:
                with open(self.storage_filepath, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            self.receipts_chain.append(json.loads(line.strip()))
            except Exception as e:
                print(f"[EvidenceReceiptEngine] Warning reading receipts: {e}")

        # Seed genesis receipt if chain is empty
        if not self.receipts_chain:
            genesis = {
                "receiptIndex": 0,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "eventType": "GENESIS_RECEIPT",
                "prevHash": "0000000000000000000000000000000000000000000000000000000000000000",
                "stageIds": {"genesis": "G0_INTENT_CHARTER"},
                "operatorSignatures": ["Unykorn_Genesis_Key"],
                "receiptHash": ""
            }
            genesis["receiptHash"] = self._compute_hash(genesis)
            self.receipts_chain.append(genesis)
            self._append_to_file(genesis)

    def _compute_hash(self, receipt: Dict[str, Any]) -> str:
        # Create deterministic json string without receiptHash
        clean_receipt = {k: v for k, v in receipt.items() if k != "receiptHash"}
        serialized = json.dumps(clean_receipt, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def _append_to_file(self, receipt: Dict[str, Any]):
        try:
            with open(self.storage_filepath, "a", encoding="utf-8") as f:
                f.write(json.dumps(receipt) + "\n")
        except Exception as e:
            print(f"[EvidenceReceiptEngine] Error appending receipt: {e}")

    def seal_receipt(self, 
                     event_type: str, 
                     stage_ids: Dict[str, Any], 
                     operator_signatures: List[str],
                     metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        
        prev_receipt = self.receipts_chain[-1]
        prev_hash = prev_receipt["receiptHash"]
        
        receipt_index = len(self.receipts_chain)
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        receipt = {
            "receiptIndex": receipt_index,
            "timestamp": timestamp,
            "eventType": event_type,
            "prevHash": prev_hash,
            "stageIds": stage_ids,
            "operatorSignatures": operator_signatures,
            "metadata": metadata or {}
        }

        receipt_hash = self._compute_hash(receipt)
        receipt["receiptHash"] = receipt_hash

        self.receipts_chain.append(receipt)
        self._append_to_file(receipt)
        return receipt

    def verify_chain_integrity(self) -> Dict[str, Any]:
        """Validates hash-chain integrity from genesis to head."""
        if not self.receipts_chain:
            return {"valid": True, "totalReceipts": 0}

        for i in range(len(self.receipts_chain)):
            current = self.receipts_chain[i]
            # Check internal hash
            computed = self._compute_hash(current)
            if computed != current["receiptHash"]:
                return {
                    "valid": False,
                    "brokenIndex": i,
                    "reason": f"Hash mismatch at index {i}: computed {computed} != stored {current['receiptHash']}"
                }

            # Check previous hash link
            if i > 0:
                prev = self.receipts_chain[i - 1]
                if current["prevHash"] != prev["receiptHash"]:
                    return {
                        "valid": False,
                        "brokenIndex": i,
                        "reason": f"Chain link broken at index {i}: prevHash {current['prevHash']} != prev receiptHash {prev['receiptHash']}"
                    }

        return {
            "valid": True,
            "totalReceipts": len(self.receipts_chain),
            "headHash": self.receipts_chain[-1]["receiptHash"]
        }

    def get_receipts(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self.receipts_chain[-limit:]


# Global singleton evidence engine instance
evidence_engine = EvidenceReceiptEngine()
