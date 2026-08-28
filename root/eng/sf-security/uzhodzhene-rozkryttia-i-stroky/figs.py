# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# 1. cvd-lifecycle-and-embargo
def fig_cvd_lifecycle_and_embargo():
    W, H = 840, 360
    p = []

    # Title background banner
    p.append(rect(20, 20, 800, 45, fill='#f8fafc', stroke=LINE, sw=1.4, rx=6))
    p.append(text(420, 48, 'Життєвий цикл CVD та шкала ембарго (ISO/IEC 29147 / 30111)', size=13, color=INK, bold=True))

    # Phase boxes
    phases = [
        ('1. Виявлення та звіт', ['День 0 (T_0)', 'Звіт через PGP', 'security.txt'], 100, '#f0f4f8', NEG),
        ('2. Тріаж і валідація', ['Дні 1–7', 'Підтвердження бага', 'CVE Reserved'], 250, '#f0faf4', FIELD),
        ('3. Розробка патча', ['Дні 8–75', 'Root Cause аналіз', 'Тести на регресію'], 400, '#fdfbf0', INK),
        ('4. Пре-нотифікація', ['Дні 76–90', 'Downstream партнери', 'Угода про ембарго'], 550, '#fef6f0', POS),
        ('5. Публічний реліз', ['День 90 (+14)', 'Бюлетень безпеки', 'CVE Published'], 700, '#f0faf4', FIELD)
    ]

    for title_text, lines, cx, fill_color, stroke_color in phases:
        p.append(rect(cx - 65, 85, 130, 110, fill=fill_color, stroke=stroke_color, sw=1.6, rx=6))
        p.append(text(cx, 108, title_text, size=11, color=stroke_color, bold=True))
        for idx, line_text in enumerate(lines):
            p.append(text(cx, 135 + idx * 20, line_text, size=9, color=INK))

    # Connecting arrows between phases
    p.append(arrow(168, 140, 182, 140, color=LINE, sw=1.6))
    p.append(arrow(318, 140, 332, 140, color=LINE, sw=1.6))
    p.append(arrow(468, 140, 482, 140, color=LINE, sw=1.6))
    p.append(arrow(618, 140, 632, 140, color=LINE, sw=1.6))

    # Timeline bar
    p.append(rect(35, 220, 770, 35, fill='#ffffff', stroke=LINE, sw=1.4, rx=4))
    
    # 90-day embargo segment
    p.append(rect(35, 220, 630, 35, fill='#edf2f7', stroke=NEG, sw=1.5, rx=4))
    p.append(text(350, 242, 'Стандартне 90-денне ембарго (Google Project Zero / CERT/CC)', size=11, color=NEG, bold=True))

    # 14-day grace period segment
    p.append(rect(665, 220, 140, 35, fill='#fef3c7', stroke=POS, sw=1.5, rx=4))
    p.append(text(735, 242, '+14 днів Grace', size=10, color=POS, bold=True))

    # Timeline markers
    p.append(line(35, 212, 35, 263, color=LINE, sw=1.8))
    p.append(text(35, 280, '0d (Звіт)', size=9, color=MUTED))

    p.append(line(175, 212, 175, 263, color=LINE, sw=1.2, dash='3,3'))
    p.append(text(175, 280, '7d (SLA)', size=9, color=MUTED))

    p.append(line(665, 212, 665, 263, color=NEG, sw=1.8))
    p.append(text(665, 280, '90d (Дедлайн)', size=9, color=NEG, bold=True))

    p.append(line(805, 212, 805, 263, color=POS, sw=1.8))
    p.append(text(805, 280, '104d (Крайній строк)', size=9, color=POS, bold=True))

    # Bottom notes
    p.append(rect(35, 305, 770, 40, fill='#fafafa', stroke=MUTED, sw=1.0, rx=4))
    p.append(text(420, 323, 'Правило перенесення: якщо дедлайн припадає на вихідний або святковий день, розкриття переноситься на наступний робочий день.', size=9, color=MUTED))
    p.append(text(420, 337, 'Публікація деталей відбувається незалежно від готовності патча виробником після вичерпання строків.', size=9, color=POS))

    render(os.path.join(OUT, 'cvd-lifecycle-and-embargo.svg'), W, H, *p,
           title='Життєвий цикл CVD та шкала ембарго')


