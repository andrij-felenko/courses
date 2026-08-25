# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_url_structure():
    """Анатомія URL за стандартом RFC 3986: схема, authority, path, query, fragment."""
    W, H = 960, 360
    frags = []
    frags.append(text(W / 2, 30, "Анатомія URL за стандартом RFC 3986", size=16, bold=True))

    # Повний приклад URL вгорі
    full_url = "https://user:pass@api.example.com:8443/v1/search?query=blue%20sky&sort=desc#results"
    b_url, _, _ = textbox(W / 2, 72, full_url, size=14, bold=True, min_w=900, fill="#f8fafc", stroke=LINE)
    frags.append(b_url)

    # 5 основних блоків
    # 1. Scheme
    b1, _, _ = textbox(110, 150, "Схема (Scheme)\nhttps\n(протокол доступу)", size=11, min_w=140, fill="#eff6ff", stroke=NEG)
    frags.append(b1)
    frags.append(line(110, 92, 110, 122, color=NEG, sw=1.5))
    frags.append(text(110, 205, "Роздільник: «:»", size=10, color=MUTED))

    # 2. Authority
    b2, _, _ = textbox(340, 150, "Орган повноважень (Authority)\nuser:pass@api.example.com:8443\n(користувач, хост і TCP-порт)", size=11, min_w=280, fill="#fef2f2", stroke=POS)
    frags.append(b2)
    frags.append(line(340, 92, 340, 122, color=POS, sw=1.5))
    frags.append(text(340, 205, "Префікс: «//», хост:порт", size=10, color=MUTED))

    # Підблоки authority (деталізація)
    b2_sub, _, _ = textbox(340, 260, "userinfo: user:pass (застаріло)  ·  host: api.example.com  ·  port: 8443", size=10, min_w=300, fill="#ffffff", stroke="#e5e7eb")
    frags.append(b2_sub)
    frags.append(arrow(340, 220, 340, 238, color=POS, sw=1.2))

    # 3. Path
    b3, _, _ = textbox(570, 150, "Шлях (Path)\n/v1/search\n(ієрархія ресурсу)", size=11, min_w=140, fill="#f0fdf4", stroke=FIELD)
    frags.append(b3)
    frags.append(line(570, 92, 570, 122, color=FIELD, sw=1.5))
    frags.append(text(570, 205, "Сегменти через «/»", size=10, color=MUTED))

    # 4. Query
    b4, _, _ = textbox(730, 150, "Запит (Query)\nquery=blue%20sky&sort=desc\n(параметри операції)", size=11, min_w=155, fill="#faf5ff", stroke="#7e22ce")
    frags.append(b4)
    frags.append(line(730, 92, 730, 122, color="#7e22ce", sw=1.5))
    frags.append(text(730, 205, "Початок: «?», пари «&»", size=10, color=MUTED))

    # 5. Fragment
    b5, _, _ = textbox(880, 150, "Фрагмент (Fragment)\nresults\n(якір клієнта)", size=11, min_w=125, fill="#fffbeb", stroke="#b45309")
    frags.append(b5)
    frags.append(line(880, 92, 880, 122, color="#b45309", sw=1.5))
    frags.append(text(880, 205, "Початок: «#» (не йде в HTTP)", size=10, color=MUTED))

    # Пояснення знизу
    frags.append(rect(40, 310, 880, 36, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(W / 2, 332, "Загальний синтаксис: URI = scheme \":\" [ \"//\" authority ] path [ \"?\" query ] [ \"#\" fragment ]", size=12, bold=True, color=INK))

    render(os.path.join(IMG, "url-structure.svg"), W, H, *frags)


def fig_percent_encoding_flow():
    """Конвеєр відсоткового кодування Unicode-символів у URL."""
    W, H = 940, 380
    frags = []
    frags.append(text(W / 2, 30, "Конвеєр відсоткового кодування (Percent-Encoding %XX)", size=16, bold=True))

    # Вхідний рядок
    b_in, _, _ = textbox(130, 95, "Вхідний символ / рядок\n«Київ» або «пробіл»\n(Юнікод-текст)", size=11, min_w=180, fill="#f8fafc", stroke=LINE)
    frags.append(b_in)

    frags.append(arrow(225, 95, 290, 95, color=LINE, sw=1.5))
    frags.append(text(258, 85, "UTF-8", size=10, color=MUTED))

    # Байти UTF-8
    b_utf, _, _ = textbox(390, 95, "Послідовність байтів UTF-8\n'К' = 0xD0 0x9A\n' ' = 0x20", size=11, min_w=180, fill="#eff6ff", stroke=NEG)
    frags.append(b_utf)

    frags.append(arrow(485, 95, 550, 95, color=LINE, sw=1.5))
    frags.append(text(518, 85, "Аналіз", size=10, color=MUTED))

    # Перевірка категорії
    b_cat, _, _ = textbox(680, 95, "Класифікація символу\nНезарезервований чи\nпотребує екранування?", size=11, min_w=220, fill="#fef2f2", stroke=POS)
    frags.append(b_cat)

    # Дві гілки вниз від класифікації
    frags.append(arrow(620, 140, 480, 220, color=FIELD, sw=1.5))
    frags.append(text(530, 175, "ALPHA / DIGIT / - . _ ~", size=10, color=FIELD))

    frags.append(arrow(740, 140, 780, 220, color=POS, sw=1.5))
    frags.append(text(800, 175, "Роздільники, пробіл, UTF-8", size=10, color=POS))

    # Результат 1: Без змін
    b_res1, _, _ = textbox(410, 260, "Незарезервовані (Unreserved)\nЗалишаються без змін\n'A' → 'A', '5' → '5', '-' → '-'", size=11, min_w=240, fill="#f0fdf4", stroke=FIELD)
    frags.append(b_res1)

    # Результат 2: Кодування %XX
    b_res2, _, _ = textbox(770, 260, "Екрановані байти (%HH)\nКожен байт стає %XX\n0xD0 0x9A → %D0%9A, 0x20 → %20", size=11, min_w=260, fill="#faf5ff", stroke="#7e22ce")
    frags.append(b_res2)

    # Підсумок знизу
    frags.append(rect(40, 330, 860, 36, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(W / 2, 352, "Правило: кодується не абстрактний «гліф», а окремі байти його UTF-8 представлення", size=12, bold=True, color=INK))

    render(os.path.join(IMG, "percent-encoding-flow.svg"), W, H, *frags)


def fig_path_normalization():
    """Алгоритм remove_dot_segments для нормалізації шляхів."""
    W, H = 940, 370
    frags = []
    frags.append(text(W / 2, 30, "Алгоритм нормалізації відносних шляхів (remove_dot_segments)", size=16, bold=True))

    # Схема буферів
    frags.append(rect(40, 65, 410, 235, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(245, 90, "Вхідний буфер (Input Buffer)", size=13, bold=True))

    steps_in = [
        "1. Початковий шлях: «/a/b/../c/./d»",
        "2. Сегмент «/a» переміщується у вихід",
        "3. Сегмент «/b» переміщується у вихід",
        "4. Префікс «/..» видаляє останній сегмент",
        "5. Сегмент «/c» переміщується у вихід",
        "6. Префікс «/.» ігнорується (поточний)",
        "7. Сегмент «/d» переміщується у вихід"
    ]
    for idx, s in enumerate(steps_in):
        frags.append(text(55, 120 + idx * 24, s, size=11, anchor="start", color=INK))

    # Стрілка між буферами
    frags.append(arrow(460, 180, 520, 180, color=FIELD, sw=2))
    frags.append(text(490, 168, "Цикл", size=11, bold=True, color=FIELD))

    frags.append(rect(530, 65, 370, 235, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(715, 90, "Вихідний буфер (Output Buffer)", size=13, bold=True, color=FIELD))

    steps_out = [
        "Початок: «»",
        "Додано: «/a»",
        "Додано: «/a/b»",
        "Видалено «/b» → лишається «/a»",
        "Додано: «/a/c»",
        "Без змін: «/a/c»",
        "Результат: «/a/c/d»"
    ]
    for idx, s in enumerate(steps_out):
        col = FIELD if idx == len(steps_out) - 1 else INK
        bld = (idx == len(steps_out) - 1)
        frags.append(text(545, 120 + idx * 24, s, size=11, anchor="start", color=col, bold=bld))

    # Висновок
    frags.append(rect(40, 315, 860, 38, fill="#eff6ff", stroke=NEG, sw=1, rx=4))
    frags.append(text(W / 2, 339, "RFC 3986 §5.2.4: усуває «.» та «..», запобігаючи виходу за межі кореня та Directory Traversal", size=12, bold=True, color=NEG))

    render(os.path.join(IMG, "path-normalization.svg"), W, H, *frags)


def fig_url_parser_state_machine():
    """Скінченний автомат парсера URL: стани та переходи."""
    W, H = 940, 360
    frags = []
    frags.append(text(W / 2, 30, "Скінченний автомат розбору компонентів URL", size=16, bold=True))

    # Стани
    # 1. Scheme
    b_sch, _, _ = textbox(110, 110, "Стан: SCHEME\nЧитання схеми до «:»\n(http, https, ftp)", size=11, min_w=140, fill="#eff6ff", stroke=NEG)
    frags.append(b_sch)

    # Перехід до Authority
    frags.append(arrow(185, 110, 275, 110, color=LINE, sw=1.5))
    frags.append(text(230, 98, "«://»", size=11, bold=True, color=POS))

    # 2. Authority / Host
    b_auth, _, _ = textbox(365, 110, "Стан: AUTHORITY\nПарсинг user@host:port\n(перевірка IPv6 «[...]»)", size=11, min_w=160, fill="#fef2f2", stroke=POS)
    frags.append(b_auth)

    # Перехід до Path
    frags.append(arrow(450, 110, 545, 110, color=LINE, sw=1.5))
    frags.append(text(498, 98, "«/»", size=11, bold=True, color=FIELD))

    # 3. Path
    b_path, _, _ = textbox(630, 110, "Стан: PATH\nЧитання сегментів\nдо «?» або «#»", size=11, min_w=150, fill="#f0fdf4", stroke=FIELD)
    frags.append(b_path)

    # Перехід до Query
    frags.append(arrow(710, 110, 795, 110, color=LINE, sw=1.5))
    frags.append(text(752, 98, "«?»", size=11, bold=True, color="#7e22ce"))

    # 4. Query
    b_query, _, _ = textbox(860, 110, "Стан: QUERY\nПари key=val\nдо «#» або кінця", size=11, min_w=120, fill="#faf5ff", stroke="#7e22ce")
    frags.append(b_query)

    # Переходи до Fragment
    frags.append(arrow(630, 160, 630, 240, color="#b45309", sw=1.5))
    frags.append(text(605, 205, "«#»", size=11, bold=True, color="#b45309"))

    frags.append(arrow(860, 160, 730, 255, color="#b45309", sw=1.5))
    frags.append(text(810, 210, "«#»", size=11, bold=True, color="#b45309"))

    # 5. Fragment
    b_frag, _, _ = textbox(630, 280, "Стан: FRAGMENT\nЛокальний якір документа до кінця рядка\n(використовується лише клієнтом)", size=11, min_w=280, fill="#fffbeb", stroke="#b45309")
    frags.append(b_frag)

    # Прямий перехід зі Scheme до Path (для urn: або mailto:)
    frags.append(line(110, 160, 110, 280, color=MUTED, sw=1.2, dash="4,4"))
    frags.append(arrow(110, 280, 480, 280, color=MUTED, sw=1.2))
    frags.append(text(260, 268, "Без authority (наприклад mailto:, file:)", size=10, color=MUTED))

    render(os.path.join(IMG, "url-parser-state-machine.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_url_structure()
    fig_percent_encoding_flow()
    fig_path_normalization()
    fig_url_parser_state_machine()
    print("Figures generated successfully.")
