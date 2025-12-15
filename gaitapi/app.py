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

# static 放你的 index.html（可有可無）
app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "static"))
CORS(app, resources={r"/*": {"origins": "*"}})

# 你的 ipynb 路徑（跟 app.py 同層）
NOTEBOOK_PATH = os.path.join(BASE_DIR, "力版修正最終(加上LLRR) - 表演+衰弱辨識.ipynb")

# 報告輸出資料夾
REPORT_DIR = os.path.join(BASE_DIR, "generated_reports")
os.makedirs(REPORT_DIR, exist_ok=True)

# 上傳暫存資料夾
UPLOAD_DIR = os.path.join(REPORT_DIR, "_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ========== 工具函式 ==========

def _safe_basename(filename: str) -> str:
    """把上傳檔名轉成安全檔名"""
    name = os.path.splitext(os.path.basename(filename))[0]
    name = re.sub(r"[^\w\u4e00-\u9fff\- ]+", "_", name)
    name = name.strip().replace(" ", "_")
    return name or "report"


def ensure_python3_kernel():
    """
    Render 環境常見：有 ipykernel 但沒有 kernelspec => 會出現 No such kernel named python3
    這裡在啟動時自動補裝 kernelspec。
    """
    try:
        from jupyter_client.kernelspec import KernelSpecManager
        ksm = KernelSpecManager()
        specs = ksm.find_kernel_specs()  # dict
        if "python3" in specs:
            return

        # 沒有 python3 kernel -> 安裝
        subprocess.check_call([
            sys.executable, "-m", "ipykernel", "install",
            "--user",
            "--name", "python3",
            "--display-name", "Python 3"
        ])
    except Exception as e:
        # 就算失敗也先讓程式跑起來，之後 /run 才會報錯比較明確
        print("⚠️ ensure_python3_kernel failed:", repr(e))


def sanitize_notebook_for_server(nb):
    """
    伺服器環境不能用 %matplotlib widget
    - 把 '%matplotlib widget' / '%matplotlib' 改成 Agg
    - 移除所有以 % 或 ! 開頭的魔法指令行
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

            # 取代 matplotlib widget
            if stripped.startswith("%matplotlib"):
                if not inserted_agg:
                    new_lines.append("import matplotlib")
                    new_lines.append("matplotlib.use('Agg')  # server/headless")
                    inserted_agg = True
                continue

            # 移除其他魔法指令
            if stripped.startswith("%") or stripped.startswith("!"):
                continue

            new_lines.append(line)

        cell["source"] = "\n".join(new_lines)

    return nb


def run_notebook_with_json(json_path: str, base_name: str) -> str:
    """執行 ipynb 並生成 PDF，回傳 pdf 檔名"""
    if not os.path.exists(NOTEBOOK_PATH):
        raise RuntimeError(f"❗找不到 Notebook：{NOTEBOOK_PATH}")

    nb = nbformat.read(NOTEBOOK_PATH, as_version=4)
    nb = sanitize_notebook_for_server(nb)

    pdf_filename = f"{base_name}.pdf"
    pdf_path = os.path.join(REPORT_DIR, pdf_filename)

    # 每次執行都用新的 env
    exec_env = os.environ.copy()
    exec_env["INPUT_JSON"] = json_path
    exec_env["OUTPUT_DIR"] = REPORT_DIR
    exec_env["RESULT_PDF"] = pdf_path

    # ✅ 這裡一定要能找到 python3 kernel
    client = NotebookClient(
        nb,
        timeout=900,
        kernel_name="python3",
        env=exec_env
    )
    client.execute()

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Notebook 跑完沒有找到 PDF：{pdf_path}")

    return pdf_filename


# ========== Routes ==========

@app.get("/")
def index():
    # 你想讓後端也能顯示 UI，就放 static/index.html
    static_index = os.path.join(app.static_folder, "index.html")
    if os.path.exists(static_index):
        return app.send_static_file("index.html")
    return "OK: gait-report-api is running"


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
        # 不想刪就註解掉
        if os.path.exists(json_path):
            os.remove(json_path)

    pdf_url = url_for("download_report", filename=pdf_filename, _external=True)
    return jsonify({"pdf_url": pdf_url})


@app.get("/report/<path:filename>")
def download_report(filename):
    return send_from_directory(REPORT_DIR, filename, mimetype="application/pdf")


# ========== 啟動前處理 ==========
ensure_python3_kernel()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
