#!/bin/bash

# Ensure we are executing at the buildroot.
cd "$(git rev-parse --show-toplevel)"

# Adds a pre-commit hook to ensure testing works as expected.
ln -sfv build-support/pre-commit.sh \
   .git/hooks/pre-commit
