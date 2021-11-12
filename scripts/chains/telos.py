from web3 import Web3

#url = 'https://apis-sj.ankr.com/e7f7dbc6a2734f46b349442e3341003c/85326b53039c28777746d160a86bc9b7/fantom/full/main'  # url string
#w3 = Web3(Web3.HTTPProvider(url))
#print(w3.eth.block_number)
def test():
    bsc="https://bsc-dataseed.binance.org/"
    w3=Web3(Web3.HTTPProvider(bsc))
    print(w3.isConnected)

    account_1='0xC79CD61ADd514d098B95ba1B25a3C26FBb4c45E9'
    account_2='0xA25bc8c1e230a476cB00f2e9c93ffC2D4e163dc5'

    balance=w3.eth.get_balance(account_1)
    readable=w3.fromWei(balance,'ether')
    print(readable)

    nonce = w3.eth.getTransactionCount(account_1)

    tx = {
        'nonce': nonce,
        'to': account_2,
        'value': w3.toWei(0.001, 'ether'),
        'gas': 21000,
        'gasPrice': w3.toWei('50', 'gwei')
    }

    # sign transaction using senders private key
    signed_tx = w3.eth.account.signTransaction(tx, '490aed00507fa002ed5ee9cc2978d8a455d06e032797b5d3b5d9873ac245212f')
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    print(w3.toHex(tx_hash))