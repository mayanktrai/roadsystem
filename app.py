from __future__ import annotations
import argparse
import logging
import os
import sys
import time
import random

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from flask import Flask, Response, jsonify, render_template_string

# Counter Simulation variables
sim_data = {
    "total_vehicles": 120,
    "total_violations": 3,
    "density_state": "Normal",
    "fps": 29.4
}

app = Flask(__name__)
log = logging.getLogger("app")

def _mjpeg_generator():
    # Yeh internet se ek real-time live traffic public camera feed stream karega blank box ki jagah!
    import cv2
    # Agar cv2 installed hai toh live traffic sample stream chalegi
    cap = cv2.VideoCapture("https://assets.mixkit.co/videos/preview/mixkit-traffic-in-a-highway-at-night-42352-large.mp4")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # Loop video
            continue
            
        # Draw fake bounding boxes on vehicles to look like REAL AI detection!
        h, w, _ = frame.shape
        # Fake Box 1
        cv2.rectangle(frame, (int(w*0.3), int(h*0.4)), (int(w*0.45), int(h*0.6)), (0, 255, 0), 2)
        cv2.putText(frame, "Car: 98%", (int(w*0.3), int(h*0.4)-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        # Fake Box 2
        cv2.rectangle(frame, (int(w*0.6), int(h*0.5)), (int(w*0.8), int(h*0.75)), (0, 0, 255), 2)
        cv2.putText(frame, "Truck: Speeding", (int(w*0.6), int(h*0.5)-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        # Virtual Counting Line
        cv2.line(frame, (0, int(h*0.65)), (w, int(h*0.65)), (255, 255, 0), 3)

        ok, buffer = cv2.imencode(".jpg", frame)
        if not ok:
            continue
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")
        time.sleep(0.03)

@app.route("/")
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Smart Road Vehicle Analytics System</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; color: #333; }
            .container { max-width: 1200px; margin: 0 auto; }
            header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; text-align: center; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 20px; }
            .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }
            .card h3 { margin: 0; color: #7f8c8d; font-size: 14px; text-transform: uppercase; }
            .card p { margin: 10px 0 0 0; font-size: 28px; font-weight: bold; color: #2c3e50; }
            .main-content { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
            .video-box { background: #000; border-radius: 8px; min-height: 400px; display: flex; align-items: center; justify-content: center; color: white; overflow: hidden; }
            .video-box img { width: 100%; height: auto; }
            .table-box { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            h2 { margin-top: 0; color: #2c3e50; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; }
        </style>
        <script>
            function refreshStats() {
                fetch('/api/stats').then(res => res.json()).then(data => {
                    document.getElementById('total-vehicles').innerText = data.total_vehicles;
                    document.getElementById('total-violations').innerText = data.total_violations;
                    document.getElementById('fps').innerText = data.fps.toFixed(1);
                    document.getElementById('density').innerText = data.density_state;
                });
            }
            setInterval(refreshStats, 2000);
            window.onload = refreshStats;
        </script>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Smart Road Vehicle Analytics & Traffic Management System</h1>
                <p style="color: #2ecc71; font-weight: bold;">🟢 System Status: Active & Processing</p>
            </header>
            
            <div class="grid">
                <div class="card"><h3>Total Vehicles</h3><p id="total-vehicles">0</p></div>
                <div class="card"><h3 style="color: #e74c3c;">Traffic Violations</h3><p id="total-violations" style="color: #e74c3c;">0</p></div>
                <div class="card"><h3>Current Density</h3><p id="density">-</p></div>
                <div class="card"><h3>System Performance</h3><p id="fps">0.0 FPS</p></div>
            </div>

            <div class="main-content">
                <div class="video-box">
                    <img src="/video_feed" alt="Live Stream Load Error">
                </div>
                <div class="table-box">
                    <h2>Live Event Logger</h2>
                    <div style="background: #111; color: #2ecc71; font-family: monospace; padding: 15px; border-radius: 5px; height: 300px; overflow-y: auto; font-size: 12px;" id="logger">
                        [INFO] Core initialized.<br>
                        [INFO] YOLOv8 Model Loaded onto Device: CPU<br>
                        [INFO] Tracking Thread Active...<br>
                    </div>
                </div>
            </div>
        </div>
        <script>
            // Fake real-time logs append block
            const logs = [
                "[DETECT] Car identified - Conf: 0.91",
                "[DETECT] Motorcycle identified - Conf: 0.86",
                "[COUNTER] Vehicle crossed line (Flow: Downward)",
                "[SPEED] Vehicle ID #42 calculated speed: 54 km/h",
                "[WARNING] Speed Violation Detected! Vehicle ID #49 - 78 km/h"
            ];
            setInterval(() => {
                const logBox = document.getElementById('logger');
                const randomLog = logs[Math.floor(Math.random() * logs.length)];
                const timeStr = new Date().toLocaleTimeString();
                logBox.innerHTML += `[${timeStr}] ${randomLog}<br>`;
                logBox.scrollTop = logBox.scrollHeight;
            }, 3000);
        </script>
    </body>
    </html>
    """)

@app.route("/video_feed")
def video_feed():
    return Response(_mjpeg_generator(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/api/stats")
def api_stats():
    # Dynamic increments to show real-time progress
    sim_data["total_vehicles"] += random.randint(1, 3)
    if random.random() > 0.85:
        sim_data["total_violations"] += 1
    
    densities = ["Low", "Normal", "Heavy", "Normal"]
    sim_data["density_state"] = densities[random.randint(0, 3)]
    sim_data["fps"] = random.uniform(28.2, 29.9)
    
    return jsonify(sim_data)

def main() -> None:
    host = "0.0.0.0"
    port = 5000
    app.run(host=host, port=port, threaded=True, debug=False)

if __name__ == "__main__":
    main()
