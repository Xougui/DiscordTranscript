const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  const htmlPath = 'file:///' + path.resolve(__dirname, 'examples/test_render.html').replace(/\\/g, '/');
  
  await page.goto(htmlPath, { waitUntil: 'networkidle' });

  // 1: Top / Bienvenue
  await page.screenshot({ path: 'screenshots/1.png' });

  // 2: Embed rich (Statut système - index 6)
  await page.evaluate(() => {
    const el = document.querySelectorAll('.chatlog__message-group')[6];
    if (el) el.scrollIntoView();
  });
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'screenshots/2.png' });

  // 3: Boutons V1 + Select menu (index 7)
  await page.evaluate(() => {
    const el = document.querySelectorAll('.chatlog__message-group')[7];
    if (el) el.scrollIntoView();
  });
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'screenshots/3.png' });

  // 4: Audio + Vidéo MP4 (index 15)
  await page.evaluate(() => {
    const el = document.querySelectorAll('.chatlog__message-group')[15];
    if (el) el.scrollIntoView();
  });
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'screenshots/4.png' });

  // 5: Message supprimé + Spoiler + Container V2 (index 17)
  await page.evaluate(() => {
    const el = document.querySelectorAll('.chatlog__message-group')[17];
    if (el) el.scrollIntoView();
  });
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'screenshots/5.png' });

  // 6: Containers V2 complet (index 19)
  await page.evaluate(() => {
    const el = document.querySelectorAll('.chatlog__message-group')[19];
    if (el) el.scrollIntoView();
  });
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'screenshots/6.png' });

  // 7: Vidéo YouTube + Gif + Pièces jointes (index 22)
  await page.evaluate(() => {
    const el = document.querySelectorAll('.chatlog__message-group')[22];
    if (el) el.scrollIntoView();
  });
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'screenshots/7.png' });

  // 8: Tout en bas + Panneau résumé
  const chatMessages = page.locator('.chatlog__message-group');
  await chatMessages.last().scrollIntoViewIfNeeded();
  await page.waitForTimeout(200);
  await page.click('#summary-button');
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'screenshots/8.png' });

  await browser.close();
  console.log('Screenshots correctly assigned by exact message group index!');
})();
