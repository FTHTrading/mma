/**
 * MMA.INC x Unykorn.ai x BitGo Enterprise — Interactive Command Center Client
 */

let activeBouts = [];
let selectedBoutId = null;
let currentTreasury = null;
let activeMarkets = [];
let oracleReports = [];
let activeHedges = [];
let beginnerModeActive = false;

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
    setupTabNavigation();
    loadAllData();
    startRealtimeYieldTicker();
});

// Toggle Beginner Explainer
function toggleBeginnerGuide() {
    const sec = document.getElementById("beginnerExplainerSection");
    const btnText = document.getElementById("beginnerToggleText");
    beginnerModeActive = !beginnerModeActive;

    if (sec) {
        if (beginnerModeActive) {
            sec.style.display = "block";
            sec.scrollIntoView({ behavior: 'smooth' });
            if (btnText) btnText.innerText = "Hide beginner guide";
        } else {
            sec.style.display = "none";
            if (btnText) btnText.innerText = "New to this? Click here";
        }
    }
}

// Tab Navigation
function setupTabNavigation() {
    const tabs = document.querySelectorAll(".nav-tab");
    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            tabs.forEach(t => t.classList.remove("active"));
            document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

            tab.classList.add("active");
            const targetId = `tab-${tab.dataset.tab}`;
            const targetPane = document.getElementById(targetId);
            if (targetPane) targetPane.classList.add("active");
        });
    });
}

// Load all platform data
async function loadAllData() {
    await Promise.all([
        loadBouts(),
        loadPredictionMarkets(),
        loadOracleReports(),
        loadInstitutionalHedges(),
        loadCorporateProfile(),
        loadRwaAgreements(),
        loadPassports(),
        loadTreasury(),
        loadCompliance(),
        loadFinancials(21000000)
    ]);
}

// API Helper
async function fetchApi(endpoint, options = {}) {
    try {
        const res = await fetch(endpoint, options);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } catch (err) {
        console.warn(`API fetch to ${endpoint} failed, utilizing local fallback:`, err);
        return null;
    }
}

// 1. Load Bouts
async function loadBouts() {
    const data = await fetchApi("/api/bouts");
    if (data && data.bouts) {
        activeBouts = data.bouts;
    }

    renderBoutList();
    if (activeBouts.length > 0 && !selectedBoutId) {
        selectBout(activeBouts[0].boutId);
    }
}

function renderBoutList() {
    const container = document.getElementById("boutListContainer");
    if (!container) return;

    container.innerHTML = activeBouts.map(b => `
        <div class="bout-item ${b.boutId === selectedBoutId ? 'active' : ''}" onclick="selectBout('${b.boutId}')">
            <div class="bout-item-header">
                <span class="bout-title">${b.eventName}</span>
                <span class="badge ${b.status === 'Settled' ? 'badge-success' : 'badge-warning'}">${b.status}</span>
            </div>
            <div class="bout-fighters">
                <span>${b.fighterA.name}</span>
                <span class="vs-badge">VS</span>
                <span>${b.fighterB.name}</span>
            </div>
            <div class="bout-tags">
                <span class="badge badge-info"> ${b.jurisdiction} Rail</span>
                <span class="badge badge-info"> $${(b.basePurseUsd).toLocaleString()} Purse</span>
                <span class="badge badge-info"> ${b.settlementToken}</span>
            </div>
        </div>
    `).join("");
}

