import time

from brownie import *
from brownie import accounts as _accounts

assert network.show_active() == 'rinkeby'

gas_price = int(1.5 * 10**9)  # warning: high than AVG to do transactions faster


def main():
    admin = _accounts.load('cryptobots-test', 'qwerty')
    new_admin = '0x04C925BBf8735b937BC0f12ba0113f8e821123A3'

    bits = BITS.deploy({'from': admin, 'gas_price': gas_price})  # 0xB68be4faE1acAa03A8f30C46e1BCb5e7Db97Cb6C
    bits.grantRole(bits.DEFAULT_ADMIN_ROLE(), new_admin, {'from': admin, 'gas_price': gas_price})
    try:
        BITS.publish_source(bits)
    except ValueError as exc:
        if 'Contract source code already verified' not in str(exc):
            raise

    vesting = Vesting.deploy(bits, {'from': admin, 'gas_price': gas_price})  # 0x64DC71Fb72EC0006CB6044474bf6c9100c6Cf640
    vesting.transferOwnership(new_admin, {'from': admin, 'gas_price': gas_price})
    try:
        Vesting.publish_source(vesting)
    except ValueError as exc:
        if 'Contract source code already verified' not in str(exc):
            raise

    total_supply = bits.totalSupply()
    assert total_supply == 10**9 * 10**18
