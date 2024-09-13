from flask import Flask, request, render_template, json, send_file
import random
import smtplib
import qrcode
from web3 import Web3
import time
from fpdf import FPDF  # For PDF generation
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from flask_cors import CORS
import base64
import hashlib

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Connect to Ganache blockchain
ganache_url = "HTTP://127.0.0.1:8545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

# Contract ABI and address
contract_address = "0xa1bA6b4Edbc60B0Df96Df1E46C059CD67fb53d8f"
file_path = r'C:\medInv\backend\build\contracts\MedicineSupply.json'
with open(file_path) as f:
    contract_json = json.load(f)
    contract_abi = contract_json['abi']

# Load contract
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Generate and send OTP
def generate_otp():
    return str(random.randint(1000, 9999))

def send_otp_email(destination_email, otp):
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login("sahidahmed7703@gmail.com", "omiodupwoelbijcc")
    message = f"Your OTP is {otp}"
    server.sendmail("mauthnweb@gmail.com", destination_email, message)
    server.quit()

# AES encryption function
def encrypt_data(data, aadhaar):
    key = hashlib.sha256(aadhaar.encode()).digest()  # Create a 32-byte key using Aadhaar
    iv = os.urandom(16)  # Generate a random initialization vector
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    # Pad the data to ensure it's a multiple of the block size (16 bytes)
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data.encode()) + padder.finalize()
    
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    
    # Return the IV and encrypted data as base64 strings
    return base64.b64encode(iv + encrypted_data).decode()

# AES decryption function
def decrypt_data(encrypted_data, aadhaar):
    encrypted_data = base64.b64decode(encrypted_data)
    key = hashlib.sha256(aadhaar.encode()).digest()
    iv = encrypted_data[:16]  # Extract the IV from the first 16 bytes
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted_data[16:]) + decryptor.finalize()
    return decrypted_data.decode()

# Wait for transaction receipt
def wait_for_transaction_receipt(tx_hash):
    while True:
        try:
            receipt = web3.provider.make_request('eth_getTransactionReceipt', [tx_hash])
            if receipt and receipt.get('result'):
                return receipt['result']
        except Exception as e:
            print(f"Error getting transaction receipt: {e}")
        time.sleep(1)

# Route to render form for medicine info
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_receipt', methods=['POST'])
def generate_receipt():
    data = request.get_json()
    customer_aadhaar = data.get('aadhaar')
    medicine_info = data.get('medicine_info')
    destination_address = data.get('destination')

    try:
        # Step 1: Encrypt QR Code Data
        qr_code_data = f"Medicine: {medicine_info}, Aadhaar: {customer_aadhaar}"
        encrypted_qr_data = encrypt_data(qr_code_data, customer_aadhaar)

        # Step 2: Generate and Save QR Code
        img = qrcode.make(encrypted_qr_data)
        qr_image_path = f'static/qr_codes/{customer_aadhaar}_qr.png'
        img.save(qr_image_path)
        print(f"QR code saved at {qr_image_path}")  # Debug log for QR code path

        # Step 3: Deploy shipment on blockchain
        tx_hash = contract.functions.createShipment(encrypted_qr_data, destination_address, customer_aadhaar).transact({
            'from': web3.eth.accounts[0]
        })
        receipt = wait_for_transaction_receipt(tx_hash)
        print(f"Transaction hash: {tx_hash}")  # Debug log for transaction hash

        # Step 4: Generate PDF Receipt
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(200, 10, txt="Medicine Receipt", ln=True, align='C')
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Customer Aadhaar: {customer_aadhaar}", ln=True)
        pdf.cell(200, 10, txt=f"Medicine Info: {medicine_info}", ln=True)
        pdf.cell(200, 10, txt=f"Destination Address: {destination_address}", ln=True)

        # Add QR Code to PDF
        pdf.image(qr_image_path, x=10, y=60, w=50)
        
        # Corrected path to save the PDF
        pdf_output_path = f'static/receipts/{customer_aadhaar}_receipt.pdf'

        try:
            pdf.output(pdf_output_path)  # Correct file save
            print(f"PDF saved successfully at {pdf_output_path}")  # Debug log for PDF path
        except Exception as e:
            print(f"Error saving PDF: {str(e)}")
        
        # Saving the PDF
        pdf_output_success = pdf.output(pdf_output_path)
        print(f"PDF saved successfully at {pdf_output_path}")  # Debug log for PDF path

        # Check if the PDF file is successfully saved
        if not pdf_output_success:
            raise Exception("Failed to generate the PDF")

        # Step 5: Send PDF file to the user
        try:
            return send_file(pdf_output_path, as_attachment=True, download_name=f"{customer_aadhaar}_receipt.pdf", mimetype='application/pdf')
        except Exception as e:
            print(f"Error sending PDF file: {str(e)}")
            return f"An error occurred while sending the PDF: {str(e)}"

    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Logging error
        return f"An error occurred: {str(e)}"



@app.route('/generate_otp', methods=['POST'])
def generate_otp():
    qr_code = request.form['qr_code']
    email = request.form['email']

    otp = str(random.randint(1000, 9999))
    send_otp_email(email, otp)

    try:
        tx_hash = contract.functions.setOTP(qr_code, otp).transact({
            'from': web3.eth.accounts[0],
            'gas': 1000000
        })
        # receipt = wait_for_transaction_receipt(tx_hash)
        
        return f"OTP sent to {email} and stored in blockchain."                                                                                 
    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    qr_code = request.form['qr_code']
    entered_otp = request.form['otp']

    try:
        tx_hash = contract.functions.verifyOTP(qr_code, entered_otp).transact({
            'from': web3.eth.accounts[0],
            'gas': 1000000
        })
        receipt = wait_for_transaction_receipt(tx_hash)
        status = contract.functions.getShipmentStatus(qr_code).call()
        is_delivered, aadhaar_verified, otp_verified = status

        if is_delivered and otp_verified:
            return f"OTP verified successfully. Shipment delivered."
        else:
            return f"OTP verification failed for QR Code: {qr_code}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == '__main__':
    os.makedirs('static/qr_codes', exist_ok=True)
    os.makedirs('static/receipts', exist_ok=True)
    app.run(debug=True)