function selectBout(boutId) {
    selectedBoutId = boutId;
    renderBoutList();

    const bout = activeBouts.find(b => b.boutId === boutId);
    if (!bout) return;

    const eventElem = document.getElementById("detailEventName");
    if (!eventElem) return;

    eventElem.innerText = bout.eventName;
    document.getElementById("detailJurisdiction").innerText = `${bout.jurisdiction} Compliance Rail`;
    document.getElementById("detailToken").innerText = bout.settlementToken;
    document.getElementById("detailBasePurse").innerText = `$${bout.basePurseUsd.toLocaleString()}.00`;
    document.getElementById("detailWinBonus").innerText = `+$${bout.winBonusUsd.toLocaleString()}.00`;
    document.getElementById("activeBoutStatus").innerText = bout.status;
    document.getElementById("activeBoutStatus").className = `badge ${bout.status === 'Settled' ? 'badge-success' : 'badge-warning'}`;

    const splitBody = document.getElementById("splitTableBody");
    const totalEst = bout.basePurseUsd + bout.winBonusUsd;

    splitBody.innerHTML = bout.splits.map(s => {
        const estPayout = (totalEst * s.percentageBps) / 10000;
        return `
            <tr>
                <td><strong>${s.name}</strong><br><span style="font-family:var(--font-mono);font-size:10px;color:var(--text-dim);">${s.recipient}</span></td>
                <td><span class="badge badge-info">${s.role}</span></td>
                <td><strong>${(s.percentageBps / 100).toFixed(2)}%</strong> (${s.percentageBps} bps)</td>
                <td class="text-green" style="font-family:var(--font-mono);font-weight:700;">$${estPayout.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
            </tr>
        `;
    }).join("");

    const winSelect = document.getElementById("winnerSelect");
    winSelect.innerHTML = `
        <option value="${bout.fighterA.name}">${bout.fighterA.name} (Winner)</option>
        <option value="${bout.fighterB.name}">${bout.fighterB.name} (Winner)</option>
    `;

    const receiptBox = document.getElementById("settlementReceiptBox");
    const btnExecute = document.getElementById("btnExecuteSettlement");
    if (bout.isSettled) {
        btnExecute.disabled = true;
        btnExecute.innerText = " Bout Already Programmatically Settled via BitGo";
        receiptBox.style.display = "block";
        renderReceipt(bout);
    } else {
        btnExecute.disabled = false;
        btnExecute.innerText = " Execute BitGo Programmatic MPC Payout (T+0)";
        receiptBox.style.display = "none";
    }
}

async function executeActiveBoutSettlement() {
    if (!selectedBoutId) return;

    const winner = document.getElementById("winnerSelect").value;
    const method = document.getElementById("winMethodSelect").value;
    const btn = document.getElementById("btnExecuteSettlement");

    btn.innerText = "⏳ Orchestrating BitGo MPC Signature & Settlement...";
    btn.disabled = true;

    const res = await fetchApi("/api/bouts/settle", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ boutId: selectedBoutId, winner, method })
    });

    if (res && res.settledBout) {
        const idx = activeBouts.findIndex(b => b.boutId === selectedBoutId);
        activeBouts[idx] = res.settledBout;
        selectBout(selectedBoutId);
    }
    loadTreasury();
}

function renderReceipt(bout) {
    const container = document.getElementById("receiptDetails");
    if (!bout.disbursements || !container) return;

    container.innerHTML = `
        <div style="margin-bottom:10px;">
            <strong>Winner:</strong> <span class="text-gold">${bout.winner}</span> | <strong>Result:</strong> ${bout.winMethod || 'KO Round 2'}
        </div>
        ${bout.disbursements.map(d => `
            <div class="receipt-item" style="display:flex;justify-content:space-between;padding:4px 0;font-size:12px;">
                <span><strong>${d.name}</strong> (${d.role} - ${(d.percentageBps/100).toFixed(1)}%)</span>
                <span class="text-green">$${d.amountUsd.toLocaleString(undefined, {minimumFractionDigits: 2})} [${d.txHash ? d.txHash.slice(0, 10) + '...' : 'BitGo MPC Confirmed'}]</span>
            </div>
        `).join("")}
    `;
}

