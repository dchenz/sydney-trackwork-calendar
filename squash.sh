#!/bin/bash

set -e

if [ "$(git config user.name)" != "github-actions[bot]" ]; then
    echo "Error: This script is intended to run in github actions."
    exit 1
fi

if git fetch origin "$DATA_BRANCH"; then
    git checkout FETCH_HEAD
fi

LATEST_COMMIT_DATE=$(git show --no-patch --format=%ci HEAD)

git reset --soft "$(git rev-list HEAD | tail -n 1)"

if git commit --amend --no-edit --date "$LATEST_COMMIT_DATE"; then
    git push origin "HEAD:$DATA_BRANCH" --force
fi
