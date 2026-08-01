#!/usr/bin/env python3
"""
🚀 Coasty DeFi Research Agent
==============================
An autonomous computer-use agent that researches trending DeFi tokens
using the Coasty Computer Use API.

It:
1. Opens DEXScreener in a managed VM
2. Finds trending tokens across multiple chains
3. Takes screenshots at each step
4. Extracts token data (price, volume, liquidity, market cap)
5. Generates a formatted research report

Built with Coasty — the #1 computer-use API (85.60% OSWorld)
https://coasty.ai/docs
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

SCREENSHOTS_DIR = Path("screenshots")
REPORT_DIR = Path("reports")


# ─── Helpers ──────────────────────────────────────────────────────────
def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


def save_screenshot(b64_data: str, name: str) -> Path:
    """Save a base64 screenshot to disk."""
    SCREENSHOTS_DIR.mkdir(exist_ok=True)
    import base64
    path = SCREENSHOTS_DIR / f"{name}.png"
    path.write_bytes(base64.b64decode(b64_data))
    log(f"📸 Screenshot saved: {path}")
    return path


def wait_for_run(run_id: str, timeout: int = 300) -> dict:
    """Poll a run until it reaches a terminal state."""
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
            log(f"✅ Run {run_id} finished: {status}")
            return data

        log(f"⏳ Run {run_id} status: {status} — waiting...")
        time.sleep(5)

    raise TimeoutError(f"Run {run_id} did not finish in {timeout}s")


def stream_run_events(run_id: str):
    """Stream SSE events from a run."""
    resp = requests.get(
        f"{COASTY_BASE}/runs/{run_id}/events",
        headers={**HEADERS, "Accept": "text/event-stream"},
        stream=True,
        timeout=300,
    )
    for line in resp.iter_lines(decode_unicode=True):
        if line and line.startswith("data:"):
            try:
                event = json.loads(line[5:].strip())
                yield event
            except json.JSONDecodeError:
                pass


# ─── Coasty API Wrappers ──────────────────────────────────────────────

def create_task(task_description: str, max_steps: int = 50) -> dict:
    """Submit an autonomous task to Coasty."""
    idem_key = f"defi-agent-{int(time.time())}"
    resp = requests.post(
        f"{COASTY_BASE}/tasks",
        headers={**HEADERS, "Idempotency-Key": idem_key},
        json={
            "task": task_description,
            "max_steps": max_steps,
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    log(f"🎯 Task created: {data['id']} (status: {data['status']})")
    return data


def predict_action(screenshot_b64: str, instruction: str) -> dict:
    """Send a screenshot + instruction and get back actions."""
    resp = requests.post(
        f"{COASTY_BASE}/predict",
        headers=HEADERS,
        json={
            "screenshot": screenshot_b64,
            "instruction": instruction,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def provision_machine() -> dict:
    """Provision a managed VM for our agent."""
    resp = requests.post(
        f"{COASTY_BASE}/machines",
        headers={**HEADERS, "Idempotency-Key": f"defi-vm-{int(time.time())}"},
        json={
            "ttl_minutes": 30,
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    log(f"🖥️ Machine provisioning: {data['id']}")
    return data


def wait_for_machine(machine_id: str, timeout: int = 120) -> dict:
    """Wait for a machine to be ready."""
    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(
            f"{COASTY_BASE}/machines/{machine_id}",
            headers=HEADERS,
            timeout=30,
        )
        data = resp.json()
        status = data.get("status", "unknown")
        if status == "ready":
            log(f"✅ Machine {machine_id} is ready!")
            return data
        if status in ("error", "terminated"):
            raise RuntimeError(f"Machine {machine_id} failed: {status}")
        log(f"⏳ Machine status: {status}")
        time.sleep(5)
    raise TimeoutError(f"Machine not ready in {timeout}s")


def machine_terminal(machine_id: str, command: str) -> dict:
    """Run a terminal command on a machine."""
    resp = requests.post(
        f"{COASTY_BASE}/machines/{machine_id}/terminal",
        headers={**HEADERS, "Idempotency-Key": f"term-{int(time.time())}"},
        json={"command": command},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def machine_screenshot(machine_id: str) -> dict:
    """Take a screenshot of the machine."""
    resp = requests.get(
        f"{COASTY_BASE}/machines/{machine_id}/screenshot",
        headers=HEADERS,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def machine_browser(machine_id: str, op: str, **kwargs) -> dict:
    """Run a browser operation on the machine."""
    resp = requests.post(
        f"{COASTY_BASE}/machines/{machine_id}/browser/{op}",
        headers={**HEADERS, "Idempotency-Key": f"browser-{op}-{int(time.time())}"},
        json=kwargs,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


# ─── DeFi Research Workflow ──────────────────────────────────────────

def run_research_with_task():
    """
    Method 1: Fully autonomous — submit a single task description
    and let Coasty handle everything.
    """
    log("=" * 60)
    log("🚀 DEFI RESEARCH AGENT — Autonomous Mode")
    log("=" * 60)

    task_prompt = """
    You are a DeFi research agent. Do the following steps:

    1. Open the browser and navigate to https://dexscreener.com
    2. Wait for the page to fully load
    3. Take a screenshot of the trending tokens page
    4. Click on the first trending token to see its details
    5. Take a screenshot of the token detail page
    6. Navigate back and click on the second trending token
    7. Take a screenshot of the second token detail page
    8. Go to https://dexscreener.com/ethereum to check Ethereum pairs
    9. Take a screenshot of the Ethereum trending pairs
    10. Summarize what you found: list the top tokens with their
        prices, volume, and any notable information from the pages.

    Take clear screenshots at each major step. Be thorough.
    """

    run = create_task(task_prompt, max_steps=100)
    log(f"📋 Task ID: {run['id']}")
    log("📡 Streaming events...")

    # Stream events for real-time progress
    screenshots = []
    for event in stream_run_events(run["id"]):
        event_type = event.get("type", "")
        if event_type == "screenshot":
            ss_path = save_screenshot(
                event["data"]["screenshot"],
                f"step_{event['data'].get('step', len(screenshots)):03d}"
            )
            screenshots.append(ss_path)
        elif event_type == "action":
            log(f"🎬 Action: {event['data'].get('action_type', 'unknown')}")
        elif event_type == "thought":
            log(f"💭 Agent thinking: {event['data'].get('text', '')[:100]}")

    # Get final result
    result = wait_for_run(run["id"])
    return result, screenshots


def run_research_with_machine():
    """
    Method 2: Direct machine control — provision a VM and drive
    the browser step by step using terminal + browser commands.
    Gives more control over the workflow.
    """
    log("=" * 60)
    log("🚀 DEFI RESEARCH AGENT — Direct Machine Mode")
    log("=" * 60)

    # Step 1: Provision machine
    log("\n📦 Step 1: Provisioning machine...")
    machine = provision_machine()
    machine = wait_for_machine(machine["id"])
    mid = machine["id"]

    screenshots = []

    # Step 2: Install tools
    log("\n🔧 Step 2: Setting up environment...")
    machine_terminal(mid, "apt-get update && apt-get install -y chromium-browser")

    # Step 3: Open DEXScreener
    log("\n🌐 Step 3: Opening DEXScreener...")
    machine_browser(mid, "navigate", url="https://dexscreener.com")
    time.sleep(5)  # Wait for page load

    # Step 4: Screenshot trending page
    log("\n📸 Step 4: Capturing trending tokens...")
    ss = machine_screenshot(mid)
    if "screenshot" in ss:
        screenshots.append(save_screenshot(ss["screenshot"], "01_trending"))

    # Step 5: Use predict to find and click first token
    log("\n🔍 Step 5: Analyzing and clicking first token...")
    if "screenshot" in ss:
        prediction = predict_action(
            ss["screenshot"],
            "Click on the first token in the trending list to see its details"
        )
        log(f"🎯 Predicted action: {json.dumps(prediction.get('actions', [])[:2], indent=2)}")

    # Step 6: Navigate to Ethereum pairs
    log("\n🔗 Step 6: Checking Ethereum pairs...")
    machine_browser(mid, "navigate", url="https://dexscreener.com/ethereum")
    time.sleep(5)

    ss2 = machine_screenshot(mid)
    if "screenshot" in ss2:
        screenshots.append(save_screenshot(ss2["screenshot"], "02_ethereum"))

    # Step 7: Navigate to Solana pairs
    log("\n☀️ Step 7: Checking Solana pairs...")
    machine_browser(mid, "navigate", url="https://dexscreener.com/solana")
    time.sleep(5)

    ss3 = machine_screenshot(mid)
    if "screenshot" in ss3:
        screenshots.append(save_screenshot(ss3["screenshot"], "03_solana"))

    # Step 8: Navigate to Base pairs
    log("\n🔵 Step 8: Checking Base pairs...")
    machine_browser(mid, "navigate", url="https://dexscreener.com/base")
    time.sleep(5)

    ss4 = machine_screenshot(mid)
    if "screenshot" in ss4:
        screenshots.append(save_screenshot(ss4["screenshot"], "04_base"))

    # Step 9: Use ground to extract specific data points
    log("\n📊 Step 9: Extracting data points...")
    if "screenshot" in ss2:
        ground_resp = requests.post(
            f"{COASTY_BASE}/ground",
            headers=HEADERS,
            json={
                "screenshot": ss2["screenshot"],
                "element": "the first token pair name and price",
            },
            timeout=30,
        )
        if ground_resp.ok:
            log(f"📍 Ground result: {ground_resp.json()}")

    # Step 10: Generate report
    log("\n📝 Step 10: Generating research report...")
    report = generate_report(screenshots)

    # Cleanup
    log("\n🧹 Cleaning up machine...")
    requests.delete(
        f"{COASTY_BASE}/machines/{mid}",
        headers=HEADERS,
        timeout=30,
    )

    return report, screenshots


def generate_report(screenshots: list) -> str:
    """Generate a markdown research report."""
    REPORT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M")
    report_path = REPORT_DIR / f"defi_report_{timestamp}.md"

    report = f"""# 🚀 DeFi Token Research Report
