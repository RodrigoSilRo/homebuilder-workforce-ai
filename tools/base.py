"""Shared logging utility for all tool functions."""
import json
from datetime import datetime
from database.db import execute


def log_tool_call(
    tool_name: str,
    input_data: dict,
    output_data,
    latency_ms: int,
    success: bool,
    error: str = None,
    agent_name: str = "system",
    run_id: int = None,
):
    try:
        execute("""
            INSERT INTO tool_calls
              (agent_run_id, agent_name, tool_name, input_json, output_json,
               latency_ms, success, error_message, created_at)
            VALUES (:run_id,:agent,:tool,:inp,:out,:lat,:suc,:err,:ts)
        """, {
            "run_id": run_id,
            "agent": agent_name,
            "tool": tool_name,
            "inp": json.dumps(input_data, default=str),
            "out": json.dumps(output_data, default=str) if output_data is not None else None,
            "lat": latency_ms,
            "suc": 1 if success else 0,
            "err": error,
            "ts": datetime.now().isoformat(),
        })
    except Exception:
        pass  # logging must never crash a tool call
