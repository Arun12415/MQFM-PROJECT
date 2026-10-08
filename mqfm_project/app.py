"""
app.py — MQFM Web App entry point
------------------------------------
Routing only. Actual logic lives in pipeline/ (schemas, extract, validate,
generate_excel) and templates/ + static/ (frontend).

Run:
    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=sk-ant-...      # for Claude, OR
    export GOOGLE_API_KEY=AQ...              # for Gemini (either works; omit both for demo mode)
    python3 app.py
    open http://localhost:5000

To add a new document format later: edit pipeline/schemas.py only.
"""
import os
import traceback

from flask import Flask, request, jsonify, send_file, render_template

from pipeline import config
from pipeline.schemas import list_types, get_type
from pipeline.extract import extract
from pipeline.validate import validate_rows
from pipeline.generate_excel import append_rows

app = Flask(__name__)


@app.route("/")
def index():
    return render_template(
        "index.html",
        has_key=config.HAS_API_KEY,
        provider=config.AI_PROVIDER,
        doc_types=list_types(),
    )


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("document")
    doc_type = request.form.get("doc_type", "production_shift")

    if not file or file.filename == "":
        return jsonify({"error": "Please choose an image file."}), 400
    if doc_type not in dict(list_types()):
        return jsonify({"error": f"Unknown document type: {doc_type}"}), 400

    save_path = os.path.join(config.UPLOAD_DIR, file.filename)
    file.save(save_path)

    try:
        extracted_rows = extract(save_path, doc_type)
        validated_rows = validate_rows(extracted_rows, doc_type)
        for row in validated_rows:
            row["source_document_id"] = file.filename
        append_rows(config.OUTPUT_XLSX, doc_type, validated_rows)

        schema = get_type(doc_type)
        overall_status = "PASSED" if all(r["validation_status"] == "PASSED" for r in validated_rows) else "FAILED"
        return jsonify({
            "doc_type": doc_type,
            "doc_label": schema["label"],
            "labels": schema["labels"],
            "fields": schema["fields"],
            "rows": validated_rows,
            "row_count": len(validated_rows),
            "overall_status": overall_status,
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/download")
def download():
    if not os.path.exists(config.OUTPUT_XLSX):
        return jsonify({"error": "No Excel log generated yet."}), 404
    return send_file(config.OUTPUT_XLSX, as_attachment=True, download_name="production_log.xlsx")


if __name__ == "__main__":
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", 5000))
    app.run(host=HOST, port=PORT, debug=os.environ.get("DEBUG", "1") == "1")
