#!/bin/bash

# Run tests with watch mode - re-runs on any file change

echo "Starting test watcher..."
echo "Tests will automatically re-run when files change."
echo "Press Ctrl+C to stop."
echo ""

# Install pytest-watch if not present
pip install pytest-watch -q

# Run pytest-watch with coverage
ptw --runner "pytest --cov=src --cov-report=term-missing -v"