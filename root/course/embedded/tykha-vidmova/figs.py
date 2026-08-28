# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

ALERT_RED   = "#c0392b"
WARN_ORANGE = "#d35400"
SAFE_GREEN  = "#27ae60"
COLD_BLUE   = "#2980b9"
PANEL_BG    = "#f8fafc"
BOX_BG      = "#ffffff"

def fig_silent_failure_anatomy():
    W, H = 880, 420
    p = []

    # 1. Physical / Sensor Layer (Left)
    p.append(rect(30, 60, 240, 310, fill=PANEL_BG, stroke=MUTED, sw=1.5, rx=8))
    p.append(text(150, 85, "Чутливий елемент і АЦП", size=13, color=INK, bold=True))
    
    b1, _, _ = textbox(150, 140, "Зависання ядра АЦП / шини\nI2C-регістр віддає старе 23.4 °C\n(Stuck Value)", size=11, fill="#fdedec", stroke=ALERT_RED, color=ALERT_RED)
    p.append(b1)
    
    b2, _, _ = textbox(150, 230, "Деградація мембрани / хімії\nЗсув нульової точки (+8 °C)\n(Sensor Drift / Aging)", size=11, fill="#fef9e7", stroke=WARN_ORANGE, color=WARN_ORANGE)
    p.append(b2)
    
    b3, _, _ = textbox(150, 320, "Залипання контакту\nГеркон / кінцевик замкнено\n(Dry Contact Stuck)", size=11, fill="#f4f6f8", stroke=MUTED, color=INK)
    p.append(b3)

    # 2. MCU / Device Layer (Middle)
    p.append(rect(310, 60, 260, 310, fill=PANEL_BG, stroke=MUTED, sw=1.5, rx=8))
    p.append(text(440, 85, "Мікроконтролер (MCU / RTOS)", size=13, color=INK, bold=True))
    
    b_mcu1, _, _ = textbox(440, 135, "RTOS-планувальник працює\nWatchdog справно годується\n(Liveness Check: PASS)", size=11, fill="#eafaf1", stroke=SAFE_GREEN, color=SAFE_GREEN)
    p.append(b_mcu1)
    
    b_mcu2, _, _ = textbox(440, 225, "Зчитування буфера шини:\nОтримує 0x00EB (23.4 °C)\nПомилки зв'язку I2C нема (ACK)", size=11, fill=BOX_BG, stroke=MUTED, color=INK)
    p.append(b_mcu2)
    
    b_mcu3, _, _ = textbox(440, 315, "Формування телеметрії:\nMQTT: {\"temp\": 23.4, \"status\": \"OK\"}\nWi-Fi / LTE пакет відправлено", size=11, fill=BOX_BG, stroke=COLD_BLUE, color=COLD_BLUE)
    p.append(b_mcu3)

    # 3. Cloud / Server Layer (Right)
    p.append(rect(610, 60, 240, 310, fill=PANEL_BG, stroke=MUTED, sw=1.5, rx=8))
    p.append(text(730, 85, "Сервер і диспетчер", size=13, color=INK, bold=True))
    
    b_srv1, _, _ = textbox(730, 140, "HTTP 200 / MQTT Broker OK\nСтатус вузла: ЗЕЛЕНИЙ\n«Пристрій на зв'язку»", size=11, fill="#eafaf1", stroke=SAFE_GREEN, color=SAFE_GREEN)
    p.append(b_srv1)
    
    b_srv2, _, _ = textbox(730, 230, "Ілюзія норми:\nЗначення 23.4 °C стабільне\nАлерти мовчать", size=11, fill="#fef9e7", stroke=WARN_ORANGE, color=WARN_ORANGE)
    p.append(b_srv2)
    
    b_srv3, _, _ = textbox(730, 320, "РЕАЛЬНІСТЬ:\nОб'єкт перегрівається (>85 °C)\nАварія розвивається тихо", size=11, fill="#fdedec", stroke=ALERT_RED, color=ALERT_RED, bold=True)
    p.append(b_srv3)

    # Connecting arrows
    p.append(arrow(270, 140, 310, 140, color=ALERT_RED, sw=2))
    p.append(arrow(270, 230, 310, 230, color=WARN_ORANGE, sw=2))
    p.append(arrow(570, 225, 610, 225, color=COLD_BLUE, sw=2))
    p.append(arrow(570, 315, 610, 315, color=COLD_BLUE, sw=2))

    # Bottom summary box
    b_bot, _, _ = textbox(440, 395, "Тиха відмова: інфраструктура зв'язку та ОС функціонують бездоганно, але семантичний зміст вимірювання втрачено", size=11.5, fill="#fff", stroke=ALERT_RED, color=ALERT_RED, bold=True)
    p.append(b_bot)

    render(os.path.join(OUT, "silent-failure-anatomy.svg"), W, H, *p,
           title="Анатомія тихої відмови: розрив між життям вузла та валідністю даних")

