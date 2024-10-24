const puppeteer = require('puppeteer');

puppeteer.launch({ headless: true }).then(async (browser) => {
    console.log('Chromium downloaded and browser instance launched');
    await browser.close();
}).catch(error => {
    console.error('Error downloading Chromium:', error);
});

