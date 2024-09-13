import qrcode

def generate_qr_code(data, filename):
    img = qrcode.make(data)
    img.save(filename)

# Example usage
generate_qr_code("test123", "static/qr_codes/test123.png")
