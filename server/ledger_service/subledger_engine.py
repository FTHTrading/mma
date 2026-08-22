"""
Integer Double-Entry Subledger Engine
Enforces strict append-only double-entry bookkeeping using integer minor units ONLY.
No floating point values allowed across accounting boundaries.
"""

import time
import uuid
from typing import Dict, List, Any

class DoubleEntryJournalEntry:
    """Represents an immutable, balanced double-entry subledger journal posting."""
    
    def __init__(self, description: str, reference_id: str, asset_symbol: str):
        self.journal_id = f"jnl_{uuid.uuid4().hex[:12]}"
        self.timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.description = description
        self.reference_id = reference_id  # Link to intent_id
        self.asset_symbol = asset_symbol.upper()
        self.postings: List[Dict[str, Any]] = []
        self.is_posted = False

    def add_debit(self, account_name: str, amount_minor_units: int):
        if not isinstance(amount_minor_units, int) or amount_minor_units <= 0:
            raise ValueError(f"Debit amount must be positive integer minor units, got: {amount_minor_units}")
        self.postings.append({
            "type": "DEBIT",
            "account": account_name,
            "amountMinorUnits": amount_minor_units
        })

    def add_credit(self, account_name: str, amount_minor_units: int):
        if not isinstance(amount_minor_units, int) or amount_minor_units <= 0:
            raise ValueError(f"Credit amount must be positive integer minor units, got: {amount_minor_units}")
        self.postings.append({
            "type": "CREDIT",
            "account": account_name,
            "amountMinorUnits": amount_minor_units
        })

    def validate_balanced(self) -> bool:
        total_debit = sum(p["amountMinorUnits"] for p in self.postings if p["type"] == "DEBIT")
        total_credit = sum(p["amountMinorUnits"] for p in self.postings if p["type"] == "CREDIT")
        if total_debit != total_credit:
            raise ValueError(f"Unbalanced Journal Entry! Total Debits: {total_debit} != Total Credits: {total_credit}")
        return True

    def to_dict(self) -> Dict[str, Any]:
        total_debit = sum(p["amountMinorUnits"] for p in self.postings if p["type"] == "DEBIT")
        return {
            "journalId": self.journal_id,
            "timestamp": self.timestamp,
            "description": self.description,
            "referenceId": self.reference_id,
            "assetSymbol": self.asset_symbol,
            "postings": self.postings,
            "totalMinorUnits": total_debit,
            "isPosted": self.is_posted
        }


class IntegerSubledgerEngine:
    """Subledger maintaining append-only journal and account balances."""
    
    def __init__(self):
        self.journal: List[Dict[str, Any]] = []
        self.accounts: Dict[str, Dict[str, Any]] = {
            "Asset:Custody:BitGo": {"type": "ASSET", "balanceMinor": 400000000},      # $4,000,000.00 in cents
            "Asset:Bank:Fiat": {"type": "ASSET", "balanceMinor": 245000000},          # $2,450,000.00 in cents
            "Liability:ClientDeposit": {"type": "LIABILITY", "balanceMinor": 500000000}, # $5,000,000.00 in cents
            "Equity:TreasuryFloat": {"type": "EQUITY", "balanceMinor": 145000000},     # $1,450,000.00 in cents
            "Revenue:Fee": {"type": "REVENUE", "balanceMinor": 0}
        }
        self._seed_initial_journal()

    def _seed_initial_journal(self):
        entry = DoubleEntryJournalEntry("Initial Treasury Float Allocation", "ref_init_001", "USD_CENT")
        entry.add_debit("Asset:Custody:BitGo", 400000000)
        entry.add_credit("Equity:TreasuryFloat", 400000000)
        self.post_journal_entry(entry)

    def post_journal_entry(self, entry: DoubleEntryJournalEntry) -> Dict[str, Any]:
        entry.validate_balanced()
        
        # Apply postings to account balances
        for p in entry.postings:
            acc_name = p["account"]
            if acc_name not in self.accounts:
                self.accounts[acc_name] = {"type": "GENERAL", "balanceMinor": 0}
            
            acc = self.accounts[acc_name]
            amt = p["amountMinorUnits"]
            
            # ASSET & EXPENSE: Debit increases (+), Credit decreases (-)
            # LIABILITY, EQUITY, REVENUE: Credit increases (+), Debit decreases (-)
            if acc["type"] in ["ASSET", "EXPENSE"]:
                if p["type"] == "DEBIT":
                    acc["balanceMinor"] += amt
                else:
                    acc["balanceMinor"] -= amt
            else:
                if p["type"] == "CREDIT":
                    acc["balanceMinor"] += amt
                else:
                    acc["balanceMinor"] -= amt
                    
        entry.is_posted = True
        record = entry.to_dict()
        self.journal.append(record)
        return record

    def get_account_balances(self) -> Dict[str, Any]:
        return {
            "accounts": self.accounts,
            "totalJournalEntries": len(self.journal)
        }

    def get_journal(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self.journal[-limit:]


# Global singleton subledger instance
subledger_engine = IntegerSubledgerEngine()
