# Evardalen Weather and Camera Image Scraper

This package contains a solution for scraping the Evardalen website to extract the latest camera image and weather data (wind speed, direction, and temperature), and displaying this information on a webpage.

## Contents

- `evardalen_scraper.py` - Python script to scrape the Evardalen website
- `evardalen_viewer.html` - Webpage to display the camera image and weather data
- `scheduler.py` - Optional Python script to run the scraper on a schedule
- `requirements.txt` - List of Python dependencies

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Directory Structure

The scraper will save data to an `evardalen_data` directory. This will be created automatically when the script runs, but you can also create it manually:

```bash
mkdir -p evardalen_data/images
```

### 3. Run the Scraper

To run the scraper once:

```bash
python evardalen_scraper.py
```

This will:
- Fetch the latest camera image from Evardalen
- Extract the current weather data (temperature, wind speed, and direction)
- Save the image to `evardalen_data/images/`
- Save the weather data to `evardalen_data/current_data.json`
- Update the history in `evardalen_data/history.json`

### 4. View the Data

Open `evardalen_viewer.html` in a web browser to view the camera image and weather data. The webpage will automatically load the latest data from the JSON files.

## Scheduling Options

Since you requested the scraper to run every 8 hours, here are several options:

### Option 1: Use the included scheduler.py

```bash
python scheduler.py
```

This will:
- Run the scraper immediately
- Schedule it to run every 8 hours
- Keep running until stopped (Ctrl+C)
- Log activities to scheduler.log

Note: This requires keeping the computer running and the script active.

### Option 2: Cron Job (Linux/Unix/Mac)

```bash
# Edit your crontab
crontab -e

# Add this line to run at 00:00, 08:00, and 16:00 daily
0 0,8,16 * * * cd /path/to/script && python evardalen_scraper.py
```

### Option 3: Windows Task Scheduler

1. Open Task Scheduler
2. Create a new Basic Task
3. Set the trigger to run daily, and configure it to repeat every 8 hours
4. Set the action to start a program: python.exe with the full path to the script as an argument

### Option 4: Docker Container

A Dockerfile is included if you prefer to run the solution in a container:

```bash
# Build the Docker image
docker build -t evardalen-scraper .

# Run the container
docker run -d -v $(pwd)/evardalen_data:/app/evardalen_data evardalen-scraper
```

## Serving the Webpage

To make the webpage accessible:

### Simple HTTP Server

You can use Python's built-in HTTP server:

```bash
# Navigate to the directory containing evardalen_viewer.html
cd /path/to/directory

# Start a simple HTTP server
python -m http.server 8000
```

Then access the webpage at http://localhost:8000/evardalen_viewer.html

### Web Server

For a more permanent solution, configure a web server like Apache or Nginx to serve the HTML file and the data directory.

## Troubleshooting

- If the scraper fails to download images, check your internet connection and verify that the Evardalen website structure hasn't changed.
- If the webpage doesn't display data, ensure the JSON files exist in the correct location and have proper permissions.
- Check the log files (`evardalen_scraper.log` and `scheduler.log`) for error messages.

## Customization

- Edit the CSS in `evardalen_viewer.html` to change the appearance
- Modify the refresh interval in the scheduler by changing `schedule.every(8).hours` to your preferred interval
