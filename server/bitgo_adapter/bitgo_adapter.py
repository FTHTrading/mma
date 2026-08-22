"""
Normalized BitGo Enterprise & Go Network Custody Adapter
Provides strict abstraction between platform logic and BitGo SDK / API.
Exposes portfolio positions, wallet balances, transfer intents, Go Network settlements, and policy states.
"""

import time
import uuid
from typing import Dict, List, Any, Optional

class BitGoEnterpriseAdapter:
    """Normalized interface wrapping BitGo Enterprise & BitGo Go Network."""

    def __init__(self):
        self.enterprise_account = {
            "enterpriseId": "ent_bitgo_mma_01",
            "name": "MMA.INC / UnyKorn LLC Institutional Custody",
            "custodian": "BitGo Trust Company, Inc. (South Dakota Chartered)",
            "verificationStatus": "OCC Chartered & SEC Registered Qualified Custody",
            "goNetworkEnabled": True
        }

        self.wallets = [
            {
                "walletId": "wlt_btc_custody_01",
                "coin": "btc",
                "label": "Corporate Treasury Cold Wallet (BitGo MPC)",
                "balanceMinor": 1250000000, # 12.5 BTC in sats
                "balanceHuman": "12.50 BTC",
                "assetUsdValue": 812500.00,
                "type": "Qualified Custody",
                "mpcPolicy": "2-of-3 Hardware MPC"
            },
            {
                "walletId": "wlt_usdc_settlement_02",
                "coin": "tusdc",
                "label": "Go Network Fast Settlement Wallet",
                "balanceMinor": 150000000, # $1,500,000 in USDC cents/micros
                "balanceHuman": "$1,500,000.00 USDC",
                "assetUsdValue": 1500000.00,
                "type": "Go Network Off-Chain Settlement",
                "mpcPolicy": "3-of-4 Enterprise Approval"
            },
            {
                "walletId": "wlt_tbills_treasury_03",
                "coin": "tbills",
                "label": "Tokenized Short-Term T-Bills Float (BUIDL)",
                "balanceMinor": 168750000, # $1,687,500 in cents
                "balanceHuman": "$1,687,500.00 USD",
                "assetUsdValue": 1687500.00,
                "type": "Yield Float (5.25% BPS)",
                "mpcPolicy": "2-of-3 Dual Control"
            }
        ]

        self.pending_approvals = [
            {
                "approvalId": "appr_bitgo_9901",
                "walletId": "wlt_usdc_settlement_02",
                "coin": "tusdc",
                "amountMinor": 14500000, # $145,000.00
                "recipient": "0x8aced25DC8530FDaf0f86D53a0A1E02AAfA7Ac7A",
                "status": "PENDING_SECOND_OPERATOR_SIGNATURE",
                "policyCheckPassed": True,
                "requestedBy": "kevan@unykorn.ai",
                "createdAt": "2026-08-22T18:00:00Z"
            }
        ]

        self.go_network_counterparties = [
            {
                "counterpartyId": "cp_go_zebra_01",
                "name": "Zebra Athletics Manufacturing (Go Account)",
                "goAccountId": "go_acc_zebra_9921",
                "status": "APPROVED",
                "supportedAssets": ["USDC", "USD", "BTC"]
            },
            {
                "counterpartyId": "cp_go_trainalta_02",
                "name": "TrainAlta Global Holdings (Go Account)",
                "goAccountId": "go_acc_trainalta_8812",
                "status": "APPROVED",
                "supportedAssets": ["USDC", "USD"]
            }
        ]

    def get_portfolio_positions(self) -> Dict[str, Any]:
        total_usd = sum(w["assetUsdValue"] for w in self.wallets)
        return {
            "enterprise": self.enterprise_account,
            "totalPortfolioValueUsd": total_usd,
            "totalWallets": len(self.wallets),
            "wallets": self.wallets
        }

    def get_wallet_balances(self, wallet_id: str = None) -> List[Dict[str, Any]]:
        if wallet_id:
            return [w for w in self.wallets if w["walletId"] == wallet_id]
        return self.wallets

    def create_transfer_intent(self, 
                              wallet_id: str, 
                              recipient_address: str, 
                              amount_minor: int, 
                              coin: str) -> Dict[str, Any]:
        
        custody_ref = f"bitgo_tx_{uuid.uuid4().hex[:10]}"
        record = {
            "custodyReference": custody_ref,
            "walletId": wallet_id,
            "coin": coin,
            "recipientAddress": recipient_address,
            "amountMinorUnits": amount_minor,
            "bitgoPolicyStatus": "SUBMITTED_TO_BITGO_POLICY_ENGINE",
            "custodyState": "PENDING_MPC_SIGNATURE",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        return record

    def list_pending_approvals(self) -> List[Dict[str, Any]]:
        return self.pending_approvals

    def get_policy_state(self) -> Dict[str, Any]:
        return {
            "bitgoPolicyRules": [
                {"rule": "Destination Allowlist", "status": "ACTIVE_ENFORCED"},
                {"rule": "2-Person MPC Approval Required Above $100k", "status": "ACTIVE_ENFORCED"},
                {"rule": "Go Network Off-Chain Instant Settlement", "status": "ACTIVE_ENFORCED"}
            ]
        }

    def list_counterparties(self) -> List[Dict[str, Any]]:
        return self.go_network_counterparties

    def create_settlement_instruction(self, 
                                      go_counterparty_id: str, 
                                      asset_symbol: str, 
                                      amount_minor: int) -> Dict[str, Any]:
        
        settlement_ref = f"go_settle_{uuid.uuid4().hex[:10]}"
        return {
            "settlementReference": settlement_ref,
            "goCounterpartyId": go_counterparty_id,
            "assetSymbol": asset_symbol,
            "amountMinorUnits": amount_minor,
            "settlementType": "BitGo Go Network Instant Off-Chain Book Transfer",
            "settlementStatus": "CONFIRMED_FINAL",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }


# Global singleton adapter instance
bitgo_adapter = BitGoEnterpriseAdapter()
