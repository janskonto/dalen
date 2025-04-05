#!/usr/bin/env python3
"""
GitHub-optimized version of the Evardalen scraper
"""
import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Constants
WEBSITE_URL = "https://www.evardalen.com"
OUTPUT_DIR = "docs"  # GitHub Pages serves from /docs or root
IMAGES_DIR = os.path.join(OUTPUT_DIR, "images") 
CURRENT_DATA_FILE = os.path.join(OUTPUT_DIR, "current_data.json")
HISTORY_FILE = os.path.join(OUTPUT_DIR, "history.json")

# Rest of your scraper code with paths updated
# ...

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

# Run the scraper
run_scraper()
