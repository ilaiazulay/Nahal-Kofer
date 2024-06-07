function printQRCode() {
    const qrCodeImage = document.getElementById('qr-code').src;
    const locationText = document.getElementById('qr-location').innerText;
    const dateText = document.getElementById('qr-date').innerText;

    // Open a new window to print the QR code with location and date
    const printWindow = window.open('', '_blank');
    printWindow.document.write('<html><head><title>Print QR Code</title>');
    printWindow.document.write('<style>');
    printWindow.document.write('@media print {');
    printWindow.document.write('body { width: 29mm; height: 90mm; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 2mm; }');
    printWindow.document.write('img { width: 27mm; height: auto; margin-bottom: 2mm; }');
    printWindow.document.write('p { font-size: 10px; margin: 0;}');
    printWindow.document.write('}');
    printWindow.document.write('</style>');
    printWindow.document.write('</head><body>');
    printWindow.document.write('<img src="' + qrCodeImage + '" alt="QR Code">');
    printWindow.document.write('<p>' + locationText + '</p>');
    printWindow.document.write('<p>' + dateText + '</p>');
    printWindow.document.write('</body></html>');
    printWindow.document.close();
    printWindow.print();
}
