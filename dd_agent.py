#!/usr/bin/env python3
"""
🔍 Coasty Crypto Due Diligence Agent
=====================================
An autonomous agent that researches crypto projects across multiple
live interfaces, gathers evidence, and compiles a due diligence report.

"Research across live interfaces, gather evidence, and turn it into
something useful end to end." — Coasty Dev

Usage:
  python dd_agent.py "Pepe"
  python dd_agent.py "BRETT" --chain base
  python dd_agent.py "WIF" --chain solana
  python dd_agent.py "Ethereum" --full
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
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
OUTPUT_DIR = Path("dd_reports")


def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


def save_screenshot(b64_data, name):
    OUTPUT_DIR.mkdir(exist_ok=True)
    import base64
    p = OUTPUT_DIR / f"{name}.png"
    p.write_bytes(base64.b64decode(b64_data))
    log(f"📸 {p}")
    return str(p)


def save_report(content, token_name):
    OUTPUT_DIR.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    p = OUTPUT_DIR / f"DD_{token_name.upper()}_{ts}.md"
    p.write_text(content)
    log(f"📄 Report: {p}")
    return str(p)


def create_task(task, max_steps=80):
    resp = requests.post(
        f"{COASTY_BASE}/tasks",
        headers={**HEADERS, "Idempotency-Key": f"dd-{int(time.time())}"},
        json={"task": task, "max_steps": max_steps},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    log(f"🎯 Task: {data['id']}")
    return data


def stream_events(run_id):
    resp = requests.get(
        f"{COASTY_BASE}/runs/{run_id}/events",
        headers={**HEADERS, "Accept": "text/event-stream"},
        stream=True, timeout=600,
    )
    for line in resp.iter_lines(decode_unicode=True):
        if line and line.startswith("data:"):
            try:
                yield json.loads(line[5:].strip())
            except json.JSONDecodeError:
                pass


def wait_run(run_id, timeout=600):
    start = time.time()
    while time.time() - start < timeout:
        r = requests.get(f"{COASTY_BASE}/runs/{run_id}", headers=HEADERS, timeout=30)
        data = r.json()
        s = data.get("status")
        if s in ("succeeded", "failed", "cancelled", "timed_out"):
            return data
        time.sleep(5)
    raise TimeoutError("Run timeout")


# ─── DD Agent ─────────────────────────────────────────────────────────

def run_due_diligence(token: str, chain: str = "", full: bool = False):
    """
    Research a crypto project across multiple live interfaces:
    1. DEXScreener — price, volume, liquidity, chart
    2. CoinGecko / CoinMarketCap — market cap, rankings, history
    3. Project website — team, roadmap, tokenomics
    4. Etherscan/Basescan/Solscan — contract verification, holders
    5. Social media — Twitter/X activity, community size
    
    Gathers evidence from each source and compiles into a DD report.
    """
    
    chain_filter = f" on {chain}" if chain else ""
    depth = "comprehensive" if full else "standard"
    
    log("=" * 60)
    log(f"🔍 CRYPTO DUE DILIGENCE AGENT")
    log("=" * 60)
    log(f"🪙 Token: {token}{chain_filter}")
    log(f"📊 Depth: {depth}")
    log("")

    task = f"""
    You are a crypto research analyst. Perform due diligence on {token}{chain_filter}.
    
    Research this project across MULTIPLE live sources and gather EVIDENCE:
    
    STEP 1 — DEXScreener (Market Data):
    - Go to https://dexscreener.com and search for "{token}"
    - Find the correct trading pair
    - Extract: price, 24h change, volume, liquidity, market cap, FDV
    - Note: number of transactions (buys vs sells), pair creation date
    - Screenshot the token page
    
    STEP 2 — CoinGecko (Market Rankings):
    - Go to https://www.coingecko.com and search for "{token}"
    - Extract: market cap rank, all-time high, all-time low
    - Note: circulating supply, total supply, max supply
    - Screenshot the page
    
    STEP 3 — Contract Verification (On-Chain):
    - Search on Google for "{token} contract address {chain}"
    - Find the contract on a block explorer (Etherscan/Basescan/Solscan)
    - Note: contract address, is it verified, number of holders
    - Check if there are any red flags (honeypot, mint function, etc)
    - Screenshot the contract page
    
    STEP 4 — Project Website (Fundamentals):
    - Search Google for "{token} crypto official website"
    - Visit the project website
    - Look for: team info, whitepaper, roadmap, tokenomics
    - Note: is the team doxxed? is there a working product?
    - Screenshot the website
    
    STEP 5 — Social Presence (Community):
    - Search Google for "{token} crypto twitter"
    - Check their Twitter/X profile
    - Note: follower count, recent activity, engagement
    - Screenshot the profile
    
    {"STEP 6 — Deep Analysis:" if full else ""}
    {"- Search for recent news about " + token if full else ""}
    {"- Check Reddit discussions" if full else ""}
    {"- Look for audit reports" if full else ""}
    
    IMPORTANT:
    - Take screenshots at EVERY step as evidence
    - Be objective — note both positives AND red flags
    - If you can't find info for a step, note it and move on
    - At the end, provide a STRUCTURED SUMMARY with:
      * Project overview
      * Market data
      * Contract analysis
      * Team & fundamentals
      * Community & social
      * Risk assessment (red flags)
      * Overall rating (1-10)
    """

    log("🚀 Launching autonomous research agent...")
    run = create_task(task, max_steps=120 if full else 80)

    screenshots = []
    for event in stream_events(run["id"]):
        etype = event.get("type", "")
        if etype == "screenshot":
            step = event["data"].get("step", len(screenshots))
            ss = save_screenshot(event["data"]["screenshot"], f"{token}_{step:03d}")
            screenshots.append(ss)
        elif etype == "action":
            log(f"🎬 {event['data'].get('action_type', '?')}")
        elif etype == "thought":
            log(f"💭 {event['data'].get('text', '')[:100]}")

    log("")
    log("⏳ Waiting for agent to finish...")
    result = wait_run(run["id"])
    summary = result.get("result", {}).get("summary", "No summary available")

    # Build markdown report
    report = f"""# 🔍 Due Diligence Report: {token.upper()}
