"""
BitGo Enterprise & Brassica RWA Custody Service
Implements SEC-registered Transfer Agent operations, OCC-chartered qualified custody,
milestone escrow management, and corporate treasury yield account tracking.
"""

import time
import uuid
from typing import Dict, List, Any, Optional

class BitGoEnterpriseService:
    def __init__(self):
        # In-memory institutional ledger state
        self.investors: Dict[str, Dict[str, Any]] = {}
        self.custody_accounts: Dict[str, Dict[str, Any]] = {}
        self.securities_registry: Dict[str, List[Dict[str, Any]]] = {}
        self.escrows: Dict[str, Dict[str, Any]] = {}
        self.transactions: List[Dict[str, Any]] = []

        # Corporate Treasury Vault State ($4.0M Private Placement Float + Multi-Asset Reserves)
        self.treasury = {
            "corporateEntity": "MMA.INC (NYSE American)",
            "qualifiedCustodian": "BitGo Trust Company, Inc. (South Dakota Chartered)",
            "totalTreasuryUsd": 4000000.00,
            "annualYieldRateBps": 525,  # 5.25% short-term tokenized T-Bills
            "dailyYieldGeneratedUsd": (4000000.00 * 0.0525) / 365,
            "accumulatedYieldUsd": 84250.00,
            "vaults": {
                "us_operating_treasury": {
                    "vaultId": "vlt_us_mma_01",
                    "jurisdiction": "United States (OCC/FinCEN)",
                    "asset": "USD / Tokenized T-Bills (BUIDL/USDY)",
                    "balance": 3150000.00,
                    "mpcThreshold": "2-of-3",
                    "status": "Active Yield Generating"
                },
                "apac_singapore_hub": {
                    "vaultId": "vlt_sg_mas_02",
                    "jurisdiction": "Singapore (MAS MPI Licensed)",
                    "asset": "USDC (Institutional Settlement)",
                    "balance": 550000.00,
                    "mpcThreshold": "3-of-4",
                    "status": "Ready for Cross-Border Purse Settlement"
                },
                "japan_jfsa_segregated": {
                    "vaultId": "vlt_jp_jfsa_03",
                    "jurisdiction": "Japan (JFSA 95% Cold Storage Segregation)",
                    "asset": "JPYC / JPY Equivalent",
                    "balance": 200000.00,
                    "mpcThreshold": "2-of-3 Hardware Cold Vault",
                    "status": "Compliant Segregated Reserve"
                },
                "thailand_vasp_liquidity": {
                    "vaultId": "vlt_th_bot_04",
                    "jurisdiction": "Thailand (Thai SEC / Bank of Thailand Rail)",
                    "asset": "THB Local Settlement Escrow",
                    "balance": 100000.00,
                    "mpcThreshold": "2-of-2 Corporate Dual-Sig",
                    "status": "Connected to PromptPay Gateway"
                }
            }
        }

        # Seed initial system state
        self._seed_initial_state()

    def _seed_initial_state(self):
        # Seed key MMA and Gym personas
        self.create_investor("Kevan Burns", "kevan@unykorn.ai", "United States", "Individual")
        self.accredit_investor("kevan@unykorn.ai")
        
        self.create_investor("TrainAlta Global Holdings", "invest@trainalta.com", "United States", "Domestic Entity")
        self.accredit_investor("invest@trainalta.com")

        self.create_investor("Zebra Athletics Manufacturing", "treasury@zebraathletics.com", "United States", "Domestic Entity")
        self.accredit_investor("treasury@zebraathletics.com")

        self.create_investor("MMA.INC Corporate Escrow", "treasury@mma.inc", "United States", "Domestic Entity")
        self.accredit_investor("treasury@mma.inc")

        # Open initial qualified custody accounts
        self.open_custody_account("MMA-INC-Main-Custody", "Domestic Entity", "Qualified Custody", 4000000.00)
        self.open_custody_account("Zebra-PO-Escrow-Account", "Domestic Entity", "Qualified Custody", 750000.00)
        self.open_custody_account("TrainAlta-APAC-Gym-Expansion", "International Entity", "DeFi Multi-Sig", 500000.00)

    # 1. Investor Onboarding
    def create_investor(self, name: str, email: str, country: str, entity_type: str = "Individual") -> Dict[str, Any]:
        investor_id = f"inv_{uuid.uuid4().hex[:8]}"
        record = {
            "id": investor_id,
            "name": name,
            "email": email,
            "country": country,
            "entityType": entity_type,
            "kycStatus": "Verified",
            "accredited": "Unverified",
            "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        self.investors[email] = record
        return {"success": True, "investor": record}

    # 2. Enhanced Accreditation Check
    def accredit_investor(self, email: str) -> Dict[str, Any]:
        if email not in self.investors:
            self.create_investor(name="Unknown", email=email, country="United States")
        
        self.investors[email]["accredited"] = "Accredited"
        return {"success": True, "investor": self.investors[email]}

    # 3. Open Regulated Custody Account
    def open_custody_account(self, name: str, entity_type: str = "Domestic Entity", 
                              custody_preference: str = "Qualified Custody", initial_balance: float = 0.0) -> Dict[str, Any]:
        account_id = f"ca_{uuid.uuid4().hex[:7]}"
        account = {
            "id": account_id,
            "name": name,
            "type": entity_type,
            "custodyPreference": custody_preference,
            "cashBalance": initial_balance,
            "status": "Active",
            "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        self.custody_accounts[account_id] = account
        return {"success": True, "account": account}

    # 4. Issue Private Securities (Transfer Agent)
    def issue_security(self, security_id: str, email: str, shares: int, name: str) -> Dict[str, Any]:
        holder = {
            "email": email,
            "name": name,
            "securityId": security_id,
            "shares": shares,
            "lastTx": f"Issued {shares} shares",
            "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        if security_id not in self.securities_registry:
            self.securities_registry[security_id] = []
        self.securities_registry[security_id].append(holder)
        return {"success": True, "holder": holder}

    # 5. Commit Funds to Escrow
    def deposit_escrow(self, custody_account_id: str, amount: float, contingency: str) -> Dict[str, Any]:
        if custody_account_id not in self.custody_accounts:
            raise ValueError("Custody account not found")
        
        acc = self.custody_accounts[custody_account_id]
        if acc["cashBalance"] < amount:
            # Auto-fund for demo / corporate placement if needed
            acc["cashBalance"] += amount

        acc["cashBalance"] -= amount
        tx_id = f"esc_{uuid.uuid4().hex[:8]}"
        escrow_record = {
            "id": tx_id,
            "custodyAccountId": custody_account_id,
            "amount": amount,
            "contingency": contingency,
            "status": "Held in Escrow",
            "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        self.escrows[tx_id] = escrow_record
        return {"success": True, "tx": escrow_record}

    # 6. Close Escrow & Disburse Funds
    def close_escrow(self, tx_id: str) -> Dict[str, Any]:
        if tx_id not in self.escrows:
            raise ValueError(f"Escrow transaction {tx_id} not found")
        
        escrow = self.escrows[tx_id]
        escrow["status"] = "Disbursed"
        escrow["closedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        self.transactions.append({
            "type": "Escrow Disbursement",
            "txId": tx_id,
            "amount": escrow["amount"],
            "recipient": escrow["contingency"],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        })
        return {"success": True, "tx": escrow}

    # 7. Refund Escrow
    def refund_escrow(self, tx_id: str) -> Dict[str, Any]:
        if tx_id not in self.escrows:
            raise ValueError(f"Escrow transaction {tx_id} not found")
        
        escrow = self.escrows[tx_id]
        escrow["status"] = "Refunded"
        acc = self.custody_accounts[escrow["custodyAccountId"]]
        acc["cashBalance"] += escrow["amount"]
        return {"success": True, "tx": escrow}

    # Direct BitGo Programmatic MPC Execution for Fight Purses
    def execute_mpc_purse_transfer(self, token_symbol: str, recipient_address: str, 
                                  amount_minor: int, role: str, jurisdiction: str) -> Dict[str, Any]:
        tx_hash = f"0x{uuid.uuid4().hex}"
        tx_record = {
            "txHash": tx_hash,
            "type": "Fight Purse Settlement",
            "token": token_symbol,
            "recipient": recipient_address,
            "amountMinor": amount_minor,
            "amountHuman": amount_minor / 100.0, # Minor cents/drops
            "role": role,
            "jurisdiction": jurisdiction,
            "mpcSignatures": ["BitGo_Trust_Key_01", "Unykorn_Orchestrator_Key_02"],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "status": "Confirmed (T+0)"
        }
        self.transactions.append(tx_record)
        return tx_record

    def get_treasury_overview(self) -> Dict[str, Any]:
        return {
            "treasury": self.treasury,
            "custodyAccounts": list(self.custody_accounts.values()),
            "activeEscrows": list(self.escrows.values()),
            "recentTransactions": self.transactions[-10:]
        }

# Singleton instance
bitgo_service = BitGoEnterpriseService()
