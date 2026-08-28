# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Стадії заморозки коду та еволюція релізу ─────────────────────────
def fig_freeze_stages():
    W, H = 1000, 480
    frags = []

    # Тло та заголовок шкали часу
    frags.append(rect(20, 20, 960, 440, fill="#fafbfc", stroke="#d1d5db", sw=1.5, rx=8))
    frags.append(text(500, 50, "Хронологія стабілізації релізу: фазове зниження ентропії коду", size=14, color=INK, bold=True))

    # Стрілка часу
    frags.append(arrow(60, 110, 940, 110, color="#4b5563", sw=2.5))
    frags.append(text(920, 95, "Час", size=12, color="#4b5563", bold=True))

    # Етапи (віхи) на шкалі
    # 1. Вільна розробка
    frags.append(circle(120, 110, 7, fill=NEG, stroke="#ffffff", sw=2))
    b1, w1, h1 = textbox(120, 190, "Активна розробка\n(Sprint / Trunk)\nВільне злиття фіч\nНові модулі та драйвери", size=11, bold=True,
                         fill="#eef4ff", stroke=NEG, sw=1.8, pad=8)
    frags.append(b1)

    # 2. Feature Freeze
    frags.append(circle(320, 110, 7, fill="#d97706", stroke="#ffffff", sw=2))
    frags.append(text(320, 95, "Feature Freeze (FF)", size=11, color="#d97706", bold=True))
    b2, w2, h2 = textbox(320, 295, "Feature Freeze\n(Заморозка фіч)\nЗаборона нових функцій\nСтворення release/vX.Y\nДозволено: bugfix, docs", size=11, bold=True,
                         fill="#fffbeb", stroke="#d97706", sw=1.8, pad=8)
    frags.append(b2)
    frags.append(line(320, 117, 320, 235, color="#d97706", sw=1.5, dash="3,3"))

    # 3. String / ABI Freeze
    frags.append(circle(530, 110, 7, fill="#7c3aed", stroke="#ffffff", sw=2))
    frags.append(text(530, 95, "ABI / String Freeze", size=11, color="#7c3aed", bold=True))
    b3, w3, h3 = textbox(530, 190, "ABI / String Freeze\n(Фіксація інтерфейсів)\nЗаморозка реєстрів NVM\nФіксація протоколів і UI\nПереклад та сертифікація", size=11, bold=True,
                         fill="#f5f3ff", stroke="#7c3aed", sw=1.8, pad=8)
    frags.append(b3)
    frags.append(line(530, 117, 530, 135, color="#7c3aed", sw=1.5, dash="3,3"))

    # 4. Code Freeze
    frags.append(circle(730, 110, 7, fill=POS, stroke="#ffffff", sw=2))
    frags.append(text(730, 95, "Code Freeze (CF)", size=11, color=POS, bold=True))
    b4, w4, h4 = textbox(730, 295, "Code Freeze\n(Повна заморозка)\nРежим нульової довіри\nПатчі лише через Bug Council\nФормування RC1, RC2...", size=11, bold=True,
                         fill="#fef2f2", stroke=POS, sw=1.8, pad=8)
    frags.append(b4)
    frags.append(line(730, 117, 730, 235, color=POS, sw=1.5, dash="3,3"))

    # 5. GA / Golden Master
    frags.append(circle(890, 110, 7, fill=FIELD, stroke="#ffffff", sw=2))
    frags.append(text(890, 95, "GA Release", size=11, color=FIELD, bold=True))
    b5, w5, h5 = textbox(890, 190, "General Availability\n(Golden Master)\nБінарна ідентичність RC\nКриптографічний підпис\nВипуск на виробництво", size=11, bold=True,
                         fill="#f0fdf4", stroke=FIELD, sw=1.8, pad=8)
    frags.append(b5)
    frags.append(line(890, 117, 890, 135, color=FIELD, sw=1.5, dash="3,3"))

    # Нижня стрічка: ціна виправлення дефекту
    frags.append(rect(60, 395, 880, 45, fill="#f3f4f6", stroke="#9ca3af", sw=1.2, rx=6))
    frags.append(text(500, 422, "Ціна помилки: 1x (Dev) ───> 10x (RC / HIL стенд) ───> 1000x (Прошивка на заводі / Відкликання пристроїв у клієнтів)", size=11, color="#1f2937", bold=True))

    render(os.path.join(IMG, 'freeze-stages-progression.svg'), W, H, *frags,
           title="Стадії заморозки коду та еволюція релізу")


