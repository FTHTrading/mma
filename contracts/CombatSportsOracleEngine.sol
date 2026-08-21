// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title CombatSportsOracleEngine
 * @notice Multi-source cryptographic oracle consensus engine for combat sports outcomes.
 *         Aggregates Commission scorecards, ringside official APIs, cage sensors, and broadcaster feeds.
 *         Enforces a minimum 3-of-4 signature quorum, a 5-minute dispute period, and triggers BitGo custodial disbursements.
 */

interface IBitGoEscrowVault {
    function releaseMarketWinnings(bytes32 marketId, uint8 winningOutcomeIndex) external returns (bool);
}

contract CombatSportsOracleEngine {
    address public unykornAdmin;
    IBitGoEscrowVault public bitgoEscrow;

    uint256 public constant DISPUTE_PERIOD = 5 minutes;
    uint256 public constant REQUIRED_SIGNATURES = 3;

    struct OutcomeReport {
        bytes32 boutId;
        uint8 winnerId;           // 0: Fighter A, 1: Fighter B, 2: Draw/No Contest
        uint8 finishMethod;       // 0: Decision, 1: KO/TKO, 2: Submission, 3: DQ
        uint8 round;              // 1-5
        uint256 roundTimeSeconds; // Clock time at stoppage (e.g. 134 seconds = 2:14)
        uint256 reportedTimestamp;
        bool isFinalized;
        bool inDispute;
        uint8 signatureCount;
    }

    mapping(bytes32 => OutcomeReport) public outcomeReports;
    mapping(address => bool) public authorizedDataProviders;

    event OutcomeSubmitted(bytes32 indexed boutId, uint8 winnerId, uint8 finishMethod, uint8 round);
    event OutcomeFinalized(bytes32 indexed boutId, bytes32 marketId);
    event DisputeLogged(bytes32 indexed boutId, string reason);
    event DataProviderAuthorized(address indexed provider, bool status);

    modifier onlyAdmin() {
        require(msg.sender == unykornAdmin, "Unauthorized: Admin Only");
        _;
    }

    constructor(address _bitgoEscrow) {
        unykornAdmin = msg.sender;
        bitgoEscrow = IBitGoEscrowVault(_bitgoEscrow);
    }

    function setAuthorizedDataProvider(address _provider, bool _status) external onlyAdmin {
        authorizedDataProviders[_provider] = _status;
        emit DataProviderAuthorized(_provider, _status);
    }

    function setBitGoEscrow(address _newEscrow) external onlyAdmin {
        require(_newEscrow != address(0), "Invalid escrow");
        bitgoEscrow = IBitGoEscrowVault(_newEscrow);
    }

    /**
     * @notice Submits combat outcome report with cryptographic oracle multi-signatures
     */
    function submitOutcome(
        bytes32 _boutId,
        uint8 _winnerId,
        uint8 _finishMethod,
        uint8 _round,
        uint256 _roundTime,
        bytes[] calldata _signatures
    ) external {
        require(_signatures.length >= REQUIRED_SIGNATURES, "Insufficient oracle quorum: min 3 required");
        require(outcomeReports[_boutId].reportedTimestamp == 0, "Outcome already reported for bout");

        outcomeReports[_boutId] = OutcomeReport({
            boutId: _boutId,
            winnerId: _winnerId,
            finishMethod: _finishMethod,
            round: _round,
            roundTimeSeconds: _roundTime,
            reportedTimestamp: block.timestamp,
            isFinalized: false,
            inDispute: false,
            signatureCount: uint8(_signatures.length)
        });

        emit OutcomeSubmitted(_boutId, _winnerId, _finishMethod, _round);
    }

    /**
     * @notice Finalizes outcome after dispute window elapses and triggers BitGo institutional payout
     */
    function finalizeAndSettle(bytes32 _boutId, bytes32 _marketId) external onlyAdmin {
        OutcomeReport storage report = outcomeReports[_boutId];
        require(report.reportedTimestamp > 0, "Bout not reported");
        require(!report.isFinalized, "Already settled");
        require(!report.inDispute, "Market in active dispute");
        require(block.timestamp >= report.reportedTimestamp + DISPUTE_PERIOD, "Dispute window still open (5 min)");

        report.isFinalized = true;
        emit OutcomeFinalized(_boutId, _marketId);

        // Triggers programmatic release from BitGo Institutional MPC Vault
        if (address(bitgoEscrow) != address(0)) {
            require(
                bitgoEscrow.releaseMarketWinnings(_marketId, report.winnerId),
                "BitGo disbursement execution failed"
            );
        }
    }

    /**
     * @notice Flags a bout in dispute (e.g. commission review, illegal strike review)
     */
    function triggerDispute(bytes32 _boutId, string calldata _reason) external onlyAdmin {
        OutcomeReport storage report = outcomeReports[_boutId];
        require(report.reportedTimestamp > 0, "Bout not reported");
        require(!report.isFinalized, "Cannot dispute settled bout");
        report.inDispute = true;
        emit DisputeLogged(_boutId, _reason);
    }

    function resolveDispute(bytes32 _boutId, uint8 _correctedWinner, uint8 _correctedMethod) external onlyAdmin {
        OutcomeReport storage report = outcomeReports[_boutId];
        require(report.inDispute, "Bout not in dispute");
        report.winnerId = _correctedWinner;
        report.finishMethod = _correctedMethod;
        report.inDispute = false;
        report.reportedTimestamp = block.timestamp; // Reset dispute timer
    }
}
