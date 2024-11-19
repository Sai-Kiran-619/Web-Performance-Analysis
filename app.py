from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

def classify_time(load_time, good_limit, ok_limit):
    if load_time < good_limit:
        return "Good"
    elif load_time < ok_limit:
        return "Ok"
    else:
        return "Bad"

def analyze_assets(url):
    analysis = {
        "html": {"load_time": None, "classification": None, "size": None, "ttfb": None},
        "css": [],
        "js": [],
        "images": [],
        "request_count": 0,
        "total_size": 0
    }

    # Measure TTFB (Time to First Byte) for HTML
    start_time = time.time()
    response = requests.get(url)
    ttfb = time.time() - start_time
    html_load_time = ttfb
    html_size = len(response.content)

    analysis["html"] = {
        "load_time": html_load_time,
        "classification": classify_time(html_load_time, 0.5, 1.5),
        "size": html_size / 1024,  # Convert to KB
        "ttfb": ttfb
    }
    analysis["total_size"] += html_size
    analysis["request_count"] += 1

    # Parse HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Analyze CSS
    for css in soup.find_all('link', rel="stylesheet"):
        css_url = css['href']
        if not css_url.startswith("http"):
            css_url = url + css_url
        start_time = time.time()
        css_response = requests.get(css_url)
        css_load_time = time.time() - start_time
        css_size = len(css_response.content)

        analysis["css"].append({
            "url": css_url,
            "load_time": css_load_time,
            "classification": classify_time(css_load_time, 0.3, 1.0),
            "size": css_size / 1024  # KB
        })
        analysis["total_size"] += css_size
        analysis["request_count"] += 1

    # Analyze JS
    for script in soup.find_all('script', src=True):
        js_url = script['src']
        if not js_url.startswith("http"):
            js_url = url + js_url
        start_time = time.time()
        js_response = requests.get(js_url)
        js_load_time = time.time() - start_time
        js_size = len(js_response.content)

        analysis["js"].append({
            "url": js_url,
            "load_time": js_load_time,
            "classification": classify_time(js_load_time, 0.3, 1.0),
            "size": js_size / 1024  # KB
        })
        analysis["total_size"] += js_size
        analysis["request_count"] += 1

    # Analyze Images
    for img in soup.find_all('img', src=True):
        img_url = img['src']
        if not img_url.startswith("http"):
            img_url = url + img_url
        start_time = time.time()
        img_response = requests.get(img_url)
        img_load_time = time.time() - start_time
        img_size = len(img_response.content)

        analysis["images"].append({
            "url": img_url,
            "load_time": img_load_time,
            "classification": classify_time(img_load_time, 1.0, 3.0),
            "size": img_size / 1024  # KB
        })
        analysis["total_size"] += img_size
        analysis["request_count"] += 1

    return analysis

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.json.get('url')
    analysis = analyze_assets(url)
    return jsonify(analysis)

@app.route('/test')
def test():
    return "Flask is running!"

if __name__ == '__main__':
    app.run(debug=True)
