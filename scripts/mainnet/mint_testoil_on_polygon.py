import os
from brownie import *

TestOIL_ETH = '0x970dA6Cd105Fe7aa2B18C904A064401835c723aE'
TestOILChildMintable_Polygon = '0xA3ea90482679A2Feb92709EB13a9b774796535F6'


def main():
    assert network.show_active() == 'polygon-main'
    admin = accounts.load('brave_main', os.environ['BRAVE_MAIN_PASS'])
    child = Contract.from_abi('Child', TestOILChildMintable_Polygon, ChildMintableERC20.abi)
    decimals = child.decimals()
    child.mint(admin, 1000 * 10 ** decimals, {"from": admin})
