# Aptos Fundamentals Quest-3 Practice Script

## Overview
This script is specifically designed for users participating in the Aptos Fundamentals Quest-3. It automates certain tasks to help users efficiently complete the quest and earn the associated OAT. The script handles two out of six tasks: NFT bidding and free NFT minting.

## Features

### 1. NFT Bidding
- **Collection Retrieval:** Fetches 100 NFT collections from the Topaz.
- **Verification Filtering:** Filters these collections to include only verified ones.
- **Automated Bidding:** Places a bid on one from these collections using the Topaz contract.

### 2. Free NFT Minting
- **Target Collection:** Targets the 'Make Every M🌐ve Count' collection available on wapal.io for free minting.

### 3. Galaxy Account Registration and Binding
- **Galaxy Account Creation:** Registers a new Galaxy account (EVM).
**Automatic Aptos Address Binding:** The script will link your Aptos address to your Galaxy account before it fill out the form. If it skip this step and fill out the form first, Galaxy won't find your address in they database after Aptos Labs approve you. This means Galaxy won't be able to give you the approval because your address wasn't there when it needed to be.

### 4. Google Form Submission
- **Form Submission:** From now for form submission you need to run separate script called fill_form.py. It required api key from [capsolver](https://dashboard.capsolver.com/dashboard/overview). It needs to be insert in to config.js. Path -- aptos-quests-3\CapSolver.Browser.Extension-chrome-v1.10.3\assets\config.js

## Usage Instructions
1. **Initial Setup:** Ensure that all necessary dependencies and environment variables are set up correctly. 
2. **Proxy:** Users need to register an account at [Smartproxy](https://dashboard.smartproxy.com) and obtain a mobile proxy link from [here](https://dashboard.smartproxy.com/mobile-proxies/proxy-setup). The link should be in the format `http://{username}:{password}@gate.smartproxy.com:7000`. Make sure that the port is 7000, as this script relies on proxy rotation after each request and only this port is configured to do the job.
3. **Required Data** Users need to fill an Excel file with data such as their Aptos private key, EVM private key (can be fresh, no transactions are made; the script uses these only for Galaxy account binding), and email addresses (used to fill out the form. Make sure you have access to these emails; DO NOT USE FAKE EMAILS!!!).
4. **Execution:** Run the script to start the automated process. Ensure there is at least 0.02 APT token in each address for the script to run properly.
 
## Important Notes
- **Funding Requirement:** Each address must have a minimum balance of 0.02 APT tokens for the script's operations. Insufficient funds will prevent the script from performing its tasks.
- This script handles specific tasks that are enough for the completion of Quest-3 but does not cover all six tasks of the quest.
