# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# 1. notification-timeline-comparison
def fig_notification_timeline_comparison():
    W, H = 840, 440
    p = []

    # Title / Header background
    p.append(rect(15, 15, 810, 410, fill='#ffffff', stroke=LINE, sw=1.5, rx=8))
    p.append(text(420, 42, 'Порівняння регуляторних строків сповіщення про інциденти та вразливості', size=13, color=INK, bold=True))

    # Time axis markers
    p.append(line(50, 85, 790, 85, color=LINE, sw=1.5))
    times = [
        (120, 'T = 0', 'Виявлення / Факт'),
        (270, '24 години', 'Раннє попередження'),
        (450, '72 години', 'Детальний звіт / GDPR'),
        (610, '4 дні (96 год)', 'SEC 8-K (суттєвість)'),
        (740, '14–30 днів', 'Фінальний звіт')
    ]
    for x, t_label, t_sub in times:
        p.append(line(x, 80, x, 90, color=LINE, sw=2.0))
        p.append(text(x, 75, t_label, size=10, color=INK, bold=True))
        p.append(text(x, 102, t_sub, size=9, color=MUTED))

    # 1. EU CRA (Cyber Resilience Act) Track
    p.append(rect(30, 118, 780, 64, fill='#f0fdf4', stroke=FIELD, sw=1.4, rx=6))
    p.append(text(85, 143, 'EU CRA', size=11, color=FIELD, bold=True))
    p.append(text(85, 161, '(Продукти/ПЗ)', size=9, color=MUTED))
    # CRA segments
    p.append(rect(145, 126, 195, 48, fill='#dcfce7', stroke=FIELD, sw=1.2, rx=4))
    p.append(text(242, 144, '24 год: Раннє сповіщення', size=10, color=FIELD, bold=True))
    p.append(text(242, 162, 'CSIRTs Network та ENISA', size=9, color=INK))

    p.append(arrow(345, 150, 368, 150, color=FIELD, sw=1.5))

    p.append(rect(372, 126, 195, 48, fill='#dcfce7', stroke=FIELD, sw=1.2, rx=4))
    p.append(text(469, 144, '72 год: Звіт про вразливість', size=10, color=FIELD, bold=True))
    p.append(text(469, 162, 'Оцінка чутливості та ризику', size=9, color=INK))

    p.append(arrow(572, 150, 628, 150, color=FIELD, sw=1.5))

    p.append(rect(632, 126, 168, 48, fill='#dcfce7', stroke=FIELD, sw=1.2, rx=4))
    p.append(text(716, 144, '14 днів: Фінальний звіт', size=10, color=FIELD, bold=True))
    p.append(text(716, 162, 'Патч або мітигація', size=9, color=INK))

    # 2. EU NIS 2 Track
    p.append(rect(30, 190, 780, 64, fill='#f0f7ff', stroke=NEG, sw=1.4, rx=6))
    p.append(text(85, 215, 'EU NIS 2', size=11, color=NEG, bold=True))
    p.append(text(85, 233, '(Критичні суб’єкти)', size=9, color=MUTED))
    # NIS 2 segments
    p.append(rect(145, 198, 195, 48, fill='#dbeafe', stroke=NEG, sw=1.2, rx=4))
    p.append(text(242, 216, '24 год: Раннє попередження', size=10, color=NEG, bold=True))
    p.append(text(242, 234, 'Підозра на зловмисний акт', size=9, color=INK))

    p.append(arrow(345, 222, 368, 222, color=NEG, sw=1.5))

    p.append(rect(372, 198, 195, 48, fill='#dbeafe', stroke=NEG, sw=1.2, rx=4))
    p.append(text(469, 216, '72 год: Сповіщення інциденту', size=10, color=NEG, bold=True))
    p.append(text(469, 234, 'Первинна оцінка тяжкості', size=9, color=INK))

    p.append(arrow(572, 222, 628, 222, color=NEG, sw=1.5))

    p.append(rect(632, 198, 168, 48, fill='#dbeafe', stroke=NEG, sw=1.2, rx=4))
    p.append(text(716, 216, '1 місяць: Підсумковий звіт', size=10, color=NEG, bold=True))
    p.append(text(716, 234, 'Root cause + транскордонність', size=9, color=INK))

    # 3. EU GDPR Track
    p.append(rect(30, 262, 780, 64, fill='#fff5f5', stroke=POS, sw=1.4, rx=6))
    p.append(text(85, 287, 'EU GDPR', size=11, color=POS, bold=True))
    p.append(text(85, 305, '(Персональні дані)', size=9, color=MUTED))
    # GDPR segments
    p.append(rect(145, 270, 215, 48, fill='#fee2e2', stroke=POS, sw=1.2, rx=4))
    p.append(text(252, 288, 'Внутрішня фіксація в реєстрі', size=10, color=POS, bold=True))
    p.append(text(252, 306, 'Оцінка ризику для суб’єктів', size=9, color=INK))

    p.append(arrow(365, 294, 388, 294, color=POS, sw=1.5))

    p.append(rect(392, 270, 190, 48, fill='#fee2e2', stroke=POS, sw=1.2, rx=4))
    p.append(text(487, 288, '72 год: Звіт наглядовому DPA', size=10, color=POS, bold=True))
    p.append(text(487, 306, 'Омбудсман / Регулятор (ст. 33)', size=9, color=INK))

    p.append(arrow(587, 294, 608, 294, color=POS, sw=1.5))

    p.append(rect(612, 270, 188, 48, fill='#fee2e2', stroke=POS, sw=1.2, rx=4))
    p.append(text(706, 288, 'Негайне сповіщення людей', size=10, color=POS, bold=True))
    p.append(text(706, 306, 'Якщо високий ризик (ст. 34)', size=9, color=POS))

    # 4. US SEC Form 8-K Track
    p.append(rect(30, 334, 780, 64, fill='#faf5ff', stroke='#7c3aed', sw=1.4, rx=6))
    p.append(text(85, 359, 'US SEC 8-K', size=11, color='#7c3aed', bold=True))
    p.append(text(85, 377, '(Публічні компанії)', size=9, color=MUTED))
    # SEC segments
    p.append(rect(145, 342, 245, 48, fill='#ede9fe', stroke='#7c3aed', sw=1.2, rx=4))
    p.append(text(267, 360, 'Аналіз матеріальності інциденту', size=10, color='#7c3aed', bold=True))
    p.append(text(267, 378, 'Оцінка фінансового впливу', size=9, color=INK))

    p.append(arrow(395, 366, 440, 366, color='#7c3aed', sw=1.5))

    p.append(rect(445, 342, 355, 48, fill='#ede9fe', stroke='#7c3aed', sw=1.2, rx=4))
    p.append(text(622, 360, '4 робочі дні від визначення суттєвості', size=10, color='#7c3aed', bold=True))
    p.append(text(622, 378, 'Публічне розкриття Item 1.05 у системі EDGAR', size=9, color=INK))

    render(os.path.join(OUT, 'notification-timeline-comparison.svg'), W, H, *p,
           title='Порівняння регуляторних строків сповіщення про інциденти та вразливості')


