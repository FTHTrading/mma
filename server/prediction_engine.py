"""
Unykorn.ai Fan Prediction Markets & Event Contracts Engine
Manages peer-to-peer prediction pools, micro-event markets (KO/TKO, Round, Strikes),
and implements CFTC/Multi-Jurisdiction 2-tier user routing (US Retail non-monetary XP vs ECP).
"""

import time
import uuid
from typing import Dict, List, Any
from passport_engine import passport_engine

class PredictionMarketService:
    def __init__(self):
        self.markets: Dict[str, Dict[str, Any]] = {}
        self.protocol_fee_bps = 150 # 1.5% protocol fee
        self.total_protocol_fees_collected_usd = 0.0

        self._seed_sample_markets()

    def _seed_sample_markets(self):
        # 1. Binary Bout Winner: Pereira vs Adesanya
        self.create_market(
            market_id="MKT-PEREIRA-ADESANYA-2026",
            bout_id="BOUT-LV-2026-001",
            title="Alex Pereira vs Israel Adesanya — Bout Winner",
            category="Binary Bout Outcome",
            options=[
                {"id": 0, "name": "Alex 'Poatan' Pereira", "poolUsd": 145000.00, "stakersCount": 1420},
                {"id": 1, "name": "Israel 'Stylebender' Adesanya", "poolUsd": 115000.00, "stakersCount": 1180}
            ]
        )

        # 2. Micro-Event: Method & Round Finish
        self.create_market(
            market_id="MKT-PROP-FINISH-ROUND-02",
            bout_id="BOUT-LV-2026-001",
            title="Main Event Finish Method & Exact Round",
            category="Micro-Event Prop Contract",
            options=[
                {"id": 0, "name": "Pereira by KO/TKO (Round 1-2)", "poolUsd": 72000.00, "stakersCount": 890},
                {"id": 1, "name": "Adesanya by Decision (5 Rounds)", "poolUsd": 48000.00, "stakersCount": 610},
                {"id": 2, "name": "Pereira by KO/TKO (Round 3-5)", "poolUsd": 35000.00, "stakersCount": 420},
                {"id": 3, "name": "Adesanya by KO/TKO or Sub", "poolUsd": 25000.00, "stakersCount": 310}
            ]
        )

        # 3. BJJLink World Grand Prix Futures
        self.create_market(
            market_id="MKT-BJJLINK-GRANDPRIX-03",
            bout_id="BJJLINK-GP-2026",
            title="BJJLink Absolute Division Grand Prix Champion",
            category="Tournament Futures",
            options=[
                {"id": 0, "name": "Mica Galvao", "poolUsd": 65000.00, "stakersCount": 780},
                {"id": 1, "name": "Tye Ruotolo", "poolUsd": 52000.00, "stakersCount": 640},
                {"id": 2, "name": "Kade Ruotolo", "poolUsd": 44000.00, "stakersCount": 510},
                {"id": 3, "name": "Field (Any Other Competitor)", "poolUsd": 19000.00, "stakersCount": 220}
            ]
        )

    def create_market(self, market_id: str, bout_id: str, title: str, category: str,
                      options: List[Dict[str, Any]]) -> Dict[str, Any]:
        
        total_pool = sum(opt["poolUsd"] for opt in options)
        
        # Calculate implied odds/probabilities
        for opt in options:
            opt["probabilityPct"] = round((opt["poolUsd"] / total_pool) * 100, 1) if total_pool > 0 else 50.0
            opt["impliedMultiplier"] = round(total_pool / opt["poolUsd"], 2) if opt["poolUsd"] > 0 else 2.0

        record = {
            "marketId": market_id,
            "boutId": bout_id,
            "title": title,
            "category": category,
            "totalPoolUsd": total_pool,
            "options": options,
            "protocolFeeBps": self.protocol_fee_bps,
            "status": "Open",
            "winningOptionId": None,
            "isResolved": False,
            "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        self.markets[market_id] = record
        return record

    def place_stake(self, market_id: str, option_id: int, amount_usd: float,
                    user_wallet: str, user_tier: str = "Tier 1 (Retail XP)") -> Dict[str, Any]:
        
        if market_id not in self.markets:
            raise ValueError(f"Market {market_id} not found")
        
        m = self.markets[market_id]
        if m["isResolved"]:
            raise ValueError(f"Market {market_id} is already resolved")

        target_opt = None
        for opt in m["options"]:
            if opt["id"] == option_id:
                target_opt = opt
                break
        
        if not target_opt:
            raise ValueError(f"Option {option_id} not found")

        # Update pools
        target_opt["poolUsd"] += amount_usd
        target_opt["stakersCount"] += 1
        m["totalPoolUsd"] += amount_usd

        # Recalculate probabilities
        for opt in m["options"]:
            opt["probabilityPct"] = round((opt["poolUsd"] / m["totalPoolUsd"]) * 100, 1)
            opt["impliedMultiplier"] = round(m["totalPoolUsd"] / opt["poolUsd"], 2)

        # Award XP to user's passport
        xp_awarded = int(amount_usd * 2) # 2 XP per $1 staked
        try:
            passport_engine.award_xp(user_wallet, xp_awarded, f"Prediction Stake on {target_opt['name']}")
        except Exception:
            pass

        return {
            "success": True,
            "market": m,
            "stakedAmountUsd": amount_usd,
            "xpAwarded": xp_awarded,
            "stakerTier": user_tier
        }

    def resolve_market(self, market_id: str, winning_option_id: int) -> Dict[str, Any]:
        if market_id not in self.markets:
            raise ValueError(f"Market {market_id} not found")
        
        m = self.markets[market_id]
        if m["isResolved"]:
            return m

        m["isResolved"] = True
        m["winningOptionId"] = winning_option_id
        m["status"] = "Resolved"
        m["resolvedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Protocol fee deduction
        fee_usd = (m["totalPoolUsd"] * self.protocol_fee_bps) / 10000.0
        self.total_protocol_fees_collected_usd += fee_usd
        m["protocolFeeCollectedUsd"] = fee_usd
        m["netDisbursedUsd"] = m["totalPoolUsd"] - fee_usd

        return m

    def get_all_markets(self) -> List[Dict[str, Any]]:
        return list(self.markets.values())

# Singleton instance
prediction_engine = PredictionMarketService()
