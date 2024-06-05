function printQRCode() {
    const qrCodeImage = document.getElementById('qr-code').src;
    const locationText = document.getElementById('qr-location').innerText;
    const dateText = document.getElementById('qr-date').innerText;

    // Open a new window to print the QR code with location and date
    const printWindow = window.open('', '_blank');
    printWindow.document.write('<html><head><title>Print QR Code</title></head><body>');
    printWindow.document.write('<div style="text-align: center;">');
    printWindow.document.write('<img src="' + qrCodeImage + '" alt="QR Code">');
    printWindow.document.write('<p>' + locationText + '</p>');
    printWindow.document.write('<p>' + dateText + '</p>');
    printWindow.document.write('</div>');
    printWindow.document.write('</body></html>');
    printWindow.document.close();
    printWindow.print();
}
