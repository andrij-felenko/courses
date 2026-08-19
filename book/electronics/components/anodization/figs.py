# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

def svg_path(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{dash_attr}/>'

# ── 1. Електрохімічна комірка анодування та іонний транспорт ──────────────────
def fig_anodization_cell():
    W, H = 760, 440
    p = []

    # Фон комірки (ванна з електролітом)
    p.append(rect(40, 50, 680, 350, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(380, 35, "Електрохімічне анодування вентильного металу", size=13, color=INK, bold=True))

    # Джерело живлення вгорі
    p.append(rect(290, 65, 180, 55, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    p.append(text(380, 88, "Джерело струму / напруги", size=10, color=INK, bold=True))
    p.append(text(380, 105, "U_form (CC → CV режим)", size=9, color=MUTED))

    # Дроти
    p.append(line(290, 92, 170, 92, color=POS, sw=2))
    p.append(line(170, 92, 170, 140, color=POS, sw=2))
    p.append(text(210, 84, "+ Анод", size=10, color=POS, bold=True))

    p.append(line(470, 92, 590, 92, color=NEG, sw=2))
    p.append(line(590, 92, 590, 140, color=NEG, sw=2))
    p.append(text(550, 84, "− Катод", size=10, color=NEG, bold=True))

    # Електроліт (ванна)
    p.append(rect(60, 140, 640, 240, fill="#e8f4fc", stroke="#9ac4db", sw=1.2, rx=4))
    p.append(text(380, 160, "Електроліт (нейтральний водний буфер або розчин кислоти)", size=10, color="#1e5780", italic=True))

    # Анод (зліва)
    p.append(rect(130, 180, 75, 180, fill="#d2d7df", stroke=LINE, sw=1.5, rx=3))
    p.append(text(167, 215, "Вентильний", size=10, color=INK, bold=True))
    p.append(text(167, 233, "метал", size=10, color=INK, bold=True))
    p.append(text(167, 252, "(Al, Ta, Nb)", size=9, color=MUTED))

    # Оксидний шар на аноді
    p.append(rect(205, 180, 30, 180, fill="#b5d5c5", stroke=FIELD, sw=1.5, rx=1))
    p.append(text(220, 275, "Оксид", size=9, color=FIELD, bold=True))
    p.append(text(220, 292, "Al₂O₃", size=9, color=FIELD))

    # Катод (справа)
    p.append(rect(560, 180, 60, 180, fill="#a0a8b3", stroke=LINE, sw=1.5, rx=3))
    p.append(text(590, 255, "Катод", size=10, color=INK, bold=True))
    p.append(text(590, 275, "(Pt, SS)", size=9, color=MUTED))

    # Збільшена врізка іонного транспорту по центру
    p.append(rect(245, 180, 295, 180, fill="#ffffff", stroke="#2b6cb0", sw=1.8, rx=6))
    p.append(text(392, 202, "Іонний транспорт під полем E ≈ 10⁷ В/см", size=10, color="#1a4971", bold=True))

    # Схема іонів
    p.append(rect(255, 218, 55, 130, fill="#d2d7df", stroke=LINE, sw=1, rx=2))
    p.append(text(282, 285, "Метал M", size=9, color=INK, bold=True))

    p.append(rect(310, 218, 90, 130, fill="#b5d5c5", stroke=FIELD, sw=1.2, rx=1))
    p.append(text(355, 235, "Діелектрик", size=9, color=FIELD, bold=True))
    p.append(text(355, 250, "M_x O_y", size=9, color=FIELD))

    # Стрілка катіонів M^(z+) вправо
    p.append(arrow(318, 278, 392, 278, color=POS, sw=1.8))
    p.append(text(355, 270, "Катіони Mᶻ⁺ →", size=9, color=POS, bold=True))

    # Стрілка аніонів O^(2-) / OH^(-) вліво
    p.append(arrow(392, 310, 318, 310, color=NEG, sw=1.8))
    p.append(text(355, 325, "← Аніони O²⁻ / OH⁻", size=9, color=NEG, bold=True))

    p.append(rect(400, 218, 130, 130, fill="#e8f4fc", stroke="#9ac4db", sw=1, rx=2))
    p.append(text(465, 260, "Електроліт", size=9, color="#1e5780", bold=True))
    p.append(text(465, 280, "2H⁺ + 2e⁻ → H₂↑", size=9, color="#1e5780"))
    p.append(text(465, 300, "(на катоді)", size=9, color=MUTED))

    # Пояснення внизу
    p.append(text(380, 420, "Надсильне електричне поле E змушує іони долати кристалічні бар'єри й добудовувати оксид", size=9, color=MUTED, italic=True))

    render(os.path.join(OUT, "anodization-cell.svg"), W, H, *p,
           title="Електрохімічна комірка анодування та іонний транспорт")


# ── 2. Бар'єрний оксид проти пористого (нейтральний vs кислий електроліт) ──────
def fig_barrier_vs_porous():
    W, H = 760, 410
    p = []

    p.append(text(380, 28, "Два типи анодних плівок: бар'єрна та пориста", size=13, color=INK, bold=True))

    # Ліва колонка — Бар'єрний оксид
    p.append(rect(40, 50, 325, 325, fill="#fdfefe", stroke=LINE, sw=1.5, rx=6))
    p.append(rect(40, 50, 325, 44, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(202, 77, "А. Бар'єрний оксид (конденсатори)", size=11, color=FIELD, bold=True))

    p.append(text(202, 115, "Нейтральний електроліт (pH 5–7)", size=10, color=INK, bold=True))
    p.append(text(202, 132, "Борні, фосфатні, адипатні розчини", size=9, color=MUTED))

    # Схема шарів бар'єрного оксиду
    # Електроліт
    p.append(rect(60, 150, 285, 45, fill="#e8f4fc", stroke="#bcd4e6", sw=1))
    p.append(text(202, 177, "Рідкий електроліт (або MnO₂ / полімер)", size=9, color="#1e5780"))

    # Оксид бар'єрний
    p.append(rect(60, 195, 285, 45, fill="#b5d5c5", stroke=FIELD, sw=1.5))
    p.append(text(202, 216, "Суцільний щільний діелектрик (Al₂O₃ / Ta₂O₅)", size=9, color="#0e5a32", bold=True))
    p.append(text(202, 230, "Товщина d = α_v · U_form (нанометри)", size=9, color="#0e5a32"))

    # Металева підкладка
    p.append(rect(60, 240, 285, 55, fill="#d2d7df", stroke=LINE, sw=1.2))
    p.append(text(202, 273, "Вентильний метал (Al, Ta, Nb фольга/губка)", size=9, color=INK, bold=True))

    p.append(text(65, 318, "• Оксид нерозчинний в електроліті", size=9, color=INK, anchor="start"))
    p.append(text(65, 336, "• Струм спадає до мікроамперів (самозамикання)", size=9, color=INK, anchor="start"))
    p.append(text(65, 354, "• Висока діелектрична міцність (E ~ 10⁷ В/см)", size=9, color=INK, anchor="start"))

    # Права колонка — Пористий оксид
    p.append(rect(395, 50, 325, 325, fill="#fdfefe", stroke=LINE, sw=1.5, rx=6))
    p.append(rect(395, 50, 325, 44, fill="#fef9e7", stroke="#d4ac0d", sw=1.2, rx=6))
    p.append(text(557, 77, "Б. Пористий оксид (AAO, захист/нанопори)", size=11, color="#7d6608", bold=True))

    p.append(text(557, 115, "Кислий електроліт (pH 0–2)", size=10, color=INK, bold=True))
    p.append(text(557, 132, "Сірчана H₂SO₄, щавлева H₂C₂O₄ кислоти", size=9, color=MUTED))

    # Схема пористого оксиду
    # Метал
    p.append(rect(415, 250, 285, 45, fill="#d2d7df", stroke=LINE, sw=1.2))
    p.append(text(557, 277, "Алюмінієва основа (Al)", size=9, color=INK, bold=True))

    # Стовпчики пористого оксиду
    pore_x = [425, 460, 495, 530, 565, 600, 635, 670]
    for px in pore_x:
        # стінка
        p.append(rect(px, 150, 26, 95, fill="#d5e8d4", stroke="#82b366", sw=1))
        # канал пори
        p.append(rect(px + 8, 150, 10, 87, fill="#e8f4fc", stroke="none"))
        # дно пори (бар'єрний шар куполом)
        p.append(circle(px + 13, 240, 6, fill="#b5d5c5", stroke="#82b366", sw=1))

    p.append(text(557, 145, "Вертикальні гексагональні пори", size=9, color="#27ae60", bold=True))
    p.append(text(557, 246, "Тонкий бар'єрний шар на дні пор", size=9, color="#0e5a32"))

    p.append(text(418, 318, "• Конкуренція росту поля і кислотного розчинення", size=9, color=INK, anchor="start"))
    p.append(text(418, 336, "• Товщина шару до десятків мікронів (пористі стінки)", size=9, color=INK, anchor="start"))
    p.append(text(418, 354, "• Забарвлення барвниками, наношаблони, антикорозія", size=9, color=INK, anchor="start"))

    p.append(text(380, 394, "У конденсаторах потрібен суто бар'єрний шар; пористий оксид використовують для твердих захисних покриттів", size=9, color=MUTED, italic=True))

    render(os.path.join(OUT, "barrier-vs-porous.svg"), W, H, *p,
           title="Бар'єрний оксид проти пористого")


# ── 3. Профіль електричного поля та лінійність товщини ────────────────────────
def fig_field_growth_profile():
    W, H = 760, 400
    p = []

    p.append(text(380, 28, "Енергетичний бар'єр перескоку і стала формування d = α_v · U", size=13, color=INK, bold=True))

    # Ліва половина: нахил потенціалу під полем
    p.append(rect(40, 50, 325, 310, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(text(202, 75, "Зниження бар'єру активації полем", size=11, color=INK, bold=True))

    # Вісь енергії та координати
    p.append(arrow(65, 290, 65, 100, color=LINE, sw=1.5))
    p.append(text(60, 95, "Енергія W", size=9, color=MUTED, anchor="end"))

    p.append(arrow(65, 290, 340, 290, color=LINE, sw=1.5))
    p.append(text(340, 305, "Координата x", size=9, color=MUTED, anchor="end"))

    # Потенціальні ями без поля (симетричні горби)
    p.append(svg_path("M 80 240 Q 110 150 140 240 Q 170 150 200 240 Q 230 150 260 240 Q 290 150 320 240",
                      fill="none", stroke="#94a3b8", sw=1.5, dash="4,3"))
    p.append(text(140, 145, "W₀ (без поля, ~1.5 еВ)", size=9, color="#64748b"))

    # Потенціальні ями під надсильним полем E (нахилені)
    p.append(svg_path("M 80 180 Q 110 120 140 200 Q 170 150 200 230 Q 230 180 260 260 Q 290 210 320 290",
                      fill="none", stroke=POS, sw=2))
    p.append(text(260, 175, "W = W₀ − q·a·E/2", size=9, color=POS, bold=True))
    p.append(text(260, 190, "(нахил полем E ≈ 10⁷ В/см)", size=9, color=POS))

    # Стрілка перескоку іона
    p.append(circle(110, 195, 4, fill=POS, stroke=LINE, sw=1))
    p.append(arrow(115, 190, 140, 200, color=POS, sw=1.5))
    p.append(text(125, 215, "Іонний дрейф", size=9, color=POS))

    p.append(text(202, 330, "Поле E деформує решітку й робить можливим", size=9, color=INK))
    p.append(text(202, 345, "перескок іонів за кімнатної температури", size=9, color=INK))

    # Права половина: лінійний графік товщини від напруги
    p.append(rect(395, 50, 325, 310, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(text(557, 75, "Товщина оксиду від напруги формування", size=11, color=INK, bold=True))

    # Осі графіка
    p.append(arrow(430, 290, 430, 100, color=LINE, sw=1.5))
    p.append(text(425, 95, "Товщина d (нм)", size=9, color=MUTED, anchor="end"))

    p.append(arrow(430, 290, 700, 290, color=LINE, sw=1.5))
    p.append(text(700, 305, "Напруга U_form (В)", size=9, color=MUTED, anchor="end"))

    # Лінії для металів:
    # Nb2O5: 2.5 нм/В (найкрутіша)
    p.append(line(430, 290, 670, 120, color="#9b59b6", sw=2))
    p.append(text(675, 120, "Nb₂O₅ (~2.5 нм/В)", size=9, color="#9b59b6", bold=True, anchor="start"))

    # Ta2O5: 1.9 нм/В
    p.append(line(430, 290, 670, 160, color="#e67e22", sw=2))
    p.append(text(675, 160, "Ta₂O₅ (~1.9 нм/В)", size=9, color="#e67e22", bold=True, anchor="start"))

    # Al2O3: 1.4 нм/В
    p.append(line(430, 290, 670, 200, color=FIELD, sw=2))
    p.append(text(675, 200, "Al₂O₃ (~1.4 нм/В)", size=9, color=FIELD, bold=True, anchor="start"))

    # Позначки напруги
    p.append(line(510, 288, 510, 292, color=LINE, sw=1))
    p.append(text(510, 305, "50 В", size=9, color=MUTED))
    p.append(line(590, 288, 590, 292, color=LINE, sw=1))
    p.append(text(590, 305, "100 В", size=9, color=MUTED))

    p.append(text(557, 330, "Рівновага наступає, коли E = U/d падає до E_crit", size=9, color=INK))
    p.append(text(557, 345, "і дрейф іонів практично припиняється", size=9, color=INK))

    p.append(text(380, 380, "Анодна стала α_v = 1/E_crit визначає товщину діелектрика на кожен вольт робочої напруги", size=9, color=MUTED, italic=True))

    render(os.path.join(OUT, "field-growth-profile.svg"), W, H, *p,
           title="Профіль поля та лінійність товщини оксиду")


# ── 4. Морфологія анодів: травлена Al-фольга та спечений танталовий порошок ────
def fig_foil_and_pellet():
    W, H = 760, 410
    p = []

    p.append(text(380, 28, "Технологія збільшення площі анода: травлення фольги і нанопорошки", size=13, color=INK, bold=True))

    # Ліва частина: травлена Al-фольга
    p.append(rect(40, 50, 325, 325, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(text(202, 75, "Алюмінієва фольга (тунельне травлення)", size=11, color=INK, bold=True))

    # Фольга метал
    p.append(rect(60, 95, 285, 140, fill="#d2d7df", stroke=LINE, sw=1.2, rx=2))
    p.append(text(202, 112, "Металева серцевина Al (~50–100 мкм)", size=9, color=MUTED))

    # Тунельні пори, витравлені хлоридами (глибокі канали)
    tunnels_x = [75, 100, 125, 150, 175, 200, 225, 250, 275, 300, 325]
    for tx in tunnels_x:
        # порожнина тунелю
        p.append(rect(tx, 120, 12, 100, fill="#e8f4fc", stroke="#2b6cb0", sw=1, rx=2))
        # шар оксиду всередині тунелю
        p.append(rect(tx + 2, 122, 8, 96, fill="#b5d5c5", stroke=FIELD, sw=0.8, rx=1))

    p.append(text(202, 255, "Мільйони тунелів Ø 0.1–2 мкм на см²", size=9, color="#1a4971", bold=True))
    p.append(text(202, 272, "Електрохімічне травлення в розчинах Cl⁻", size=9, color=INK))
    p.append(text(202, 290, "Збільшення активної площі A у 50–100 разів", size=9, color=FIELD, bold=True))
    p.append(text(202, 308, "Конформний оксид Al₂O₃ повторює всі вигини", size=9, color=INK))
    p.append(text(202, 345, "Рідкий електроліт затікає вглиб кожного тунелю", size=9, color=MUTED, italic=True))

    # Права частина: танталова спечена губка
    p.append(rect(395, 50, 325, 325, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(text(557, 75, "Танталова анодна таблетка (спечений порошок)", size=11, color=INK, bold=True))

    # Губка з крупинок
    p.append(rect(415, 95, 285, 140, fill="#fdf2e9", stroke="#e67e22", sw=1.2, rx=4))

    # Крупинки танталу зі з'єднаннями (шийками)
    grains = [
        (445, 125, 14), (475, 120, 16), (510, 130, 13), (545, 122, 15), (580, 128, 14), (615, 120, 16), (650, 125, 13),
        (440, 160, 15), (470, 155, 14), (505, 165, 17), (540, 158, 15), (575, 162, 14), (610, 155, 16), (645, 160, 15),
        (450, 195, 14), (480, 200, 15), (515, 192, 14), (550, 202, 16), (585, 195, 15), (620, 200, 14), (655, 195, 13)
    ]
    for gx, gy, gr in grains:
        p.append(circle(gx, gy, gr + 2, fill="#b5d5c5", stroke=FIELD, sw=0.8)) # оксид Ta2O5
        p.append(circle(gx, gy, gr, fill="#7f8c8d", stroke=LINE, sw=1))       # тантал зерно

    p.append(text(557, 255, "Нанопорошок Ta (CV-номінал до 150 000 мкКл/г)", size=9, color="#b9770e", bold=True))
    p.append(text(557, 272, "Вакуумне спікання при 1400–1800 °C (утворення шийок)", size=9, color=INK))
    p.append(text(557, 290, "Об'ємна пористість 40–60%, площа ~2–10 м²/г", size=9, color=FIELD, bold=True))
    p.append(text(557, 308, "Твердий катод (MnO₂ або PEDOT:PSS) у порах", size=9, color=INK))
    p.append(text(557, 345, "Дає рекордну питому ємність у мінімальному об'ємі", size=9, color=MUTED, italic=True))

    p.append(text(380, 390, "Обидва методи розгортають 2D-площу в 3D-лабіринт, компенсуючи малі геометричні розміри деталі", size=9, color=MUTED, italic=True))

    render(os.path.join(OUT, "foil-and-pellet-morphology.svg"), W, H, *p,
           title="Морфологія анодів: травлена фольга і спечений порошок")


# ── 5. Самозаліковування проти іскрового пробою ───────────────────────────────
def fig_self_healing_and_breakdown():
    W, H = 760, 400
    p = []

    p.append(text(380, 28, "Поведінка діелектрика під навантаженням: відновлення проти пробою", size=13, color=INK, bold=True))

    # Ліва колонка: Самозаліковування (Self-healing)
    p.append(rect(40, 50, 325, 310, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(rect(40, 50, 325, 40, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(202, 75, "А. Ефект самозаліковування (Self-healing)", size=11, color=FIELD, bold=True))

    # Метал + оксид + тріщина
    p.append(rect(60, 110, 285, 45, fill="#d2d7df", stroke=LINE, sw=1))
    p.append(text(202, 136, "Вентильний метал (Al / Ta анод)", size=9, color=INK))

    p.append(rect(60, 155, 285, 35, fill="#b5d5c5", stroke=FIELD, sw=1.2))
    p.append(text(120, 176, "Оксидний діелектрик", size=9, color="#0e5a32"))

    # Дефект / тріщина
    p.append(rect(230, 155, 14, 35, fill="#fbecec", stroke=POS, sw=1.2))
    p.append(text(237, 176, "!", size=10, color=POS, bold=True))

    # Катод зверху
    p.append(rect(60, 190, 285, 35, fill="#e8f4fc", stroke="#9ac4db", sw=1))
    p.append(text(202, 211, "Електроліт / Провідний полімер (катод)", size=9, color="#1e5780"))

    # Стрілка відновлення
    p.append(arrow(237, 245, 237, 195, color=FIELD, sw=1.8))
    p.append(text(65, 260, "1. Рідкий електроліт: електрохімічне доокиснення Al₂O₃", size=9, color=FIELD, bold=True, anchor="start"))
    p.append(text(65, 278, "2. Полімер / MnO₂: локальний нагрів перетворює катод", size=9, color=INK, anchor="start"))
    p.append(text(65, 295, "в ізолятор (вигорання дефекту без пожежі)", size=9, color=INK, anchor="start"))
    p.append(text(202, 335, "Струм витоку падає, дефект ізолюється", size=10, color=FIELD, bold=True))

    # Права колонка: Іскровий пробій / Сцинтиляція
    p.append(rect(395, 50, 325, 310, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(rect(395, 50, 325, 40, fill="#fbecec", stroke=POS, sw=1.2, rx=6))
    p.append(text(557, 75, "Б. Іскровий пробій (Scintillation / PEO)", size=11, color=POS, bold=True))

    p.append(rect(415, 110, 285, 45, fill="#d2d7df", stroke=LINE, sw=1))
    p.append(text(557, 136, "Метал (напруга U_form > U_breakdown)", size=9, color=INK))

    p.append(rect(415, 155, 285, 35, fill="#b5d5c5", stroke=FIELD, sw=1.2))

    # Іскри / плазмові мікророзряди
    p.append(svg_path("M 530 195 L 538 172 L 532 172 L 542 150 L 536 170 L 544 170 Z", fill="#f39c12", stroke=POS, sw=1))
    p.append(svg_path("M 580 195 L 588 172 L 582 172 L 592 150 L 586 170 L 594 170 Z", fill="#f39c12", stroke=POS, sw=1))

    p.append(rect(415, 190, 285, 35, fill="#e8f4fc", stroke="#9ac4db", sw=1))
    p.append(text(557, 211, "Електроліт під високою напругою", size=9, color="#1e5780"))

    p.append(text(418, 260, "1. Електричне поле перевищує діелектричну міцність", size=9, color=POS, bold=True, anchor="start"))
    p.append(text(418, 278, "2. Лавинна іонізація та локальні плазмові мікродуги", size=9, color=INK, anchor="start"))
    p.append(text(418, 295, "3. Кристалізація аморфного оксиду (руйнування ізоляції)", size=9, color=INK, anchor="start"))
    p.append(text(557, 335, "Утворення грубих керамічних плівок (PEO)", size=10, color=POS, bold=True))

    p.append(text(380, 380, "Конденсатори формують нижче напруги сцинтиляції; явище PEO застосовують для надтвердої кераміки", size=9, color=MUTED, italic=True))

    render(os.path.join(OUT, "self-healing-and-breakdown.svg"), W, H, *p,
           title="Самозаліковування та іскровий пробій")


if __name__ == "__main__":
    fig_anodization_cell()
    fig_barrier_vs_porous()
    fig_field_growth_profile()
    fig_foil_and_pellet()
    fig_self_healing_and_breakdown()
    print("Всі фігури згенеровано успішно.")
