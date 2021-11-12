from web3.middleware import geth_poa_middleware
from web3 import Web3

addr = "0xca26ECF47Ce060855E652a4179d1D461de943822"

w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org:443'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

balance = float(w3.fromWei(w3.eth.get_balance(addr), 'bnb'))
print(balance)