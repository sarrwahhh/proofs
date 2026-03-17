from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
except ImportError:  # pragma: no cover - tkinter ships with most Windows Python installs
    tk = None
    filedialog = None
    messagebox = None
    ttk = None

from site_manager import add_proof_item, pages_url, publish_changes


IMAGE_FILE_TYPES = [
    ("Image files", "*.png *.jpg *.jpeg *.webp *.gif *.bmp *.svg"),
    ("All files", "*.*"),
]


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


def default_title_from_paths(*paths: str) -> str:
    for raw_path in paths:
        if not raw_path:
            continue
        stem = Path(raw_path).stem.replace("-", " ").replace("_", " ").strip()
        if stem:
            return stem.title()
    return "Untitled proof"


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
    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Use terminal prompts instead of opening the desktop window.",
    )
    return parser


def wants_gui(args: argparse.Namespace) -> bool:
    if args.no_gui:
        return False

    return not any(
        [
            args.proof,
            args.payment,
            args.title,
            args.customer,
            args.note,
            args.date,
            args.publish,
            args.message,
        ]
    )


def submit_proof_set(
    *,
    proof: str,
    payment: str,
    title: str,
    customer: str = "",
    note: str = "",
    date: str = "",
    publish: bool = False,
    message: str = "",
) -> tuple[dict, str | None]:
    final_title = title.strip() or default_title_from_paths(proof, payment)

    item = add_proof_item(
        proof_source=proof,
        payment_source=payment,
        title=final_title,
        customer=customer,
        note=note,
        date=date,
    )

    published_branch = None
    if publish:
        commit_message = message or f"Add proof set: {item['title']}"
        published_branch = publish_changes(message=commit_message)

    return item, published_branch


class ProofUploaderApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Proof Uploader")
        self.root.geometry("720x420")
        self.root.minsize(700, 400)
        self.root.configure(bg="#f5efe4")

        self.proof_path = tk.StringVar()
        self.payment_path = tk.StringVar()
        self.title_var = tk.StringVar()
        self.publish_now = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(
            value="Choose the proof image and payment image, then click confirm."
        )

        self._build_ui()

    def _build_ui(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Main.TFrame", background="#f5efe4")
        style.configure("Card.TFrame", background="#fff9f1")
        style.configure("Heading.TLabel", background="#fff9f1", foreground="#23170f")
        style.configure("Body.TLabel", background="#fff9f1", foreground="#6f5e4b")
        style.configure("Status.TLabel", background="#f5efe4", foreground="#8c3513")
        style.configure("Accent.TButton", padding=(18, 12))

        shell = ttk.Frame(self.root, padding=24, style="Main.TFrame")
        shell.pack(fill="both", expand=True)
        shell.columnconfigure(0, weight=1)
        shell.rowconfigure(0, weight=1)

        card = ttk.Frame(shell, padding=24, style="Card.TFrame")
        card.grid(row=0, column=0, sticky="nsew")
        card.columnconfigure(1, weight=1)

        ttk.Label(
            card,
            text="Proof uploader",
            font=("Segoe UI Semibold", 18),
            style="Heading.TLabel",
        ).grid(row=0, column=0, columnspan=3, sticky="w")

        ttk.Label(
            card,
            text="Pick one proof photo and one payment photo, then confirm to send them to the website.",
            wraplength=620,
            style="Body.TLabel",
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(6, 22))

        self._build_file_row(
            parent=card,
            row=2,
            label="Proof image",
            variable=self.proof_path,
            command=self.choose_proof,
            button_text="Choose proof",
        )
        self._build_file_row(
            parent=card,
            row=3,
            label="Payment image",
            variable=self.payment_path,
            command=self.choose_payment,
            button_text="Choose payment",
        )

        ttk.Label(
            card,
            text="Title (optional)",
            font=("Segoe UI", 10, "bold"),
            style="Heading.TLabel",
        ).grid(row=4, column=0, sticky="w", pady=(18, 8))
        ttk.Entry(card, textvariable=self.title_var).grid(
            row=4, column=1, columnspan=2, sticky="ew", pady=(18, 8)
        )

        ttk.Label(
            card,
            text="Leave the title blank if you want it to use the file name automatically.",
            wraplength=620,
            style="Body.TLabel",
        ).grid(row=5, column=0, columnspan=3, sticky="w", pady=(0, 14))

        ttk.Checkbutton(
            card,
            text="Send to website now",
            variable=self.publish_now,
        ).grid(row=6, column=0, columnspan=2, sticky="w")

        actions = ttk.Frame(card, style="Card.TFrame")
        actions.grid(row=7, column=0, columnspan=3, sticky="ew", pady=(22, 0))
        actions.columnconfigure(0, weight=1)

        ttk.Label(
            actions,
            textvariable=self.status_var,
            wraplength=460,
            style="Status.TLabel",
        ).grid(row=0, column=0, sticky="w")

        self.confirm_button = ttk.Button(
            actions,
            text="Confirm and upload",
            command=self.submit,
            style="Accent.TButton",
        )
        self.confirm_button.grid(row=0, column=1, sticky="e", padx=(16, 0))

    def _build_file_row(
        self,
        *,
        parent: ttk.Frame,
        row: int,
        label: str,
        variable: tk.StringVar,
        command,
        button_text: str,
    ) -> None:
        ttk.Label(
            parent,
            text=label,
            font=("Segoe UI", 10, "bold"),
            style="Heading.TLabel",
        ).grid(row=row, column=0, sticky="w", pady=8)

        entry = ttk.Entry(parent, textvariable=variable, state="readonly")
        entry.grid(row=row, column=1, sticky="ew", pady=8, padx=(14, 12))

        ttk.Button(parent, text=button_text, command=command).grid(
            row=row, column=2, sticky="e", pady=8
        )

    def choose_proof(self) -> None:
        self._choose_file(self.proof_path)
        if not self.title_var.get().strip():
            self.title_var.set(default_title_from_paths(self.proof_path.get()))

    def choose_payment(self) -> None:
        self._choose_file(self.payment_path)
        if not self.title_var.get().strip():
            self.title_var.set(
                default_title_from_paths(self.proof_path.get(), self.payment_path.get())
            )

    def _choose_file(self, variable: tk.StringVar) -> None:
        path = filedialog.askopenfilename(
            parent=self.root,
            title="Choose an image",
            filetypes=IMAGE_FILE_TYPES,
        )
        if path:
            variable.set(path)

    def set_busy(self, busy: bool) -> None:
        self.confirm_button.configure(state="disabled" if busy else "normal")
        self.root.configure(cursor="watch" if busy else "")
        self.root.update_idletasks()

    def submit(self) -> None:
        proof = self.proof_path.get().strip()
        payment = self.payment_path.get().strip()
        title = self.title_var.get().strip()

        if not proof:
            messagebox.showwarning("Missing proof image", "Choose the proof image first.")
            return

        if not payment:
            messagebox.showwarning("Missing payment image", "Choose the payment image first.")
            return

        self.set_busy(True)
        self.status_var.set("Uploading files and updating the gallery...")

        try:
            item, branch = submit_proof_set(
                proof=proof,
                payment=payment,
                title=title,
                publish=self.publish_now.get(),
            )
        except Exception as error:
            self.status_var.set("Upload failed. Please try again.")
            messagebox.showerror("Upload failed", str(error))
            self.set_busy(False)
            return

        self.set_busy(False)
        self.proof_path.set("")
        self.payment_path.set("")
        self.title_var.set("")

        url = pages_url()
        if branch and url:
            self.status_var.set("Uploaded and sent to the website.")
            messagebox.showinfo(
                "Upload complete",
                f"Added '{item['title']}' and pushed it to {branch}.\n\nWebsite: {url}\n\nGitHub Pages usually refreshes within a minute or two.",
            )
        elif branch:
            self.status_var.set("Uploaded and pushed to GitHub.")
            messagebox.showinfo(
                "Upload complete",
                f"Added '{item['title']}' and pushed it to {branch}.",
            )
        else:
            self.status_var.set("Saved locally. Publish later when you're ready.")
            messagebox.showinfo(
                "Saved locally",
                f"Added '{item['title']}'.\n\nRun python tools/publish.py when you want to send it to the website.",
            )


def launch_gui() -> int:
    if tk is None or ttk is None or filedialog is None or messagebox is None:
        print("Tkinter is not available in this Python install, so the desktop window cannot open.")
        return 1

    try:
        root = tk.Tk()
    except tk.TclError as error:
        print(f"Could not open the desktop window: {error}")
        return 1

    app = ProofUploaderApp(root)
    root.mainloop()
    return 0


def run_cli(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    stdin_is_tty = sys.stdin.isatty()

    missing_required = [
        name
        for name, value in {
            "--proof": args.proof,
            "--payment": args.payment,
        }.items()
        if not value
    ]

    if missing_required and not stdin_is_tty:
        parser.error(
            f"{', '.join(missing_required)} must be provided when running without interactive prompts."
        )

    proof = args.proof or prompt_for_value("Proof image path: ", required=True)
    payment = args.payment or prompt_for_value("Payment image path: ", required=True)
    title = args.title or prompt_for_value("Title (optional): ")
    customer = args.customer or prompt_for_value("Customer name (optional): ")
    note = args.note or prompt_for_value("Note (optional): ")
    date = args.date or prompt_for_value("Date to show (optional): ")

    try:
        item, branch = submit_proof_set(
            proof=proof,
            payment=payment,
            title=title,
            customer=customer,
            note=note,
            date=date,
            publish=args.publish,
            message=args.message,
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
            try:
                branch = publish_changes(message=args.message or f"Add proof set: {item['title']}")
            except Exception as error:
                print(f"Proof set was added locally, but publishing failed: {error}")
                return 1

    if should_publish:
        print(f"Published branch: {branch}")
        url = pages_url()
        if url:
            print(f"Pages URL: {url}")
            print("GitHub Pages usually refreshes within a minute or two after the push.")

    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if wants_gui(args):
        return launch_gui()

    return run_cli(args, parser)


if __name__ == "__main__":
    raise SystemExit(main())
