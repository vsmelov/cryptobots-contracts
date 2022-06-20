import os

from brownie import *
from brownie import accounts as _accounts

gas_price = None
assert network.show_active() == 'polygon-main'


def main():
    # https://docs.polygon.technology/docs/develop/ethereum-polygon/mintable-assets/
    admin = _accounts.load('brave_main', os.environ['BRAVE_MAIN_PASS'])
    child = ChildMintableERC20.deploy(
        'TestOILChildMintable',
        'TestOILChildMintable',
        18,
        '0xA6FA4fB5f76172d178d61B04b0ecd319C5d1C0aa',
        {"from": admin, "gas_price": gas_price}
    )
    # child = Contract.from_abi("ChildMintableERC20", "...", ChildMintableERC20.abi)
    try:
        ChildMintableERC20.publish_source(child)
    except ValueError as exc:
        if 'Contract source code already verified' not in str(exc):
            raise

