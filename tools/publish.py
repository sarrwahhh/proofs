from __future__ import annotations

import argparse

from site_manager import current_branch, pages_url, publish_changes


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Commit and push the proof gallery updates to GitHub."
    )
    parser.add_argument(
        "--message",
        default="Update proof gallery",
        help="Git commit message to use for the publish step.",
    )
    args = parser.parse_args()

    try:
        branch = publish_changes(message=args.message, branch=current_branch())
    except Exception as error:
        print(f"Publish failed: {error}")
        return 1

    print(f"Published branch: {branch}")
    url = pages_url()
    if url:
        print(f"Pages URL: {url}")
        print("GitHub Pages usually refreshes within a minute or two after the push.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
