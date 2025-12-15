from flask import Flask, request, jsonify, send_from_directory, url_for
from flask_cors import CORS
import os
import tempfile
import nbformat
from nbclient import NotebookClient

# =========================================================
# 基本設定
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# static 放前端：gaitapi/static/index.html
app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "static"))
CORS(app, resources={r"/*": {"origins": "*"}})  # 保險：就算前後端不同網域也能 call

# 你的 ipynb 檔放在哪裡（相對於 gaitapi/）
NOTEBOOK_PATH = os.path.join(BASE_DIR, "力版修正最終(加上LLRR) - 表演+衰弱辨識.ipynb")

# PDF 輸出資料夾（相對於 gaitapi/）
REPORT_DIR = os.path.join(BASE_DIR, "generated_reports")
os.makedirs(REPORT_DIR, exist_ok=True)


@app.route("/")
def index():
    # 會回傳 gaitapi/static/index.html
    return app.send_static_file("index.html")


def run_notebook_with_json(json_path: str, base_name: str) -> str:
    """執行 ipynb 並生成 PDF，回傳 pdf 檔名"""
    if not os.path.exists(NOTEBOOK_PATH):
        raise FileNotFoundError(f"找不到 Notebook：{NOTEBOOK_PATH}")

    nb = nbformat.read(NOTEBOOK_PATH, as_version=4)

    pdf_filename = f"{base_name}_gait_report.pdf"
    pdf_path = os.path.join(REPORT_DIR, pdf_filename)

    # 注入給 notebook 用的環境變數（你 notebook 內要用 os.environ.get 讀）
    os.environ["INPUT_JSON"] = json_path
    os.environ["RESULT_PDF"] = pdf_path
    os.environ["OUTPUT_DIR"] = REPORT_DIR

    # 執行 notebook
    client = NotebookClient(nb, timeout=900)
    client.execute()

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Notebook 跑完沒有找到 PDF：{pdf_path}")

    return pdf_filename


@app.route("/run", methods=["POST"])
def run_analysis():
    if "file" not in request.files:
        return jsonify({"error": "沒有收到檔案（欄位名稱要是 file）"}), 400

    f = request.files["file"]
    if not f or f.filename == "":
        return jsonify({"error": "檔案名稱無效"}), 400

    if not f.filename.lower().endswith(".json"):
        return jsonify({"error": "請上傳 .json 檔"}), 400

    base_name = os.path.splitext(os.path.basename(f.filename))[0]

    # 存成暫存檔
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
            f.save(tmp.name)
            tmp_path = tmp.name

        pdf_filename = run_notebook_with_json(tmp_path, base_name)

        # 回傳可下載 PDF 的網址（前端用 data.pdf_url 直接打開即可）
        pdf_url = url_for("download_report", filename=pdf_filename, _external=False)
        return jsonify({"pdf_url": pdf_url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.route("/report/<path:filename>")
def download_report(filename):
    return send_from_directory(REPORT_DIR, filename, mimetype="application/pdf")


if __name__ == "__main__":
    # Render 會給 PORT，必須綁 0.0.0.0
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)

