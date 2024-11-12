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
        "html": {"load_time": None, "classification": None},
        "css": [],
        "js": [],
        "images": []
    }

    # Measure HTML load time
    start_time = time.time()
    response = requests.get(url)
    html_load_time = time.time() - start_time
    analysis["html"] = {
        "load_time": html_load_time,
        "classification": classify_time(html_load_time, 0.5, 1.5)
    }

    soup = BeautifulSoup(response.text, 'html.parser')

    # Measure CSS, JS, and Image load times
    for css in soup.find_all('link', rel="stylesheet"):
        css_url = css['href']
        if not css_url.startswith("http"):
            css_url = url + css_url
        start_time = time.time()
        requests.get(css_url)
        css_load_time = time.time() - start_time
        analysis["css"].append({
            "url": css_url,
            "load_time": css_load_time,
            "classification": classify_time(css_load_time, 0.3, 1.0)
        })

    for script in soup.find_all('script', src=True):
        js_url = script['src']
        if not js_url.startswith("http"):
            js_url = url + js_url
        start_time = time.time()
        requests.get(js_url)
        js_load_time = time.time() - start_time
        analysis["js"].append({
            "url": js_url,
            "load_time": js_load_time,
            "classification": classify_time(js_load_time, 0.3, 1.0)
        })

    for img in soup.find_all('img', src=True):
        img_url = img['src']
        if not img_url.startswith("http"):
            img_url = url + img_url
        start_time = time.time()
        requests.get(img_url)
        img_load_time = time.time() - start_time
        analysis["images"].append({
            "url": img_url,
            "load_time": img_load_time,
            "classification": classify_time(img_load_time, 1.0, 3.0)
        })

    return analysis

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.json.get('url')
    analysis = analyze_assets(url)
    return jsonify(analysis)

if __name__ == '__main__':
    app.run(debug=True)
