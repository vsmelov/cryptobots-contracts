import time

from brownie import *
from brownie import accounts as _accounts

assert network.show_active() == 'rinkeby'

gas_price = int(1.5 * 10**9)

"""
Ecosystem DAO  25%, 3 year vesting linear (not locked)
Private Sale1 - 10% - 1 year lock up, 2  year linear vesting
Private Sale2 - 10% - 1 year lock up, 2 linear year linear vesting
Public  - 5%  6 month lock up, 6 month linear vesting (возможно будет 3)
Company - 15% - 1 year lock up, 2 year linear vesting
Founders - 15% -  1 year lock up, 2 year linear vesting
"""


def main():
    admin = _accounts.load('cryptobots-test', 'qwerty')

    bits = BITS.deploy({'from': admin, 'gas_price': gas_price})
    try:
        BITS.publish_source(bits)
    except ValueError as exc:
        if 'Contract source code already verified' not in str(exc):
            raise

    vesting = Vesting.deploy(bits, {'from': admin, 'gas_price': gas_price})
    try:
        Vesting.publish_source(vesting)
    except ValueError as exc:
        if 'Contract source code already verified' not in str(exc):
            raise

    total_supply = bits.totalSupply()
    assert total_supply == 10**9 * 10**18

    now = int(time.time())
    month = 30 * 24 * 3600
    year = 365 * 24 * 3600

    def create_vesting(lock, vestingPeriod, receiver, amount):
        tx = vesting.createVestingParams(
            0,  # tgePercentage
            now + lock,  # tge
            0,  # cliffDuration
            vestingPeriod,  # vestingDuration
            1,  # vestingInterval
            {"from": admin}
        )
        vestingParamsId = tx.events['vestingParamsId']
        bits.approve(vesting, amount, {"from": admin})
        vesting.createUserVesting(
            receiver,  # receiver
            amount,  # totalAmount
            vestingParamsId,  # vestingParamsId
            {"from": admin}
        )

    # EcosystemDAO
    create_vesting(
        lock=0,
        vestingPeriod=3 * 365 * 24 * 3600,
        receiver=admin,  # todo
        amount=total_supply * 25 // 100,
    )

    # PrivateSale1
    create_vesting(
        lock=1 * year,
        vestingPeriod=2 * year,
        receiver=admin,  # todo
        amount=total_supply * 10 // 100,
    )

    # PrivateSale2
    create_vesting(
        lock=1 * year,
        vestingPeriod=2 * year,
        receiver=admin,  # todo
        amount=total_supply * 10 // 100,
    )

    # Public
    create_vesting(
        lock=6 * month,
        vestingPeriod=6 * month,
        receiver=admin,  # todo
        amount=total_supply * 5 // 100,
    )

    # Company
    create_vesting(
        lock= 1 * year,
        vestingPeriod=2 * year,
        receiver=admin,  # todo
        amount=total_supply * 15 // 100,
    )

    # Founders
    create_vesting(
        lock= 1 * year,
        vestingPeriod=2 * year,
        receiver=admin,  # todo
        amount=total_supply * 15 // 100,
    )
