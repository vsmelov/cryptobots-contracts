from brownie import *
from brownie import reverts
from web3.constants import *

ADDRESS_ZERO = '0x0000000000000000000000000000000000000000'


def test_wrapper_setBaseURI(wrapper, admin):
    tx = wrapper.setBaseURI('xxx', {"from": admin})
    assert tx.events['BaseURISet']['value'] == 'xxx'
    assert wrapper.baseURI() == 'xxx'


def test_wrapper_setContractURI(wrapper, admin):
    tx = wrapper.setContractURI('xxx', {"from": admin})
    assert tx.events['ContractURISet']['value'] == 'xxx'
    assert wrapper.contractURI() == 'xxx'


def test_nonexistent_tokenURI(wrapper, admin):
    with reverts('ERC721Metadata: URI query for nonexistent token'):
        tx = wrapper.tokenURI(1, {"from": admin})


def test_incorrect_owner(wrapper, admin, users):
    with reverts('ERC721: owner query for nonexistent token'):
        tx = wrapper.unwrap(1, {"from": users[1]})


def test_wrap(wrapper, botcore, admin, user0):
    coo = botcore.cooAddress()
    tx = botcore.createPromoBot(0, user0, {"from": coo})
    bot_id = tx.events['Birth']['botId']
    botcore.approve(wrapper, bot_id, {"from": user0})
    tx = wrapper.wrap(bot_id, {"from": user0})

    assert tx.events['Transfer'][0]['from'] == user0
    assert tx.events['Transfer'][0]['to'] == wrapper
    assert tx.events['Transfer'][0]['tokenId'] == bot_id
    assert tx.events['Transfer'][1]['from'] == ADDRESS_ZERO
    assert tx.events['Transfer'][1]['to'] == user0
    assert tx.events['Transfer'][1]['tokenId'] == bot_id


def test_wrap_getBot(wrapper, botcore, admin, user0):
    coo = botcore.cooAddress()
    tx = botcore.createPromoBot(0, user0, {"from": coo})
    bot_id = tx.events['Birth']['botId']
    botcore.approve(wrapper, bot_id, {"from": user0})
    tx = wrapper.wrap(bot_id, {"from": user0})

    assert tx.events['Transfer'][0]['from'] == user0
    assert tx.events['Transfer'][0]['to'] == wrapper
    assert tx.events['Transfer'][0]['tokenId'] == bot_id
    assert tx.events['Transfer'][1]['from'] == ADDRESS_ZERO
    assert tx.events['Transfer'][1]['to'] == user0
    assert tx.events['Transfer'][1]['tokenId'] == bot_id

    assert wrapper.getBot(bot_id) == botcore.getBot(bot_id)


def test_wrap_and_transfer(wrapper, botcore, admin, user0, user1):
    coo = botcore.cooAddress()
    tx = botcore.createPromoBot(0, user0, {"from": coo})
    bot_id = tx.events['Birth']['botId']
    botcore.approve(wrapper, bot_id, {"from": user0})
    tx = wrapper.wrap(bot_id, {"from": user0})

    assert tx.events['Transfer'][0]['from'] == user0
    assert tx.events['Transfer'][0]['to'] == wrapper
    assert tx.events['Transfer'][0]['tokenId'] == bot_id
    assert tx.events['Transfer'][1]['from'] == ADDRESS_ZERO
    assert tx.events['Transfer'][1]['to'] == user0
    assert tx.events['Transfer'][1]['tokenId'] == bot_id

    wrapper.transfer(user1, bot_id, {"from": user0})
    assert wrapper.ownerOf(bot_id) == user1


def test_wrap_and_transfer_many(wrapper, botcore, admin, user0, user1):
    coo = botcore.cooAddress()

    tx = botcore.createPromoBot(0, user0, {"from": coo})
    bot_id0 = tx.events['Birth']['botId']
    botcore.approve(wrapper, bot_id0, {"from": user0})
    tx = wrapper.wrap(bot_id0, {"from": user0})

    tx = botcore.createPromoBot(1, user0, {"from": coo})
    bot_id1 = tx.events['Birth']['botId']
    botcore.approve(wrapper, bot_id1, {"from": user0})
    tx = wrapper.wrap(bot_id1, {"from": user0})

    wrapper.transferMany([user1, user1], [bot_id0, bot_id1], {"from": user0})
    assert wrapper.ownerOf(bot_id0) == user1
    assert wrapper.ownerOf(bot_id1) == user1


