# -*- coding: utf-8 -*-
"""Фігури до теми «МК як USB-host» та її вставки comp-otg.
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── roles-swapped: той самий чип як device і як host ────────────────────────
# Ідея: апаратний блок один, а ролі дзеркальні. Зліва ПК командує — чип лише
# відповідає й бере живлення; справа чип сам командує й сам дає VBUS.
def fig_roles_swapped():
    W, H = 820, 380
    p = [text(W / 2, 30, "Один блок USB-OTG — дві ролі", size=17, bold=True)]

    # ── ліва сцена: чип як пристрій ──
    p.append(text(205, 64, "чип як ПРИСТРІЙ (просто)", size=13, bold=True, color=NEG))
    pc, pcw, _ = textbox(110, 150, ["ПК", "host"], size=14, bold=True,
                         fill="#eaf0fd", stroke=NEG, sw=2, min_w=110)
    mc, mcw, _ = textbox(300, 150, ["чип", "device"], size=14, bold=True,
                         fill=FILL, stroke=LINE, sw=2, min_w=110)
    p += [pc, mc]
    p.append(arrow(166, 138, 244, 138, color=NEG))      # команди →
    p.append(text(205, 128, "запити", size=11, color=NEG))
    p.append(line(244, 162, 166, 162, color=MUTED, dash="4 3"))
    p.append(text(205, 178, "відповіді", size=11, color=MUTED))
    p.append(arrow(166, 206, 244, 206, color=POS))       # VBUS →
    p.append(text(205, 224, "VBUS від ПК", size=11, color=POS))

    # роздільник
    p.append(line(410, 70, 410, 330, color=MUTED, dash="5 4"))

    # ── права сцена: чип як хост ──
    p.append(text(615, 64, "чип як HOST (складніше)", size=13, bold=True, color=POS))
    mh, mhw, _ = textbox(520, 150, ["чип", "host"], size=14, bold=True,
                         fill="#fdecea", stroke=POS, sw=2, min_w=110)
    dv, dvw, _ = textbox(710, 150, ["флешка,", "клавіатура"], size=13, bold=True,
                         fill=FILL, stroke=LINE, sw=2, min_w=120)
    p += [mh, dv]
    p.append(arrow(576, 138, 654, 138, color=POS))
    p.append(text(615, 128, "запити", size=11, color=POS))
    p.append(line(654, 162, 576, 162, color=MUTED, dash="4 3"))
    p.append(text(615, 178, "відповіді", size=11, color=MUTED))
    p.append(arrow(576, 206, 654, 206, color=POS))
    p.append(text(615, 224, "VBUS дає чип", size=11, color=POS))

    p.append(fitbox(70, 286, 680, 64,
                    "Стрілки команд завжди йдуть від host. Помінявши роль, чип бере "
                    "на себе все: живлення, виявлення, енумерацію, розклад передач.",
                    size=12, color=MUTED, fill=BG, stroke=MUTED))
    render(os.path.join(IMG, "roles-swapped.svg"), W, H, *p)


# ── otg-id-pin: контакт ID вирішує роль ─────────────────────────────────────
# Ідея: статичний рівень на п'ятому контакті, ще до будь-яких даних, диктує
# контролеру роль. Висить → пристрій. На землю (OTG-кабель) → host + VBUS.
def fig_otg_id_pin():
    W, H = 760, 400
    p = [text(W / 2, 30, "Контакт ID задає роль до першого біта даних", size=16, bold=True)]

    # верхній випадок — ID висить
    p.append(rect(60, 64, 300, 130, fill="#eaf0fd", stroke=NEG, sw=2))
    p.append(text(210, 90, "micro-B: ID висить", size=14, bold=True, color=NEG))
    p.append(text(210, 116, "ID ──/  (не підключено)", size=12, color=INK))
    p.append(text(210, 142, "контролер: лишаюсь", size=12, color=MUTED))
    p.append(text(210, 162, "ПРИСТРОЄМ", size=14, bold=True, color=NEG))
    p.append(text(210, 184, "VBUS бере ззовні", size=11, color=MUTED))

    # нижній випадок — ID на GND
    p.append(rect(400, 64, 300, 130, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(550, 90, "micro-A (OTG-кабель)", size=14, bold=True, color=POS))
    p.append(text(550, 116, "ID ──● GND  (замкнуто)", size=12, color=INK))
    p.append(text(550, 142, "контролер: стаю", size=12, color=MUTED))
    p.append(text(550, 162, "HOST", size=14, bold=True, color=POS))
    p.append(text(550, 184, "зобов'язаний дати VBUS", size=11, color=POS))

    # п'ять контактів роз'єму
    p.append(text(W / 2, 236, "П'ять контактів micro-USB:", size=13, bold=True))
    names = ["VBUS", "D−", "D+", "ID", "GND"]
    cols = [POS, NEG, POS, FIELD, INK]
    x0, gap = 200, 90
    for i, (n, c) in enumerate(zip(names, cols)):
        x = x0 + i * gap
        p.append(circle(x, 270, 16, fill=FILL, stroke=c, sw=2))
        p.append(text(x, 275, n, size=11, bold=True, color=c))
    p.append(fitbox(60, 312, 640, 64,
                    "На USB-C тієї самої ролі досягають резистори CC, але ідея та сама: "
                    "статичний сигнал каже контролеру, хто головний.",
                    size=12, color=MUTED, fill=BG, stroke=MUTED))
    render(os.path.join(IMG, "otg-id-pin.svg"), W, H, *p)


# ── host-use-cases: типові ролі хоста на МК ─────────────────────────────────
# Ідея: дві найчастіші причини взагалі вмикати host — носій (MSC) і ввід (HID).
def fig_host_use_cases():
    W, H = 760, 360
    p = [text(W / 2, 30, "Найчастіші причини зробити МК хостом", size=16, bold=True)]

    mh, _, _ = textbox(380, 150, ["МК", "host", "(S2 / S3)"], size=14, bold=True,
                       fill="#fdecea", stroke=POS, sw=2.2, min_w=130)
    p.append(mh)

    # ліворуч — флешка (MSC)
    fl, _, _ = textbox(150, 150, ["USB-флешка", "клас MSC"], size=13, bold=True,
                       fill=FILL, stroke=LINE, sw=2, min_w=150)
    p.append(fl)
    p.append(arrow(310, 150, 232, 150, color=POS))
    p.append(mtext(150, 210, ["логи на знімний носій,", "оновлення без програматора"],
                   size=11, color=MUTED, lh=1.3))

    # праворуч — клавіатура (HID)
    kb, _, _ = textbox(610, 150, ["USB-клавіатура", "клас HID"], size=13, bold=True,
                       fill=FILL, stroke=LINE, sw=2, min_w=150)
    p.append(kb)
    p.append(arrow(450, 150, 528, 150, color=POS))
    p.append(mtext(610, 210, ["ввід команд", "без матриці кнопок"],
                   size=11, color=MUTED, lh=1.3))

    p.append(fitbox(120, 268, 520, 64,
                    "В обох випадках МК мусить подати на порт 5 В VBUS,\n"
                    "а сам живиться від 3.3 В — тож потрібне зовнішнє джерело й ключ.",
                    size=12, color=POS, fill="#fdecea", stroke=POS))
    render(os.path.join(IMG, "host-use-cases.svg"), W, H, *p)


# ── id-pin (вставка comp-otg): два штекери, ID вирішує роль ──────────────────
# Ідея для вставки: показати ФІЗИЧНУ відмінність micro-A від micro-B на рівні
# одного контакту — звідси й уся плутанина новачка з «будь-яким кабелем».
def fig_comp_id_pin():
    W, H = 720, 360
    p = [text(W / 2, 30, "Той самий роз'єм, різний контакт ID → різна роль", size=15, bold=True)]

    # micro-B
    p.append(rect(70, 70, 280, 220, fill="#eaf0fd", stroke=NEG, sw=2))
    p.append(text(210, 100, "micro-B (звичайний)", size=14, bold=True, color=NEG))
    p.append(text(210, 134, "ID  висить", size=13, color=INK))
    p.append(text(210, 162, "(floating)", size=11, color=MUTED))
    p.append(text(210, 206, "→ контролер лишається", size=12, color=MUTED))
    p.append(text(210, 228, "ПРИСТРОЄМ", size=15, bold=True, color=NEG))
    p.append(text(210, 262, "VBUS приходить ззовні", size=11, color=MUTED))

    # micro-A
    p.append(rect(370, 70, 280, 220, fill="#fdecea", stroke=POS, sw=2))
    p.append(text(510, 100, "micro-A (OTG-кабель)", size=14, bold=True, color=POS))
    p.append(text(510, 134, "ID  на GND", size=13, color=INK))
    p.append(text(510, 162, "(замкнуто)", size=11, color=MUTED))
    p.append(text(510, 206, "→ контролер стає", size=12, color=MUTED))
    p.append(text(510, 228, "HOST", size=15, bold=True, color=POS))
    p.append(text(510, 262, "мусить подати VBUS", size=11, color=POS))

    p.append(fitbox(70, 308, 580, 40,
                    "Дрібний центральний майданчик у micro-A — єдина видима різниця, "
                    "а наслідок діаметральний.", size=12, color=MUTED, fill=BG, stroke=MUTED))
    render(os.path.join(IMG, "id-pin.svg"), W, H, *p)


# ── vbus-power (вставка comp-otg): три джерела 5 В і бюджет струму ───────────
# Ідея: чип не видає 5 В, тож VBUS треба взяти ззовні. Три типові способи й
# нагадування про стелю струму гнізда.
def fig_comp_vbus_power():
    W, H = 760, 380
    p = [text(W / 2, 30, "Чип не видає 5 В — VBUS беремо одним із трьох способів", size=15, bold=True)]

    mh, _, _ = textbox(W / 2, 86, ["МК-host (3.3 В)", "потрібні 5 В на VBUS"], size=13, bold=True,
                       fill="#fdecea", stroke=POS, sw=2, min_w=260)
    p.append(mh)

    boxes = [
        (150, "Ключ на платі",      ["load switch,", "GPIO-enable"]),
        (380, "Зовнішні 5 В",       ["окреме джерело,", "повербанк"]),
        (610, "Живлений хаб",       ["хаб сам живить", "периферію"]),
    ]
    for x, title, sub in boxes:
        b, _, _ = textbox(x, 190, [title], size=13, bold=True, fill=FILL, stroke=LINE, sw=1.8, min_w=170)
        p.append(b)
        p.append(arrow(W / 2, 110, x, 168, color=MUTED))
        p.append(mtext(x, 232, sub, size=11, color=MUTED, lh=1.3))

    p.append(fitbox(90, 286, 580, 76,
                    "Стеля типового гнізда host-DevKit — близько 500 мА.\n"
                    "Старий 2.5″ HDD чи потужний Wi-Fi-свисток виходять за неї:\n"
                    "звідси просадки VBUS і збої енумерації. Ліки — хаб або зовнішнє джерело.",
                    size=12, color=INK, fill=BG, stroke=MUTED))
    render(os.path.join(IMG, "vbus-power.svg"), W, H, *p)


# ── host-stack-layers (детальна): чотири шари host-стека ─────────────────────
# Ідея: великий розмір стека — це не один шматок, а чотири шари; запит іде знизу
# вгору, і помилка майже завжди локалізується на одному рівні.
def fig_host_stack_layers():
    W, H = 760, 420
    p = [text(W / 2, 30, "Host-стек: чотири шари, запит іде знизу вгору", size=16, bold=True)]

    layers = [
        ("застосунок",            "читає файли й звіти — про кадри й канали не знає", FILL),
        ("клас-драйвери",         "MSC · HID · CDC — що означають ці байти",          "#eafaf1"),
        ("ядро host (hub + enum)","адреси, дескриптори, дерево пристроїв",            "#eaf0fd"),
        ("HCD — драйвер контролера","канали, кадри, реальне залізо",                  "#fdecea"),
    ]
    x, w = 130, 500
    y0, bh, gap = 64, 74, 14
    for i, (name, sub, fill) in enumerate(layers):
        y = y0 + i * (bh + gap)
        p.append(rect(x, y, w, bh, fill=fill, stroke=LINE, sw=1.8))
        p.append(text(x + 18, y + 30, name, size=14, bold=True, anchor="start"))
        p.append(text(x + 18, y + 54, sub, size=11, color=MUTED, anchor="start"))

    # стрілка «запит знизу вгору» збоку
    ax = x + w + 36
    p.append(arrow(ax, y0 + 4 * (bh + gap) - gap, ax, y0 + 6, color=POS, sw=2.2))
    p.append(text(ax + 14, (y0 + y0 + 4 * (bh + gap)) / 2, "знизу вгору", size=11,
                  color=POS, anchor="start"))
    # залізо під низом
    p.append(text(x + w / 2, y0 + 4 * (bh + gap) + 6, "↓ регістри USB-OTG контролера ↓",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "host-stack-layers.svg"), W, H, *p)


if __name__ == "__main__":
    fig_roles_swapped()
    fig_otg_id_pin()
    fig_host_use_cases()
    fig_comp_id_pin()
    fig_comp_vbus_power()
    fig_host_stack_layers()
    print("OK: 6 figures ->", IMG)
