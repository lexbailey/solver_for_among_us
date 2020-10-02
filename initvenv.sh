#!/usr/bin/env sh
virtualenv --python=python3 venv
. venv/bin/activate
pip install -r requirements.txt
