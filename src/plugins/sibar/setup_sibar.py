#!/usr/bin/env python3
"""
Sibar plugin setup helper (MANUAL workflow step automation).

Usage (recommended, via manage.py shell):
  python src/manage.py shell < src/plugins/sibar/setup_sibar.py -- <JOURNAL_CODE_OR_ID> [--api-url https://sibar.ilmovas.com]

Examples:
  python src/manage.py shell < src/plugins/sibar/setup_sibar.py -- ABC
  python src/manage.py shell < src/plugins/sibar/setup_sibar.py -- 12 --api-url https://sibar.example.edu

What this script does:
- Ensures the workflow element with stage/name `sibar_plugin` exists for the target journal.
- Inserts it at order 0 by shifting existing elements' order values.
- Optionally sets the `sibar_api_url` setting (does NOT set any API key).

Notes:
- Idempotent: if `sibar_plugin` is already present, it will not add a duplicate.
- Secrets: do NOT pass/store the Sibar API key here. Set `sibar_api_key` via the Manager UI.
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional, Tuple, Union


STAGE = "sibar_plugin"
DEFAULT_API_URL = "https://sibar.ilmovas.com"


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="setup_sibar.py",
        description="Add sibar_plugin workflow element to a journal (idempotent).",
    )
    parser.add_argument(
        "journal",
        help="Journal code (e.g. ABC) or journal pk/id (e.g. 12).",
    )
    parser.add_argument(
        "--api-url",
        default=None,
        help=f"Optional: set sibar_api_url (default: {DEFAULT_API_URL}).",
    )
    return parser.parse_args(argv)


def _resolve_journal(journal_arg: str):
    from journal.models import Journal

    # Prefer numeric pk if the arg is digits only.
    if journal_arg.isdigit():
        return Journal.objects.get(pk=int(journal_arg))
    return Journal.objects.get(code=journal_arg)


def _ensure_workflow_element(journal) -> Tuple[bool, object]:
    """
    Returns (created, element).
    """
    from core.models import Workflow, WorkflowElement

    workflow = Workflow.objects.get(journal=journal)

    # If already exists on this journal, keep as-is.
    existing = workflow.elements.filter(stage=STAGE).first()
    if existing:
        return False, existing

    # Shift existing elements so sibar becomes order 0.
    # Janeway orders elements by (order, element_name).
    for el in workflow.elements.all():
        el.order = (el.order or 0) + 1
        el.save(update_fields=["order"])

    element = WorkflowElement.objects.create(
        journal=journal,
        element_name=STAGE,
        stage=STAGE,
        handshake_url="sibar_articles",
        jump_url="sibar_article",
        article_url=True,
        order=0,
    )
    workflow.elements.add(element)
    return True, element


def _set_api_url(journal, api_url: str) -> bool:
    """
    Returns True if the value was updated/created, False if left unchanged.
    """
    from core.models import Setting, SettingGroup

    group, _ = SettingGroup.objects.get_or_create(name="plugin:sibar")
    setting, _ = Setting.objects.get_or_create(
        group=group,
        name="sibar_api_url",
        defaults={
            "types": "text",
            "pretty_name": "Sibar API Base URL",
            "description": "Base URL for the Sibar duplication and integrity API.",
            "is_translatable": False,
        },
    )

    # Values are journal-scoped in Janeway via SettingValue (core.models).
    from core.models import SettingValue

    current = (
        SettingValue.objects.filter(setting=setting, journal=journal).first()
    )
    if current and (current.value == api_url):
        return False

    if current:
        current.value = api_url
        current.save(update_fields=["value"])
    else:
        SettingValue.objects.create(setting=setting, journal=journal, value=api_url)
    return True


def main(argv: Optional[list[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    # manage.py shell may pass a leading "--" depending on how it was invoked; ignore it.
    if argv and argv[0] == "--":
        argv = argv[1:]

    args = _parse_args(argv)

    journal = _resolve_journal(args.journal)

    created, element = _ensure_workflow_element(journal)
    if created:
        print(f"OK: added workflow element '{STAGE}' for journal {journal} (order=0).")
    else:
        print(f"OK: workflow element '{STAGE}' already present for journal {journal}.")

    if args.api_url is not None:
        api_url = args.api_url.strip() or DEFAULT_API_URL
        changed = _set_api_url(journal, api_url)
        if changed:
            print(f"OK: set sibar_api_url to: {api_url}")
        else:
            print(f"OK: sibar_api_url already set to: {api_url}")
    else:
        print(
            f"NOTE: sibar_api_url not changed (default is {DEFAULT_API_URL})."
        )

    print(
        "NEXT: Set 'sibar_api_key' for this journal in the Manager UI (Settings group: plugin:sibar)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