# ── Фігура 2: Топологія гілкування та механіка Cherry-Pick ────────────────────
def fig_branching_model():
    W, H = 1000, 460
    frags = []

    frags.append(rect(20, 20, 960, 420, fill="#ffffff", stroke="#e5e7eb", sw=1.5, rx=8))
    frags.append(text(500, 48, "Топологія гілок: ізоляція релізу та вибірковий перенос виправлень (Cherry-Pick)", size=14, color=INK, bold=True))

    # Лінія Main/Trunk
    frags.append(line(60, 120, 920, 120, color=NEG, sw=3))
    frags.append(text(120, 100, "main / trunk (Розробка майбутнього релізу v2.0)", size=12, color=NEG, bold=True))

    # Лінія Release Branch
    frags.append(line(280, 260, 920, 260, color="#d97706", sw=3))
    frags.append(text(380, 240, "release/v1.2 (Стабілізація під час заморозки)", size=12, color="#d97706", bold=True))

    # Відгалуження release/v1.2 від main
    frags.append(circle(280, 120, 6, fill=NEG, stroke="#ffffff", sw=2))
    frags.append(arrow(280, 120, 280, 260, color="#d97706", sw=2))
    frags.append(text(300, 180, "Feature Freeze: гілка відсікається", size=10, color="#d97706", bold=True, anchor="start"))

    # Коміти в main
    frags.append(circle(440, 120, 6, fill=NEG, stroke="#ffffff", sw=2))
    frags.append(circle(600, 120, 6, fill=POS, stroke="#ffffff", sw=2))
    frags.append(text(600, 95, "Bugfix Commit (Fix #402)", size=10, color=POS, bold=True))
    frags.append(circle(760, 120, 6, fill=NEG, stroke="#ffffff", sw=2))

    # Кандидати в релізній гілці
    frags.append(circle(460, 260, 6, fill="#d97706", stroke="#ffffff", sw=2))
    frags.append(text(460, 290, "v1.2.0-rc.1", size=11, color="#d97706", bold=True))

    # Cherry-pick перенесення з main в release
    frags.append(circle(660, 260, 6, fill=POS, stroke="#ffffff", sw=2))
    frags.append(arrow(600, 126, 660, 254, color=POS, sw=2))
    frags.append(text(645, 190, "git cherry-pick -x\n(Лише критичний фікс)", size=10, color=POS, bold=True))

    # RC2 та GA
    frags.append(circle(780, 260, 6, fill="#d97706", stroke="#ffffff", sw=2))
    frags.append(text(780, 290, "v1.2.0-rc.2", size=11, color="#d97706", bold=True))

    frags.append(circle(890, 260, 8, fill=FIELD, stroke="#ffffff", sw=2))
    frags.append(text(890, 290, "v1.2.0 (GA)", size=12, color=FIELD, bold=True))

    # Попередження про антипатерн
    b_warn, ww, wh = textbox(500, 380, "АНТИПАТЕРН: Заборонено робити «git merge main» у release-гілку під час заморозки!\nЗлиття затягує неперевірений код і руйнує всю попередню валідацію HIL.", size=11, bold=True,
                             fill="#fef2f2", stroke=POS, sw=1.5, pad=10)
    frags.append(b_warn)

    render(os.path.join(IMG, 'branching-and-cherry-pick-model.svg'), W, H, *frags,
           title="Топологія гілкування та механіка вибіркового переносу виправлень")