# 2. incident-triage-and-dispatch-flow
def fig_incident_triage_flow():
    W, H = 820, 440
    p = []

    # Detection & Triage Root
    p.append(rect(295, 15, 230, 52, fill='#ffffff', stroke=LINE, sw=1.6, rx=6))
    p.append(text(410, 37, 'Виявлення безпекової події', size=12, color=INK, bold=True))
    p.append(text(410, 55, 'SIEM, PSIRT, звіт дослідника, лог', size=9, color=MUTED))

    p.append(arrow(410, 70, 410, 95, color=LINE, sw=1.8))

    # Triage decision block
    p.append(rect(255, 98, 310, 52, fill='#f4f6f8', stroke=LINE, sw=1.5, rx=6))
    p.append(text(410, 120, 'Тріаж та кваліфікація події', size=12, color=INK, bold=True))
    p.append(text(410, 138, 'Перевірка експлуатабельності та шкоди', size=9, color=MUTED))

    # 3 Main Classification Branches
    p.append(arrow(320, 153, 145, 188, color=FIELD, sw=1.6))
    p.append(arrow(410, 153, 410, 188, color=NEG, sw=1.6))
    p.append(arrow(500, 153, 675, 188, color=POS, sw=1.6))

    # Branch 1: CRA / Vulnerability
    p.append(rect(25, 192, 240, 70, fill='#f0fdf4', stroke=FIELD, sw=1.5, rx=6))
    p.append(text(145, 214, 'Активно експлуатована', size=11, color=FIELD, bold=True))
    p.append(text(145, 230, 'вразливість у продукті', size=11, color=FIELD, bold=True))
    p.append(text(145, 249, 'CRA Art. 14 / ISO 29147', size=9, color=MUTED))

    # Branch 2: NIS 2 / Operational Incident
    p.append(rect(290, 192, 240, 70, fill='#f0f7ff', stroke=NEG, sw=1.5, rx=6))
    p.append(text(410, 214, 'Суттєвий кіберінцидент', size=11, color=NEG, bold=True))
    p.append(text(410, 230, 'в інфраструктурі/сервісі', size=11, color=NEG, bold=True))
    p.append(text(410, 249, 'NIS 2 Art. 23 / DORA', size=9, color=MUTED))

    # Branch 3: GDPR / Data Breach
    p.append(rect(555, 192, 240, 70, fill='#fff5f5', stroke=POS, sw=1.5, rx=6))
    p.append(text(675, 214, 'Витік або компрометація', size=11, color=POS, bold=True))
    p.append(text(675, 230, 'персональних даних (PII)', size=11, color=POS, bold=True))
    p.append(text(675, 249, 'GDPR Art. 33/34', size=9, color=MUTED))

    # Next layer: Dispatch Channels
    p.append(arrow(145, 265, 145, 295, color=FIELD, sw=1.6))
    p.append(arrow(410, 265, 410, 295, color=NEG, sw=1.6))
    p.append(arrow(675, 265, 675, 295, color=POS, sw=1.6))

    # Dispatch Targets CRA
    p.append(rect(25, 298, 240, 122, fill='#ffffff', stroke=FIELD, sw=1.4, rx=6))
    p.append(text(145, 320, 'Канал: CSIRTs & ENISA', size=11, color=FIELD, bold=True))
    p.append(text(145, 340, '1. 24h Early Warning', size=10, color=INK))
    p.append(text(145, 358, '2. 72h Vulnerability Notice', size=10, color=INK))
    p.append(text(145, 376, '3. Сповіщення OEM/користувачів', size=10, color=INK))
    p.append(text(145, 396, '4. Патч + CSAF/VEX', size=10, color=FIELD, bold=True))

    # Dispatch Targets NIS 2
    p.append(rect(290, 298, 240, 122, fill='#ffffff', stroke=NEG, sw=1.4, rx=6))
    p.append(text(410, 320, 'Канал: Національний CSIRT', size=11, color=NEG, bold=True))
    p.append(text(410, 340, '1. 24h Early Warning (атака)', size=10, color=INK))
    p.append(text(410, 358, '2. 72h Incident Notification', size=10, color=INK))
    p.append(text(410, 376, '3. Сповіщення клієнтів сервісу', size=10, color=INK))
    p.append(text(410, 396, '4. 1m Фінальний аналіз причин', size=10, color=NEG, bold=True))

    # Dispatch Targets GDPR
    p.append(rect(555, 298, 240, 122, fill='#ffffff', stroke=POS, sw=1.4, rx=6))
    p.append(text(675, 320, 'Канал: Наглядовий орган (DPA)', size=11, color=POS, bold=True))
    p.append(text(675, 340, '1. 72h Звіт регулятору (Art 33)', size=10, color=INK))
    p.append(text(675, 358, '2. Оцінка ризику для осіб', size=10, color=INK))
    p.append(text(675, 376, '3. Публічне / пряме сповіщення', size=10, color=INK))
    p.append(text(675, 396, '4. Запис у внутрішній журнал', size=10, color=POS, bold=True))

    render(os.path.join(OUT, 'incident-triage-and-dispatch-flow.svg'), W, H, *p,
           title='Дерево рішень тріажу та диспетчеризації обов’язкових сповіщень')


