#!/usr/bin/env python3
"""CLI entry point for lets-debug-helper.

Wraps the Let's Debug API (https://letsdebug.net/) by submitting a domain,
polling for the test result, and rendering any reported problems with
rich color formatting.
"""
import argparse
import json
import sys
from time import sleep
from typing import Any, Dict, List

import requests
from rich.console import Console

from letsdebughelper.helpers import ValidateArgRegex

console = Console(highlight=False)
LE_API_URL = 'https://letsdebug.net'
HTTP_TIMEOUT_SECS = 10
# Real Let's Debug tests typically finish in <5s. Cap polling at 60s so a
# stuck test or API outage surfaces as an error instead of a silent hang.
MAX_POLL_ATTEMPTS = 60


def parse_args() -> argparse.Namespace:
    """Parse the single positional `domain` argument."""
    parser = argparse.ArgumentParser(description="Diagnose Let's Encrypt issuance issues for a domain")
    parser.add_argument('domain', type=ValidateArgRegex('domain'), nargs=1)
    args: argparse.Namespace = parser.parse_args()
    args.domain = args.domain[0]
    return args


def le_get_call(check_url: str) -> requests.Response:
    """GET a Let's Debug test result by URL."""
    headers = {'accept': 'application/json'}
    return requests.get(check_url, headers=headers, timeout=HTTP_TIMEOUT_SECS)


def le_post_call(post_data: Dict[str, str]) -> requests.Response:
    """POST a new Let's Debug test request."""
    headers = {'content-type': 'application/json'}
    return requests.post(LE_API_URL, data=json.dumps(post_data), headers=headers, timeout=HTTP_TIMEOUT_SECS)


def check_status(result: requests.Response, result_json: Dict[str, Any]) -> None:
    """Exit non-zero if the HTTP response wasn't 200."""
    if result.status_code != 200:
        console.print(f"[bold red]ERROR:[/] not a 200 result. instead got: {result.status_code}.")
        console.print(json.dumps(result_json, indent=2))
        sys.exit(1)


def decode_result(result: requests.Response) -> Dict[str, Any]:
    """Decode an HTTP response body as JSON, exiting non-zero on failure."""
    try:
        return result.json()  # type: ignore[no-any-return]
    except Exception as e:
        console.log("Couldn't decode the response as JSON:", e)
        sys.exit(1)


def check_debug_test_status(test_id_url: str) -> Dict[str, Any]:
    """Poll the Let's Debug test URL until status == 'Complete' or the cap is hit."""
    console.print("\n[bold blue]Waiting for test to complete....[/]")
    for _ in range(MAX_POLL_ATTEMPTS):
        check_result: requests.Response = le_get_call(check_url=test_id_url)
        check_result_json: Dict[str, Any] = decode_result(result=check_result)
        check_status(result=check_result, result_json=check_result_json)
        if check_result_json.get("status") == 'Complete':
            return check_result_json
        sleep(1)
    console.print(f"[bold red]ERROR:[/] test did not complete within {MAX_POLL_ATTEMPTS}s.")
    sys.exit(1)


def pre_result_output(domain: str, test_id: str, test_id_url: str) -> None:
    """Print the test metadata header before polling for results."""
    console.print(f"\n[bold green]Checking Domain:[/] {domain}")
    console.print(f"[bold green]     Testing ID:[/] {test_id}")
    console.print(f"[bold green]            URL:[/] {test_id_url}")


def format_problem_output(problems: List[Dict[str, Any]], domain: str) -> None:
    """Render each problem from the test result, or an all-clear message."""
    if problems:
        for problem in problems:
            console.print(f"\n[bold yellow]Warning Type:[/] {problem.get('name')}")
            console.print(f"[bold yellow] Explanation:[/] {problem.get('explanation')}")
            console.print(f"     [bold yellow]Details:[/] {problem.get('detail')}")
            console.print(f"    [bold yellow]Severity:[/] {problem.get('severity')}")
        console.print()
    else:
        console.print("\n[bold green]All OK![/]")
        console.print(
            f"\nNo issues were found with {domain}. If you are having problems with creating an\n"
            "SSL certificate, please visit the Let's Encrypt Community forums and post a question there.\n"
            "https://community.letsencrypt.org/\n")


def main() -> None:
    """CLI entry: submit the domain, poll for results, render problems."""
    args: argparse.Namespace = parse_args()
    post_data: Dict[str, str] = {"method": "http-01", "domain": args.domain}
    result: requests.Response = le_post_call(post_data)
    result_json: Dict[str, Any] = decode_result(result)
    check_status(result=result, result_json=result_json)
    test_id_url = f"{LE_API_URL}/{result_json.get('Domain')}/{result_json.get('ID')}"
    pre_result_output(domain=result_json.get('Domain', ""), test_id=result_json.get('ID', ""), test_id_url=test_id_url)
    check_result_dict: Dict[str, Any] = check_debug_test_status(test_id_url)
    problems: List[Dict[str, Any]] = (check_result_dict.get('result') or {}).get('problems') or []
    format_problem_output(problems=problems, domain=args.domain)


if __name__ == '__main__':
    main()
