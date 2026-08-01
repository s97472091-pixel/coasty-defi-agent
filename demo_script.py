#!/usr/bin/env python3
"""
🎬 Coasty DeFi Agent — Video Demo Script
Generates a terminal recording script for asciinema or similar tools.
"""

DEMO_SCRIPT = """
# Coasty DeFi Research Agent — Live Demo
# Run this with: asciinema rec demo.cast -c "python demo_script.py"

import time
import sys

def type_text(text, delay=0.03):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def pause(seconds=1):
    time.sleep(seconds)

# Title
print()
print("  ╔══════════════════════════════════════════════════════╗")
print("  ║  🚀 Coasty DeFi Research Agent — Live Demo          ║")
print("  ║  Autonomous computer-use for DeFi token research     ║")
print("  ╚══════════════════════════════════════════════════════╝")
print()
pause(2)

# Step 1
print("  📦 Step 1: Setting up...")
pause(0.5)
type_text("  $ export COASTY_API_KEY='sk-coa-...'")
pause(0.3)
type_text("  $ pip install requests")
pause(1)
print("  ✅ Ready!")
print()
pause(1)

# Step 2
print("  🚀 Step 2: Launching autonomous research agent...")
pause(0.5)
type_text("  $ python agent.py --mode autonomous")
pause(1)
print()
print("  ┌─ Coasty API ─────────────────────────────────────┐")
print("  │ POST /v1/tasks                                    │")
print("  │ → Provisioning sandboxed VM...                    │")
pause(1)
print("  │ → VM ready (Linux + Chromium)                     │")
pause(0.5)
print("  │ → Opening DEXScreener...                          │")
pause(1.5)
print("  │ 📸 Screenshot: trending_tokens.png                │")
pause(0.5)
print("  │ → Analyzing with AI vision (85.60% OSWorld)...    │")
pause(1)
print("  │ → Clicking top token...                           │")
pause(1)
print("  │ 📸 Screenshot: token_details.png                  │")
pause(0.5)
print("  │ → Navigating to /ethereum...                      │")
pause(1.5)
print("  │ 📸 Screenshot: ethereum_pairs.png                 │")
pause(0.5)
print("  │ → Navigating to /solana...                        │")
pause(1.5)
print("  │ 📸 Screenshot: solana_pairs.png                   │")
pause(0.5)
print("  │ → Navigating to /base...                          │")
pause(1.5)
print("  │ 📸 Screenshot: base_pairs.png                     │")
pause(0.5)
print("  │ → Generating research report...                   │")
pause(1)
print("  └───────────────────────────────────────────────────┘")
print()
pause(0.5)

# Result
print("  ✅ Research complete!")
print()
print("  📊 Results:")
print("  ├── screenshots/trending_tokens.png")
print("  ├── screenshots/token_details.png")
print("  ├── screenshots/ethereum_pairs.png")
print("  ├── screenshots/solana_pairs.png")
print("  ├── screenshots/base_pairs.png")
print("  └── reports/defi_report_2026-08-02.md")
print()
pause(1)

# Stats
print("  ┌─ Stats ──────────────────────────┐")
print("  │ ⏱️  Duration:    2m 34s            │")
print("  │ 📸 Screenshots: 5                 │")
print("  │ 🔗 Chains:      3 (ETH/SOL/BASE) │")
print("  │ 💰 Cost:        ~$0.35            │")
print("  │ 🤖 VM:          Linux sandboxed   │")
print("  └───────────────────────────────────┘")
print()
pause(1)

print("  Built with Coasty — #1 Computer Use API")
print("  🔗 coasty.ai/docs | @coastyai")
print()
"""

if __name__ == "__main__":
    exec(DEMO_SCRIPT)
