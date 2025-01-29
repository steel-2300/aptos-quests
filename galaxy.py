# Standard library imports
import json
import random
import string
from datetime import datetime, timedelta
from time import time

# Third-party imports
import nltk
import requests
from aptos_sdk.account import Account
from eth_account.messages import encode_defunct
from nltk.corpus import words
from web3 import Web3

# Local imports
from logger import setup_gay_logger
from utils import galaxy_headers
from config import SMART_PROXY_URL

proxies = {
    'http': SMART_PROXY_URL,
    'https': SMART_PROXY_URL
}

# NLTK setup
nltk.download('words', quiet=True)

class GalaxyAccountManager:
    def __init__(self, account_apt, account_evm):
        self.account_apt = account_apt
        self.account_evm = account_evm
        self.galaxy_query = 'https://graphigo.prd.galaxy.eco/query'
        self.word_list = words.words()

    def update_user_address(self, galaxy_token):
        logger = setup_gay_logger("update_user_address")
        try:
            headers = galaxy_headers(galaxy_token)
            current_time = int(time())
            rounded_time = int(current_time - (current_time % 3600))
            apt_address = self.account_apt.address()
            message = (f"You are updating your Galaxy profile with aptos address APTOS:{apt_address} "
                       "Please sign the transaction to confirm.")
            full_message = f'APTOS\nmessage: {message}\nnonce: {time}'
            signature = self.account_apt.sign(full_message.encode('utf-8'))
            payload = {
                "operationName": "UpdateUserAddress",
                "variables": {
                    "input": {
                        "address": str(self.account_evm.address),
                        "addressType": "EVM",
                        "updateAddress": str(apt_address),
                        "updateAddressType": "APTOS",
                        "sig": str(signature.signature.hex()),
                        "sigNonce": str(rounded_time),
                        "addressPublicKey": str(self.account_apt.public_key())
                    }
                },
                "query": ("mutation UpdateUserAddress($input: UpdateUserAddressInput!) {"
                          "updateUserAddress(input: $input) { code message __typename }}")
            }
            response = requests.post(self.galaxy_query, headers=headers, json=payload, proxies=proxies)

            if response.status_code == 200:
                if 'errors' in response.json():
                    for error in response.json()['errors']:
                        if error.get('extensions', {}).get('code') == 1004:
                            logger.error("Address update error: The new address is tied to another address.")
                            return False
                elif 'data' in response.json():
                    logger.info("Address bind successfully.")
                    return True
            else:
                logger.error(f"Update user address request failed."
                             f"\nStatus code {response.status_code}"
                             f"\nResponse {response.text}")
                return None
        except Exception as e:
            logger.critical(f"Exception during the update user address request: {e}")
            return None

    def sign_in_evm(self):
        logger = setup_gay_logger('sign_in_evm')
        try:
            characters = string.ascii_letters + string.digits
            nonce = ''.join(random.choice(characters) for i in range(17))
            current_time = datetime.utcnow()
            seven_days_later = current_time + timedelta(days=7)
            issued_time = current_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            expiration_time = seven_days_later.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

            message = (f"galxe.com wants you to sign in with your Ethereum account:\n"
                       f"{self.account_evm.address}\n\n"
                       "Sign in with Ethereum to the app.\n\n"
                       "URI: https://galxe.com\n"
                       "Version: 1\n"
                       "Chain ID: 1\n"
                       f"Nonce: {nonce}\n"
                       f"Issued At: {issued_time}\n"
                       f"Expiration Time: {expiration_time}")

            signature = self.account_evm.sign_message(encode_defunct(text=message))

            data = {
                "operationName": "SignIn",
                "variables": {
                    "input": {
                        "address": self.account_evm.address,
                        "message": message,
                        "signature": signature.signature.hex(),
                        "addressType": "EVM"
                    }
                },
                "query": "mutation SignIn($input: Auth) { signin(input: $input) }"
            }

            response = requests.post(self.galaxy_query, json=data, proxies=proxies)

            if response.status_code == 200 and 'signin' in response.text:
                signin = response.json()['data']['signin']
                logger.info('Got the signIn token')
                return signin
            else:
                logger.error(f"{self.account_evm.address} Login failed."
                             f"\nResponse code: {response.status_code}."
                             f"\nResponse content {response.content}")
                return None

        except Exception as e:
            logger.critical(f"{self.account_evm.address} Login failed."
                            f"\nException: {e}")
            return None

    def sign_in_apt(self):
        logger = setup_gay_logger('sign_in_apt')
        apt_address = self.account_apt.address()
        public_key = self.account_apt.public_key()

        try:
            now = datetime.utcnow()
            next_day = now + timedelta(days=7)
            iso_time_next_day = next_day.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            current_time = int(time())
            rounded_time = int(current_time - (current_time % 3600))

            message = (f"Galxe.com wants you to sign in with your Aptos account: "
                       f"{apt_address}; "
                       f"<Public key: {public_key}>, "
                       f"<Version: 1>, "
                       f"<Chain ID: 1>, "
                       f"<Nonce: {rounded_time}>, "
                       f"<Expiration Time: {iso_time_next_day}>")

            full_message = f'APTOS\nmessage: {message}\nnonce: {rounded_time}'

            signature = self.account_apt.sign(full_message.encode('utf-8'))

            data = {
                "operationName": "SignIn",
                "variables": {
                    "input": {
                        "address": str(apt_address),
                        "message": message,
                        "signature": str(signature.signature.hex())
                    }
                },
                "query": "mutation SignIn($input: Auth) {\n  signin(input: $input)\n}\n"
            }

            response = requests.post(self.galaxy_query, json=data, proxies=proxies)

            if response.status_code == 200 and 'signin' in response.text:
                signin = response.json()['data']['signin']
                logger.info('Got the signIn token')
                return signin
            else:
                logger.error(f"{apt_address} Login failed."
                             f"\nResponse code: {response.status_code}."
                             f"\nResponse content {response.content}")
                return None

        except Exception as e:
            logger.critical(f"{apt_address} Login failed."
                            f"\nException: {e}")
            return None
    def _get_address(self, address_type):
        if address_type == 'EVM':
            return self.account_evm.address
        elif address_type == 'APTOS':
            return self.account_apt.address
        else:
            raise ValueError("Invalid address type")

    def create_username(self, galaxy_token, username, address_type):
        logger = setup_gay_logger('create_username')
        try:
            headers = galaxy_headers(galaxy_token)
            address = self._get_address(address_type)  # Address based on the type (EVM or APTOS)

            payload = {
                "operationName": "CreateNewAccount",
                "query": "mutation CreateNewAccount($input: CreateNewAccount!) {\n  createNewAccount(input: $input)\n}\n",
                "variables": {
                    "input": {
                        "schema": f"{address_type}:{address}",
                        "socialUsername": "",
                        "username": username
                    }
                }
            }

            response = requests.post(self.galaxy_query, headers=headers, json=payload, proxies=proxies)
            response_json = response.json()

            if 'data' in response_json and 'createNewAccount' in response_json['data']:
                logger.info(f"Account creation successful for username: {username}")
                return True
            else:
                logger.error(f"Account creation failed for username: {username}."
                             f"\nResponse: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Exception during account creation for username: {username}. "
                         f"\nException: {e}")
            return False

    def check_username_availability(self, galaxy_token, username):
        try:
            headers = galaxy_headers(galaxy_token)

            payload = {
                "operationName": "IsUsernameExisting",
                "query": "query IsUsernameExisting($username: String!) {\n  usernameExist(username: $username)\n}\n",
                "variables": {
                    "username": username
                }
            }

            response = requests.post(self.galaxy_query, headers=headers, json=payload, proxies=proxies)
            response_json = response.json()
            is_username_existing = response_json.get('data', {}).get('usernameExist', None)
            return is_username_existing
        except Exception:
            return None

    def get_basic_user_info(self, galaxy_token, user_address):
        logger = setup_gay_logger('get_basic_user_info')
        try:
            headers = galaxy_headers(galaxy_token)
            payload = {
                "operationName": "BasicUserInfo",
                "variables": {"address": user_address},
                "query": """query BasicUserInfo($address: String!) {
                            addressInfo(address: $address) {
                                id
                                username
                                address
                                aptosAddress
                                hasEvmAddress
                                hasAptosAddress
                                hasTwitter
                                twitterUserID
                                twitterUserName
                            }
                        }"""
            }
            response = requests.post(self.galaxy_query, headers=headers, json=payload, proxies=proxies)

            # print(json.dumps(response.json(), indent=4))

            if response.status_code == 200:
                logger.info("User info retrieval successful")
                return response.json()
            else:
                logger.error(f"Failed to retrieve user info for address: {user_address}.\nResponse: {response.text}")
                return None
        except Exception as e:
            logger.critical(f"Exception during user info retrieval for address: {user_address}.\nException: {e}")
            return None

    def create_new_account(self, galaxy_token, address_type: str):
        logger = setup_gay_logger('create_new_account')
        while True:
            username = random.choice(self.word_list)
            if not self.check_username_availability(galaxy_token, username):
                self.create_username(galaxy_token, username, address_type)
                return True
            logger.warning(f"{username} username is already taken. Retry...")

if __name__ == "__main__":
    # Web3 and Galaxy API setup
    w3 = Web3(Web3.HTTPProvider('https://rpc.ankr.com/eth'))
    account_apt = Account.load_key('0x8a299c3285ba90b721732e4414299fa1deb3f7909c50010717d173bc6bc6b470')
    account_evm = w3.eth.account.from_key("0x9c16ee871c240a0165a184b69fc166cb540f9730f44124b95a84f7088b1e82af")

    # Test for method of the GalaxyAccountManager
    manager = GalaxyAccountManager(account_apt, account_evm)

    # Sign in EVM
    token = manager.sign_in_evm()

    # Create New Account (address type "EVM" or "APTOS")
    create_new_account_result = manager.create_new_account(token, 'EVM')

    # Update user address
    update_address_result = manager.update_user_address(token)

    # Get Basic User Info
    get_user_info_result = manager.get_basic_user_info(token, account_evm.address)

    # Sign in APT
    sign_in_apt_result = manager.sign_in_apt()


