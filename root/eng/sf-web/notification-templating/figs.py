#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми notification-templating."""

import sys
import os

# Додаємо scripts до шляху імпорту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, textbox, fitbox, rect, line, arrow, text, mtext, circle,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG, FONT
)

def fig_pipeline(path):
    """Ілюстрація: Архітектурний конвеєр рендерингу та локалізації сповіщень."""
    w, h = 880, 520
    frags = []

    # Верхній рівень: Вхідні дані
    frags.append(rect(20, 20, 410, 110, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(225, 42, "Канонічна бізнес-подія (Canonical Event)", size=13, bold=True, color=INK))
    tb_ev = fitbox(30, 55, 390, 65, "event: \"order_confirmed\"\npayload: { id: \"ord_982\", amount_cents: 12999,\ncurrency: \"USD\", created_at: \"2026-08-20T10:15:30Z\" }", size=11, fill="#ffffff", stroke="#cbd5e1")
    frags.append(tb_ev)

    frags.append(rect(450, 20, 410, 110, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(655, 42, "Контекст отримувача (Recipient Context)", size=13, bold=True, color=INK))
    tb_usr = fitbox(460, 55, 390, 65, "recipient: { user_id: \"usr_42\", locale: \"uk-UA\",\ntimezone: \"Europe/Kyiv\", channels: [\"email\", \"push\", \"sms\"],\ncurrency_fmt: \"narrowSymbol\" }", size=11, fill="#ffffff", stroke="#cbd5e1")
    frags.append(tb_usr)

    # Стрілки вхідних даних до ядра
    frags.append(arrow(225, 130, 360, 175, color=LINE, sw=1.8))
    frags.append(arrow(655, 130, 520, 175, color=LINE, sw=1.8))

    # Центральний рівень: Вузол рендерингу (Notification Engine)
    frags.append(rect(20, 175, 840, 175, fill="#f0f7ff", stroke=NEG, sw=2, rx=10))
    frags.append(text(440, 200, "Вузол шаблонізації та локалізації (Templating & Localization Engine)", size=14, bold=True, color=NEG))

    tb_reg, _, _ = textbox(165, 260, "Реєстр шаблонів\n• Версіонування (v2.1)\n• AST Cache (LRU в RAM)\n• Fallback каскад локалей", size=11, pad=8, fill="#ffffff", stroke=LINE)
    tb_icu, _, _ = textbox(440, 260, "Рушій i18n / CLDR\n• ICU Plural Rules (uk: 3 форми)\n• Форматування сум ($129.99 / 129,99 $)\n• Конвертація дат (UTC -> Kyiv)", size=11, pad=8, fill="#ffffff", stroke=FIELD)
    tb_sec, _, _ = textbox(715, 260, "Пісочниця та Безпека\n• Захист від SSTI (No eval)\n• Context-Aware Escaping\n• Ліміти CPU та глибини AST", size=11, pad=8, fill="#ffffff", stroke=POS)
    frags.extend([tb_reg, tb_icu, tb_sec])

    frags.append(arrow(275, 260, 325, 260, color=LINE, sw=1.5))
    frags.append(arrow(555, 260, 605, 260, color=LINE, sw=1.5))

    # Стрілки вниз до каналів
    frags.append(arrow(130, 350, 130, 395, color=LINE, sw=1.8))
    frags.append(arrow(330, 350, 330, 395, color=LINE, sw=1.8))
    frags.append(arrow(550, 350, 550, 395, color=LINE, sw=1.8))
    frags.append(arrow(750, 350, 750, 395, color=LINE, sw=1.8))

    # Нижній рівень: Канали та артефакти доставки
    tb_em = fitbox(20, 395, 200, 105, "Email Adapter\n• Responsive HTML\n• Inlined CSS\n• Plaintext Fallback\n• multipart/alternative", size=11, fill="#ffffff", stroke=LINE)
    tb_pu = fitbox(230, 395, 200, 105, "Push Adapter\n• APNs / FCM JSON\n• Title / Body (<4 KB)\n• Deep-link route data\n• UTF-8 Truncation", size=11, fill="#ffffff", stroke=LINE)
    tb_sm = fitbox(440, 395, 200, 105, "SMS Adapter\n• GSM-7 (160 зн.)\n• UCS-2 (70 зн. кирилиця)\n• UDH-сегментація\n• Контроль бюджету", size=11, fill="#ffffff", stroke=LINE)
    tb_ia = fitbox(650, 395, 210, 105, "In-App / Slack Adapter\n• UI Block Kit\n• Динамічні кнопки дії\n• JSON картка картки\n• Медіа-прев'ю", size=11, fill="#ffffff", stroke=LINE)
    frags.extend([tb_em, tb_pu, tb_sm, tb_ia])

    render(path, w, h, *frags)

def fig_locale_plural_ast(path):
    """Ілюстрація: Синтаксичне дерево ICU MessageFormat та вибір форми множини за CLDR."""
    w, h = 840, 440
    frags = []

    # Вхідний рядок шаблону
    frags.append(rect(20, 15, 800, 60, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(420, 35, "Вхідний шаблон ICU MessageFormat", size=12, bold=True, color=MUTED))
    frags.append(text(420, 58, "\"{name}, ви маєте {count, plural, one{# нове завдання} few{# нові завдання} many{# нових завдань} other{# нового завдання}}\"", size=11, bold=True, color=INK))

    # Корінь AST
    frags.append(arrow(420, 75, 420, 105, color=LINE, sw=1.8))
    tb_root, _, _ = textbox(420, 125, "Message AST Root\n[Послідовність вузлів]", size=12, pad=6, fill="#eaf0fd", stroke=NEG)
    frags.append(tb_root)

    # Вузли дерева
    frags.append(arrow(340, 145, 160, 185, color=LINE, sw=1.5))
    frags.append(arrow(420, 145, 420, 185, color=LINE, sw=1.5))
    frags.append(arrow(500, 145, 660, 185, color=LINE, sw=1.5))

    tb_n1, _, _ = textbox(160, 205, "ArgumentNode\nvar: \"name\"\n(Екранування тексту)", size=11, pad=6, fill="#ffffff", stroke=LINE)
    tb_n2, _, _ = textbox(420, 205, "LiteralNode\nvalue: \", ви маєте \"", size=11, pad=6, fill="#ffffff", stroke=LINE)
    tb_n3, _, _ = textbox(660, 205, "PluralNode (CLDR)\nvar: \"count\", offset: 0\n(Розгалуження форм)", size=11, pad=6, fill="#edf7ed", stroke=FIELD)
    frags.extend([tb_n1, tb_n2, tb_n3])

    # Гілки Plural
    frags.append(arrow(600, 235, 520, 275, color=FIELD, sw=1.5))
    frags.append(arrow(640, 235, 615, 275, color=FIELD, sw=1.5))
    frags.append(arrow(680, 235, 710, 275, color=FIELD, sw=1.5))
    frags.append(arrow(720, 235, 795, 275, color=FIELD, sw=1.5))

    tb_b1, _, _ = textbox(520, 295, "one\n(# % 10 = 1)", size=10, pad=4, fill="#f8fafc", stroke=LINE)
    tb_b2, _, _ = textbox(615, 295, "few\n(# % 10 in 2..4)", size=10, pad=4, fill="#edf7ed", stroke=FIELD, bold=True)
    tb_b3, _, _ = textbox(710, 295, "many\n(# % 10 in 0,5..9)", size=10, pad=4, fill="#f8fafc", stroke=LINE)
    tb_b4, _, _ = textbox(795, 295, "other\n(дробові)", size=10, pad=4, fill="#f8fafc", stroke=LINE)
    frags.extend([tb_b1, tb_b2, tb_b3, tb_b4])

    # Блок обчислення
    frags.append(rect(20, 345, 800, 80, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    frags.append(text(420, 368, "Обчислення для контексту: { name: \"Олена\", count: 23, locale: \"uk-UA\" }", size=12, bold=True, color=FIELD))
    frags.append(text(420, 390, "1. name = \"Олена\" | 2. 23 mod 10 = 3 (не 13) -> категорія 'few' -> \"23 нові завдання\"", size=11, color=INK))
    frags.append(text(420, 412, "Результат: \"Олена, ви маєте 23 нові завдання\"", size=12, bold=True, color=INK))

    render(path, w, h, *frags)

def fig_email_layout_compilation(path):
    """Ілюстрація: Композиція HTML-листа, інлайнінг стилів та генерація текстового двійника."""
    w, h = 840, 420
    frags = []

    # Ліва колонка: Джерела
    frags.append(rect(20, 25, 230, 370, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(135, 50, "Компоненти шаблону", size=13, bold=True, color=INK))

    tb_c1 = fitbox(30, 65, 210, 85, "1. Base Shell Layout\n• <!DOCTYPE html>\n• Шапка бренду\n• Підвал & Unsubscribe\n• <slot id=\"content\"/>", size=10, fill="#ffffff", stroke=LINE)
    tb_c2 = fitbox(30, 160, 210, 85, "2. Body Partial\n• ICU локалізований текст\n• Таблиця товарів <table>\n• CTA Кнопка переходу\n• Параметри трекінгу", size=10, fill="#ffffff", stroke=FIELD)
    tb_c3 = fitbox(30, 255, 210, 85, "3. Channel CSS\n• Класи .button, .card\n• Адаптивні @media\n• Підтримка Dark Mode\n• Нормалізація для Outlook", size=10, fill="#ffffff", stroke=NEG)
    frags.extend([tb_c1, tb_c2, tb_c3])

    frags.append(arrow(250, 210, 290, 210, color=LINE, sw=2))

    # Центральна колонка: Компілятор та Інлайнер
    frags.append(rect(290, 25, 245, 370, fill="#f0f7ff", stroke=NEG, sw=2, rx=8))
    frags.append(text(412, 50, "Конвеєр збірки листа", size=13, bold=True, color=NEG))

    tb_p1 = fitbox(302, 75, 220, 65, "Вбудовування слота\nСклеювання Base Shell та Body Partial у єдине HTML-дерево", size=11, fill="#ffffff", stroke=LINE)
    tb_p2 = fitbox(302, 150, 220, 85, "CSS Inliner Engine\nПарсинг <style> та прописування правил у атрибути style=\"...\"\n(Захист від вирізання Gmail)", size=11, fill="#ffffff", stroke=NEG)
    tb_p3 = fitbox(302, 245, 220, 85, "Генератор Plaintext\nВилучення тегів, перетворення <a> на посилання в дужках,\nтаблиць на списки з відступами", size=11, fill="#ffffff", stroke=FIELD)
    frags.extend([tb_p1, tb_p2, tb_p3])

    frags.append(arrow(535, 210, 575, 210, color=LINE, sw=2))

    # Права колонка: Вихідний MIME-пакет
    frags.append(rect(575, 25, 245, 370, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(697, 50, "Готовий MIME Payload", size=13, bold=True, color=INK))

    tb_m1 = fitbox(587, 75, 220, 80, "MIME Headers\nContent-Type: multipart/alternative;\nboundary=\"----=_Part_42\"\nSubject: Замовлення підтверджено", size=10, fill="#ffffff", stroke=LINE)
    tb_m2 = fitbox(587, 165, 220, 95, "Part 1: text/plain\nПривіт, Олено!\nВаше замовлення #982 підтверджено на суму $129.99.\nПереглянути: https://...", size=10, fill="#ffffff", stroke=FIELD)
    tb_m3 = fitbox(587, 270, 220, 110, "Part 2: text/html\n<table style=\"width:100%\">\n  <tr><td style=\"color:#1a1a1a\">\n    Привіт, Олено!...\n  </td></tr>\n</table>", size=10, fill="#ffffff", stroke=NEG)
    frags.extend([tb_m1, tb_m2, tb_m3])

    render(path, w, h, *frags)

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    
    fig_pipeline(os.path.join(out_dir, "pipeline.svg"))
    fig_locale_plural_ast(os.path.join(out_dir, "locale-plural-ast.svg"))
    fig_email_layout_compilation(os.path.join(out_dir, "email-layout-compilation.svg"))
    print("Згенеровано 3 ілюстрації в img/")
