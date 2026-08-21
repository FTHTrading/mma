// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title MMAPurseSettlementEngine
 * @notice Orchestrates automated fight purse splits, win bonuses, manager/trainer commissions,
 *         and state athletic commission tax withholdings, triggering BitGo Enterprise MPC custody settlement.
 * @dev Integrates ERC-3643 permissioned identity registry for strict KYC/AML compliance.
 */

interface IERC3643IdentityRegistry {
    function isVerified(address _userAddress) external view returns (bool);
    function getCountry(address _userAddress) external view returns (uint16);
    function isSanctioned(address _userAddress) external view returns (bool);
}

interface IBitGoSettlementVault {
    function executeTransfer(address token, address recipient, uint256 amount) external returns (bool);
    function holdInEscrow(address token, uint256 amount, bytes32 escrowId) external returns (bool);
    function releaseEscrow(bytes32 escrowId, address recipient, uint256 amount) external returns (bool);
}

contract MMAPurseSettlementEngine {
    address public unykornAdmin;
    address public treasuryOperator;
    IERC3643IdentityRegistry public identityRegistry;
    IBitGoSettlementVault public bitgoVault;

    enum BoutStatus { Scheduled, InProgress, Completed, Disputed, Settled, Cancelled }

    struct SplitAllocation {
        address recipient;
        uint256 percentageBps; // Basis points: 100 bps = 1.00%, 10,000 bps = 100.00%
        string role;           // "Fighter", "Corner/Trainer", "Management", "AthleticCommission", "SanctioningBody"
        uint16 jurisdiction;   // ISO country code e.g. 840 (US), 392 (Japan), 764 (Thailand), 702 (Singapore)
    }

    struct Bout {
        bytes32 boutId;
        string eventName;
        address fighterA;
        address fighterB;
        uint256 totalPurse;          // Guaranteed base purse in minor units
        uint256 winBonusAmount;      // Winner performance incentive
        address settlementToken;     // USDC, JPYC, THB-backed stablecoin, or address(0) for native USD
        BoutStatus status;
        address winner;
        bool isSettled;
        uint256 settledAt;
    }

    mapping(bytes32 => Bout) public bouts;
    mapping(bytes32 => SplitAllocation[]) public boutSplits;
    mapping(bytes32 => uint256) public totalDisbursed;

    event BoutCreated(bytes32 indexed boutId, string eventName, uint256 totalPurse, uint256 winBonus, address token);
    event BoutResultPosted(bytes32 indexed boutId, address winner, BoutStatus status);
    event PurseDisbursed(bytes32 indexed boutId, address indexed recipient, string role, uint256 amount, address token);
    event BoutSettled(bytes32 indexed boutId, uint256 totalDisbursedAmount, uint256 timestamp);
    event AdminTransferred(address indexed previousAdmin, address indexed newAdmin);

    modifier onlyAdmin() {
        require(msg.sender == unykornAdmin || msg.sender == treasuryOperator, "Unauthorized: Admin/Operator only");
        _;
    }

    constructor(address _identityRegistry, address _bitgoVault, address _treasuryOperator) {
        require(_identityRegistry != address(0), "Invalid identity registry");
        require(_bitgoVault != address(0), "Invalid BitGo vault");
        
        unykornAdmin = msg.sender;
        treasuryOperator = _treasuryOperator != address(0) ? _treasuryOperator : msg.sender;
        identityRegistry = IERC3643IdentityRegistry(_identityRegistry);
        bitgoVault = IBitGoSettlementVault(_bitgoVault);
    }

    function setTreasuryOperator(address _newOperator) external onlyAdmin {
        require(_newOperator != address(0), "Invalid operator");
        treasuryOperator = _newOperator;
    }

    function setBitGoVault(address _newVault) external onlyAdmin {
        require(_newVault != address(0), "Invalid vault address");
        bitgoVault = IBitGoSettlementVault(_newVault);
    }

    /**
     * @notice Registers a new fight card bout with split allocations and KYC pre-check
     */
    function createBoutPurse(
        bytes32 _boutId,
        string calldata _eventName,
        address _fighterA,
        address _fighterB,
        uint256 _totalPurse,
        uint256 _winBonus,
        address _token,
        SplitAllocation[] calldata _splits
    ) external onlyAdmin {
        require(bouts[_boutId].totalPurse == 0, "Bout already registered");
        require(_fighterA != address(0) && _fighterB != address(0), "Invalid fighter address");
        require(_totalPurse > 0, "Purse must be > 0");

        // Identity and Sanctions Verification
        require(identityRegistry.isVerified(_fighterA), "Fighter A KYC/AML failed");
        require(!identityRegistry.isSanctioned(_fighterA), "Fighter A is sanctioned");
        require(identityRegistry.isVerified(_fighterB), "Fighter B KYC/AML failed");
        require(!identityRegistry.isSanctioned(_fighterB), "Fighter B is sanctioned");

        uint256 totalBps = 0;
        for (uint256 i = 0; i < _splits.length; i++) {
            require(_splits[i].recipient != address(0), "Invalid split recipient");
            require(identityRegistry.isVerified(_splits[i].recipient), "Recipient fails KYC/AML");
            require(!identityRegistry.isSanctioned(_splits[i].recipient), "Recipient is sanctioned");
            boutSplits[_boutId].push(_splits[i]);
            totalBps += _splits[i].percentageBps;
        }
        require(totalBps == 10000, "Splits must sum to exactly 10,000 BPS (100%)");

        bouts[_boutId] = Bout({
            boutId: _boutId,
            eventName: _eventName,
            fighterA: _fighterA,
            fighterB: _fighterB,
            totalPurse: _totalPurse,
            winBonusAmount: _winBonus,
            settlementToken: _token,
            status: BoutStatus.Scheduled,
            winner: address(0),
            isSettled: false,
            settledAt: 0
        });

        emit BoutCreated(_boutId, _eventName, _totalPurse, _winBonus, _token);
    }

    /**
     * @notice Records the official athletic commission result for a bout
     */
    function recordBoutResult(bytes32 _boutId, address _winner, BoutStatus _status) external onlyAdmin {
        Bout storage bout = bouts[_boutId];
        require(bout.totalPurse > 0, "Bout does not exist");
        require(!bout.isSettled, "Bout already settled");
        require(_status == BoutStatus.Completed || _status == BoutStatus.Disputed, "Invalid status");

        if (_winner != address(0)) {
            require(_winner == bout.fighterA || _winner == bout.fighterB, "Winner must be participant");
            bout.winner = _winner;
        }
        bout.status = _status;
        emit BoutResultPosted(_boutId, _winner, _status);
    }

    /**
     * @notice Programmatically settles the bout purse across all split recipients via BitGo Enterprise Custody
     */
    function executePurseSettlement(bytes32 _boutId) external onlyAdmin {
        Bout storage bout = bouts[_boutId];
        require(bout.totalPurse > 0, "Bout not found");
        require(bout.status == BoutStatus.Completed, "Bout not completed/disputed");
        require(!bout.isSettled, "Bout already settled");

        uint256 finalPurse = bout.totalPurse;
        if (bout.winner != address(0) && bout.winBonusAmount > 0) {
            finalPurse += bout.winBonusAmount;
        }

        SplitAllocation[] memory splits = boutSplits[_boutId];
        uint256 cumulativePaid = 0;

        for (uint256 i = 0; i < splits.length; i++) {
            // Integer math with strict rounding
            uint256 payout = (finalPurse * splits[i].percentageBps) / 10000;
            
            // For last recipient, handle any dust due to integer division
            if (i == splits.length - 1) {
                uint256 remaining = finalPurse - cumulativePaid;
                payout = remaining;
            }
            
            cumulativePaid += payout;

            // Execute programmatic transfer via BitGo Enterprise Vault
            bool success = bitgoVault.executeTransfer(bout.settlementToken, splits[i].recipient, payout);
            require(success, "BitGo settlement transfer failed");

            emit PurseDisbursed(_boutId, splits[i].recipient, splits[i].role, payout, bout.settlementToken);
        }

        bout.isSettled = true;
        bout.status = BoutStatus.Settled;
        bout.settledAt = block.timestamp;
        totalDisbursed[_boutId] = cumulativePaid;

        emit BoutSettled(_boutId, cumulativePaid, block.timestamp);
    }

    function getBoutSplits(bytes32 _boutId) external view returns (SplitAllocation[] memory) {
        return boutSplits[_boutId];
    }
}
