import asyncio
import random
import re
from urllib.parse import urljoin
from playwright.async_api import async_playwright

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
EVENT_LINK_HINTS = re.compile(r"(event|conference|expo|summit)", re.I)


async def discover_event_links(page, listing_url, selector, max_links=25):
    await page.goto(listing_url, timeout=45000, wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)
    hrefs = set()
    try:
        links = await page.query_selector_all(selector)
        for link in links:
            href = await link.get_attribute("href")
            if href:
                hrefs.add(urljoin(listing_url, href))
    except Exception:
        pass
    if not hrefs:
        all_links = await page.query_selector_all("a")
        for link in all_links:
            href = await link.get_attribute("href")
            if href and EVENT_LINK_HINTS.search(href):
                hrefs.add(urljoin(listing_url, href))
    return list(hrefs)[:max_links]


async def fetch_page_text(page, url):
    await page.goto(url, timeout=45000, wait_until="domcontentloaded")
    await page.wait_for_timeout(1500)
    text = await page.inner_text("body")
    return text[:12000]


async def run_source(source):
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(user_agent=USER_AGENT)
        links = await discover_event_links(page, source["listing_url"], source["link_selector"])
        print(f"[{source['name']}] found {len(links)} candidate event links")
        for url in links:
            try:
                await asyncio.sleep(random.uniform(2, 4))
                text = await fetch_page_text(page, url)
                results.append({"url": url, "text": text, "source": source["name"]})
            except Exception as e:
                print(f"[{source['name']}] failed on {url}: {e}")
        await browser.close()
    return results
