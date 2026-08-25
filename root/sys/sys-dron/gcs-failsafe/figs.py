# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_watchdog_timeline():
    """Часова шкала Heartbeat Watchdog: від пропуску пакетів до Failsafe."""
    W, H = 780, 360
    p = []
    p.append(text(W/2, 28, "Хронологія детектора пульсу (Heartbeat Watchdog) при розриві каналу", size=16, bold=True))

    axis_y = 130
    p.append(line(40, axis_y, 740, axis_y, color=INK, sw=2))
    p.append(text(740, axis_y + 24, "час t (секунди) →", size=11, color=MUTED, anchor="end"))

    # Нормальні імпульси Heartbeat (1 Гц)
    hb_times = [0, 1, 2, 3]
    for i, t_val in enumerate(hb_times):
        x = 70 + t_val * 65
        p.append(line(x, axis_y - 18, x, axis_y + 18, color=FIELD, sw=3))
        p.append(circle(x, axis_y - 18, 4, fill=FIELD, stroke=FIELD))
        p.append(text(x, axis_y - 26, "HB", size=10.5, color=FIELD, bold=True))
        p.append(text(x, axis_y + 32, "%d с" % t_val, size=11, color=INK))

    # Точка втрати зв'язку
    loss_x = 70 + 3 * 65 + 30
    p.append(line(loss_x, axis_y - 35, loss_x, axis_y + 35, color=POS, sw=2, dash="4 3"))
    p.append(text(loss_x, axis_y - 42, "Обрив сигналу", size=11, color=POS, bold=True))

    # Зони стану каналу
    # Зона 1: Активний канал (0 .. 3 с)
    p.append(rect(60, 190, 220, 130, fill="#f0faf4", stroke=FIELD, sw=1.5))
    p.append(text(170, 214, "СТАН: CONNECTED", size=12.5, color=FIELD, bold=True))
    p.append(fitbox(70, 228, 200, 80, "• Δt < 1.5 с\n• Телеметрія активна\n• Джойстик і команди\n  дозволені", size=11, fill="#ffffff"))

    # Зона 2: Попередження / Деградація (3.5 .. 6.5 с)
    p.append(rect(295, 190, 210, 130, fill="#fffbf0", stroke="#d97706", sw=1.5))
    p.append(text(400, 214, "СТАН: DEGRADED", size=12.5, color="#d97706", bold=True))
    p.append(fitbox(305, 228, 190, 80, "• 1.5 с ≤ Δt < 3.5 с\n• Жовтий статус у GCS\n• Очікування пакета,\n  накопичення втрат", size=11, fill="#ffffff"))

    # Зона 3: Аварійний розрив / Failsafe (t >= 7 с / таймаут 3.5-5с після останнього HB)
    p.append(rect(520, 190, 220, 130, fill="#fdf2f2", stroke=POS, sw=1.5))
    p.append(text(630, 214, "СТАН: LINK LOST", size=12.5, color=POS, bold=True))
    p.append(fitbox(530, 228, 200, 80, "• Δt ≥ 3.5–5.0 с\n• Звукова тривога в GCS\n• Блокування джойстика\n• Автопілот: DataLink FS", size=11, fill="#ffffff"))

    # Відмітки на осі часу після обриву
    lost_hb = [4, 5, 6, 7, 8]
    for t_val in lost_hb:
        x = 70 + t_val * 65
        p.append(line(x, axis_y - 12, x, axis_y + 12, color="#d1d5db", sw=2, dash="3 3"))
        p.append(text(x, axis_y - 18, "✖", size=10, color=POS))
        p.append(text(x, axis_y + 32, "%d с" % t_val, size=11, color=MUTED))

    # Стрілка таймауту 3.5-5 с
    fs_trigger_x = 70 + 7 * 65
    p.append(line(fs_trigger_x, axis_y - 25, fs_trigger_x, axis_y + 25, color=POS, sw=2.5))
    p.append(text(fs_trigger_x, axis_y - 32, "Спрацювання Failsafe", size=11, color=POS, bold=True))

    render(os.path.join(IMG, 'watchdog-timeline.svg'), W, H, *p)


