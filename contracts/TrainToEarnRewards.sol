// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title TrainToEarnRewards
 * @notice "Get Paid to Train" Gym Rewards & Gamified Check-in Engine.
 *         Disburses World Liberty Financial USD1 stablecoin micro-rewards and XP Passport points
 *         for verified gym check-ins, belt ranking promotions, and tournament completions across
 *         BJJLink, TrainAlta, and UFC GYM BJJ franchise studios.
 */

interface IERC20Token {
    function transfer(address recipient, uint256 amount) external returns (bool);
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

interface IXPPassportRegistry {
    function awardXP(address _user, uint256 _points) external;
    function isVerified(address _user) external view returns (bool);
}

contract TrainToEarnRewards {
    address public unykornAdmin;
    IERC20Token public usd1Token; // World Liberty Financial USD1 Stablecoin
    IXPPassportRegistry public xpPassport;

    uint256 public rewardPerCheckInMinor = 250; // $2.50 USD1 per verified gym check-in (in cents)
    uint256 public xpPerCheckIn = 50;           // 50 XP per check-in
    uint256 public totalUSD1DisbursedMinor;
    uint256 public totalCheckInsVerified;

    mapping(address => uint256) public lastCheckInTimestamp;
    mapping(address => uint256) public userTotalRewardsMinor;
    mapping(address => bool) public authorizedGymBeacons; // UFC GYM BJJ & BJJLink verified beacons

    event GymCheckInVerified(address indexed athlete, address indexed gymBeacon, uint256 usd1AmountMinor, uint256 xpAwarded);
    event RewardPoolFunded(address indexed funder, uint256 amountMinor);
    event GymBeaconAuthorized(address indexed beacon, bool status);

    modifier onlyAdmin() {
        require(msg.sender == unykornAdmin, "Unauthorized: Admin only");
        _;
    }

    constructor(address _usd1Token, address _xpPassport) {
        unykornAdmin = msg.sender;
        usd1Token = IERC20Token(_usd1Token);
        xpPassport = IXPPassportRegistry(_xpPassport);
    }

    function setGymBeacon(address _beacon, bool _status) external onlyAdmin {
        authorizedGymBeacons[_beacon] = _status;
        emit GymBeaconAuthorized(_beacon, _status);
    }

    function setRewardAmounts(uint256 _usd1Minor, uint256 _xp) external onlyAdmin {
        rewardPerCheckInMinor = _usd1Minor;
        xpPerCheckIn = _xp;
    }

    /**
     * @notice Records a verified gym check-in (e.g. UFC GYM BJJ or TrainAlta Academy)
     */
    function recordGymCheckIn(address _athlete, address _gymBeacon) external {
        require(authorizedGymBeacons[_gymBeacon] || msg.sender == unykornAdmin, "Unauthorized gym beacon");
        require(block.timestamp >= lastCheckInTimestamp[_athlete] + 12 hours, "Check-in cooldown active (12h)");
        
        if (address(xpPassport) != address(0)) {
            require(xpPassport.isVerified(_athlete), "Athlete KYC not verified");
            xpPassport.awardXP(_athlete, xpPerCheckIn);
        }

        lastCheckInTimestamp[_athlete] = block.timestamp;
        userTotalRewardsMinor[_athlete] += rewardPerCheckInMinor;
        totalUSD1DisbursedMinor += rewardPerCheckInMinor;
        totalCheckInsVerified++;

        // Transfer USD1 micro-reward if funded
        if (address(usd1Token) != address(0) && usd1Token.balanceOf(address(this)) >= rewardPerCheckInMinor) {
            usd1Token.transfer(_athlete, rewardPerCheckInMinor);
        }

        emit GymCheckInVerified(_athlete, _gymBeacon, rewardPerCheckInMinor, xpPerCheckIn);
    }

    function fundRewardPool(uint256 _amountMinor) external {
        require(usd1Token.transferFrom(msg.sender, address(this), _amountMinor), "Funding transfer failed");
        emit RewardPoolFunded(msg.sender, _amountMinor);
    }
}
