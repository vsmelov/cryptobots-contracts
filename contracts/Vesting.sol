// SPDX-License-Identifier: MIT
pragma solidity 0.8.10;

import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import '@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol';

import "./libraries/PercentageVestingLibrary.sol";


// @notice does not work with deflationary tokens (BITS and OIL are not deflationary)
contract Vesting is Ownable {
    using SafeMath for uint256;
    using SafeERC20 for IERC20;
    using PercentageVestingLibrary for PercentageVestingLibrary.Data;

    struct VestingPool {
        PercentageVestingLibrary.Data data;
        uint256 totalAmount;
        uint256 allocatedAmount;
    }

    struct UserVesting {
        address receiver;
        uint256 totalAmount;
        uint256 withdrawnAmount;
        uint256 vestingPoolId;
        bool cancelIsRestricted;
    }

    IERC20 public coin;
    uint256 public totalUserVestingsCount;
    uint256 public totalVestingPoolsCount;
    mapping (address /* user wallet */ => uint256[] /* list of vesting ids */) public userVestingIds;
    mapping (uint256 /* userVestingId */ => UserVesting) public userVestings;
    mapping (uint256 /* vestingPoolId */ => VestingPool) public vestingPools;

    event VestingPoolCreated(
        uint256 indexed vestingPoolId,
        uint16 tgePercentage,
        uint32 tge,
        uint32 cliffDuration,
        uint32 vestingDuration,
        uint32 vestingInterval,
        uint256 totalAmount
    );
    event UserVestingCreated (
        uint256 indexed userVestingId,
        address receiver,
        uint256 totalAmount,
        uint256 vestingPoolId,
        bool cancelIsRestricted
    );
    event UserVestingCanceled(
        uint256 indexed userVestingId,
        uint256 restAmount
    );
    event Withdrawn(
        uint256 indexed userVestingId,
        address indexed user,
        uint256 amount
    );
    event TotalWithdrawn(
        address indexed user,
        uint256 amount
    );

    function userVestingsLength(address user) external view returns(uint256 length) {
        length = userVestingIds[user].length;
    }

    constructor(address coinAddress) Ownable() {
        require(coinAddress != address(0), "ZERO_ADDRESS");
        coin = IERC20(coinAddress);
    }

    function getVestingPool(uint256 vestingPoolId) external view returns(
        uint16 tgePercentage,
        uint32 tge,
        uint32 cliffDuration,
        uint32 vestingDuration,
        uint32 vestingInterval,
        uint256 totalAmount,
        uint256 allocatedAmount
    ) {
        (
            tgePercentage,
            tge,
            cliffDuration,
            vestingDuration,
            vestingInterval
        ) = vestingPools[vestingPoolId].data.vestingDetails();
        totalAmount = vestingPools[vestingPoolId].totalAmount;
        allocatedAmount = vestingPools[vestingPoolId].allocatedAmount;
    }

    function getVestingParams(uint256 vestingPoolId) external view returns(
        uint16 tgePercentage,
        uint32 tge,
        uint32 cliffDuration,
        uint32 vestingDuration,
        uint32 vestingInterval
    ) {
        return vestingPools[vestingPoolId].data.vestingDetails();
    }

    function getUserVesting(uint256 userVestingId) public view returns(
        address receiver,
        uint256 totalAmount,
        uint256 withdrawnAmount,
        uint256 vestingPoolId,
        uint256 avaliable,
        bool cancelIsRestricted
    ) {
        UserVesting storage o = userVestings[userVestingId];
        require(o.receiver != address(0), "NOT_EXISTS");

        receiver = o.receiver;
        totalAmount = o.totalAmount;
        withdrawnAmount = o.withdrawnAmount;
        vestingPoolId = o.vestingPoolId;
        avaliable = vestingPools[o.vestingPoolId].data.availableOutputAmount({
            totalAmount: o.totalAmount,
            withdrawnAmount: o.withdrawnAmount
        });
        cancelIsRestricted = o.cancelIsRestricted;
    }

    function getWalletInfo(address wallet) external view returns(
        uint256 totalAmount,
        uint256 alreadyWithdrawn,
        uint256 availableToWithdraw
    ) {
        totalAmount = 0;
        alreadyWithdrawn = 0;
        availableToWithdraw = 0;

        uint256 totalVestingsCount = userVestingIds[wallet].length;
        for (uint256 i; i < totalVestingsCount; i++) {
            uint256 userVestingId = userVestingIds[wallet][i];
            (
                address _receiver,
                uint256 _totalAmount,
                uint256 _withdrawnAmount,
                uint256 _vestingParamsId,
                uint256 _avaliable,
                /* bool cancelIsRestricted */
            ) = getUserVesting(userVestingId);
            totalAmount += _totalAmount;
            alreadyWithdrawn += _withdrawnAmount;
            availableToWithdraw += _avaliable;
        }
    }

    function createVestingPools(
        uint16[] memory tgePercentageList,
        uint32[] memory tgeList,
        uint32[] memory cliffDurationList,
        uint32[] memory vestingDurationList,
        uint32[] memory vestingIntervalList,
        uint256[] memory totalAmountList
    ) external onlyOwner {
        uint256 length = tgePercentageList.length;
        require(tgeList.length == length, "length mismatch");
        require(cliffDurationList.length == length, "length mismatch");
        require(vestingDurationList.length == length, "length mismatch");
        require(vestingIntervalList.length == length, "length mismatch");
        require(totalAmountList.length == length, "length mismatch");
        for (uint256 i=0; i < length; i++) {
            createVestingPool({
                tgePercentage: tgePercentageList[i],
                tge: tgeList[i],
                cliffDuration: cliffDurationList[i],
                vestingDuration: vestingDurationList[i],
                vestingInterval: vestingIntervalList[i],
                totalAmount: totalAmountList[i]
            });
        }
    }

    function createVestingPool(
        uint16 tgePercentage,
        uint32 tge,
        uint32 cliffDuration,
        uint32 vestingDuration,
        uint32 vestingInterval,
        uint256 totalAmount
    ) public onlyOwner {
        uint256 vestingPoolId = totalVestingPoolsCount++;
        vestingPools[vestingPoolId].data.initialize({
            tgePercentage: tgePercentage,
            tge: tge,
            cliffDuration: cliffDuration,
            vestingDuration: vestingDuration,
            vestingInterval: vestingInterval
        });
        vestingPools[vestingPoolId].totalAmount = totalAmount;
        coin.safeTransferFrom(msg.sender, address(this), totalAmount);
        emit VestingPoolCreated({
            vestingPoolId: vestingPoolId,
            tgePercentage: tgePercentage,
            tge: tge,
            cliffDuration: cliffDuration,
            vestingDuration: vestingDuration,
            vestingInterval: vestingInterval,
            totalAmount: totalAmount
        });
    }

    function createUserVesting(
        address receiver,
        uint256 totalAmount,
        uint256 vestingPoolId,
        bool cancelIsRestricted
    ) public onlyOwner {
        require(receiver != address(0), "ZERO_ADDRESS");
        require(totalAmount > 0, "ZERO_AMOUNT");
        VestingPool storage vestingPool = vestingPools[vestingPoolId];

        vestingPool.allocatedAmount += totalAmount;
        require(vestingPool.allocatedAmount <= vestingPool.totalAmount, "too much allocated");

        require(vestingPool.data.tge > 0, "VESTING_PARAMS_NOT_EXISTS");
        uint256 userVestingId = totalUserVestingsCount++;
        userVestings[userVestingId] = UserVesting({
            receiver: receiver,
            totalAmount: totalAmount,
            withdrawnAmount: 0,
            vestingPoolId: vestingPoolId,
            cancelIsRestricted: cancelIsRestricted
        });
        userVestingIds[receiver].push(userVestingId);
        emit UserVestingCreated({
            userVestingId: userVestingId,
            receiver: receiver,
            totalAmount: totalAmount,
            vestingPoolId: vestingPoolId,
            cancelIsRestricted: cancelIsRestricted
        });
    }

    function createUserVestings(
        address[] memory receiverList,
        uint256[] memory totalAmountList,
        uint256[] memory vestingPoolIdList,
        bool[] memory cancelIsRestrictedList
    ) external onlyOwner {
        uint256 length = receiverList.length;
        require(totalAmountList.length == length, "length mismatch");
        require(vestingPoolIdList.length == length, "length mismatch");
        require(cancelIsRestrictedList.length == length, "length mismatch");
        for (uint i = 0; i < length; i++) {
            createUserVesting({
                receiver: receiverList[i],
                totalAmount: totalAmountList[i],
                vestingPoolId: vestingPoolIdList[i],
                cancelIsRestricted: cancelIsRestrictedList[i]
            });
        }
    }

    /// @notice cancel user vesting, returns the rest of tokens to the owner account
    /// @param userVestingId userVestingId
    /// @param indexInUserVestingIds index of `userVestingId` inside userVestingIds[receiver], to get rid of onchain for-loop to search
    function cancelUserVesting(uint256 userVestingId, uint256 indexInUserVestingIds) external onlyOwner {
        UserVesting storage userVesting = userVestings[userVestingId];
        address receiver = userVesting.receiver;
        require(receiver != address(0), "NOT_EXISTS");
        require(!userVesting.cancelIsRestricted, "update is restricted");

        uint256 restAmount = userVesting.totalAmount - userVesting.withdrawnAmount;

        // remove from userVestingIds
        require(indexInUserVestingIds < userVestingIds[receiver].length, "indexInUserVestingIds is out of range");
        require(userVestingIds[receiver][indexInUserVestingIds] == userVestingId, "wrong indexInUserVestingIds");
        if (indexInUserVestingIds != userVestingIds[msg.sender].length-1) {
            userVestingIds[receiver][indexInUserVestingIds] = userVestingIds[receiver][userVestingIds[msg.sender].length-1];
        }
        userVestingIds[receiver].pop();

        coin.safeTransfer(owner(), restAmount);
        emit UserVestingCanceled({
            userVestingId: userVestingId,
            restAmount: restAmount
        });
    }

    function withdraw(uint256 userVestingId) public {
        UserVesting memory userVesting = userVestings[userVestingId];
        require(userVesting.receiver == msg.sender, "NOT_RECEIVER");
        uint256 amountToWithdraw = vestingPools[userVesting.vestingPoolId].data.availableOutputAmount({
            totalAmount: userVesting.totalAmount,
            withdrawnAmount: userVesting.withdrawnAmount
        });

        userVestings[userVestingId].withdrawnAmount += amountToWithdraw;
        coin.safeTransfer(msg.sender, amountToWithdraw);
        emit Withdrawn({
            userVestingId: userVestingId,
            user: msg.sender,
            amount: amountToWithdraw
        });
    }

    function withdrawAll() external {
        uint256 totalVestingsCount = userVestingIds[msg.sender].length;
        uint256 totalAmountToWithdraw;
        for (uint256 i; i < totalVestingsCount; i++) {
            uint256 userVestingId = userVestingIds[msg.sender][i];
            UserVesting storage userVesting = userVestings[userVestingId];
            uint256 amountToWithdraw = vestingPools[userVesting.vestingPoolId].data.availableOutputAmount({
                totalAmount: userVesting.totalAmount,
                withdrawnAmount: userVesting.withdrawnAmount
            });
            if (amountToWithdraw > 0) {
                userVestings[userVestingId].withdrawnAmount += amountToWithdraw;
                totalAmountToWithdraw += amountToWithdraw;
                emit Withdrawn({
                    userVestingId: userVestingId,
                    user: msg.sender,
                    amount: amountToWithdraw
                });
            }
        }
        if (totalAmountToWithdraw > 0) {
            coin.safeTransfer(msg.sender, totalAmountToWithdraw);
        }
        emit TotalWithdrawn({user: msg.sender, amount: totalAmountToWithdraw});
    }
}
