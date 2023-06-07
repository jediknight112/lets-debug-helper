#!/bin/bash
# shellcheck disable=SC2046
set -ex

DEBUG_HELPER_VERSION=$(grep -Eo '^version = "(.+)"' pyproject.toml | awk -F\" '{print $2}')

gh repo set-default git@github.com:jediknight112/lets-debug-helper.git

gh release create v"${DEBUG_HELPER_VERSION}" --generate-notes

gh release upload v"${DEBUG_HELPER_VERSION}" ./dist/*