import sys
import os

# Імпортуємо svgkit з директорії scripts у корені репозиторію
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../scripts')))
from svgkit import *

def generate_trust_chain():
    # Забезпечуємо наявність директорії img
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    
    frags = []
    
    # 1. Мейнтейнер (Джерело підпису)
    b1, w1, h1 = textbox(160, 140, "Розробник / Signing Server\n• Закритий ключ GPG (Private Key)\n• Створення Release/InRelease\n• Обчислення SHA-256 індексів", size=13, fill="#fef3c7", stroke="#d97706", sw=1.5, min_w=240)
    frags.append(b1)
    
    # 2. Дзеркало репозиторію (Публічний сервер)
    b2, w2, h2 = textbox(480, 140, "Публічне дзеркало (HTTP/HTTPS)\n• InRelease (метадані + підпис)\n• Packages.xz (каталог пакунків)\n• app_1.2_amd64.deb (бінарники)", size=13, fill="#e0f2fe", stroke="#0284c7", sw=1.5, min_w=240)
    frags.append(b2)
    
    # 3. Локальний клієнт (Система користувача)
    b3, w3, h3 = textbox(800, 140, "Локальна система (APT / DNF)\n• /etc/apt/keyrings/docker.gpg\n• Вказівка [signed-by=...]\n• Перевірка підпису та хешів", size=13, fill="#dcfce7", stroke="#16a34a", sw=1.5, min_w=240)
    frags.append(b3)
    
    # Стрілки передачі даних
    frags.append(arrow(285, 140, 355, 140, color="#d97706", sw=2))
    frags.append(text(320, 125, "Публікація", size=11, color="#b45f06", bold=True))
    
    frags.append(arrow(605, 140, 675, 140, color="#0284c7", sw=2))
    frags.append(text(640, 125, "apt update", size=11, color="#0284c7", bold=True))
    
    # Блок захисту та перевірки цілісності
    b4, w4, h4 = textbox(480, 270, "Захист від атак (Man-in-the-Middle & Downgrade)\n• Valid-Until: захист від застарілих індексів\n• SHA-256: захист від підміни пакунка на дзеркалі\n• GPG підпис: гарантія авторства мейнтейнера", size=12, fill="#f3f4f6", stroke="#4b5563", sw=1.5, min_w=380)
    frags.append(b4)
    
    frags.append(line(480, 205, 480, 225, color="#6b7280", sw=1.5, dash="4,4"))
    
    output_path = os.path.join(img_dir, "fig-trust-chain.svg")
    render(output_path, 960, 340, *frags, title="Криптографічний ланцюжок довіри в екосистемі репозиторіїв")

def generate_verification_flow():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    
    frags = []
    
    # Кроки верифікації
    b1, w1, h1 = textbox(150, 100, "1. Завантаження InRelease\nОтримання індексу з підписом", size=12, fill="#f3f4f6", stroke="#4b5563", min_w=200)
    frags.append(b1)
    
    b2, w2, h2 = textbox(410, 100, "2. Перевірка GPG-підпису\nЗвірка з [signed-by=...]", size=12, fill="#fef3c7", stroke="#d97706", min_w=200)
    frags.append(b2)
    
    b3, w3, h3 = textbox(670, 100, "3. Звірка хешу Packages.xz\nВитяг SHA-256 з InRelease", size=12, fill="#e0f2fe", stroke="#0284c7", min_w=200)
    frags.append(b3)
    
    b4, w4, h4 = textbox(150, 220, "4. Завантаження .deb / .rpm\nОтримання архіву програми", size=12, fill="#f3f4f6", stroke="#4b5563", min_w=200)
    frags.append(b4)
    
    b5, w5, h5 = textbox(410, 220, "5. Перевірка SHA-256 пакунка\nЗвірка з Packages.xz", size=12, fill="#e0f2fe", stroke="#0284c7", min_w=200)
    frags.append(b5)
    
    b6, w6, h6 = textbox(670, 220, "6. Передача у dpkg / rpm\nВстановлення у систему", size=12, fill="#dcfce7", stroke="#16a34a", min_w=200)
    frags.append(b6)
    
    # Стрілки потоку
    frags.append(arrow(255, 100, 305, 100, color="#4b5563", sw=1.5))
    frags.append(arrow(515, 100, 565, 100, color="#d97706", sw=1.5))
    
    # Перехід від 3 до 4
    frags.append(line(670, 135, 670, 160, color="#0284c7", sw=1.5))
    frags.append(line(670, 160, 150, 160, color="#0284c7", sw=1.5))
    frags.append(arrow(150, 160, 150, 185, color="#0284c7", sw=1.5))
    
    frags.append(arrow(255, 220, 305, 220, color="#4b5563", sw=1.5))
    frags.append(arrow(515, 220, 565, 220, color="#0284c7", sw=1.5))
    
    output_path = os.path.join(img_dir, "fig-repo-verification-flow.svg")
    render(output_path, 820, 300, *frags, title="Послідовність криптографічних перевірок під час оновлення та встановлення")

if __name__ == "__main__":
    generate_trust_chain()
    generate_verification_flow()
