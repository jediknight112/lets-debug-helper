#!/usr/bin/env python3
import argparse
import json
import sys
import textwrap
from time import sleep

import requests
from rich.console import Console

from letsdebughelper.helpers import ValidateArgRegex

console = Console(highlight=False)
LE_API_URL = 'https://letsdebug.net'


def parse_args():
    parser = argparse.ArgumentParser(description='Checks the DNS of a domain')
    parser.add_argument('domain', type=ValidateArgRegex('domain'))

    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()
    else:
        return args


def le_get_call(check_url):
    headers = {'accept': 'application/json'}
    return requests.get(check_url, headers=headers)


def le_post_call(post_data):
    headers = {'content-type': 'application/json'}
    return requests.post(LE_API_URL, data=json.dumps(post_data), headers=headers)


def check_status(result, result_json):
    if result.status_code != 200:
        print("ERROR: not a 200 result. instead got: %s." % result.status_code)
        print(json.dumps(result_json, indent=2))
        sys.exit()


def decode_result(result):
    try:
        return result.json()
    except Exception as e:
        print("Couldn't decode the response as JSON:", e)
        sys.exit()


def check_debug_test_status(test_id_url):
    console.print("\n[bold blue]Waiting for test to complete....[/]")
    check_result = le_get_call(test_id_url)
    check_result_dict = decode_result(check_result)
    status = check_result_dict.get('status')
    check_status(check_result, check_result_dict)
    while status != 'Complete':
        check_result = le_get_call(test_id_url)
        check_result_dict = decode_result(check_result)
        status = check_result_dict.get('status')
        check_status(check_result, check_result_dict)
        sleep(1)
    return check_result_dict


def pre_result_output(domain, test_id, test_id_url):
    console.print(f"\n[bold green]Checking Domain:[/] {domain}")
    console.print(f"[bold green]     Testing ID:[/] {test_id}")
    console.print(f"[bold green]            URL:[/] {test_id_url}")


def format_problem_output(problems, domain):
    if problems:
        for problem in problems:
            console.print(f"\n[bold yellow]Warning Type:[/] {problem.get('name')}")
            explanation = textwrap.wrap(f"[bold yellow] Explanation:[/] {problem.get('explanation')}",
                                        width=120,
                                        subsequent_indent="              ")
            for line in explanation:
                console.print(line)
            console.print(f"     [bold yellow]Details:[/] {problem.get('detail')}")
            console.print(f"    [bold yellow]Severity:[/] {problem.get('severity')}")
        print()
    else:
        console.print("\n[bold green]All OK![/]")
        print('\nNo issues were found with {}. If you are having problems with creating an\n\
SSL certificate, please visit the Let\'s Encrypt Community forums and post a question there.\n\
https://community.letsencrypt.org/\n'.format(domain))


def main():
    args = parse_args()
    post_data = {"method": "http-01", "domain": args.domain}
    result = le_post_call(post_data)
    result_json = decode_result(result)
    check_status(result, result_json)
    test_id_url = '{}/{}/{}'.format(LE_API_URL, result_json.get('Domain'), result_json.get('ID'))
    pre_result_output(result_json.get('Domain'), result_json.get('ID'), test_id_url)
    check_result_dict = check_debug_test_status(test_id_url)
    problems = check_result_dict.get('result').get('problems')
    format_problem_output(problems, args.domain)


if __name__ == '__main__':
    main()
