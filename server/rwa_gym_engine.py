"""
Gym Real-World Asset (RWA) Financing & $21M Platform Fee Optimization Engine
Manages:
1. TrainAlta & BJJLink Revenue-Share Tranches
2. Zebra Athletics Equipment Purchase Order Escrows
3. Interchange Fee & Capital Velocity Financial Analytics
"""

import time
import uuid
from typing import Dict, List, Any
from bitgo_service import bitgo_service

class GymRWAEngine:
    def __init__(self):
        self.rwa_agreements: Dict[str, Dict[str, Any]] = {}
        self._seed_rwa_agreements()

    def _seed_rwa_agreements(self):
        # 1. Zebra Athletics Equipment PO Financing
        self.create_agreement(
            agreement_id="RWA-ZEBRA-PO-2026-088",
            entity_name="Zebra Athletics Global Facility Rollout #88",
            category="Equipment Purchase Order Financing",
            sponsor="MMA.INC Capital Syndication",
            beneficiary="Zebra Athletics Manufacturing LLC",
            total_committed_usd=750000.00,
            milestones=[
                {"id": 0, "description": "Raw Material Procurement (High-Density EVA Foam & Antimicrobial Vinyl)", "amountUsd": 250000.00, "isReleased": True},
                {"id": 1, "description": "Precision Cutting, Mat Vulcanization & Cage Wall Assembly", "amountUsd": 250000.00, "isReleased": True},
                {"id": 2, "description": "Global Freight Logistics & Facility Delivery Verification", "amountUsd": 250000.00, "isReleased": False}
            ]
        )

        # 2. TrainAlta Austin Flagship Gym Expansion
        self.create_agreement(
            agreement_id="RWA-ALTA-ATX-2026-012",
            entity_name="TrainAlta Austin 20,000 sq ft High-Performance Center",
            category="Gym Expansion Tranche (Revenue Share)",
            sponsor="BitGo Qualified Investor Syndicate",
            beneficiary="TrainAlta Austin LLC",
            total_committed_usd=1200000.00,
            milestones=[
                {"id": 0, "description": "Commercial Lease Execution & Architectural Permitting", "amountUsd": 400000.00, "isReleased": True},
                {"id": 1, "description": "HVAC, Cage Grid Octagon & Recovery Zone Buildout", "amountUsd": 400000.00, "isReleased": False},
                {"id": 2, "description": "Grand Opening & First 500 Member Subscriptions Active", "amountUsd": 400000.00, "isReleased": False}
            ]
        )

        # 3. BJJLink Software & Belt Verification Hub
        self.create_agreement(
            agreement_id="RWA-BJJLINK-TECH-2026-004",
            entity_name="BJJLink Global Tournament & Belt Passport Integration",
            category="SaaS & Digital Infrastructure Tranche",
            sponsor="Unykorn RWA Fund",
            beneficiary="BJJLink International Pte Ltd",
            total_committed_usd=500000.00,
            milestones=[
                {"id": 0, "description": "ERC-3643 Belt Registry Smart Contract Audit & Deployment", "amountUsd": 200000.00, "isReleased": True},
                {"id": 1, "description": "Integration with 350+ IBJJF Certified Academies", "amountUsd": 200000.00, "isReleased": False},
                {"id": 2, "description": "Live On-Chain Tournament Bracket Pilot (1,000 Athletes)", "amountUsd": 100000.00, "isReleased": False}
            ]
        )

    def create_agreement(self, agreement_id: str, entity_name: str, category: str,
                         sponsor: str, beneficiary: str, total_committed_usd: float,
                         milestones: List[Dict[str, Any]]) -> Dict[str, Any]:
        
        released_amount = sum(m["amountUsd"] for m in milestones if m.get("isReleased", False))
        status = "Completed" if released_amount == total_committed_usd else ("Milestone Met" if released_amount > 0 else "Active")

        record = {
            "agreementId": agreement_id,
            "entityName": entity_name,
            "category": category,
            "sponsor": sponsor,
            "beneficiary": beneficiary,
            "totalCommittedUsd": total_committed_usd,
            "totalReleasedUsd": released_amount,
            "remainingEscrowUsd": total_committed_usd - released_amount,
            "status": status,
            "milestones": milestones,
            "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        self.rwa_agreements[agreement_id] = record
        return record

    def release_milestone(self, agreement_id: str, milestone_id: int) -> Dict[str, Any]:
        if agreement_id not in self.rwa_agreements:
            raise ValueError(f"Agreement {agreement_id} not found")
        
        agreement = self.rwa_agreements[agreement_id]
        if milestone_id >= len(agreement["milestones"]):
            raise ValueError(f"Milestone index {milestone_id} out of bounds")

        milestone = agreement["milestones"][milestone_id]
        if milestone.get("isReleased", False):
            raise ValueError(f"Milestone {milestone_id} already released")

        milestone["isReleased"] = True
        milestone["releasedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Update totals
        agreement["totalReleasedUsd"] += milestone["amountUsd"]
        agreement["remainingEscrowUsd"] = agreement["totalCommittedUsd"] - agreement["totalReleasedUsd"]

        if agreement["totalReleasedUsd"] == agreement["totalCommittedUsd"]:
            agreement["status"] = "Completed"
        else:
            agreement["status"] = "Milestone Met"

        # Log BitGo disbursement
        bitgo_service.transactions.append({
            "type": "RWA Milestone Escrow Release",
            "agreementId": agreement_id,
            "entity": agreement["entityName"],
            "beneficiary": agreement["beneficiary"],
            "amountUsd": milestone["amountUsd"],
            "milestone": milestone["description"],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "status": "Released (T+0)"
        })

        return agreement

    def get_financial_velocity_model(self, run_rate_usd: float = 21000000.00) -> Dict[str, Any]:
        """
        Calculates exact financial model matching the institutional prompt specification:
        Legacy (~3.70% / $777,000) vs Unykorn + BitGo (~0.55% / $115,500)
        Net Annual Savings = $661,500 / year + $210,000 T-Bills Yield = $871,500 / year Total Benefit.
        """
        # Legacy Breakdown
        legacy_merchant_cost = round(run_rate_usd * 0.021, 2) # $441,000 base
        legacy_fx_cost = round(run_rate_usd * 0.010, 2)       # $210,000
        legacy_chargeback_cost = round(run_rate_usd * 0.006, 2) # $126,000
        legacy_total_cost = round(run_rate_usd * 0.037, 2)    # $777,000

        # Unykorn + BitGo Breakdown
        unykorn_network_fee = round(run_rate_usd * 0.0040, 2) # $84,000
        unykorn_fx_cost = round(run_rate_usd * 0.0015, 2)     # $31,500
        unykorn_chargeback_cost = 0.00                        # $0.00
        unykorn_total_cost = round(run_rate_usd * 0.0055, 2)  # $115,500

        net_annual_savings = round(legacy_total_cost - unykorn_total_cost, 2) # $661,500.00

        # Treasury Yield on $4.0M Float
        treasury_float = 4000000.00
        annual_yield_rate = 0.0525
        annual_yield_generated = round(treasury_float * annual_yield_rate, 2) # $210,000.00

        total_economic_benefit = round(net_annual_savings + annual_yield_generated, 2) # $871,500.00

        return {
            "platformRunRateUsd": run_rate_usd,
            "legacyRails": {
                "name": "Legacy Card Gateways (Stripe/Authorize.net)",
                "merchantProcessingFee": legacy_merchant_cost,
                "crossBorderFxMarkup": legacy_fx_cost,
                "chargebacksAndFraud": legacy_chargeback_cost,
                "totalCostUsd": legacy_total_cost,
                "blendedRatePct": 3.70,
                "settlementTime": "T+2 to T+5 Rolling Reserves"
            },
            "unykornBitGoRails": {
                "name": "Unykorn.ai + BitGo Enterprise Rails",
                "merchantProcessingFee": unykorn_network_fee,
                "crossBorderFxMarkup": unykorn_fx_cost,
                "chargebacksAndFraud": 0.00,
                "totalCostUsd": unykorn_total_cost,
                "blendedRatePct": 0.55,
                "settlementTime": "T+0 Instant Real-Time Liquidity"
            },
            "annualSavingsUsd": net_annual_savings,
            "treasuryOptimization": {
                "idleTreasuryFloat": treasury_float,
                "tokenizedTBillYieldRatePct": 5.25,
                "annualYieldGeneratedUsd": annual_yield_generated,
                "dailyYieldGeneratedUsd": round(annual_yield_generated / 365.0, 2)
            },
            "totalAnnualEconomicBenefitUsd": total_economic_benefit
        }

    def get_all_agreements(self) -> List[Dict[str, Any]]:
        return list(self.rwa_agreements.values())

# Singleton instance
rwa_gym_engine = GymRWAEngine()
