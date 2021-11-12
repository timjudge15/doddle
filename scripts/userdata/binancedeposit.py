from binance.client import Client
from binance.exceptions import BinanceAPIException

api_key = 'HAKengax6Jqhg5QIi9dn36uHbHcr4MaADNj0qvDzR1I1zlo1C4JWJyjGw9gqGvcZ'
api_secret = 'cAIQWpvNwNRxh0axk7IW1rXHTIXIjixoKSDzs3fZTYjZ4fLzqynL1VUv5RtjDDeI'

client = Client(api_key, api_secret)
   
try:
# name parameter will be set to the asset value by the client if not passed
    result = client.withdraw(
        coin='ETH',
        address='<eth_address>',
        amount=100)
except BinanceAPIException as e:
    print(e)
else:
    print("Success")

# passing a name parameter
result = client.withdraw(
    coin='ETH',
    address='<eth_address>',
    amount=100,
    name='Withdraw')

# if the coin requires a extra tag or name such as XRP or XMR then pass an `addressTag` parameter.
result = client.withdraw(
    coin='XRP',
    address='<xrp_address>',
    addressTag='<xrp_address_tag>',
    amount=10000)

    