def test_wrap_and_transfer_many_lengths_mismatch(wrapper, botcore, admin, user0, user1):
    coo = botcore.cooAddress()

    tx = botcore.createPromoBot(0, user0, {"from": coo})
    bot_id0 = tx.events['Birth']['botId']
    botcore.approve(wrapper, bot_id0, {"from": user0})
    tx = wrapper.wrap(bot_id0, {"from": user0})

    tx = botcore.createPromoBot(1, user0, {"from": coo})
    bot_id1 = tx.events['Birth']['botId']
    botcore.approve(wrapper, bot_id1, {"from": user0})
    tx = wrapper.wrap(bot_id1, {"from": user0})

    with reverts('Wrapper: lengths mismatch'):
        wrapper.transferMany([user1, user1], [bot_id0], {"from": user0})


def test_wrap_and_transferFrom_many(wrapper, botcore, admin, user0, user1, user2):
    coo = botcore.cooAddress()

    tx = botcore.createPromoBot(0, user0, {"from": coo})
    bot_id0 = tx.events['Birth']['botId']
    botcore.approve(wrapper, bot_id0, {"from": user0})
    tx = wrapper.wrap(bot_id0, {"from": user0})

    tx = botcore.createPromoBot(1, user0, {"from": coo})
    bot_id1 = tx.events['Birth']['botId']
    botcore.approve(wrapper, bot_id1, {"from": user0})
    tx = wrapper.wrap(bot_id1, {"from": user0})

    wrapper.approveMany([user1, user1], [bot_id0, bot_id1], {"from": user0})

    wrapper.transferFromMany([user0, user0], [user2, user2], [bot_id0, bot_id1], {"from": user1})
    assert wrapper.ownerOf(bot_id0) == user2
    assert wrapper.ownerOf(bot_id1) == user2


def test_wrap_and_transferFrom_many_lengths_mismatch(wrapper, botcore, admin, user0, user1, user2):
    coo = botcore.cooAddress()

    tx = botcore.createPromoBot(0, user0, {"from": coo})
    bot_id0 = tx.events['Birth']['botId']
    botcore.approve(wrapper, bot_id0, {"from": user0})
    tx = wrapper.wrap(bot_id0, {"from": user0})

    tx = botcore.createPromoBot(1, user0, {"from": coo})
    bot_id1 = tx.events['Birth']['botId']
    botcore.approve(wrapper, bot_id1, {"from": user0})
    tx = wrapper.wrap(bot_id1, {"from": user0})


    with reverts('Wrapper: lengths mismatch'):
        wrapper.approveMany([user1, user1], [bot_id0], {"from": user0})

    wrapper.approveMany([user1, user1], [bot_id0, bot_id1], {"from": user0})

    with reverts('Wrapper: lengths mismatch'):
        wrapper.transferFromMany([user0, user0], [user2], [bot_id0, bot_id1], {"from": user1})

    with reverts('Wrapper: lengths mismatch'):
        wrapper.transferFromMany([user0, user0], [user2, user2], [bot_id0], {"from": user1})


def test_wrap_pause(wrapper, botcore, admin, user0):
    coo = botcore.cooAddress()
    tx = botcore.createPromoBot(0, user0, {"from": coo})
    bot_id = tx.events['Birth']['botId']
    botcore.approve(wrapper, bot_id, {"from": user0})

    wrapper.pause({"from": admin})

    with reverts('ERC721Pausable: token transfer while paused'):
        wrapper.wrap(bot_id, {"from": user0})


def test_wrap_pause_unpause(wrapper, botcore, admin, user0):
    coo = botcore.cooAddress()
    tx = botcore.createPromoBot(0, user0, {"from": coo})
    bot_id = tx.events['Birth']['botId']
    botcore.approve(wrapper, bot_id, {"from": user0})

    wrapper.pause({"from": admin})
    wrapper.unpause({"from": admin})

    tx = wrapper.wrap(bot_id, {"from": user0})

    assert tx.events['Transfer'][0]['from'] == user0
    assert tx.events['Transfer'][0]['to'] == wrapper
    assert tx.events['Transfer'][0]['tokenId'] == bot_id
    assert tx.events['Transfer'][1]['from'] == ADDRESS_ZERO
    assert tx.events['Transfer'][1]['to'] == user0
    assert tx.events['Transfer'][1]['tokenId'] == bot_id

    wrapper.setBaseURI('xxx/', {"from": admin})
    assert wrapper.tokenURI(bot_id, {"from": admin}) == f'xxx/{bot_id}'


