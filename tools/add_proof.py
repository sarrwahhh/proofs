from __future__ import annotations

import argparse
import sys

from site_manager import add_proof_item, pages_url, publish_changes


def prompt_for_value(prompt: str, required: bool = False) -> str:
    while True:
        try:
            value = input(prompt).strip()
        except EOFError:
            if required:
                raise RuntimeError(f"Missing required value for prompt: {prompt.strip()}")
            return ""
        if value or not required:
            return value
        print("This field is required.")


def prompt_yes_no(prompt: str, default: bool = False) -> bool:
    suffix = " [Y/n]: " if default else " [y/N]: "

    while True:
        try:
            answer = input(prompt + suffix).strip().lower()
        except EOFError:
            return default

        if not answer:
            return default

        if answer in {"y", "yes"}:
            return True

        if answer in {"n", "no"}:
            return False

        print("Please answer y or n.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Add a proof image and payment image pair to the GitHub Pages gallery."
    )
    parser.add_argument("--proof", help="Path to the proof image.")
    parser.add_argument("--payment", help="Path to the payment image.")
    parser.add_argument("--title", help="Card title shown on the site.")
    parser.add_argument("--customer", default="", help="Optional customer name.")
    parser.add_argument("--note", default="", help="Optional note for the card.")
    parser.add_argument("--date", default="", help="Optional date shown on the card.")
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Commit and push the new proof set right after adding it.",
    )
    parser.add_argument(
        "--message",
        default="",
        help="Custom git commit message used when --publish is enabled.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    stdin_is_tty = sys.stdin.isatty()

    missing_required = [
        name
        for name, value in {
            "--proof": args.proof,
            "--payment": args.payment,
            "--title": args.title,
        }.items()
        if not value
    ]

    if missing_required and not stdin_is_tty:
        parser.error(
            f"{', '.join(missing_required)} must be provided when running without interactive prompts."
        )

    proof = args.proof or prompt_for_value("Proof image path: ", required=True)
    payment = args.payment or prompt_for_value("Payment image path: ", required=True)
    title = args.title or prompt_for_value("Title for this proof set: ", required=True)
    customer = args.customer or prompt_for_value("Customer name (optional): ")
    note = args.note or prompt_for_value("Note (optional): ")
    date = args.date or prompt_for_value("Date to show (optional): ")

    try:
        item = add_proof_item(
            proof_source=proof,
            payment_source=payment,
            title=title,
            customer=customer,
            note=note,
            date=date,
        )
    except Exception as error:
        print(f"Could not add proof set: {error}")
        return 1

    print("")
    print("Added proof set:")
    print(f"  Title: {item['title']}")
    print(f"  Proof image: {item['proof_image']}")
    print(f"  Payment image: {item['payment_image']}")

    should_publish = args.publish
    if not should_publish and stdin_is_tty:
        should_publish = prompt_yes_no("Push this update to GitHub now?", default=False)

    if should_publish:
        message = args.message or f"Add proof set: {item['title']}"

        try:
            branch = publish_changes(message=message)
        except Exception as error:
            print(f"Proof set was added locally, but publishing failed: {error}")
            return 1

        print(f"Published branch: {branch}")
        if pages_url():
            print(f"Pages URL: {pages_url()}")
            print("GitHub Pages usually refreshes within a minute or two after the push.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
