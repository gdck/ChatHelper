import os
import subprocess
import shutil
import sys

def build():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(base_dir, "frontend")
    dist_dir = os.path.join(frontend_dir, "dist")

    print("[1/3] 构建 Vue 3 前端静态资源...")
    cmd_build = "npm.cmd run build" if sys.platform == "win32" else "npm run build"
    subprocess.run(cmd_build, shell=True, cwd=frontend_dir, check=True)

    if not os.path.exists(os.path.join(dist_dir, "index.html")):
        raise FileNotFoundError("前端构建产物未找到！")
    print("前端构建产物检查通过！")

    print("[2/3] 清理旧构建目录...")
    for folder in ["build", "dist"]:
        p = os.path.join(base_dir, folder)
        if os.path.exists(p):
            shutil.rmtree(p, ignore_errors=True)

    print("[3/3] 运行 PyInstaller 生成便携绿色包...")
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconsole",
        "--onedir",
        "--name=ChatHelper",
        f"--add-data={dist_dir};frontend/dist",
        "--clean",
        "-y",
        os.path.join(base_dir, "src", "main.py")
    ]
    subprocess.run(cmd, cwd=base_dir, check=True)
    print("==========================================")
    print("🎉 打包成功！输出绿色版路径：dist/ChatHelper/ChatHelper.exe")
    print("==========================================")

if __name__ == "__main__":
    build()