def test_wrap_and_check_token_uri(wrapper, botcore, admin, user0):
    coo = botcore.cooAddress()
    tx = botcore.createPromoBot(0, user0, {"from": coo})
    bot_id = tx.events['Birth']['botId']
    botcore.approve(wrapper, bot_id, {"from": user0})
    tx = wrapper.wrap(bot_id, {"from": user0})

    assert tx.events['Transfer'][0]['from'] == user0
    assert tx.events['Transfer'][0]['to'] == wrapper
    assert tx.events['Transfer'][0]['tokenId'] == bot_id
    assert tx.events['Transfer'][1]['from'] == ADDRESS_ZERO
    assert tx.events['Transfer'][1]['to'] == user0
    assert tx.events['Transfer'][1]['tokenId'] == bot_id

    wrapper.setBaseURI('xxx/', {"from": admin})
    assert wrapper.tokenURI(bot_id, {"from": admin}) == f'xxx/{bot_id}'


def test_wrap_many(wrapper, botcore, admin, user0):
    coo = botcore.cooAddress()
    tx = botcore.createPromoBot(0, user0, {"from": coo})
    bot_id0 = tx.events['Birth']['botId']

    tx = botcore.createPromoBot(0, user0, {"from": coo})
    bot_id1 = tx.events['Birth']['botId']

    botcore.approve(wrapper, bot_id0, {"from": user0})
    botcore.approve(wrapper, bot_id1, {"from": user0})
    tx = wrapper.wrapMany([bot_id0, bot_id1], {"from": user0})

    assert tx.events['Transfer'][0]['from'] == user0
    assert tx.events['Transfer'][0]['to'] == wrapper
    assert tx.events['Transfer'][0]['tokenId'] == bot_id0
    assert tx.events['Transfer'][1]['from'] == ADDRESS_ZERO
    assert tx.events['Transfer'][1]['to'] == user0
    assert tx.events['Transfer'][1]['tokenId'] == bot_id0

    assert tx.events['Transfer'][2]['from'] == user0
    assert tx.events['Transfer'][2]['to'] == wrapper
    assert tx.events['Transfer'][2]['tokenId'] == bot_id1
    assert tx.events['Transfer'][3]['from'] == ADDRESS_ZERO
    assert tx.events['Transfer'][3]['to'] == user0
    assert tx.events['Transfer'][3]['tokenId'] == bot_id1


def test_unwrap(wrapper, botcore, admin, user0):
    coo = botcore.cooAddress()
    tx = botcore.createPromoBot(0, user0, {"from": coo})
    bot_id = tx.events['Birth']['botId']
    botcore.approve(wrapper, bot_id, {"from": user0})
    tx = wrapper.wrap(bot_id, {"from": user0})

    assert tx.events['Transfer'][0]['from'] == user0
    assert tx.events['Transfer'][0]['to'] == wrapper
    assert tx.events['Transfer'][0]['tokenId'] == bot_id
    assert tx.events['Transfer'][1]['from'] == ADDRESS_ZERO
    assert tx.events['Transfer'][1]['to'] == user0
    assert tx.events['Transfer'][1]['tokenId'] == bot_id
    assert botcore.ownerOf(bot_id) == wrapper
    assert wrapper.ownerOf(bot_id) == user0

    tx = wrapper.unwrap(bot_id, {"from": user0})
    assert tx.events['Transfer'][0]['from'] == user0
    assert tx.events['Transfer'][0]['to'] == ADDRESS_ZERO
    assert tx.events['Transfer'][0]['tokenId'] == bot_id
    assert tx.events['Transfer'][1]['from'] == wrapper
    assert tx.events['Transfer'][1]['to'] == user0
    assert tx.events['Transfer'][1]['tokenId'] == bot_id
    assert botcore.ownerOf(bot_id) == user0


def test_unwrap_fails(wrapper, botcore, admin, user0, user1):
    coo = botcore.cooAddress()
    tx = botcore.createPromoBot(0, user0, {"from": coo})
    bot_id = tx.events['Birth']['botId']
    botcore.approve(wrapper, bot_id, {"from": user0})
    tx = wrapper.wrap(bot_id, {"from": user0})

    assert tx.events['Transfer'][0]['from'] == user0
    assert tx.events['Transfer'][0]['to'] == wrapper
    assert tx.events['Transfer'][0]['tokenId'] == bot_id
    assert tx.events['Transfer'][1]['from'] == ADDRESS_ZERO
    assert tx.events['Transfer'][1]['to'] == user0
    assert tx.events['Transfer'][1]['tokenId'] == bot_id
    assert botcore.ownerOf(bot_id) == wrapper
    assert wrapper.ownerOf(bot_id) == user0

    with reverts('Wrapper: unwrap from incorrect owner'):
        tx = wrapper.unwrap(bot_id, {"from": user1})