# 2. multiparty-coordination-hub
def fig_multiparty_coordination_hub():
    W, H = 840, 370
    p = []

    # Title
    p.append(rect(20, 15, 800, 40, fill='#f8fafc', stroke=LINE, sw=1.4, rx=6))
    p.append(text(420, 40, 'Модель багатосторонньої координації вразливостей (MPCVD Hub)', size=13, color=INK, bold=True))

    # Left: Researcher / Finder
    p.append(rect(30, 80, 170, 160, fill='#f0f4f8', stroke=NEG, sw=1.6, rx=6))
    p.append(text(115, 105, 'Дослідник безпеки', size=11, color=NEG, bold=True))
    p.append(text(115, 122, '(Security Researcher)', size=9, color=MUTED))
    p.append(text(115, 150, '• Пошук вразливості', size=9, color=INK))
    p.append(text(115, 172, '• Створення PoC', size=9, color=INK))
    p.append(text(115, 194, '• Первинний звіт', size=9, color=INK))
    p.append(text(115, 216, '• Згода на ембарго', size=9, color=FIELD, bold=True))

    # Center: Coordinator Hub (CERT/CC, CISA, CERT-UA)
    p.append(rect(240, 70, 240, 185, fill='#f0faf4', stroke=FIELD, sw=1.8, rx=8))
    p.append(text(360, 95, 'Координаційний центр', size=12, color=FIELD, bold=True))
    p.append(text(360, 113, '(CERT/CC / CISA / CERT-UA)', size=9, color=MUTED))
    p.append(text(360, 140, '1. Верифікація та скоринг CVSS', size=9, color=INK))
    p.append(text(360, 160, '2. Резервування CVE ID (CNA)', size=9, color=INK))
    p.append(text(360, 180, '3. Синхронізація дати ембарго', size=9, color=INK))
    p.append(text(360, 200, '4. Розподіл закритої інформації', size=9, color=INK))
    p.append(text(360, 220, '5. Моніторинг активних витоків', size=9, color=POS, bold=True))

    # Top Right: Upstream Maintainer
    p.append(rect(520, 68, 290, 88, fill='#fdfbf0', stroke=INK, sw=1.5, rx=6))
    p.append(text(665, 90, 'Upstream розробник (Linux / OpenSSL)', size=11, color=INK, bold=True))
    p.append(text(665, 110, '• Розробка та перевірка виправлення', size=9, color=INK))
    p.append(text(665, 130, '• Закрите тестування в приватних гілках', size=9, color=MUTED))

    # Bottom Right: Downstream Integrators under NDA
    p.append(rect(520, 168, 290, 102, fill='#fef6f0', stroke=POS, sw=1.5, rx=6))
    p.append(text(665, 190, 'Downstream партнери (Tier 1/2)', size=11, color=POS, bold=True))
    p.append(text(665, 210, '• Хмарні провайдери (AWS, Azure, GCP)', size=9, color=INK))
    p.append(text(665, 228, '• Дистрибутиви ОС (Debian, RHEL, Ubuntu)', size=9, color=INK))
    p.append(text(665, 246, '• Патчинг інфраструктури до зняття ембарго', size=9, color=FIELD))

    # Arrows between parties
    p.append(arrow(200, 160, 235, 160, color=NEG, sw=1.8))
    p.append(text(218, 148, 'Звіт', size=9, color=NEG))

    p.append(arrow(480, 112, 515, 112, color=FIELD, sw=1.6))
    p.append(arrow(515, 128, 480, 128, color=LINE, sw=1.6))

    p.append(arrow(480, 215, 515, 215, color=FIELD, sw=1.6))

    # Bottom Public Output
    p.append(rect(140, 290, 560, 60, fill='#ffffff', stroke=FIELD, sw=1.6, rx=6))
    p.append(text(420, 312, 'Синхронний публічний реліз (Coordinated Public Release)', size=11, color=FIELD, bold=True))
    p.append(text(420, 332, 'Одночасна публікація CVE, Security Advisory, оновлень пакунків та PoC аналізу', size=9, color=INK))

    p.append(arrow(360, 258, 360, 285, color=FIELD, sw=2.0))

    render(os.path.join(OUT, 'multiparty-coordination-hub.svg'), W, H, *p,
           title='Багатостороння координація вразливостей MPCVD')


