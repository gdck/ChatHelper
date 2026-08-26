import pystray
from PIL import Image, ImageDraw
import threading

def create_default_icon():
    image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((4, 4, 60, 60), fill=(7, 193, 96, 255))
    draw.text((18, 20), "WX", fill="white")
    return image

class TrayManager:
    def __init__(self, on_toggle=None, on_exit=None):
        self.on_toggle = on_toggle
        self.on_exit = on_exit
        self.icon = None

    def start(self):
        menu = pystray.Menu(
            pystray.MenuItem("显示/隐藏助手", self.on_toggle, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("退出", self.on_exit)
        )
        self.icon = pystray.Icon("ChatHelper", create_default_icon(), "微信聊天助手", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()

    def stop(self):
        if self.icon:
            self.icon.stop()
