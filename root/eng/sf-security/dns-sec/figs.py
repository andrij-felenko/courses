# -*- coding: utf-8 -*-
"""Фігури до теми «DNSSEC: цифровий підпис і ланцюг довіри в системі доменних імен»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

SOFT_BLUE = "#eef3fb"
WARM_ORANGE = "#fdf3e6"
COOL_GREEN = "#eef8f1"
PURPLE_TINT = "#f5f3ff"
BORDER_GRAY = "#cbd5e1"
TEXT_DARK = "#0f172a"
TEXT_MUTED = "#475569"

def box(cx, cy, s, size=12, fill=FILL, bold=False):
    body, w, h = textbox(cx, cy, s, size=size, fill=fill, bold=bold)
    return body, w / 2.0, h / 2.0


# ─────────────────────────────────────────────────────────────────────────────
# 1. Ланцюг довіри DNSSEC (Chain of Trust)
# ─────────────────────────────────────────────────────────────────────────────
def fig_chain_of_trust():
    W, H = 1040, 720
    f = []

    f.append(text(40, 35, "Ланцюг довіри DNSSEC: від іменованого якоря кореня до запису A в зоні",
                  size=14, color=TEXT_DARK, anchor="start", bold=True))

    levels = [
        (60, SOFT_BLUE, "Коренева зона «.» (Root Zone)",
         "Root KSK\n(Trust Anchor)", "Root ZSK",
         "підписує DNSKEY RRset кореня",
         "DS запит вказує на KSK зони .ua"),
        (220, WARM_ORANGE, "TLD зона «.ua»",
         "DS (.ua)\n(хеш KSK .ua)", "ZSK (.ua)",
         "підписано Root ZSK у зоні «.»",
         "DS вказує на KSK example.ua"),
        (380, COOL_GREEN, "Авторитетна зона «example.ua»",
         "DS (example.ua)\n(хеш KSK example.ua)", "ZSK (example.ua)",
         "підписано ZSK зони .ua",
         "ZSK підписує A/AAAA RRset"),
        (540, PURPLE_TINT, "Цільовий запис даних (RRset)",
         "A RRset\nexample.ua IN A 193.0.2.1", "RRSIG (A)\nпідпис запису A",
         "перевіряється публічним ZSK example.ua",
         "Дані валідовані (AD flag)"),
    ]

    for py, tone, zone_title, ksk_txt, zsk_txt, left_desc, right_desc in levels:
        f.append(rect(30, py, 980, 135, fill=tone, stroke=BORDER_GRAY, sw=1.2, rx=10))
        f.append(text(50, py + 25, zone_title, size=13, color=TEXT_MUTED, anchor="start", bold=True))
        
        kb, kw, kh = box(240, py + 80, ksk_txt, size=11, fill="#ffffff", bold=True)
        zb, zw, zh = box(620, py + 80, zsk_txt, size=11, fill="#ffffff", bold=True)
        f += [kb, zb]
        
        f.append(arrow(240 + kw + 10, py + 80, 620 - zw - 10, py + 80))
        f.append(text(430, py + 65, left_desc, size=10, color=TEXT_MUTED))
        f.append(text(850, py + 80, right_desc, size=10, color=TEXT_MUTED, anchor="middle"))

    # Вертикальні стрілки зв'язку між рівнями
    f.append(arrow(240, 150, 240, 205, color="#2563eb", sw=1.5))
    f.append(arrow(240, 310, 240, 365, color="#2563eb", sw=1.5))
    f.append(arrow(620, 470, 620, 525, color="#16a34a", sw=1.5))

    f.append(fitbox(30, 680, 980, 35,
                    "Валідатор спускається від Root KSK до RRSIG: кожен рівень засвідчує підлинність ключа наступного рівня",
                    size=12, bold=True, fill="#ffffff", stroke="#94a3b8"))

    render(os.path.join(OUT, 'dnssec-chain-of-trust.svg'), W, H, *f,
           title="Ланцюг довіри DNSSEC від кореня до домену")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Порівняння підтвердження неіснування: NSEC проти NSEC3
# ─────────────────────────────────────────────────────────────────────────────
def fig_nsec_vs_nsec3():
    W, H = 1040, 580
    f = []

    f.append(text(40, 35, "Підтвердження неіснування записів: відкрите кільце NSEC проти хешованого NSEC3",
                  size=14, color=TEXT_DARK, anchor="start", bold=True))

    # Верхня панель - NSEC
    f.append(rect(30, 60, 980, 220, fill=SOFT_BLUE, stroke=BORDER_GRAY, sw=1.2, rx=10))
    f.append(text(50, 85, "1. NSEC (RFC 4034): Лексикографічне зв'язане кільце дійсних імен",
                  size=13, color=TEXT_MUTED, anchor="start", bold=True))

    nsec_nodes = [
        (130, 145, "api.example.ua\n(NSEC -> mail)"),
        (430, 145, "mail.example.ua\n(NSEC -> www)"),
        (730, 145, "www.example.ua\n(NSEC -> api)"),
    ]

    for cx, cy, label in nsec_nodes:
        b, w, _ = box(cx, cy, label, size=11, fill="#ffffff", bold=True)
        f.append(b)

    f.append(arrow(210, 145, 350, 145, color="#2563eb", sw=1.5))
    f.append(arrow(510, 145, 650, 145, color="#2563eb", sw=1.5))
    f.append(arrow(730, 175, 130, 175, color="#dc2626", sw=1.5)) # Замикання кільця

    f.append(fitbox(50, 215, 940, 50,
                    "Запит на 'blog.example.ua': повертається NSEC між 'api' та 'mail'. Доведеться, що blog не існує, але відкривається весь список імен зони (Zone Walking).",
                    size=11, fill="#ffffff", stroke="#94a3b8"))

    # Нижня панель - NSEC3
    f.append(rect(30, 300, 980, 240, fill=WARM_ORANGE, stroke=BORDER_GRAY, sw=1.2, rx=10))
    f.append(text(50, 325, "2. NSEC3 (RFC 5155): Хешований простір імен із солю (Salt)",
                  size=13, color=TEXT_MUTED, anchor="start", bold=True))

    nsec3_nodes = [
        (140, 385, "H(api) = 2v1... \n(NSEC3 -> 7b9...)"),
        (440, 385, "H(mail) = 7b9...\n(NSEC3 -> k4m...)"),
        (740, 385, "H(www) = k4m...\n(NSEC3 -> 2v1...)"),
    ]

    for cx, cy, label in nsec3_nodes:
        b, w, _ = box(cx, cy, label, size=11, fill="#ffffff", bold=True)
        f.append(b)

    f.append(arrow(230, 385, 350, 385, color="#d97706", sw=1.5))
    f.append(arrow(530, 385, 650, 385, color="#d97706", sw=1.5))
    f.append(arrow(740, 415, 140, 415, color="#dc2626", sw=1.5))

    f.append(fitbox(50, 455, 940, 65,
                    "Запит на 'blog.example.ua': обчислюється H('blog') = 4q2... Повертається NSEC3 проміжку [2v1... 7b9...]. Доведено відсутність без розкриття вихідних імен зони.",
                    size=11, fill="#ffffff", stroke="#94a3b8"))

    render(os.path.join(OUT, 'nsec-vs-nsec3.svg'), W, H, *f,
           title="Порівняння записів NSEC та NSEC3 у DNSSEC")


if __name__ == "__main__":
    fig_chain_of_trust()
    fig_nsec_vs_nsec3()
    print("Figures generated successfully in img/")