// 2. USD1 "Train-to-Earn" Check-In Simulator
function simulateTrainToEarnCheckIn() {
    const athleteElem = document.getElementById("athleteCheckInSelect");
    const gymElem = document.getElementById("gymBeaconSelect");
    if (!athleteElem || !gymElem) return;

    const athleteName = athleteElem.selectedOptions[0].text;
    const gymName = gymElem.selectedOptions[0].text;

    const resBox = document.getElementById("checkInResultBox");
    const details = document.getElementById("checkInResultDetails");

    const txHash = "0x" + Array.from({length: 64}, () => Math.floor(Math.random()*16).toString(16)).join("");

    details.innerHTML = `
        <div style="font-size:13px;line-height:1.6;">
            <div><strong>Athlete:</strong> <span class="text-gold">${athleteName}</span></div>
            <div><strong>Gym Location:</strong> <span class="text-cyan">${gymName}</span></div>
            <div><strong>Reward Disbursed:</strong> <span class="text-green" style="font-family:var(--font-mono);font-weight:800;">+$2.50 USD1 (World Liberty Financial)</span></div>
            <div><strong>XP Awarded:</strong> <span class="text-gold">+50 XP to Passport</span></div>
            <div style="font-family:var(--font-mono);font-size:10px;color:var(--text-dim);margin-top:6px;">Smart Contract Tx: ${txHash.slice(0, 20)}... (T+0 Confirmed)</div>
        </div>
    `;
    resBox.style.display = "block";
}

// 3. Load Prediction Markets
async function loadPredictionMarkets() {
    const container = document.getElementById("predMarketsContainer");
    if (!container) return;

    const data = await fetchApi("/api/prediction/markets");
    if (data && data.markets) {
        activeMarkets = data.markets;
    }

    container.innerHTML = activeMarkets.map(m => `
        <div class="pred-market-card">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div>
                    <span class="badge badge-purple">${m.category}</span>
                    <h4 style="font-size:15px;margin-top:6px;">${m.title}</h4>
                    <span style="font-size:11px;color:var(--text-muted);">Pool: <strong class="text-gold">$${m.totalPoolUsd.toLocaleString()}</strong> (1.5% Protocol Fee)</span>
                </div>
                <span class="badge ${m.status === 'Open' ? 'badge-success' : 'badge-warning'}">${m.status}</span>
            </div>

            <div style="margin-top:12px;">
                ${m.options.map(opt => `
                    <div class="pred-opt-row" onclick="stakeOnMarket('${m.marketId}', ${opt.id}, '${opt.name}')">
                        <div>
                            <strong>${opt.name}</strong>
                            <div style="font-size:10px;color:var(--text-dim);">$${opt.poolUsd.toLocaleString()} Pool (${opt.stakersCount || 0} stakers)</div>
                        </div>
                        <div style="text-align:right;">
                            <span class="pred-odds-badge">${opt.probabilityPct}% (${opt.impliedMultiplier}x)</span>
                            <div style="font-size:9px;color:var(--cyan);">+50 XP Stake</div>
                        </div>
                    </div>
                `).join("")}
            </div>
        </div>
    `).join("");
}

async function stakeOnMarket(marketId, optionId, optionName) {
    const amount = prompt(`Enter prediction stake amount (USD1 / USDC / Credits) for: "${optionName}"`, "250");
    if (!amount || isNaN(amount) || parseFloat(amount) <= 0) return;

    const res = await fetchApi("/api/prediction/stake", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ marketId, optionId, amount: parseFloat(amount) })
    });

    if (res && res.success) {
        alert(`Stake of $${amount} confirmed! Awarded +${res.xpAwarded} XP to your XP Passport.`);
        loadPredictionMarkets();
        loadPassports();
    }
}

