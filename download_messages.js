const { Client, LocalAuth } = require('whatsapp-web.js');
const fs = require('fs');
const path = require('path');

const sessionFolderPath = path.join(__dirname, 'session');
const client = new Client({
    authStrategy: new LocalAuth({ clientId: "client-one", dataPath: sessionFolderPath }),
    puppeteer: { executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe' }
});

const groupId = process.argv[2]; // Group ID from command line
const analysisType = process.argv[3]; // Analysis type: 'main_topics' or 'specific_messages'

client.on('qr', qr => console.log('QR code received. Please scan it.'));
client.on('ready', async () => {
    console.log('Client is ready!');
    const chat = await client.getChatById(groupId);
    const messages = await chat.fetchMessages({ limit: 1000 });

    const now = Math.floor(Date.now() / 1000);
    const recentMessages = messages.filter(msg => msg.timestamp >= now - 86400);

    let filteredMessages;
    if (analysisType === 'specific_messages') {
        const criteria = process.argv[4]; // User-defined criteria
        filteredMessages = recentMessages.filter(msg => msg.body.includes(criteria));
    } else {
        filteredMessages = recentMessages;
    }

    const messagesData = filteredMessages.map(msg => ({
        id: msg.id._serialized,
        from: msg.from,
        body: msg.body,
        timestamp: msg.timestamp,
        reactions: msg.reactions?.length || 0
    }));

    fs.writeFileSync(`static/messages_${groupId}.json`, JSON.stringify(messagesData, null, 2));
    console.log(`Messages saved for group ${chat.name}`);
    client.destroy();
});

client.on('auth_failure', () => fs.rmSync(sessionFolderPath, { recursive: true }));
client.on('disconnected', () => fs.rmSync(sessionFolderPath, { recursive: true }));
client.initialize();