def fig_sensor_health_metrics():
    W, H = 880, 440
    p = []

    # Layer 1: Plausibility / Physical Rails
    p.append(rect(40, 60, 250, 320, fill=PANEL_BG, stroke=MUTED, sw=1.5, rx=8))
    p.append(text(165, 85, "1. Фізичні межі (Plausibility)", size=12.5, color=INK, bold=True))
    
    # Mini chart for plausibility
    p.append(rect(60, 110, 210, 120, fill="#fff", stroke=MUTED, sw=1))
    p.append(line(60, 130, 270, 130, color=ALERT_RED, sw=1.5, dash="4 3")) # upper rail
    p.append(line(60, 210, 270, 210, color=ALERT_RED, sw=1.5, dash="4 3")) # lower rail
    p.append(text(265, 124, "Vdd (3.3 В / КЗ)", size=9, color=ALERT_RED, anchor="end"))
    p.append(text(265, 222, "GND (0 В / Обрив)", size=9, color=ALERT_RED, anchor="end"))
    p.append(rect(60, 145, 210, 50, fill="#eafaf1", stroke=SAFE_GREEN, sw=1, rx=2))
    p.append(text(165, 173, "Допустимий робочий коридор", size=10, color=SAFE_GREEN, bold=True))
    
    b_p1, _, _ = textbox(165, 260, "Відсікання електричних крайнощів:\n0 В (обрив сенсора при pull-down)\n3.3 В (закорочення на шину живлення)", size=10.5, fill="#fff", stroke=MUTED, color=INK)
    p.append(b_p1)
    
    b_p2, _, _ = textbox(165, 335, "Фізична неможливість:\nВологість > 100% або < 0%\nТиск у кімнаті < 300 гПа", size=10.5, fill="#fff", stroke=MUTED, color=INK)
    p.append(b_p2)

    # Layer 2: Gradient / Rate of Change
    p.append(rect(315, 60, 250, 320, fill=PANEL_BG, stroke=MUTED, sw=1.5, rx=8))
    p.append(text(440, 85, "2. Градієнтний ліміт (dY/dt)", size=12.5, color=INK, bold=True))
    
    # Mini chart for gradient
    p.append(rect(335, 110, 210, 120, fill="#fff", stroke=MUTED, sw=1))
    # continuous physical curve
    p.append(line(345, 200, 410, 175, color=SAFE_GREEN, sw=2))
    p.append(text(380, 205, "Фізична інерція", size=9, color=SAFE_GREEN))
    # abrupt step
    p.append(line(410, 175, 415, 125, color=ALERT_RED, sw=2.5))
    p.append(line(415, 125, 490, 125, color=ALERT_RED, sw=2))
    p.append(text(475, 140, "Стрибок: |ΔY/Δt| > ліміт", size=9, color=ALERT_RED, bold=True, anchor="end"))
    
    b_g1, _, _ = textbox(440, 260, "Теплоємність і гідравліка:\nТемпература 100 кг бойлера\nне може стрибнути на +30 °C за 10 мс", size=10.5, fill="#fff", stroke=MUTED, color=INK)
    p.append(b_g1)
    
    b_g2, _, _ = textbox(440, 335, "Діагностика збою:\nІмпульсна завада, тріщина на платі,\nзбій фрейму АЦП без CRC", size=10.5, fill="#fff", stroke=MUTED, color=INK)
    p.append(b_g2)

    # Layer 3: Noise & Zero-Variance
    p.append(rect(590, 60, 250, 320, fill=PANEL_BG, stroke=MUTED, sw=1.5, rx=8))
    p.append(text(715, 85, "3. Дисперсія та шум (σ²)", size=12.5, color=INK, bold=True))
    
    # Mini chart for noise vs zero-variance
    p.append(rect(610, 110, 210, 120, fill="#fff", stroke=MUTED, sw=1))
    # noisy line (healthy)
    p.append(line(620, 150, 635, 145, color=SAFE_GREEN, sw=1.5))
    p.append(line(635, 145, 650, 154, color=SAFE_GREEN, sw=1.5))
    p.append(line(650, 154, 665, 147, color=SAFE_GREEN, sw=1.5))
    p.append(line(665, 147, 680, 152, color=SAFE_GREEN, sw=1.5))
    p.append(text(650, 135, "Живий шум (σ² > 0)", size=9, color=SAFE_GREEN))
    # flat line (frozen)
    p.append(line(680, 152, 700, 185, color=WARN_ORANGE, sw=1.5, dash="3 3"))
    p.append(line(700, 185, 805, 185, color=ALERT_RED, sw=2.5))
    p.append(text(760, 202, "Зависання (σ² = 0.000)", size=9, color=ALERT_RED, bold=True))

    b_n1, _, _ = textbox(715, 260, "Природний термічний шум:\nФізичний сенсор завжди коливається\nна рівні молодших бітів (LSB)", size=10.5, fill="#fff", stroke=MUTED, color=INK)
    p.append(b_n1)
    
    b_n2, _, _ = textbox(715, 335, "Zero-Variance критерій:\nДисперсія = 0 на вікні 100 відліків\n= мертвий кристал або застряглий буфер", size=10.5, fill="#fff", stroke=MUTED, color=INK)
    p.append(b_n2)

    # Bottom summary box
    b_bot, _, _ = textbox(440, 410, "Комплексний фільтр перевіряє не лише поточне число, а й динаміку, швидкість зміни та статистичний спектр сигналу", size=11, fill="#fff", stroke=SAFE_GREEN, color=SAFE_GREEN, bold=True)
    p.append(b_bot)

    render(os.path.join(OUT, "sensor-health-metrics.svg"), W, H, *p,
           title="Три рівні локальної перевірки здоров'я сенсорного сигналу")

