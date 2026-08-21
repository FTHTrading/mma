// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title XPPassportRegistry
 * @notice Sovereign on-chain identity registry adhering to ERC-3643 principles.
 *         Maintains verified KYC/AML status, jurisdiction classification, sanctions monitoring,
 *         fighter combat records (belt ranks, weight division), and fan VIP token gating credentials.
 */

contract XPPassportRegistry {
    address public unykornAdmin;

    enum IdentityType { Fighter, Trainer, GymOwner, FanVIP, Promoter, AthleticCommission }
    enum KYCLevel { Unverified, Tier1_Basic, Tier2_Institutional, Tier3_Accredited }

    struct Identity {
        address walletAddress;
        string didUri;           // Decentralized ID / Metadata URI
        IdentityType identityType;
        KYCLevel kycLevel;
        uint16 countryCode;      // ISO 3166-1 numeric (e.g. 840 = US, 392 = Japan, 764 = Thailand, 702 = Singapore)
        bool isVerified;
        bool isSanctioned;
        uint256 registeredAt;
        uint256 xpScore;
        string combatRank;       // e.g. "Pro MMA (14-2)", "BJJ Black Belt 2nd Stripe"
    }

    mapping(address => Identity) public identities;
    mapping(address => bool) public verifiers;

    event IdentityRegistered(address indexed user, IdentityType idType, uint16 countryCode, KYCLevel kycLevel);
    event KYCStatusUpdated(address indexed user, KYCLevel kycLevel, bool isVerified);
    event SanctionStatusUpdated(address indexed user, bool isSanctioned);
    event XPScoreAwarded(address indexed user, uint256 addedXp, uint256 newTotal);

    modifier onlyAdmin() {
        require(msg.sender == unykornAdmin || verifiers[msg.sender], "Unauthorized");
        _;
    }

    constructor() {
        unykornAdmin = msg.sender;
        verifiers[msg.sender] = true;
    }

    function setVerifier(address _verifier, bool _status) external {
        require(msg.sender == unykornAdmin, "Only admin");
        verifiers[_verifier] = _status;
    }

    function registerIdentity(
        address _user,
        string calldata _didUri,
        IdentityType _identityType,
        KYCLevel _kycLevel,
        uint16 _countryCode,
        string calldata _combatRank
    ) external onlyAdmin {
        require(_user != address(0), "Invalid address");

        identities[_user] = Identity({
            walletAddress: _user,
            didUri: _didUri,
            identityType: _identityType,
            kycLevel: _kycLevel,
            countryCode: _countryCode,
            isVerified: (_kycLevel != KYCLevel.Unverified),
            isSanctioned: false,
            registeredAt: block.timestamp,
            xpScore: 100,
            combatRank: _combatRank
        });

        emit IdentityRegistered(_user, _identityType, _countryCode, _kycLevel);
    }

    function updateKYCStatus(address _user, KYCLevel _level, bool _verified) external onlyAdmin {
        require(identities[_user].registeredAt > 0, "Identity not found");
        identities[_user].kycLevel = _level;
        identities[_user].isVerified = _verified;
        emit KYCStatusUpdated(_user, _level, _verified);
    }

    function setSanctionStatus(address _user, bool _isSanctioned) external onlyAdmin {
        require(identities[_user].registeredAt > 0, "Identity not found");
        identities[_user].isSanctioned = _isSanctioned;
        emit SanctionStatusUpdated(_user, _isSanctioned);
    }

    function awardXP(address _user, uint256 _points) external onlyAdmin {
        require(identities[_user].registeredAt > 0, "Identity not found");
        identities[_user].xpScore += _points;
        emit XPScoreAwarded(_user, _points, identities[_user].xpScore);
    }

    // ERC-3643 Interface Compliance Methods
    function isVerified(address _userAddress) external view returns (bool) {
        return identities[_userAddress].isVerified && !identities[_userAddress].isSanctioned;
    }

    function getCountry(address _userAddress) external view returns (uint16) {
        return identities[_userAddress].countryCode;
    }

    function isSanctioned(address _userAddress) external view returns (bool) {
        return identities[_userAddress].isSanctioned;
    }

    function getIdentity(address _userAddress) external view returns (Identity memory) {
        return identities[_userAddress];
    }
}
