import random
import time
import calendar


import requests
from aptos_sdk.client import ClientConfig
from aptos_sdk.account import Account
import pandas as pd
from web3 import Web3
from pyuseragents import random as random_user_agent

from logger import setup_gay_logger
from txn_staff import made_topaz_bid, mint_free_nft
from utils import get_verified_collection_ids
from galaxy import GalaxyAccountManager
from config import (MIN_SLEEP,
                    MAX_SLEEP)

config = ClientConfig()
config.max_gas_amount = 100_00
# This adjustment decreases the required balance for transaction execution.
# It changes the upper limit for gas, avoiding triggering tx termination.

EXEL = "data.xlsx"
df = pd.read_excel(EXEL, engine='openpyxl')
w3 = Web3(Web3.HTTPProvider('https://rpc.ankr.com/eth'))


def process_key(index, evm_key, aptos_key, mail):
    # Load the account using the provided key
    account_apt = Account.load_key(aptos_key)
    account_evm = w3.eth.account.from_key(evm_key)

    manager = GalaxyAccountManager(account_apt, account_evm)

    address_apt = account_apt.address()
    address_evm = account_evm.address

    logger = setup_gay_logger(f"Acc N{index} | {address_apt}")
    logger.info(f"Processing started")

    # # Fetch verified collection IDs
    # verified_collection_ids = get_verified_collection_ids()
    # logger.info("Retrieved verified collection IDs")
    #
    # # Choose a collection for bidding
    # chosen_collection_for_bid = random.choice(list(verified_collection_ids))
    # contract, name = chosen_collection_for_bid.split("::")
    # logger.info(f"Chosen collection for bid: {name}")
    #
    # # Make a bid
    # bid = made_topaz_bid(account_apt, contract, name)
    # if bid == 1:
    #     return 1
    #
    # # Retrieve available free mints (currently out of use due to wapal.io page lags)
    # # free_mints = get_available_free_mints()
    # free_mints = [
    #     '0xa79267255727285e55bc42d34134ffa2133b6983391846810d39f094fb5f1c87::Make Every M🌐ve Count.'
    # ]
    #
    # # logger.info("Retrieved list of available free mints")
    #
    # # Choose a free mint
    # chosen_free_mint = random.choice(list(free_mints))
    # contract1, name1 = chosen_free_mint.split("::")
    # logger.info(f"Chosen free mint collection: {name1}")
    #
    # # Mint the chosen free mint
    # mint = mint_free_nft(account_apt, contract1)
    # if mint == 1:
    #     return 1

    token = manager.sign_in_evm()
    manager.create_new_account(token, 'EVM')
    manager.update_user_address(token)
    data = manager.get_basic_user_info(token, address_evm)

    if data["data"]["addressInfo"]["hasAptosAddress"] is True:
        logger.info(f"Processing completed for account {address_apt}")
        logger.info('It now registered on galaxy')
        return 0


for index, row in df.iterrows():
    if pd.notna(row['Done?']):
        continue

    evm_key = row['EVM Key']
    aptos_key = row['Aptos Key']
    mail = row['Mail']

    try:
        result = process_key(index, evm_key, aptos_key, mail)
        if result == 0:
            df.at[index, 'Done?'] = 1  # Mark as done
            df.to_excel(EXEL, index=False)
            time.sleep(random.randint(MIN_SLEEP, MAX_SLEEP))
        else:
            continue
    except Exception as e:
        print(f"Error processing row {index}: {e}")
