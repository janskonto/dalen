#!/usr/bin/env python3
"""
Evardalen Weather and Camera Image Scraper

This script scrapes the Evardalen website to extract:
1. The latest camera image
2. Current wind speed and direction
3. Current temperature

The script saves the image and weather data for display on a webpage.
"""

import os
import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("evardalen_scraper.log"),
        logging.StreamHandler()
    ]
)

# Constants
WEBSITE_URL = "https://www.evardalen.com"
IMAGE_BASE_URL = "https://www.evardalen.com/Hikvision1/"
OUTPUT_DIR = "evardalen_data"
HISTORY_FILE = os.path.join(OUTPUT_DIR, "history.json")

def ensure_output_dir():
    """Ensure the output directory exists."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        logging.info(f"Created output directory: {OUTPUT_DIR}")
    
    # Create subdirectories
    images_dir = os.path.join(OUTPUT_DIR, "images")
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        logging.info(f"Created images directory: {images_dir}")

def get_webpage_content():
    """Fetch the webpage content."""
    try:
        response = requests.get(WEBSITE_URL, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching webpage: {e}")
        return None

def extract_camera_image_url(html_content):
    """Extract the camera image URL from the HTML content."""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for the image in the widget area
        widget_area = soup.select('.widget-area')
        if widget_area:
            # Find the section with "KAMERA NÅ" heading
            camera_section = None
            for section in widget_area:
                if "KAMERA NÅ" in section.text:
                    camera_section = section
                    break
            
            if camera_section:
                image = camera_section.find('img')
                if image and 'src' in image.attrs:
                    img_src = image['src']
                    # Ensure URL is absolute
                    if not img_src.startswith(('http://', 'https://')):
                        if img_src.startswith('/'):
                            img_src = f"{WEBSITE_URL}{img_src}"
                        else:
                            img_src = f"{WEBSITE_URL}/{img_src}"
                    return img_src
        
        # Fallback: search for any image with Hikvision1 in the URL
        all_images = soup.find_all('img')
        for img in all_images:
            if 'src' in img.attrs and 'Hikvision1' in img['src']:
                img_src = img['src']
                # Ensure URL is absolute
                if not img_src.startswith(('http://', 'https://')):
                    if img_src.startswith('/'):
                        img_src = f"{WEBSITE_URL}{img_src}"
                    else:
                        img_src = f"{WEBSITE_URL}/{img_src}"
                return img_src
                
        logging.warning("Camera image URL not found")
        return None
    except Exception as e:
        logging.error(f"Error extracting camera image URL: {e}")
        return None

def extract_weather_data(html_content):
    """Extract weather data (wind speed, direction, and temperature) from the HTML content."""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Initialize weather data
        weather_data = {
            'wind_speed': None,
            'wind_direction': None,
            'temperature': None,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Find the weather section
        weather_section = None
        for section in soup.find_all(['div', 'section']):
            if "VÆR OG VIND" in section.text:
                weather_section = section
                break
        
        if not weather_section:
            # Try to find by looking at all text
            text = soup.get_text()
            
            # Extract wind data
            wind_match = re.search(r'Vind Nå:\s*([\d.]+)\s*m/s\s*([A-Z]+)', text)
            if wind_match:
                weather_data['wind_speed'] = float(wind_match.group(1))
                weather_data['wind_direction'] = wind_match.group(2)
            
            # Extract temperature data
            temp_match = re.search(r'Ute Nå:\s*([-\d.]+)\s*°C', text)
            if temp_match:
                weather_data['temperature'] = float(temp_match.group(1))
        else:
            # Extract from the weather section
            text = weather_section.get_text()
            
            # Extract wind data
            wind_match = re.search(r'Vind Nå:\s*([\d.]+)\s*m/s\s*([A-Z]+)', text)
            if wind_match:
                weather_data['wind_speed'] = float(wind_match.group(1))
                weather_data['wind_direction'] = wind_match.group(2)
            
            # Extract temperature data
            temp_match = re.search(r'Ute Nå:\s*([-\d.]+)\s*°C', text)
            if temp_match:
                weather_data['temperature'] = float(temp_match.group(1))
        
        if weather_data['wind_speed'] is None and weather_data['temperature'] is None:
            logging.warning("Weather data not found")
            return None
            
        return weather_data
    except Exception as e:
        logging.error(f"Error extracting weather data: {e}")
        return None

def download_image(image_url):
    """Download the camera image."""
    try:
        if not image_url:
            logging.warning("No image URL provided")
            return None
            
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # Extract filename from URL
        filename = os.path.basename(image_url)
        save_path = os.path.join(OUTPUT_DIR, "images", filename)
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
            
        logging.info(f"Image downloaded and saved to {save_path}")
        return save_path
    except requests.exceptions.RequestException as e:
        logging.error(f"Error downloading image: {e}")
        return None
    except Exception as e:
        logging.error(f"Error saving image: {e}")
        return None

def save_weather_data(weather_data, image_path):
    """Save weather data and image info to JSON file."""
    try:
        if not weather_data:
            logging.warning("No weather data to save")
            return False
            
        # Create data entry
        data_entry = {
            'timestamp': weather_data['timestamp'],
            'wind_speed': weather_data['wind_speed'],
            'wind_direction': weather_data['wind_direction'],
            'temperature': weather_data['temperature'],
            'image_path': os.path.basename(image_path) if image_path else None
        }
        
        # Save current data
        current_data_path = os.path.join(OUTPUT_DIR, "current_data.json")
        with open(current_data_path, 'w') as f:
            json.dump(data_entry, f, indent=2)
        
        # Update history
        history = []
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r') as f:
                    history = json.load(f)
            except json.JSONDecodeError:
                logging.warning("Error reading history file, starting fresh")
                history = []
        
        # Add new entry to history
        history.append(data_entry)
        
        # Keep only the last 30 entries
        if len(history) > 30:
            history = history[-30:]
        
        # Save updated history
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
            
        logging.info("Weather data saved successfully")
        return True
    except Exception as e:
        logging.error(f"Error saving weather data: {e}")
        return False

def is_new_image(image_url):
    """Check if the image is new by comparing with the last downloaded image."""
    if not image_url:
        return False
        
    # Extract filename from URL
    filename = os.path.basename(image_url)
    
    # Check if we have history
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
                
            if history and history[-1]['image_path']:
                last_image = history[-1]['image_path']
                return last_image != filename
        except Exception:
            # If there's any error, assume it's a new image
            return True
    
    return True

def run_scraper():
    """Run the scraper to extract and save data."""
    logging.info("Starting Evardalen scraper")
    
    # Ensure output directory exists
    ensure_output_dir()
    
    # Get webpage content
    html_content = get_webpage_content()
    if not html_content:
        logging.error("Failed to get webpage content")
        return False
    
    # Extract camera image URL
    image_url = extract_camera_image_url(html_content)
    logging.info(f"Found camera image URL: {image_url}")
    
    # Check if it's a new image
    if not is_new_image(image_url):
        logging.info("No new image found, skipping download")
        return False
    
    # Download image
    image_path = download_image(image_url)
    
    # Extract weather data
    weather_data = extract_weather_data(html_content)
    logging.info(f"Extracted weather data: {weather_data}")
    
    # Save data
    if weather_data and image_path:
        save_weather_data(weather_data, image_path)
        logging.info("Scraping completed successfully")
        return True
    else:
        logging.warning("Scraping completed with missing data")
        return False

if __name__ == "__main__":
    run_scraper()
