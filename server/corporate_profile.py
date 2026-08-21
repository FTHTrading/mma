"""
Mixed Martial Arts Group Limited (NYSE American: MMA / MMA.INC)
Public Company Financial Profile & Strategic Advisory Intelligence
Incorporates $4.0M Strategic Private Placement (160% Premium), Donald Trump Jr. Strategic Advisory,
Conor McGregor Shareholder Alignment, UFC Gym Group BJJLink Admin+ Rollout, and USD1 Stablecoin Integration.
"""

from typing import Dict, Any

class CorporateFinancialProfile:
    def __init__(self):
        self.profile = {
            "entity": "Mixed Martial Arts Group Limited",
            "dba": "MMA.INC",
            "ticker": "MMA",
            "exchange": "NYSE American",
            "isin": "AU0000319329",
            "stockPriceUsd": 0.47,
            "sharesOutstanding": 25740000,
            "marketCapUsd": 12097800.00,
            "weekRange52": "$0.3456 - $3.07 USD",
            "regulatoryStatus": "Foreign Private Issuer (SEC Form 20-F / 6-K)",
            "ceo": "Nick Langton",
            "headquarters": "Sydney / New York / Las Vegas",
            
            # High-Profile Brand & Strategic Advisory Alignment
            "strategicAdvisory": [
                {
                    "name": "Donald Trump Jr.",
                    "role": "Strategic Advisor",
                    "affiliation": "Co-Founder, World Liberty Financial (USD1 Stablecoin)",
                    "impact": "Top-of-Funnel Media Reach, Digital Media Strategy, USD1 Stablecoin Integration across 15,300+ Academies",
                    "announcedDate": "September 2025"
                },
                {
                    "name": "Conor McGregor",
                    "role": "Key Shareholder & Strategic Combat Icon",
                    "affiliation": "Former UFC 2-Division World Champion / Global Sports Brand Icon",
                    "impact": "Global Combat Athlete Conversion, Brand Ambassador, Organic Gym Onboarding Reach",
                    "announcedDate": "Strategic Holding"
                },
                {
                    "name": "UFC Gym Group Strategic Partnership",
                    "role": "Global Enterprise Franchise Partner",
                    "affiliation": "UFC GYM Global Franchise Network",
                    "impact": "BJJLink.com & BJJLink Admin+ selected as the official gym management software for all new UFC GYM BJJ franchise studios",
                    "announcedDate": "September 2025"
                }
            ],

            # USD1 Stablecoin Transactional Layer (World Liberty Financial)
            "usd1Integration": {
                "stablecoin": "USD1 (World Liberty Financial)",
                "peg": "1.00 USD (Fully Cash & T-Bill Backed)",
                "utility": "Train-to-Earn Gym Check-In Rewards, BJJLink Subscription Billing, Zebra Athletics PO Escrow, Zero-Volatility Settlement",
                "interchangeRate": "0.40% flat (replacing 2.9% + $0.30 traditional cards)",
                "status": "Active across BJJLink, TrainAlta, and UFC GYM BJJ Studios"
            },

            # $4.0M Strategic Private Placement (August 2026)
            "privatePlacement": {
                "grossProceedsUsd": 4000000.00,
                "sharesIssued": 4000000,
                "issuePriceUsd": 1.00,
                "marketPriceAtExecutionUsd": 0.38,
                "premiumToMarketPct": 163.16,
                "investor": "Texas-Based Family Office",
                "warrantCoveragePct": 0.00,
                "brokerPlacementFeesUsd": 0.00,
                "shareRestriction": "Rule 144 Restricted (Anti-Dilutive, No Toxic Selling)",
                "netCashReceivedPct": 100.00
            },

            # Debt & Credit Facilities
            "creditFacility": {
                "lender": "Number 8 Partners Pty Ltd",
                "facilityLimitUsd": 5000000.00,
                "interestRatePct": 12.0,
                "termMonths": 24,
                "nature": "Non-dilutive revolving standby facility"
            },

            # Total Capital Access & Cash Runway
            "cashRunwayModel": {
                "preTransactionCashUsd": 1250000.00,
                "postPlacementCashUsd": 5250000.00,
                "totalCapitalAccessUsd": 10250000.00, # $5.25M cash + $5.0M credit line
                "monthlyNetBurnBaselineUsd": 250000.00,
                "monthlyNetBurnAcceleratedUsd": 350000.00,
                "cashRunwayMonthsBaseline": 21.0,      # $5.25M / $250k
                "cashRunwayMonthsAccelerated": 15.0,   # $5.25M / $350k
                "totalLiquidityRunwayMonths": 41.0     # $10.25M / $250k
            },

            # Platform Monitored Properties ($21M Annualized Run-Rate)
            "ecosystemProperties": [
                {
                    "brand": "BJJLink.com & BJJLink Admin+ (UFC GYM Official Software)",
                    "type": "SaaS & Gym Management Software",
                    "footprint": "Powers all new UFC GYM BJJ Franchise Studios + 15,326 Academies & 680,000 Athletes",
                    "annualPaymentVolumeUsd": 14500000.00,
                    "monetizationVector": "Software Subscriptions, Tournament Entry Fees, USD1 Stablecoin Rails"
                },
                {
                    "brand": "Zebra Athletics",
                    "type": "B2B Combat Equipment & Matting Manufacturing",
                    "footprint": "Premier Global Facilities & High-Density Matting",
                    "annualPaymentVolumeUsd": 5500000.00,
                    "monetizationVector": "Facility Fitouts, Matting PO Escrows, Wholesale Equipment"
                },
                {
                    "brand": "MixedMartialArts.com",
                    "type": "Media & Community Portal",
                    "footprint": "5M+ Social Reach & Legacy Fight Database",
                    "annualPaymentVolumeUsd": 1000000.00,
                    "monetizationVector": "XP Passport Fan Subscriptions, Digital Collectibles, Ad Syndication"
                }
            ]
        }

    def get_profile(self) -> Dict[str, Any]:
        return self.profile

# Singleton instance
corporate_profile = CorporateFinancialProfile()
