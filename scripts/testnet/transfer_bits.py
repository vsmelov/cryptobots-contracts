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

    balance = bits.balanceOf(admin)
    print(f'{balance=}')
    bits.transfer(new_admin, int(balance/2), {"from": admin})
