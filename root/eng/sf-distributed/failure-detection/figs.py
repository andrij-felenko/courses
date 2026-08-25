# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def box(cx, cy, s, size=11, pad=8, **kw):
    frag, w, h = textbox(cx, cy, s, size=size, pad=pad, **kw)
    return frag


# ── Фігура 1: Неможливість розрізнення ────────────────────────────────────────
def fig_impossibility_ambiguity():
    W, H = 1000, 480
    frags = []

    frags.append(text(500, 26, 'Фундаментальна невизначеність: 4 фізичні причини однакового мовчання', size=15, bold=True))

    # Ліва колонка: Вузол-спостерігач
    frags.append(rect(25, 55, 230, 400, fill='#fcfdfe', stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(140, 82, 'Спостерігач (Node A)', size=12, bold=True, color=NEG))
    frags.append(box(140, 140, 'Надсилання зонда\n(Ping / Heartbeat)\nФіксація таймера t = 0', size=10, fill='#ffffff', stroke=MUTED, min_w=190))
    frags.append(arrow(140, 180, 140, 220, color=MUTED, sw=1.5))
    frags.append(box(140, 265, 'Таймаут T сплив!\nВідповіді немає.\nСимптом: ПОВНЕ\nМОВЧАННЯ СОКЕТА', size=10, bold=True, fill='#fff5f5', stroke=POS, min_w=190))
    frags.append(arrow(140, 315, 140, 355, color=POS, sw=1.5))
    frags.append(box(140, 400, 'Дилема рішення:\nОголосити DEAD чи\nпродовжувати чекати?', size=10, fill='#fff8e1', stroke='#e67e22', min_w=190))

    # Стрілка посередині до 4 сценаріїв
    frags.append(arrow(240, 265, 290, 265, color=POS, sw=2))

    # Права секція: 4 сценарії фізичної реальності
    frags.append(rect(285, 55, 690, 400, fill='#fcfdfe', stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(630, 82, 'Фізична реальність віддаленого вузла (Node B) та мережі', size=12, bold=True, color=INK))

    scenarios = [
        ('1. Аварійна зупинка (Crash-Stop)', 'Вимкнення живлення, крах ядра ОС (Kernel Panic), апаратний збій.\nВузол фізично мертвий і більше ніколи не відповість самостійно.', POS, '#fff5f5', 130),
        ('2. Втрата пакетів у мережі (Packet Loss)', 'Переповнення буфера черги комутатора, CRC-помилка, скидання SYN/ACK.\nВузол B живий і працює, але пакет запиту або відповіді знищено.', '#d97706', '#fffbeb', 215),
        ('3. Тимчасова пауза процесу (GC / CPU Stall)', 'Stop-The-World пауза збирача сміття на 4 секунди, swap-шторм на диску.\nВузол B живий, але потік виконання тимчасово заморожений OS.', '#2563eb', '#eff6ff', 300),
        ('4. Аномальна затримка мережі (Extreme Jitter)', 'Маршрутизатор перенаправив трафік довшим резервним каналом.\nЗатримка RTT зросла з 20 мс до 3500 мс; пакет живий і повільно рухається.', '#059669', '#ecfdf5', 385),
    ]

    for title_s, desc_s, border_col, bg_col, y_pos in scenarios:
        frags.append(rect(300, y_pos - 32, 660, 68, fill=bg_col, stroke=border_col, sw=1.2, rx=5))
        frags.append(text(315, y_pos - 12, title_s, size=11, bold=True, color=border_col, anchor='start'))
        frags.append(mtext(315, y_pos + 8, desc_s, size=9.5, color=INK, anchor='start', lh=1.25))

    return render(os.path.join(IMG, 'impossibility-ambiguity.svg'), W, H, *frags)


# ── Фігура 2: Матриця Чандри-Туега ───────────────────────────────────────────
def fig_chandra_toueg_matrix():
    W, H = 1020, 520
    frags = []

    frags.append(text(510, 26, 'Класифікація детектора відмов Чандри — Туега (Chandra & Toueg, 1996)', size=15, bold=True))

    # Ліва вісь: Повнота (Completeness)
    frags.append(rect(20, 60, 165, 430, fill='#f4f6f8', stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(102, 90, 'Властивість:', size=10, bold=True, color=MUTED))
    frags.append(text(102, 110, 'ПОВНОТА', size=11, bold=True, color=INK))
    
    frags.append(rect(30, 140, 145, 155, fill='#ffffff', stroke=MUTED, sw=1, rx=4))
    frags.append(text(102, 165, 'Сильна (Strong)', size=11, bold=True, color=POS))
    frags.append(mtext(102, 190, 'Кожен аварійний\nвузол ЗРЕШТОЮ\nпідозрюється ВСІМА\nздоровими вузлами', size=9.5, color=INK, lh=1.25))

    frags.append(rect(30, 315, 145, 155, fill='#ffffff', stroke=MUTED, sw=1, rx=4))
    frags.append(text(102, 340, 'Слабка (Weak)', size=11, bold=True, color='#d97706'))
    frags.append(mtext(102, 365, 'Кожен аварійний\nвузол ЗРЕШТОЮ\nпідозрюється ХОЧ\nОДНИМ здоровим', size=9.5, color=INK, lh=1.25))

    # Стовпчики точності (Accuracy)
    cols = [
        ('Сильна (Strong)', 'Жоден живий вузол\nНІКОЛИ не підозрюється', 'P', 'Q', POS, 195),
        ('Слабка (Weak)', 'ХОЧ ОДИН живий вузол\nНІКОЛИ не підозрюється', 'S', 'W', '#d97706', 395),
        ('Зрештою сильна (◇P)', 'Після моменту GST\nжоден живий не підозрюється', '◇P', '◇Q', '#2563eb', 595),
        ('Зрештою слабка (◇S)', 'Після моменту GST ХОЧ ОДИН\nживий не підозрюється', '◇S', '◇W', FIELD, 795),
    ]

    for col_title, col_desc, top_cls, bot_cls, col_col, x_pos in cols:
        # Заголовок стовпчика
        frags.append(rect(x_pos, 60, 190, 70, fill='#fcfdfe', stroke=MUTED, sw=1.2, rx=5))
        frags.append(text(x_pos + 95, 82, col_title, size=10.5, bold=True, color=col_col))
        frags.append(mtext(x_pos + 95, 100, col_desc, size=9, color=MUTED, lh=1.2))

        # Верхній осередок (Сильна повнота)
        bg_top = '#eafaf0' if '◇S' in top_cls else ('#fdecea' if top_cls == 'P' else '#ffffff')
        br_top = FIELD if '◇S' in top_cls else (POS if top_cls == 'P' else MUTED)
        sw_top = 2.0 if ('◇S' in top_cls or top_cls == 'P') else 1.0

        frags.append(rect(x_pos, 140, 190, 155, fill=bg_top, stroke=br_top, sw=sw_top, rx=6))
        frags.append(text(x_pos + 95, 175, 'Клас ' + top_cls, size=16, bold=True, color=br_top))
        
        if top_cls == 'P':
            frags.append(text(x_pos + 95, 205, 'Ідеальний (Perfect)', size=10, bold=True, color=POS))
            frags.append(mtext(x_pos + 95, 230, 'Неможливий в\nасинхронних мережах', size=9, color=MUTED, lh=1.2))
        elif top_cls == 'S':
            frags.append(text(x_pos + 95, 205, 'Сильний (Strong)', size=10, bold=True, color='#d97706'))
            frags.append(mtext(x_pos + 95, 230, 'Вимагає часткової\nсинхронності мережі', size=9, color=MUTED, lh=1.2))
        elif '◇P' in top_cls:
            frags.append(text(x_pos + 95, 205, 'Зрештою ідеальний', size=10, bold=True, color='#2563eb'))
            frags.append(mtext(x_pos + 95, 230, 'Припускає стабілізацію\nмережі після часу GST', size=9, color=MUTED, lh=1.2))
        elif '◇S' in top_cls:
            frags.append(text(x_pos + 95, 200, 'Зрештою сильний', size=11, bold=True, color=FIELD))
            frags.append(rect(x_pos + 8, 218, 174, 65, fill='#d1fae5', stroke=FIELD, sw=1, rx=4))
            frags.append(mtext(x_pos + 95, 238, 'НАЙСЛАБШИЙ ДЕТЕКТОР\nДЛЯ РОЗВ\'ЯЗАННЯ\nКОНСЕНСУСУ (Ω)', size=9, bold=True, color='#065f46', lh=1.25))

        # Нижній осередок (Слабка повнота)
        frags.append(rect(x_pos, 315, 190, 155, fill='#ffffff', stroke=MUTED, sw=1.0, rx=6))
        frags.append(text(x_pos + 95, 350, 'Клас ' + bot_cls, size=14, bold=True, color=MUTED))
        frags.append(text(x_pos + 95, 380, 'Редукується до ' + top_cls, size=10, bold=True, color=INK))
        frags.append(mtext(x_pos + 95, 408, 'Через фонову розсилку\nсписків підозр (Gossip)\nміж усіма вузлами', size=9, color=MUTED, lh=1.25))

    return render(os.path.join(IMG, 'chandra-toueg-matrix.svg'), W, H, *frags)


# ── Фігура 3: Heartbeat проти Ping-Ack та асиметричні обриви ──────────────────
def fig_heartbeat_vs_pingack():
    W, H = 1000, 480
    frags = []

    frags.append(text(500, 26, 'Топології виявлення: Push (Heartbeat), Pull (Ping-Ack) та асиметричний обрив', size=15, bold=True))

    # Секція 1: Push (Heartbeat)
    frags.append(rect(25, 55, 300, 400, fill='#fcfdfe', stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(175, 82, '1. Push-модель (Heartbeat)', size=12, bold=True, color=POS))
    
    # Вузли розсилають пульс
    frags.append(circle(100, 140, 20, fill='#ffffff', stroke=POS, sw=1.5))
    frags.append(text(100, 145, 'A', size=11, bold=True))
    frags.append(circle(250, 140, 20, fill='#ffffff', stroke=POS, sw=1.5))
    frags.append(text(250, 145, 'B', size=11, bold=True))
    frags.append(arrow(125, 140, 225, 140, color=POS, sw=1.5))
    frags.append(text(175, 130, 'Heartbeat', size=9.5, color=POS, bold=True))

    frags.append(box(175, 230, 'Вузол періодично випромінює\nсигнали пульсу (beacons).\nСпостерігач очікує прибуття:\nt_diff = t_now - t_last > T_timeout', size=9.5, fill='#ffffff', stroke=MUTED, min_w=270))

    frags.append(rect(35, 320, 280, 120, fill='#fff5f5', stroke=POS, sw=1, rx=4))
    frags.append(mtext(175, 345, [
        'Складність All-to-All: O(N²) повідомлень',
        'При N = 1000: 1 000 000 пакетів/с.',
        'Не перевіряє зворотний канал зв\'язку.',
        'Застосування: Cassandra, Akka (з Gossip).'
    ], size=9.5, color=INK, lh=1.3))

    # Секція 2: Pull (Ping-Ack)
    frags.append(rect(350, 55, 300, 400, fill='#fcfdfe', stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(500, 82, '2. Pull-модель (Ping-Ack)', size=12, bold=True, color=NEG))

    frags.append(circle(425, 130, 20, fill='#ffffff', stroke=NEG, sw=1.5))
    frags.append(text(425, 135, 'A', size=11, bold=True))
    frags.append(circle(575, 130, 20, fill='#ffffff', stroke=NEG, sw=1.5))
    frags.append(text(575, 135, 'B', size=11, bold=True))

    frags.append(arrow(450, 122, 550, 122, color=NEG, sw=1.5))
    frags.append(text(500, 114, 'Ping (Запит)', size=9, color=NEG, bold=True))
    frags.append(arrow(550, 138, 450, 138, color=FIELD, sw=1.5))
    frags.append(text(500, 152, 'Ack (Відповідь)', size=9, color=FIELD, bold=True))

    frags.append(box(500, 230, 'Спостерігач A активно пінгує B\nта очікує підтвердження Ack.\nПеревіряє двосторонню зв\'язність\n(Forward + Reverse RTT).', size=9.5, fill='#ffffff', stroke=MUTED, min_w=270))

    frags.append(rect(360, 320, 280, 120, fill='#eff6ff', stroke=NEG, sw=1, rx=4))
    frags.append(mtext(500, 345, [
        'Складність опитування: O(N) або O(1)',
        'Двосторонній контроль сокета.',
        'Ризик: навантаження на ціль (Fan-in),',
        'якщо 100 вузлів одночасно пінгують B.',
        'Застосування: HTTP health-checks, SWIM.'
    ], size=9.5, color=INK, lh=1.3))

    # Секція 3: Пастка асиметричного обриву
    frags.append(rect(675, 55, 300, 400, fill='#fcfdfe', stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(825, 82, '3. Асиметричний обрив зв\'язку', size=12, bold=True, color='#d97706'))

    frags.append(circle(750, 130, 20, fill='#ffffff', stroke='#d97706', sw=1.5))
    frags.append(text(750, 135, 'A', size=11, bold=True))
    frags.append(circle(900, 130, 20, fill='#ffffff', stroke='#d97706', sw=1.5))
    frags.append(text(900, 135, 'B', size=11, bold=True))

    # Прямий лінк працює, зворотний зламано
    frags.append(arrow(775, 122, 875, 122, color=FIELD, sw=1.5))
    frags.append(text(825, 114, 'A -> B: ПРАЦЮЄ', size=9, color=FIELD, bold=True))
    
    frags.append(line(875, 138, 775, 138, color=POS, sw=1.5, dash='4,4'))
    frags.append(text(825, 154, 'B -> A: ОБІРВАНО ✕', size=9, color=POS, bold=True))

    frags.append(box(825, 230, 'Односторонній збій комутатора / firewall:\nB отримує пакети від A, але його\nвідповіді Ack не доходять до A.\nВузол A помилково вважає B мертвим!', size=9.5, fill='#ffffff', stroke='#d97706', min_w=270))

    frags.append(rect(685, 320, 280, 120, fill='#fffbeb', stroke='#d97706', sw=1, rx=4))
    frags.append(mtext(825, 345, [
        'Небезпека: розкол кластера (Split-Brain).',
        'A вважає B мертвим -> перевибори лідера.',
        'B вважає A мертвим -> власний лідер.',
        'Потрібне непряме зондування (Indirect Ping)',
        'через посередників (як у SWIM).'
    ], size=9.5, color=INK, lh=1.3))

    return render(os.path.join(IMG, 'heartbeat-vs-pingack-topology.svg'), W, H, *frags)


# ── Фігура 4: SWIM протокол та механізм підозри ──────────────────────────────
def fig_swim_protocol_cycle():
    W, H = 1040, 500
    frags = []

    frags.append(text(520, 26, 'Протокол SWIM: прямий пінг, непряме зондування (Ping-Req) та спростування', size=15, bold=True))

    # Фаза 1: Прямий пінг
    frags.append(rect(20, 55, 305, 420, fill='#fcfdfe', stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(172, 82, 'Фаза 1: Прямий Ping', size=12, bold=True, color=NEG))
    
    frags.append(circle(80, 150, 18, fill='#ffffff', stroke=NEG, sw=1.5))
    frags.append(text(80, 155, 'Mi', size=10, bold=True))
    frags.append(circle(260, 150, 18, fill='#ffffff', stroke=NEG, sw=1.5))
    frags.append(text(260, 155, 'Mj', size=10, bold=True))

    frags.append(arrow(105, 140, 235, 140, color=NEG, sw=1.5))
    frags.append(text(170, 130, '1. Ping', size=9.5, color=NEG, bold=True))
    frags.append(line(235, 160, 105, 160, color=POS, sw=1.5, dash='3,3'))
    frags.append(text(170, 175, 'Таймаут T_ping сплив!', size=9, color=POS, bold=True))

    frags.append(box(172, 260, 'Вузол Mi випадковим чином\nобирає Mj зі списку членів.\nНадсилає прямий UDP-пакет Ping.\nВідповідь Ack не надійшла за T_ping.', size=9.5, fill='#ffffff', stroke=MUTED, min_w=280))

    frags.append(rect(30, 345, 285, 115, fill='#eff6ff', stroke=NEG, sw=1, rx=4))
    frags.append(mtext(172, 370, [
        'Mi НЕ оголошує Mj мертвим негайно!',
        'Причиною мовчання може бути локальний',
        'дроп пакетів або короткочасний джиттер',
        'на конкретному маршруті Mi <-> Mj.'
    ], size=9, color=INK, lh=1.3))

    # Фаза 2: Непряме зондування (Ping-Req)
    frags.append(rect(345, 55, 335, 420, fill='#fcfdfe', stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(512, 82, 'Фаза 2: Непрямий Ping-Req', size=12, bold=True, color='#d97706'))

    frags.append(circle(390, 140, 18, fill='#ffffff', stroke=NEG, sw=1.5))
    frags.append(text(390, 145, 'Mi', size=10, bold=True))
    
    frags.append(circle(512, 110, 16, fill='#ffffff', stroke='#d97706', sw=1.5))
    frags.append(text(512, 115, 'H1', size=9, bold=True))
    frags.append(circle(512, 170, 16, fill='#ffffff', stroke='#d97706', sw=1.5))
    frags.append(text(512, 175, 'H2', size=9, bold=True))

    frags.append(circle(635, 140, 18, fill='#ffffff', stroke=POS, sw=1.5))
    frags.append(text(635, 145, 'Mj', size=10, bold=True))

    frags.append(arrow(410, 130, 492, 115, color='#d97706', sw=1.3))
    frags.append(arrow(410, 150, 492, 165, color='#d97706', sw=1.3))
    frags.append(text(450, 98, 'Ping-Req(Mj)', size=9, color='#d97706'))

    frags.append(arrow(532, 115, 615, 130, color=MUTED, sw=1.3))
    frags.append(arrow(532, 165, 615, 150, color=MUTED, sw=1.3))
    frags.append(text(575, 98, 'Ping', size=9, color=MUTED))

    frags.append(box(512, 260, 'Mi обирає k випадкових помічників\n(H1..Hk, зазвичай k = 3..5) та просить\nїх перевірити зв\'язність із Mj.\nПомічники пінгують Mj паралельно.', size=9.5, fill='#ffffff', stroke=MUTED, min_w=305))

    frags.append(rect(355, 345, 315, 115, fill='#fffbeb', stroke='#d97706', sw=1, rx=4))
    frags.append(mtext(512, 370, [
        'Якщо хоч один посередник отримає Ack,',
        'він пересилає його до Mi -> Mj живий!',
        'Це повністю нейтралізує локальні збої',
        'маршрутизації між парою (Mi, Mj).'
    ], size=9, color=INK, lh=1.3))

    # Фаза 3: Механізм підозри та спростування
    frags.append(rect(700, 55, 320, 420, fill='#fcfdfe', stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(860, 82, 'Фаза 3: Підозра та спростування', size=12, bold=True, color=FIELD))

    frags.append(box(860, 135, 'Жоден помічник не відповів:\nСтатус Mj стає Suspect(Incarnation I)\nРозповсюдження пліткою (Gossip)', size=9.5, fill='#fff5f5', stroke=POS, min_w=290))

    frags.append(arrow(810, 175, 775, 215, color=FIELD, sw=1.5))
    frags.append(text(760, 195, 'Mj живий', size=9, color=FIELD, bold=True))
    frags.append(box(775, 260, 'Спростування:\nMj чує підозру\nта оголошує:\nAlive(Incarnation I+1)', size=9, fill='#eafaf0', stroke=FIELD, min_w=135))

    frags.append(arrow(910, 175, 945, 215, color=POS, sw=1.5))
    frags.append(text(960, 195, 'Таймер сплив', size=9, color=POS, bold=True))
    frags.append(box(945, 260, 'Підтвердження:\nТаймер сплив\nбез спростувань ->\nСтатус DEAD (Evict)', size=9, fill='#fdecea', stroke=POS, min_w=135))

    frags.append(rect(710, 345, 300, 115, fill='#f4f6f8', stroke=MUTED, sw=1, rx=4))
    frags.append(mtext(860, 370, [
        'Інкарнаційні числа захищають від',
        'застарілих повідомлень.',
        'Мерехтливі вузли самі спростовують',
        'хибні підозри, не ламаючи кластер.'
    ], size=9, color=INK, lh=1.3))

    return render(os.path.join(IMG, 'swim-protocol-cycle.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_impossibility_ambiguity()
    fig_chandra_toueg_matrix()
    fig_heartbeat_vs_pingack()
    fig_swim_protocol_cycle()
    print('All failure-detection figures generated successfully.')
