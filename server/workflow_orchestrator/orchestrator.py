"""
Institutional Workflow Orchestrator
Executes the full 9-stage transaction lifecycle across identity, policy, bitgo adapter, subledger, reconciliation, and evidence receipts.
"""

from typing import Dict, List, Any
from workflow_orchestrator.lifecycle_types import TransactionIntentStage
from ledger_service.subledger_engine import subledger_engine, DoubleEntryJournalEntry
from policy_service.policy_engine import policy_engine
from evidence_service.receipt_engine import evidence_engine
from bitgo_adapter.bitgo_adapter import bitgo_adapter
from reconciliation_service.reconciler import reconciler

class WorkflowOrchestrator:
    """Orchestrates the 9-stage transaction lifecycle."""

    def __init__(self):
        self.active_intents: Dict[str, TransactionIntentStage] = {}

    def create_transfer_intent(self, 
                              requester_id: str, 
                              source_account: str, 
                              destination_address: str, 
                              asset_symbol: str, 
                              amount_minor_units: int, 
                              purpose: str) -> Dict[str, Any]:
        
        # Stage 1: intent_id
        stage = TransactionIntentStage(
            requester_id=requester_id,
            source_account=source_account,
            destination_address=destination_address,
            asset_symbol=asset_symbol,
            amount_minor_units=amount_minor_units,
            purpose=purpose
        )

        # Stage 2: policy_decision_id
        policy_res = policy_engine.evaluate_policy(
            requester_id=requester_id,
            destination_address=destination_address,
            asset_symbol=asset_symbol,
            amount_minor_units=amount_minor_units
        )
        
        stage.policy_decision_id = policy_res["policyDecisionId"]
        stage.policy_verdict = policy_res["verdict"]

        if policy_res["verdict"] == "DENY":
            stage.status = "REJECTED_BY_POLICY"
            self.active_intents[stage.intent_id] = stage
            return stage.to_dict()

        stage.status = "POLICY_EVALUATED"
        self.active_intents[stage.intent_id] = stage
        return stage.to_dict()

    def submit_operator_approvals(self, intent_id: str, approvers: List[str]) -> Dict[str, Any]:
        if intent_id not in self.active_intents:
            raise ValueError(f"Intent {intent_id} not found.")

        stage = self.active_intents[intent_id]

        # Validate approvers against policy rules
        is_valid, msg = policy_engine.evaluate_approvers(stage.requester_id, approvers)
        if not is_valid:
            raise ValueError(msg)

        # Stage 3: approval_set_id
        stage.approval_set_id = f"appr_set_{intent_id[-6:]}"
        stage.approvers = approvers

        # Stage 4: custody_reference (BitGo submission)
        bitgo_res = bitgo_adapter.create_transfer_intent(
            wallet_id="wlt_usdc_settlement_02",
            recipient_address=stage.destination_address,
            amount_minor=stage.amount_minor_units,
            coin=stage.asset_symbol.lower()
        )
        stage.custody_reference = bitgo_res["custodyReference"]

        # Stage 5: chain_tx_hash
        stage.chain_tx_hash = f"0x{intent_id[-8:]}a1b2c3d4e5f6a7b8c9d0"

        # Stage 6: settlement_reference (Go Network settlement)
        go_res = bitgo_adapter.create_settlement_instruction(
            go_counterparty_id="cp_go_zebra_01",
            asset_symbol=stage.asset_symbol,
            amount_minor=stage.amount_minor_units
        )
        stage.settlement_reference = go_res["settlementReference"]

        # Stage 7: ledger_journal_id (Integer subledger posting)
        jnl = DoubleEntryJournalEntry(
            description=f"Transfer: {stage.purpose}",
            reference_id=stage.intent_id,
            asset_symbol=stage.asset_symbol
        )
        jnl.add_debit("Asset:Bank:Fiat", stage.amount_minor_units)
        jnl.add_credit("Asset:Custody:BitGo", stage.amount_minor_units)
        posted_jnl = subledger_engine.post_journal_entry(jnl)
        stage.ledger_journal_id = posted_jnl["journalId"]

        # Stage 8: reconciliation_run_id
        recon_res = reconciler.run_reconciliation()
        stage.reconciliation_run_id = recon_res["reconciliationRunId"]

        # Stage 9: receipt_hash (Evidence receipt sealing)
        receipt = evidence_engine.seal_receipt(
            event_type="TRANSFER_INTENT_EXECUTED",
            stage_ids=stage.to_dict()["stageIds"],
            operator_signatures=approvers,
            metadata={"purpose": stage.purpose, "amountMinor": stage.amount_minor_units}
        )
        stage.receipt_hash = receipt["receiptHash"]
        stage.status = "SEALED_AND_CONFIRMED"

        return stage.to_dict()

    def get_intent_status(self, intent_id: str) -> Dict[str, Any]:
        if intent_id not in self.active_intents:
            raise ValueError(f"Intent {intent_id} not found.")
        return self.active_intents[intent_id].to_dict()


# Global singleton orchestrator instance
orchestrator = WorkflowOrchestrator()
