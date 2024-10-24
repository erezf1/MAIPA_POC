const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode');
const fs = require('fs');
const path = require('path');

// Define the session folder path
const sessionFolderPath = path.join(__dirname, 'session');

// Clear session folder to force new QR generation
if (fs.existsSync(sessionFolderPath)) {
    fs.rmSync(sessionFolderPath, { recursive: true, force: true });
    console.log('Old session folder cleared.');
}

// Initialize WhatsApp client
const client = new Client({
    authStrategy: new LocalAuth({ clientId: "client-one", dataPath: sessionFolderPath }),
    puppeteer: { headless: true, executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe' }
});

// QR code event: Save and print the QR code
client.on('qr', async (qr) => {
    console.log('QR code event received.');

    try {
        const qrDataUrl = await qrcode.toDataURL(qr);
        
        // Save the QR code to qr_code.txt
        fs.writeFileSync('static/qr_code.txt', qrDataUrl, { flag: 'w' });
        console.log('QR code saved as base64 data.');

        // Print the full QR code to the terminal
        console.log('Generated QR Code (JS):', qrDataUrl);
    } catch (error) {
        console.error('Error generating QR code:', error);
    }
});

client.on('authenticated', () => {
    console.log('Authenticated successfully!');
});

client.on('auth_failure', (msg) => {
    console.error('Authentication failed:', msg);
});

client.on('ready', () => {
    console.log('WhatsApp client is ready!');
});

client.on('disconnected', (reason) => {
    console.log('Client disconnected:', reason);
    if (fs.existsSync(sessionFolderPath)) {
        fs.rmSync(sessionFolderPath, { recursive: true });
        console.log('Session folder cleared on disconnect.');
    }
});

client.initialize();