// 4. Load Oracle Reports
async function loadOracleReports() {
    const nodesGrid = document.getElementById("oracleNodesGrid");
    const reportsContainer = document.getElementById("oracleReportsContainer");
    if (!nodesGrid || !reportsContainer) return;

    const data = await fetchApi("/api/oracle/reports");
    if (!data) return;

    if (data.nodes) {
        nodesGrid.innerHTML = data.nodes.map(n => `
            <div class="oracle-node-card">
                <div style="display:flex;justify-content:space-between;">
                    <span class="oracle-node-name">${n.name}</span>
                    <span class="badge badge-success"> Quorum Active</span>
                </div>
                <div class="oracle-sig-hash">ECDSA_PUBKEY: 0x${Math.random().toString(16).substr(2, 8)}...${Math.random().toString(16).substr(2, 6)}</div>
            </div>
        `).join("");
    }

    if (data.reports) {
        oracleReports = data.reports;
        reportsContainer.innerHTML = data.reports.map(r => `
            <div class="oracle-report-banner">
                <div style="display:flex;justify-content:space-between;">
                    <strong>Bout ID: ${r.boutId}</strong>
                    <span class="badge ${r.inDispute ? 'badge-warning' : (r.isFinalized ? 'badge-success' : 'badge-info')}">
                        ${r.inDispute ? ' Active Dispute' : (r.isFinalized ? ' Finalized & Paid' : '⏳ 5-Min Dispute Window')}
                    </span>
                </div>
                <div style="margin-top:8px;font-size:13px;">
                    Reported Winner: <strong class="text-gold">${r.winnerName}</strong> by <strong class="text-cyan">${r.finishMethod}</strong> (Round ${r.round}, ${r.roundTimeFormatted})
                </div>
                <div style="font-size:11px;color:var(--text-muted);margin-top:4px;">
                    Consensus: <strong>${r.signatureQuorum}</strong> | Scorecards: <strong>${r.officialScorecards.join(", ")}</strong>
                </div>
            </div>
        `).join("");
    }
}

async function simulateDispute() {
    if (oracleReports.length === 0) return;
    const boutId = oracleReports[0].boutId;
    const reason = prompt("Enter athletic commission dispute reason:", "Ringside eye-poke / illegal strike video review requested");
    if (!reason) return;

    await fetchApi("/api/oracle/dispute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ boutId, reason })
    });

    loadOracleReports();
}

async function finalizeOracleOutcome() {
    if (oracleReports.length === 0) return;
    const boutId = oracleReports[0].boutId;

    const res = await fetchApi("/api/oracle/finalize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ boutId, bypassDispute: true })
    });

    if (res && res.report) {
        alert("Oracle outcome finalized! Programmatic BitGo T+0 payout triggered to winning market stakers.");
        loadOracleReports();
    }
}

// 5. Load Institutional OTC Hedges
async function loadInstitutionalHedges() {
    const container = document.getElementById("otcHedgesContainer");
    if (!container) return;

    const data = await fetchApi("/api/institutional/hedges");
    if (!data || !data.hedgesOverview) return;

    const overview = data.hedgesOverview;
    const marginSummary = document.getElementById("otcMarginValSummary");
    const unencumbered = document.getElementById("otcUnencumberedVal");
    if (marginSummary) marginSummary.innerText = `$${overview.totalMarginAllocatedUsd.toLocaleString(undefined, {minimumFractionDigits: 2})}`;
    if (unencumbered) unencumbered.innerText = `$${overview.unencumberedTreasuryFloatUsd.toLocaleString(undefined, {minimumFractionDigits: 2})}`;

    container.innerHTML = overview.activeHedges.map(h => `
        <div class="otc-hedge-card">
            <div>
                <div class="otc-risk-tag">RISK VECTOR: ${h.riskVector}</div>
                <h3 style="font-size:16px;font-weight:800;margin-top:6px;">${h.name}</h3>
                <div style="font-family:var(--font-mono);font-size:11px;color:var(--text-dim);margin-top:2px;">ID: ${h.contractId}</div>

                <div style="background:rgba(255,255,255,0.02);border:1px solid var(--border-color);border-radius:8px;padding:12px;margin:12px 0;font-size:12px;">
                    <div>Notional Protection: <strong class="text-green">$${h.notionalUsd.toLocaleString()}</strong></div>
                    <div>Earmarked Margin: <strong class="text-gold">$${h.marginCollateralUsd.toLocaleString()}</strong> (Zero-Unwrap Float)</div>
                    <div>Liquidity Desk: <strong class="text-cyan">${h.liquidityProvider}</strong></div>
                    <div>Documentation: <strong style="font-size:11px;">${h.masterAgreement}</strong></div>
                </div>

                <p style="font-size:11px;color:var(--text-muted);">${h.payoutProfile}</p>
            </div>

            <div style="margin-top:14px;display:flex;justify-content:space-between;align-items:center;">
                <span class="badge ${h.status.includes('Active') ? 'badge-info' : 'badge-success'}">${h.status}</span>
                ${h.status.includes('Active') ? `<button class="btn btn-outline btn-sm" onclick="triggerHedgeSettlement('${h.contractId}')">Settle Event</button>` : ''}
            </div>
        </div>
    `).join("");
}

