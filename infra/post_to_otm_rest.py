#!/usr/bin/env python3
"""Simple helper to send POST requests to OTM REST.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

import requests
from requests.auth import HTTPBasicAuth


OTM_BASE_URL = "https://otmgtm-dev1-bauducco.otmgtm.us-phoenix-1.ocs.oraclecloud.com"
OTM_API_PREFIX = "/gc3services/v1/rest"  # adjust if needed
OTM_USER = "BAU.TEST_INTEGRATION"
OTM_PASSWORD = "TestIntegracao@2025"
DEFAULT_TIMEOUT = 60
DEFAULT_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


def _parse_payload(path: Path | None, inline: str | None) -> Dict[str, Any]:
    if path:
        return json.loads(path.read_text(encoding="utf-8"))
    if inline:
        return json.loads(inline)
    return {}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="POST payload to an OTM REST resource.")
    parser.add_argument("--resource", required=True, help="REST path after .../transportation/25c/ (without leading slash)")
    parser.add_argument("--payload", help="Path to a JSON file containing the request body")
    parser.add_argument("--inline", help="Inline JSON payload string")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    body = _parse_payload(Path(args.payload) if args.payload else None, args.inline)
    url = f"{OTM_BASE_URL}/transportation/25c/{args.resource}"

    print("POSTing to", url)
    print("Payload", json.dumps(body, ensure_ascii=False))

    if args.dry_run:
        print("Dry run: skipping HTTP call")
        return 0

    auth = HTTPBasicAuth(OTM_USER, OTM_PASSWORD)
    response = requests.post(url, json=body, headers=DEFAULT_HEADERS, auth=auth, timeout=args.timeout)
    response.raise_for_status()
    print("Status", response.status_code)
    print(response.text[:1000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
