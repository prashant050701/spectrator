from flask import Flask, request, jsonify, send_from_directory
import os
import crossmatch
import fetch_data
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

CSV_DIRECTORY = os.path.join(app.root_path, 'spectra_csv')

def is_gaia_id(identifier):
    return identifier.startswith("Gaia DR2") or identifier.startswith("Gaia DR3")

def extract_filter_name(file_name):
    name_parts = os.path.splitext(file_name)[0].split('_')
    if len(name_parts) > 1:
        return name_parts[-1]
    else:
        return None

@app.route('/get_spectrum', methods=['POST'])
def get_spectrum():
    identifier = request.json.get('name')
    if not identifier:
        return jsonify({"error": "No identifier provided"}), 400

    if is_gaia_id(identifier):
        gaia_id = identifier.split()[-1]
        object_info = crossmatch.fetch_object_info(identifier)
        ra = object_info['ra'] if object_info else None
        dec = object_info['dec'] if object_info else None
    else:
        object_info = crossmatch.fetch_object_info(identifier)
        gaia_id = object_info['gaia_id'] if object_info and 'gaia_id' in object_info else None
        ra = object_info['ra'] if object_info else None
        dec = object_info['dec'] if object_info else None

    if gaia_id and ra is not None and dec is not None:
        results = fetch_data.download_spectrum(gaia_id, ra, dec)
        if results:
            response = {"spectra": []}
            for source_type, file_paths in results.items():
                for file_path in file_paths:
                    file_name = os.path.basename(file_path)
                    file_url = f"http://127.0.0.1:5000/files/{file_name}"
                    filter_name = extract_filter_name(file_name)
                    response["spectra"].append({
                        "file_path": file_url,
                        "source_type": source_type,
                        "filter_name": filter_name
                    })
            return jsonify(response), 200
        else:
            return jsonify({"error": "Spectrum not found in any source", "source_type": "None"}), 404
    else:
        return jsonify({"error": "Object ID not found or missing RA/Dec", "source_type": "None"}), 404

@app.route('/files/<filename>')
def serve_file(filename):
    try:
        return send_from_directory(CSV_DIRECTORY, filename)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