async function triggerHedgeSettlement(contractId) {
    const triggered = confirm("Did the risk trigger condition occur? (Click OK to trigger cash payout to MMA.INC, or Cancel to release margin back to float)");
    await fetchApi("/api/institutional/settle-hedge", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ contractId, triggered })
    });
    loadInstitutionalHedges();
}

// 6. Load Corporate Profile & NYSE Balance Sheet
async function loadCorporateProfile() {
    const brandsGrid = document.getElementById("ecoBrandsGrid");
    const data = await fetchApi("/api/company/profile");
    if (!data || !data.profile) return;

    const p = data.profile;
    const priceTag = document.getElementById("stockPriceTag");
    if (priceTag) priceTag.innerText = `NYSE: ${p.ticker} $${p.stockPriceUsd.toFixed(2)}`;

    if (brandsGrid && p.ecosystemProperties) {
        brandsGrid.innerHTML = p.ecosystemProperties.map(b => `
            <div class="eco-brand-card">
                <span class="badge badge-info">${b.type}</span>
                <h3 style="font-size:16px;font-weight:800;margin-top:6px;">${b.brand}</h3>
                <div style="font-size:12px;color:var(--text-muted);margin:4px 0;">${b.footprint}</div>
                <div class="text-gold" style="font-family:var(--font-mono);font-weight:800;font-size:15px;margin-top:6px;">$${b.annualPaymentVolumeUsd.toLocaleString()} / yr volume</div>
                <div style="font-size:11px;color:var(--cyan);margin-top:4px;">Monetization: ${b.monetizationVector}</div>
            </div>
        `).join("");
    }
}

// 7. Load Gym RWA & Zebra PO Escrows
async function loadRwaAgreements() {
    const container = document.getElementById("rwaContainer");
    if (!container) return;

    const data = await fetchApi("/api/rwa/agreements");
    if (!data || !data.agreements) return;

    container.innerHTML = data.agreements.map(a => {
        const pct = Math.round((a.totalReleasedUsd / a.totalCommittedUsd) * 100);
        return `
            <div class="rwa-card">
                <div class="rwa-header">
                    <span class="rwa-category">${a.category}</span>
                    <h3 class="rwa-name">${a.entityName}</h3>
                    <div style="font-family:var(--font-mono);font-size:11px;color:var(--text-dim);margin-top:2px;">ID: ${a.agreementId}</div>
                </div>

                <div>
                    <div style="display:flex;justify-content:space-between;font-size:12px;margin-top:10px;">
                        <span>Released: <strong class="text-green">$${a.totalReleasedUsd.toLocaleString()}</strong></span>
                        <span>Total: <strong class="text-gold">$${a.totalCommittedUsd.toLocaleString()}</strong></span>
                    </div>
                    <div class="rwa-progress-bar">
                        <div class="rwa-progress-fill" style="width: ${pct}%"></div>
                    </div>
                </div>

                <div class="milestones-list">
                    <span style="font-size:11px;font-weight:700;color:var(--text-dim);">QUALIFIED ESCROW MILESTONES:</span>
                    ${a.milestones.map((m, idx) => `
                        <div class="milestone-row ${m.isReleased ? 'released' : ''}">
                            <div style="max-width:70%;">
                                <strong>${m.description}</strong><br>
                                <span class="text-green" style="font-family:var(--font-mono);">$${m.amountUsd.toLocaleString()}</span>
                            </div>
                            <div>
                                ${m.isReleased 
                                    ? '<span class="badge badge-success"> Disbursed</span>' 
                                    : `<button class="btn btn-outline btn-sm" onclick="releaseMilestone('${a.agreementId}', ${idx})">Verify & Release</button>`
                                }
                            </div>
                        </div>
                    `).join("")}
                </div>
            </div>
        `;
    }).join("");
}

