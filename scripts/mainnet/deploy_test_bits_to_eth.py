import os

from brownie import *
from brownie import accounts as _accounts

# gas_price = None
if network.show_active() == 'mainnet':
    gas_price = 20 * 10**9   # WARNING
else:
    raise ValueError('unknown network')


def main():
    admin = _accounts.load('brave_main', os.environ['BRAVE_MAIN_PASS'])

    bits = TestBITS.deploy({'from': admin, 'gas_price': gas_price})  # 0x4b90b7AE33A9E88dED786E38Db57D4ee3bD9E611
    try:
        TestBITS.publish_source(bits)
    except ValueError as exc:
        if 'Contract source code already verified' not in str(exc):
            raise
