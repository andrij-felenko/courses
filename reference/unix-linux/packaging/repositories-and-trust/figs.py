import sys
import os

# Імпортуємо svgkit з директорії scripts у корені репозиторію
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../scripts')))
try:
    import svgkit
except ImportError:
    print("Не знайдено svgkit у scripts/")
    sys.exit(1)

def render():
    svgkit.init(800, 450)
    
    # Заголовок
    svgkit.text(400, 30, "Ланцюжок довіри репозиторіїв (APT)", font_size=24, anchor="middle", font_weight="bold", fill="#333")

    # Мейнтейнер (Джерело)
    svgkit.rect(50, 100, 200, 100, rx=10, fill="#f9cb9c", stroke="#b45f06", stroke_width=2)
    svgkit.text(150, 130, "Мейнтейнер", font_size=16, anchor="middle", font_weight="bold", fill="#000")
    svgkit.text(150, 160, "Закритий ключ GPG", font_size=14, anchor="middle", fill="#000")
    svgkit.text(150, 180, "(Підписує Release)", font_size=12, anchor="middle", fill="#555")

    # Сервер репозиторію
    svgkit.rect(300, 100, 200, 120, rx=10, fill="#cfe2f3", stroke="#0b5394", stroke_width=2)
    svgkit.text(400, 130, "Дзеркало Репозиторію", font_size=16, anchor="middle", font_weight="bold", fill="#000")
    svgkit.text(400, 155, "Release (хеші)", font_size=14, anchor="middle", fill="#000")
    svgkit.text(400, 175, "Release.gpg (підпис)", font_size=14, anchor="middle", fill="#000")
    svgkit.text(400, 195, "Packages.gz", font_size=14, anchor="middle", fill="#000")
    
    # Клієнтська система
    svgkit.rect(550, 100, 200, 120, rx=10, fill="#d9ead3", stroke="#38761d", stroke_width=2)
    svgkit.text(650, 130, "Система Користувача", font_size=16, anchor="middle", font_weight="bold", fill="#000")
    svgkit.text(650, 155, "/etc/apt/keyrings/", font_size=14, anchor="middle", fill="#000")
    svgkit.text(650, 175, "Відкритий ключ GPG", font_size=14, anchor="middle", fill="#000")
    svgkit.text(650, 195, "APT / dpkg", font_size=14, anchor="middle", fill="#000")

    # Стрілки
    svgkit.arrow(250, 150, 300, 150, color="#b45f06", width=3)
    svgkit.text(275, 140, "Публікація", font_size=12, anchor="middle", fill="#b45f06")
    
    svgkit.arrow(500, 150, 550, 150, color="#0b5394", width=3)
    svgkit.text(525, 140, "apt update", font_size=12, anchor="middle", fill="#0b5394")
    
    # Процес перевірки на клієнті
    svgkit.rect(550, 260, 200, 130, rx=8, fill="#eeeeee", stroke="#666666", stroke_width=1, stroke_dasharray="5,5")
    svgkit.text(650, 280, "Процес перевірки", font_size=14, anchor="middle", font_weight="bold", fill="#333")
    svgkit.text(650, 310, "1. GPG підпис OK?", font_size=12, anchor="middle", fill="#000")
    svgkit.text(650, 335, "2. Хеш Release == Packages?", font_size=12, anchor="middle", fill="#000")
    svgkit.text(650, 360, "3. Хеш Packages == .deb?", font_size=12, anchor="middle", fill="#000")
    
    # Стрілка вниз на клієнті
    svgkit.arrow(650, 220, 650, 260, color="#38761d", width=2)
    
    # Додаткові позначки безпеки
    svgkit.rect(320, 260, 160, 50, rx=5, fill="#fff2cc", stroke="#d9a5b3", stroke_width=1)
    svgkit.text(400, 275, "Valid-Until (дата)", font_size=12, anchor="middle", fill="#990000")
    svgkit.text(400, 295, "Запобігає Replay-атакам", font_size=10, anchor="middle", fill="#990000")
    
    svgkit.arrow(400, 220, 400, 260, color="#990000", width=1, stroke_dasharray="3,3")

    svgkit.save("trust_chain.svg")

if __name__ == "__main__":
    render()
