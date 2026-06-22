# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── two-threats: дві загрози — два щити ──────────────────────────────────────
# Ідея: підміна (хочуть запустити свій код) і підглядання (хочуть прочитати
# секрети) — різні біди; secure boot закриває першу, шифрування Flash — другу.

def fig_two_threats():
    W, H = 760, 250
    # ліва панель — підміна / secure boot
    p = [rect(40, 50, 320, 168, fill="#fbecec", stroke=POS, sw=2, rx=12)]
    p.append(text(200, 78, "Підміна прошивки", size=14, color=POS, bold=True))
    p.append(text(200, 100, "зловмисник заливає свій код", size=11, color=INK))
    b, _, _ = textbox(200, 140, "щит: secure boot", size=12, color=POS,
                      stroke=POS, fill="#ffffff", bold=True, min_w=210)
    p.append(b)
    p.append(text(200, 182, "перевіряє, чи прошивка наша,", size=10, color=MUTED))
    p.append(text(200, 200, "і не дає стартувати чужій", size=10, color=MUTED))
    # права панель — підглядання / шифрування Flash
    p.append(rect(400, 50, 320, 168, fill="#eaf0fd", stroke=NEG, sw=2, rx=12))
    p.append(text(560, 78, "Підглядання даних", size=14, color=NEG, bold=True))
    p.append(text(560, 100, "зловмисник читає вміст Flash", size=11, color=INK))
    b, _, _ = textbox(560, 140, "щит: шифрування Flash", size=12, color=NEG,
                      stroke=NEG, fill="#ffffff", bold=True, min_w=210)
    p.append(b)
    p.append(text(560, 182, "робить вміст нечитним для", size=10, color=MUTED))
    p.append(text(560, 200, "будь-кого без ключа в чипі", size=10, color=MUTED))
    render(os.path.join(OUT, "two-threats.svg"), W, H, *p,
           title="Дві різні загрози — два різні щити")


# ── signature: підпис таємним, перевірка відкритим ───────────────────────────
# Ідея: виробник ставить підпис таємним ключем; пристрій звіряє відкритим,
# зашитим у нього. Збіг — наше, ні — чуже. Сума ловить випадок, підпис — намір.

def fig_signature():
    W, H = 760, 300
    p = [rect(40, 60, 300, 120, fill="#ffffff", stroke=INK, sw=1.8, rx=10)]
    p.append(text(190, 86, "виробник", size=12, color=INK, bold=True))
    p.append(text(190, 110, "прошивка + таємний ключ", size=10, color=MUTED))
    b, _, _ = textbox(190, 150, "підписаний образ", size=12, color="#8a6d1a",
                      fill="#fff6e0", stroke="#caa24a", bold=True, min_w=200)
    p.append(b)
    p.append(arrow(340, 120, 420, 120, color=MUTED, sw=2.2))
    p.append(text(380, 108, "віддаємо", size=10, color=MUTED))
    p.append(rect(420, 60, 300, 120, fill="#ffffff", stroke=INK, sw=1.8, rx=10))
    p.append(text(570, 86, "пристрій", size=12, color=INK, bold=True))
    p.append(text(570, 110, "звіряє відкритим ключем (зашитий)", size=10, color=MUTED))
    p.append(text(500, 150, "збіг → наше", size=11, color=FIELD, bold=True))
    p.append(text(645, 150, "ні → чуже", size=11, color=POS, bold=True))
    p.append(fitbox(80, 210, 600, 64,
                    "Як печатка: підробити не може ніхто, упізнати — кожен.\n"
                    "Контрольна сума ловить випадок; підпис — навмисну підміну.",
                    size=11, color=INK, fill="#fbfbfb", stroke=MUTED, sw=1.4))
    render(os.path.join(OUT, "signature.svg"), W, H, *p,
           title="Цифровий підпис: «це справді наше?»")


# ── chain: ланцюг довіри — корінь → завантажувач → додаток ────────────────────
# Ідея: незмінний корінь у запобіжниках вивіряє завантажувач, той — додаток;
# кожна ланка перевіряє наступну, ПЕРШ НІЖ віддати їй керування.

