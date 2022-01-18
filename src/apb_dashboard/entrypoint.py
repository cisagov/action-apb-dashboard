"""GitHub Action to rebuild repositories that haven't be built in a while."""

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


def main() -> None:
    """Parse environment and perform requested actions."""
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
        sys.exit(-1)

    if read_filename is None:
        logging.fatal(
            "Input filename environment variable must be set. (INPUT_READ_FILENAME)"
        )
        sys.exit(-1)

    if write_filename is None:
        logging.fatal(
            "Output filename environment variable must be set. (INPUT_WRITE_FILENAME)"
        )
        sys.exit(-1)

    # Read json data created by apb action
    logging.info("Loading json data from: %s", read_filename)
    with (Path(github_workspace_dir) / Path(read_filename)).open() as f:
        data = json.load(f)

    # Make data mustache-friendly
    flat_repos: list = list()
    for k, v in data["repositories"].items():
        v["repository"] = k
        flat_repos.append(v)
    data["repositories"] = flat_repos

    # Render the internal or external template
    if template_filename:
        logging.info("Loading template file: %s", template_filename)
        with (Path(github_workspace_dir) / Path(template_filename)).open() as f:
            template_data: str = f.read()
            logging.info("Rendering template from external file.")
            rendered = pystache.render(template_data, data)
    else:
        logging.info("Rendering default template.")
        rendered = pystache.render(TEMPLATE, data)

    # Write rendered data out to file
    logging.info("Writing rendered data to: %s", write_filename)
    with (Path(github_workspace_dir) / Path(write_filename)).open("w") as f:
        f.write(rendered)
