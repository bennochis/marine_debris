from flask import Flask, request, redirect, render_template, url_for, flash
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sqlite3
from werkzeug.utils import secure_filename
from llm_classification import classify_debris
import requests

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DATABASE = 'database.db'

load_dotenv()
app.secret_key = os.environ.get("SECRET_KEY")


# Initialize DB
def init_db():
    conn = sqlite3.connect(DATABASE)
    with open('init.sql', 'r') as f:
        sql = f.read()
    conn.executescript(sql)
    conn.commit()
    conn.close()

init_db()
# Get country from lat,lon using Nominatim
def get_country_from_coords(lat, lon):
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        'lat': lat,
        'lon': lon,
        'format': 'json'
    }
    HEADERS = {
        'User-Agent': 'debris-flask-app-Lab6/1.0'
    }
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()  # raise HTTPError if the response was unsuccessful
        return response.json().get('address', {}).get('country', 'Unknown')
    except Exception as e:
        print(f"Geocoding failed: {e}") # added for check
        return 'Unknown'

# Root route – input form + submission table
@app.route('/', methods=['GET'])
def index():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM debris")
    rows = cur.fetchall()
    conn.close()
    return render_template('index.html', records=rows)

# Submit route – LLM debris categorization request with GPS coordinates
@app.route('/submit', methods=['POST'])
def submit():
    if 'photo' not in request.files or request.files['photo'].filename == '':
        flash('No photo provided')
        return redirect(url_for('index'))

    photo = request.files['photo']
    desc = request.form.get('description', '')
    gps = request.form.get('gps', '')  # Get "lat,lon" as a string
    
    try:
        lat_str, lon_str = gps.split(',')
        lat = float(lat_str.strip())
        lon = float(lon_str.strip())
        
    except:
        flash("Invalid GPS coordinates. See example format")
        return redirect(url_for('index'))

    filename = secure_filename(photo.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    filepath = filepath.replace("\\", "/") # Normalize path for consistent slashes
    photo.save(filepath)

    # LLM classification
    category = classify_debris(filepath, desc)
    if category == 'Other':
        flash("Rejected: Image is not a categorised marine debris.")
        return redirect(url_for('index'))

    country = get_country_from_coords(lat, lon)

    # Save to DB
    relative_path = filepath.replace("\\", "/")
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    gps = f"{lat},{lon}"
    cur.execute("INSERT INTO debris (file_path, category, gps, country) VALUES (?, ?, ?, ?)",
            (relative_path, category, gps, country))
    conn.commit()
    conn.close()

    flash("Submission successful")
    return redirect(url_for('index'))

#print("Starting Flask server...")
if __name__ == '__main__': # use this block of code if you plan to run Flask App with built-in development server.
    #app.run(debug=True) # default - runs only on localhost:5000
    app.run(debug=True, host="0.0.0.0", port=8080) # allows all network_interface:8080 to be open.
    #app.run(debug=True, port=8080) # runs on localhost:8080 (200), redirects other network_interfaces (304).