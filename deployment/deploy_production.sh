#!/usr/bin/env bash
# ==============================================================================
# UNYKORN.AI x BITGO ENTERPRISE x MMA.INC - PRODUCTION DEPLOYMENT SCRIPT
# ==============================================================================
set -euo pipefail

echo "======================================================================="
echo " Starting MMA.INC x Unykorn.ai x BitGo Enterprise Production Deployment "
echo "======================================================================="

# Step 1: Pre-flight Verification
if [ ! -f ".env.production" ]; then
    echo "[-] Error: .env.production file not found. Copy .env.production.example and fill credentials."
    exit 1
fi

source .env.production

echo "[+] Step 1: Validating environment variables and BitGo connectivity..."
if [ -z "${BITGO_ACCESS_TOKEN:-}" ] || [ -z "${NETWORK_RPC_URL:-}" ]; then
    echo "[-] Error: Missing critical environment variables (BITGO_ACCESS_TOKEN or NETWORK_RPC_URL)."
    exit 1
fi

# Check BitGo Express Daemon
echo "[+] Checking BitGo Express proxy health at ${BITGO_EXPRESS_URL}..."
BITGO_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${BITGO_EXPRESS_URL}/ping" || echo "000")
if [ "$BITGO_STATUS" != "200" ]; then
    echo "[!] Warning: BitGo Express ping returned $BITGO_STATUS. Ensure BitGo Express service is running."
fi

# Step 2: Smart Contract Compilation & Mainnet Deployment
echo "[+] Step 2: Compiling and deploying ERC-3643 & Settlement Contracts..."
python3 deploy_orchestration.py

echo "======================================================================="
echo "[✓] Deployment Completed Successfully."
echo "    - Unykorn API Endpoint: ${UNYKORN_BASE_URL}"
echo "    - BitGo Enterprise Mode: ${BITGO_ENV}"
echo "    - Status: Live & Listening"
echo "======================================================================="