def fig_chain():
    W, H = 760, 280
    boxes = [
        (40,  "корінь у чипі", "перепалені запобіжники", "незмінний", "#fff6e0", "#caa24a", "#8a6d1a"),
        (290, "завантажувач", "підписаний", "перевірений", "#eaf6ec", FIELD, FIELD),
        (540, "ваш додаток", "підписаний", "перевірений", "#eaf6ec", FIELD, FIELD),
    ]
    p = []
    for x, t, sub, tag, fill, stroke, ink in boxes:
        p.append(rect(x, 96, 180, 92, fill=fill, stroke=stroke, sw=2, rx=10))
        p.append(text(x + 90, 126, t, size=13, color=ink, bold=True))
        p.append(text(x + 90, 150, sub, size=10, color=MUTED))
        p.append(text(x + 90, 174, tag, size=10, color=stroke, bold=True))
    for x in (220, 470):
        p.append(arrow(x, 142, x + 70, 142, color=INK, sw=2.2))
        p.append(text(x + 35, 130, "вивіряє", size=9, color=INK))
    p.append(text(W / 2, 230, "Кожна ланка перевіряє підпис наступної, перш ніж віддати їй керування.",
                  size=11, color=INK, bold=True))
    p.append(text(W / 2, 252, "Усе тримається на корені, якого не підмінити, — це «якір довіри».",
                  size=10, color=MUTED))
    render(os.path.join(OUT, "chain.svg"), W, H, *p,
           title="Ланцюг довіри: кожна ланка ручається за наступну")


# ── secure-boot: підписи сходяться — старт; підмінили — відмова ───────────────
# Ідея: при кожному вмиканні чип проходить ланцюг; усе сходиться — запуск,
# щось підмінили — відмова стартувати.

