# doddle

Doddle Finance enables easy access to decentralsied finanial tools through the simple to use Doddle app. 

Note: ignore the chains section in the scripts folder, Doddle is currently only working on BSC Blockchain.   
scripts/userdata/transactions.py is where the users transactions are being built. 
main.py is where the main flask app runs. This is where user inputs are sent and handled. 

For example:
1. User enters amount they wish to send to a friend. 
2. This information is sent from app.html to the doddlepay function in the main.py file via a post request (a backend to frontend messeging system)
3. The doddlepay function then calls the transaction fucntion in transaction.py sending the recipientemail, senderusername and transferamount. 
(this line here scripts.userdata.transactions.doddlePay(recipientemail, senderusername, transferamount))   We are now in the doddlepay function in transactions.py
4. The users information is then checked in the database to make sure the recipient exists. 
5. 5. We then retrieve the recipients public key (this is the blockchain address we are sending the money to)
6. We also retrieve the senders public and private key, which are used to sign and send transactions.
7. We then check to make sure the sender has sufficicient funds to send the transaction
8. Now we build the transaction. 
    1. This contains a nonce (number only used once ;) this is required to prevent double spending of transactions )
    2. The recipients public address
    3. The senders public address
    4. The gas price (a small fee required to send the transaction) this is variable dependant on how congested the network is.
9. We then sign off the transaction using the senders private key and retrive the transaction hash that can be used to lookup the transaction on the blockchain.

Other functions such as the lending function follow a similr process with slightly more complexity. (Still building these atm!)



