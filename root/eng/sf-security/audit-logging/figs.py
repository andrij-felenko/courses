# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# 1. audit-threat-model
def fig_audit_threat_model():
    W, H = 780, 310
    p = []

    p.append(rect(25, 30, 345, 255, fill='#fff5f5', stroke=POS, sw=1.6, rx=8))
    p.append(text(197, 56, 'Локальний файл (Вразливо)', size=13, color=POS, bold=True))
    p.append(text(197, 76, 'Звичайний текстовий лог на сервері', size=10, color=MUTED))

    p.append(rect(45, 95, 305, 55, fill='#ffffff', stroke=INK, sw=1.4, rx=6))
    p.append(text(197, 117, 'Сервер застосунку (App Server)', size=11, color=INK, bold=True))
    p.append(text(197, 137, 'Запис подій у локальний /var/log/audit.log', size=10, color=MUTED))

    p.append(arrow(197, 155, 197, 190, color=POS, sw=2.0))
    p.append(rect(45, 195, 305, 75, fill='#ffffff', stroke=POS, sw=1.5, rx=6))
    p.append(text(197, 217, 'Зловмисник здобув права root', size=11, color=POS, bold=True))
    p.append(text(197, 237, '1. sed -i \'/attacker/d\' audit.log (стирання)', size=10, color=POS))
    p.append(text(197, 255, '2. Фальсифікація міток часу та дій', size=10, color=POS))

    p.append(rect(395, 30, 360, 255, fill='#f0faf4', stroke=FIELD, sw=1.6, rx=8))
    p.append(text(575, 56, 'Незмінний контур аудиту (WORM)', size=13, color=FIELD, bold=True))
    p.append(text(575, 76, 'Криптографічний захист та ізоляція', size=10, color=MUTED))

    p.append(rect(415, 95, 320, 60, fill='#ffffff', stroke=INK, sw=1.4, rx=6))
    p.append(text(575, 115, 'Агент аудиту (Forward-Secure)', size=11, color=INK, bold=True))
    p.append(text(575, 133, 'Геш-ланцюг + знищення старих ключів', size=10, color=FIELD))
    p.append(text(575, 147, 'Потокова передача по TLS/mTLS', size=10, color=MUTED))

    p.append(arrow(575, 160, 575, 190, color=FIELD, sw=2.2))

    p.append(rect(415, 195, 320, 75, fill='#ffffff', stroke=FIELD, sw=1.5, rx=6))
    p.append(text(575, 217, 'Ізольоване WORM-сховище / SIEM', size=11, color=FIELD, bold=True))
    p.append(text(575, 237, 'Апаратна заборона перезапису (Object Lock)', size=10, color=INK))
    p.append(text(575, 255, 'Корінь Меркла публікується незалежно', size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, 'audit-threat-model.svg'), W, H, *p,
           title='Модель загроз компрометації журналу аудиту')


# 2. forward-secure-ratchet
def fig_forward_secure_ratchet():
    W, H = 780, 270
    p = []

    p.append(text(70, 50, 'Ключі HMAC:', size=11, color=MUTED, bold=True))

    p.append(rect(140, 30, 80, 36, fill='#f4f6f8', stroke=LINE, sw=1.5, rx=6))
    p.append(text(180, 53, 'K_0', size=12, color=INK, bold=True))

    p.append(arrow(225, 48, 275, 48, color=FIELD, sw=1.8))
    p.append(text(250, 40, 'H(K)', size=9, color=FIELD, bold=True))

    p.append(rect(280, 30, 80, 36, fill='#f4f6f8', stroke=LINE, sw=1.5, rx=6))
    p.append(text(320, 53, 'K_1', size=12, color=INK, bold=True))

    p.append(arrow(365, 48, 415, 48, color=FIELD, sw=1.8))
    p.append(text(390, 40, 'H(K)', size=9, color=FIELD, bold=True))

    p.append(rect(420, 30, 80, 36, fill='#f4f6f8', stroke=LINE, sw=1.5, rx=6))
    p.append(text(460, 53, 'K_2', size=12, color=INK, bold=True))

    p.append(arrow(505, 48, 555, 48, color=FIELD, sw=1.8))
    p.append(text(530, 40, 'H(K)', size=9, color=FIELD, bold=True))

    p.append(rect(560, 30, 80, 36, fill='#fdf2f2', stroke=POS, sw=1.8, rx=6))
    p.append(text(600, 53, 'K_3 (Злам)', size=11, color=POS, bold=True))

    p.append(arrow(180, 70, 180, 105, color=LINE, sw=1.4))
    p.append(arrow(320, 70, 320, 105, color=LINE, sw=1.4))
    p.append(arrow(460, 70, 460, 105, color=LINE, sw=1.4))
    p.append(arrow(600, 70, 600, 105, color=POS, sw=1.4))

    p.append(text(70, 135, 'Записи логу:', size=11, color=MUTED, bold=True))

    p.append(rect(130, 110, 100, 50, fill='#f0faf4', stroke=FIELD, sw=1.5, rx=6))
    p.append(text(180, 130, 'Запис R_0', size=11, color=INK, bold=True))
    p.append(text(180, 148, 'HMAC(K_0, R_0)', size=9, color=FIELD))

    p.append(rect(270, 110, 100, 50, fill='#f0faf4', stroke=FIELD, sw=1.5, rx=6))
    p.append(text(320, 130, 'Запис R_1', size=11, color=INK, bold=True))
    p.append(text(320, 148, 'HMAC(K_1, R_1)', size=9, color=FIELD))

    p.append(rect(410, 110, 100, 50, fill='#f0faf4', stroke=FIELD, sw=1.5, rx=6))
    p.append(text(460, 130, 'Запис R_2', size=11, color=INK, bold=True))
    p.append(text(460, 148, 'HMAC(K_2, R_2)', size=9, color=FIELD))

    p.append(rect(550, 110, 100, 50, fill='#fff5f5', stroke=POS, sw=1.5, rx=6))
    p.append(text(600, 130, 'Запис R_3', size=11, color=INK, bold=True))
    p.append(text(600, 148, 'HMAC(K_3, R_3)', size=9, color=POS))

    p.append(rect(40, 180, 700, 75, fill='#f8fafc', stroke=INK, sw=1.4, rx=8))
    p.append(text(390, 202, 'Гарантія безпеки минулого (Forward Secrecy):', size=11, color=INK, bold=True))
    p.append(text(390, 222, '1. Ключі K_0, K_1, K_2 негайно затираються в ОЗП (Zeroization)', size=10, color=MUTED))
    p.append(text(390, 240, '2. Знаючи K_3, неможливо відновити K_2 чи K_1 (одностороння функція) — минуле захищено', size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, 'forward-secure-ratchet.svg'), W, H, *p,
           title='Схема односпрямованого оновлення ключів (HMAC-Ratchet)')


