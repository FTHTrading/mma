"""
9-Stage Transaction Lifecycle Event Types & Data Structures
Enforces the mandatory 9-stage transaction lifecycle:
intent_id -> policy_decision_id -> approval_set_id -> custody_reference -> 
chain_tx_hash -> settlement_reference -> ledger_journal_id -> reconciliation_run_id -> receipt_hash
"""

import time
import uuid
from typing import Dict, List, Any, Optional

class TransactionIntentStage:
    """9-Stage Transaction Lifecycle State Container"""
    
    def __init__(self, 
                 requester_id: str, 
                 source_account: str, 
                 destination_address: str, 
                 asset_symbol: str, 
                 amount_minor_units: int, 
                 purpose: str,
                 metadata: Optional[Dict[str, Any]] = None):
        
        # 1. intent_id
        self.intent_id = f"intent_{uuid.uuid4().hex[:12]}"
        self.created_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.requester_id = requester_id
        self.source_account = source_account
        self.destination_address = destination_address
        self.asset_symbol = asset_symbol.upper()
        
        # Integer minor units check
        if not isinstance(amount_minor_units, int) or amount_minor_units <= 0:
            raise ValueError("amount_minor_units must be a positive integer (e.g. cents, drops, wei)")
        self.amount_minor_units = amount_minor_units
        self.purpose = purpose
        self.metadata = metadata or {}
        
        # Stages 2-9 initialized as None until processed
        self.policy_decision_id: Optional[str] = None
        self.policy_verdict: Optional[str] = None  # ALLOW, DENY, REQUIRE_MANUAL_REVIEW
        
        self.approval_set_id: Optional[str] = None
        self.approvers: List[str] = []
        
        self.custody_reference: Optional[str] = None  # BitGo transfer ID
        self.chain_tx_hash: Optional[str] = None     # EVM / XRPL / Solana tx hash
        self.settlement_reference: Optional[str] = None  # Go Network or Bank settlement ID
        
        self.ledger_journal_id: Optional[str] = None
        self.reconciliation_run_id: Optional[str] = None
        self.receipt_hash: Optional[str] = None
        
        self.status = "INTENT_CREATED"  # INTENT_CREATED, POLICY_APPROVED, APPROVAL_COMPLETE, CUSTODY_SUBMITTED, CONFIRMED, RECONCILED, SEALED, REJECTED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intentId": self.intent_id,
            "createdAt": self.created_at,
            "requesterId": self.requester_id,
            "sourceAccount": self.source_account,
            "destinationAddress": self.destination_address,
            "assetSymbol": self.asset_symbol,
            "amountMinorUnits": self.amount_minor_units,
            "purpose": self.purpose,
            "status": self.status,
            "stageIds": {
                "intentId": self.intent_id,
                "policyDecisionId": self.policy_decision_id,
                "approvalSetId": self.approval_set_id,
                "custodyReference": self.custody_reference,
                "chainTxHash": self.chain_tx_hash,
                "settlementReference": self.settlement_reference,
                "ledgerJournalId": self.ledger_journal_id,
                "reconciliationRunId": self.reconciliation_run_id,
                "receiptHash": self.receipt_hash
            },
            "policyVerdict": self.policy_verdict,
            "approvers": self.approvers,
            "metadata": self.metadata
        }