async function releaseMilestone(agreementId, milestoneId) {
    await fetchApi("/api/rwa/release-milestone", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ agreementId, milestoneId })
    });
    loadRwaAgreements();
    loadTreasury();
}

// 8. Load Passports (ERC-3643)
async function loadPassports() {
    const container = document.getElementById("passportContainer");
    if (!container) return;

    const data = await fetchApi("/api/passports");
    if (!data || !data.passports) return;

    container.innerHTML = data.passports.map(p => `
        <div class="passport-card">
            <div class="passport-top">
                <div>
                    <span class="passport-id">${p.passportId}</span>
                    <h3 class="passport-name">${p.name}</h3>
                    <div class="passport-rank">${p.combatRank}</div>
                </div>
                <span class="badge badge-info">${p.role}</span>
            </div>

            <div style="font-size:12px;color:var(--text-muted);display:flex;justify-content:space-between;">
                <span>Jurisdiction: <strong>${p.countryName}</strong></span>
                <span class="text-green"> ${p.kycLevel}</span>
            </div>

            <div class="passport-xp">${p.xpPoints.toLocaleString()} <span style="font-size:12px;color:var(--text-dim);">XP</span></div>

            <div class="badge-cloud">
                ${p.badges.map(b => `<span class="badge-tag">${b}</span>`).join("")}
            </div>
        </div>
    `).join("");
}

// 9. Load BitGo Treasury
async function loadTreasury() {
    const data = await fetchApi("/api/treasury");
    if (!data) return;

    currentTreasury = data;
    const vContainer = document.getElementById("vaultsContainer");
    if (vContainer && data.treasury && data.treasury.vaults) {
        const vaults = data.treasury.vaults;
        vContainer.innerHTML = Object.keys(vaults).map(k => {
            const v = vaults[k];
            return `
                <div class="vault-card">
                    <span class="vault-name">${v.jurisdiction}</span>
                    <div class="vault-balance text-gold">$${v.balance.toLocaleString(undefined, {minimumFractionDigits:2})}</div>
                    <div style="font-size:11px;color:var(--text-muted);">Asset: <strong>${v.asset}</strong></div>
                    <div style="font-size:10px;color:var(--cyan);margin-top:6px;">MPC: ${v.mpcThreshold}</div>
                    <div style="font-size:10px;color:var(--green);margin-top:2px;"> ${v.status}</div>
                </div>
            `;
        }).join("");
    }

    const txTable = document.getElementById("treasuryTxTable");
    if (txTable && data.recentTransactions) {
        txTable.innerHTML = data.recentTransactions.map(tx => `
            <tr>
                <td><strong>${tx.type}</strong></td>
                <td>${tx.token || 'USD'}</td>
                <td class="text-green font-mono">$${(tx.amountHuman || tx.amountUsd || tx.amount || 0).toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                <td>${tx.recipient || tx.jurisdiction || 'BitGo Vault'}</td>
                <td><span class="badge badge-success"> Confirmed</span></td>
                <td style="font-family:var(--font-mono);font-size:11px;color:var(--text-dim);">${tx.timestamp}</td>
            </tr>
        `).join("");
    }
}

