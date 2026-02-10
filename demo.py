#!/usr/bin/env python
"""
Human-in-the-loop demo of Yutori Navi-Bench (Zillow) where:

- The human + Playwright browser act as the "agent loop".
- Each page navigation is treated as an agent step.
- We call evaluator.update(...) on every step.
- At the end, we call evaluator.compute() for the final score.

This version includes bot-detection mitigations:
  1. playwright-stealth for JS-level fingerprint patching
  2. Fallback to connect_over_cdp with a real Chrome instance
  3. Additional context/launch tweaks

Usage:
    # Default mode: stealth Playwright browser
    python demo.py

    # CDP mode: connect to a real Chrome you launched manually with:
    #   google-chrome --remote-debugging-port=9222
    python demo.py --cdp
"""

import argparse
import asyncio
import json
import sys
from typing import Any, Dict

from playwright.async_api import Page, async_playwright

from navi_bench.base import DatasetItem, instantiate

# Try to import playwright-stealth; warn if missing
try:
    from playwright_stealth import stealth_async

    HAS_STEALTH = True
except ImportError:
    HAS_STEALTH = False

# ---------------------------------------------------------------------------
# Local Zillow task
# ---------------------------------------------------------------------------
ZILLOW_LOCAL_TASK = {
    "task_id": "navi_bench/zillow/for_sale_filters/0",
    "task_generation_config_json": json.dumps(
        {
            "_target_": "navi_bench.zillow.zillow_url_match.generate_task_config",
            "url": "https://www.zillow.com/homes/for_sale/",
            "task": (
                "Find houses for sale in Los Angeles, CA with at least 3 bedrooms "
                "priced under $800,000"
            ),
            "location": "San Francisco, CA, United States",
            "timezone": "America/Los_Angeles",
            "ground_truth_url": (
                "https://www.zillow.com/homes/for_sale/Los-Angeles,-CA_rb/"
                '?searchQueryState={"filterState":{"beds":{"min":3},'
                '"price":{"max":800000},"isHouse":{"value":true}}}'
            ),
        }
    ),
    "env": "real",
    "domain": "zillow",
    "l1_category": "realestate",
    "l2_category": "for_sale_filters",
    "suggested_split": "validation",
    "suggested_difficulty": "medium",
}

# ---------------------------------------------------------------------------
# Stealth init script – patches many properties that bot detectors check
# beyond what playwright-stealth covers.
# ---------------------------------------------------------------------------
EXTRA_STEALTH_JS = """
// Hide webdriver
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

// Fake plugins (real Chrome has at least a few)
Object.defineProperty(navigator, 'plugins', {
    get: () => {
        const plugins = [
            { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer',
              description: 'Portable Document Format' },
            { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
              description: '' },
            { name: 'Native Client', filename: 'internal-nacl-plugin',
              description: '' },
        ];
        plugins.length = 3;
        return plugins;
    }
});

// Fake languages
Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en'],
});

// Remove Playwright/Automation artifacts
delete window.__playwright;
delete window.__pw_manual;

// Patch permissions API
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) =>
    parameters.name === 'notifications'
        ? Promise.resolve({ state: Notification.permission })
        : originalQuery(parameters);

// Chrome runtime mock (real Chrome has this, Playwright doesn't)
if (!window.chrome) { window.chrome = {}; }
if (!window.chrome.runtime) {
    window.chrome.runtime = {
        connect: function() {},
        sendMessage: function() {},
    };
}
"""


async def attach_human_agent_loop(page: Page, evaluator) -> None:
    """
    This is the human-agent-loop. Execute the task by navigating the website.
    """

    async def on_navigation():
        try:
            await evaluator.update(url=page.url, page=page)
        except Exception as e:
            print(
                f"[WARN] evaluator.update(url={page.url!r}, page={page}) failed: {e}"
            )

    page.on("framenavigated", lambda frame: asyncio.create_task(on_navigation()))


# ---------------------------------------------------------------------------
# Browser launch helpers
# ---------------------------------------------------------------------------
async def launch_stealth_browser(p):
    """Launch a Playwright Chromium browser with stealth mitigations."""
    if not HAS_STEALTH:
        print(
            "[WARN] playwright-stealth is not installed. "
            "Install it for better bot-detection evasion:\n"
            "  pip install playwright-stealth\n"
        )

    browser = await p.chromium.launch(
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-extensions",
            "--disable-component-extensions-with-background-pages",
            "--disable-default-apps",
            "--disable-dev-shm-usage",
        ],
    )

    context = await browser.new_context(
        viewport={"width": 1280, "height": 720},
        user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        locale="en-US",
        timezone_id="America/Los_Angeles",
        geolocation={"latitude": 37.7749, "longitude": -122.4194},
        permissions=["geolocation"],
        color_scheme="light",
    )

    # Extra JS-level patches
    await context.add_init_script(EXTRA_STEALTH_JS)

    page = await context.new_page()

    # Apply playwright-stealth if available
    if HAS_STEALTH:
        await stealth_async(page)

    return browser, context, page


