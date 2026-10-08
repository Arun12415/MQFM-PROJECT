"""
pipeline/schemas.py — Document Type Registry
------------------------------------------------
Every supported form/report type is defined ONCE here: its display name,
its fields (with human labels for the UI/Excel), which fields are
required, and whether one upload produces a single record or a whole
table of rows.

TO ADD A NEW DOCUMENT FORMAT LATER:
  1. Copy one of the dicts below.
  2. Change the key, label, sheet_name, and fields/labels/required.
  3. That's it — the upload UI, AI prompt, validation, and Excel export
     all pick it up automatically. No other file needs to change.
"""

DOCUMENT_TYPES = {

    "production_shift": {
        "label": "Production Shift Sheet",
        "sheet_name": "Production Shift",
        "row_mode": "single",  # one record per uploaded document
        "fields": [
            "date", "shift", "heat_no", "production_qty", "temperature",
            "png_consumption", "operator", "remarks",
        ],
        "labels": {
            "date": "Date", "shift": "Shift", "heat_no": "Heat No.",
            "production_qty": "Production Qty", "temperature": "Temperature",
            "png_consumption": "PNG Consumption", "operator": "Operator",
            "remarks": "Remarks",
        },
        "required": ["date", "shift", "heat_no", "production_qty", "temperature", "png_consumption", "operator"],
        "demo_rows": [{
            "date": "11-09-2026", "shift": "B (2:00 PM - 10:00 PM)", "heat_no": "HT-4821",
            "production_qty": "18.6 MT", "temperature": "1420 C", "png_consumption": "312 SCM",
            "operator": "R. Mehta", "remarks": "Minor delay - furnace relining, 20 min",
        }],
    },

    "inspection_report": {
        "label": "Inspection Report of Rolled Products",
        "sheet_name": "Inspection Report",
        "row_mode": "multi",  # one table row per row on the physical sheet
        "fields": [
            "h_no", "grade", "size_mm", "dimension_mm", "b_no", "total_cut_pcs",
            "fl_length_mtr", "total_inspected_pcs", "fin", "scale", "ovality",
            "hook_bend", "s_line", "lc", "miss_roll", "size_out", "dc", "sl",
            "flo", "ut", "mixup_found", "ok_pcs", "not_ok_pcs",
            "defect_type_not_ok", "total_rejected_pcs", "total_ok_pcs",
            "rej_cutting_length_mtr", "end_color_code", "uid", "job_no",
        ],
        "labels": {
            "h_no": "H.No.", "grade": "Grade", "size_mm": "Size (mm)",
            "dimension_mm": "Dimension (mm)", "b_no": "B.No.",
            "total_cut_pcs": "Total Cut Pcs.", "fl_length_mtr": "F.L. (Mtr) Pcs.",
            "total_inspected_pcs": "Total Inspected Pcs.", "fin": "FIN",
            "scale": "Scale", "ovality": "Ovality", "hook_bend": "Hook Bend",
            "s_line": "S.Line", "lc": "L.C", "miss_roll": "Miss Roll",
            "size_out": "Size out", "dc": "D.C", "sl": "S/L", "flo": "FL/O",
            "ut": "UT", "mixup_found": "Mix-up found (Yes/No)", "ok_pcs": "OK",
            "not_ok_pcs": "Not OK", "defect_type_not_ok": "Defect Type for Not OK Pcs.",
            "total_rejected_pcs": "Total Rejected Pcs.", "total_ok_pcs": "Total OK Pcs.",
            "rej_cutting_length_mtr": "Rej. Cutting Length (Mtr)",
            "end_color_code": "End Color Code (Yes/No)", "uid": "UID", "job_no": "Job No.",
        },
        "required": ["h_no", "grade", "size_mm"],
        "demo_rows": [
            {"h_no": "23056", "grade": "303", "size_mm": "12.7", "dimension_mm": "24.4X24.4X2.3",
             "b_no": "7304", "total_cut_pcs": "99", "fl_length_mtr": "99", "total_inspected_pcs": "99",
             "fin": "", "scale": "", "ovality": "", "hook_bend": "", "s_line": "", "lc": "",
             "miss_roll": "", "size_out": "", "dc": "", "sl": "", "flo": "", "ut": "",
             "mixup_found": "No", "ok_pcs": "99", "not_ok_pcs": "0", "defect_type_not_ok": "",
             "total_rejected_pcs": "0", "total_ok_pcs": "99", "rej_cutting_length_mtr": "0",
             "end_color_code": "Yes", "uid": "R0241R2", "job_no": "MFLJ"},
        ],
    },

    "section_size_report": {
        "label": "Section Size Report",
        "sheet_name": "Section Size",
        "row_mode": "multi",
        "fields": [
            "time_hrs", "qcr_no", "size_mm", "heat_no", "grade",
            "top_mm", "bot_mm", "sh_a_mm", "sh_b_mm", "ovality_mm",
            "etching_result", "observation", "mill_inspector_sign", "mill_fitter_sign",
        ],
        "labels": {
            "time_hrs": "Time (Hrs)", "qcr_no": "QCR No.", "size_mm": "Size (mm)",
            "heat_no": "Heat No.", "grade": "Grade", "top_mm": "Top (mm)",
            "bot_mm": "Bot. (mm)", "sh_a_mm": "SH.A (mm)", "sh_b_mm": "SH.B (mm)",
            "ovality_mm": "Ovality (mm)", "etching_result": "Etching Result",
            "observation": "Observation", "mill_inspector_sign": "Mill Inspector Sign",
            "mill_fitter_sign": "Mill Fitter Sign",
        },
        "required": ["qcr_no", "heat_no", "grade"],
        "demo_rows": [
            {"time_hrs": "07:15", "qcr_no": "4895", "size_mm": "80RC1", "heat_no": "00",
             "grade": "SA105", "top_mm": "80.60", "bot_mm": "80.70", "sh_a_mm": "104.70",
             "sh_b_mm": "105.50", "ovality_mm": "-", "etching_result": "-",
             "observation": "-", "mill_inspector_sign": "M", "mill_fitter_sign": ""},
        ],
    },

}


def get_type(doc_type: str) -> dict:
    return DOCUMENT_TYPES.get(doc_type, DOCUMENT_TYPES["production_shift"])


def list_types():
    """Returns [(key, label), ...] for populating the upload dropdown."""
    return [(key, meta["label"]) for key, meta in DOCUMENT_TYPES.items()]
