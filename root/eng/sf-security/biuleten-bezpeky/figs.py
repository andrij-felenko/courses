# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# 1. advisory-disclosure-timeline
def fig_advisory_disclosure_timeline():
    W, H = 820, 340
    p = []

    # Головна вісь часу
    p.append(line(50, 60, 770, 60, color=LINE, sw=2.0))
    p.append(arrow(750, 60, 780, 60, color=LINE, sw=2.0))
    p.append(text(760, 45, 'Час (t)', size=11, color=MUTED, bold=True))

    # Точка T_0: Публікація бюлетеня
    p.append(circle(90, 60, 7, fill=POS, stroke=LINE, sw=1.5))
    p.append(text(90, 40, 'T_0: Реліз бюлетеня', size=11, color=POS, bold=True))
    p.append(text(90, 24, 'Патч + Advisory', size=9, color=MUTED))

    # Вісь нападника (верхній блок / червоний)
    p.append(rect(170, 85, 270, 105, fill='#fff5f5', stroke=POS, sw=1.5, rx=6))
    p.append(text(305, 105, 'Маршрут нападника (1-Day)', size=11, color=POS, bold=True))
    p.append(text(305, 125, '1. Binary diffing патча / commit log', size=10, color=INK))
    p.append(text(305, 145, '2. Складання надійного PoC-експлойту', size=10, color=INK))
    p.append(text(305, 165, '3. Автоматизоване сканування мережі', size=10, color=POS, bold=True))

    # Точка T_exploit
    p.append(circle(460, 60, 6, fill=POS, stroke=LINE, sw=1.5))
    p.append(text(460, 40, 'T_exploit', size=11, color=POS, bold=True))
    p.append(text(460, 24, 'Зброя в мережі', size=9, color=POS))

    # Вісь захисника (нижній блок / зелений)
    p.append(rect(170, 210, 580, 105, fill='#f0faf4', stroke=FIELD, sw=1.5, rx=6))
    p.append(text(460, 230, 'Маршрут захисника (Incident Response & Patching)', size=11, color=FIELD, bold=True))
    p.append(text(460, 250, '1. Оцінка ризику за бюлетенем (CVSS, CPE, версії) та активація Workarounds', size=10, color=INK))
    p.append(text(460, 270, '2. Тестування патча у staging-середовищі (сумісність, регресії)', size=10, color=INK))
    p.append(text(460, 290, '3. Повне розгортання оновлення на парку серверів (Fleet Update)', size=10, color=FIELD, bold=True))

    # Точка T_patch
    p.append(circle(710, 60, 6, fill=FIELD, stroke=LINE, sw=1.5))
    p.append(text(710, 40, 'T_patch', size=11, color=FIELD, bold=True))
    p.append(text(710, 24, 'Парк оновлено', size=9, color=FIELD))

    # Зона ризику між T_exploit та T_patch
    p.append(rect(460, 52, 250, 16, fill='#fdecea', stroke=POS, sw=1.2, rx=3))
    p.append(text(585, 64, 'Критичне вікно компрометації (Exposure Window)', size=9, color=POS, bold=True))

    render(os.path.join(OUT, 'advisory-disclosure-timeline.svg'), W, H, *p,
           title='Часова шкала безпекового розкриття та вікно компрометації')


