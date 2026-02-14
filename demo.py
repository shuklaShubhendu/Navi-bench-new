#!/usr/bin/env python
"""
Human-in-the-loop demo of Yutori Navi-Bench (Zillow) where:

- The human + Playwright browser act as the "agent loop".
- Each page navigation is treated as an agent step.
- We call evaluator.update(...) on every step.
- At the end, we call evaluator.compute() for the final score.

Uses CDP (Chrome DevTools Protocol) by default to connect to a real
Chrome browser, which bypasses Zillow's bot detection entirely.

Usage:
    python demo.py              # Auto-launches Chrome and connects via CDP
"""

import asyncio
import json
import os
import platform
import shutil
import subprocess
import time
from typing import Any, Dict

from playwright.async_api import Page, async_playwright

from navi_bench.base import DatasetItem, instantiate

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
                "?searchQueryState=%7B%22filterState%22%3A%7B%22beds%22%3A%7B%22min%22%3A3%7D%2C"
                "%22price%22%3A%7B%22max%22%3A800000%7D%2C%22isHouse%22%3A%7B%22value%22%3Atrue%7D%7D%7D"
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
# Chrome auto-launcher (CDP mode)
# ---------------------------------------------------------------------------
CDP_PORT = 9222
CDP_URL = f"http://localhost:{CDP_PORT}"

# Common Chrome install paths by OS
CHROME_PATHS_WINDOWS = [
    os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
    os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
    os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
]
CHROME_PATHS_MAC = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]
CHROME_PATHS_LINUX = [
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium-browser",
    "/usr/bin/chromium",
]


def find_chrome() -> str:
    """Find the Chrome executable on this system."""
    # Try 'which'/'where' first
    cmd = "where" if platform.system() == "Windows" else "which"
    for name in ("google-chrome", "chrome", "chromium"):
        path = shutil.which(name)
        if path:
            return path

    # Try known paths
    system = platform.system()
    if system == "Windows":
        candidates = CHROME_PATHS_WINDOWS
    elif system == "Darwin":
        candidates = CHROME_PATHS_MAC
    else:
        candidates = CHROME_PATHS_LINUX

    for p in candidates:
        if os.path.isfile(p):
            return p

    raise FileNotFoundError(
        "Could not find Chrome. Please install Google Chrome or set the "
        "CHROME_PATH environment variable to the path of the Chrome executable."
    )


def launch_chrome_with_cdp(chrome_path: str, port: int = CDP_PORT) -> subprocess.Popen:
    """Launch Chrome with --remote-debugging-port and return the process."""
    # Use a dedicated user-data-dir so it doesn't conflict with existing Chrome
    user_data = os.path.join(os.path.expanduser("~"), ".navi-bench-chrome-profile")

    args = [
        chrome_path,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-infobars",
    ]

    print(f"Launching Chrome: {chrome_path}")
    print(f"  CDP port: {port}")
    print(f"  Profile:  {user_data}\n")

    # CREATE_NO_WINDOW on Windows so the console isn't blocked
    kwargs = {}
    if platform.system() == "Windows":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

    proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kwargs)
    return proc


def wait_for_cdp(url: str = CDP_URL, timeout: float = 15.0) -> bool:
    """Wait until the CDP endpoint is reachable."""
    import urllib.request
    import urllib.error
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"{url}/json/version", timeout=2)
            return True
        except (urllib.error.URLError, OSError):
            time.sleep(0.5)
    return False


async def connect_cdp_browser(p, cdp_url: str = CDP_URL):
    """Connect to Chrome via CDP."""
    browser = await p.chromium.connect_over_cdp(cdp_url)
    context = browser.contexts[0] if browser.contexts else await browser.new_context()
    page = context.pages[0] if context.pages else await context.new_page()
    return browser, context, page


# ---------------------------------------------------------------------------
# Main session
# ---------------------------------------------------------------------------
async def run_human_session(row: Dict[str, Any]) -> None:
    """Run the human demo with a Zillow task row using CDP (real Chrome)."""
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
    print(f"Mode:     CDP (real Chrome — bypasses bot detection)")
    print("=" * 80 + "\n")

    # Find and launch Chrome
    chrome_path = os.environ.get("CHROME_PATH") or find_chrome()
    chrome_proc = launch_chrome_with_cdp(chrome_path)

    print("Waiting for Chrome to start...")
    if not wait_for_cdp():
        chrome_proc.kill()
        raise RuntimeError(
            "Chrome did not start in time. Make sure no other Chrome is "
            "running with --remote-debugging-port, or close all Chrome windows first."
        )
    print("Chrome is ready!\n")

    try:
        async with async_playwright() as p:
            browser, context, page = await connect_cdp_browser(p)

            await page.goto(task_config.url, timeout=60_000, wait_until="load")

            print(
                "Browser opened.\n"
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
                    f"[WARN] Final evaluator.update failed: {e}"
                )

            # Compute the evaluation result
            print("\nComputing evaluation result...\n")
            result = await evaluator.compute()

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

    finally:
        # Clean up Chrome process
        chrome_proc.terminate()


if __name__ == "__main__":
    asyncio.run(run_human_session(ZILLOW_LOCAL_TASK))