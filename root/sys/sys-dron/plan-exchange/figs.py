# -*- coding: utf-8 -*-
"""Фігури до теми «Обмін планом із апаратом: вивантаження й звірка»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def row_list(x, y, w, rows, rh=34, size=12, fill=FILL, stroke=LINE):
    """Стовпчик однакових рядків-рамок. Повертає (фрагмент, нижня межа)."""
    out = ''
    for i, s in enumerate(rows):
        out += fitbox(x, y + i * rh, w, rh - 6, s, size=size, pad=8,
                      fill=fill, stroke=stroke)
    return out, y + len(rows) * rh - 6


# ── 1. Три форми того самого плану ─────────────────────────────────────────
def fig_plan_forms():
    W, H = 1340, 780
    f = [text(W / 2, 36, 'Документ у застосунку і три плоскі списки на борту',
              size=19, bold=True)]

    # ліва панель — документ
    f.append(rect(40, 70, 410, 470, fill='#ffffff'))
    f.append(text(245, 100, 'Документ плану (.plan)', size=15, bold=True))
    doc = [
        ('Місія', True),
        ('налаштування: дім, швидкості, режим висоти', False),
        ('зліт на 30 м', False),
        ('полігон зйомки: крок 25 м, кут 90°,', False),
        ('перекриття 70 %', False),
        ('посадковий патерн', False),
        ('Геозона', True),
        ('полігон-включення (4 вершини)', False),
        ('коло-виключення (r = 60 м)', False),
        ('Точки збору', True),
        ('дві точки', False),
    ]
    yy = 126
    for s, head in doc:
        if head:
            yy += 10
            f.append(text(62, yy + 14, s, size=14, bold=True, anchor='start'))
            yy += 26
        else:
            f.append(text(80, yy + 14, '· ' + s, size=13, color=MUTED, anchor='start'))
            yy += 24

    # стрілка проєкції
    f.append(text(560, 268, 'проєкція', size=15, bold=True))
    f.append(text(560, 290, 'при вивантаженні', size=13, color=MUTED))
    f.append(arrow(474, 320, 646, 320, sw=2.4))

    # праві стовпчики — плоскі списки
    cols = [
        (670, 'Місія · type 0', [
            '0 · дім (ArduPilot)', '1 · TAKEOFF', '2 · WAYPOINT', '3 · WAYPOINT',
            '4 · WAYPOINT', '5 · WAYPOINT', '…', '10 · WAYPOINT', '11 · LAND']),
        (890, 'Геозона · type 1', [
            '0 · VERTEX_INCL', '1 · VERTEX_INCL', '2 · VERTEX_INCL',
            '3 · VERTEX_INCL', '4 · CIRCLE_EXCL']),
        (1110, 'Точки збору · type 2', [
            '0 · RALLY_POINT', '1 · RALLY_POINT']),
    ]
    for x, title_, rows in cols:
        f.append(fitbox(x, 82, 200, 32, title_, size=13, bold=True, fill='#eef2f7'))
        frag, _ = row_list(x, 124, 200, rows)
        f.append(frag)

    f.append(fitbox(670, 560, 640, 76,
                    'Борт зберігає лише пронумеровані записи однакової довжини.\n'
                    'Крок, кут і перекриття зникли: замість полігона зйомки —\n'
                    'просто вісім точок підряд, нічим між собою не зв\'язаних.',
                    size=13, fill='#fdecea', stroke=POS))

    f.append(fitbox(40, 578, 410, 76,
                    'Структура живе тільки тут: типи елементів,\n'
                    'параметри патернів, режими висоти, посилання\n'
                    'на рельєф, планована домашня точка.',
                    size=13, fill='#eaf6ee', stroke=FIELD))
    render(os.path.join(OUT, 'plan-forms.svg'), W, H, *f)


# ── 2. Крок за кроком: вивантаження місії ──────────────────────────────────
def fig_upload_lockstep():
    W, H = 1120, 900
    XL, XR = 240, 860
    f = [text(W / 2, 36, 'Вивантаження: наступний пункт їде лише у відповідь на запит',
              size=19, bold=True)]

    b, _, _ = textbox(XL, 82, 'Станція', size=15, bold=True, min_w=200)
    f.append(b)
    b, _, _ = textbox(XR, 82, 'Борт', size=15, bold=True, min_w=200)
    f.append(b)
    f.append(line(XL, 108, XL, 790, color=MUTED, dash='6 6'))
    f.append(line(XR, 108, XR, 790, color=MUTED, dash='6 6'))

    msgs = [
        ('r', 'MISSION_COUNT (n = 12, type = MISSION)'),
        ('l', 'MISSION_REQUEST_INT (seq = 0)'),
        ('r', 'MISSION_ITEM_INT (seq = 0)'),
        ('l', 'MISSION_REQUEST_INT (seq = 1)'),
        ('r', 'MISSION_ITEM_INT (seq = 1)'),
        ('.', 'ще десять пар «запит — пункт»'),
        ('l', 'MISSION_REQUEST_INT (seq = 11)'),
        ('r', 'MISSION_ITEM_INT (seq = 11)'),
        ('l', 'MISSION_ACK (MAV_MISSION_ACCEPTED)'),
    ]
    y = 158
    for d, s in msgs:
        f.append(text((XL + XR) / 2, y - 12, s, size=13))
        if d == 'r':
            f.append(arrow(XL + 6, y + 10, XR - 6, y + 10))
        elif d == 'l':
            f.append(arrow(XR - 6, y + 10, XL + 6, y + 10, color=NEG))
        else:
            f.append(line(XL + 6, y + 10, XR - 6, y + 10, color=MUTED, dash='4 8'))
        y += 68

    f.append(fitbox(60, 806, 1000, 76,
                    'Кожен запит — водночас підтвердження попереднього пункту й замовлення наступного.\n'
                    'Немає відповіді 1500 мс — станція повторює; на невідданий пункт чекає 250 мс;\n'
                    'після п\'ятої невдалої спроби транзакцію скасовано, місія на борту лишається старою.',
                    size=13, fill='#eef2f7'))
    render(os.path.join(OUT, 'upload-lockstep.svg'), W, H, *f)


# ── 3. Оборотна й необоротна проєкція ──────────────────────────────────────
def fig_projection():
    W, H = 1260, 740
    f = [text(W / 2, 36, 'Чому геозона повертається з борту цілою, а зйомка — ні',
              size=19, bold=True)]

    # ── ряд 1: геозона
    f.append(text(70, 84, 'Геозона: проєкція оборотна', size=15, bold=True, anchor='start'))
    f.append(fitbox(70, 104, 300, 90,
                    'полігон-включення\nз чотирьох вершин', size=14, fill='#eaf6ee', stroke=FIELD))
    f.append(arrow(384, 149, 458, 149, sw=2.2))
    frag, _ = row_list(472, 100, 300, [
        'VERTEX_INCL · param1 = 4',
        'VERTEX_INCL · param1 = 4',
        'VERTEX_INCL · param1 = 4',
        'VERTEX_INCL · param1 = 4'], rh=32, size=12)
    f.append(frag)
    f.append(arrow(786, 149, 860, 149, sw=2.2))
    f.append(fitbox(874, 104, 316, 90,
                    'полігон зібрано назад:\nчотири вершини, включення',
                    size=14, fill='#eaf6ee', stroke=FIELD))
    f.append(fitbox(70, 244, 1120, 46,
                    'Кожна вершина везе в param1 кількість вершин свого полігону — і цього поля досить, щоб розрізати плоский список назад на полігони.',
                    size=13, fill='#f7faf8', stroke=FIELD))

    # ── ряд 2: зйомка
    f.append(text(70, 366, 'Зйомка: проєкція необоротна', size=15, bold=True, anchor='start'))
    f.append(fitbox(70, 386, 300, 108,
                    'полігон зйомки\nкрок 25 м · кут 90°\nперекриття 70 %',
                    size=14, fill='#fdecea', stroke=POS))
    f.append(arrow(384, 440, 458, 440, sw=2.2))
    f.append(fitbox(472, 386, 300, 44, 'WAYPOINT × 8', size=14, fill=FILL))
    for i in range(8):
        cx = 500 + (i % 4) * 68
        cy = 452 + (i // 4) * 34
        f.append(circle(cx, cy, 8, fill='#eef2f7', stroke=MUTED, sw=1.4))
    f.append(arrow(786, 440, 860, 440, sw=2.2))
    f.append(fitbox(874, 386, 316, 108,
                    'вісім окремих точок:\nані кроку, ані кута,\nані меж полігона',
                    size=14, fill='#fdecea', stroke=POS))
    f.append(fitbox(70, 544, 1120, 74,
                    'У пункті місії сім числових параметрів, і всі сім зайняті координатами й аргументами команди.\n'
                    'Покласти туди крок, кут чи межі полігона нема куди — тож відновити зйомку з точок нема з чого.',
                    size=13, fill='#fdf6f5', stroke=POS))
    render(os.path.join(OUT, 'projection.svg'), W, H, *f)


# ── 4. Розширені поля й обрізаний хвіст тіла ───────────────────────────────
def fig_count_truncation():
    W, H = 1360, 610
    XL, WL = 36, 240          # ліва підпис-колонка
    XS = 292                  # початок смуги полів
    XV, WV = 1110, 214        # колонка висновку
    f = [text(W / 2, 36, 'Одне й те саме MISSION_COUNT у трьох виглядах на дроті',
              size=19, bold=True)]

    widths = [120, 160, 180, 160, 150]
    names = ['count', 'target_system', 'target_component', 'mission_type', 'opaque_id']

    GONE = ('#eef2f7', MUTED, MUTED)      # обрізано нулями
    KEPT = ('#eaf6ee', FIELD, INK)        # поле реально в кадрі
    NONE_ = ('#fdecea', POS, POS)         # у v1 такого поля немає
    BASE = (FILL, LINE, INK)

    rows = [
        ('MAVLink 2\nтип = 0 (місія)',
         ['2 Б', '1 Б', '1 Б', 'обрізано (0)', 'обрізано (0)'],
         [BASE, BASE, BASE, GONE, GONE],
         '4 байти в тілі\nтип прочитано як 0 —\nсаме те, що слали', KEPT),
        ('MAVLink 2\nтип = 1 (геозона)',
         ['2 Б', '1 Б', '1 Б', '= 1', 'обрізано (0)'],
         [BASE, BASE, BASE, KEPT, GONE],
         '5 байтів у тілі\nтип прочитано як 1 —\nсаме те, що слали', KEPT),
        ('MAVLink 1\nтип = 1 (геозона)',
         ['2 Б', '1 Б', '1 Б', 'немає в v1', 'немає в v1'],
         [BASE, BASE, BASE, NONE_, NONE_],
         '4 байти в тілі\nтип прочитано як 0 —\nгеозона пішла як місія', NONE_),
    ]

    y = 104
    for label, second, styles, verdict, vstyle in rows:
        f.append(fitbox(XL, y, WL, 74, label, size=13, bold=True, fill='#ffffff'))
        x = XS
        for w, nm, s2, (fill_, stroke_, color_) in zip(widths, names, second, styles):
            f.append(fitbox(x, y, w, 74, nm + '\n' + s2, size=13,
                            fill=fill_, stroke=stroke_, color=color_))
            x += w + 8
        f.append(fitbox(XV, y, WV, 74, verdict, size=13,
                        fill=vstyle[0], stroke=vstyle[1]))
        y += 130

    f.append(fitbox(XL, 470, 1288, 104,
                    'Розширені поля mission_type й opaque_id додали до повідомлень уже після появи MAVLink 2.\n'
                    'Кадр MAVLink 1 їх не везе взагалі, а MAVLink 2 обрізає нульовий хвіст тіла перед відправленням.\n'
                    'Приймач добиває коротке тіло нулями — тож «поля немає» і «поле дорівнює нулю» на дроті нерозрізненні,\n'
                    'а нуль у mission_type означає «місія».',
                    size=13, fill='#eef2f7'))
    render(os.path.join(OUT, 'mission-count-wire.svg'), W, H, *f)


# ── 5. Машина станів вивантажувача ─────────────────────────────────────────
def fig_upload_fsm():
    W, H = 1420, 940
    CX = 300
    f = [text(W / 2, 40, 'Машина станів вивантажувача: чого чекаємо і скільки',
              size=19, bold=True)]

    states = [
        (100, 'СПОКІЙ\nтаймерів немає', '#eef2f7'),
        (250, 'ЧЕКАЮ ПЕРШОГО ЗАПИТУ\nтаймер 1500 мс · до 5 спроб', '#eaf0fd'),
        (400, 'ЧЕКАЮ ЧЕРГОВОГО ЗАПИТУ\nтаймер 250 мс · до 5 спроб', '#eaf0fd'),
        (550, 'ЧЕКАЮ ПІДТВЕРДЖЕННЯ\nтаймер 1500 мс · без повторів', '#eaf0fd'),
        (700, 'СПОКІЙ\nуспіх або названа помилка', '#eef2f7'),
    ]
    for cy, s, fill_ in states:
        b, _, _ = textbox(CX, cy, s, size=14, min_w=340, fill=fill_)
        f.append(b)

    labels = [
        (175, ['надіслали MISSION_COUNT (n = 12, тип плану — місія);',
               'у черзі всі номери 0…11, віддано жодного']),
        (325, ['прийшов MISSION_REQUEST або MISSION_REQUEST_INT:',
               'шлемо MISSION_ITEM_INT і викреслюємо номер із черги']),
        (475, ['черга спорожніла — кожен номер віддано принаймні раз']),
        (625, ['MISSION_ACK: ACCEPTED — місія на борту;',
               'інший код — помилка з описом останнього відданого пункта']),
    ]
    for cy, lines in labels:
        f.append(arrow(CX, cy - 49, CX, cy + 49, sw=2.2))
        ty = cy - (len(lines) - 1) * 13 * 1.3 / 2 + 4
        f.append(mtext(CX + 210, ty, lines, size=13, anchor='start'))

    rules = [
        ('Повторний запит — не помилка',
         'борт має право попросити номер, який уже віддано,\n'
         'і просити не підряд. Відповідаємо ще раз; черга\n'
         'лише каже, чи все віддано, а не куди йти далі.'),
        ('Таймаут — повтор останнього',
         'мовчання: шлемо ще раз те саме, що й посилали, —\n'
         'лічильник або той самий пункт, спроба +1.\n'
         'Нічого, чого не просили, у канал не йде.'),
        ('Скасування — теж повідомлення',
         'своє скасування й вичерпані спроби закриваємо\n'
         'через MISSION_ACK (OPERATION_CANCELLED): борт\n'
         'не чекатиме решти до власного таймауту.'),
    ]
    x = 60
    for title_, body in rules:
        f.append(fitbox(x, 790, 420, 36, title_, size=14, bold=True, fill='#f3efe6'))
        f.append(fitbox(x, 830, 420, 82, body, size=13, fill='#fbf9f5', stroke=MUTED))
        x += 450
    render(os.path.join(OUT, 'upload-fsm.svg'), W, H, *f)


# ── 6. Чому таймери різні ──────────────────────────────────────────────────
def fig_two_timers():
    W, H = 1340, 500
    cols = [(60, 250), (330, 390), (740, 350), (1110, 170)]
    f = [text(W / 2, 40,
              'Один протокол, два таймери: різниця не в смаку, а в тому, чим зайнятий борт',
              size=18, bold=True)]
    for (x, w), s in zip(cols, ['момент обміну', 'що робить борт',
                                'що означає тиша', 'таймер']):
        f.append(fitbox(x, 76, w, 38, s, size=14, bold=True, fill='#eef2f7'))

    rows = [
        ('після MISSION_COUNT',
         'перевіряє тип плану,\nрахує місце в пам\'яті,\nготується приймати',
         'борт може бути\nсправді зайнятий —\nчекати варто довго',
         '1500 мс'),
        ('між пунктами',
         'нічого важкого:\nкладе пункт у буфер\nі просить наступний',
         'зайнятості немає, тож\nтиша майже напевно —\nце втрачений кадр',
         '250 мс'),
        ('після останнього пункту',
         'перевіряє місію цілком\nі записує її у сховище',
         'запис у флеш триває\nдовше за політ кадру —\nчекати варто довго',
         '1500 мс'),
    ]
    y = 126
    for r in rows:
        for (x, w), s in zip(cols, r):
            fill_ = '#fdf6f5' if s.endswith('мс') else FILL
            f.append(fitbox(x, y, w, 96, s, size=13, fill=fill_))
        y += 106

    f.append(fitbox(60, 448, 1220, 40,
                    'Коротший таймер мусить бути більший за затримку туди-назад: на радіо з RTT 150 мс '
                    'поріг 250 мс іще безпечний, а 100 мс подвоїв би кожен пункт.',
                    size=13, fill='#eaf6ee', stroke=FIELD))
    render(os.path.join(OUT, 'two-timers.svg'), W, H, *f)


# ── Шари протоколу, датовані за номерами повідомлень ───────────────────────
def fig_protocol_strata():
    ROWH = 32
    XN, WN = 56, 68            # колонка номера
    XM, WM = 132, 360          # колонка назви повідомлення
    XA, WA = 566, 740          # колонка приміток
    W, H = XA + WA + 40, 1090

    ORIG = ('#eaf6ee', FIELD, INK)      # первісний блок
    LATE = ('#fdecea', POS, INK)        # дописане пізніше
    OTHER = ('#f2f3f5', MUTED, MUTED)   # чужі повідомлення
    GAP = None

    rows = [
        ('37', 'MISSION_REQUEST_PARTIAL_LIST', ORIG),
        ('38', 'MISSION_WRITE_PARTIAL_LIST', ORIG),
        ('39', 'MISSION_ITEM', ORIG),
        ('40', 'MISSION_REQUEST', ORIG),
        ('41', 'MISSION_SET_CURRENT', ORIG),
        ('42', 'MISSION_CURRENT', ORIG),
        ('43', 'MISSION_REQUEST_LIST', ORIG),
        ('44', 'MISSION_COUNT', ORIG),
        ('45', 'MISSION_CLEAR_ALL', ORIG),
        ('46', 'MISSION_ITEM_REACHED', ORIG),
        ('47', 'MISSION_ACK', ORIG),
        ('48', 'SET_GPS_GLOBAL_ORIGIN', OTHER),
        ('49', 'GPS_GLOBAL_ORIGIN', OTHER),
        ('50', 'PARAM_MAP_RC', OTHER),
        ('51', 'MISSION_REQUEST_INT', LATE),
        ('54', 'SAFETY_SET_ALLOWED_AREA', OTHER),
        ('55', 'SAFETY_ALLOWED_AREA', OTHER),
        ('', '56 … 69 — інші повідомлення', GAP),
        ('70', 'RC_CHANNELS_OVERRIDE', OTHER),
        ('73', 'MISSION_ITEM_INT', LATE),
        ('74', 'VFR_HUD', OTHER),
        ('75', 'COMMAND_INT', OTHER),
    ]

    f = [text(W / 2, 38, 'Номер повідомлення датує свій шар: суцільний блок і дві пізні латки',
              size=19, bold=True)]
    f.append(text(XM + WM / 2, 74, 'номери повідомлень MAVLink, за порядком',
                  size=13, color=MUTED))

    ytop = 92
    ypos = {}
    for i, (num, name, style) in enumerate(rows):
        y = ytop + i * ROWH
        if style is GAP:
            f.append(line(XN, y + ROWH / 2, XM + WM, y + ROWH / 2,
                          color=MUTED, dash='5 7'))
            f.append(text(XM + WM / 2, y + ROWH / 2 - 6, name, size=12, color=MUTED))
            continue
        fill_, stroke_, color_ = style
        f.append(fitbox(XN, y, WN, ROWH - 6, num, size=13, bold=True,
                        fill='#ffffff', stroke=stroke_, color=color_))
        f.append(fitbox(XM, y, WM, ROWH - 6, name, size=13,
                        fill=fill_, stroke=stroke_, color=color_))
        ypos[num] = y + (ROWH - 6) / 2

    # ── примітка до первісного блоку
    ytop37, ybot47 = ytop, ytop + 11 * ROWH - 6
    f.append(line(XM + WM + 14, ytop37, XM + WM + 14, ybot47, color=FIELD, sw=3))
    f.append(arrow(XM + WM + 14, (ytop37 + ybot47) / 2, XA - 12,
                   (ytop37 + ybot47) / 2, color=FIELD, sw=2))
    f.append(fitbox(XA, (ytop37 + ybot47) / 2 - 66, WA, 132,
                    'Перший шар: одинадцять номерів поспіль, без жодного пропуску.\n'
                    'Так виглядає підсистема, спроєктована за один захід.\n'
                    'Координати пунктів тут — сім чисел з рухомою комою,\n'
                    'широта й довгота просто в градусах.',
                    size=14, fill='#eaf6ee', stroke=FIELD))

    # ── примітка до 48/49
    y49 = ypos['49']
    f.append(arrow(XM + WM + 8, y49, XA - 12, y49, color=MUTED, sw=1.6))
    f.append(fitbox(XA, y49 - 34, WA, 68,
                    'Сусіди блоку вже тоді везли широту й довготу\n'
                    'як int32 у десятимільйонних частках градуса.',
                    size=13, fill='#f7f8fa', stroke=MUTED, color=MUTED))

    # ── примітка до 51 і 73
    y51, y73 = ypos['51'], ypos['73']
    f.append(arrow(XM + WM + 8, y51, XA - 12, y51, color=POS, sw=2))
    f.append(arrow(XM + WM + 8, y73, XA - 12, y73, color=POS, sw=2))
    f.append(fitbox(XA, (y51 + y73) / 2 - 74, WA, 148,
                    'Другий шар: цілочислові координати.\n'
                    'Номер повідомлення роздають раз і назавжди, тож замінити\n'
                    'старі повідомлення було нічим — лишалося дописати нові\n'
                    'у перші вільні номери, серед зовсім чужих сусідів.\n'
                    'Із 2020-06 старі оголошено застарілими.',
                    size=14, fill='#fdecea', stroke=POS))

    # ── нижня смуга: розширені поля
    yb = ytop + len(rows) * ROWH + 26
    f.append(text(W / 2, yb + 4,
                  'Третій і четвертий шари власних номерів не мають зовсім',
                  size=16, bold=True))
    boxes = [
        (XN, 420, 'Третій шар: mission_type\n\n'
                  'розширене поле в кожному повідомленні блоку:\n'
                  '0 — місія · 1 — геозона · 2 — точки збору\n'
                  '255 — усі типи, лише в MISSION_CLEAR_ALL'),
        (XN + 440, 420, 'Четвертий шар: ідентифікатори плану\n\n'
                        'MISSION_ACK.opaque_id · MISSION_COUNT.opaque_id\n'
                        'MISSION_CURRENT.mission_id / fence_id / rally_points_id'),
    ]
    for x, w, s in boxes:
        f.append(fitbox(x, yb + 22, w, 116, s, size=13, fill='#eef4fb', stroke=NEG))
    f.append(fitbox(XN + 900, yb + 22, W - XN - 900 - 40, 116,
                    'Розширені поля дописують у кінець уже випущеного\n'
                    'повідомлення. Це можливо лише в MAVLink 2 — і саме\n'
                    'тому обидва шари молодші за нього.',
                    size=13, fill='#f7f8fa', stroke=MUTED))
    render(os.path.join(OUT, 'protocol-strata.svg'), W, H, *f)


# ── Геозона до і після поля mission_type ───────────────────────────────────
def fig_fence_before_after():
    W, H = 1420, 700
    f = [text(W / 2, 38, 'Геозона й точки збору: два вендорські протоколи проти одного поля',
              size=19, bold=True)]

    # ── ліва половина: було
    f.append(text(320, 84, 'Було: діалект ArduPilot', size=16, bold=True))
    f.append(fitbox(60, 100, 250, 40, 'FENCE_POINT · 160', size=14, bold=True,
                    fill='#fdecea', stroke=POS))
    f.append(fitbox(330, 100, 250, 40, 'FENCE_FETCH_POINT · 161', size=14, bold=True,
                    fill='#fdecea', stroke=POS))
    f.append(fitbox(60, 148, 520, 76,
                    'lat, lng — float у градусах: та сама вада, що й у місіях,\n'
                    'тільки тут вона припала на межу дозволеної зони.\n'
                    'Перша точка має індекс 1: нульовий зайнято точкою повернення.',
                    size=13, fill='#fdf6f5', stroke=POS))

    f.append(fitbox(60, 256, 250, 40, 'RALLY_POINT · 175', size=14, bold=True,
                    fill='#eef4fb', stroke=NEG))
    f.append(fitbox(330, 256, 250, 40, 'RALLY_FETCH_POINT · 176', size=14, bold=True,
                    fill='#eef4fb', stroke=NEG))
    f.append(fitbox(60, 304, 520, 76,
                    'lat, lng — int32 у десятимільйонних частках градуса,\n'
                    'тобто зроблено правильно.\n'
                    'Перша точка має індекс 0.',
                    size=13, fill='#f7faff', stroke=NEG))

    f.append(fitbox(60, 410, 520, 92,
                    'Дві пари повідомлень одного діалекту, написані для однієї\n'
                    'задачі, розійшлися і в поданні координат, і в нумерації.\n'
                    'Кожна пара — крихітний власний протокол із власними\n'
                    'таймаутами, повторами й порядком обміну.',
                    size=13, fill='#f2f3f5', stroke=MUTED))

    # ── стрілка переходу
    f.append(text(675, 250, 'одне розширене', size=13, bold=True))
    f.append(text(675, 270, 'поле mission_type', size=13, bold=True))
    f.append(arrow(608, 300, 742, 300, sw=3))

    # ── права половина: стало
    f.append(text(1075, 84, 'Стало: той самий протокол місій', size=16, bold=True))
    f.append(fitbox(770, 100, 610, 40,
                    'Протокол місій: рахунок, запит пункту, підтвердження, повтори',
                    size=14, bold=True, fill='#eaf6ee', stroke=FIELD))
    types = [
        ('mission_type = 0', 'місія\nMAV_CMD_NAV_*'),
        ('mission_type = 1', 'геозона\nMAV_CMD_NAV_FENCE_*'),
        ('mission_type = 2', 'точки збору\nMAV_CMD_NAV_RALLY_POINT'),
    ]
    for i, (head, body) in enumerate(types):
        x = 770 + i * 206
        f.append(fitbox(x, 160, 196, 36, head, size=13, bold=True,
                        fill='#ffffff', stroke=FIELD))
        f.append(fitbox(x, 202, 196, 70, body, size=13,
                        fill='#eaf6ee', stroke=FIELD))
    f.append(fitbox(770, 288, 610, 62,
                    'Координати всюди int32 · 10⁷, нумерація всюди з нуля,\n'
                    'домовленість про обмін одна на всі три частини плану.',
                    size=13, fill='#f7faf8', stroke=FIELD))

    f.append(fitbox(770, 374, 610, 128,
                    'У застосунку це один клас:\n\n'
                    'PlanManager(vehicle, _planType)\n'
                    '    GeoFenceManager   → MAV_MISSION_TYPE_FENCE\n'
                    '    RallyPointManager → MAV_MISSION_TYPE_RALLY',
                    size=13, fill='#eef4fb', stroke=NEG))

    f.append(fitbox(60, 540, 1320, 106,
                    'Поле mission_type — розширене, тобто дописане в кінець уже випущених повідомлень, а розширені поля існують лише в MAVLink 2.\n'
                    'Приймач, який поля не знає, добиває тіло нулями — тож нуль мусив означати саме те, що діялося до появи поля, тобто місію.\n'
                    'Якби нулем позначили геозону, кожна стара станція зносила б апаратові межі дозволеної зони своїм маршрутом.',
                    size=13, fill='#f2f3f5', stroke=MUTED))
    render(os.path.join(OUT, 'fence-before-after.svg'), W, H, *f)


fig_plan_forms()
fig_upload_lockstep()
fig_projection()
fig_count_truncation()
fig_upload_fsm()
fig_two_timers()
fig_protocol_strata()
fig_fence_before_after()
print('ok')
