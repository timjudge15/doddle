from secrets import token_bytes
from coincurve import PublicKey
from sha3 import keccak_256
import pandas as pd
from web3.middleware import geth_poa_middleware
from web3 import Web3
from pycoingecko import CoinGeckoAPI
import json
import os
#import abis
import requests
import time
import random

cg = CoinGeckoAPI()

bsc = "https://bsc-dataseed.binance.org/"
w3 = Web3(Web3.HTTPProvider(bsc))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
print(w3.isConnected())

# Function Works

def checktokenbalance(senderusername,abi):
    df = pd.read_csv("userdata.csv", index_col="email")
    publickey = df.loc[senderusername]['publickey']
    checksumpublickey = Web3.toChecksumAddress(publickey)
    balances = [0,42,5,75]
    testbalance = random.choice(balances)
    return testbalance

def userstats(senderusername,abi):
    df = pd.read_csv("userdata.csv", index_col="email")
    publickey = df.loc[senderusername]['publickey']
    checksumpublickey = Web3.toChecksumAddress(publickey)
    address = Web3.toChecksumAddress('0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d')
    USDC = w3.eth.contract(address=address, abi=abi) # declaring the token contract
    USDC_balance = USDC.functions.balanceOf(publickey).call()
    USDC_balance = round(USDC_balance,2)
    balance = float(w3.fromWei(w3.eth.get_balance(checksumpublickey), 'ether'))
    balance = round(balance, 2)
    etherusd = cg.get_price(ids='binancecoin', vs_currencies='usd')
    binancecoin = etherusd['binancecoin']['usd']
    balance = balance*binancecoin
    savingsbalance = '0.00'
    loans = '0.00'
    return balance, savingsbalance, loans, USDC_balance


def userKeys(senderusername):  # Function Works
    # userkeys
    df = pd.read_csv("userdata.csv", index_col="email")
    privatekey = df.loc[senderusername]['privatekey']
    publickey = df.loc[senderusername]['publickey']
    return publickey, privatekey

    # Function Works


def checkexising(username):
    df = pd.read_csv("userdata.csv")
    checkemail = df['email'].str.contains(username)
    founduser = False
    for i in range(len(checkemail)):
        while founduser == False:
            founduser = checkemail[i]
            print(founduser)
            break
    if founduser == True:
        return False
    else:
        return True


def verifylogin(username, password):  # Function Works
    df = pd.read_csv("userdata.csv")
    checkemail = df['email'].str.contains(username)
    founduser = False
    for i in range(len(checkemail)):
        while founduser == False:
            founduser = checkemail[i]
            print(founduser)
            break
    if founduser == True:
        df = pd.read_csv("userdata.csv", index_col="email")
        dbpassword = df.loc[username]['password']
        if dbpassword == password:
            return True
        else:
            return False
    else:
        return False

def sendMessage(email,message,sender):
    df = pd.read_csv("messages.csv") 
    m = df['email'] == email
    record=False
    for i in range(1,8):
        while record==False:
            if df.loc[m, 'message_{}'.format(i)].any()==False:
                df.loc[m, 'message_{}'.format(i)] = df.loc[m, 'message_{}'.format(i)].replace(0, message)
                df.loc[m, 'message_{}'.format(i+1)] = df.loc[m, 'message_{}'.format(i+1)].replace(0, sender)
                df.to_csv('messages.csv', index = False)
                record=True
            break
    
def newuserKeys(password, email):  # Apending New user data to wrong line?
    private_key = keccak_256(token_bytes(32)).digest()
    public_key = PublicKey.from_valid_secret(
        private_key).format(compressed=False)[1:]
    addr = keccak_256(public_key).digest()[-20:]
    print('private key:', private_key.hex())
    print('Public Key: 0x' + addr.hex())
    df = pd.DataFrame({'password': [password], 'email': [email], 'public_key': ['0x'+addr.hex()], 'private_key': [private_key.hex()], 'appusdc': ['no']})
    df.to_csv('userdata.csv', sep=',', header=None, mode='a')

    # Function Works

