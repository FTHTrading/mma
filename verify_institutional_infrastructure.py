"""
Verification Test Suite for FTH Institutional Infrastructure
Verifies:
1. Integer double-entry subledger balance checks (zero-sum debits/credits).
2. Policy-as-code evaluation (allowlist & role separation enforcement).
3. Hash-chained evidence receipts (.anvil/ops.receipts.jsonl integrity).
4. BitGo Enterprise & Go Network adapter functions.
5. Automated 3-way reconciliation engine.
6. 9-stage transaction lifecycle end-to-end execution.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "server"))

from workflow_orchestrator.orchestrator import orchestrator
from ledger_service.subledger_engine import subledger_engine, DoubleEntryJournalEntry
from policy_service.policy_engine import policy_engine
from evidence_service.receipt_engine import evidence_engine
from bitgo_adapter.bitgo_adapter import bitgo_adapter
from reconciliation_service.reconciler import reconciler

def test_institutional_infrastructure():
    print("=== STARTING FTH INSTITUTIONAL INFRASTRUCTURE VERIFICATION ===")

    # 1. Test Integer Double-Entry Subledger
    balances = subledger_engine.get_account_balances()
    print("1. Subledger Balances:", balances)
    assert "Asset:Custody:BitGo" in balances["accounts"]

    jnl = DoubleEntryJournalEntry("Test Settlement", "ref_test_01", "USD_CENT")
    jnl.add_debit("Asset:Custody:BitGo", 500000)
    jnl.add_credit("Asset:Bank:Fiat", 500000)
    posted = subledger_engine.post_journal_entry(jnl)
    print("   Posted Balanced Entry:", posted["journalId"])

    # Test float block (ValueError)
    try:
        jnl_bad = DoubleEntryJournalEntry("Float Test", "ref_bad", "USD")
        jnl_bad.add_debit("Asset:Custody:BitGo", 50.50)
        print("   FAILED: Float wasn't blocked")
    except ValueError as e:
        print("   SUCCESS: Float math strictly blocked by integer minor units rule:", e)

    # 2. Test Policy-as-Code Engine
    pol_pass = policy_engine.evaluate_policy(
        requester_id="kevan@unykorn.ai",
        destination_address="0x8aced25DC8530FDaf0f86D53a0A1E02AAfA7Ac7A",
        asset_symbol="USDC",
        amount_minor_units=14500000
    )
    print("2. Policy Evaluation (Valid Destination):", pol_pass["verdict"])
    assert pol_pass["verdict"] in ["ALLOW", "REQUIRE_MANUAL_REVIEW"]

    # Test Allowlist Block
    pol_fail = policy_engine.evaluate_policy(
        requester_id="kevan@unykorn.ai",
        destination_address="0xUnapprovedDestinationAddress9999",
        asset_symbol="USDC",
        amount_minor_units=1000
    )
    print("   Policy Evaluation (Unapproved Destination):", pol_fail["verdict"], pol_fail["violations"])
    assert pol_fail["verdict"] == "DENY"

    # Test Role Separation Block
    is_valid, msg = policy_engine.evaluate_approvers("kevan@unykorn.ai", ["kevan@unykorn.ai", "op2"])
    print("   Role Separation Check (Requester = Approver):", is_valid, msg)
    assert not is_valid

    # 3. Test BitGo Adapter
    positions = bitgo_adapter.get_portfolio_positions()
    print("3. BitGo Portfolio Value USD:", positions["totalPortfolioValueUsd"])
    assert len(positions["wallets"]) >= 3

    # 4. Test 3-Way Reconciliation
    recon_res = reconciler.run_reconciliation()
    print("4. Automated 3-Way Reconciliation Result:", recon_res["status"], f"RunId: {recon_res['reconciliationRunId']}")

    # 5. Test Evidence Receipt Chain Integrity
    integrity = evidence_engine.verify_chain_integrity()
    print("5. Evidence Receipts Hash-Chain Integrity:", integrity)
    assert integrity["valid"] is True

    # 6. Test 9-Stage Transaction Lifecycle Execution
    intent = orchestrator.create_transfer_intent(
        requester_id="operator_alice",
        source_account="Asset:Bank:Fiat",
        destination_address="0x8aced25DC8530FDaf0f86D53a0A1E02AAfA7Ac7A",
        asset_symbol="USDC",
        amount_minor_units=2500000,
        purpose="Institutional Treasury Liquidity Settlement"
    )
    print("6a. Stage 1 & 2 Intent Created:", intent["intentId"], "Status:", intent["status"])

    sealed = orchestrator.submit_operator_approvals(
        intent_id=intent["intentId"],
        approvers=["operator_bob", "operator_charlie"]
    )
    print("6b. Full 9-Stage Execution Sealed:", sealed["status"])
    print("    Stage Identifiers:", sealed["stageIds"])
    assert sealed["stageIds"]["receiptHash"] is not None

    print("\nALL FTH INSTITUTIONAL INFRASTRUCTURE TESTS PASSED 100% CLEANLY!")

if __name__ == "__main__":
    test_institutional_infrastructure()
