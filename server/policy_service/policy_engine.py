"""
Policy-As-Code Engine
Enforces 9 institutional governance policy rules before value movement.
Evaluates risk, limits, allowlists, role separation, and velocity.
"""

import time
import uuid
from typing import Dict, List, Any, Tuple

class PolicyEngine:
    """Evaluates transfer intents against policy-as-code rules."""

    def __init__(self):
        # 1. Destination Allowlist
        self.approved_destinations = {
            "0x8aced25DC8530FDaf0f86D53a0A1E02AAfA7Ac7A",
            "0x4E574939D460d284B5D990646D4aeaEF2D49Fa13",
            "0x7c4f8820a1b94e1d3c5f6a7b8c9d0e1f2a3b4567",
            "rJLMSTy77hTxqgDw9WMxCnYC8m5vhqN3FQ",
            "GB4FHGFUTLLMS3SC5RWRK6RYBGDIUQ5NR7IGN5TWAA3QVHULJ34JGEG4"
        }

        # 2. Risk & Velocity Limits
        self.max_single_tx_minor = 100000000  # $1,000,000 in cents
        self.dual_approval_threshold_minor = 10000000  # $100,000 in cents
        self.daily_velocity_limit_minor = 500000000  # $5,000,000 in cents
        self.current_daily_spent_minor = 14500000

        # 3. Emergency Pause & Reconciliation Hold
        self.emergency_pause_active = False
        self.reconciliation_hold_active = False

    def evaluate_policy(self, 
                        requester_id: str, 
                        destination_address: str, 
                        asset_symbol: str, 
                        amount_minor_units: int, 
                        break_glass_reason: str = None) -> Dict[str, Any]:
        
        decision_id = f"pol_{uuid.uuid4().hex[:12]}"
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        violations: List[str] = []
        requires_manual_review = False

        # Rule 1: Emergency Pause Check
        if self.emergency_pause_active and not break_glass_reason:
            violations.append("Emergency Pause active. Transfer blocked unless break-glass procedure invoked.")

        # Rule 2: Reconciliation Hold Check
        if self.reconciliation_hold_active:
            violations.append("Reconciliation Hold active: Unresolved discrepancy detected in prior ledger run.")

        # Rule 3: Destination Allowlist Check
        if destination_address not in self.approved_destinations:
            violations.append(f"Destination address {destination_address} is NOT on the approved counterparty allowlist.")

        # Rule 4: Maximum Single Transaction Limit Check
        if amount_minor_units > self.max_single_tx_minor:
            violations.append(f"Amount {amount_minor_units} exceeds maximum single transaction limit ({self.max_single_tx_minor}).")

        # Rule 5: Daily Velocity Limit Check
        if self.current_daily_spent_minor + amount_minor_units > self.daily_velocity_limit_minor:
            violations.append(f"Transfer would breach daily velocity limit ({self.daily_velocity_limit_minor} cents).")

        # Rule 6: Dual Approval Threshold Trigger
        requires_dual_approval = amount_minor_units >= self.dual_approval_threshold_minor
        if requires_dual_approval:
            requires_manual_review = True

        # Verdict Resolution
        if violations:
            verdict = "DENY"
        elif requires_manual_review:
            verdict = "REQUIRE_MANUAL_REVIEW"
        else:
            verdict = "ALLOW"

        return {
            "policyDecisionId": decision_id,
            "timestamp": timestamp,
            "verdict": verdict,
            "requesterId": requester_id,
            "destinationAddress": destination_address,
            "assetSymbol": asset_symbol,
            "amountMinorUnits": amount_minor_units,
            "requiresDualApproval": requires_dual_approval,
            "breakGlassInvoked": bool(break_glass_reason),
            "breakGlassReason": break_glass_reason,
            "violations": violations
        }

    def evaluate_approvers(self, requester_id: str, approvers: List[str]) -> Tuple[bool, str]:
        # Role Separation Rule: Requester cannot approve their own transfer intent
        if requester_id in approvers:
            return False, "Role Separation Violation: Requester cannot be an approver of their own transfer intent."
        
        if len(approvers) < 2:
            return False, "Dual Approval Required: Minimum 2 authorized operator signatures required."

        return True, "Approver set validated cleanly."


# Global singleton policy engine instance
policy_engine = PolicyEngine()