#Compiles transaction for peer to peer payments, transactions 
def doddlePay(recipientemail, senderusername, transferamount):
    # first check if the recipients email is in the data base
    df = pd.read_csv("userdata.csv")
    checkemail = df['email'].str.contains(recipientemail)
    founduser = False
    for i in range(len(checkemail)):
        while founduser == False:
            founduser = checkemail[i]
            print(founduser)
            break
    print(senderusername)

    # if the recipients email is in the db, get the senders ethereum key pairs
    if founduser == True:
        df = pd.read_csv("userdata.csv", index_col="email")
        privatekey = df.loc[senderusername]['privatekey']
        publickey = df.loc[senderusername]['publickey']
        checksumpublickey = Web3.toChecksumAddress(publickey)
        balance = float(w3.fromWei(
            w3.eth.get_balance(checksumpublickey), 'ether'))

        # API to retrive current Eth Price so user input can be converted to
        etherusd = cg.get_price(ids='binancecoin', vs_currencies='usd')
        binancecoin = etherusd['binancecoin']['usd']
        convert_dollar_to_bnb = float(transferamount)/binancecoin
        print(convert_dollar_to_bnb)
        sendamount = convert_dollar_to_bnb

        # if the amount trying to be sent is smaller than the users account balance, continue to transaction.
        if balance >= convert_dollar_to_bnb:
            df = pd.read_csv("userdata.csv", index_col="email")
            recipientpublickey = df.loc[recipientemail]['publickey']
            nonce = w3.eth.getTransactionCount(publickey)

            # construct transaction
            tx = {
                'nonce': nonce,
                'to': recipientpublickey,
                'value': w3.toWei(sendamount, 'ether'),
                'gas': 21000,
                'gasPrice': w3.toWei('50', 'gwei')
            }

            # sign transaction using senders private key
            signed_tx = w3.eth.account.signTransaction(tx, privatekey)
            tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
            print(w3.toHex(tx_hash))
            print(len(w3.toHex(tx_hash)))
            return 'success'

        else:
            return 'insufficientfunds'
    else:
        return 'nouser'

        # Transaction Works, ToDo: Deposit amount>0

#Lending function to compile user transaction and send it to 3rd party lending smart contract on BSC 
def doddleLend(senderusername, lendamount):
    df = pd.read_csv("userdata.csv", index_col="email")
    privatekey = df.loc[senderusername]['privatekey']
    publickey = df.loc[senderusername]['publickey']

    checksumpublickey = Web3.toChecksumAddress(publickey)
    balance = float(w3.fromWei(w3.eth.get_balance(checksumpublickey), 'ether'))

    # API to retrive current Eth Price so user input can be converted to
    etherusd = cg.get_price(ids='binancecoin', vs_currencies='usd')
    binancecoin = etherusd['binancecoin']['usd']
    sendamount = float(lendamount)/binancecoin

    #  event Mint(address minter, uint mintAmount, uint mintTokens);
    # function mint(uint mintAmount) external returns (uint);

    if balance >= sendamount:
        #abi = abis.venus()
        contractaddress = w3.toChecksumAddress(
            '0xecA88125a5ADbe82614ffC12D0DB554E2e2867C8')
        abi_url = 'https://raw.githubusercontent.com/VenusProtocol/venus-config/master/networks/mainnet-abi.json'
        abi = requests.get(abi_url)
        abi = abi.json()["vUSDC"]
        print(abi)
        amount = w3.toWei(0.0, 'ether')
        Vusdc = w3.eth.contract(abi=abi, address=contractaddress)
        nonce = w3.eth.getTransactionCount(publickey)

        tx = Vusdc.functions.mint(0).buildTransaction({
            'gas': 300000,
            'gasPrice': w3.toWei('20', 'gwei'),
            'nonce': nonce,
            'value': int(amount),
        })

        # sign transaction using senders private key
        signed_tx = w3.eth.account.signTransaction(tx, privatekey)
        tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        print(w3.toHex(tx_hash))
        print(len(w3.toHex(tx_hash)))

        # return 'success'

        # else:
        #   return 'insufficientfunds'

#This function converts BNB token into an ERC20 compatable version so that it can be swapped to USDC/DAI/Tether 

