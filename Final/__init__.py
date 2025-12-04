from .cli import build_parser
from .storage import Store
from typing import List, Optional
import sys


def inc(n: int) -> int:
    return n + 1


def main(argv: Optional[List[str]] = None) -> int:
    try:
        parser = build_parser()
        args = parser.parse_args(argv)
        store = Store()
        # args.fn is set by subparser set_defaults
        args.fn(args, store)
        return 0
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
