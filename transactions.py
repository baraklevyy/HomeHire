from web3 import Web3, HTTPProvider
import json
import time
import config

w3 = Web3(HTTPProvider(config.INFURA_URL))

contract_abi_json = json.loads(open('contract_abi.json', 'r').read())

contract_address = config.CONTRACT_ADDRESS
hire_contract = w3.eth.contract(address=contract_address, abi=contract_abi_json)

# pay rent transaction - renter pay to the landlord
def payRent(landlord, amount_wei):
    txn_dict = hire_contract.functions.payRent(w3.toChecksumAddress(landlord)).buildTransaction({
                'chainId': 3,
                'value': int(amount_wei),
                'gas': 2000000,
                'gasPrice': w3.toWei('2', 'gwei')
    })
    return txn_dict

# add landlord transaction
def addLandlord(landlord):
    txn_dict = hire_contract.functions.addLandlord(w3.toChecksumAddress(landlord)).buildTransaction({
                'chainId': 3,
                'value': 0,
                'gas': 2000000,
                'gasPrice': w3.toWei('2', 'gwei')
    })
    return txn_dict

"""This method convert wei (smallest ether measurement unit) into Ethereum"""
def wei_to_ethereum(wei_amount):
    return (w3.fromWei(int(wei_amount), 'ether'))

# add home transaction - only approvel landlord can add home
def addHome(_homeRent, _monthsToPay, _renter, _dateOfStart, _dateOfEnd, _elevator, _garage, _roomNum):
    txn_dict = hire_contract.functions.addHome(int(_homeRent), int(_monthsToPay), w3.toChecksumAddress(_renter), _dateOfStart, _dateOfEnd, _elevator, _garage, int(_roomNum)).buildTransaction({
        'chainId': 3,
        'value': 0,
        'gas': 2000000,
        'gasPrice': w3.toWei('2', 'gwei')
    })
    return txn_dict

# delete homr transaction - only admin can delete home
def deleteHome(renter):
    txn_dict = hire_contract.functions.deleteHome(w3.toChecksumAddress(renter)).buildTransaction({
                'chainId': 3,
                'value': 0,
                'gas': 2000000,
                'gasPrice': w3.toWei('2', 'gwei')
    })
    print(txn_dict)
    return txn_dict

# change rent price transaction - only approvel landlord can change rent price
def changeHomeRent(renter, newHomeRent):
    txn_dict = hire_contract.functions.changeHomeRent(w3.toChecksumAddress(renter), int(newHomeRent)).buildTransaction({
                'chainId': 3,
                'value': 0,
                'gas': 2000000,
                'gasPrice': w3.toWei('2', 'gwei')
    })
    print(txn_dict)
    return txn_dict

# change renter transaction - only approvel landlord can change rentr
def changeRenter(oldRenter, newRenter, dateOfStart, dateOfEnd, monthsToPay):
    txn_dict = hire_contract.functions.changeRenter(w3.toChecksumAddress(oldRenter), w3.toChecksumAddress(newRenter), dateOfStart, dateOfEnd, int(monthsToPay)).buildTransaction({
                'chainId': 3,
                'value': 0,
                'gas': 2000000,
                'gasPrice': w3.toWei('2', 'gwei')
    })
    return txn_dict

# function to get home from Homes map
def getHome(_renter):
    home = hire_contract.functions.Homes(w3.toChecksumAddress(_renter)).call()
    return home

def sign_transaction(txn_dict, wallet_address, private_key):
    txn_dict['nonce'] = w3.eth.getTransactionCount(w3.toChecksumAddress(wallet_address))

    signed_txn = w3.eth.account.signTransaction(txn_dict, private_key=private_key)

    result = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

    tx_receipt = None

    count = 0
    while tx_receipt is None and (count < 30):
        try:
            time.sleep(10)

            tx_receipt = w3.eth.getTransactionReceipt(result)

            return tx_receipt
        except:
            tx_receipt = None
            count += 1

    if tx_receipt is None:
        return {'status': 'failed', 'error': 'timeout'}
