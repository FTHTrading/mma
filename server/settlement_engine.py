"""
Unykorn.ai MMA Purse Settlement & Multi-Jurisdiction Compliance Engine
Manages fight cards, programmable split distributions, athletic commission reporting,
and automated tax withholding across US, Japan, Thailand, Singapore, and Middle East.
"""

import time
import uuid
from typing import Dict, List, Any, Optional
from bitgo_service import bitgo_service

class MMAPurseSettlementEngine:
    def __init__(self):
        self.bouts: Dict[str, Dict[str, Any]] = {}
        self.jurisdiction_compliance_rules = {
            "US": {
                "name": "United States",
                "regulators": ["SEC", "CFTC", "FinCEN", "State Athletic Commissions (NSAC/CSAC/NYSAC)"],
                "taxForms": "Form 1099-MISC (Domestic) / Form 1042-S (Foreign National)",
                "withholdingTaxBps": 1000, # 10.0% statutory state/federal purse withholding
                "settlementRail": "BitGo Trust Bank Custody (USD Wire / USDC)",
                "coldStorageMandate": "Standard OCC Chartered Qualified Trust",
                "tokenLegality": "Fully compliant institutional stablecoins"
            },
            "JP": {
                "name": "Japan",
                "regulators": ["JFSA (Financial Services Agency)", "JVCEA"],
                "taxForms": "National Tax Agency (NTA) Article 161 Foreign Athlete Withholding (20.42%)",
                "withholdingTaxBps": 2042, # 20.42%
                "settlementRail": "BitGo MPC / Licensed Electronic Payment Instrument (EPI / JPYC)",
                "coldStorageMandate": "Strict 95% Offline Cold Storage Mandate (PSA Article 63-11)",
                "tokenLegality": "JVCEA Whitelisted Tokens & Regulated EPI only"
            },
            "TH": {
                "name": "Thailand",
                "regulators": ["Thai SEC", "Bank of Thailand (BOT)", "Sports Authority of Thailand (SAT)"],
                "taxForms": "Revenue Department Form P.N.D. 53 (15% Foreign Entertainer/Athlete)",
                "withholdingTaxBps": 1500, # 15.0%
                "settlementRail": "Regulated Thai VASP Bridge -> THB Instant PromptPay/BAHTNET",
                "coldStorageMandate": "BOT Payment Gateway Segregation",
                "tokenLegality": "Restricted direct retail tender; programmatic conversion to THB required"
            },
            "SG": {
                "name": "Singapore (APAC Hub)",
                "regulators": ["Monetary Authority of Singapore (MAS)"],
                "taxForms": "IRAS Non-Resident Professional Withholding (15.0% or 24.0%)",
                "withholdingTaxBps": 1500, # 15.0%
                "settlementRail": "BitGo Singapore (Major Payment Institution License) Global Hub",
                "coldStorageMandate": "MAS PSN01 / PSN02 Segregated Treasury Vaults",
                "tokenLegality": "Standard Payment Token (DPT) compliant rails"
            },
            "UAE": {
                "name": "United Arab Emirates (Dubai / Abu Dhabi)",
                "regulators": ["VARA (Dubai)", "ADGM (Abu Dhabi)", "UAE General Sports Authority"],
                "taxForms": "Zero Personal Income Tax / Corporate Tax Gateway",
                "withholdingTaxBps": 0, # 0.0%
                "settlementRail": "VARA-Compliant Virtual Asset Infrastructure / Sovereign Syndication",
                "coldStorageMandate": "VARA Custody & Cybersecurity Standards",
                "tokenLegality": "Full virtual asset distribution authorization"
            }
        }
        self._seed_sample_bouts()

    def _seed_sample_bouts(self):
        # 1. UFC / MMA.INC Las Vegas Championship Bout (US Jurisdiction)
        self.create_bout(
            bout_id="BOUT-LV-2026-001",
            event_name="MMA.INC World Championship Series: Vegas Main Event",
            fighter_a_name="Alex 'The Apex' Pereira",
            fighter_a_wallet="0x8ACED25dc8530FDaf0f86D53a0A1E02AAfA7Ac7A",
            fighter_b_name="Israel Adesanya",
            fighter_b_wallet="0x71C568ba458E303649e31ff48a60F65D6169996D",
            jurisdiction="US",
            base_purse_minor=100000000, # $1,000,000.00 (in minor cents)
            win_bonus_minor=50000000,   # $500,000.00 win bonus
            settlement_token="USDC",
            splits=[
                {"recipient": "0x8ACED25dc8530FDaf0f86D53a0A1E02AAfA7Ac7A", "name": "Fighter Net Payout", "percentageBps": 7000, "role": "Fighter"},
                {"recipient": "0x1111222233334444555566667777888899990001", "name": "Head Coach & Training Camp", "percentageBps": 1000, "role": "Corner/Trainer"},
                {"recipient": "0x1111222233334444555566667777888899990002", "name": "Dominance MMA Management", "percentageBps": 1000, "role": "Management"},
                {"recipient": "0x1111222233334444555566667777888899990003", "name": "Nevada State Athletic Commission Tax", "percentageBps": 1000, "role": "AthleticCommission"}
            ]
        )

        # 2. RIZIN / MMA.INC Tokyo Super Bout (Japan Jurisdiction)
        self.create_bout(
            bout_id="BOUT-TYO-2026-002",
            event_name="MMA.INC x RIZIN Landmark Saitama Grand Prix",
            fighter_a_name="Kai Asakura",
            fighter_a_wallet="0x3333444455556666777788889999000011112222",
            fighter_b_name="Kyoji Horiguchi",
            fighter_b_wallet="0x4444555566667777888899990000111122223333",
            jurisdiction="JP",
            base_purse_minor=60000000, # $600,000.00
            win_bonus_minor=20000000,  # $200,000.00
            settlement_token="JPYC",
            splits=[
                {"recipient": "0x3333444455556666777788889999000011112222", "name": "Fighter Net Payout (JPYC)", "percentageBps": 6500, "role": "Fighter"},
                {"recipient": "0x5555666677778888999900001111222233334444", "name": "American Top Team Gym", "percentageBps": 1000, "role": "Corner/Trainer"},
                {"recipient": "0x6666777788889999000011112222333344445555", "name": "Rizin Management Corp", "percentageBps": 500, "role": "Management"},
                {"recipient": "0x7777888899990000111122223333444455556666", "name": "JFSA / NTA Withholding Tax Account", "percentageBps": 2000, "role": "AthleticCommission"}
            ]
        )

        # 3. Lumpinee Muay Thai Super Series (Thailand Jurisdiction)
        self.create_bout(
            bout_id="BOUT-BKK-2026-003",
            event_name="ONE Lumpinee / MMA.INC Bangkok Muay Thai Title",
            fighter_a_name="Rodtang Jitmuangnon",
            fighter_a_wallet="0x8888999900001111222233334444555566667777",
            fighter_b_name="Superlek Kiatmoo9",
            fighter_b_wallet="0x9999000011112222333344445555666677778888",
            jurisdiction="TH",
            base_purse_minor=30000000, # $300,000.00
            win_bonus_minor=10000000,  # $100,000.00
            settlement_token="THB_PROMPTPAY",
            splits=[
                {"recipient": "0x8888999900001111222233334444555566667777", "name": "Fighter THB Direct Account", "percentageBps": 7000, "role": "Fighter"},
                {"recipient": "0xAAAA000011112222333344445555666677778888", "name": "Jitmuangnon Gym Camp Split", "percentageBps": 1000, "role": "Corner/Trainer"},
                {"recipient": "0xBBBB000011112222333344445555666677778888", "name": "Promoter Fee Escrow", "percentageBps": 500, "role": "Management"},
                {"recipient": "0xCCCC000011112222333344445555666677778888", "name": "Thai Revenue Dept (PND 53)", "percentageBps": 1500, "role": "AthleticCommission"}
            ]
        )

    def create_bout(self, bout_id: str, event_name: str, fighter_a_name: str, fighter_a_wallet: str,
                    fighter_b_name: str, fighter_b_wallet: str, jurisdiction: str,
                    base_purse_minor: int, win_bonus_minor: int, settlement_token: str,
                    splits: List[Dict[str, Any]]) -> Dict[str, Any]:
        
        # Verify 10,000 BPS exact
        total_bps = sum(s["percentageBps"] for s in splits)
        if total_bps != 10000:
            raise ValueError(f"Splits must sum to exactly 10,000 BPS (got {total_bps})")
        
        record = {
            "boutId": bout_id,
            "eventName": event_name,
            "fighterA": {"name": fighter_a_name, "wallet": fighter_a_wallet, "kycVerified": True},
            "fighterB": {"name": fighter_b_name, "wallet": fighter_b_wallet, "kycVerified": True},
            "jurisdiction": jurisdiction,
            "jurisdictionDetails": self.jurisdiction_compliance_rules.get(jurisdiction, {}),
            "basePurseMinor": base_purse_minor,
            "basePurseUsd": base_purse_minor / 100.0,
            "winBonusMinor": win_bonus_minor,
            "winBonusUsd": win_bonus_minor / 100.0,
            "settlementToken": settlement_token,
            "splits": splits,
            "status": "Scheduled",
            "winner": None,
            "isSettled": False,
            "settledAt": None,
            "disbursements": []
        }
        self.bouts[bout_id] = record
        return record

    def record_and_settle_bout(self, bout_id: str, winner_name: str, method: str = "KO/TKO Round 2") -> Dict[str, Any]:
        if bout_id not in self.bouts:
            raise ValueError(f"Bout {bout_id} not found")
        
        bout = self.bouts[bout_id]
        if bout["isSettled"]:
            raise ValueError(f"Bout {bout_id} already settled")

        bout["winner"] = winner_name
        bout["winMethod"] = method
        bout["status"] = "Completed"

        # Calculate final purse with win bonus
        final_purse_minor = bout["basePurseMinor"] + (bout["winBonusMinor"] if winner_name else 0)
        bout["finalPurseMinor"] = final_purse_minor
        bout["finalPurseUsd"] = final_purse_minor / 100.0

        disbursements = []
        cumulative_minor = 0

        # Execute programmatic splits via BitGo MPC
        for i, split in enumerate(bout["splits"]):
            # Integer math in minor units
            payout_minor = (final_purse_minor * split["percentageBps"]) // 10000
            
            # Handle dust rounding on last tranche
            if i == len(bout["splits"]) - 1:
                payout_minor = final_purse_minor - cumulative_minor
            
            cumulative_minor += payout_minor

            # Trigger BitGo MPC transfer
            tx = bitgo_service.execute_mpc_purse_transfer(
                token_symbol=bout["settlementToken"],
                recipient_address=split["recipient"],
                amount_minor=payout_minor,
                role=split["role"],
                jurisdiction=bout["jurisdiction"]
            )
            disbursements.append({
                "recipient": split["recipient"],
                "name": split["name"],
                "role": split["role"],
                "percentageBps": split["percentageBps"],
                "amountMinor": payout_minor,
                "amountUsd": payout_minor / 100.0,
                "txHash": tx["txHash"],
                "status": "Settled T+0"
            })

        bout["disbursements"] = disbursements
        bout["isSettled"] = True
        bout["status"] = "Settled"
        bout["settledAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        return bout

    def get_all_bouts(self) -> List[Dict[str, Any]]:
        return list(self.bouts.values())

    def get_compliance_matrix(self) -> Dict[str, Any]:
        return self.jurisdiction_compliance_rules

# Singleton instance
settlement_engine = MMAPurseSettlementEngine()
