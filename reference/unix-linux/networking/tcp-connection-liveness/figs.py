import sys
import os
import glob

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))

from svgkit import render, textbox, fitbox, rect, text, line, arrow, circle, POS, NEG, FIELD, INK, MUTED, LINE, FILL

def generate_keepalive_sequence(img_dir):
    path = os.path.join(img_dir, 'keepalive-sequence.svg')
    w, h = 860, 440
    
    frags = []
    
    # Заголовок фігури
    frags.append(text(w / 2, 28, "Хронологія зондування TCP Keepalive при обриві зв'язку", size=16, bold=True))
    
    # Хости
    b1, _, _ = textbox(180, 70, "Клієнт (Host A)\nЯдро Linux", size=13, fill="#e8f4f8", stroke="#2980b9")
    b2, _, _ = textbox(720, 70, "Сервер (Host B)\nЗбій / Обрив", size=13, fill="#fdeaea", stroke="#c0392b")
    frags.extend([b1, b2])
    
    # Вертикальні лінії життя
    frags.append(line(180, 95, 180, 390, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(line(720, 95, 720, 260, color=MUTED, sw=1.5, dash="4,4"))
    
    # Збій на сервері (хрестик)
    frags.append(line(710, 255, 730, 275, color=POS, sw=3))
    frags.append(line(730, 255, 710, 275, color=POS, sw=3))
    frags.append(text(745, 268, "Обрив / Crash", size=12, color=POS, bold=True, anchor="start"))
    
    # Останній пакет даних
    frags.append(arrow(180, 120, 720, 120, color=FIELD, sw=2))
    frags.append(text(450, 112, "Останній ACK / Дані", size=12, color=FIELD, bold=True))
    
    # Інтервал TCP_KEEPIDLE (зліва від життя)
    frags.append(line(150, 120, 150, 210, color="#2980b9", sw=2))
    frags.append(line(145, 120, 155, 120, color="#2980b9", sw=2))
    frags.append(line(145, 210, 155, 210, color="#2980b9", sw=2))
    frags.append(text(140, 160, "TCP_KEEPIDLE", size=11, color="#2980b9", bold=True, anchor="end"))
    frags.append(text(140, 175, "(простой, 60 с)", size=10, color=MUTED, anchor="end"))
    
    # Перший зонд
    frags.append(arrow(180, 210, 715, 210, color="#e67e22", sw=1.8))
    frags.append(text(450, 202, "Probe 1: ACK (SEQ = snd_una - 1)", size=11, color="#e67e22"))
    
    # Ніхто не відповідає на Probe 1
    frags.append(circle(720, 210, 4, fill=POS, stroke=POS))
    
    # Інтервал TCP_KEEPINTVL
    frags.append(line(150, 210, 150, 270, color="#8e44ad", sw=2))
    frags.append(line(145, 210, 155, 210, color="#8e44ad", sw=2))
    frags.append(line(145, 270, 155, 270, color="#8e44ad", sw=2))
    frags.append(text(140, 235, "TCP_KEEPINTVL", size=11, color="#8e44ad", bold=True, anchor="end"))
    frags.append(text(140, 250, "(інтервал, 10 с)", size=10, color=MUTED, anchor="end"))
    
    # Другий зонд
    frags.append(arrow(180, 270, 715, 270, color="#e67e22", sw=1.8))
    frags.append(text(450, 262, "Probe 2: ACK (SEQ = snd_una - 1)", size=11, color="#e67e22"))
    
    # Повторні спроби до TCP_KEEPCNT
    frags.append(text(450, 310, "• • •  Повторення N спроб (TCP_KEEPCNT)  • • •", size=12, color=MUTED, bold=True))
    
    # Останній зонд N
    frags.append(arrow(180, 340, 715, 340, color="#e67e22", sw=1.8))
    frags.append(text(450, 332, "Probe N (останній зонд)", size=11, color="#e67e22"))
    
    # Таймаут та розрив
    tb, _, _ = textbox(180, 390, "Помилка: ETIMEDOUT / ECONNRESET\nСокет закривається в ядрі", size=12, fill="#fdeaea", stroke=POS, bold=True)
    frags.append(tb)
    
    render(path, w, h, *frags)
    print(f"Generated {path}")

def generate_liveness_mechanisms(img_dir):
    path = os.path.join(img_dir, 'liveness-mechanisms.svg')
    w, h = 840, 380
    
    frags = []
    
    frags.append(text(w / 2, 28, "Рівні виявлення мертвих з'єднань у стеку Linux", size=16, bold=True))
    
    # Рівень 1: Kernel TCP Keepalive
    box1 = fitbox(40, 60, 240, 280, "1. TCP Keepalive\n\n• Рівень: Ядро (TCP)\n• Зонд: Порожній ACK\n• Відповідає: Ядро peer-а\n• Виявляє: Обрив мережі, crash ОС\n• Не бачить: Зависання процесів\n• Налаштування: setsockopt", size=12, fill="#eef7fa", stroke="#2980b9")
    frags.append(box1)
    
    # Рівень 2: TCP_USER_TIMEOUT
    box2 = fitbox(300, 60, 240, 280, "2. TCP_USER_TIMEOUT\n\n• Рівень: Ядро (Таймаут)\n• Зонд: Таймер повтору ACK\n• Відповідає: ACK на дані/зонд\n• Виявляє: Застрягання буферів передачі, невідповідь на проби\n• Границя: Жорсткий ліміт мс\n• Налаштування: RFC 5482", size=12, fill="#fdf7e7", stroke="#d35400")
    frags.append(box2)
    
    # Рівень 3: Application Heartbeat
    box3 = fitbox(560, 60, 240, 280, "3. App Heartbeat\n\n• Рівень: Застосунок\n• Зонд: Ping / Pong кадри\n• Відповідає: Застосунок peer-а\n• Виявляє: Deadlock, freeze циклу, обрив мережі, NAT-drop\n• Гарантія: Повна перевірка стеку\n• Налаштування: Код програми", size=12, fill="#eafaf1", stroke="#27ae60")
    frags.append(box3)
    
    render(path, w, h, *frags)
    print(f"Generated {path}")

def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    # Видаляємо застарілі SVG
    for old_svg in glob.glob(os.path.join(img_dir, '*.svg')):
        try:
            os.remove(old_svg)
        except OSError:
            pass
    generate_keepalive_sequence(img_dir)
    generate_liveness_mechanisms(img_dir)

if __name__ == '__main__':
    main()
