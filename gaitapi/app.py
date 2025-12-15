from flask import Flask, request, jsonify, send_from_directory, url_for
import os
import tempfile
import nbformat
from nbclient import NotebookClient

app = Flask(__name__, static_folder="static")

# 你的 ipynb 路徑
NOTEBOOK_PATH = os.path.abspath("./力版修正最終(加上LLRR) - 表演+衰弱辨識.ipynb")

# 你會手動建立的資料夾（我們不再自動建立）
REPORT_DIR = os.path.abspath("./generated_reports")
if not os.path.exists(REPORT_DIR):
    raise RuntimeError("❗ generated_reports 資料夾不存在，請手動建立後再執行。")


@app.route("/")
def index():
    return app.send_static_file("index.html")


def run_notebook_with_json(json_path: str, base_name: str) -> str:
    """執行 ipynb 並生成 PDF"""
    nb = nbformat.read(NOTEBOOK_PATH, as_version=4)

    # 固定 PDF 存在 generated_reports 裡
    pdf_filename = f"{base_name}_gait_report.pdf"
    pdf_path = os.path.join(REPORT_DIR, pdf_filename)

    # 注入給 notebook 的環境變數
    os.environ["INPUT_JSON"] = json_path
    os.environ["RESULT_PDF"] = pdf_path      # 告訴 Notebook 要輸出在哪
    os.environ["OUTPUT_DIR"] = REPORT_DIR    # 仍然提供，但 Notebook 不會建資料夾

    client = NotebookClient(nb, timeout=600, kernel_name="python3")
    client.execute()

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Notebook 執行後沒有找到 PDF：{pdf_path}")

    return pdf_filename


@app.route("/run", methods=["POST"])
def run_analysis():
    if "file" not in request.files:
        return jsonify({"error": "沒有收到檔案"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "檔案名稱無效"}), 400

    # 儲存上傳 JSON 為暫存檔
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        file.save(tmp.name)
        json_path = tmp.name

    base_name = os.path.splitext(file.filename)[0]

    try:
        pdf_filename = run_notebook_with_json(json_path, base_name)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(json_path):
            os.remove(json_path)

    pdf_url = url_for("download_report", filename=pdf_filename)
    return jsonify({"pdf_url": pdf_url})


@app.route("/report/<path:filename>")
def download_report(filename):
    return send_from_directory(REPORT_DIR, filename, mimetype="application/pdf")


if __name__ == "__main__":
    app.run(debug=True)