def test_unwrap_many(wrapper, botcore, admin, user0):
    coo = botcore.cooAddress()
    tx = botcore.createPromoBot(0, user0, {"from": coo})
    bot_id0 = tx.events['Birth']['botId']

    tx = botcore.createPromoBot(0, user0, {"from": coo})
    bot_id1 = tx.events['Birth']['botId']

    botcore.approve(wrapper, bot_id0, {"from": user0})
    botcore.approve(wrapper, bot_id1, {"from": user0})
    tx = wrapper.wrapMany([bot_id0, bot_id1], {"from": user0})

    assert tx.events['Transfer'][0]['from'] == user0
    assert tx.events['Transfer'][0]['to'] == wrapper
    assert tx.events['Transfer'][0]['tokenId'] == bot_id0
    assert tx.events['Transfer'][1]['from'] == ADDRESS_ZERO
    assert tx.events['Transfer'][1]['to'] == user0
    assert tx.events['Transfer'][1]['tokenId'] == bot_id0

    assert tx.events['Transfer'][2]['from'] == user0
    assert tx.events['Transfer'][2]['to'] == wrapper
    assert tx.events['Transfer'][2]['tokenId'] == bot_id1
    assert tx.events['Transfer'][3]['from'] == ADDRESS_ZERO
    assert tx.events['Transfer'][3]['to'] == user0
    assert tx.events['Transfer'][3]['tokenId'] == bot_id1


    tx = wrapper.unwrapMany([bot_id0, bot_id1], {"from": user0})
    assert tx.events['Transfer'][0]['from'] == user0
    assert tx.events['Transfer'][0]['to'] == ADDRESS_ZERO
    assert tx.events['Transfer'][0]['tokenId'] == bot_id0
    assert tx.events['Transfer'][1]['from'] == wrapper
    assert tx.events['Transfer'][1]['to'] == user0
    assert tx.events['Transfer'][1]['tokenId'] == bot_id0
    assert botcore.ownerOf(bot_id0) == user0

    assert tx.events['Transfer'][2]['from'] == user0
    assert tx.events['Transfer'][2]['to'] == ADDRESS_ZERO
    assert tx.events['Transfer'][2]['tokenId'] == bot_id1
    assert tx.events['Transfer'][3]['from'] == wrapper
    assert tx.events['Transfer'][3]['to'] == user0
    assert tx.events['Transfer'][3]['tokenId'] == bot_id1
    assert botcore.ownerOf(bot_id1) == user0


def test_unwrap_many_fails(wrapper, botcore, admin, user0, user1):
    coo = botcore.cooAddress()
    tx = botcore.createPromoBot(0, user0, {"from": coo})
    bot_id0 = tx.events['Birth']['botId']

    tx = botcore.createPromoBot(0, user0, {"from": coo})
    bot_id1 = tx.events['Birth']['botId']

    botcore.approve(wrapper, bot_id0, {"from": user0})
    botcore.approve(wrapper, bot_id1, {"from": user0})
    tx = wrapper.wrapMany([bot_id0, bot_id1], {"from": user0})

    assert tx.events['Transfer'][0]['from'] == user0
    assert tx.events['Transfer'][0]['to'] == wrapper
    assert tx.events['Transfer'][0]['tokenId'] == bot_id0
    assert tx.events['Transfer'][1]['from'] == ADDRESS_ZERO
    assert tx.events['Transfer'][1]['to'] == user0
    assert tx.events['Transfer'][1]['tokenId'] == bot_id0

    assert tx.events['Transfer'][2]['from'] == user0
    assert tx.events['Transfer'][2]['to'] == wrapper
    assert tx.events['Transfer'][2]['tokenId'] == bot_id1
    assert tx.events['Transfer'][3]['from'] == ADDRESS_ZERO
    assert tx.events['Transfer'][3]['to'] == user0
    assert tx.events['Transfer'][3]['tokenId'] == bot_id1

    with reverts('Wrapper: unwrap from incorrect owner'):
        tx = wrapper.unwrapMany([bot_id0, bot_id1], {"from": user1})
