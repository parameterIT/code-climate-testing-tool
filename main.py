import os
import sys
import requests
import logging
import time
import csv

from pathlib import Path

ACCESS_TOKEN = os.getenv("CODE_CLIMATE_TOKEN")


def main():
    if ACCESS_TOKEN is None:
        logging.error("CODE_CLIMATE_TOKEN environment variable must be set")
        exit(1)

    if len(sys.argv) < 2:
        logging.error(
            "Usage: main.py <GITHUB_SLUG>, where GITHUB_SLUG is in the format 'username/reponame' on GitHub"
        )
        exit(1)

    github_slug = sys.argv[1]

    results = {}

    for issue in get_issues(github_slug):
        check_name = issue["attributes"]["check_name"]
        category = issue["attributes"]["categories"][0]
        try:
            results[check_name] = results[check_name] + 1
        except KeyError:
            results[check_name] = 1

        try:
            results[category] = results[category] + 1
        except KeyError:
            results[category] = 1

    write_to_csv(results, github_slug)


def get_repo(github_slug: str):
    """
    gets a repo from the github slug. github slug is a "username/reponame" format
    """
    target = f"https://api.codeclimate.com/v1/repos?github_slug={github_slug}"
    headers = {"Authorization": f"Token token={ACCESS_TOKEN}"}

    r = requests.get(target, headers=headers)
    return r.json()


def get_latest_build_snapshot(github_slug: str):
    repo = get_repo(github_slug)
    latest_build_snapshot = repo["data"][0]["relationships"][
        "latest_default_branch_snapshot"
    ]["data"]["id"]
    return latest_build_snapshot


def get_issues(github_slug: str):
    repo_id = get_repo(github_slug)["data"][0]["id"]
    snapshot_id = get_latest_build_snapshot(github_slug)

    target = (
        f"https://api.codeclimate.com/v1/repos/{repo_id}/snapshots/{snapshot_id}/issues"
    )
    headers = {"Authorization": f"Token token={ACCESS_TOKEN}"}

    r = requests.get(target, headers=headers)
    return r.json()["data"]


def write_to_csv(results, src_root: str):
    # See https://docs.python.org/3/library/time.html#time.strftime for table
    # explaining formattng
    # Format: YYYY-MM-DD_HH-MM-SS
    current_time: str = time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime())
    file_name = Path(current_time + ".csv")

    _write_metadata(file_name, src_root)
    _write_resutls(file_name, results)


def _write_metadata(file_name: Path, src_root: str):
    file_location = Path("output") / Path("metadata") / file_name

    with open(file_location, "w") as metadata_file:
        writer = csv.writer(metadata_file)
        writer.writerow(["qualitymodel", "src_root"])
        writer.writerow(["actual code climate", src_root])


def _write_resutls(file_name: Path, results):
    file_location = Path("output") / Path("frequencies") / file_name

    with open(file_location, "w") as results_file:
        writer = csv.writer(results_file)
        writer.writerow(["metric", "value"])
        for description, value in results.items():
            writer.writerow([description, value])


if __name__ == "__main__":
    main()
