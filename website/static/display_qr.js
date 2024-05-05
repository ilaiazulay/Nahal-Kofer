function printQRCode() {
    const qrCodeImage = document.getElementById('qr-code').src;

    // Open a new window to print the QR code
    const printWindow = window.open('', '_blank');
    printWindow.document.write('<html><head><title>Print QR Code</title></head><body>');
    printWindow.document.write('<img src="' + qrCodeImage + '" alt="QR Code">');
    printWindow.document.write('</body></html>');
    printWindow.document.close();
    printWindow.print();