# 3. supply-chain-disclosure-cascade
def fig_supply_chain_disclosure():
    W, H = 840, 340
    p = []

    # Node 1: Upstream Component / Open-Source / Chipset
    p.append(rect(20, 50, 225, 140, fill='#fdf4ff', stroke='#a855f7', sw=1.5, rx=6))
    p.append(text(132, 75, 'Upstream постачальник', size=11, color='#a855f7', bold=True))
    p.append(text(132, 93, '(Бібліотека, RTOS, SoC)', size=9, color=MUTED))
    p.append(line(35, 105, 230, 105, color='#e9d5ff', sw=1.0))
    p.append(text(132, 125, '• Виявлення 0-day дірки', size=10, color=INK))
    p.append(text(132, 143, '• Призначення CVE-ID', size=10, color=INK))
    p.append(text(132, 163, '• Старт ембарго під CVD', size=10, color='#a855f7', bold=True))

    p.append(arrow(250, 120, 290, 120, color='#a855f7', sw=2.0))
    p.append(text(270, 110, 'Ембарго', size=9, color='#a855f7', bold=True))

    # Node 2: OEM Product Manufacturer
    p.append(rect(295, 40, 245, 165, fill='#eff6ff', stroke=NEG, sw=1.6, rx=6))
    p.append(text(417, 65, 'OEM-виробник пристрою', size=12, color=NEG, bold=True))
    p.append(text(417, 83, '(Інтегратор прошивки/ПЗ)', size=9, color=MUTED))
    p.append(line(310, 95, 525, 95, color='#bfdbfe', sw=1.0))
    p.append(text(417, 115, '• Оцінка експлуатабельності', size=10, color=INK))
    p.append(text(417, 131, '• Генерація VEX (affected/not)', size=10, color=INK))
    p.append(text(417, 147, '• 24h/72h сповіщення CSIRT', size=10, color=NEG, bold=True))
    p.append(text(417, 165, '• Збірка захищеного оновлення', size=10, color=INK))
    p.append(text(417, 183, '• Синхронізація дати релізу', size=9, color=MUTED))

    p.append(arrow(545, 120, 585, 120, color=NEG, sw=2.0))
    p.append(text(565, 110, 'CSAF/VEX', size=9, color=NEG, bold=True))

    # Node 3: Downstream Enterprise / End Users
    p.append(rect(590, 50, 230, 140, fill='#f0fdf4', stroke=FIELD, sw=1.5, rx=6))
    p.append(text(705, 75, 'Downstream клієнти', size=11, color=FIELD, bold=True))
    p.append(text(705, 93, '(Оператори інфраструктури)', size=9, color=MUTED))
    p.append(line(605, 105, 805, 105, color='#bbf7d0', sw=1.0))
    p.append(text(705, 125, '• Автоматичний прийом VEX', size=10, color=INK))
    p.append(text(705, 143, '• Застосування патча/OTA', size=10, color=INK))
    p.append(text(705, 163, '• Мітигація на рівні мережі', size=10, color=FIELD, bold=True))

    # Bottom coordination layer
    p.append(rect(30, 240, 780, 80, fill='#f8fafc', stroke=LINE, sw=1.4, rx=6))
    p.append(text(420, 262, 'Координаційний хаб (CSIRTs Network / ENISA / CERT-UA)', size=11, color=INK, bold=True))
    p.append(text(420, 281, 'Забезпечує захищений обмін інформацією під час ембарго та запобігає завчасному розкриттю PoC', size=9, color=MUTED))
    p.append(text(420, 301, 'Штрафи за порушення строків: до 15 млн євро / 2.5% обороту за CRA; до 10 млн / 2% за NIS 2', size=9, color=POS, bold=True))

    # Vertical sync arrows
    p.append(arrow(132, 192, 132, 235, color='#a855f7', sw=1.4))
    p.append(arrow(417, 207, 417, 235, color=NEG, sw=1.4))
    p.append(arrow(705, 192, 705, 235, color=FIELD, sw=1.4))

    render(os.path.join(OUT, 'supply-chain-disclosure-cascade.svg'), W, H, *p,
           title='Каскад узгодженого розкриття вразливостей у ланцюгу постачання')


if __name__ == '__main__':
    fig_notification_timeline_comparison()
    fig_incident_triage_flow()
    fig_supply_chain_disclosure()
    print('Generated 3 figures successfully.')
