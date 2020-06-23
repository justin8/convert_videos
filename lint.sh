#!/bin/bash
flake8="poetry run flake8"

# stop the build if there are Python syntax errors or undefined names
echo "Checking for syntax errors..."
$flake8 --select=E9,F63,F7,F82 --show-source --statistics convert_videos tests
# exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
echo "Checking for complexity issues..."
$flake8 --exit-zero --max-complexity=10 --max-line-length=140 --statistics convert_videos tests
