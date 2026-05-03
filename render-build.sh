#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install Tesseract OCR binary (Linux version)
apt-get update && apt-get install -y tesseract-ocr
