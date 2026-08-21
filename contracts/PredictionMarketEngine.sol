// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title PredictionMarketEngine
 * @notice Unykorn.ai Event Contract & Outcome Liquidity Pool Engine.
 *         Supports binary bout winner markets, micro-events (KO Round 2, Submission),
 *         and tournament futures with automated protocol fee deduction (1.5%) and XP loyalty rewards.
 */

interface IERC3643Identity {
    function isVerified(address _user) external view returns (bool);
    function getCountry(address _user) external view returns (uint16);
}

contract PredictionMarketEngine {
    address public unykornAdmin;
    IERC3643Identity public identityRegistry;

    uint256 public constant PROTOCOL_FEE_BPS = 150; // 1.50% protocol fee
    uint256 public totalProtocolFeesCollected;

    enum MarketType { BinaryWinner, MethodOfVictory, RoundFinish, OverUnderStrikes, GrandPrixChampion }
    enum MarketState { Open, Locked, Resolved, Cancelled }

    struct OutcomeOption {
        string name;            // e.g. "Alex Pereira by KO/TKO", "Israel Adesanya by Decision"
        uint256 totalShares;    // Total pool shares staked
        uint256 poolAmount;     // Total minor currency in pool
    }

    struct Market {
        bytes32 marketId;
        bytes32 boutId;
        string title;
        MarketType marketType;
        MarketState state;
        uint8 outcomeCount;
        uint8 winningOutcomeIndex;
        uint256 totalPool;
        uint256 resolvedAt;
    }

    mapping(bytes32 => Market) public markets;
    mapping(bytes32 => OutcomeOption[]) public marketOptions;
    mapping(bytes32 => mapping(address => mapping(uint8 => uint256))) public userStakes; // marketId => user => outcome => amount

    event MarketCreated(bytes32 indexed marketId, bytes32 indexed boutId, string title, MarketType marketType);
    event StakePlaced(bytes32 indexed marketId, address indexed user, uint8 outcomeIndex, uint256 amount);
    event MarketResolved(bytes32 indexed marketId, uint8 winningOutcomeIndex, uint256 totalPayout);
    event WinningsClaimed(bytes32 indexed marketId, address indexed user, uint256 payoutAmount, uint256 xpAwarded);

    modifier onlyAdmin() {
        require(msg.sender == unykornAdmin, "Unauthorized: Admin only");
        _;
    }

    constructor(address _identityRegistry) {
        unykornAdmin = msg.sender;
        if (_identityRegistry != address(0)) {
            identityRegistry = IERC3643Identity(_identityRegistry);
        }
    }

    function createMarket(
        bytes32 _marketId,
        bytes32 _boutId,
        string calldata _title,
        MarketType _marketType,
        string[] calldata _optionNames
    ) external onlyAdmin {
        require(markets[_marketId].totalPool == 0 && markets[_marketId].state == MarketState.Open, "Market exists");
        require(_optionNames.length >= 2, "Min 2 outcome options required");

        markets[_marketId] = Market({
            marketId: _marketId,
            boutId: _boutId,
            title: _title,
            marketType: _marketType,
            state: MarketState.Open,
            outcomeCount: uint8(_optionNames.length),
            winningOutcomeIndex: 255,
            totalPool: 0,
            resolvedAt: 0
        });

        for (uint8 i = 0; i < _optionNames.length; i++) {
            marketOptions[_marketId].push(OutcomeOption({
                name: _optionNames[i],
                totalShares: 0,
                poolAmount: 0
            }));
        }

        emit MarketCreated(_marketId, _boutId, _title, _marketType);
    }

    function placeStake(bytes32 _marketId, uint8 _outcomeIndex, uint256 _amount) external {
        Market storage m = markets[_marketId];
        require(m.state == MarketState.Open, "Market is not open for staking");
        require(_outcomeIndex < m.outcomeCount, "Invalid outcome index");
        require(_amount > 0, "Amount must be > 0");

        // Identity compliance check if configured
        if (address(identityRegistry) != address(0)) {
            require(identityRegistry.isVerified(msg.sender), "User KYC not verified");
        }

        m.totalPool += _amount;
        marketOptions[_marketId][_outcomeIndex].poolAmount += _amount;
        marketOptions[_marketId][_outcomeIndex].totalShares += _amount;
        userStakes[_marketId][msg.sender][_outcomeIndex] += _amount;

        emit StakePlaced(_marketId, msg.sender, _outcomeIndex, _amount);
    }

    function resolveMarket(bytes32 _marketId, uint8 _winningOutcomeIndex) external onlyAdmin {
        Market storage m = markets[_marketId];
        require(m.state == MarketState.Open || m.state == MarketState.Locked, "Market not in resolvable state");
        require(_winningOutcomeIndex < m.outcomeCount, "Invalid winning index");

        m.state = MarketState.Resolved;
        m.winningOutcomeIndex = _winningOutcomeIndex;
        m.resolvedAt = block.timestamp;

        // Protocol fee deduction
        uint256 protocolFee = (m.totalPool * PROTOCOL_FEE_BPS) / 10000;
        totalProtocolFeesCollected += protocolFee;
        uint256 netPayoutPool = m.totalPool - protocolFee;

        emit MarketResolved(_marketId, _winningOutcomeIndex, netPayoutPool);
    }

    function claimWinnings(bytes32 _marketId) external returns (uint256 payout) {
        Market storage m = markets[_marketId];
        require(m.state == MarketState.Resolved, "Market not yet resolved");

        uint8 winnerIdx = m.winningOutcomeIndex;
        uint256 userShares = userStakes[_marketId][msg.sender][winnerIdx];
        require(userShares > 0, "No winning shares to claim");

        userStakes[_marketId][msg.sender][winnerIdx] = 0; // Prevent re-entrancy

        uint256 winningPool = marketOptions[_marketId][winnerIdx].poolAmount;
        uint256 protocolFee = (m.totalPool * PROTOCOL_FEE_BPS) / 10000;
        uint256 netPool = m.totalPool - protocolFee;

        payout = (userShares * netPool) / winningPool;
        uint256 xpAward = (payout / 100) * 5; // 5 XP per dollar won

        emit WinningsClaimed(_marketId, msg.sender, payout, xpAward);
        return payout;
    }

    function getMarketOptions(bytes32 _marketId) external view returns (OutcomeOption[] memory) {
        return marketOptions[_marketId];
    }
}
