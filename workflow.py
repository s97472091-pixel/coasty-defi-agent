#!/usr/bin/env python3
"""
🎬 Coasty DeFi Agent — Workflow DSL Version
Uses Coasty's Workflow API for versioned, repeatable multi-step automation.
"""

import os
import json
import requests
import time

COASTY_BASE = "https://coasty.ai/v1"
API_KEY = os.environ.get("COASTY_API_KEY", "")
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}


def create_workflow():
    """Create a reusable DeFi research workflow."""
    workflow_definition = {
        "name": "defi-token-research",
        "description": "Autonomous DeFi token research across multiple chains",
        "version": "1.0.0",
        "steps": [
            {
                "id": "open_dexscreener",
                "type": "task",
                "instruction": "Navigate to https://dexscreener.com and wait for it to fully load. Take a screenshot.",
                "max_steps": 10,
                "on_success": "analyze_trending",
            },
            {
                "id": "analyze_trending",
                "type": "task",
                "instruction": "Look at the DEXScreener trending page. Click on the first token listed to see its details. Take a screenshot of the token details page. Then go back.",
                "max_steps": 20,
                "on_success": "check_ethereum",
            },
            {
                "id": "check_ethereum",
                "type": "task",
                "instruction": "Navigate to https://dexscreener.com/ethereum. Wait for the page to load. Take a screenshot. Note the top 3 token pairs by volume.",
                "max_steps": 15,
                "on_success": "check_solana",
            },
            {
                "id": "check_solana",
                "type": "task",
                "instruction": "Navigate to https://dexscreener.com/solana. Wait for the page to load. Take a screenshot. Note the top 3 token pairs by volume.",
                "max_steps": 15,
                "on_success": "check_base",
            },
            {
                "id": "check_base",
                "type": "task",
                "instruction": "Navigate to https://dexscreener.com/base. Wait for the page to load. Take a screenshot. Note the top 3 token pairs by volume.",
                "max_steps": 15,
                "on_success": "generate_summary",
            },
            {
                "id": "generate_summary",
                "type": "task",
                "instruction": "Based on all the pages you've visited, write a brief research summary. Include: top trending tokens, notable price movements, and any interesting patterns across Ethereum, Solana, and Base chains. Format as a clean summary.",
                "max_steps": 10,
            },
        ],
    }

    resp = requests.post(
        f"{COASTY_BASE}/workflows",
        headers={**HEADERS, "Idempotency-Key": f"defi-workflow-{int(time.time())}"},
        json=workflow_definition,
        timeout=30,
    )
    resp.raise_for_status()
    workflow = resp.json()
    print(f"✅ Workflow created: {workflow['id']}")
    return workflow


def run_workflow(workflow_id: str):
    """Execute the DeFi research workflow."""
    resp = requests.post(
        f"{COASTY_BASE}/workflows/{workflow_id}/runs",
        headers={**HEADERS, "Idempotency-Key": f"defi-run-{int(time.time())}"},
        json={},
        timeout=30,
    )
    resp.raise_for_status()
    run = resp.json()
    print(f"🚀 Workflow run started: {run['id']}")

    # Poll for completion
    while True:
        status_resp = requests.get(
            f"{COASTY_BASE}/workflows/runs/{run['id']}",
            headers=HEADERS,
            timeout=30,
        )
        status_data = status_resp.json()
        status = status_data.get("status", "unknown")

        if status in ("succeeded", "failed", "cancelled"):
            print(f"🏁 Workflow finished: {status}")
            return status_data

        current_step = status_data.get("current_step", "?")
        total_steps = status_data.get("total_steps", "?")
        print(f"⏳ Step {current_step}/{total_steps} — status: {status}")
        time.sleep(10)


def main():
    if not API_KEY:
        print("❌ Set COASTY_API_KEY first!")
        print("   export COASTY_API_KEY='sk-coa-...'")
        return

    print("=" * 60)
    print("🚀 Coasty DeFi Research — Workflow Mode")
    print("=" * 60)

    # Create the workflow
    workflow = create_workflow()

    # Run it
    result = run_workflow(workflow["id"])

    # Print summary
    if result.get("result", {}).get("summary"):
        print("\n📊 Research Summary:")
        print(result["result"]["summary"])

    print(f"\n✨ Done! Status: {result.get('status')}")


if __name__ == "__main__":
    main()
