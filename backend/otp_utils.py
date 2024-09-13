import random, json
import smtplib
from web3 import Web3
import time

# Connect to Ganache blockchain
ganache_url = "HTTP://127.0.0.1:8545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

# Contract ABI and address (after deployment via Truffle)
contract_address = "0xe080be378C0eFA9aA32b3D5119C0c454c4E8DbFf"
file_path = r'C:\medInv\backend\build\contracts\MedicineSupply.json'
with open(file_path) as f:
    contract_json = json.load(f)
    contract_abi = contract_json['abi']  # Extract the 'abi' field from the JSON

# Load contract
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

def generate_otp():
    """Generate a random 4-digit OTP."""
    return str(random.randint(1000, 9999))

def send_otp_email(destination_email, otp):
    """Send OTP via email using SMTP."""
    try:
        # Send email via SMTP (use your SMTP server details)
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login("sahidahmed7703@gmail.com", "omiodupwoelbijcc")
        message = f"Your OTP is {otp}"
        server.sendmail("sahidahmed7703@gmail.com", destination_email, message)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def wait_for_transaction_receipt(tx_hash):
    """Wait for the transaction to be mined and return the receipt."""
    while True:
        try:
            receipt = web3.provider.make_request('eth_getTransactionReceipt', [tx_hash])
            if receipt and receipt.get('result'):
                return receipt['result']
        except Exception as e:
            print(f"Error getting transaction receipt: {e}")
        time.sleep(1)

def deploy_shipment(qr_code, destination_address, otp):
    """Deploy shipment details (including OTP) to the blockchain."""
    try:
        tx_hash = contract.functions.createShipment(qr_code, destination_address, otp).transact({
            'from': web3.eth.accounts[0]
        })
        receipt = wait_for_transaction_receipt(tx_hash)
        return receipt
    except Exception as e:
        print(f"Error deploying shipment: {e}")
        return None

def verify_otp_on_blockchain(qr_code, entered_otp):
    """Verify the OTP on the blockchain."""
    try:
        tx_hash = contract.functions.verifyOTP(qr_code, entered_otp).transact({
            'from': web3.eth.accounts[0],
            'gas': 1000000  # Adjust gas limit if needed
        })
        receipt = wait_for_transaction_receipt(tx_hash)
        status = contract.functions.getShipmentStatus(qr_code).call()
        is_delivered, otp_verified = status
        return is_delivered and otp_verified
    except Exception as e:
        print(f"Error verifying OTP: {e}")
        return False
