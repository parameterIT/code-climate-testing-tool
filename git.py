import subprocess
from pathlib import Path
from typing import Callable, List


def read_tags(git_folder: Path):
    tags_path: Path = git_folder / Path("refs") / Path("tags")
    tags = [(tag.name, tag.read_text().strip()) for tag in tags_path.iterdir()]
    # Assumes versioning lexographical sort is chronological
    return sorted(tags)


def switch_repo(remote_url: str):
    subprocess.run(
        ["cd ../testing && git remote add target git@github.com:pallets/flask.git"],
        shell=True,
    )
    subprocess.run(
        [
            "cd ../testing && git remote add origin git@github.com:parameterIT/testing.git"
        ],
        shell=True,
    )
    subprocess.run(["cd ../testing && git fetch target"], shell=True)
    subprocess.run(["cd ../testing && git checkout main"], shell=True)
    subprocess.run(["cd ../testing && git reset --hard target/main"], shell=True)
    subprocess.run(["cd ../testing && git push -f"], shell=True)


def reset_repo(commit: str):
    subprocess.run([f"cd ../testing && git reset --hard {commit}"], shell=True)
    subprocess.run(["cd ../testing && git push -f"], shell=True)


def iterate_over_tags(tags: List, action_between_tags: Callable):
    for tag, commit in tags:
        reset_repo(commit)
        action_between_tags(tag)
