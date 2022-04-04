from brownie import *
import pytest


@pytest.fixture
def admin(accounts):
    return accounts[0]


@pytest.fixture
def users(accounts):
    return accounts[1:]


@pytest.fixture
def user0(users):
    return users[0]


@pytest.fixture
def user1(users):
    return users[1]


@pytest.fixture
def user2(users):
    return users[2]


@pytest.fixture
def wrapper(admin, users, botcore):
    baseURI = 'https://some.base/path/to/token/'
    contractURI = 'https://some.path/to/contractMetadata/'
    contract = BotCoreWrapper.deploy(botcore, baseURI, contractURI, {"from": admin})
    return contract


@pytest.fixture
def botcore(admin, users):
    contract = Contract.from_abi("BotCore", "0xF7a6E15dfD5cdD9ef12711Bd757a9b6021ABf643", BotCore.abi)
    return contract


@pytest.fixture
def bits(admin):
    contract = BITS.deploy({"from": admin})
    return contract


@pytest.fixture
def vesting(admin, bits):
    contract = Vesting.deploy(bits, {"from": admin})
    return contract