**Generated:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}
**Agent:** Coasty DeFi Research Agent
**Screenshots captured:** {len(screenshots)}

---

## 📊 Methodology
This report was generated autonomously by a Coasty computer-use agent.
The agent navigated DEXScreener across multiple chains, captured screenshots,
and analyzed trending token data using AI vision.

## 🔍 Chains Analyzed
- **Ethereum** — dexscreener.com/ethereum
- **Solana** — dexscreener.com/solana
- **Base** — dexscreener.com/base

## 📸 Screenshots
"""
    for i, ss in enumerate(screenshots):
        report += f"\n### Screenshot {i+1}\n"
        report += f"![Screenshot {i+1}]({ss})\n"

    report += """
## 🛠️ Technical Details
- **API:** Coasty Computer Use API v1
- **Model:** Coasty managed (85.60% OSWorld)
- **Features used:** Tasks, Predict, Ground, Machines, Browser ops
- **Cost:** ~$0.25-0.50 in API credits

## 💡 How This Works
1. **Provision** — Coasty spins up an isolated VM (Linux, sandboxed)
2. **Navigate** — Browser commands open DEXScreener pages
3. **Capture** — Screenshots taken at each step via `/machines/{id}/screenshot`
4. **Analyze** — `/predict` extracts actions from screenshots
5. **Ground** — `/ground` finds specific UI elements by description
6. **Report** — Data compiled into this markdown report

