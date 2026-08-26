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

    print("[4/4] 运行 PyInstaller 生成单文件独立可执行程序 (--onefile)...")
    
    # 排除庞大的无用依赖（PyQt6 488MB、numpy 26MB、cryptography 等）
    exclude_modules = [
        "PyQt6", "PyQt5", "PySide6", "PySide2",
        "numpy", "scipy", "pandas", "matplotlib",
        "cryptography", "tkinter", "pytest", "unittest",
        "IPython", "jupyter", "torch", "setuptools"
    ]
    
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name=ChatHelper",
        f"--add-data={dist_dir};frontend/dist",
        "--hidden-import=win32clipboard",
        "--hidden-import=win32con",
        "--hidden-import=pystray",
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
    print(f"[SUCCESS] 单文件打包完成！")
    print(f"产物路径: {exe_path}")
    print(f"文件大小: {size_mb:.2f} MB")
    print("==========================================")

if __name__ == "__main__":
    build()
