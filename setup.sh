#!/usr/bin/env bash
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
printf "\n |-----------------------------------------------------------------------------| \n "
printf "|  Don't forget to run \". venv/bin/activate\" and update credentials in app.py.| \n "
printf "|-----------------------------------------------------------------------------| \n "
printf "\n"