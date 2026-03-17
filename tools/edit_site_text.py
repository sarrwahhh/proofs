from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from site_manager import (
    default_site_content,
    load_site_content,
    pages_url,
    publish_changes,
    save_site_content,
)


def padded_strings(values: list[str], count: int) -> list[str]:
    cleaned = list(values[:count])
    while len(cleaned) < count:
        cleaned.append("")
    return cleaned


def padded_terms(values: list[dict], count: int) -> list[dict]:
    cleaned = [dict(item) for item in values[:count]]
    while len(cleaned) < count:
        cleaned.append({"label": "", "value": ""})
    return cleaned


class SiteTextEditorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Site Text Editor")
        self.root.geometry("980x860")
        self.root.minsize(940, 780)
        self.root.configure(bg="#111214")

        self.status_var = tk.StringVar(value="Current site text loaded. Edit any field and confirm to publish.")
        self.confirm_button: ttk.Button | None = None
        self.reload_button: ttk.Button | None = None

        self.short_fields: dict[str, tk.StringVar] = {}
        self.long_fields: dict[str, ScrolledText] = {}
        self.list_fields: dict[str, list[tk.StringVar]] = {}
        self.term_fields: list[tuple[tk.StringVar, tk.StringVar]] = []

        self.content = {}
        self.load_current_content()
        self.build_ui()

    def load_current_content(self) -> None:
        defaults = default_site_content()
        current = load_site_content()

        self.content = {
            "hero": {
                "pill": current.get("hero", {}).get("pill", defaults["hero"]["pill"]),
                "title": current.get("hero", {}).get("title", defaults["hero"]["title"]),
                "subtitle": current.get("hero", {}).get("subtitle", defaults["hero"]["subtitle"]),
            },
            "stats": {
                "count_label": current.get("stats", {}).get("count_label", defaults["stats"]["count_label"]),
                "updated_label": current.get("stats", {}).get("updated_label", defaults["stats"]["updated_label"]),
                "layout_value": current.get("stats", {}).get("layout_value", defaults["stats"]["layout_value"]),
                "layout_label": current.get("stats", {}).get("layout_label", defaults["stats"]["layout_label"]),
            },
            "gallery": {
                "kicker": current.get("gallery", {}).get("kicker", defaults["gallery"]["kicker"]),
                "title": current.get("gallery", {}).get("title", defaults["gallery"]["title"]),
                "note": current.get("gallery", {}).get("note", defaults["gallery"]["note"]),
                "empty_title": current.get("gallery", {}).get("empty_title", defaults["gallery"]["empty_title"]),
                "empty_body": current.get("gallery", {}).get("empty_body", defaults["gallery"]["empty_body"]),
            },
            "overview": {
                "pill": current.get("overview", {}).get("pill", defaults["overview"]["pill"]),
                "title": current.get("overview", {}).get("title", defaults["overview"]["title"]),
                "note": current.get("overview", {}).get("note", defaults["overview"]["note"]),
            },
            "details": {
                "benefits": {
                    "title": current.get("details", {}).get("benefits", {}).get("title", defaults["details"]["benefits"]["title"]),
                    "items": padded_strings(
                        current.get("details", {}).get("benefits", {}).get("items", defaults["details"]["benefits"]["items"]),
                        4,
                    ),
                },
                "privacy": {
                    "title": current.get("details", {}).get("privacy", {}).get("title", defaults["details"]["privacy"]["title"]),
                    "items": padded_strings(
                        current.get("details", {}).get("privacy", {}).get("items", defaults["details"]["privacy"]["items"]),
                        4,
                    ),
                },
                "terms": {
                    "title": current.get("details", {}).get("terms", {}).get("title", defaults["details"]["terms"]["title"]),
                    "items": padded_terms(
                        current.get("details", {}).get("terms", {}).get("items", defaults["details"]["terms"]["items"]),
                        4,
                    ),
                },
            },
        }

    def build_ui(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Root.TFrame", background="#111214")
        style.configure("Card.TFrame", background="#17181b")
        style.configure("Title.TLabel", background="#17181b", foreground="#f6f2eb")
        style.configure("Body.TLabel", background="#17181b", foreground="#a29d95")
        style.configure("Status.TLabel", background="#111214", foreground="#d9c8b5")
        style.configure("Accent.TButton", padding=(18, 11))

        shell = ttk.Frame(self.root, padding=20, style="Root.TFrame")
        shell.pack(fill="both", expand=True)
        shell.columnconfigure(0, weight=1)
        shell.rowconfigure(1, weight=1)

        header = ttk.Frame(shell, padding=20, style="Card.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))

        ttk.Label(
            header,
            text="Edit Site Text",
            font=("Segoe UI Semibold", 18),
            style="Title.TLabel",
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            header,
            text="Everything currently shown on the site is loaded here. Edit the fields you want, then confirm to push the new text live right away.",
            wraplength=860,
            style="Body.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(8, 0))

        notebook = ttk.Notebook(shell)
        notebook.grid(row=1, column=0, sticky="nsew")

        self.build_hero_tab(notebook)
        self.build_gallery_tab(notebook)
        self.build_overview_tab(notebook)
        self.build_benefits_tab(notebook)
        self.build_privacy_tab(notebook)
        self.build_terms_tab(notebook)

        footer = ttk.Frame(shell, style="Root.TFrame")
        footer.grid(row=2, column=0, sticky="ew", pady=(16, 0))
        footer.columnconfigure(0, weight=1)

        ttk.Label(
            footer,
            textvariable=self.status_var,
            wraplength=640,
            style="Status.TLabel",
        ).grid(row=0, column=0, sticky="w")

        button_row = ttk.Frame(footer, style="Root.TFrame")
        button_row.grid(row=0, column=1, sticky="e")

        self.reload_button = ttk.Button(button_row, text="Reload current text", command=self.reload_form)
        self.reload_button.grid(row=0, column=0, padx=(0, 10))

        self.confirm_button = ttk.Button(
            button_row,
            text="Confirm and send to site",
            command=self.submit,
            style="Accent.TButton",
        )
        self.confirm_button.grid(row=0, column=1)

    def build_hero_tab(self, notebook: ttk.Notebook) -> None:
        frame = self.create_tab_frame(notebook, "Hero")
        self.add_entry(frame, "hero.pill", "Top pill", self.content["hero"]["pill"], 0)
        self.add_entry(frame, "hero.title", "Main title", self.content["hero"]["title"], 1)
        self.add_text(frame, "hero.subtitle", "Subtitle", self.content["hero"]["subtitle"], 2, height=5)
        self.add_entry(frame, "stats.count_label", "Proof count label", self.content["stats"]["count_label"], 3)
        self.add_entry(frame, "stats.updated_label", "Last update label", self.content["stats"]["updated_label"], 4)
        self.add_text(frame, "stats.layout_value", "Layout text", self.content["stats"]["layout_value"], 5, height=4)
        self.add_entry(frame, "stats.layout_label", "Layout label", self.content["stats"]["layout_label"], 6)

    def build_gallery_tab(self, notebook: ttk.Notebook) -> None:
        frame = self.create_tab_frame(notebook, "Gallery")
        self.add_entry(frame, "gallery.kicker", "Gallery kicker", self.content["gallery"]["kicker"], 0)
        self.add_entry(frame, "gallery.title", "Gallery title", self.content["gallery"]["title"], 1)
        self.add_text(frame, "gallery.note", "Gallery note", self.content["gallery"]["note"], 2, height=5)
        self.add_entry(frame, "gallery.empty_title", "Empty gallery title", self.content["gallery"]["empty_title"], 3)
        self.add_text(frame, "gallery.empty_body", "Empty gallery body", self.content["gallery"]["empty_body"], 4, height=4)

    def build_overview_tab(self, notebook: ttk.Notebook) -> None:
        frame = self.create_tab_frame(notebook, "Overview")
        self.add_entry(frame, "overview.pill", "Overview pill", self.content["overview"]["pill"], 0)
        self.add_entry(frame, "overview.title", "Overview title", self.content["overview"]["title"], 1)
        self.add_text(frame, "overview.note", "Overview note", self.content["overview"]["note"], 2, height=5)

    def build_benefits_tab(self, notebook: ttk.Notebook) -> None:
        frame = self.create_tab_frame(notebook, "Benefits")
        self.add_entry(
            frame,
            "details.benefits.title",
            "Benefits section title",
            self.content["details"]["benefits"]["title"],
            0,
        )
        self.add_list_fields(frame, "details.benefits.items", "Benefit line", self.content["details"]["benefits"]["items"], start_row=1)

    def build_privacy_tab(self, notebook: ttk.Notebook) -> None:
        frame = self.create_tab_frame(notebook, "Privacy")
        self.add_entry(
            frame,
            "details.privacy.title",
            "Privacy section title",
            self.content["details"]["privacy"]["title"],
            0,
        )
        self.add_list_fields(frame, "details.privacy.items", "Privacy line", self.content["details"]["privacy"]["items"], start_row=1)

    def build_terms_tab(self, notebook: ttk.Notebook) -> None:
        frame = self.create_tab_frame(notebook, "Terms")
        self.add_entry(
            frame,
            "details.terms.title",
            "Terms section title",
            self.content["details"]["terms"]["title"],
            0,
        )

        ttk.Label(
            frame,
            text="Each term card has a label and a value.",
            style="Body.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 12))

        for index, item in enumerate(self.content["details"]["terms"]["items"], start=2):
            label_var = tk.StringVar(value=item.get("label", ""))
            value_var = tk.StringVar(value=item.get("value", ""))

            ttk.Label(frame, text=f"Card {index - 1} label", style="Body.TLabel").grid(
                row=index * 2 - 2, column=0, sticky="w", pady=(8, 4)
            )
            ttk.Entry(frame, textvariable=label_var).grid(row=index * 2 - 2, column=1, sticky="ew", pady=(8, 4))

            ttk.Label(frame, text=f"Card {index - 1} value", style="Body.TLabel").grid(
                row=index * 2 - 1, column=0, sticky="w", pady=(0, 4)
            )
            ttk.Entry(frame, textvariable=value_var).grid(row=index * 2 - 1, column=1, sticky="ew", pady=(0, 4))

            self.term_fields.append((label_var, value_var))

    def create_tab_frame(self, notebook: ttk.Notebook, title: str) -> ttk.Frame:
        frame = ttk.Frame(notebook, padding=18, style="Card.TFrame")
        frame.columnconfigure(1, weight=1)
        notebook.add(frame, text=title)
        return frame

    def add_entry(self, parent: ttk.Frame, key: str, label: str, value: str, row: int) -> None:
        variable = tk.StringVar(value=value)
        self.short_fields[key] = variable

        ttk.Label(parent, text=label, style="Body.TLabel").grid(row=row, column=0, sticky="w", pady=(8, 4))
        ttk.Entry(parent, textvariable=variable).grid(row=row, column=1, sticky="ew", pady=(8, 4))

    def add_text(
        self,
        parent: ttk.Frame,
        key: str,
        label: str,
        value: str,
        row: int,
        *,
        height: int,
    ) -> None:
        ttk.Label(parent, text=label, style="Body.TLabel").grid(row=row, column=0, sticky="nw", pady=(8, 4))
        widget = ScrolledText(parent, height=height, wrap="word")
        widget.insert("1.0", value)
        widget.grid(row=row, column=1, sticky="ew", pady=(8, 4))
        self.long_fields[key] = widget

    def add_list_fields(
        self,
        parent: ttk.Frame,
        key: str,
        label_prefix: str,
        values: list[str],
        *,
        start_row: int,
    ) -> None:
        variables = []
        for offset, value in enumerate(values):
            row = start_row + offset
            variable = tk.StringVar(value=value)
            ttk.Label(parent, text=f"{label_prefix} {offset + 1}", style="Body.TLabel").grid(
                row=row, column=0, sticky="w", pady=(8, 4)
            )
            ttk.Entry(parent, textvariable=variable).grid(row=row, column=1, sticky="ew", pady=(8, 4))
            variables.append(variable)
        self.list_fields[key] = variables

    def read_text_widget(self, key: str) -> str:
        return self.long_fields[key].get("1.0", "end").strip()

    def collect_payload(self) -> dict:
        return {
            "hero": {
                "pill": self.short_fields["hero.pill"].get().strip(),
                "title": self.short_fields["hero.title"].get().strip(),
                "subtitle": self.read_text_widget("hero.subtitle"),
            },
            "stats": {
                "count_label": self.short_fields["stats.count_label"].get().strip(),
                "updated_label": self.short_fields["stats.updated_label"].get().strip(),
                "layout_value": self.read_text_widget("stats.layout_value"),
                "layout_label": self.short_fields["stats.layout_label"].get().strip(),
            },
            "gallery": {
                "kicker": self.short_fields["gallery.kicker"].get().strip(),
                "title": self.short_fields["gallery.title"].get().strip(),
                "note": self.read_text_widget("gallery.note"),
                "empty_title": self.short_fields["gallery.empty_title"].get().strip(),
                "empty_body": self.read_text_widget("gallery.empty_body"),
            },
            "overview": {
                "pill": self.short_fields["overview.pill"].get().strip(),
                "title": self.short_fields["overview.title"].get().strip(),
                "note": self.read_text_widget("overview.note"),
            },
            "details": {
                "benefits": {
                    "title": self.short_fields["details.benefits.title"].get().strip(),
                    "items": [field.get().strip() for field in self.list_fields["details.benefits.items"]],
                },
                "privacy": {
                    "title": self.short_fields["details.privacy.title"].get().strip(),
                    "items": [field.get().strip() for field in self.list_fields["details.privacy.items"]],
                },
                "terms": {
                    "title": self.short_fields["details.terms.title"].get().strip(),
                    "items": [
                        {"label": label_var.get().strip(), "value": value_var.get().strip()}
                        for label_var, value_var in self.term_fields
                    ],
                },
            },
        }

    def set_busy(self, busy: bool) -> None:
        state = "disabled" if busy else "normal"
        if self.confirm_button is not None:
            self.confirm_button.configure(state=state)
        if self.reload_button is not None:
            self.reload_button.configure(state=state)
        self.root.configure(cursor="watch" if busy else "")
        self.root.update_idletasks()

    def reload_form(self) -> None:
        if not messagebox.askyesno("Reload current text", "Discard your unsaved edits and reload the current saved text?"):
            return

        self.root.destroy()
        new_root = tk.Tk()
        SiteTextEditorApp(new_root)
        new_root.mainloop()

    def submit(self) -> None:
        payload = self.collect_payload()
        self.set_busy(True)
        self.status_var.set("Saving text and publishing the update...")

        try:
            save_site_content(payload)
            branch = publish_changes("Update site text")
        except Exception as error:
            self.status_var.set("Update failed. Please try again.")
            messagebox.showerror("Publish failed", str(error))
            self.set_busy(False)
            return

        self.set_busy(False)
        url = pages_url()
        self.status_var.set("Text updated and sent to the site.")

        message = f"Updated the site text and pushed it to {branch}."
        if url:
            message += f"\n\nWebsite: {url}\n\nGitHub Pages usually refreshes within a minute or two."

        messagebox.showinfo("Site updated", message)


def main() -> int:
    root = tk.Tk()
    SiteTextEditorApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
