"""
Unykorn.ai MMA Purse Settlement & Multi-Jurisdiction Compliance Engine
Manages fight cards, programmable split distributions, athletic commission reporting,
and automated tax withholding across US, Japan, Thailand, Singapore, South Korea, Greater China, and Middle East.
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
                "name": "United States (North America Hub)",
                "promotions": ["UFC", "PFL", "Bellator MMA", "LFA", "BKFC"],
                "regulators": ["SEC", "CFTC", "FinCEN", "Nevada State Athletic Commission (NSAC)", "California State Athletic Commission (CSAC)", "NYSAC"],
                "taxForms": "Form 1099-MISC (Domestic) / Form 1042-S (Foreign National)",
                "withholdingTaxBps": 1000, # 10.0% statutory state/federal purse withholding
                "settlementRail": "BitGo Trust Bank Custody (USD Wire / USDC / USD1)",
                "coldStorageMandate": "Standard OCC Chartered Qualified Trust",
                "tokenLegality": "Fully compliant institutional stablecoins & SEC Reg D/S rails"
            },
            "JP": {
                "name": "Japan (East Asia Combat Capital)",
                "promotions": ["RIZIN Fighting Federation", "K-1 World GP", "RISE Kickboxing", "DEEP / DEEP JEWELS", "Pancrase", "Shooto", "Pride FC Legacy Archive"],
                "regulators": ["JFSA (Japan Financial Services Agency)", "JVCEA (Japan Virtual and Crypto Assets Exchange Association)", "JMOC (Japan Martial Arts Oversight Commission)"],
                "taxForms": "National Tax Agency (NTA) Article 161 Foreign Athlete Withholding (20.42%)",
                "withholdingTaxBps": 2042, # 20.42%
                "settlementRail": "BitGo MPC / Licensed Electronic Payment Instrument (EPI / JPYC & USD1)",
                "coldStorageMandate": "Strict 95% Offline Cold Storage Mandate (Payment Services Act Art. 63-11)",
                "tokenLegality": "JVCEA Whitelisted Tokens, JPYC & Regulated EPI only"
            },
            "SG": {
                "name": "Singapore (APAC Financial & Combat Headquarters)",
                "promotions": ["ONE Championship", "Matrix Fight Night (MFN Asia)", "WBC Muaythai Asia"],
                "regulators": ["Monetary Authority of Singapore (MAS - Payment Services Act)"],
                "taxForms": "IRAS Non-Resident Professional Withholding (15.0% or 24.0%)",
                "withholdingTaxBps": 1500, # 15.0%
                "settlementRail": "BitGo Singapore Pte Ltd (Major Payment Institution License) Global Hub",
                "coldStorageMandate": "MAS PSN01 / PSN02 Segregated Treasury Vaults",
                "tokenLegality": "Standard Payment Token (DPT) compliant rails & USD1 instant settlement"
            },
            "TH": {
                "name": "Thailand (Muay Thai & Striking Capital)",
                "promotions": ["ONE Friday Fights (Lumpinee Stadium)", "Rajadamnern World Series (RWS)", "Fairtex Fight", "Thai Fight"],
                "regulators": ["Sports Authority of Thailand (SAT - Boxing Act B.E. 2542)", "Thai SEC", "Bank of Thailand (BOT)"],
                "taxForms": "Revenue Department Form P.N.D. 53 (15% Foreign Entertainer/Athlete Withholding)",
                "withholdingTaxBps": 1500, # 15.0%
                "settlementRail": "Regulated Thai VASP Bridge -> THB Instant PromptPay / BAHTNET",
                "coldStorageMandate": "Bank of Thailand Payment Gateway Segregation",
                "tokenLegality": "Programmatic THB conversion for local purses; USD1 for foreign camps"
            },
            "KR": {
                "name": "South Korea (East Asia MMA Hub)",
                "promotions": ["ROAD FC", "Black Combat", "Z-Fight Night (ZFN)", "Angel's Fighting Championship (AFC)"],
                "regulators": ["FSC (Financial Services Commission Korea)", "FIU (Financial Intelligence Unit)", "KOC MMA Commission"],
                "taxForms": "National Tax Service (NTS) Foreign Entertainer Tax (22.0% incl. local surtax)",
                "withholdingTaxBps": 2200, # 22.0%
                "settlementRail": "BitGo Korea / VerifyVASP Travel Rule Rail -> KRW / USD1 Instant Settlement",
                "coldStorageMandate": "FSC Virtual Asset User Protection Act Compliance",
                "tokenLegality": "Travel Rule compliant VASP transfers & KRW fiat gateways"
            },
            "CN": {
                "name": "Greater China & Hong Kong",
                "promotions": ["Wu Lin Feng (WLF)", "JCK MMA (Night of Cage)", "CKF (Chinese Kung Fu)", "ONE Championship China"],
                "regulators": ["SFC Hong Kong (VASP Regulatory Framework)", "General Administration of Sport of China"],
                "taxForms": "State Taxation Administration / HK Inland Revenue Dept (15.0% Withholding)",
                "withholdingTaxBps": 1500, # 15.0%
                "settlementRail": "SFC-Licensed Digital Asset Custodian Bridge & Zebra Matting PO Escrow",
                "coldStorageMandate": "SFC AMLO Regulation 98% Cold Storage Standard",
                "tokenLegality": "SFC VATP Licensed Platforms & Institutional HKD/USD Stablecoins"
            },
            "UAE": {
                "name": "United Arab Emirates & Middle East",
                "promotions": ["PFL MENA (Riyadh / Dubai)", "BRAVE Combat Federation (Bahrain)", "UFC Fight Island (Abu Dhabi)", "UAE Warriors"],
                "regulators": ["VARA (Dubai Virtual Assets Regulatory Authority)", "ADGM FSRA (Abu Dhabi)", "UAE General Sports Authority"],
                "taxForms": "Zero Personal Income Tax / Sovereign Financial Hub Gateway",
                "withholdingTaxBps": 0, # 0.0% tax-free fight purses
                "settlementRail": "VARA-Compliant Virtual Asset Infrastructure & Sovereign Syndication",
                "coldStorageMandate": "VARA Full Market Product (FMP) Custody & Cybersecurity Standards",
                "tokenLegality": "Full virtual asset distribution authorization & USD1 sovereign sponsorship escrow"
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
                {"recipient": "0x3333444455556666777788889999000011112222", "name": "Fighter Net Payout (JPYC)", "percentageBps": 6458, "role": "Fighter"},
                {"recipient": "0x5555666677778888999900001111222233334444", "name": "American Top Team Gym", "percentageBps": 1000, "role": "Corner/Trainer"},
                {"recipient": "0x6666777788889999000011112222333344445555", "name": "Rizin Management Corp", "percentageBps": 500, "role": "Management"},
                {"recipient": "0x7777888899990000111122223333444455556666", "name": "JFSA / NTA Withholding Tax Account (20.42%)", "percentageBps": 2042, "role": "AthleticCommission"}
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

        # 4. ROAD FC / Black Combat Seoul Championship (South Korea Jurisdiction)
        self.create_bout(
            bout_id="BOUT-SEL-2026-004",
            event_name="MMA.INC x ROAD FC Korea Championship",
            fighter_a_name="Soo Chul Kim",
            fighter_a_wallet="0xKR11223344556677889900112233445566778899",
            fighter_b_name="Jung Young Lee",
            fighter_b_wallet="0xKR99887766554433221100998877665544332211",
            jurisdiction="KR",
            base_purse_minor=25000000, # $250,000.00
            win_bonus_minor=10000000,  # $100,000.00
            settlement_token="USD1",
            splits=[
                {"recipient": "0xKR11223344556677889900112233445566778899", "name": "Fighter Net Payout (USD1)", "percentageBps": 6800, "role": "Fighter"},
                {"recipient": "0xKR22334455667788990011223344556677889900", "name": "Team MOB Training Camp", "percentageBps": 1000, "role": "Corner/Trainer"},
                {"recipient": "0xKR33445566778899001122334455667788990011", "name": "ROAD FC Management", "percentageBps": 0, "role": "Management"},
                {"recipient": "0xKR44556677889900112233445566778899001122", "name": "Korea National Tax Service Withholding", "percentageBps": 2200, "role": "AthleticCommission"}
            ]
        )

        # 5. ONE Championship Singapore World Title (Singapore Jurisdiction)
        self.create_bout(
            bout_id="BOUT-SIN-2026-005",
            event_name="ONE Championship x MMA.INC Singapore World Grand Prix",
            fighter_a_name="Christian Lee",
            fighter_a_wallet="0xSG11112222333344445555666677778888999900",
            fighter_b_name="Saygid Izagakhmaev",
            fighter_b_wallet="0xSG22223333444455556666777788889999000011",
            jurisdiction="SG",
            base_purse_minor=75000000, # $750,000.00
            win_bonus_minor=25000000,  # $250,000.00
            settlement_token="USD1",
            splits=[
                {"recipient": "0xSG11112222333344445555666677778888999900", "name": "Fighter Net Payout (BitGo SG)", "percentageBps": 7500, "role": "Fighter"},
                {"recipient": "0xSG33334444555566667777888899990000111122", "name": "Evolve MMA Camp", "percentageBps": 1000, "role": "Corner/Trainer"},
                {"recipient": "0xSG44445555666677778888999900001111222233", "name": "ONE Championship Escrow", "percentageBps": 0, "role": "Management"},
                {"recipient": "0xSG55556666777788889999000011112222333344", "name": "IRAS Singapore Withholding", "percentageBps": 1500, "role": "AthleticCommission"}
            ]
        )

    def create_bout(self, bout_id: str, event_name: str, fighter_a_name: str, fighter_a_wallet: str,
                    fighter_b_name: str, fighter_b_wallet: str, jurisdiction: str,
                    base_purse_minor: int, win_bonus_minor: int, settlement_token: str,
                    splits: List[Dict[str, Any]]) -> Dict[str, Any]:
        
        # Verify BPS sum
        total_bps = sum(s["percentageBps"] for s in splits)
        if total_bps > 10000:
            raise ValueError(f"Splits exceeds 10,000 BPS (got {total_bps})")
        
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
            "createdAt": int(time.time())
        }
        
        self.bouts[bout_id] = record
        return record

    def get_bout(self, bout_id: str) -> Optional[Dict[str, Any]]:
        return self.bouts.get(bout_id)

    def get_all_bouts(self) -> List[Dict[str, Any]]:
        return list(self.bouts.values())

    def get_compliance_matrix(self) -> Dict[str, Any]:

        return self.jurisdiction_compliance_rules

    def execute_settlement(self, bout_id: str, winner_name: str, winner_wallet: str) -> Dict[str, Any]:
        bout = self.bouts.get(bout_id)
        if not bout:
            raise ValueError(f"Bout {bout_id} not found")
        
        if bout["isSettled"]:
            return {"status": "ALREADY_SETTLED", "bout": bout}
        
        total_payout_usd = bout["basePurseUsd"] + bout["winBonusUsd"]
        
        # Execute BitGo Vault / Unykorn Rail distributions
        settlement_results = []
        for split in bout["splits"]:
            share_usd = total_payout_usd * (split["percentageBps"] / 10000.0)
            tx = bitgo_service.execute_transfer(
                vault_key="us_operating_treasury" if bout["jurisdiction"] == "US" else "apac_singapore_treasury",
                token=bout["settlementToken"],
                recipient_address=split["recipient"],
                amount_usd=share_usd
            )
            settlement_results.append({
                "recipientName": split["name"],
                "role": split["role"],
                "amountUsd": share_usd,
                "percentageBps": split["percentageBps"],
                "txHash": tx["txHash"]
            })
            
        bout["isSettled"] = True
        bout["status"] = "Settled"
        bout["winner"] = winner_name
        bout["settledAt"] = int(time.time())
        bout["settlementResults"] = settlement_results
        
        return {
            "status": "SUCCESS",
            "boutId": bout_id,
            "totalDistributedUsd": total_payout_usd,
            "settlements": settlement_results
        }

# Singleton instance
settlement_engine = MMAPurseSettlementEngine()