# ── Фігура 3: Матриця вихідних критеріїв та HIL-ворота якості ──────────────────
def fig_exit_criteria_matrix():
    W, H = 1000, 500
    frags = []

    frags.append(rect(20, 20, 960, 460, fill="#fafbfc", stroke="#d1d5db", sw=1.5, rx=8))
    frags.append(text(500, 50, "Матриця вихідних критеріїв (Exit Criteria Gate) для схвалення реліз-кандидата", size=14, color=INK, bold=True))

    # 4 стовпці перевірок
    # Стовпець 1: Дефекти коду
    b_col1, w_c1, h_c1 = textbox(160, 190, "1. Дефекти (Bug Bar)\n\n• P0 (Блокери): 0\n• P1 (Критичні): 0\n• P2/P3: задокументовані\n• Crash / Panic rate: 0%\n• Memory Leak: 0 байт", size=11, bold=True,
                                 fill="#ffffff", stroke="#4b5563", sw=1.5, pad=12)
    frags.append(b_col1)

    # Стовпець 2: HIL і регресії
    b_col2, w_c2, h_c2 = textbox(390, 190, "2. HIL Верифікація\n\n• 100% проходження HIL\n• CAN / UART / SPI тести: OK\n• Flash Wear стрес: OK\n• WDT Recovery тест: OK\n• Симуляція збоїв живлення", size=11, bold=True,
                                 fill="#ffffff", stroke="#4b5563", sw=1.5, pad=12)
    frags.append(b_col2)

    # Стовпець 3: Бюджети ресурсів
    b_col3, w_c3, h_c3 = textbox(620, 190, "3. Бюджети заліза\n\n• Flash ROM: <= 85% сектора\n• RAM (Stack watermark): OK\n• Струм сну: <= 15 мкА\n• Піковий струм TX: у ліміті\n• Холодний старт: < 250 мс", size=11, bold=True,
                                 fill="#ffffff", stroke="#4b5563", sw=1.5, pad=12)
    frags.append(b_col3)

    # Стовпець 4: Стрес-тест (Soak)
    b_col4, w_c4, h_c4 = textbox(845, 190, "4. 72h Soak / Burn-in\n\n• 50 пристроїв на стенді\n• 72 год безперервної роботи\n• Температура: -20..+70 °C\n• 0 перезавантажень\n• Стабільність радіоканалу", size=11, bold=True,
                                 fill="#ffffff", stroke="#4b5563", sw=1.5, pad=12)
    frags.append(b_col4)

    # Стрілки зведення в Арбітр релізу
    frags.append(arrow(160, 275, 450, 360, color=MUTED, sw=1.6))
    frags.append(arrow(390, 275, 480, 360, color=MUTED, sw=1.6))
    frags.append(arrow(620, 275, 520, 360, color=MUTED, sw=1.6))
    frags.append(arrow(845, 275, 550, 360, color=MUTED, sw=1.6))

    # Центральний блок арбітражу
    b_arb, wa, ha = textbox(500, 395, "Автоматизований арбітр якості (Quality Gate Engine)\nПеревірка цифрових підтверджень, логів HIL та аналізу бінарного образу\nВсі 4 критерії виконано = Схвалення кандидата для промоції в GA", size=11, bold=True,
                            fill="#f0fdf4", stroke=FIELD, sw=2, pad=12)
    frags.append(b_arb)

    render(os.path.join(IMG, 'exit-criteria-hil-matrix.svg'), W, H, *frags,
           title="Матриця вихідних критеріїв та HIL-ворота якості")


