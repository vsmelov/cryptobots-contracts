import os

from brownie import *
from brownie import accounts as _accounts

# gas_price = None
if network.show_active() == 'mainnet':
    gas_price = 85 * 10**9   # WARNING
else:
    raise ValueError('unknown network')


def main():
    admin = _accounts.load('brave_main', os.environ['BRAVE_MAIN_PASS'])

    # oil = TestOIL.deploy({'from': admin, 'gas_price': gas_price})  # 0x970dA6Cd105Fe7aa2B18C904A064401835c723aE
    # try:
    #     TestOIL.publish_source(oil)
    # except ValueError as exc:
    #     if 'Contract source code already verified' not in str(exc):
    #         raise

    oil = Contract.from_abi("TestOIL", "0x970dA6Cd105Fe7aa2B18C904A064401835c723aE", TestOIL.abi)

    # from https://docs.polygon.technology/docs/develop/ethereum-polygon/mintable-assets/
    oil.grantRole(oil.PREDICATE_ROLE(), '0x9923263fA127b3d1484cFD649df8f1831c2A74e4', {'from': admin, 'gas_price': gas_price})
