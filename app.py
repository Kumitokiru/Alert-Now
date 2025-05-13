import eventlet
eventlet.monkey_patch()

from flask import Flask, request, render_template, jsonify
from flask_socketio import SocketIO, emit
import pickle, numpy as np, math, os, time
from werkzeug.utils import secure_filename
from roboflow import Roboflow  # make sure to install roboflow

# === Flask + Socket.IO setup ===
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# === Upload folder ===
UPLOAD_FOLDER = "static/uploads/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# === KNN geofencing ===
def haversine_distance(c1, c2):
    lat1,lon1,lat2,lon2 = map(math.radians, [*c1,*c2])
    dlat,dlon = lat2-lat1, lon2-lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

with open("knn_model.pkl","rb") as f:
    knn = pickle.load(f)
with open("label_encoder.pkl","rb") as f:
    label_encoder = pickle.load(f)

def predict_barangay(lat, lon):
    idx = knn.predict(np.array([[lat, lon]]))
    return label_encoder.inverse_transform(idx)[0]

# === Roboflow model for accidents ===
rf = Roboflow(api_key="Evdj8YqGLC5At2Cu080d")
project = rf.workspace().project("roadaccident")
rf_model = project.version("1").model

def detect_accident(image_path):
    res = rf_model.predict(image_path, confidence=40, overlap=30).json()
    return any(obj["class"] == "road_accident" for obj in res["predictions"])

# === In-memory alert store ===
alerts = []

# === Routes ===
@app.route('/')
def login_type():
    return render_template("login_type.html")

@app.route('/resident')
def resident():
    return render_template("resident_page.html")

@app.route('/barangay')
def barangay():
    return render_template("barangay_page_sse.html")

@app.route('/cdrrmo')
def cdrrmo():
    return render_template("cdrrmo_page.html")

@app.route('/pnp')
def pnp():
    return render_template("pnp_page.html")

@app.route('/send_alert', methods=['POST'])
def send_alert():
    lat = float(request.form['lat'])
    lon = float(request.form['lon'])
    img = request.files.get('image')
    barangay = predict_barangay(lat, lon)

    alert = {
        "timestamp": time.time(),
        "lat": lat,
        "lon": lon,
        "barangay": barangay,
        "image": None,
        "alert_type": "normal"
    }

    if img:
        fn = secure_filename(img.filename)
        path = os.path.join(UPLOAD_FOLDER, fn)
        img.save(path)
        alert["image"] = fn
        if detect_accident(path):
            alert["alert_type"] = "road_accident"

    alerts.append(alert)
    socketio.emit("new_alert", alert, broadcast=True)
    return jsonify(success=True, barangay=barangay)

@socketio.on("connect")
def on_connect():
    emit("bulk_alerts", alerts)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=True)
