from __future__ import annotations
import argparse
import logging
import os
import sys
import time

# ─── PATH MANAGEMENT FOR LOCAL & RENDER CLOUD ───────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

# Add parent just in case Render treats 'src' weirdly
_PARENT = os.path.dirname(_HERE)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)
# ───────────────────────────────────────────────────────────────────

from flask import Flask, Response, jsonify, render_template

try:
    from src.config import Config
    from src.pipeline import Pipeline
except (ModuleNotFoundError, ImportError):
    import config as Config  # type: ignore
    import pipeline as Pipeline  # type: ignore

RUN_PIPELINE = os.environ.get("RUN_PIPELINE", "1") != "0"

app = Flask(
    __name__,
    template_folder="dashboard/templates",
    static_folder="dashboard/static",
)
log = logging.getLogger("app")
pipeline: Pipeline | None = None
config: Config | None = None

def _mjpeg_generator():
    while True:
        frame = pipeline.get_latest_frame() if pipeline is not None else None
        if frame is None:
            time.sleep(0.1)
            continue
        import cv2
        ok, buffer = cv2.imencode(".jpg", frame)
        if not ok:
            continue
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")
        time.sleep(0.03)

@app.route("/")
def index():
    # Render fallback templates layout check
    try:
        return render_template(
            "index.html",
            refresh_seconds=int(config.get("dashboard.refresh_seconds", 5)) if config else 5,
            speed_limit=config.get("speed.speed_limit_kmph", 60) if config else 60,
        )
    except Exception:
        return "<h1>Smart Road Vehicle Analytics System Live!</h1><p>Dashboard UI template folders are missing, but API endpoints are working fine.</p>"

@app.route("/video_feed")
def video_feed():
    if pipeline is None:
        return Response("Live processing disabled.", status=503, mimetype="text/plain")
    return Response(_mjpeg_generator(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/api/stats")
def api_stats():
    if pipeline is None:
        return jsonify({"count_up": 0, "count_down": 0, "total": 0, "density_state": "-", "occupancy": 0.0, "fps": 0.0, "total_vehicles": 0, "total_violations": 0, "total_plates": 0})
    return jsonify({**pipeline.get_stats(), **pipeline.db.summary()})

@app.route("/api/categories")
def api_categories():
    return jsonify(pipeline.db.counts_by_category() if pipeline is not None else {})

@app.route("/api/hourly")
def api_hourly():
    return jsonify(pipeline.db.hourly_counts(hours=24) if pipeline is not None else [])

@app.route("/api/violations")
def api_violations():
    return jsonify(pipeline.db.recent_violations(limit=20) if pipeline is not None else [])

def main() -> None:
    global pipeline, config
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    config = Config.load(args.config)

    if RUN_PIPELINE:
        try:
            pipeline = Pipeline(config)
            pipeline.start_async()
        except Exception as exc:
            log.error("Could not start pipeline: %s", exc)
            pipeline = None

    host = "0.0.0.0"
    port = int(os.environ.get("PORT", 5000))
    log.info("Dashboard on http://%s:%s", host, port)
    app.run(host=host, port=port, threaded=True, debug=False)

if __name__ == "__main__":
    main()