def fig_failsafe_decision_tree():
    """Дерево рішень автопілота при втраті каналу передачі даних (DataLink Loss)."""
    W, H = 820, 430
    p = []
    p.append(text(W/2, 26, "Логіка дій польотного контролера при DataLink Loss (GCS Failsafe)", size=16, bold=True))

    # Корінь: Подія DataLink Loss
    p.append(rect(300, 50, 220, 50, fill="#fdf2f2", stroke=POS, sw=2))
    p.append(text(410, 72, "Втрата зв'язку з GCS", size=13, color=POS, bold=True))
    p.append(text(410, 90, "Таймаут HB > COM_DL_LOSS_T", size=10.5, color=MUTED))

    # Перевірка 1: Чи активний режим автономної місії (Mission / Auto)?
    p.append(rect(100, 140, 250, 60, fill="#f4f6f8", stroke=LINE, sw=1.5))
    p.append(text(225, 164, "Режим: Auto / Mission?", size=12.5, bold=True))
    p.append(text(225, 184, "Автопілот виконує польотний план", size=10.5, color=MUTED))

    # Перевірка 2: Ручне керування з GCS (Joystick / Guided / Offboard)
    p.append(rect(470, 140, 250, 60, fill="#f4f6f8", stroke=LINE, sw=1.5))
    p.append(text(595, 164, "Режим: Manual / Joystick / Guided?", size=12.5, bold=True))
    p.append(text(595, 184, "Керування спиралося на потік GCS", size=10.5, color=MUTED))

    # З'єднання від кореня
    p.append(arrow(360, 100, 250, 140))
    p.append(arrow(460, 100, 570, 140))

    # Гілка 1: Mission
    # Якщо дозволено Continue Mission
    p.append(rect(30, 250, 180, 80, fill="#f0faf4", stroke=FIELD, sw=1.5))
    p.append(text(120, 274, "Continue Mission", size=12, color=FIELD, bold=True))
    p.append(fitbox(38, 286, 164, 38, "Політ за планом до точки\nпосадки (NAV_DLL_ACT=0)", size=10.5, fill="#ffffff"))

    # Якщо вимагається RTL
    p.append(rect(230, 250, 180, 80, fill="#fffbf0", stroke="#d97706", sw=1.5))
    p.append(text(320, 274, "RTL (Повернення)", size=12, color="#d97706", bold=True))
    p.append(fitbox(238, 286, 164, 38, "Переривання місії,\nповернення до Home", size=10.5, fill="#ffffff"))

    p.append(arrow(180, 200, 120, 250))
    p.append(text(130, 222, "FS_GCS=2", size=10, color=MUTED))
    p.append(arrow(270, 200, 320, 250))
    p.append(text(310, 222, "FS_GCS=1", size=10, color=MUTED))

    # Гілка 2: Manual / Joystick
    # Є GPS -> Loiter / Hold
    p.append(rect(430, 250, 170, 80, fill="#eef2ff", stroke=NEG, sw=1.5))
    p.append(text(515, 274, "Loiter / Hold", size=12, color=NEG, bold=True))
    p.append(fitbox(438, 286, 154, 38, "Зависання/кружляння\nна час очікування", size=10.5, fill="#ffffff"))

    # Немає GPS або криза заряду -> Land
    p.append(rect(620, 250, 170, 80, fill="#fdf2f2", stroke=POS, sw=1.5))
    p.append(text(705, 274, "Emergency Land", size=12, color=POS, bold=True))
    p.append(fitbox(628, 286, 154, 38, "Вертикальна посадка\nна поточному місці", size=10.5, fill="#ffffff"))

    p.append(arrow(550, 200, 515, 250))
    p.append(text(510, 222, "Є GPS", size=10, color=MUTED))
    p.append(arrow(640, 200, 705, 250))
    p.append(text(685, 222, "Нема GPS", size=10, color=MUTED))

    # Ескалація з Loiter в RTL або Land
    p.append(arrow(515, 330, 515, 370))
    p.append(rect(400, 370, 230, 48, fill="#ffffff", stroke=LINE, sw=1.2))
    p.append(text(515, 390, "Таймаут зависання вичерпано (20-30 с)", size=10.5, color=MUTED))
    p.append(text(515, 406, "→ Ескалація в RTL або Land", size=11, color=POS, bold=True))

    render(os.path.join(IMG, 'failsafe-decision-tree.svg'), W, H, *p)


