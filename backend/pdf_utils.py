from fpdf import FPDF
import qrcode
import os

# Ensure QR Code folder exists
QR_CODE_FOLDER = 'static/qr_codes'
if not os.path.exists(QR_CODE_FOLDER):
    os.makedirs(QR_CODE_FOLDER)

def generate_qr(qr_code_data):
    """Generate QR code and save it as PNG."""
    img = qrcode.make(qr_code_data)
    qr_code_path = os.path.join(QR_CODE_FOLDER, f'{qr_code_data}.png')
    img.save(qr_code_path)
    return qr_code_path

def create_pdf_with_qr(customer_name, medicines, aadhar_number, qr_code_data):
    """Create a PDF receipt with embedded QR code."""
    pdf = FPDF()
    pdf.add_page()

    # Add title and customer details
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Medicine Receipt", ln=True, align='C')
    
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Customer Name: {customer_name}", ln=True)
    pdf.cell(200, 10, txt=f"Aadhar Number: {aadhar_number}", ln=True)
    
    # Add medicines list
    pdf.cell(200, 10, txt="Medicines Purchased:", ln=True)
    for medicine in medicines:
        pdf.cell(200, 10, txt=f"- {medicine}", ln=True)
    
    # Embed QR code
    qr_code_path = generate_qr(qr_code_data)
    pdf.image(qr_code_path, x=10, y=100, w=50)  # Adjust positioning as needed

    # Save PDF
    pdf_file_path = f'static/receipts/{customer_name}_receipt.pdf'
    if not os.path.exists('static/receipts'):
        os.makedirs('static/receipts')
    pdf.output(pdf_file_path)
    return pdf_file_path
