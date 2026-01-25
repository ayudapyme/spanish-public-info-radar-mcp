"""Entry point for Spanish Public Data MCP server.

Usage:
    python -m public_radar              # Run SSE server (default)
    python -m public_radar --stdio      # Run stdio server (for Claude Desktop)
    python -m public_radar --port 8080  # Custom port

Environment variables:
    MCP_HOST: Host to bind to (default: 0.0.0.0)
    MCP_PORT: Port to bind to (default: 8080)
    MCP_LOGS_DIR: Directory for tool call logs (default: ./logs)
"""

import argparse
import asyncio
import sys


def run_serve(args: argparse.Namespace) -> None:
    """Run the MCP server.

    :param args: Parsed command line arguments.
    :type args: argparse.Namespace
    """
    if args.stdio:
        from public_radar.mcp.server import run_server

        print("Starting Spanish Public Data MCP server (stdio)...", file=sys.stderr)
        asyncio.run(run_server())
    else:
        from public_radar.mcp.server import run_sse_server

        print(f"Starting Spanish Public Data MCP server on http://{args.host}:{args.port}", file=sys.stderr)
        asyncio.run(run_sse_server(host=args.host, port=args.port))


def main() -> None:
    """Run the Spanish Public Data MCP CLI."""
    parser = argparse.ArgumentParser(
        description="Spanish Public Data MCP Server - Access BDNS, BOE, INE, and datos.gob.es APIs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--stdio",
        action="store_true",
        help="Use stdio transport (for Claude Desktop integration)",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to bind to (default: 8080)",
    )

    args = parser.parse_args()
    run_serve(args)


if __name__ == "__main__":
    main()
