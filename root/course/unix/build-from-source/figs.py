# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми build-from-source."""
import sys, os

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від root/course/unix/build-from-source)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def fig_autotools_pipeline(out_dir):
    """Фігура 1: Класичний конвеєр збірки GNU Autotools."""
    w, h = 940, 480
    frags = []

    # Фон і загальна назва
    frags.append(rect(10, 10, 920, 460, fill="#fafbfc", stroke="#d1d5db", sw=1.5, rx=8))
    frags.append(text(470, 38, "Конвеєр конфігурації, компіляції та інсталяції GNU Autotools", size=16, bold=True))

    # Фаза 1: Релізний архів та вихідні дані
    frags.append(rect(30, 65, 265, 375, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(162, 92, "1. Вхідні дані релізу", size=14, bold=True, color=NEG))
    frags.append(text(162, 110, "Релізний архів (Tarball)", size=11, italic=True, color=MUTED))
    frags.append(line(45, 122, 280, 122, color=NEG, sw=1, dash="3,3"))

    frags.append(fitbox(45, 135, 235, 42, "configure (шел-скрипт)\nГотовий зондувальник середовища", size=11, fill="#ffffff", stroke="#93c5fd"))
    frags.append(fitbox(45, 185, 235, 42, "Makefile.in / config.h.in\nШаблони правил та макросів", size=11, fill="#ffffff", stroke="#93c5fd"))
    frags.append(fitbox(45, 235, 235, 42, "Вихідний код (*.c, *.h)\nНезмінні джерела програми", size=11, fill="#ffffff", stroke="#93c5fd"))

    frags.append(rect(45, 290, 235, 135, fill="#dbeafe", stroke=NEG, sw=1, rx=4))
    frags.append(text(162, 310, "Параметри запуску:", size=12, bold=True, color=NEG))
    frags.append(text(55, 332, "• --prefix=/opt/app (ціль FHS)", size=11, anchor="start", color=INK))
    frags.append(text(55, 354, "• --enable-feature / --with-lib", size=11, anchor="start", color=INK))
    frags.append(text(55, 376, "• CFLAGS='-O3 -march=native'", size=11, anchor="start", color=INK))
    frags.append(text(55, 398, "• PKG_CONFIG_PATH=/custom/lib", size=11, anchor="start", color=INK))

    # Стрілка 1 -> 2
    frags.append(arrow(295, 220, 335, 220, color=LINE, sw=2))
    frags.append(text(315, 210, "./configure", size=10, bold=True, color=MUTED))

    # Фаза 2: Конфігурація та генерація
    frags.append(rect(345, 65, 265, 375, fill="#fffbeb", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(477, 92, "2. Зондування системи", size=14, bold=True, color="#d97706"))
    frags.append(text(477, 110, "Перевірка заголовків і компілятора", size=11, italic=True, color=MUTED))
    frags.append(line(360, 122, 595, 122, color="#d97706", sw=1, dash="3,3"))

    frags.append(fitbox(360, 135, 235, 52, "Зондування Toolchain\nCC/CXX, прапорці, архітектура CPU,\nнаявність бібліотек через pkg-config", size=11, fill="#ffffff", stroke="#fcd34d"))
    frags.append(fitbox(360, 195, 235, 42, "Перевірка API та заголовків\nsys/epoll.h, pthread, statx()", size=11, fill="#ffffff", stroke="#fcd34d"))

    frags.append(rect(360, 250, 235, 175, fill="#fef3c7", stroke="#d97706", sw=1, rx=4))
    frags.append(text(477, 270, "Згенеровані артефакти:", size=12, bold=True, color="#d97706"))
    frags.append(fitbox(370, 282, 215, 38, "config.h\n#define HAVE_SYS_EPOLL_H 1", size=11, fill="#ffffff", stroke="#f59e0b"))
    frags.append(fitbox(370, 326, 215, 38, "Makefile\nПідставлені CC, CFLAGS, PREFIX", size=11, fill="#ffffff", stroke="#f59e0b"))
    frags.append(fitbox(370, 370, 215, 42, "config.log\nПовний лог для діагностики помилок", size=10, fill="#ffffff", stroke="#f59e0b"))

    # Стрілка 2 -> 3
    frags.append(arrow(610, 220, 650, 220, color=LINE, sw=2))
    frags.append(text(630, 210, "make", size=10, bold=True, color=MUTED))

    # Фаза 3: Компіляція та інсталяція
    frags.append(rect(660, 65, 250, 375, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(785, 92, "3. Збірка та розкладка", size=14, bold=True, color=FIELD))
    frags.append(text(785, 110, "make -j$(nproc) та make install", size=11, italic=True, color=MUTED))
    frags.append(line(675, 122, 895, 122, color=FIELD, sw=1, dash="3,3"))

    frags.append(fitbox(675, 135, 220, 48, "make -j$(nproc)\nКомпіляція *.c -> *.o\nЛінкування в ELF бінарник", size=11, fill="#ffffff", stroke="#86efac"))
    frags.append(fitbox(675, 192, 220, 42, "Тестування (make check)\nПрогін локальних тестів", size=11, fill="#ffffff", stroke="#86efac"))

    frags.append(rect(675, 245, 220, 180, fill="#dcfce7", stroke=FIELD, sw=1, rx=4))
    frags.append(text(785, 265, "Розкладка за FHS:", size=12, bold=True, color=FIELD))
    frags.append(text(685, 288, "• $PREFIX/bin (виконувані файли)", size=10, anchor="start", color=INK))
    frags.append(text(685, 308, "• $PREFIX/lib (*.so, *.a бібліотеки)", size=10, anchor="start", color=INK))
    frags.append(text(685, 328, "• $PREFIX/include (*.h заголовки)", size=10, anchor="start", color=INK))
    frags.append(text(685, 348, "• $PREFIX/share/man (довідка)", size=10, anchor="start", color=INK))
    frags.append(line(685, 360, 885, 360, color=FIELD, sw=1, dash="2,2"))
    frags.append(text(785, 378, "Пакетна ізоляція:", size=10, bold=True, color=FIELD))
    frags.append(text(685, 396, "make install DESTDIR=/tmp/stage", size=10, anchor="start", color=FIELD))
    frags.append(text(685, 414, "-> безпечне створення DEB/RPM", size=10, anchor="start", color=FIELD))

    # Стрілка знизу
    frags.append(line(50, 455, 890, 455, color=LINE, sw=1.2))
    frags.append(arrow(870, 455, 895, 455, color=LINE, sw=1.2))
    frags.append(text(470, 448, "Послідовність виконання: Конфігурація -> Паралельна компіляція -> Інсталяція за FHS", size=11, bold=True, color=LINE))

    path = os.path.join(out_dir, "autotools-pipeline.svg")
    render(path, w, h, *frags)
    print(f"Generated: {path}")

def fig_pkgconfig_resolution(out_dir):
    """Фігура 2: Механізм розв'язання залежностей через pkg-config."""
    w, h = 920, 420
    frags = []

    frags.append(rect(10, 10, 900, 400, fill="#fafbfc", stroke="#d1d5db", sw=1.5, rx=8))
    frags.append(text(460, 38, "Механізм розв'язання компіляційних та лінкових залежностей через pkg-config", size=15, bold=True))

    # Ліва колонка: Проблема та пошук
    frags.append(rect(30, 65, 270, 320, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(165, 92, "Вихідний код програми", size=13, bold=True, color=NEG))
    frags.append(line(45, 104, 285, 104, color=NEG, sw=1, dash="3,3"))

    frags.append(fitbox(45, 115, 240, 52, "#include <openssl/ssl.h>\nSSL_CTX_new(TLS_method());\nПотребує API та символів бібліотеки", size=11, fill="#ffffff", stroke="#93c5fd"))
    frags.append(fitbox(45, 180, 240, 60, "Запит системи збірки:\npkg-config --cflags openssl\npkg-config --libs openssl\npkg-config --modversion openssl", size=10, fill="#ffffff", stroke="#93c5fd"))

    frags.append(rect(45, 255, 240, 115, fill="#dbeafe", stroke=NEG, sw=1, rx=4))
    frags.append(text(165, 275, "Каталоги пошуку .pc:", size=11, bold=True, color=NEG))
    frags.append(text(55, 295, "1. $PKG_CONFIG_PATH", size=10, anchor="start", color=INK))
    frags.append(text(55, 315, "2. /usr/lib/x86_64-linux-gnu/pkgconfig", size=10, anchor="start", color=INK))
    frags.append(text(55, 335, "3. /usr/share/pkgconfig", size=10, anchor="start", color=INK))
    frags.append(text(55, 355, "4. /usr/local/lib/pkgconfig", size=10, anchor="start", color=INK))

    # Стрілка до центру
    frags.append(arrow(300, 220, 340, 220, color=LINE, sw=2))

    # Центральна колонка: Файл метаданих .pc
    frags.append(rect(350, 65, 250, 320, fill="#fffbeb", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(475, 92, "Метадані: openssl.pc", size=13, bold=True, color="#d97706"))
    frags.append(line(365, 104, 585, 104, color="#d97706", sw=1, dash="3,3"))

    pc_content = "prefix=/usr\nexec_prefix=${prefix}\nlibdir=${exec_prefix}/lib/x86_64-linux-gnu\nincludedir=${prefix}/include\n\nName: OpenSSL\nVersion: 3.0.13\nRequires.private: libssl libcrypto\nCflags: -I${includedir}\nLibs: -L${libdir} -lssl -lcrypto"
    frags.append(fitbox(365, 115, 220, 190, pc_content, size=9, fill="#ffffff", stroke="#fcd34d"))

    frags.append(rect(365, 315, 220, 55, fill="#fef3c7", stroke="#d97706", sw=1, rx=4))
    frags.append(text(475, 332, "Постачальник .pc файлу:", size=10, bold=True, color="#d97706"))
    frags.append(text(475, 352, "Пакунок libssl-dev / openssl-devel", size=10, color=INK))

    # Стрілка до правої
    frags.append(arrow(600, 220, 640, 220, color=LINE, sw=2))

    # Права колонка: Ін'єкція у фази компілятора
    frags.append(rect(650, 65, 240, 320, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(770, 92, "Ін'єкція прапорців", size=13, bold=True, color=FIELD))
    frags.append(line(665, 104, 875, 104, color=FIELD, sw=1, dash="3,3"))

    frags.append(fitbox(665, 115, 210, 75, "Фаза компіляції (gcc -c)\nCflags: -I/usr/include\n-> Знаходить openssl/ssl.h\n(запобігає fatal error:\nmissing header)", size=10, fill="#ffffff", stroke="#86efac"))

    frags.append(fitbox(665, 200, 210, 80, "Фаза лінкування (gcc -o)\nLibs: -L/usr/lib/... -lssl -lcrypto\n-> Розв'язує SSL_CTX_new\nта додає DT_NEEDED\n(запобігає undefined reference)", size=10, fill="#ffffff", stroke="#86efac"))

    frags.append(rect(665, 290, 210, 80, fill="#dcfce7", stroke=FIELD, sw=1, rx=4))
    frags.append(text(770, 310, "Результат:", size=11, bold=True, color=FIELD))
    frags.append(text(770, 330, "Бінарник зібрано успішно,", size=10, color=INK))
    frags.append(text(770, 348, "динамічні лінки зафіксовано", size=10, color=INK))

    path = os.path.join(out_dir, "dependency-resolution-pkgconfig.svg")
    render(path, w, h, *frags)
    print(f"Generated: {path}")

def fig_clean_installation(out_dir):
    """Фігура 3: Стратегії чистого встановлення ПЗ у системі."""
    w, h = 920, 420
    frags = []

    frags.append(rect(10, 10, 900, 400, fill="#fafbfc", stroke="#d1d5db", sw=1.5, rx=8))
    frags.append(text(460, 38, "Порівняння стратегій встановлення скомпільованого ПЗ у Linux", size=15, bold=True))

    cols = [
        {
            "x": 30, "w": 270, "title": "1. Прямий make install", "sub": "Небезпечний підхід",
            "color": POS, "bg": "#fef2f2",
            "items": [
                "Копіює у спільний /usr/local",
                "Змішує файли різних версій",
                "Немає реєстру встановленого",
                "make uninstall часто відсутній",
                "Ризик зламати системні ліби"
            ],
            "verdict": "Засмічення ОС / Високий ризик"
        },
        {
            "x": 325, "w": 270, "title": "2. Ізольований префікс", "sub": "--prefix=/opt/<app>",
            "color": "#d97706", "bg": "#fffbeb",
            "items": [
                "Всі файли в одній теці /opt/app",
                "RUNPATH = $ORIGIN/../lib",
                "Видалення: rm -rf /opt/app",
                "Кілька паралельних версій",
                "Потребує налаштування PATH"
            ],
            "verdict": "Чистота / Автономність"
        },
        {
            "x": 620, "w": 270, "title": "3. Пакування через DESTDIR", "sub": "checkinstall або fpm -> DEB/RPM",
            "color": FIELD, "bg": "#f0fdf4",
            "items": [
                "make install DESTDIR=/tmp/stage",
                "fpm генерує нативний *.deb / *.rpm",
                "Інсталяція через dpkg / rpm",
                "Повний облік у менеджері пакетів",
                "Чисте видалення: apt remove"
            ],
            "verdict": "Максимальна керованість"
        }
    ]

    for c in cols:
        cx, cw = c["x"], c["w"]
        frags.append(rect(cx, 65, cw, 320, fill=c["bg"], stroke=c["color"], sw=1.5, rx=6))
        frags.append(text(cx + cw/2, 92, c["title"], size=13, bold=True, color=c["color"]))
        frags.append(text(cx + cw/2, 110, c["sub"], size=11, italic=True, color=MUTED))
        frags.append(line(cx + 15, 120, cx + cw - 15, 120, color=c["color"], sw=1, dash="3,3"))

        for idx, it in enumerate(c["items"]):
            iy = 145 + idx * 28
            frags.append(circle(cx + 25, iy - 4, 3, fill=c["color"], stroke=c["color"]))
            frags.append(text(cx + 35, iy, it, size=11, anchor="start", color=INK))

        frags.append(rect(cx + 15, 320, cw - 30, 45, fill="#ffffff", stroke=c["color"], sw=1.2, rx=4))
        frags.append(text(cx + cw/2, 347, c["verdict"], size=11, bold=True, color=c["color"]))

    path = os.path.join(out_dir, "clean-installation-strategies.svg")
    render(path, w, h, *frags)
    print(f"Generated: {path}")

def main():
    topic_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(topic_dir, "img")
    os.makedirs(out_dir, exist_ok=True)
    fig_autotools_pipeline(out_dir)
    fig_pkgconfig_resolution(out_dir)
    fig_clean_installation(out_dir)

if __name__ == "__main__":
    main()
