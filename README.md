# lets-debug-helper

[![CI](https://github.com/jediknight112/lets-debug-helper/actions/workflows/main.yml/badge.svg)](https://github.com/jediknight112/lets-debug-helper/actions/workflows/main.yml)
[![Coverage Status](https://coveralls.io/repos/github/jediknight112/lets-debug-helper/badge.svg?branch=main)](https://coveralls.io/github/jediknight112/lets-debug-helper?branch=main)
[![PyPI](https://img.shields.io/pypi/v/lets-debug-helper.svg)](https://pypi.org/project/lets-debug-helper/)
[![Python](https://img.shields.io/pypi/pyversions/lets-debug-helper.svg)](https://pypi.org/project/lets-debug-helper/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A small command-line wrapper around the [Let's Debug](https://letsdebug.net/) public API. Hand it a domain name and it submits a diagnostic test, polls until the result is ready, and prints any problems found in a readable, color-coded format. Useful when you're trying to figure out why Let's Encrypt won't issue a certificate for a domain you control.

## Install

```bash
pip install lets-debug-helper
```

Requires Python 3.13+.

## Usage

```bash
lets-debug example.com
```

Wildcards are supported:

```bash
lets-debug "*.example.com"
```

For full options:

```bash
lets-debug --help
```

## Example output

When the domain has issues:

```
Checking Domain: example.com
     Testing ID: 2916375
            URL: https://letsdebug.net/example.com/2916375

Waiting for test to complete....

Warning Type: IssueFromLetsEncrypt
 Explanation: A test authorization for example.com to the Let's Encrypt staging
              service has revealed issues that may prevent any certificate for
              this domain being issued.
     Details: Error creating new order :: Cannot issue for "example.com": ...
    Severity: Error
```

When everything checks out:

```
Checking Domain: yourdomain.com
     Testing ID: 2916380
            URL: https://letsdebug.net/yourdomain.com/2916380

Waiting for test to complete....

All OK!

No issues were found with yourdomain.com. If you are having problems with
creating an SSL certificate, please visit the Let's Encrypt Community forums
and post a question there.
https://community.letsencrypt.org/
```

## What it checks

The Let's Debug service runs a battery of pre-flight checks that frequently catch the real reasons certificate issuance fails. A non-exhaustive list:

- DNS resolution and authoritative-NS sanity
- CAA records that disallow Let's Encrypt
- Public-suffix-list / domain blocklist hits
- HTTP-01 reachability (port 80 open, no redirect loops, correct content type)
- TXT record state for DNS-01 (when applicable)
- Cloudflare / CDN-fronted SSL configuration warnings
- IPv4/IPv6 reachability mismatches
- Rate-limit-state hints from Let's Encrypt's staging environment

For the full list and underlying logic, see the [Let's Debug source](https://github.com/letsdebug/letsdebug).

## Exit codes

| Code | Meaning |
|------|---------|
| `0`  | Test completed successfully (regardless of whether problems were reported) |
| `1`  | API error, JSON decode error, or test did not complete within 60 seconds |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for dev setup, the make targets, and the release process.

## License

[MIT](LICENSE).

## Acknowledgements

This tool is just a thin client. All the diagnostic work is done by the [Let's Debug](https://letsdebug.net/) project — please consider supporting them.
