#!/usr/bin/env python3
"""
CFO Agent — Command Line Interface

Usage:
    python run.py --task monthly-report
    python run.py --task full-suite --period 2025-02
    python run.py --task board-memo --local        (skip Drive, use local folder)
    python run.py --setup-drive                    (create Drive folders once)
    python run.py --cost                           (show OpenAI spend)
    python run.py --check                          (check environment)
"""

import argparse
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agent.orchestrator import run_agent
from agent.llm_caller import get_total_spend
from agent.drive_connector import check_gws_installed, setup_drive_folders


def main():
    parser = argparse.ArgumentParser(
        description="Fractional CFO Agent — AI-powered financial reporting"
    )
    parser.add_argument("--task",
        choices=["monthly-report","budget-variance","cashflow-forecast","board-memo","full-suite"])
    parser.add_argument("--period", default=None, help="YYYY-MM (default: current month)")
    parser.add_argument("--source", default="drop-files-here")
    parser.add_argument("--local",  action="store_true", help="Skip Drive, use local folder")
    parser.add_argument("--drive",  action="store_true", help="Force Drive mode")
    parser.add_argument("--setup-drive", action="store_true", help="Create Drive folders (run once)")
    parser.add_argument("--cost",   action="store_true", help="Show OpenAI spend")
    parser.add_argument("--check",  action="store_true", help="Check environment")
    args = parser.parse_args()

    if args.check:
        print("\n🔍 Environment Check")
        print("=" * 40)
        print(f"  OpenAI API key:  {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Missing'}")
        print(f"  gws CLI:         {'✅ Installed' if check_gws_installed() else '❌ Not found'}")
        print(f"  NOTIFY_EMAIL:    {os.getenv('NOTIFY_EMAIL','(not set)')}")
        print("=" * 40 + "\n")
        return

    if args.setup_drive:
        if not check_gws_installed():
            print("\n❌ Install gws first: npm install -g @googleworkspace/cli && gws auth setup")
            sys.exit(1)
        setup_drive_folders()
        return

    if args.cost:
        spend = get_total_spend()
        print(f"\n💰 Spent: ${spend['total_usd']:.4f}  |  Remaining: ${spend['remaining_from_20']:.4f}  |  Calls: {spend['calls']}\n")
        return

    if not args.task:
        parser.print_help()
        return

    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ Add OPENAI_API_KEY=sk-... to your .env file\n")
        sys.exit(1)

    use_drive = None
    if args.local: use_drive = False
    elif args.drive: use_drive = True

    run_agent(task=args.task, source_dir=args.source,
              period=args.period, use_drive=use_drive)


if __name__ == "__main__":
    main()
