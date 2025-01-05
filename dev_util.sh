#!/bin/bash

# Check if a flag is provided
if [ -z "$1" ]; then
  echo "Usage: $0 {tokenize|parse|test-all|test|submit}"
  exit 1
fi

# Run commands based on the provided flag
case "$1" in
  "tokenize")
    python3 -m app.main tokenize test.lox
    ;;
  "parse")
    python3 -m app.main parse test.lox
    ;;
  "eval")
    python3 -m app.main evaluate test.lox
    ;;
  *)
    echo "Unknown flag: $1"
    echo "Usage: $0 {tokenize|parse|eval}"
    exit 1
    ;;
esac