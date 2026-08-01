#!/usr/bin/env python3
"""
🔍 Coasty Universal Web Scraper Agent
======================================
An autonomous computer-use agent that scrapes data from complex websites.
Just describe what you want — the agent handles scrolling, clicking,
pagination, and extraction automatically.

Examples:
  python scraper.py "https://www.coingecko.com" "top 10 tokens by market cap"
  python scraper.py "https://www.producthunt.com" "today's top 5 products"
  python scraper.py "https://news.ycombinator.com" "top 10 headlines"
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timezone
from pathlib import Path

# ─── Config ───────────────────────────────────────────────────────────
COASTY_BASE = "https://coasty.ai/v1"
API_KEY = os.environ.get("COASTY_API_KEY", "")

HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json",
}

OUTPUT_DIR = Path("scraped_data")


# ─── Helpers ──────────────────────────────────────────────────────────
def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


def save_screenshot(b64_data: str, name: str) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    import base64
    path = OUTPUT_DIR / f"{name}.png"
    path.write_bytes(base64.b64decode(b64_data))
    log(f"📸 Screenshot: {path}")
    return path


def save_data(data: dict, name: str) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / f"{name}.json"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    log(f"💾 Data saved: {path}")
    return path


def stream_run_events(run_id: str):
    resp = requests.get(
        f"{COASTY_BASE}/runs/{run_id}/events",
        headers={**HEADERS, "Accept": "text/event-stream"},
        stream=True,
        timeout=300,
    )
    for line in resp.iter_lines(decode_unicode=True):
        if line and line.startswith("data:"):
            try:
                yield json.loads(line[5:].strip())
            except json.JSONDecodeError:
                pass


def wait_for_run(run_id: str, timeout: int = 300) -> dict:
    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(
            f"{COASTY_BASE}/runs/{run_id}",
            headers=HEADERS,
            timeout=30,
        )
        data = resp.json()
        status = data.get("status", "unknown")
        if status in ("succeeded", "failed", "cancelled", "timed_out"):
            log(f"✅ Run finished: {status}")
            return data
        log(f"⏳ Status: {status}...")
        time.sleep(5)
    raise TimeoutError(f"Run did not finish in {timeout}s")


# ─── Scraper Core ─────────────────────────────────────────────────────

def scrape(url: str, instruction: str, max_steps: int = 50) -> dict:
    """
    Scrape data from any website using Coasty.
    
    Args:
        url: Target website URL
        instruction: What data to extract (plain English)
        max_steps: Max agent steps (default 50)
    
    Returns:
        dict with task result, screenshots, and extracted data
    """
    log("=" * 60)
    log(f"🔍 COASTY WEB SCRAPER")
    log("=" * 60)
    log(f"🌐 Target: {url}")
    log(f"📋 Task: {instruction}")
    log("")

    # Build the task prompt
    task_prompt = f"""
    Navigate to {url} and extract the following data:
    
    {instruction}
    
    Instructions:
    1. Open the URL in the browser
    2. Wait for the page to fully load
    3. Take a screenshot of the page
    4. If needed, scroll down to find more data
    5. If needed, click on elements to expand/show more content
    6. If there's pagination, go through the next pages
    7. Extract ALL the requested data
    8. At the end, provide a CLEAR SUMMARY of the extracted data
       in a structured format (JSON if possible)
    9. Take a final screenshot showing the extracted data
    
    Be thorough. Extract every item that matches the request.
    """

    # Create task
    idem_key = f"scraper-{int(time.time())}"
    resp = requests.post(
        f"{COASTY_BASE}/tasks",
        headers={**HEADERS, "Idempotency-Key": idem_key},
        json={
            "task": task_prompt,
            "max_steps": max_steps,
        },
        timeout=30,
    )
    resp.raise_for_status()
    run = resp.json()
    log(f"🎯 Task created: {run['id']}")

    # Stream events
    screenshots = []
    actions = []
    for event in stream_run_events(run["id"]):
        etype = event.get("type", "")
        
        if etype == "screenshot":
            step = event['data'].get('step', len(screenshots))
            ss = save_screenshot(event["data"]["screenshot"], f"step_{step:03d}")
            screenshots.append(str(ss))
        
        elif etype == "action":
            action = event["data"].get("action_type", "unknown")
            actions.append(action)
            log(f"🎬 Action: {action}")
        
        elif etype == "thought":
            text = event["data"].get("text", "")[:120]
            log(f"💭 {text}")
        
        elif etype == "scroll":
            log(f"📜 Scrolling...")

    # Get final result
    result = wait_for_run(run["id"])
    
    # Save everything
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output = {
        "url": url,
        "instruction": instruction,
        "task_id": run["id"],
        "status": result.get("status"),
        "summary": result.get("result", {}).get("summary", ""),
        "screenshots": screenshots,
        "actions_count": len(actions),
        "actions": list(set(actions)),
        "timestamp": timestamp,
    }
    
    save_data(output, f"scrape_{timestamp}")
    
    # Print summary
    log("")
    log("=" * 60)
    log("📊 SCRAPE RESULTS")
    log("=" * 60)
    log(f"✅ Status: {output['status']}")
    log(f"📸 Screenshots: {len(screenshots)}")
    log(f"🎬 Actions: {len(actions)}")
    log("")
    
    if output["summary"]:
        log("📋 Extracted Data:")
        log("-" * 40)
        print(output["summary"])
        log("-" * 40)
    
    return output


# ─── Preset Scrapers ──────────────────────────────────────────────────

PRESETS = {
    "coingecko": {
        "url": "https://www.coingecko.com",
        "task": """
        Extract the top 10 cryptocurrencies by market cap:
        - Name
        - Symbol  
        - Current price (USD)
        - 24h change (%)
        - Market cap
        - 24h volume
        
        Scroll down if needed to see all 10.
        Format as a numbered list.
        """,
        "max_steps": 40,
    },
    "dexscreener": {
        "url": "https://dexscreener.com",
        "task": """
        Extract the top 8 trending tokens:
        - Token name and symbol
        - Chain (ETH/SOL/BASE/etc)
        - Current price
        - 24h price change (%)
        - 24h volume
        - Liquidity
        
        Format as a structured list.
        """,
        "max_steps": 40,
    },
    "producthunt": {
        "url": "https://www.producthunt.com",
        "task": """
        Extract today's top 5 products on Product Hunt:
        - Product name
        - Tagline/description
        - Number of upvotes
        - Category
        
        Click on each product if needed to get details.
        """,
        "max_steps": 50,
    },
    "hackernews": {
        "url": "https://news.ycombinator.com",
        "task": """
        Extract the top 10 stories on Hacker News:
        - Title
        - URL/domain
        - Points
        - Number of comments
        - Posted time
        
        Format as a numbered list.
        """,
        "max_steps": 30,
    },
    "github-trending": {
        "url": "https://github.com/trending",
        "task": """
        Extract the top 10 trending repositories on GitHub:
        - Repository name
        - Description
        - Language
        - Stars
        - Stars today
        
        Format as a numbered list.
        """,
        "max_steps": 40,
    },
    "reddit-crypto": {
        "url": "https://www.reddit.com/r/cryptocurrency/hot/",
        "task": """
        Extract the top 10 hot posts from r/cryptocurrency:
        - Post title
        - Upvotes
        - Number of comments
        - Posted time
        
        Scroll down to find all 10 posts.
        """,
        "max_steps": 50,
    },
}


def list_presets():
    log("📦 Available presets:")
    log("")
    for name, config in PRESETS.items():
        log(f"  • {name:20s} → {config['url']}")
    log("")
    log("Usage:")
    log('  python scraper.py --preset coingecko')
    log('  python scraper.py "https://example.com" "extract data"')


# ─── Main ─────────────────────────────────────────────────────────────

def main():
    if not API_KEY:
        print("❌ Set COASTY_API_KEY first!")
        print("   export COASTY_API_KEY='sk-coa-...'")
        print()
        print("   Get a free sandbox key at: https://coasty.ai")
        sys.exit(1)

    # Parse args
    if len(sys.argv) < 2:
        print("""
🔍 Coasty Universal Web Scraper Agent
======================================

Usage:
  python scraper.py --preset <name>
  python scraper.py <url> "<what to extract>"
  python scraper.py --list

Examples:
  python scraper.py --preset coingecko
  python scraper.py --preset dexscreener
  python scraper.py "https://example.com" "extract all product prices"
  python scraper.py "https://news.ycombinator.com" "top 10 headlines"
        """)
        sys.exit(0)

    if sys.argv[1] == "--list":
        list_presets()
        sys.exit(0)

    if sys.argv[1] == "--preset":
        if len(sys.argv) < 3 or sys.argv[2] not in PRESETS:
            print(f"❌ Unknown preset. Available: {', '.join(PRESETS.keys())}")
            sys.exit(1)
        preset = PRESETS[sys.argv[2]]
        scrape(preset["url"], preset["task"], preset["max_steps"])
    else:
        url = sys.argv[1]
        instruction = sys.argv[2] if len(sys.argv) > 2 else "Extract all visible data from this page"
        scrape(url, instruction)


if __name__ == "__main__":
    main()
