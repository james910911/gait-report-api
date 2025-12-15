from flask import Flask, request, jsonify, send_from_directory, url_for
from flask_cors import CORS
import os
import re
import sys
import subprocess
import nbformat
from nbclient import NotebookClient

# ========== 基本設定 ==========
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "static"))

# ✅ CORS：讓 GitHub Pages / 任何網域都能打（先全開，穩定後再收斂）
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=False,
    allow_headers=["Content-Type"],
    methods=["GET", "POST", "OPTIONS"],
)

NOTEBOOK_PATH = os.path.join(BASE_DIR, "力版修正最終(加上LLRR) - 表演+衰弱辨識.ipynb")

REPORT_DIR = os.path.join(BASE_DIR, "generated_reports")
os.makedirs(REPORT_DIR, exist_ok=True)

UPLOAD_DIR = os.path.join(REPORT_DIR, "_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ========== 工具函式 ==========
def _safe_basename(filename: str) -> str:
    name = os.path.splitext(os.path.basename(filename))[0]
    name = re.sub(r"[^\w\u4e00-\u9fff\- ]+", "_", name)
    name = name.strip().replace(" ", "_")
    return name or "report"


def ensure_python3_kernel():
    """
    可留著：Render 環境常見有 ipykernel 但沒 kernelspec。
    但就算失敗也不會阻止服務啟動。
    """
    try:
        from jupyter_client.kernelspec import KernelSpecManager
        ksm = KernelSpecManager()
        specs = ksm.find_kernel_specs()
        if "python3" in specs:
            return

        subprocess.check_call([
            sys.executable, "-m", "ipykernel", "install",
            "--user", "--name", "python3", "--display-name", "Python 3"
        ])
    except Exception as e:
        print("⚠️ ensure_python3_kernel failed:", repr(e))


def sanitize_notebook_for_server(nb):
    """
    ✅ Render/伺服器是 headless，不能用 %matplotlib widget
    - 任何 %matplotlib... 一律改成 Agg
    - 移除其他以 % 或 ! 開頭的魔法指令
    """
    for cell in nb.cells:
        if cell.get("cell_type") != "code":
            continue

        src = cell.get("source", "")
        if not src:
            continue

        lines = src.splitlines()
        new_lines = []
        inserted_agg = False

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("%matplotlib"):
                if not inserted_agg:
                    new_lines.append("import matplotlib")
                    new_lines.append("matplotlib.use('Agg')  # server/headless")
                    inserted_agg = True
                continue

            if stripped.startswith("%") or stripped.startswith("!"):
                continue

            new_lines.append(line)

        cell["source"] = "\n".join(new_lines)

    return nb


def run_notebook_with_json(json_path: str, base_name: str) -> str:
    if not os.path.exists(NOTEBOOK_PATH):
        raise RuntimeError(f"❗找不到 Notebook：{NOTEBOOK_PATH}")

    nb = nbformat.read(NOTEBOOK_PATH, as_version=4)
    nb = sanitize_notebook_for_server(nb)

    pdf_filename = f"{base_name}.pdf"
    pdf_path = os.path.join(REPORT_DIR, pdf_filename)

    exec_env = os.environ.copy()
    exec_env["INPUT_JSON"] = json_path
    exec_env["OUTPUT_DIR"] = REPORT_DIR
    exec_env["RESULT_PDF"] = pdf_path

    # ✅ 最穩：不指定 kernel_name（避免 No such kernel）
    client = NotebookClient(nb, timeout=900, env=exec_env)
    client.execute()

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Notebook 跑完沒有找到 PDF：{pdf_path}")

    return pdf_filename


# ========== Routes ==========
@app.get("/")
def health():
    # 你有放 static/index.html 就顯示 UI；沒有就顯示健康檢查
    static_index = os.path.join(app.static_folder, "index.html")
    if os.path.exists(static_index):
        return app.send_static_file("index.html")
    return "OK: gait-report-api is running", 200


@app.post("/run")
def run_analysis():
    if "file" not in request.files:
        return jsonify({"error": "沒有收到檔案（欄位名稱必須是 file）"}), 400

    up = request.files["file"]
    if not up.filename:
        return jsonify({"error": "檔案名稱無效"}), 400

    if not up.filename.lower().endswith(".json"):
        return jsonify({"error": "只接受 .json 檔案"}), 400

    base_name = _safe_basename(up.filename)
    json_path = os.path.join(UPLOAD_DIR, f"{base_name}.json")
    up.save(json_path)

    try:
        pdf_filename = run_notebook_with_json(json_path, base_name)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(json_path):
            os.remove(json_path)

    # ✅ 回傳「完整網址」給前端（前端不要再拼 BACKEND_URL）
    pdf_url = url_for("download_report", filename=pdf_filename, _external=True)
    return jsonify({"pdf_url": pdf_url}), 200


@app.get("/report/<path:filename>")
def download_report(filename):
    return send_from_directory(REPORT_DIR, filename, mimetype="application/pdf")


# ========== 啟動前處理 ==========
ensure_python3_kernel()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
