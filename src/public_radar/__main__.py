"""Entry point for Spanish Public Data MCP server.
Usage:
    python -m public_radar              # Run SSE server (default)
    python -m public_radar --stdio      # Run stdio server (for Claude Desktop)
    python -m public_radar --streamable # Run Streamable HTTP server (for n8n)
    python -m public_radar --port 8080  # Custom port
Environment variables:
    MCP_HOST: Host to bind to (default: 0.0.0.0)
    MCP_PORT: Port to bind to (default: 8080)
    MCP_LOGS_DIR: Directory for tool call logs (default: ./logs)
    MCP_TRANSPORT: Transport type: 'sse' or 'streamable' (default: sse)
"""
import argparse
import asyncio
import os
import sys


def run_serve(args: argparse.Namespace) -> None:
    """Run the MCP server."""
    transport = os.environ.get("MCP_TRANSPORT", "sse").lower()

    if args.stdio:
        from public_radar.mcp.server import run_server
        print("Starting Spanish Public Data MCP server (stdio)...", file=sys.stderr)
        asyncio.run(run_server())
    elif transport == "streamable":
        import uvicorn
        from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
        from starlette.applications import Starlette
        from starlette.routing import Mount, Route
        from starlette.responses import JSONResponse
        from public_radar.mcp.server import create_server

        host = os.environ.get("MCP_HOST", args.host)
        port = int(os.environ.get("MCP_PORT", args.port))

        print(f"Starting Spanish Public Data MCP server (Streamable HTTP) on http://{host}:{port}/mcp", file=sys.stderr)

        mcp_server = create_server()
        session_manager = StreamableHTTPSessionManager(
            app=mcp_server,
            event_store=None,
            json_response=False,
            stateless=True,
        )

        async def handle_mcp(scope, receive, send):
            await session_manager.handle_request(scope, receive, send)

        async def health(request):
            return JSONResponse({"status": "healthy", "service": "spanish-public-data-mcp"})

        async def lifespan(app):
            async with session_manager.run():
                yield

        app = Starlette(
            lifespan=lifespan,
            routes=[
                Route("/health", health),
                Mount("/mcp", app=handle_mcp),
            ],
        )

        config = uvicorn.Config(app, host=host, port=port, log_level="info")
        server_instance = uvicorn.Server(config)
        asyncio.run(server_instance.serve())
    else:
        from public_radar.mcp.server import run_sse_server
        print(f"Starting Spanish Public Data MCP server (SSE) on http://{args.host}:{args.port}", file=sys.stderr)
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
