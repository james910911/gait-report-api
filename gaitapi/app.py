from flask import Flask, request, jsonify, send_from_directory, url_for
from flask_cors import CORS
import os
import re
import tempfile
import nbformat
from nbclient import NotebookClient

app = Flask(__name__, static_folder="static")

# 讓 GitHub Pages / 其他網域可以呼叫你的 API
CORS(app)

# 你的 ipynb 路徑（跟 app.py 同層）
NOTEBOOK_PATH = os.path.abspath("./力版修正最終(加上LLRR) - 表演+衰弱辨識.ipynb")
if not os.path.exists(NOTEBOOK_PATH):
    raise RuntimeError(f"❗找不到 Notebook：{NOTEBOOK_PATH}")

# 報告輸出資料夾（自動建立，不再要你手動建）
REPORT_DIR = os.path.abspath("./generated_reports")
os.makedirs(REPORT_DIR, exist_ok=True)

# 上傳暫存資料夾（避免用系統 tmp，讓你看得到）
UPLOAD_DIR = os.path.join(REPORT_DIR, "_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.route("/")
def index():
    # 你如果要讓這個 API 也能直接打開 UI，就保留
    return app.send_static_file("index.html")


def _safe_basename(filename: str) -> str:
    """
    把上傳檔名轉成安全的檔名（去掉路徑、特殊字元）
    例如：'../a.json' -> 'a'
    """
    name = os.path.splitext(os.path.basename(filename))[0]
    name = re.sub(r"[^\w\u4e00-\u9fff\- ]+", "_", name)  # 允許中文/英數/底線/減號/空白
    name = name.strip().replace(" ", "_")
    return name or "report"


def run_notebook_with_json(json_path: str, base_name: str) -> str:
    """執行 ipynb 並生成 PDF，回傳 pdf 檔名（存在 generated_reports 裡）"""
    nb = nbformat.read(NOTEBOOK_PATH, as_version=4)

    # ✅ PDF 檔名要跟 JSON 檔名一樣
    pdf_filename = f"{base_name}.pdf"
    pdf_path = os.path.join(REPORT_DIR, pdf_filename)

    # 每次執行都用「新的 env」，避免多請求互相污染
    exec_env = os.environ.copy()
    exec_env["INPUT_JSON"] = json_path
    exec_env["OUTPUT_DIR"] = REPORT_DIR
    exec_env["RESULT_PDF"] = pdf_path

    client = NotebookClient(nb, timeout=600, kernel_name="python3", env=exec_env)
    client.execute()

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Notebook 執行後沒有找到 PDF：{pdf_path}")

    return pdf_filename


@app.route("/run", methods=["POST"])
def run_analysis():
    if "file" not in request.files:
        return jsonify({"error": "沒有收到檔案（欄位名稱必須是 file）"}), 400

    up = request.files["file"]
    if not up.filename:
        return jsonify({"error": "檔案名稱無效"}), 400

    # ✅ 只接受 .json
    if not up.filename.lower().endswith(".json"):
        return jsonify({"error": "只接受 .json 檔案"}), 400

    base_name = _safe_basename(up.filename)

    # ✅ 不用系統 tmp，改存到 generated_reports/_uploads
    json_path = os.path.join(UPLOAD_DIR, f"{base_name}.json")
    up.save(json_path)

    try:
        pdf_filename = run_notebook_with_json(json_path, base_name)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # 產完就刪掉上傳 json（你要保留也可以把這段註解）
        if os.path.exists(json_path):
            os.remove(json_path)

    # 產生可讓前端點開的 PDF 連結（絕對 URL）
    pdf_url = url_for("download_report", filename=pdf_filename, _external=True)
    return jsonify({"pdf_url": pdf_url})


@app.route("/report/<path:filename>")
def download_report(filename):
    # ✅ 只從 generated_reports 送出
    return send_from_directory(REPORT_DIR, filename, mimetype="application/pdf")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
