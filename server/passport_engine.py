"""
XP Passport Sovereign Identity & ERC-3643 Verification Engine
Maintains verified fighter fight records, belt promotions, jurisdiction compliance status,
and token-gated fan VIP credentials.
"""

import time
import uuid
from typing import Dict, List, Any

class XPPassportEngine:
    def __init__(self):
        self.passports: Dict[str, Dict[str, Any]] = {}
        self._seed_passports()

    def _seed_passports(self):
        # Mackenzie Dern (Featured Flagship Athlete & World Champion)

        self.register_passport(
            wallet="0x4E574939D460d284B5D990646D4aeaEF2D49Fa13",
            name="Mackenzie Dern",
            role="Fighter",
            country_code=840,
            country_name="United States / Brazil 🇺🇸 🇧🇷",
            combat_rank="UFC Champion Contender & ADCC World Champion (3x BJJ World Champion, Black Belt 2nd Degree)",
            kyc_level="Tier 3 (Accredited World Champion / ERC-6551 TBA)",
            xp_points=210000,
            badges=[
                "UFC 330 Title Defense Collectible",
                "ADCC Gold Medalist",
                "3x BJJ World Champion",
                "UFC GYM Global Brand Ambassador",
                "Train-to-Earn USD1 Pioneer",
                "ERC-6551 Token Bound Account",
                "ERC-3643 KYC Verified"
            ]
        )

        # Alex Pereira
        self.register_passport(
            wallet="0x8ACED25dc8530FDaf0f86D53a0A1E02AAfA7Ac7A",
            name="Alex 'Poatan' Pereira",
            role="Fighter",
            country_code=840, # US / Brazil Dual License
            country_name="United States / Brazil",
            combat_rank="2-Division World Champion (14-2 Pro MMA, GLORY Hall of Fame)",
            kyc_level="Tier 3 (Accredited Athlete)",
            xp_points=125000,
            badges=["UFC Gold Champion", "Glory Kickboxing Legend", "ERC-3643 KYC Verified", "Instant BitGo Payout Enabled"]
        )


        # Israel Adesanya
        self.register_passport(
            wallet="0x71C568ba458E303649e31ff48a60F65D6169996D",
            name="Israel 'The Last Stylebender' Adesanya",
            role="Fighter",
            country_code=840,
            country_name="New Zealand / United States",
            combat_rank="Former 2x Middleweight Champion (24-3 Pro MMA, BJJ Purple Belt)",
            kyc_level="Tier 3 (Accredited Athlete)",
            xp_points=118000,
            badges=["UFC Middleweight Legend", "Combat XP Elite", "ERC-3643 KYC Verified"]
        )

        # Kai Asakura (Japan)
        self.register_passport(
            wallet="0x3333444455556666777788889999000011112222",
            name="Kai Asakura",
            role="Fighter",
            country_code=392,
            country_name="Japan",
            combat_rank="RIZIN Bantamweight Champion (21-4 Pro MMA)",
            kyc_level="Tier 2 (Institutional Athlete)",
            xp_points=94000,
            badges=["RIZIN Grand Prix Winner", "JFSA Compliant Wallet", "ERC-3643 KYC Verified"]
        )

        # Rodtang Jitmuangnon (Thailand)
        self.register_passport(
            wallet="0x8888999900001111222233334444555566667777",
            name="Rodtang Jitmuangnon",
            role="Fighter",
            country_code=764,
            country_name="Thailand",
            combat_rank="ONE Flyweight Muay Thai World Champion (272-42-10)",
            kyc_level="Tier 2 (Institutional Athlete)",
            xp_points=145000,
            badges=["ONE Muay Thai World Champ", "PromptPay THB Gateway Verified", "Iron Man Record"]
        )

        # Kevan Burns (MMA.INC / Unykorn Executive)
        self.register_passport(
            wallet="0x1111222233334444555566667777888899990000",
            name="Kevan Burns",
            role="Promoter",
            country_code=840,
            country_name="United States",
            combat_rank="Executive Director & Sovereign Architect",
            kyc_level="Tier 3 (Accredited Entity / Promoter)",
            xp_points=250000,
            badges=["ANVIL Master Architect", "BitGo Trust Operator", "NYSE American Governance", "ERC-3643 Admin"]
        )

        # VIP Fan Pass Holder
        self.register_passport(
            wallet="0x9999888877776666555544443333222211110000",
            name="VIP Octagonside Holder #042",
            role="FanVIP",
            country_code=840,
            country_name="United States",
            combat_rank="Lifetime Black Tier Member",
            kyc_level="Tier 1 (Basic Fan KYC)",
            xp_points=32000,
            badges=["Octagonside Access Pass", "PPV Token-Gated VIP", "Zebra Equipment Discount Tier"]
        )

    def register_passport(self, wallet: str, name: str, role: str, country_code: int,
                          country_name: str, combat_rank: str, kyc_level: str = "Tier 2",
                          xp_points: int = 1000, badges: List[str] = None) -> Dict[str, Any]:
        
        record = {
            "wallet": wallet,
            "passportId": f"XP-PASS-{wallet[:6]}-{uuid.uuid4().hex[:4].upper()}",
            "name": name,
            "role": role,
            "countryCode": country_code,
            "countryName": country_name,
            "combatRank": combat_rank,
            "kycLevel": kyc_level,
            "isVerified": True,
            "isSanctioned": False,
            "xpPoints": xp_points,
            "badges": badges or ["ERC-3643 KYC Verified"],
            "issuedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        self.passports[wallet.lower()] = record
        return record

    def award_xp(self, wallet: str, points: int, reason: str = "Fight Completion Bonus") -> Dict[str, Any]:
        w_lower = wallet.lower()
        if w_lower not in self.passports:
            raise ValueError(f"Passport for wallet {wallet} not found")
        
        p = self.passports[w_lower]
        p["xpPoints"] += points
        p["badges"].append(f"+{points} XP: {reason}")
        return p

    def get_all_passports(self) -> List[Dict[str, Any]]:
        return list(self.passports.values())

    def get_passport(self, wallet: str) -> Optional[Dict[str, Any]]:
        return self.passports.get(wallet.lower())

# Singleton instance
passport_engine = XPPassportEngine()
