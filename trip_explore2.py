import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Navigating to trip.com hotels/list...")
        try:
            # Let's try directly hitting the hotel search page for London
            await page.goto('https://uk.trip.com/hotels/list?city=2&cityName=London', wait_until='networkidle')
            await page.wait_for_timeout(5000)
            print("Current URL:", page.url)

            # Extract all links that might be related to filters or pagination to see URL params
            links = await page.evaluate('''() => {
                const anchors = Array.from(document.querySelectorAll('a'));
                return anchors.map(a => a.href).filter(href => href.includes('trip.com/hotels/') && (href.includes('?') || href.includes('-')));
            }''')
            print(f"Found {len(links)} links. Here is a sample:")
            for l in list(set(links))[:20]:
                print(l)

            # Also try to extract any div that looks like a filter to see if it has data attributes
            filters = await page.evaluate('''() => {
                const els = document.querySelectorAll('[data-filter-id], [data-id], .filter-item, input[type="checkbox"]');
                return Array.from(els).map(el => el.outerHTML).slice(0, 10);
            }''')
            print("\nPotential filter elements:")
            for f in filters:
                print(f)
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

asyncio.run(main())
