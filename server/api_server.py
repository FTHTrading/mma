"""
MMA.INC x Unykorn.ai x BitGo Enterprise — REST API Server
Autonomous zero-dependency Python HTTP Server providing full REST API services
and static dashboard hosting with port fallback resilience.
"""

import json
import os
import sys
import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure local imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bitgo_service import bitgo_service
from settlement_engine import settlement_engine
from rwa_gym_engine import rwa_gym_engine
from passport_engine import passport_engine
from oracle_service import oracle_service
from institutional_hedging import institutional_hedging_desk
from prediction_engine import prediction_engine
from corporate_profile import corporate_profile

WEB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web")

class MMACommandServerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def _set_json_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_json_headers(200)

    def _read_json_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length).decode("utf-8")
        try:
            return json.loads(body)
        except Exception:
            return {}

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/status":
            self._set_json_headers(200)
            self.wfile.write(json.dumps({
                "status": "OPERATIONAL",
                "network": "Unykorn.ai Sovereign L1 / Arbitrum / Base Rail",
                "custodian": "BitGo Trust Company Qualified Custody",
                "nyseEntity": "MMA.INC (NYSE American: MMA)",
                "timestamp": bitgo_service.treasury["vaults"]["us_operating_treasury"]["status"]
            }).encode("utf-8"))
            return

        elif path == "/api/treasury":
            self._set_json_headers(200)
            self.wfile.write(json.dumps(bitgo_service.get_treasury_overview()).encode("utf-8"))
            return

        elif path == "/api/bouts":
            self._set_json_headers(200)
            self.wfile.write(json.dumps({
                "success": True,
                "bouts": settlement_engine.get_all_bouts()
            }).encode("utf-8"))
            return

        elif path == "/api/rwa/agreements":
            self._set_json_headers(200)
            self.wfile.write(json.dumps({
                "success": True,
                "agreements": rwa_gym_engine.get_all_agreements()
            }).encode("utf-8"))
            return

        elif path == "/api/financials/velocity":
            self._set_json_headers(200)
            self.wfile.write(json.dumps(rwa_gym_engine.get_financial_velocity_model()).encode("utf-8"))
            return

        elif path == "/api/passports":
            self._set_json_headers(200)
            self.wfile.write(json.dumps({
                "success": True,
                "passports": passport_engine.get_all_passports()
            }).encode("utf-8"))
            return

        elif path == "/api/compliance/matrix":
            self._set_json_headers(200)
            self.wfile.write(json.dumps({
                "success": True,
                "jurisdictions": settlement_engine.get_compliance_matrix()
            }).encode("utf-8"))
            return

        # NEW ENDPOINTS FOR PREDICTION MARKETS & ORACLE DESK
        elif path == "/api/prediction/markets":
            self._set_json_headers(200)
            self.wfile.write(json.dumps({
                "success": True,
                "markets": prediction_engine.get_all_markets(),
                "totalProtocolFeesCollectedUsd": prediction_engine.total_protocol_fees_collected_usd
            }).encode("utf-8"))
            return

        elif path == "/api/oracle/reports":
            self._set_json_headers(200)
            self.wfile.write(json.dumps({
                "success": True,
                "reports": oracle_service.get_all_reports(),
                "nodes": oracle_service.oracle_nodes
            }).encode("utf-8"))
            return

        elif path == "/api/institutional/hedges":
            self._set_json_headers(200)
            self.wfile.write(json.dumps({
                "success": True,
                "hedgesOverview": institutional_hedging_desk.get_desk_overview()
            }).encode("utf-8"))
            return

        elif path == "/api/company/profile":
            self._set_json_headers(200)
            self.wfile.write(json.dumps({
                "success": True,
                "profile": corporate_profile.get_profile()
            }).encode("utf-8"))
            return

        # Otherwise serve static files from web/
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._read_json_body()

        try:
            # Settle a Bout
            if path == "/api/bouts/settle":
                bout_id = body.get("boutId")
                winner_name = body.get("winner")
                method = body.get("method", "Decision / KO")
                res = settlement_engine.record_and_settle_bout(bout_id, winner_name, method)
                self._set_json_headers(200)
                self.wfile.write(json.dumps({"success": True, "settledBout": res}).encode("utf-8"))
                return

            # Release RWA Milestone
            elif path == "/api/rwa/release-milestone":
                agreement_id = body.get("agreementId")
                milestone_id = int(body.get("milestoneId", 0))
                res = rwa_gym_engine.release_milestone(agreement_id, milestone_id)
                self._set_json_headers(200)
                self.wfile.write(json.dumps({"success": True, "agreement": res}).encode("utf-8"))
                return

            # Prediction Market Staking
            elif path == "/api/prediction/stake":
                market_id = body.get("marketId")
                option_id = int(body.get("optionId", 0))
                amount = float(body.get("amount", 100))
                wallet = body.get("wallet", "0x8ACED25dc8530FDaf0f86D53a0A1E02AAfA7Ac7A")
                res = prediction_engine.place_stake(market_id, option_id, amount, wallet)
                self._set_json_headers(200)
                self.wfile.write(json.dumps(res).encode("utf-8"))
                return

            # Prediction Market Resolution
            elif path == "/api/prediction/resolve":
                market_id = body.get("marketId")
                winning_id = int(body.get("winningOptionId", 0))
                res = prediction_engine.resolve_market(market_id, winning_id)
                self._set_json_headers(200)
                self.wfile.write(json.dumps({"success": True, "market": res}).encode("utf-8"))
                return

            # Oracle Outcome Ingestion
            elif path == "/api/oracle/submit":
                bout_id = body.get("boutId")
                market_id = body.get("marketId", "MKT-BOUT-GENERIC")
                winner_name = body.get("winnerName")
                winner_idx = int(body.get("winnerIndex", 0))
                method = body.get("finishMethod", "KO/TKO")
                round_num = int(body.get("round", 2))
                round_time = int(body.get("roundTimeSeconds", 120))
                res = oracle_service.submit_combat_outcome(
                    bout_id, market_id, winner_name, winner_idx, method, round_num, round_time
                )
                self._set_json_headers(200)
                self.wfile.write(json.dumps({"success": True, "report": res}).encode("utf-8"))
                return

            # Oracle Dispute Trigger
            elif path == "/api/oracle/dispute":
                bout_id = body.get("boutId")
                reason = body.get("reason", "Official Scorecard Audit Requested")
                res = oracle_service.trigger_dispute(bout_id, reason)
                self._set_json_headers(200)
                self.wfile.write(json.dumps({"success": True, "report": res}).encode("utf-8"))
                return

            # Oracle Finalize & Settle
            elif path == "/api/oracle/finalize":
                bout_id = body.get("boutId")
                bypass = body.get("bypassDispute", True)
                res = oracle_service.finalize_and_settle(bout_id, bypass_dispute_for_test=bypass)
                self._set_json_headers(200)
                self.wfile.write(json.dumps({"success": True, "report": res}).encode("utf-8"))
                return

            # Settle Institutional OTC Hedge
            elif path == "/api/institutional/settle-hedge":
                contract_id = body.get("contractId")
                triggered = body.get("triggered", False)
                res = institutional_hedging_desk.settle_otc_contract(contract_id, triggered)
                self._set_json_headers(200)
                self.wfile.write(json.dumps({"success": True, "hedge": res}).encode("utf-8"))
                return

            # Award XP
            elif path == "/api/passports/award-xp":
                wallet = body.get("wallet")
                points = int(body.get("points", 500))
                reason = body.get("reason", "Combat Achievement")
                res = passport_engine.award_xp(wallet, points, reason)
                self._set_json_headers(200)
                self.wfile.write(json.dumps({"success": True, "passport": res}).encode("utf-8"))
                return

            else:
                self._set_json_headers(404)
                self.wfile.write(json.dumps({"error": f"Endpoint {path} not found"}).encode("utf-8"))

        except Exception as e:
            self._set_json_headers(400)
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

def run_server(preferred_port: int = 8888):
    port_candidates = [preferred_port, 8088, 8888, 9090, 5000, 3000, 8000]
    httpd = None
    active_port = None

    for port in port_candidates:
        try:
            server_address = ("127.0.0.1", port)
            httpd = HTTPServer(server_address, MMACommandServerHandler)
            active_port = port
            break
        except OSError:
            continue

    if not httpd or not active_port:
        print("[ERROR] Could not bind to any available local port.")
        sys.exit(1)

    print(f"============================================================")
    print(f"  [SERVER] MMA.INC x UNYKORN.AI x BITGO ENTERPRISE PLATFORM")
    print(f"  Institutional Web3 Gateway & Qualified Custody Engine")
    print(f"  Live Server listening on: http://127.0.0.1:{active_port}")
    print(f"============================================================")
    
    # Save active port to config file for launcher
    port_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".active_port")
    with open(port_file, "w") as f:
        f.write(str(active_port))

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer shutting down gracefully.")
        httpd.server_close()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8888))
    run_server(port)