async def connect_cdp_browser(p, cdp_url="http://localhost:9222"):
    """
    Connect to a real Chrome instance that was launched with:
        google-chrome --remote-debugging-port=9222

    This is the most robust anti-detection approach because the browser
    is a genuine Chrome install with real fingerprints.
    """
    print(f"Connecting to Chrome via CDP at {cdp_url} ...")
    browser = await p.chromium.connect_over_cdp(cdp_url)
    context = browser.contexts[0] if browser.contexts else await browser.new_context()
    page = context.pages[0] if context.pages else await context.new_page()
    return browser, context, page


# ---------------------------------------------------------------------------
# Main session
# ---------------------------------------------------------------------------
async def run_human_session(row: Dict[str, Any], use_cdp: bool = False) -> None:
    """Run the human demo with a Zillow task row."""
    # Validate the row and generate the task config
    dataset_item = DatasetItem.model_validate(row)
    task_config = dataset_item.generate_task_config()

    # Instantiate the evaluator
    evaluator = instantiate(task_config.eval_config)

    print("\n" + "=" * 80)
    print("ZILLOW DEMO TASK")
    print("=" * 80)
    print(f"Task ID:  {row['task_id']}")
    print(f"Domain:   {row['domain']}")
    print(f"URL:      {task_config.url}")
    print(f"Task:     {task_config.task}")
    print(f"Mode:     {'CDP (real Chrome)' if use_cdp else 'Stealth Playwright'}")
    print("=" * 80 + "\n")

    if use_cdp:
        print(
            "Make sure you launched Chrome with:\n"
            "  google-chrome --remote-debugging-port=9222\n"
            "  (or: /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome "
            "--remote-debugging-port=9222)\n"
        )

    input("Press Enter when ready to start the browser...")

    async with async_playwright() as p:
        if use_cdp:
            browser, context, page = await connect_cdp_browser(p)
        else:
            browser, context, page = await launch_stealth_browser(p)

        await page.goto(task_config.url, timeout=60_000, wait_until="load")

        print(
            "\nBrowser opened.\n"
            "➡ You are now the agent.\n"
            "➡ Follow the instructions in the terminal to complete the task.\n"
            "➡ When done, press ENTER in this terminal (do not close the browser).\n"
        )

        # Reset the evaluator
        await evaluator.reset()
        await evaluator.update(url=task_config.url, page=page)
        await attach_human_agent_loop(page, evaluator)

        # Wait for user to press Enter when task is complete
        await asyncio.to_thread(
            input, "\nPress Enter when you've completed the task... "
        )

        # Final update before computing result
        try:
            await evaluator.update(url=page.url, page=page)
        except Exception as e:
            print(
                f"[WARN] Final evaluator.update(url={page.url!r}, page={page}) "
                f"failed: {e}"
            )

        # Compute the evaluation result
        print("\nComputing evaluation result...\n")
        result = await evaluator.compute()

        # Now we can close the browser
        await context.close()
        await browser.close()

    # Report the result
    print("=" * 80)
    print("RESULT")
    print("=" * 80)
    print(f"Score: {getattr(result, 'score', None)}")
    if hasattr(result, "match"):
        print(f"Match: {result.match}")
    if hasattr(result, "details"):
        print(f"Details: {result.details}")
    print("=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Human-in-the-loop Navi-Bench demo with bot-detection mitigations"
    )
    parser.add_argument(
        "--cdp",
        action="store_true",
        help=(
            "Connect to a real Chrome instance via CDP instead of launching "
            "Playwright's bundled Chromium. Most robust anti-detection. "
            "Launch Chrome first with: google-chrome --remote-debugging-port=9222"
        ),
    )
    parser.add_argument(
        "--cdp-url",
        default="http://localhost:9222",
        help="CDP endpoint URL (default: http://localhost:9222)",
    )
    args = parser.parse_args()

    asyncio.run(run_human_session(ZILLOW_LOCAL_TASK, use_cdp=args.cdp))


if __name__ == "__main__":
    main()