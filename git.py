import subprocess
from pathlib import Path
from typing import Callable, List


def read_tags(git_folder: Path):
    tags_path: Path = git_folder / Path("refs") / Path("tags")
    tags = [(tag.name, tag.read_text().strip()) for tag in tags_path.iterdir()]
    # Assumes versioning lexographical sort is chronological
    return sorted(tags)


def switch_repo(github_slug: str):
    github_url = f"git@github.com:{github_slug}.git"

    clone_repo(github_slug)
    subprocess.run(
        [f"cd ../testing && git remote add target {github_url}"],
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


def clone_repo(github_slug: str):
    github_url = f"git@github.com:{github_slug}.git"

    subprocess.run("cd .. && rm -rf target", shell=True)
    subprocess.run([f"cd .. && git clone {github_url} target"], shell=True)


def reset_repo(commit: str):
    subprocess.run([f"cd ../testing && git reset --hard {commit}"], shell=True)
    subprocess.run(["cd ../testing && git push -f"], shell=True)


def iterate_over_tags(tags: List, action_between_tags: Callable):
    tags = tags[20:]
    for tag, commit in tags:
        reset_repo(commit)
        action_between_tags(tag)
