import pystray
from PIL import Image, ImageDraw
import threading

def create_default_icon():
    # 创建高质量 64x64 绿色微信聊天气泡托盘图标
    image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((2, 2, 62, 62), fill=(7, 193, 96, 255))
    # 居中白色对话气泡
    draw.rounded_rectangle((14, 16, 50, 42), radius=6, fill="white")
    draw.polygon([(20, 42), (20, 50), (28, 42)], fill="white")
    return image

class TrayManager:
    def __init__(self, on_toggle=None, on_exit=None):
        self.on_toggle = on_toggle
        self.on_exit = on_exit
        self.icon = None

    def start(self):
        menu = pystray.Menu(
            pystray.MenuItem("显示/收起助手", self.on_toggle, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("退出", self.on_exit)
        )
        self.icon = pystray.Icon("ChatHelper", create_default_icon(), "微信聊天助手", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()

    def stop(self):
        if self.icon:
            try:
                self.icon.stop()
            except Exception:
                pass