# 3. timeline-compression-decision
def fig_timeline_compression_decision():
    W, H = 840, 380
    p = []

    # Title
    p.append(rect(20, 15, 800, 40, fill='#f8fafc', stroke=LINE, sw=1.4, rx=6))
    p.append(text(420, 40, 'Дерево рішень: скорочення строків розкриття (Emergency Disclosure)', size=13, color=INK, bold=True))

    # Start Node
    p.append(rect(300, 75, 240, 45, fill='#f0f4f8', stroke=NEG, sw=1.6, rx=6))
    p.append(text(420, 95, 'Виявлено та підтверджено вразливість', size=10, color=INK, bold=True))
    p.append(text(420, 110, 'Початок процесу координації (CVD)', size=9, color=MUTED))

    # Arrow to Decision 1
    p.append(arrow(420, 120, 420, 150, color=LINE, sw=1.6))

    # Decision 1: In-the-wild exploitation?
    p.append(rect(270, 155, 300, 50, fill='#fff5f5', stroke=POS, sw=1.8, rx=6))
    p.append(text(420, 177, 'Чи є ознаки активної експлуатації?', size=11, color=POS, bold=True))
    p.append(text(420, 193, '(0-day in-the-wild / атаки на користувачів)', size=9, color=MUTED))

    # Branch 1: YES -> 7-day compressed timeline
    p.append(arrow(570, 180, 640, 180, color=POS, sw=2.0))
    p.append(text(605, 170, 'ТАК', size=10, color=POS, bold=True))

    p.append(rect(645, 145, 175, 88, fill='#fdf2f2', stroke=POS, sw=1.8, rx=6))
    p.append(text(732, 168, 'Екстрений дедлайн 7 днів', size=10, color=POS, bold=True))
    p.append(text(732, 188, '• Негайний реліз мітигацій', size=9, color=INK))
    p.append(text(732, 206, '• Патч або тимчасовий захист', size=9, color=INK))
    p.append(text(732, 224, '• Публічне попередження', size=9, color=POS, bold=True))

    # Branch 1: NO -> Check Decision 2
    p.append(arrow(420, 205, 420, 235, color=LINE, sw=1.6))
    p.append(text(435, 222, 'НІ', size=10, color=FIELD, bold=True))

    # Decision 2: Public leak / accidental commit?
    p.append(rect(270, 240, 300, 50, fill='#fef6f0', stroke=POS, sw=1.6, rx=6))
    p.append(text(420, 262, 'Чи стався публічний витік інформації?', size=11, color=POS, bold=True))
    p.append(text(420, 278, '(PoC у мережі, публічний коміт із фіксом)', size=9, color=MUTED))

    # Branch 2: YES -> Immediate disclosure (0-48h)
    p.append(arrow(270, 265, 200, 265, color=POS, sw=2.0))
    p.append(text(235, 255, 'ТАК', size=10, color=POS, bold=True))

    p.append(rect(20, 235, 175, 88, fill='#fff5f5', stroke=POS, sw=1.8, rx=6))
    p.append(text(107, 258, 'Миттєве розкриття (0–48г)', size=10, color=POS, bold=True))
    p.append(text(107, 278, '• Зняття режиму ембарго', size=9, color=INK))
    p.append(text(107, 296, '• Реліз поточного патча', size=9, color=INK))
    p.append(text(107, 314, '• Оповіщення про загрозу', size=9, color=POS, bold=True))

    # Branch 2: NO -> Standard 90-day CVD
    p.append(arrow(420, 290, 420, 318, color=FIELD, sw=1.8))
    p.append(text(435, 306, 'НІ', size=10, color=FIELD, bold=True))

    p.append(rect(260, 322, 320, 44, fill='#f0faf4', stroke=FIELD, sw=1.8, rx=6))
    p.append(text(420, 340, 'Стандартний процес CVD: 90 днів ембарго', size=10, color=FIELD, bold=True))
    p.append(text(420, 356, 'Планова розробка, тестування та скоординований реліз', size=9, color=MUTED))

    render(os.path.join(OUT, 'timeline-compression-decision.svg'), W, H, *p,
           title='Дерево рішень скорочення строків розкриття')


if __name__ == '__main__':
    fig_cvd_lifecycle_and_embargo()
    fig_multiparty_coordination_hub()
    fig_timeline_compression_decision()
    print("Figures generated successfully.")
