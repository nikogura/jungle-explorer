#!/usr/bin/env bash

PYTHON=$(which python)

$PYTHON -c "__import__('compiler').parse(open('jungle.py').read())"
