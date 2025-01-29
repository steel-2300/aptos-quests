import random
from datetime import datetime

from aptos_sdk.client import ClientConfig
from aptos_sdk.client import RestClient

from logger import setup_gay_logger


ClientConfig.max_gas_amount = 100_00
# This adjustment decreases the required balance for transaction execution.
# It changes the upper limit for gas, avoiding trigger safety shut down.

Rest_Client = RestClient("https://fullnode.mainnet.aptoslabs.com/v1")

def submit_and_log_transaction(account, payload, logger):
    try:
        txn = Rest_Client.submit_transaction(account, payload)
        Rest_Client.wait_for_transaction(txn)
        logger.info(f'Success: https://explorer.aptoslabs.com/txn/{txn}?network=mainnet')
        return 0
    except AssertionError as e:
        logger.error(f"AssertionError caught: {e}")
        return 1
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}")
        return 1


def made_topaz_bid(account, contract: str, name: str):
    logger = setup_gay_logger('made_topaz_bid')

    amount = random.randint(200, 300)
    amount_str = str(amount) + '000'
    amount = int(amount_str)
    hours = random.randint(1, 24)

    # Current Unix timestamp in microseconds
    current_unix_timestamp = int(datetime.utcnow().timestamp() * 1e6)
    # Convert hours to microseconds and subtract one hour in microseconds (required by topaz)
    expiration_timestamp = int(current_unix_timestamp + ((hours - 1) * 3600 * 1e6))

    payload = {
        "type": "entry_function_payload",
        "function": "0x2c7bccf7b31baf770fdbcc768d9e9cb3d87805e255355df5db32ac9a669010a2::collection_marketplace::bid",
        "type_arguments": [
            "0x1::aptos_coin::AptosCoin"
        ],
        "arguments": [
            str(amount),
            "1",
            str(expiration_timestamp),
            contract,
            name,
        ]
    }

    logger.info(f"Offer value: {amount / 10**8} | offer duration: {hours}h. ")
    return submit_and_log_transaction(account, payload, logger)


def mint_free_nft(account, contract: str):
    logger = setup_gay_logger('mint_free_mint')

    payload = {
        "type": "entry_function_payload",
        "function": "0x6547d9f1d481fdc21cd38c730c07974f2f61adb7063e76f9d9522ab91f090dac::candymachine::mint_script",
        "type_arguments": [],
        "arguments": [
            contract
        ]
    }

    return submit_and_log_transaction(account, payload, logger)
