import puppeteer from 'puppeteer';

const browser = await puppeteer.launch({
  headless: "new",
});
const page = await browser.newPage();
await page.goto('https://example.com');
const h1 = await page.waitForSelector("h1");
const textContent = await h1?.evaluate((element: HTMLHeadingElement) => element.textContent);
console.log("textContent", textContent);
await browser.close();
