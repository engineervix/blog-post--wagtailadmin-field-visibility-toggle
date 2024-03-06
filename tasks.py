import os
import subprocess
from datetime import datetime
from pathlib import Path  # noqa: F401

import tomllib
from colorama import Fore, init
from invoke import run, task


@task
def clean_pyc(c):
    """remove Python file artifacts"""

    c.run("find . -name '*.pyc' -exec rm -f {} +", pty=True)
    c.run("find . -name '*.pyo' -exec rm -f {} +", pty=True)
    c.run("find . -name '*~' -exec rm -f {} +", pty=True)
    c.run("find . -name '__pycache__' -exec rm -fr {} +", pty=True)


@task
def clean_test(c):
    """remove test and coverage artifacts"""

    c.run("rm -fr .tox/", pty=True)
    c.run("rm -f .coverage", pty=True)
    c.run("rm -f coverage.xml", pty=True)
    c.run("rm -fr htmlcov/", pty=True)
    c.run("rm -fr .pytest_cache", pty=True)


def get_first_commit():
    try:
        output = subprocess.check_output(
            ["git", "log", "--reverse", "--format=%H", "--max-parents=0"],
            universal_newlines=True,
        )
        return output.strip()
    except subprocess.CalledProcessError:
        return None


@task(
    help={
        "branch": "The branch against which you wanna bump",
        "push": "Push to origin after bumping",
    }
)
def bump(c, branch="main", is_first_release=False, push=False):
    """Use BumpVer & standard-version to bump version and generate changelog

    Run this task when you want to prepare a release.
    First we check that there are no unstaged files before running
    """

    init()

    unstaged_str = "not staged for commit"
    uncommitted_str = "to be committed"
    check = c.run("git status", pty=True)
    if unstaged_str not in check.stdout or uncommitted_str not in check.stdout:
        if is_first_release:
            first_commit = get_first_commit()
            project = "a Wagtail project"
            if first_commit:
                c.run(f"git checkout {first_commit}", pty=True)
                cmd = "git show --format=%aD | head -1"
                c.run(f'GIT_COMMITTER_DATE="$({cmd})"', pty=True)
                result = run(cmd, hide=True, warn=True)
                commit_date = (
                    result.stdout.splitlines()[-1]
                    if result.ok
                    else "Wed, 6 Mar 2024 01:01:09 +0000"
                )
                formatted_commit_date = datetime.strptime(
                    commit_date, "%a, %d %b %Y %H:%M:%S %z"
                ).strftime("%Y.%m.%d")
                c.run(
                    f'git tag -a {formatted_commit_date} -m "version {formatted_commit_date} - this is where it all starts"',
                    pty=True,
                )
                c.run("unset GIT_COMMITTER_DATE", pty=True)
                c.run(f"git checkout {branch}", pty=True)
                c.run("bumpver update", pty=True)

                with open("pyproject.toml", "rb") as f:
                    toml_dict = tomllib.load(f)
                version_files = toml_dict["bumpver"]["file_patterns"].keys()
                files_to_add = " ".join(list(version_files))
                c.run(
                    f"git add {files_to_add}",
                    pty=True,
                )
                c.run(
                    f'npm run release -- --commit-all --skip.bump --tag-prefix "" --releaseCommitMessageFormat "chore: This is {project} kickstarted on {{{{currentTag}}}} 🎉"',
                    pty=True,
                )
                if push:
                    # push to origin
                    c.run(f"git push --follow-tags origin {branch}", pty=True)
            else:
                print("No commit found or Git repository not initialized.")

        else:
            get_current_tag = c.run(
                "git describe --abbrev=0 --tags `git rev-list --tags --skip=0  --max-count=1`",
                pty=True,
            )
            previous_tag = get_current_tag.stdout.rstrip()
            c.run("bumpver update", pty=True)

            with open("pyproject.toml", "rb") as f:
                toml_dict = tomllib.load(f)
            version_files = toml_dict["bumpver"]["file_patterns"].keys()
            files_to_add = " ".join(list(version_files))
            c.run(
                f"git add {files_to_add}",
                pty=True,
            )
            c.run(
                f'npm run release -- --commit-all --skip.bump --tag-prefix "" --releaseCommitMessageFormat "bump: ✈️ {previous_tag} → {{{{currentTag}}}}"',
                pty=True,
            )
            if push:
                # push to origin
                c.run(f"git push --follow-tags origin {branch}", pty=True)
    else:
        print(
            f"{Fore.RED}Sorry mate, please ensure there are no unstaged files before creating a release{Fore.RESET}"
        )


@task
def get_release_notes(c):
    """extract content from CHANGELOG.md for use in Github/Gitlab Releases

    we read the file and loop through line by line
    we wanna extract content beginning from the first Heading 2 text
    to the last line before the next Heading 2 text
    """

    pattern_to_match = "## ["

    count = 0
    lines = []
    heading_text = "## What's changed in this release\n"
    lines.append(heading_text)

    with open("CHANGELOG.md", "r") as c:
        for line in c:
            if pattern_to_match in line and count == 0:
                count += 1
            elif pattern_to_match not in line and count == 1:
                lines.append(line)
            elif pattern_to_match in line and count == 1:
                break

    # home = str(Path.home())
    # release_notes = os.path.join(home, "LATEST_RELEASE_NOTES.md")
    release_notes = os.path.join("../", "LATEST_RELEASE_NOTES.md")
    with open(release_notes, "w") as f:
        print("".join(lines), file=f, end="")
