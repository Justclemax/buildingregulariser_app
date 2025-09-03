from flask import Flask, render_template, request, jsonify, redirect
import geopandas as gpd
from buildingregulariser import regularize_geodataframe
import os
import time

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return redirect("/")
    file = request.files["file"]
    if file.filename == "":
        return redirect("/")

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    # Charger données
    gdf = gpd.read_file(filepath)

    # Régulariser
    start = time.time()
    regularized = regularize_geodataframe(gdf, simplify_tolerance=2.0)
    speed = f"{len(gdf) / (time.time() - start):.0f} polygons/sec"

    # Convertir en GeoJSON string
    original_json = gdf.to_crs(epsg=4326).to_json()
    regularized_json = regularized.to_crs(epsg=4326).to_json()

    return jsonify({
        "speed": speed,
        "original": original_json,
        "regularized": regularized_json
    })

if __name__ == "__main__":
    app.run()