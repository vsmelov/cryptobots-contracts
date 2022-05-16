from brownie import *
from brownie import accounts as _accounts

if network.show_active() == 'rinkeby':
    gas_price = int(1.5 * 10**9)
    OLD_BOT_CORE_CONTRACT = '0x0D44BacB97bA46CC46A6F11B47433f4664fe6658'  # mainnet
    baseURI = 'https://path.to/token/'
    contractURI = 'https://path.to/contractMetadata/'
elif network.show_active() == 'mainnet':
    gas_price = None   # WARNING
    OLD_BOT_CORE_CONTRACT = '0xF7a6E15dfD5cdD9ef12711Bd757a9b6021ABf643'  # mainnet
    baseURI = 'https://path.to/token/'
    contractURI = 'https://path.to/contractMetadata/'
else:
    raise ValueError('unknown network')


def main():
    admin = _accounts.load('cryptobots-test', 'qwerty')

    wrapper = BotCoreWrapper.deploy(OLD_BOT_CORE_CONTRACT, baseURI, contractURI, {'from': admin, 'gas_price': gas_price})
    try:
        BotCoreWrapper.publish_source(wrapper)
    except ValueError as exc:
        if 'Contract source code already verified' not in str(exc):
            raise

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

    oil = OIL.deploy({'from': admin, 'gas_price': gas_price})
    try:
        OIL.publish_source(oil)
    except ValueError as exc:
        if 'Contract source code already verified' not in str(exc):
            raise
