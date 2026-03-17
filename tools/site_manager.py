from __future__ import annotations

import json
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = REPO_ROOT / "data" / "proofs.json"
SITE_CONTENT_FILE = REPO_ROOT / "data" / "site_content.json"
UPLOADS_DIR = REPO_ROOT / "assets" / "uploads"


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    return cleaned.strip("-") or "proof-set"


def ensure_structure() -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def load_data() -> dict:
    ensure_structure()

    if not DATA_FILE.exists():
        return {"updated_at": None, "items": []}

    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def save_data(payload: dict) -> None:
    ensure_structure()
    payload["updated_at"] = now_iso()
    content = json.dumps(payload, indent=2) + "\n"
    DATA_FILE.write_text(content, encoding="utf-8")


def default_site_content() -> dict:
    return {
        "hero": {
            "pill": "Verified showcase",
            "title": "Proofs, key details, and terms in one polished view.",
            "subtitle": "Review the proof and payment gallery first, then scroll into a clean placeholder section built for highlights, privacy notes, and terms you can swap later.",
        },
        "stats": {
            "count_label": "proof sets",
            "updated_label": "last update",
            "layout_value": "Proof + payment stay paired together for fast review.",
            "layout_label": "layout",
        },
        "gallery": {
            "kicker": "Verified gallery",
            "title": "Proof board",
            "note": "Every card keeps the full proof and payment visible so the gallery stays clean, readable, and easy to scan on desktop or mobile.",
            "empty_title": "No proof sets yet",
            "empty_body": "Your proof and payment pairs will appear here after the first upload.",
        },
        "overview": {
            "pill": "Overview preview",
            "title": "Placeholder sections you can replace later",
            "note": "This area is set up to preview extra copy under the gallery. The wording below stays neutral on purpose so you can swap in your final version whenever you are ready.",
        },
        "details": {
            "benefits": {
                "title": "Exclusive Benefits",
                "items": [
                    "Placeholder line for the main premium feature or standout offer.",
                    "Placeholder line for higher limits, expanded access, or added value.",
                    "Placeholder line for creative tools, extras, or advanced options.",
                    "Placeholder line for additional perks you want to highlight clearly.",
                ],
            },
            "privacy": {
                "title": "Privacy & Security",
                "items": [
                    "Placeholder line for privacy expectations or personal-use wording.",
                    "Placeholder line for secure setup, support, or access notes.",
                    "Placeholder line for reliability, consistency, or account stability.",
                    "Placeholder line for anything important people should know up front.",
                ],
            },
            "terms": {
                "title": "Pricing & Terms",
                "items": [
                    {"label": "Duration", "value": "Placeholder duration text"},
                    {"label": "Price", "value": "Placeholder price here"},
                    {"label": "Fees", "value": "Placeholder one-time payment note"},
                    {"label": "Payment", "value": "Placeholder payment methods here"},
                ],
            },
        },
    }


def load_site_content() -> dict:
    ensure_structure()

    if not SITE_CONTENT_FILE.exists():
        payload = default_site_content()
        save_site_content(payload)
        return payload

    return json.loads(SITE_CONTENT_FILE.read_text(encoding="utf-8"))


def save_site_content(payload: dict) -> None:
    ensure_structure()
    content = json.dumps(payload, indent=2) + "\n"
    SITE_CONTENT_FILE.write_text(content, encoding="utf-8")


def resolve_image(source: str) -> Path:
    path = Path(source).expanduser()

    if not path.is_absolute():
        path = Path.cwd() / path

    path = path.resolve()

    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Image not found: {path}")

    return path


def unique_destination(stem: str, label: str, suffix: str) -> Path:
    candidate = UPLOADS_DIR / f"{stem}-{label}{suffix}"
    counter = 2

    while candidate.exists():
        candidate = UPLOADS_DIR / f"{stem}-{label}-{counter}{suffix}"
        counter += 1

    return candidate


def copy_image(source: str, stem: str, label: str) -> str:
    ensure_structure()
    source_path = resolve_image(source)
    suffix = source_path.suffix.lower() or ".png"
    destination = unique_destination(stem, label, suffix)
    shutil.copy2(source_path, destination)
    return destination.relative_to(REPO_ROOT).as_posix()


def add_proof_item(
    proof_source: str,
    payment_source: str,
    title: str,
    customer: str = "",
    note: str = "",
    date: str = "",
) -> dict:
    payload = load_data()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    stem = f"{timestamp}-{slugify(title or customer or 'proof-set')}"

    item = {
        "id": stem,
        "title": title or "Untitled proof",
        "customer": customer.strip(),
        "date": date.strip(),
        "note": note.strip(),
        "proof_image": copy_image(proof_source, stem, "proof"),
        "payment_image": copy_image(payment_source, stem, "payment"),
        "added_at": now_iso(),
    }

    payload.setdefault("items", [])
    payload["items"].insert(0, item)
    save_data(payload)
    return item


def run_git(args: list[str], capture_output: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=capture_output,
        text=True,
    )


def current_branch() -> str:
    return run_git(["symbolic-ref", "--quiet", "--short", "HEAD"], capture_output=True).stdout.strip()


def has_upstream() -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def status_has_changes() -> bool:
    return bool(run_git(["status", "--porcelain"], capture_output=True).stdout.strip())


def publish_changes(message: str, branch: str | None = None) -> str:
    active_branch = branch or current_branch()

    if status_has_changes():
        run_git(["add", "-A"])
        run_git(["commit", "-m", message])

    if has_upstream():
        run_git(["push"])
    else:
        run_git(["push", "-u", "origin", active_branch])

    return active_branch


def pages_url() -> str | None:
    try:
        remote = run_git(["remote", "get-url", "origin"], capture_output=True).stdout.strip()
    except subprocess.CalledProcessError:
        return None

    match = re.search(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+)", remote)
    if not match:
        return None

    owner = match.group("owner")
    repo = match.group("repo")
    return f"https://{owner}.github.io/{repo}/"