def fig_secure_boot():
    W, H = 760, 300
    p = [rect(260, 60, 240, 52, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=8)]
    p.append(text(380, 92, "вмикання → перевірка ланцюга", size=12, color=NEG, bold=True))
    p.append(arrow(345, 112, 230, 168, color=FIELD, sw=2.2))
    p.append(arrow(415, 112, 530, 168, color=POS, sw=2.2))
    p.append(rect(50, 172, 320, 96, fill="#eaf6ec", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(210, 200, "усе сходиться", size=12, color=FIELD, bold=True))
    p.append(text(210, 224, "підписи правильні", size=10, color=INK))
    p.append(text(210, 250, "запуск", size=13, color=FIELD, bold=True))
    p.append(rect(390, 172, 320, 96, fill="#fbecec", stroke=POS, sw=1.8, rx=10))
    p.append(text(550, 200, "щось підмінили", size=12, color=POS, bold=True))
    p.append(text(550, 224, "підпис не сходиться", size=10, color=INK))
    p.append(text(550, 250, "відмова стартувати", size=12, color=POS, bold=True))
    render(os.path.join(OUT, "secure-boot.svg"), W, H, *p,
           title="Secure boot: стартує лише наше")


# ── flash-enc: вміст переплутаний, ключ замкнений у чипі ──────────────────────
# Ідея: ззовні Flash — нісенітниця; ключ розшифрування замкнений у чипі й
# назовні не виходить; чип сам на льоту розшифровує для процесора.

def fig_flash_enc():
    W, H = 760, 300
    p = [rect(50, 64, 320, 130, fill="#f4f4f4", stroke=MUTED, sw=1.8, rx=10)]
    p.append(text(210, 88, "Flash (як його видно ззовні)", size=11, color=INK, bold=True))
    for i, row in enumerate(("9F 3A C1 70 E2 88 4B",
                             "A0 1D FF 5C 39 B7 02",
                             "6E D4 91 28 AC 7F 50")):
        p.append(text(210, 116 + i * 22, row, size=11, color=MUTED))
    p.append(text(210, 210, "висмикнув і прочитав → нісенітниця", size=10, color=POS, bold=True))
    p.append(rect(410, 64, 300, 130, fill="#fff6e0", stroke="#caa24a", sw=2, rx=12))
    p.append(text(560, 90, "чип", size=13, color="#8a6d1a", bold=True))
    p.append(text(560, 118, "ключ замкнений усередині", size=10, color=INK))
    p.append(text(560, 142, "на льоту розшифровує для процесора", size=9, color=MUTED))
    p.append(text(560, 170, "ключ ніколи не покидає чип", size=10, color=FIELD, bold=True))
    p.append(fitbox(70, 234, 620, 50,
                    "Захищає вкладені ключі, ваш код і дані: навіть фізичний "
                    "доступ до чипа не віддає їхній зміст.",
                    size=11, color=INK, fill="#fbfbfb", stroke=MUTED, sw=1.4))
    render(os.path.join(OUT, "flash-enc.svg"), W, H, *p,
           title="Шифрування Flash: секрети лишаються нечитними")


# ── caution: одноразові запобіжники, цінність ключа, плата за швидкість ───────
# Ідея: захист — двері в один бік; запобіжники одноразові, ключ найцінніший,
# є плата за швидкість і складність.

def fig_caution():
    W, H = 760, 270
    cards = [
        (40,  "Запобіжники — назавжди", "перепалив — назад не повернеш", "#fbecec", POS),
        (300, "Ключ — це все", "втратив чи виказав — лихо", "#fff6e0", "#caa24a"),
        (560, "Плата за швидкість", "трохи складніше й повільніше", "#eaf0fd", NEG),
    ]
    p = []
    for x, t, sub, fill, stroke in cards:
        p.append(rect(x, 60, 200, 104, fill=fill, stroke=stroke, sw=1.8, rx=12))
        p.append(text(x + 100, 100, t, size=12, color=stroke, bold=True))
        p.append(text(x + 100, 130, sub, size=9, color=INK))
    p.append(fitbox(80, 196, 600, 56,
                    "Хобі-проєкт — зазвичай вимкнено; серійний виріб — увімкнено, "
                    "але обережно.\nЦе інструмент готового продукту, а не першого "
                    "знайомства з платою.",
                    size=11, color=INK, fill="#fff6e0", stroke="#caa24a", sw=1.4))
    render(os.path.join(OUT, "caution.svg"), W, H, *p,
           title="Ціна й обережність: двері в один бік")


# ── math: hash — короткий відбиток, зміна на біт міняє все ────────────────────
# Ідея (вставка): хеш бере дані будь-якого розміру й дає коротке число сталої
# довжини; зміна навіть на біт дає геть інший відбиток; назад не відновити.

def fig_hash():
    W, H = 760, 260
    p = [rect(40, 70, 250, 60, fill="#ffffff", stroke=INK, sw=1.6, rx=8)]
    p.append(text(165, 96, "«привіт»", size=13, color=INK))
    p.append(text(165, 118, "дані будь-якого розміру", size=9, color=MUTED))
    p.append(arrow(290, 100, 380, 100, color=INK, sw=2.2))
    p.append(text(335, 88, "Hash", size=10, color=INK, bold=True))
    b, _, _ = textbox(470, 100, "3F A9 1C", size=14, color="#8a6d1a",
                      fill="#fff6e0", stroke="#caa24a", bold=True, min_w=130)
    p.append(b)
    p.append(text(470, 140, "коротке число сталої довжини", size=9, color=MUTED))
    # зміна на біт
    p.append(rect(40, 170, 250, 50, fill="#ffffff", stroke=POS, sw=1.6, rx=8))
    p.append(text(165, 200, "«привіт.»  (один знак)", size=12, color=POS))
    p.append(arrow(290, 195, 380, 195, color=POS, sw=2.2))
    b, _, _ = textbox(470, 195, "C7 02 EE", size=13, color=POS,
                      fill="#fbecec", stroke=POS, bold=True, min_w=130)
    p.append(b)
    p.append(text(W / 2, 244, "Зміна на біт — геть інший відбиток; однобічний (назад не відновити), без колізій.",
                  size=10, color=MUTED))
    render(os.path.join(OUT, "hash.svg"), W, H, *p,
           title="Хеш: з великих даних — короткий відбиток")


# ── math: sign — хешуй, підпиши таємним, перевір відкритим ────────────────────
# Ідея (вставка): виробник хешує дані й підписує відбиток таємним ключем;
# пристрій сам хешує отримане, відкритим добуває закладений відбиток і звіряє.

def fig_sign():
    W, H = 760, 280
    # виробник
    p = [rect(40, 60, 320, 100, fill="#ffffff", stroke=INK, sw=1.8, rx=10)]
    p.append(text(200, 84, "виробник", size=12, color=INK, bold=True))
    p.append(text(200, 110, "h = Hash(дані)", size=11, color=MUTED))
    b, _, _ = textbox(200, 138, "s = Sign(h, таємний ключ)", size=11, color="#8a6d1a",
                      fill="#fff6e0", stroke="#caa24a", bold=True, min_w=240)
    p.append(b)
    p.append(arrow(360, 110, 440, 110, color=MUTED, sw=2.2))
    p.append(text(400, 98, "дані + s", size=9, color=MUTED))
    # пристрій
    p.append(rect(440, 60, 280, 100, fill="#ffffff", stroke=INK, sw=1.8, rx=10))
    p.append(text(580, 84, "пристрій", size=12, color=INK, bold=True))
    p.append(text(580, 108, "сам рахує Hash(дані)", size=10, color=MUTED))
    p.append(text(580, 128, "відкритим добуває закладений h", size=10, color=MUTED))
    p.append(text(580, 148, "і звіряє", size=10, color=INK, bold=True))
    p.append(fitbox(120, 196, 520, 56,
                    "Збіг → прошивка справжня і ціла.\n"
                    "Розбіжність → підробка: чужий код або зіпсовані дані.",
                    size=11, color=INK, fill="#fbfbfb", stroke=MUTED, sw=1.4))
    render(os.path.join(OUT, "sign.svg"), W, H, *p,
           title="Підпис і перевірка: хешуй, підпиши, перевір")


if __name__ == "__main__":
    fig_two_threats()
    fig_signature()
    fig_chain()
    fig_secure_boot()
    fig_flash_enc()
    fig_caution()
    fig_hash()
    fig_sign()
    print("figs: 8 written to", OUT)
