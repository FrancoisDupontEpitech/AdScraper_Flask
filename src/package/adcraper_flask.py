#!/usr/bin/env python
# Flask
from flask import Flask, render_template, jsonify, request, send_from_directory
import threading
from threading import Event
from get_new_company import get_new_company
from get_company_partnership import get_company_partnership
from utils.websites_variable import websites
import favicon
import os
import hashlib
import requests  # Import requests module

app = Flask(__name__)
stop_events = {}
scraping_status_dict = {}
FAVICON_DIR = 'favicons'  # Directory to store favicons

if not os.path.exists(FAVICON_DIR):
    os.makedirs(FAVICON_DIR)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_websites', methods=['GET'])
def get_websites():
    website_info = []
    for website in websites:
        icon_path = get_favicon_path(website["url"])
        website_info.append({"name": website["name"], "url": website["url"], "icon": icon_path})
    return jsonify({"websites": website_info})

def get_favicon_path(url):
    # Generate a unique filename based on the website URL
    filename = hashlib.md5(url.encode()).hexdigest() + '.ico'
    filepath = os.path.join(FAVICON_DIR, filename)

    # If the favicon already exists, return its path
    if os.path.exists(filepath):
        return filename  # Return only the filename

    # Otherwise, fetch and store the favicon
    try:
        icons = favicon.get(url)
        if icons:
            icon_url = icons[0].url
            response = requests.get(icon_url, stream=True)
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                return filename  # Return only the filename
    except Exception as e:
        print(f"Error fetching favicon for {url}: {e}")

    # Return a default icon path if fetching fails
    return 'default-icon.png'

@app.route('/start_scraping', methods=['POST'])
def start_scraping():
    mode = request.form.get('mode', 'ads')  # Correctly retrieves 'mode' from form data
    force = request.form.get('force', 'false') == 'true'
    scrape_id = request.form.get('scrape_id', 'default')
    selected_websites_indices = request.form.getlist('websites')

    # Create a new stop event for this scraping process
    stop_event = Event()
    stop_events[scrape_id] = stop_event
    scraping_status_dict[scrape_id] = {"completed": False}

    # Filter selected websites
    selected_websites = [websites[int(index)] for index in selected_websites_indices]

    thread = threading.Thread(target=scrape_and_process_data, args=(mode, force, scrape_id, selected_websites))
    thread.start()
    return jsonify({"message": "Scraping started", "scrape_id": scrape_id})  # popup message

def scrape_and_process_data(mode, force, scrape_id, selected_websites):
    stop_event = stop_events.get(scrape_id)
    if stop_event:
        get_company_partnership(mode, force, stop_event, selected_websites)
        get_new_company(mode, selected_websites)
        scraping_status_dict[scrape_id]["completed"] = True  # Use the new name

@app.route('/scraping_status/<scrape_id>', methods=['GET'])
def scraping_status(scrape_id):
    status = scraping_status_dict.get(scrape_id, {"completed": False})  # Use the new name
    return jsonify(status)

@app.route('/favicon/<filename>')
def serve_favicon(filename):
    return send_from_directory(FAVICON_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)
