"""CLI runner for GAME_AGENTS with live terminal monitoring."""

import argparse
from pathlib import Path
from game_agents.workflows.feature_development import FeatureDevelopmentWorkflow


def _make_monitor(agent_label: str):
    def _on_event(ev: str, payload: dict) -> None:
        if ev == "agent_start":
            print(
                f"  [{agent_label}] START ({payload.get('provider')}:{payload.get('model')}) -> {payload.get('task')}",
                flush=True,
            )
        elif ev == "tool_call":
            args = ", ".join(f"{k}={repr(v)[:35]}" for k, v in (payload.get("args") or {}).items())
            print(f"  [{agent_label}] TOOL  > {payload.get('tool')}({args})", flush=True)
        elif ev == "tool_result":
            ok = "OK" if payload.get("success") else "ERR"
            out = str(payload.get("output", "")).splitlines()[0][:80] if payload.get("output") else ""
            print(f"  [{agent_label}] RESULT [{ok}] {out}", flush=True)
        elif ev == "agent_finish":
            print(
                f"  [{agent_label}] DONE (created={payload.get('files_created')}, modified={payload.get('files_modified')})",
                flush=True,
            )

    return _on_event


def main() -> None:
    parser = argparse.ArgumentParser(description="Run GAME_AGENTS multi-agent workflow from the terminal.")
    parser.add_argument("prompt", help="Game development prompt (e.g. 'Create a Phaser 3 chess game using Vite + TypeScript')")
    parser.add_argument("--path", default="./workspace/generated_game", help="Target game project directory")
    parser.add_argument("--approval", action="store_true", help="Pause for human approval after PlannerAgent")
    parser.add_argument("--retries", type=int, default=2, help="Max Debugger -> Developer retry attempts")
    args = parser.parse_args()

    target_dir = Path(args.path).resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    def _cli_approval(plan_text: str) -> bool:
        print("\n=== PLANNER APPROVAL GATE ===\n", plan_text, "\n=============================")
        return input("Approve plan and start DeveloperAgent? (y/n): ").strip().lower() in ("y", "yes")

    wf = FeatureDevelopmentWorkflow(approval_callback=_cli_approval if args.approval else None)
    for label, ag in [
        ("Supervisor", wf.supervisor),
        ("ProjectAnalyzer", wf.project_analyzer),
        ("Planner", wf.planner),
        ("Developer", wf.developer),
        ("CodeReviewer", wf.code_reviewer),
        ("QAAgent", wf.qa_agent),
        ("Debugger", wf.debugger),
    ]:
        ag.on_event = _make_monitor(label)

    print(f"=== STARTING WORKFLOW IN: {target_dir} ===", flush=True)
    result = wf.run(
        feature_description=args.prompt,
        project_path=str(target_dir),
        require_approval=args.approval,
        max_debug_attempts=args.retries,
    )
    print("\n" + result.summary)
    print("Files Created:", result.files_created)
    print("Files Modified:", result.files_modified)


if __name__ == "__main__":
    main()