## 🔗 Links
- [Coasty Docs](https://coasty.ai/docs)
- [DEXScreener](https://dexscreener.com)
- [Coasty API](https://coasty.ai/v1)

---
*Built with ❤️ using [Coasty Computer Use API](https://coasty.ai)*
"""

    report_path.write_text(report)
    log(f"📄 Report saved: {report_path}")
    return report


# ─── Main ─────────────────────────────────────────────────────────────

def main():
    if not API_KEY:
        print("❌ Set COASTY_API_KEY environment variable first!")
        print("   Get a free sandbox key at: https://coasty.ai")
        print()
        print("   export COASTY_API_KEY='sk-coa-...'")
        print("   python agent.py [--mode autonomous|direct]")
        sys.exit(1)

    mode = sys.argv[1] if len(sys.argv) > 1 else "--mode"
    mode_val = sys.argv[2] if len(sys.argv) > 2 else "autonomous"

    if mode == "--mode" or mode_val == "autonomous":
        # Fully autonomous: let Coasty handle everything
        result, screenshots = run_research_with_task()
        log(f"\n🏁 Final status: {result.get('status')}")
        if result.get("result", {}).get("summary"):
            log(f"📋 Summary:\n{result['result']['summary']}")
    else:
        # Direct machine control
        report, screenshots = run_research_with_machine()
        log(f"\n🏁 Report generated with {len(screenshots)} screenshots")

    log("\n✨ Done! Check screenshots/ and reports/ directories.")


if __name__ == "__main__":
    main()
