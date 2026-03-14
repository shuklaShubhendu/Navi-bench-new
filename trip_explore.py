import asyncio
from playwright.async_api import async_playwright
import time

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Navigating to trip.com hotels...")
        try:
            await page.goto('https://www.trip.com/hotels/list?city=2&cityName=London')
            await page.wait_for_timeout(5000)
            
            # Print the initial URL
            print("Initial URL:", page.url)

            # Let's try to find some filter checkboxes and click them
            # Trip.com usually has a sidebar with filters
            filter_selectors = [
                'input[type="checkbox"]',
                '.filter-checkbox', 
                '.checkbox-group',
            ]
            
            inputs = await page.locator('input[type="checkbox"]').element_handles()
            print(f"Found {len(inputs)} checkboxes")
            for i, checkbox in enumerate(inputs[:5]):
                try:
                    await checkbox.click(force=True)
                    await page.wait_for_timeout(3000)
                    print(f"URL after clicking checkbox {i}:", page.url)
                except Exception as e:
                    print(f"Failed to click checkbox {i}: {e}")
                    
            print("Done exploring.")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

asyncio.run(main())