def fig_cross_checking_voting():
    W, H = 900, 440
    p = []

    # 1. Homogeneous Redundancy (Left half)
    p.append(rect(20, 60, 415, 330, fill=PANEL_BG, stroke=MUTED, sw=1.5, rx=8))
    p.append(text(227, 85, "Апаратна надлишковість (2oo3 Voting)", size=13, color=INK, bold=True))
    
    b_s1, _, _ = textbox(105, 135, "Сенсор A\n24.1 °C (OK)", size=10, fill="#eafaf1", stroke=SAFE_GREEN, color=SAFE_GREEN)
    p.append(b_s1)
    b_s2, _, _ = textbox(105, 205, "Сенсор B\n24.3 °C (OK)", size=10, fill="#eafaf1", stroke=SAFE_GREEN, color=SAFE_GREEN)
    p.append(b_s2)
    b_s3, _, _ = textbox(105, 275, "Сенсор C (дрейф)\n31.8 °C (FLT)", size=10, fill="#fdedec", stroke=ALERT_RED, color=ALERT_RED)
    p.append(b_s3)

    b_voter, _, _ = textbox(305, 205, "Мажоритарний\nкворум (2oo3):\nМедіана = 24.2 °C\nСенсор C ізольовано", size=10.5, fill="#fff", stroke=COLD_BLUE, color=COLD_BLUE, bold=True)
    p.append(b_voter)

    p.append(arrow(165, 135, 235, 185, color=SAFE_GREEN, sw=1.8))
    p.append(arrow(165, 205, 235, 205, color=SAFE_GREEN, sw=1.8))
    p.append(arrow(165, 275, 235, 225, color=ALERT_RED, sw=1.8))

    b_vote_note, _, _ = textbox(227, 350, "Кворум захищає від раптового збою 1 з 3 каналів;\nнесправний сенсор позначається прапорцем деградації", size=9.5, fill="#fff", stroke=MUTED, color=MUTED)
    p.append(b_vote_note)

    # 2. Analytical Redundancy (Right half)
    p.append(rect(460, 60, 420, 330, fill=PANEL_BG, stroke=MUTED, sw=1.5, rx=8))
    p.append(text(670, 85, "Аналітична / перехресна верифікація", size=13, color=INK, bold=True))

    b_in1, _, _ = textbox(565, 135, "Струм I(t) + Т середовища", size=10, fill=BOX_BG, stroke=MUTED, color=INK)
    p.append(b_in1)

    b_mod, _, _ = textbox(565, 215, "Теплова модель АКБ:\nТ_розр = f(I, R, t)\nОчікувано: 38.5 °C", size=10, fill="#eaf2f8", stroke=COLD_BLUE, color=COLD_BLUE)
    p.append(b_mod)

    b_meas, _, _ = textbox(775, 135, "NTC-термістор:\nТ_вимір: 21.0 °C\n(Залипання)", size=10, fill="#fdedec", stroke=ALERT_RED, color=ALERT_RED)
    p.append(b_meas)

    b_comp, _, _ = textbox(670, 290, "Нев'язка: |T_вимір − T_розр| = 17.5 °C > Поріг\nВисновок: NTC залип; перехід на розрахункову модель", size=9.5, fill="#fff", stroke=ALERT_RED, color=ALERT_RED, bold=True)
    p.append(b_comp)

    p.append(arrow(565, 155, 565, 185, color=MUTED, sw=1.5))
    p.append(arrow(565, 245, 625, 270, color=COLD_BLUE, sw=1.8))
    p.append(arrow(775, 165, 715, 270, color=ALERT_RED, sw=1.8))

    b_an_note, _, _ = textbox(670, 350, "Зіставлення фізично пов'язаних величин (тиск ↔ оберти)\nвикриває тихий збій без дублювання однакових сенсорів", size=9.5, fill="#fff", stroke=MUTED, color=MUTED)
    p.append(b_an_note)

    # Bottom summary box
    b_bot, _, _ = textbox(450, 415, "Перехресна верифікація викриває тихий дрейф, який легко проходить поодинокі фільтри фізичних меж", size=11, fill="#fff", stroke=COLD_BLUE, color=COLD_BLUE, bold=True)
    p.append(b_bot)

    render(os.path.join(OUT, "cross-checking-voting.svg"), W, H, *p,
           title="Перехресна верифікація та аналітична надлишковість проти тихого дрейфу")

if __name__ == "__main__":
    fig_silent_failure_anatomy()
    fig_sensor_health_metrics()
    fig_cross_checking_voting()
    print("Figures generated successfully.")