# 3. merkle-transparency-log
def fig_merkle_transparency_log():
    W, H = 780, 310
    p = []

    p.append(rect(320, 25, 140, 42, fill='#f0faf4', stroke=FIELD, sw=1.8, rx=6))
    p.append(text(390, 43, 'Корінь Меркла', size=11, color=FIELD, bold=True))
    p.append(text(390, 58, 'Root = H(H_01 || H_23)', size=9, color=INK))

    p.append(line(355, 68, 235, 105, color=LINE, sw=1.6))
    p.append(line(425, 68, 545, 105, color=FIELD, sw=2.0))

    p.append(rect(165, 105, 140, 40, fill='#e8f4fd', stroke=NEG, sw=1.8, rx=6))
    p.append(text(235, 122, 'Вузол H_01 (Аудит-шлях)', size=10, color=NEG, bold=True))
    p.append(text(235, 137, 'H(0x01 || H_0 || H_1)', size=9, color=INK))

    p.append(rect(475, 105, 140, 40, fill='#f4f6f8', stroke=LINE, sw=1.5, rx=6))
    p.append(text(545, 122, 'Вузол H_23', size=10, color=INK, bold=True))
    p.append(text(545, 137, 'H(0x01 || H_2 || H_3)', size=9, color=INK))

    p.append(line(205, 146, 120, 180, color=LINE, sw=1.4))
    p.append(line(265, 146, 235, 180, color=LINE, sw=1.4))
    p.append(line(515, 146, 485, 180, color=FIELD, sw=2.0))
    p.append(line(575, 146, 660, 180, color=NEG, sw=1.8))

    p.append(rect(65, 180, 110, 36, fill='#ffffff', stroke=LINE, sw=1.4, rx=5))
    p.append(text(120, 196, 'Геш H_0', size=10, color=INK, bold=True))
    p.append(text(120, 209, 'H(0x00 || L_0)', size=9, color=MUTED))

    p.append(rect(180, 180, 110, 36, fill='#ffffff', stroke=LINE, sw=1.4, rx=5))
    p.append(text(235, 196, 'Геш H_1', size=10, color=INK, bold=True))
    p.append(text(235, 209, 'H(0x00 || L_1)', size=9, color=MUTED))

    p.append(rect(430, 180, 110, 36, fill='#e8f8f0', stroke=FIELD, sw=2.0, rx=5))
    p.append(text(485, 196, 'Геш H_2 (Ціль)', size=10, color=FIELD, bold=True))
    p.append(text(485, 209, 'H(0x00 || L_2)', size=9, color=FIELD))

    p.append(rect(605, 180, 110, 36, fill='#e8f4fd', stroke=NEG, sw=1.8, rx=5))
    p.append(text(660, 196, 'Геш H_3 (Шлях)', size=9, color=NEG, bold=True))
    p.append(text(660, 209, 'H(0x00 || L_3)', size=9, color=NEG))

    p.append(arrow(485, 245, 485, 220, color=FIELD, sw=1.6))
    p.append(rect(415, 245, 140, 32, fill='#ffffff', stroke=FIELD, sw=1.5, rx=5))
    p.append(text(485, 265, 'Сирий Запис №2 (L_2)', size=9, color=FIELD, bold=True))

    p.append(rect(40, 235, 330, 60, fill='#f8fafc', stroke=INK, sw=1.3, rx=6))
    p.append(text(205, 253, 'Доказ включення (Audit Proof) для Запису №2:', size=10, color=INK, bold=True))
    p.append(text(205, 270, 'Потрібно лише: { H_3, H_01 } та Корінь Root', size=9, color=NEG, bold=True))
    p.append(text(205, 284, 'Складність перевірки: O(log N)', size=9, color=FIELD))

    render(os.path.join(OUT, 'merkle-transparency-log.svg'), W, H, *p,
           title='Дерево Меркла для журналу аудиту та доказ включення')


if __name__ == '__main__':
    fig_audit_threat_model()
    fig_forward_secure_ratchet()
    fig_merkle_transparency_log()
    print('Figures generated successfully.')
