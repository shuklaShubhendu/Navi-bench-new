import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Navigating to trip.com...")
        try:
            await page.goto('https://uk.trip.com/hotels/list?city=2&cityName=London')
            await page.wait_for_timeout(8000)
            
            print("Current URL:", page.url)

            # Extract any element with "data-filter-id" or similar
            html = await page.content()
            import re
            
            # Find common param names like 'star=', 'price=', 'amenity=' in script tags or anchor hrefs
            finds = re.findall(r'href="[^"]*hotels/[a-zA-Z0-9\-\?=&]*"', html)
            print("Found hrefs:")
            for f in list(set(finds))[:10]:
                print(f)
                
            inputs = await page.evaluate('''() => {
                let els = document.querySelectorAll('input, button, a');
                return Array.from(els).map(el => {
                    return {
                        tag: el.tagName,
                        id: el.id,
                        class: el.className,
                        text: el.innerText || el.value,
                        href: el.href || ''
                    };
                }).filter(o => (o.text && o.text.includes('Pool')) || (o.href && o.href.includes('?')));
            }''')
            print("Filter elements:", inputs[:10])

        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

asyncio.run(main())
