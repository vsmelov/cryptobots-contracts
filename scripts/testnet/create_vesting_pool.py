import time

from brownie import *
from brownie import accounts as _accounts

assert network.show_active() == 'rinkeby'

gas_price = int(1.5 * 10**9)  # warning: high than AVG to do transactions faster


def main():
    admin = _accounts.load('cryptobots-test', 'qwerty')
    new_admin = '0x04C925BBf8735b937BC0f12ba0113f8e821123A3'

    bits = Contract.from_abi('BITS', '0xB68be4faE1acAa03A8f30C46e1BCb5e7Db97Cb6C', BITS.abi)
    vesting = Contract.from_abi('Vesting', '0x64DC71Fb72EC0006CB6044474bf6c9100c6Cf640', Vesting.abi)

    now = int(time.time())
    month = 30 * 24 * 3600
    year = 365 * 24 * 3600

    def create_vesting_pool(lock, vestingPeriod, amount):
        bits.approve(vesting, amount, {"from": admin})
        tx = vesting.createVestingPool(
            0,  # tgePercentage
            now + lock,  # tge
            0,  # cliffDuration
            vestingPeriod,  # vestingDuration
            1,  # vestingInterval
            amount,
            {"from": admin}
        )
        vestingPoolId = tx.events['VestingPoolCreated']['vestingPoolId']
        print(f'created {vestingPoolId=}')
        return vestingPoolId

    vestingPoolId = create_vesting_pool(3 * month, 6 * month, 10*10**6)

    tx = vesting.createUserVesting(
        admin,  # receiver
        10**6,  # totalAmount,
        vestingPoolId,  # vestingPoolId,
        False,  # cancelIsRestricted
    )
    userVestingId = tx.events['UserVestingCreated']['userVestingId']
    print(f'created {userVestingId=}')
