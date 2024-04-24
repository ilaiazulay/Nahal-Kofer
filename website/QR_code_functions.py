import base64
import hashlib
from datetime import datetime
import qrcode
from io import BytesIO
from . import db
from .models import QRCode, LabTest  # Assuming QRCode is your model


def generate_qr_code(location, name):
    unique_str = f"{datetime.utcnow()}_{location}_{name}"
    unique_code = hashlib.sha256(unique_str.encode()).hexdigest()[:10]
    created_at = datetime.utcnow()

    # Generate QR code content as a URL
    base_url = "http://localhost:5000/submit_test"  # Change 'yourdomain.com' to your actual domain
    qr_url = f"{base_url}?code={unique_code}&name={name}&qr_created_time={created_at.isoformat()}&location={location}"

    # Generate the QR code image
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    # Convert the image to a format that can be displayed in HTML
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    img_data = base64.b64encode(img_io.getvalue()).decode('utf-8')

    # Create a new QRCode object and associate it with a LabTest
    lab_test = LabTest(location=location)  # Create LabTest object with relevant data
    db.session.add(lab_test)
    db.session.commit()

    # Optionally save QR code data to database
    qr_code_entry = QRCode(code=unique_code, name=name, location=location, lab_test_id=lab_test.id)
    db.session.add(qr_code_entry)
    db.session.commit()

    return img_data
