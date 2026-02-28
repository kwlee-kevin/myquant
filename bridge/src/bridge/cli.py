import argparse
from collections.abc import Sequence
from typing import Optional


def _add_sync_subcommand(subparsers: argparse._SubParsersAction, name: str) -> None:
    sync_parser = subparsers.add_parser(name, help="Sync stock master data to backend")
    sync_parser.add_argument(
        "--dry-run",
        "--no-push",
        dest="dry_run",
        action="store_true",
        help="Fetch and normalize only (skip backend upsert)",
    )
    sync_parser.add_argument("--limit", type=int, default=None, help="Limit normalized items")
    sync_parser.add_argument("--verbose", action="store_true", help="Verbose per-market logs")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m bridge.cli")
    subparsers = parser.add_subparsers(dest="command")
    _add_sync_subcommand(subparsers, "sync")
    _add_sync_subcommand(subparsers, "sync-stocks")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command in {"sync", "sync-stocks"}:
        if args.limit is not None and args.limit < 1:
            print("--limit must be >= 1")
            return 2

        # Import lazily so --help never loads requests/dotenv/Kiwoom modules.
        from .sync import sync_stocks

        return int(sync_stocks(dry_run=args.dry_run, limit=args.limit, verbose=args.verbose))

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