# 2. csaf-document-tree
def fig_csaf_document_tree():
    W, H = 820, 360
    p = []

    # Кореневий вузол CSAF 2.0
    p.append(rect(330, 25, 160, 40, fill='#f4f6f8', stroke=LINE, sw=2.0, rx=6))
    p.append(text(410, 45, 'CSAF 2.0 Document', size=12, color=INK, bold=True))
    p.append(text(410, 58, 'JSON Object', size=9, color=MUTED))

    # Зв'язки від кореня
    p.append(line(350, 65, 150, 105, color=LINE, sw=1.5))
    p.append(line(410, 65, 410, 105, color=LINE, sw=1.5))
    p.append(line(470, 65, 670, 105, color=LINE, sw=1.5))

    # 1. Секція document
    p.append(rect(40, 105, 220, 115, fill='#ffffff', stroke=NEG, sw=1.5, rx=6))
    p.append(text(150, 125, 'document (Метадані)', size=11, color=NEG, bold=True))
    p.append(text(150, 145, '• title, category: csaf_security_advisory', size=9, color=INK))
    p.append(text(150, 163, '• publisher: вендор, namespace, PGP', size=9, color=INK))
    p.append(text(150, 181, '• tracking: id, status, version', size=9, color=INK))
    p.append(text(150, 199, '• references & notes', size=9, color=MUTED))

    # 2. Секція product_tree
    p.append(rect(300, 105, 220, 115, fill='#ffffff', stroke=FIELD, sw=1.5, rx=6))
    p.append(text(410, 125, 'product_tree (Каталог)', size=11, color=FIELD, bold=True))
    p.append(text(410, 145, '• branches: вендори, родини ПЗ', size=9, color=INK))
    p.append(text(410, 163, '• full_product_names (ID, назва)', size=9, color=INK))
    p.append(text(410, 181, '• cpe: cpe:2.3:a:vendor:pkg:...', size=9, color=INK))
    p.append(text(410, 199, '• purl: pkg:npm/openssl@3.0.0', size=9, color=MUTED))

    # 3. Секція vulnerabilities
    p.append(rect(560, 105, 220, 115, fill='#ffffff', stroke=POS, sw=1.5, rx=6))
    p.append(text(670, 125, 'vulnerabilities[] (Вади)', size=11, color=POS, bold=True))
    p.append(text(670, 145, '• cve: CVE-YYYY-NNNNN', size=9, color=INK))
    p.append(text(670, 163, '• cwe: CWE-787 (Out-of-bounds)', size=9, color=INK))
    p.append(text(670, 181, '• scores: CVSS v3.1 / CVSS v4.0', size=9, color=INK))
    p.append(text(670, 199, '• product_status: affected, fixed', size=9, color=POS, bold=True))

    # Зв'язки між product_tree та vulnerabilities
    p.append(arrow(410, 220, 410, 255, color=FIELD, sw=1.5))
    p.append(arrow(670, 220, 670, 255, color=POS, sw=1.5))

    # Блок зв'язку продуктового статусу та пом'якшень
    p.append(rect(230, 255, 550, 85, fill='#f8fafc', stroke=LINE, sw=1.4, rx=6))
    p.append(text(505, 275, 'Пов\'язування продукту з дією (Remediations & Threat Assessment)', size=11, color=INK, bold=True))
    p.append(text(505, 295, '• product_status: відображає product_id на матрицю (known_affected, fixed, known_not_affected)', size=9, color=INK))
    p.append(text(505, 313, '• remediations: category (vendor_fix, workaround, mitigation) + product_ids + url', size=9, color=FIELD, bold=True))
    p.append(text(505, 329, '• flags: machine-readable маркери відсутності експлуатації / VEX-статуси', size=9, color=MUTED))

    render(os.path.join(OUT, 'csaf-document-tree.svg'), W, H, *p,
           title='Ієрархічна структура машиночитних даних CSAF 2.0')


# 3. advisory-content-balance
def fig_advisory_content_balance():
    W, H = 820, 310
    p = []

    # Ліва колонка: Що обов'язково розкрити (Зелений)
    p.append(rect(30, 35, 360, 250, fill='#f0faf4', stroke=FIELD, sw=1.8, rx=8))
    p.append(text(210, 60, 'Обов\'язково розкрити (Захист)', size=13, color=FIELD, bold=True))
    p.append(text(210, 80, 'Інформація, критична для оборони систем', size=10, color=MUTED))

    items_left = [
        '• Точний діапазон версій, конфігурації та архітектури',
        '• Ідентифікатори: CVE ID, CWE клас, CVSS вектор',
        '• Умови досяжності вади (мережева, локальна, прапорці)',
        '• Інструкція оновлення та SHA-256 / PGP підписи пакетів',
        '• Тимчасові пом\'якшення (Workarounds) без простою',
        '• Індикатори компрометації (IoC) для детекції в логах'
    ]
    for i, it in enumerate(items_left):
        p.append(text(50, 110 + i * 26, it, size=10, color=INK, anchor='start'))

    # Права колонка: Чого не можна розкривати (Червоний)
    p.append(rect(430, 35, 360, 250, fill='#fff5f5', stroke=POS, sw=1.8, rx=8))
    p.append(text(610, 60, 'Категорично заборонено (Атака)', size=13, color=POS, bold=True))
    p.append(text(610, 80, 'Деталі, що автоматизують створення зброї', size=10, color=MUTED))

    items_right = [
        '• Готовий код PoC-експлойту та curl-команди атаки',
        '• Точні зміщення пам\'яті (offsets) та адреси ROP-гаджетів',
        '• Покрокові інструкції з обходу захистів (ASLR, DEP, WAF)',
        '• Готове шкідливе навантаження (shellcode / payload)',
        '• Недокументовані вторинні вразливості до їх закриття',
        '• Приховані вразливі адреси серверів жертв чи вендора'
    ]
    for i, it in enumerate(items_right):
        p.append(text(450, 110 + i * 26, it, size=10, color=POS, anchor='start'))

    render(os.path.join(OUT, 'advisory-content-balance.svg'), W, H, *p,
           title='Баланс безпекового розкриття: захисна цінність проти наступальної зброї')


if __name__ == '__main__':
    fig_advisory_disclosure_timeline()
    fig_csaf_document_tree()
    fig_advisory_content_balance()
    print('Figures generated successfully.')