def wrapBNB(senderusername, abi):  # Function Works
    # userkeys
    df = pd.read_csv("userdata.csv", index_col="email")
    privatekey = df.loc[senderusername]['privatekey']
    publickey = df.loc[senderusername]['publickey']
    balance = float(w3.fromWei(w3.eth.get_balance(publickey), 'ether'))
    if balance > 0.004:
        nonce = w3.eth.get_transaction_count(publickey)
        contractaddress = w3.toChecksumAddress(
            "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c")
        wbnb = w3.eth.contract(address=contractaddress, abi=abi)
        nonce = w3.eth.getTransactionCount(publickey)

        transaction = wbnb.functions.deposit().buildTransaction({
            'nonce': nonce,
            'from': publickey,
            'value': w3.toWei(0.001, 'ether'),
            'gas': 43738,
            'gasPrice': w3.toWei('5', 'gwei')})

        # sign transaction using senders private key
        signed_tx = w3.eth.account.signTransaction(transaction, privatekey)
        tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        print(w3.toHex(tx_hash))
        print(len(w3.toHex(tx_hash)))
        time.sleep(60)
        swapamount = balance
        # check if the user has already approved usdc
        if df.at[senderusername, 'appusdc'] == 'yes':
            tokenSwap(senderusername, swapamount)
        else:
            approveToken(senderusername)
            time.sleep(60)
            tokenSwap(senderusername, swapamount)

            # function works


def approveToken(senderusername, abi):
    contractaddress = '0xecA88125a5ADbe82614ffC12D0DB554E2e2867C8'
    usdc = w3.eth.contract(address=contractaddress, abi=abi)
    publickey, privatekey = userKeys(senderusername)
    max_amount = w3.toWei(2**64-1, 'ether')
    nonce = w3.eth.getTransactionCount(publickey)

    # build transaction
    tx = usdc.functions.approve(publickey, max_amount).buildTransaction({
        'from': publickey,
        'nonce': nonce
    })
    signed_tx = w3.eth.account.signTransaction(tx, privatekey)
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    print(w3.toHex(tx_hash))
    df = pd.read_csv("userdata.csv", index_col="email")
    df.at[senderusername, 'appusdc'] = 'yes'
    df.to_csv("userdata.csv", index=False)


def tokenSwap(senderusername, swapamount, pancakeabi):
    # pancakeswap router
    panRouterContractAddress = '0x10ED43C718714eb63d5aA57B78B54704E256024E'
    # userkeys
    df = pd.read_csv("userdata.csv", index_col="email")
    privatekey = df.loc[senderusername]['privatekey']
    publickey = df.loc[senderusername]['publickey']
    tokenToBuy = w3.toChecksumAddress(
        "0xecA88125a5ADbe82614ffC12D0DB554E2e2867C8")
    spend = w3.toChecksumAddress("0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c")

    # Setup the PancakeSwap contract
    contract = w3.eth.contract(
        address=panRouterContractAddress, abi=pancakeabi)
    nonce = w3.eth.get_transaction_count(publickey)

    # API to retrive current Eth Price so user input can be converted to
    etherusd = cg.get_price(ids='binancecoin', vs_currencies='usd')
    binancecoin = etherusd['binancecoin']['usd']
    swapvalue = float(swapamount)/binancecoin

    pancakeswap2_txn = contract.functions.swapExactETHForTokens(
        1,  # set to 0, or specify minimum amount of tokeny you want to receive - consider decimals!!!
        [spend, tokenToBuy],
        publickey,
        (int(time.time()) + 10000)
    ).buildTransaction({
        'from': publickey,
        # This is the Token(BNB) amount you want to Swap from
        'value': w3.toWei(swapvalue, 'ether'),
        'gas': 250000,
        'gasPrice': w3.toWei('5', 'gwei'),
        'nonce': nonce,
    })

    signed_txn = w3.eth.account.sign_transaction(pancakeswap2_txn, privatekey)
    tx_token = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print(w3.toHex(tx_token))


def getUSDTAPY():
    blockmax = w3.eth.block_number
    blockmin = blockmax-1
    response = requests.get(
        "https://api.venus.io/api/market_history/graph?asset=0xfD5840Cd36d94D7229439859C0112a4185BC0255&min_block_timestamp={0}&max_block_timestamp={1}&num_buckets=10".format(blockmin, blockmax))
    data = response.json()
    currentUSDTAPY = data['data']['result'][-1]['supplyApy']
    return currentUSDTAPY


def getUSDCAPY():
    blockmax = w3.eth.block_number
    blockmin = blockmax-1
    response = requests.get(
        "https://api.venus.io/api/market_history/graph?asset=0xecA88125a5ADbe82614ffC12D0DB554E2e2867C8&min_block_timestamp={0}&max_block_timestamp={1}&num_buckets=10".format(blockmin, blockmax))
    data = response.json()
    currentUSDCAPY = data['data']['result'][-1]['supplyApy']
    return currentUSDCAPY


def checkhighestAPY():
    USDC = getUSDCAPY()
    USDT = getUSDTAPY()
    if USDC >= USDT:
        return 'USDC'
    else:
        return 'USDT'
