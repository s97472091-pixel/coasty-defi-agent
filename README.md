# 🚀 Coasty DeFi Research Agent

**Autonomous computer-use agent that researches trending DeFi tokens using the [Coasty Computer Use API](https://coasty.ai/docs).**

Built for the Coasty Build Challenge — $500 prize submission 🏆

## What It Does

This agent spins up a real VM via Coasty's API and autonomously:

1. 🌐 Opens DEXScreener in a sandboxed browser
2. 📸 Captures screenshots at every step
3. 🔍 Analyzes trending tokens using AI vision (`/predict`)
4. 📍 Extracts specific data points (`/ground`)
5. 📊 Researches multiple chains (Ethereum, Solana, Base)
6. 📝 Generates a markdown research report with embedded screenshots

## Two Modes

| Mode | Command | What Happens |
|------|---------|-------------|
| **Autonomous** | `python agent.py --mode autonomous` | Submit one goal → Coasty handles everything |
| **Direct** | `python agent.py --mode direct` | Provision VM, drive browser step-by-step |

## Quick Start

```bash
# 1. Get a free API key at https://coasty.ai (sandbox keys are free forever)
export COASTY_API_KEY="sk-coa-your-key-here"

# 2. Install deps
pip install requests

# 3. Run the agent
python agent.py --mode autonomous
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│              DeFi Research Agent                │
│         (Python + Coasty REST API)              │
└───────────────┬─────────────────────────────────┘
                │
    ┌───────────▼───────────┐
    │   Coasty API v1       │
    │   coasty.ai/v1        │
    └───────────┬───────────┘
                │
    ┌───────────▼───────────┐
    │   Managed Sandbox VM  │
    │   (Linux + Chromium)  │
    │   ┌───────────────┐   │
    │   │   Browser      │   │
    │   │   DEXScreener  │   │
    │   └───────────────┘   │
    └───────────────────────┘
```

## API Endpoints Used

| Endpoint | Purpose | Cost |
|----------|---------|------|
| `POST /v1/tasks` | Submit autonomous research task | 5 cr/step |
| `POST /v1/predict` | Analyze screenshot → actions | $0.05/call |
| `POST /v1/ground` | Find UI element coordinates | $0.03/call |
| `POST /v1/machines` | Provision sandboxed VM | $0.05/hr |
| `POST /v1/machines/{id}/browser/navigate` | Navigate browser | Free |
| `GET /v1/machines/{id}/screenshot` | Capture screen | Free |
| `POST /v1/machines/{id}/terminal` | Run commands | Free |
| `GET /v1/runs/{id}/events` | Stream real-time progress | Free |

## Cost Estimate

- **Autonomous mode:** ~$0.25-0.50 per full research run
- **Direct mode:** ~$0.15-0.30 (more efficient, fewer LLM calls)
- **Sandbox keys:** Free forever, zero cost for testing

## Output

```
screenshots/
  ├── 01_trending.png
  ├── 02_ethereum.png
  ├── 03_solana.png
  └── 04_base.png
reports/
  └── defi_report_2026-08-02_12-00.md
```

## Why This Is Cool

🤖 **True autonomy** — describe what you want in plain English, the agent does it
🖥️ **Real VMs** — not headless Chrome tricks, actual sandboxed desktops
📸 **Visual verification** — screenshots at every step, AI sees what a human would
🔗 **Multi-chain** — researches Ethereum, Solana, and Base in one run
📊 **Structured output** — clean markdown reports with embedded screenshots
⚡ **Real-time streaming** — watch the agent work via SSE events

## Tech Stack

- **Coasty Computer Use API** — #1 computer-use agent (85.60% OSWorld)
- **Python 3.10+** — simple, no framework bloat
- **DEXScreener** — real-time DeFi token data
- **Coasty Managed VMs** — Linux + Chromium sandboxed environments

## Links

- 🌐 [Coasty Docs](https://coasty.ai/docs)
- 🔑 [Get API Key](https://coasty.ai)
- 📊 [DEXScreener](https://dexscreener.com)
- 🐦 [@coastyai on X](https://x.com/coastyai)

---

*Built with ❤️ for the Coasty Build Challenge*

@coastyai #ComputerUse #DeFi #AI
