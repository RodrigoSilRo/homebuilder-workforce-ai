"""
HomeBuilder Workforce AI — MCP Server

Exposes all 11 tool functions via the Model Context Protocol using FastMCP.
Compatible with Claude Desktop, Cursor, Windsurf, and any MCP-compatible client.

Usage:
  stdio (Claude Desktop / Cursor):
    python -m mcp_server.server

  HTTP (remote / Streamlit integration):
    python -m mcp_server.server --transport http --port 8000

Claude Desktop config (~/.claude/claude_desktop_config.json):
  {
    "mcpServers": {
      "homebuilder-workforce-ai": {
        "command": "python",
        "args": ["-m", "mcp_server.server"],
        "cwd": "/path/to/homebuilder-workforce-ai"
      }
    }
  }
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from mcp_server.tool_registry import (
    tool_get_community_metrics,
    tool_get_inventory_status,
    tool_get_lead_conversion,
    tool_get_construction_delays,
    tool_calculate_incentive_impact,
    tool_get_vendor_profile,
    tool_get_vendor_risk_score,
    tool_get_policy_workflow,
    tool_create_approval_request,
    tool_generate_marketing_campaign,
    tool_create_executive_report,
)

mcp = FastMCP(
    name="homebuilder-workforce-ai",
    instructions=(
        "You are connected to the HomeBuilder Workforce AI tool layer. "
        "These tools give you real-time access to homebuilding community performance data, "
        "vendor risk assessments, corporate policy workflows, incentive modeling, "
        "marketing campaign generation, and the human-in-the-loop approval system. "
        "All tool calls are logged to an audit trail. "
        "For any action that requires human approval (contracts > $50K, margin impact > 1.0%, "
        "customer-facing campaigns), use create_approval_request to route to the correct approver."
    ),
)

# ── Register all tools (names stripped of tool_ prefix) ───────────────────────

mcp.tool(name="get_community_metrics")(tool_get_community_metrics)
mcp.tool(name="get_inventory_status")(tool_get_inventory_status)
mcp.tool(name="get_lead_conversion")(tool_get_lead_conversion)
mcp.tool(name="get_construction_delays")(tool_get_construction_delays)
mcp.tool(name="calculate_incentive_impact")(tool_calculate_incentive_impact)
mcp.tool(name="get_vendor_profile")(tool_get_vendor_profile)
mcp.tool(name="get_vendor_risk_score")(tool_get_vendor_risk_score)
mcp.tool(name="get_policy_workflow")(tool_get_policy_workflow)
mcp.tool(name="create_approval_request")(tool_create_approval_request)
mcp.tool(name="generate_marketing_campaign")(tool_generate_marketing_campaign)
mcp.tool(name="create_executive_report")(tool_create_executive_report)

# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="HomeBuilder Workforce AI MCP Server")
    parser.add_argument("--transport", choices=["stdio", "http"], default="stdio")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    if args.transport == "http":
        mcp.run(transport="streamable-http", host="0.0.0.0", port=args.port)
    else:
        mcp.run(transport="stdio")
