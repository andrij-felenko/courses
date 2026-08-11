import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../scripts')))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def render_svg():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    
    frags = [
        # Ліва частина (PID)
        rect(50, 80, 300, 80, fill="#ffcccc", stroke="#cc0000", sw=2),
        text(200, 110, "Процес A", size=16),
        text(200, 135, "kill(PID 1234)", size=14, color="#cc0000"),
        
        arrow(200, 160, 200, 240, color="#000", sw=2),
        text(200, 200, "PID 1234 перепризначено", size=12, color="#555"),
        
        rect(50, 240, 300, 80, fill="#e6f2ff", stroke="#0066cc", sw=2),
        text(200, 270, "Новий Процес C (PID 1234)", size=16),
        text(200, 295, "Отримує помилковий сигнал!", size=14, color="#cc0000"),
        
        # Права частина (PIDFD)
        rect(450, 80, 300, 80, fill="#ccffcc", stroke="#009900", sw=2),
        text(600, 110, "Процес A", size=16),
        text(600, 135, "pidfd_send_signal(fd)", size=14, color="#009900"),
        
        arrow(600, 160, 600, 240, color="#000", sw=2),
        text(600, 200, "Процес B завершено", size=12, color="#555"),
        
        rect(450, 240, 300, 80, fill="#f2f2f2", stroke="#999999", sw=2),
        text(600, 270, "Мертвий об'єкт struct pid", size=16, color="#666"),
        text(600, 295, "ESRCH (помилка, безпечно)", size=14, color="#009900"),
        
        # Розділювач
        line(400, 20, 400, 380, color="#ccc", sw=2, dash="4,4"),
        
        # Заголовки
        text(200, 40, "Проблема PID Recycling", size=20, bold=True),
        text(600, 40, "Рішення з pidfd / pidfs", size=20, bold=True)
    ]
    
    render(os.path.join(out_dir, "pidfs-architecture.svg"), 800, 400, *frags)

if __name__ == '__main__':
    render_svg()
