"""Run the order history API server."""

import argparse
from pathlib import Path

import uvicorn

from order_history import create_app, init_database

DEFAULT_DB_PATH = Path("orders.db")
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the order history API")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--db-path", type=Path, default=DEFAULT_DB_PATH)
    args = parser.parse_args()

    init_database(args.db_path)
    app = create_app(db_path=args.db_path)
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
