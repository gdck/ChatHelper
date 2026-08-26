import os
import subprocess
import shutil
import sys

def build():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(base_dir, "frontend")
    dist_dir = os.path.join(frontend_dir, "dist")

    print("[1/4] 终止正在运行的旧实例（如有）...")
    if sys.platform == "win32":
        subprocess.run("taskkill /f /im ChatHelper.exe 2>nul", shell=True)

    print("[2/4] 构建 Vue 3 前端静态资源...")
    cmd_build = "npm.cmd run build" if sys.platform == "win32" else "npm run build"
    subprocess.run(cmd_build, shell=True, cwd=frontend_dir, check=True)

    if not os.path.exists(os.path.join(dist_dir, "index.html")):
        raise FileNotFoundError("前端构建产物未找到！")
    print("前端构建产物检查通过！")

    print("[3/4] 清理旧构建目录...")
    for folder in ["build", "dist"]:
        p = os.path.join(base_dir, folder)
        if os.path.exists(p):
            try:
                shutil.rmtree(p)
            except Exception as e:
                print(f"提示: 清理 {folder} 遇到异常: {e}")

    print("[4/4] 运行 PyInstaller 生成单文件独立可执行程序 (--onefile --uac-admin)...")
    
    # 极简依赖剪裁：彻底移除 sqlite3、Pillow、pystray、Qt、科学计算等庞大模块
    # 注意：保留 pywebview 必需的标准库模块（如 http、email 等）
    exclude_modules = [
        "sqlite3", "_sqlite3",
        "PIL", "Pillow", "pystray",
        "PyQt6", "PyQt5", "PySide6", "PySide2", "qtpy",
        "numpy", "scipy", "pandas", "matplotlib", "pygments", "jinja2", "mako",
        "tkinter", "_tkinter", "tcl", "tk",
        "unittest", "pytest", "pydoc", "doctest", "difflib", "test",
        "xmlrpc", "curses",
        "cryptography", "IPython", "jupyter", "torch"
    ]
    
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconsole",
        "--onefile",
        "--uac-admin", # 默认以管理员权限运行（UAC 盾牌提权标记）
        "--name=ChatHelper",
        f"--add-data={dist_dir};frontend/dist",
        "--hidden-import=pythonnet",
        "--hidden-import=clr_loader",
        "--hidden-import=webview.platforms.winforms",
        "--clean",
        "-y",
        os.path.join(base_dir, "src", "main.py")
    ]
    
    for mod in exclude_modules:
        cmd.extend(["--exclude-module", mod])

    subprocess.run(cmd, cwd=base_dir, check=True)
    
    exe_path = os.path.join(base_dir, "dist", "ChatHelper.exe")
    size_mb = os.path.getsize(exe_path) / (1024 * 1024) if os.path.exists(exe_path) else 0

    print("==========================================")
    print(f"[SUCCESS] 超精简单文件（管理员权限）打包完成！")
    print(f"产物路径: {exe_path}")
    print(f"文件大小: {size_mb:.2f} MB")
    print("==========================================")

if __name__ == "__main__":
    build()