**Generated:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}
**Agent:** Coasty Crypto DD Agent
**Sources:** DEXScreener, CoinGecko, Block Explorer, Website, Twitter/X
**Screenshots:** {len(screenshots)} captured as evidence

---

## 📋 Research Summary

{summary}

---

## 📸 Evidence (Screenshots)

"""
    for i, ss in enumerate(screenshots):
        report += f"### Evidence {i+1}\n![Evidence {i+1}]({ss})\n\n"

    report += f"""---

## 🛠️ Technical Details
- **API:** Coasty Computer Use API v1
- **Model:** Coasty managed (85.60% OSWorld)
- **Agent Steps:** {len(screenshots)} screenshots captured
- **Sources Visited:** DEXScreener, CoinGecko, Block Explorer, Project Website, Twitter/X
- **Methodology:** Autonomous multi-source research with visual evidence

---

## ⚠️ Disclaimer
This report is generated by an AI agent for research purposes only.
Always DYOR (Do Your Own Research) before making investment decisions.
This is NOT financial advice.

---

*Built with [Coasty Computer Use API](https://coasty.ai) — Research across live interfaces, gather evidence, turn it into something useful.*
"""

    report_path = save_report(report, token)

    # Print summary
    log("")
    log("=" * 60)
    log(f"✅ DD REPORT COMPLETE: {token.upper()}")
    log("=" * 60)
    log(f"📸 Evidence: {len(screenshots)} screenshots")
    log(f"📄 Report: {report_path}")
    log(f"💰 Status: {result.get('status')}")
    log("")
    print(summary)

    return {
        "token": token,
        "status": result.get("status"),
        "screenshots": screenshots,
        "report": report_path,
        "summary": summary,
    }


# ─── Main ─────────────────────────────────────────────────────────────

def main():
    if not API_KEY:
        print("❌ Set COASTY_API_KEY first!")
        print("   export COASTY_API_KEY='sk-coa-...'")
        print("   Get free key: https://coasty.ai")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("""
🔍 Coasty Crypto DD Agent
==========================
Research any crypto project across 5+ live sources.

Usage:
  python dd_agent.py "PEPE"
  python dd_agent.py "BRETT" --chain base
  python dd_agent.py "WIF" --chain solana
  python dd_agent.py "Ethereum" --full
        """)
        sys.exit(0)

    token = sys.argv[1]
    chain = ""
    full = False

    for i, arg in enumerate(sys.argv):
        if arg == "--chain" and i + 1 < len(sys.argv):
            chain = sys.argv[i + 1]
        if arg == "--full":
            full = True

    run_due_diligence(token, chain, full)


if __name__ == "__main__":
    main()
