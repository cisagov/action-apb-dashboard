#!/usr/bin/env python3
"""GitHub Action to rebuild respositories that haven't be built in a while."""

# Standard Python Libraries
import json
import logging
import os
from pathlib import Path
import sys
from typing import Optional

# Third-Party Libraries
import pystache

TEMPLATE = """
# APB Status

## {{ran_at}}

## `{{repository_query}}`

| Repository | Build Status | Build Age | Event Sent |
|------------|--------------|-----------|------------|
{{#repositories}}
| {{repository}} \
| {{#workflow}}[![GitHub Build Status](https://github.com/{{repository}}/workflows/build/badge.svg)](https://github.com/{{repository}}/actions){{/workflow}} \
{{^workflow}}No workflow{{/workflow}} \
| {{run_age}} \
| {{event_sent}} |
{{/repositories}}
"""


def main() -> int:
    """Parse evironment and perform requested actions."""
    # Set up logging
    logging.basicConfig(format="%(levelname)s %(message)s", level="INFO")

    # Get inputs from the environment
    github_workspace_dir: Optional[str] = os.environ.get("GITHUB_WORKSPACE")
    read_filename: Optional[str] = os.environ.get("INPUT_READ_FILENAME", "apb.json")
    write_filename: Optional[str] = os.environ.get("INPUT_WRITE_FILENAME", "apb.md")
    template_filename: Optional[str] = os.environ.get("INPUT_TEMPLATE_FILENAME")

    # sanity checks
    if github_workspace_dir is None:
        logging.fatal(
            "GitHub workspace environment variable must be set. (GITHUB_WORKSPACE)"
        )
        return -1

    if read_filename is None:
        logging.fatal(
            "Input filename environment variable must be set. (INPUT_READ_FILENAME)"
        )
        return -1

    if write_filename is None:
        logging.fatal(
            "Output filename environment variable must be set. (INPUT_WRITE_FILENAME)"
        )
        return -1

    with Path(read_filename).open() as f:
        data = json.load(f)

    # make data mustache-friendly
    flat_repos: list = list()
    for k, v in data["repositories"].items():
        v["repository"] = k
        flat_repos.append(v)
    data["repositories"] = flat_repos

    if template_filename is not None:
        with Path(template_filename).open() as f:
            template_data: str = f.read()
            print(pystache.render(template_data, data))
    else:
        print(pystache.render(TEMPLATE, data))

    return 0


if __name__ == "__main__":
    sys.exit(main())
