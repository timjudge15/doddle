import os
import json
import requests
from decimal import *
from flask import Flask, request
from web3 import Web3
app = Flask(__name__)

ETH_PROVIDER = os.environ.get('ETH_PROVIDER')
ETH_ACCT_KEY = os.environ.get('ETH_ACCT_KEY')
ETH_ADDRESS = os.environ.get('ETH_ADDR')
w3 = Web3(Web3.HTTPProvider(ETH_PROVIDER))

@app.route('/ctokens')
def ctokens():
    """
      Returns all ctokens:
      - symbol
      - symbol on compound
      - interest rate
    """
    res = requests.get("https://api.compound.finance/api/v2/ctoken")
    response = []
    for t in res.json()['cToken']:
        token = {
            'symbol': t['underlying_symbol'],
            'compound_symbol': t['symbol'],
            'rate': '{}%'.format(round(Decimal(t['supply_rate']['value'])*100, 2))
        } 
        response.append(token)
    return ({'supported': response}, {'Content-Type': 'application/json'})

@app.route('/ctokens/<symbol>')
def ctokens_detail(symbol):
    """
      Returns particular ctoken for underlying:
      - symbol
      - interest accrued
      - principal
      - current ctoken balance
    """
    symbol = symbol.upper()
    tokens = requests.get("https://api.compound.finance/api/v2/ctoken")
    balances = requests.get("https://api.compound.finance/api/v2/account?addresses[]={}".format(ETH_ADDRESS))

    response = {
        'principal': '0.0',
        'current_balance': '0.0',
        'interest_accrued': '0.0',
        'ctoken_balance': '0.0'
    }
    for t in tokens.json()['cToken']:
        if t['underlying_symbol'] == symbol:
            response['symbol'] = t['underlying_symbol']
            accts = balances.json()['accounts']
            if len(accts) > 0:
                for acct in accts[0]['tokens']:
                    if acct['symbol'] == t['symbol']:
                        abi_url = "https://raw.githubusercontent.com/compound-finance/compound-protocol/master/networks/mainnet-abi.json"
                        abi = requests.get(abi_url)
                        tokens = requests.get("https://api.compound.finance/api/v2/ctoken")
                        contract_address = [t['token_address'] for t in tokens.json()['cToken'] if t['underlying_symbol'] == symbol][0]
                        compound_token_contract = w3.eth.contract(abi=abi.json()["c{}".format(symbol)], address=Web3.toChecksumAddress(contract_address)) 
                        nonce = w3.eth.getTransactionCount(ETH_ADDRESS)
                        total = acct['safe_withdraw_amount_underlying']['value']
                        interest = acct['lifetime_supply_interest_accrued']['value']
                        response['principal'] = "{}".format(Decimal(total) - Decimal(interest))
                        response['current_balance'] = total
                        response['interest_accrued'] = interest
                        response['ctoken_balance'] = str(compound_token_contract.functions.balanceOf(ETH_ADDRESS).call())
    return (response, {'Content-Type': 'application/json'})

@app.route('/ctokens/<symbol>/mint', methods=['POST'])
def ctokens_mint(symbol):
    """
      Mints particular ctoken based on:
      - symbol
      - amount
      and returns:
      - symbol
      - amount minted
      - tx id
    """
    symbol = symbol.upper()
    amt = request.form['amount']
    abi_url = "https://raw.githubusercontent.com/compound-finance/compound-protocol/master/networks/mainnet-abi.json"
    abi = requests.get(abi_url)
    tokens = requests.get("https://api.compound.finance/api/v2/ctoken")
    contract_address = [t['token_address'] for t in tokens.json()['cToken'] if t['underlying_symbol'] == symbol][0]
    amount = w3.toWei(amt, 'ether')
    compound_token_contract = w3.eth.contract(abi=abi.json()["c{}".format(symbol)], address=Web3.toChecksumAddress(contract_address)) 
    nonce = w3.eth.getTransactionCount(ETH_ADDRESS)
    mint_tx = compound_token_contract.functions.mint().buildTransaction({
        'chainId': 1,
        'gas': 500000,
        'gasPrice': w3.toWei('20', 'gwei'),
        'nonce': nonce,
        'value': int(amount)
    })
    signed_txn = w3.eth.account.sign_transaction(mint_tx, ETH_ACCT_KEY)
    try:
        tx = w3.eth.sendRawTransaction(signed_txn.rawTransaction) 
    except ValueError as err:
        return (json.loads(str(err).replace("'", '"')), 402, {'Content-Type': 'application/json'})

    response = {
        'symbol': symbol,
        'amount': amt,
        'tx_id': tx.hex()
    }
    return (response, {'Content-Type': 'application/json'})

@app.route('/ctokens/<symbol>/redeem', methods=['POST'])
def ctokens_redeem(symbol):
    """
      Redeems particular ctoken based on:
      - symbol
      - amount
      and returns:
      - symbol
      - tx_id
    """
    symbol = symbol.upper()
    amt = request.form['amount']
    abi_url = "https://raw.githubusercontent.com/compound-finance/compound-protocol/master/networks/mainnet-abi.json"
    abi = requests.get(abi_url)
    tokens = requests.get("https://api.compound.finance/api/v2/ctoken")
    contract_address = [t['token_address'] for t in tokens.json()['cToken'] if t['underlying_symbol'] == symbol][0]
    compound_token_contract = w3.eth.contract(abi=abi.json()["c{}".format(symbol)], address=Web3.toChecksumAddress(contract_address)) 
    nonce = w3.eth.getTransactionCount(ETH_ADDRESS)
    redeem_tx = compound_token_contract.functions.redeem(int(amt)).buildTransaction({
        'chainId': 1,
        'gas': 500000,
        'gasPrice': w3.toWei('20', 'gwei'),
        'nonce': nonce
    })
    signed_txn = w3.eth.account.sign_transaction(redeem_tx, ETH_ACCT_KEY)
    try:
        tx = w3.eth.sendRawTransaction(signed_txn.rawTransaction) 
    except ValueError as err:
        return (json.loads(str(err).replace("'", '"')), 402, {'Content-Type': 'application/json'})

    response = {
        'symbol': symbol,
        'tx_id': tx.hex()
    }
    return (response, {'Content-Type': 'application/json'})