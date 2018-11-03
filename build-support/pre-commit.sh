#!/bin/bash

# Ensure we are executing at the buildroot.
cd "$(git rev-parse --show-toplevel)"

./pants lint ::
./pants test ::