# ── Фігура 4: Промоція від RC до GA та фабричний пакет ─────────────────────────
def fig_rc_to_ga_promotion():
    W, H = 1000, 450
    frags = []

    frags.append(rect(20, 20, 960, 410, fill="#ffffff", stroke="#e5e7eb", sw=1.5, rx=8))
    frags.append(text(500, 50, "Промоція «RC -> GA»: принцип бінарної ідентичності та фіксація артефактів", size=14, color=INK, bold=True))

    # Етап 1: Кандидат зібраний у CI
    b_rc, wr, hr = textbox(150, 160, "Реліз-кандидат\n(firmware-v1.2.0-rc.3.elf)\nЗібраний у чистому CI\nДетермінована збірка", size=11, bold=True,
                           fill="#fffbeb", stroke="#d97706", sw=1.8, pad=10)
    frags.append(b_rc)

    # Етап 2: Обчислення SHA-256
    b_sha, ws, hs = textbox(400, 160, "Хеш-ідентифікатор\nSHA-256: 4f8b9e...\nФіксація в маніфесті\n(Immutable Checksum)", size=11, bold=True,
                            fill="#f3f4f6", stroke="#4b5563", sw=1.5, pad=10)
    frags.append(b_sha)
    frags.append(arrow(245, 160, 310, 160, color=INK, sw=1.8))

    # Етап 3: HSM Криптографічний підпис
    b_sign, wsi, hsi = textbox(660, 160, "HSM Модуль підпису\nНакладання цифрового підпису\nECDSA / RSA-3072\nЗахист Secure Boot", size=11, bold=True,
                               fill="#eff6ff", stroke=NEG, sw=1.8, pad=10)
    frags.append(b_sign)
    frags.append(arrow(490, 160, 560, 160, color=INK, sw=1.8))

    # Етап 4: Golden Master Package
    b_ga, wg, hg = textbox(880, 160, "Golden Master (GA)\n(firmware-v1.2.0.bin)\nТочний двійковий клон RC3\nПідписаний та валідований", size=11, bold=True,
                           fill="#f0fdf4", stroke=FIELD, sw=2, pad=10)
    frags.append(b_ga)
    frags.append(arrow(760, 160, 785, 160, color=FIELD, sw=2))

    # Розгалуження на виробництво та OTA
    frags.append(line(880, 215, 880, 275, color=FIELD, sw=1.8))
    frags.append(arrow(880, 275, 720, 340, color=FIELD, sw=1.8))
    frags.append(arrow(880, 275, 920, 340, color=FIELD, sw=1.8))

    b_fac, wfa, hfa = textbox(650, 360, "Заводська лінія прошивки\n(Factory Flashing Rig)\nПрошивання через JTAG/SWD\nOTP / eFuse захист ключів", size=10, bold=True,
                              fill="#f9fafb", stroke="#6b7280", sw=1.5, pad=8)
    frags.append(b_fac)

    b_ota, wot, hot = textbox(910, 360, "OTA Хмарне сховище\n(CDN / Fleet Registry)\nДиференційні оновлення\nПоетапна доставка на флот", size=10, bold=True,
                              fill="#f9fafb", stroke="#6b7280", sw=1.5, pad=8)
    frags.append(b_ota)

    # Правило бінарної ідентичності
    frags.append(rect(60, 260, 480, 60, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    frags.append(text(300, 285, "ПРАВИЛО БІНАРНОЇ ІДЕНТИЧНОСТІ:", size=11, color=POS, bold=True))
    frags.append(text(300, 305, "GA = RC (байтове збігання). Перекомпільовувати реліз ЗАБОРОНЕНО.", size=10, color=INK))

    render(os.path.join(IMG, 'rc-to-ga-golden-promotion.svg'), W, H, *frags,
           title="Промоція від RC до GA та формування фабричного пакету")


if __name__ == '__main__':
    fig_freeze_stages()
    fig_branching_model()
    fig_exit_criteria_matrix()
    fig_rc_to_ga_promotion()
    print("Всі 4 фігури успішно згенеровано.")