// 10. Load Financial Velocity & Interchange
async function loadFinancials(runRate = 21000000) {
    const legacyCost = runRate * 0.037; // ~3.70%
    const unykornCost = runRate * 0.0055; // ~0.55%
    const netSavings = legacyCost - unykornCost;
    const tbillYield = 4000000 * 0.0525; // $210,000
    const totalBenefit = netSavings + tbillYield;

    const netElem = document.getElementById("netSavingsDisplay");
    const totElem = document.getElementById("totalBenefitDisplay");

    if (netElem) netElem.innerText = `$${netSavings.toLocaleString(undefined, {minimumFractionDigits: 2})} / year`;
    if (totElem) totElem.innerText = `$${totalBenefit.toLocaleString(undefined, {minimumFractionDigits: 2})} / year`;
}

function updateRunRateSimulation(val) {
    const runRate = parseFloat(val);
    document.getElementById("sliderValDisplay").innerText = `$${runRate.toLocaleString(undefined, {minimumFractionDigits: 2})}`;
    loadFinancials(runRate);
}

// 11. Load Compliance
async function loadCompliance() {
    const container = document.getElementById("jurisdictionGrid");
    if (!container) return;

    const jurisdictions = [
        {
            name: "United States (Base)",
            footprint: "MMA.INC (NYSE American), NSAC / CSAC Vegas & California bouts",
            regulators: "SEC, CFTC, FinCEN, State Athletic Commissions",
            impl: "SEC-compliant reporting; BitGo Trust bank qualified custody; corporate treasury yield via tokenized T-Bills."
        },
        {
            name: "Singapore (APAC Hub)",
            footprint: "Regional headquarters, ONE Championship ecosystem",
            regulators: "MAS (Monetary Authority of Singapore)",
            impl: "BitGo Singapore (Major Payment Institution licensed) acts as the operational and treasury hub for APAC settlements."
        },
        {
            name: "Japan",
            footprint: "RIZIN, Pride legacy brands, K-1",
            regulators: "JFSA (Financial Services Agency) & JVCEA",
            impl: "BitGo MPC custody satisfies stringent JFSA 95% offline cold storage standards; enables compliant cross-border event financing and JPY-pegged settlement."
        },
        {
            name: "Thailand",
            footprint: "Muay Thai circuits (Lumpinee, Rajadamnern), Training camps",
            regulators: "Thai SEC & Bank of Thailand",
            impl: "Unykorn enforces identity rules avoiding banned retail token types; uses regulated on/off-ramps for foreign fighter purse conversion into Thai Baht (THB)."
        },
        {
            name: "Middle East (UAE / Saudi)",
            footprint: "UFC Fight Island (Abu Dhabi), PFL MENA (Riyadh)",
            regulators: "VARA (Dubai) & ADGM (Abu Dhabi)",
            impl: "Compliant virtual asset service distribution and sovereign sports investment syndication."
        }
    ];

    container.innerHTML = jurisdictions.map(j => `
        <div class="jur-card">
            <h3 class="jur-name">${j.name}</h3>
            <div class="jur-row">
                <span class="jur-label">Footprint</span>
                <p class="jur-val">${j.footprint}</p>
            </div>
            <div class="jur-row">
                <span class="jur-label">Regulators</span>
                <p class="jur-val text-gold">${j.regulators}</p>
            </div>
            <div class="jur-row">
                <span class="jur-label">Unykorn + BitGo Solution</span>
                <p class="jur-val text-cyan">${j.impl}</p>
            </div>
        </div>
    `).join("");
}

// Real-time yield ticker animation
function startRealtimeYieldTicker() {
    let accumulated = 84250.00;
    const ratePerSecond = (4000000.00 * 0.0525) / (365 * 86400);

    setInterval(() => {
        accumulated += ratePerSecond;
        const elem = document.getElementById("accumYieldVal");
        if (elem) elem.innerText = `$${accumulated.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    }, 1000);
}
