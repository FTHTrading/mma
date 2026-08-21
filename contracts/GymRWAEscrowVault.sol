// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title GymRWAEscrowVault
 * @notice Real-World Asset (RWA) Escrow and Milestone Disbursement engine for:
 *         1. TrainAlta & BJJLink Gym Expansion Financing Tranches
 *         2. Zebra Athletics Equipment Purchase Order (PO) Escrow
 *         3. Pre-event fight sponsorship escrow accounts
 */

interface IERC20Token {
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
    function transfer(address recipient, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

contract GymRWAEscrowVault {
    address public unykornAdmin;
    address public bitgoCustodyVault;

    enum EscrowStatus { Active, MilestoneMet, Completed, Refunded }
    enum TrancheType { GymExpansion, EquipmentPO, SponsorshipPool }

    struct Milestone {
        string description;
        uint256 amountMinor;
        bool isReleased;
        uint256 verifiedTimestamp;
        address verifier;
    }

    struct EscrowAgreement {
        bytes32 agreementId;
        string entityName;          // e.g., "Zebra Athletics Mfg Order #892", "TrainAlta Austin Gym #04"
        address sponsorOrInvestor;
        address beneficiary;        // Gym owner or Manufacturer
        address settlementToken;    // USDC / USD / USDT
        uint256 totalCommitted;
        uint256 totalReleased;
        TrancheType trancheType;
        EscrowStatus status;
        uint256 milestoneCount;
    }

    mapping(bytes32 => EscrowAgreement) public agreements;
    mapping(bytes32 => Milestone[]) public agreementMilestones;

    event EscrowCreated(bytes32 indexed agreementId, string entityName, uint256 totalCommitted, TrancheType trancheType);
    event MilestoneVerified(bytes32 indexed agreementId, uint256 milestoneIndex, string description, uint256 amount);
    event MilestoneReleased(bytes32 indexed agreementId, uint256 milestoneIndex, address beneficiary, uint256 amount);
    event EscrowRefunded(bytes32 indexed agreementId, address investor, uint256 refundedAmount);

    modifier onlyAdmin() {
        require(msg.sender == unykornAdmin, "Unauthorized: Admin only");
        _;
    }

    constructor(address _bitgoCustodyVault) {
        require(_bitgoCustodyVault != address(0), "Invalid custody vault");
        unykornAdmin = msg.sender;
        bitgoCustodyVault = _bitgoCustodyVault;
    }

    function createEscrowAgreement(
        bytes32 _agreementId,
        string calldata _entityName,
        address _sponsorOrInvestor,
        address _beneficiary,
        address _settlementToken,
        TrancheType _trancheType,
        string[] calldata _milestoneDescriptions,
        uint256[] calldata _milestoneAmounts
    ) external onlyAdmin {
        require(agreements[_agreementId].totalCommitted == 0, "Agreement ID already exists");
        require(_beneficiary != address(0) && _sponsorOrInvestor != address(0), "Invalid parties");
        require(_milestoneDescriptions.length == _milestoneAmounts.length, "Mismatched milestone arrays");
        require(_milestoneDescriptions.length > 0, "At least 1 milestone required");

        uint256 totalSum = 0;
        for (uint256 i = 0; i < _milestoneAmounts.length; i++) {
            require(_milestoneAmounts[i] > 0, "Milestone amount must be > 0");
            totalSum += _milestoneAmounts[i];
            agreementMilestones[_agreementId].push(Milestone({
                description: _milestoneDescriptions[i],
                amountMinor: _milestoneAmounts[i],
                isReleased: false,
                verifiedTimestamp: 0,
                verifier: address(0)
            }));
        }

        agreements[_agreementId] = EscrowAgreement({
            agreementId: _agreementId,
            entityName: _entityName,
            sponsorOrInvestor: _sponsorOrInvestor,
            beneficiary: _beneficiary,
            settlementToken: _settlementToken,
            totalCommitted: totalSum,
            totalReleased: 0,
            trancheType: _trancheType,
            status: EscrowStatus.Active,
            milestoneCount: _milestoneDescriptions.length
        });

        emit EscrowCreated(_agreementId, _entityName, totalSum, _trancheType);
    }

    /**
     * @notice Verifies milestone criteria (e.g. Zebra equipment delivery receipt, gym occupancy permit)
     */
    function verifyAndReleaseMilestone(bytes32 _agreementId, uint256 _milestoneIndex) external onlyAdmin {
        EscrowAgreement storage agreement = agreements[_agreementId];
        require(agreement.status == EscrowStatus.Active || agreement.status == EscrowStatus.MilestoneMet, "Escrow not active");
        require(_milestoneIndex < agreement.milestoneCount, "Invalid milestone index");

        Milestone storage m = agreementMilestones[_agreementId][_milestoneIndex];
        require(!m.isReleased, "Milestone already released");

        m.isReleased = true;
        m.verifiedTimestamp = block.timestamp;
        m.verifier = msg.sender;

        agreement.totalReleased += m.amountMinor;

        if (agreement.totalReleased == agreement.totalCommitted) {
            agreement.status = EscrowStatus.Completed;
        } else {
            agreement.status = EscrowStatus.MilestoneMet;
        }

        emit MilestoneVerified(_agreementId, _milestoneIndex, m.description, m.amountMinor);
        emit MilestoneReleased(_agreementId, _milestoneIndex, agreement.beneficiary, m.amountMinor);
    }

    /**
     * @notice Refunds unreleased escrow capital back to investor if terms fail
     */
    function refundRemainingEscrow(bytes32 _agreementId) external onlyAdmin {
        EscrowAgreement storage agreement = agreements[_agreementId];
        require(agreement.status == EscrowStatus.Active || agreement.status == EscrowStatus.MilestoneMet, "Not refundable");

        uint256 remaining = agreement.totalCommitted - agreement.totalReleased;
        require(remaining > 0, "No remaining balance");

        agreement.status = EscrowStatus.Refunded;
        emit EscrowRefunded(_agreementId, agreement.sponsorOrInvestor, remaining);
    }

    function getMilestones(bytes32 _agreementId) external view returns (Milestone[] memory) {
        return agreementMilestones[_agreementId];
    }
}