def fig_reconnect_resync():
    """Процес відновлення зв'язку (Reconnect) та очищення відкладених команд."""
    W, H = 780, 350
    p = []
    p.append(text(W/2, 26, "Відновлення зв'язку: ресинхронізація стану та очищення черг", size=16, bold=True))

    # Три кроки реконнекту
    # Крок 1: Відновлення пакета
    p.append(rect(30, 70, 220, 240, fill="#f4f6f8", stroke=LINE, sw=1.5))
    p.append(text(140, 96, "1. ДЕТЕКЦІЯ СИГНАЛУ", size=12.5, bold=True))
    p.append(fitbox(42, 110, 196, 50, "Надходження першого валідного\nHEARTBEAT після паузи", size=11, fill="#ffffff"))
    p.append(fitbox(42, 170, 196, 60, "• Скидання таймера тиші\n• Статус: CONNECTED\n• Оцінка затримки RTT", size=10.5, fill="#ffffff"))
    p.append(fitbox(42, 240, 196, 56, "Звукове сповіщення\nоператора про відновлення", size=10.5, fill="#f0faf4", stroke=FIELD))

    # Крок 2: Очищення застарілих команд (Discard Stale)
    p.append(rect(280, 70, 220, 240, fill="#fff7ed", stroke="#ea580c", sw=1.5))
    p.append(text(390, 96, "2. ОЧИЩЕННЯ ЧЕРГИ", size=12.5, color="#ea580c", bold=True))
    p.append(fitbox(292, 110, 196, 50, "Видалення всіх накопичених\nручних команд керування", size=11, fill="#ffffff"))
    p.append(fitbox(292, 170, 196, 60, "• Flush буфера джойстика\n• Блокування автодосилання\n• Запобігання ривкам дрона", size=10.5, fill="#ffffff"))
    p.append(fitbox(292, 240, 196, 56, "Застарілі команди\nзнищуються без виконання", size=10.5, fill="#fdf2f2", stroke=POS))

    # Крок 3: Ресинхронізація телеметрії та стану
    p.append(rect(530, 70, 220, 240, fill="#f0faf4", stroke=FIELD, sw=1.5))
    p.append(text(640, 96, "3. РЕСИНХРОНІЗАЦІЯ", size=12.5, color=FIELD, bold=True))
    p.append(fitbox(542, 110, 196, 50, "Оновлення режиму та стану\nбортових систем", size=11, fill="#ffffff"))
    p.append(fitbox(542, 170, 196, 60, "• Зчитування STATUSTEXT\n• Перевірка режиму (RTL/Auto)\n• Синхронізація WPs місії", size=10.5, fill="#ffffff"))
    p.append(fitbox(542, 240, 196, 56, "Оператор отримує повну\nкартину обстановки", size=10.5, fill="#ffffff", stroke=FIELD))

    # Стрілки між кроками
    p.append(arrow(250, 190, 280, 190))
    p.append(arrow(500, 190, 530, 190))

    render(os.path.join(IMG, 'reconnect-resync.svg'), W, H, *p)


if __name__ == '__main__':
    fig_watchdog_timeline()
    fig_failsafe_decision_tree()
    fig_reconnect_resync()
    print("All figures generated successfully.")
