# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── hash — короткий відбиток, зміна на біт міняє все ──────────────────────────
# Ідея: хеш бере дані будь-якого розміру й дає коротке число сталої довжини;
# зміна навіть на біт дає геть інший відбиток; назад не відновити.

def fig_hash():
    W, H = 760, 260
    p = [rect(40, 70, 250, 60, fill="#ffffff", stroke=INK, sw=1.6, rx=8)]
    p.append(text(165, 96, "«привіт»", size=13, color=INK))
    p.append(text(165, 118, "дані будь-якого розміру", size=9, color=MUTED))
    p.append(arrow(290, 100, 380, 100, color=INK, sw=2.2))
    p.append(text(335, 88, "Hash", size=10, color=INK, bold=True))
    b, _, _ = textbox(470, 100, "3F A9 1C", size=14, color="#8a6d1a",
                      fill="#fff6e0", stroke="#caa24a", bold=True, min_w=130)
    p.append(b)
    p.append(text(470, 140, "коротке число сталої довжини", size=9, color=MUTED))
    # зміна на біт
    p.append(rect(40, 170, 250, 50, fill="#ffffff", stroke=POS, sw=1.6, rx=8))
    p.append(text(165, 200, "«привіт.»  (один знак)", size=12, color=POS))
    p.append(arrow(290, 195, 380, 195, color=POS, sw=2.2))
    b, _, _ = textbox(470, 195, "C7 02 EE", size=13, color=POS,
                      fill="#fbecec", stroke=POS, bold=True, min_w=130)
    p.append(b)
    p.append(text(W / 2, 244, "Зміна на біт — геть інший відбиток; однобічний (назад не відновити), без колізій.",
                  size=10, color=MUTED))
    render(os.path.join(OUT, "hash.svg"), W, H, *p,
           title="Хеш: з великих даних — короткий відбиток")


# ── sign — хешуй, підпиши таємним, перевір відкритим ──────────────────────────
# Ідея: автор хешує дані й підписує відбиток таємним ключем; отримувач сам
# хешує дані, відкритим ключем добуває закладений відбиток і звіряє.

def fig_sign():
    W, H = 760, 280
    # автор
    p = [rect(40, 60, 320, 100, fill="#ffffff", stroke=INK, sw=1.8, rx=10)]
    p.append(text(200, 84, "автор", size=12, color=INK, bold=True))
    p.append(text(200, 110, "h = Hash(дані)", size=11, color=MUTED))
    b, _, _ = textbox(200, 138, "s = Sign(h, таємний ключ)", size=11, color="#8a6d1a",
                      fill="#fff6e0", stroke="#caa24a", bold=True, min_w=240)
    p.append(b)
    p.append(arrow(360, 110, 440, 110, color=MUTED, sw=2.2))
    p.append(text(400, 98, "дані + s", size=9, color=MUTED))
    # отримувач
    p.append(rect(440, 60, 280, 100, fill="#ffffff", stroke=INK, sw=1.8, rx=10))
    p.append(text(580, 84, "отримувач", size=12, color=INK, bold=True))
    p.append(text(580, 108, "сам рахує Hash(дані)", size=10, color=MUTED))
    p.append(text(580, 128, "відкритим добуває закладений h", size=10, color=MUTED))
    p.append(text(580, 148, "і звіряє", size=10, color=INK, bold=True))
    p.append(fitbox(120, 196, 520, 56,
                    "Збіг → дані справжні й цілі.\n"
                    "Розбіжність → підробка: підмінені дані або чужий підпис.",
                    size=11, color=INK, fill="#fbfbfb", stroke=MUTED, sw=1.4))
    render(os.path.join(OUT, "sign.svg"), W, H, *p,
           title="Підпис і перевірка: хешуй, підпиши, перевір")


# ── trapdoor — легко вперед, важко назад без секрету ──────────────────────────
# Ідея: однобічна дія з потаємним ходом. Помножити два прості легко; розкласти
# добуток назад — практично неможливо, ЯКЩО не знаєш множників (таємний ключ).

def fig_trapdoor():
    W, H = 760, 250
    # вперед — легко
    p = [rect(40, 60, 300, 70, fill="#eaf6ec", stroke=FIELD, sw=1.8, rx=10)]
    p.append(text(190, 86, "p = 61,  q = 53", size=12, color=INK, bold=True))
    p.append(text(190, 110, "два прості числа", size=10, color=MUTED))
    p.append(arrow(340, 95, 430, 95, color=FIELD, sw=2.6))
    p.append(text(385, 82, "×  легко", size=10, color=FIELD, bold=True))
    b, _, _ = textbox(560, 95, "n = 3233", size=14, color="#8a6d1a",
                      fill="#fff6e0", stroke="#caa24a", bold=True, min_w=150)
    p.append(b)
    # назад — важко
    p.append(arrow(430, 165, 340, 165, color=POS, sw=2.6))
    p.append(text(385, 152, "розкласти", size=10, color=POS, bold=True))
    p.append(text(385, 186, "надважко", size=10, color=POS, bold=True))
    p.append(fitbox(70, 205, 620, 34,
                    "Помножити — легко в один бік; розкласти велике n назад на множники — "
                    "практично неможливо. Це і є «потаємний хід».",
                    size=11, color=INK, fill="#fbfbfb", stroke=MUTED, sw=1.4))
    render(os.path.join(OUT, "trapdoor.svg"), W, H, *p,
           title="Однобічна дія з потаємним ходом: легко вперед, важко назад")


if __name__ == "__main__":
    fig_hash()
    fig_sign()
    fig_trapdoor()
    print("figs: 3 written to", OUT)
