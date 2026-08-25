# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
WARM_FILL = "#fff6e5"
GREY_FILL = "#eceff1"


# ── 1. Реєстр імен і добір за пріоритетом ───────────────────────────────────
def fig_registry_lookup():
    W, H = 1420, 700
    p = []

    x_cons, x_name, x_reg, x_win = 200, 545, 900, 1275

    p.append(text(x_cons, 90, "споживачі в ядрі", size=14, bold=True))
    p.append(text(x_name, 90, "те, що вони кажуть", size=14, bold=True))
    p.append(text(x_reg, 90, "реєстр алгоритмів", size=14, bold=True))
    p.append(text(x_win, 90, "кого віддадуть", size=14, bold=True))

    cons = [
        (185, "dm-crypt"),
        (300, "fscrypt"),
        (415, "AF_ALG із програми"),
    ]
    cons_edges = []
    for y, label in cons:
        fr, w, h = textbox(x_cons, y, label, size=13, pad=12,
                           fill=BLUE_FILL, stroke=LINE)
        p.append(fr)
        cons_edges.append((y, x_cons + w / 2))

    name_fr, name_w, name_h = textbox(x_name, 300, ["ім'я алгоритму", "«xts(aes)»"],
                                      size=14, pad=16, fill=WARM_FILL,
                                      stroke=LINE, bold=True)
    p.append(name_fr)
    for y, xe in cons_edges:
        p.append(arrow(xe, y, x_name - name_w / 2 - 6, 300))

    rows = [
        (185, ["xts-aes-aesni", "пріоритет 401"], GREEN_FILL, LINE),
        (300, ["xts-aes-ce (ARM)", "модуля тут немає"], GREY_FILL, MUTED),
        (415, ["xts(ecb(aes-generic))", "пріоритет 100"], GREY_FILL, MUTED),
    ]
    reg_edges = []
    for y, lines, fill, stroke in rows:
        fr, w, h = textbox(x_reg, y, lines, size=13, pad=13,
                           fill=fill, stroke=stroke, sw=1.4, min_w=280)
        p.append(fr)
        reg_edges.append((y, x_reg - w / 2, x_reg + w / 2))

    p.append(arrow(x_name + name_w / 2, 300, x_reg - 145, 300))

    win_fr, win_w, win_h = textbox(x_win, 185, ["обрано", "xts-aes-aesni"],
                                   size=13, pad=14, fill=GREEN_FILL, stroke=LINE)
    p.append(win_fr)
    p.append(arrow(reg_edges[0][2], 185, x_win - win_w / 2 - 6, 185))

    p.append(text(W / 2, 545,
                  "Споживач називає лише узагальнене ім'я. Під цим іменем у реєстрі стоїть кілька реалізацій —",
                  size=13, color=MUTED))
    p.append(text(W / 2, 573,
                  "переносна на C, векторна на інструкціях процесора, апаратний рушій. Виграє найвищий пріоритет.",
                  size=13, color=MUTED))
    p.append(text(W / 2, 615,
                  "Модуль не завантажився — вибір мовчки падає на наступну реалізацію, і це видно лише в /proc/crypto.",
                  size=13, color=POS))

    render(os.path.join(IMG, 'registry-lookup.svg'), W, H, *p,
           title="Ім'я стоїть між споживачем і реалізацією")


# ── 2. Ім'я як вираз із шаблонів ────────────────────────────────────────────
def fig_name_grammar():
    W, H = 1400, 700
    p = []

    root_y, mid_y, leaf_y = 150, 320, 480

    root_fr, root_w, root_h = textbox(430, root_y, "authenc(hmac(sha256),cbc(aes))",
                                      size=15, pad=16, fill=WARM_FILL,
                                      stroke=LINE, bold=True)
    p.append(root_fr)
    p.append(text(430, root_y - root_h / 2 - 16, "те, що просить IPsec",
                  size=13, color=MUTED))

    kids = [
        (215, "hmac(sha256)", "шаблон hmac", "sha256", "геш"),
        (645, "cbc(aes)", "шаблон cbc", "aes", "блоковий шифр"),
    ]
    for x, mid_label, tpl_note, leaf_label, leaf_note in kids:
        fr, w, h = textbox(x, mid_y, mid_label, size=14, pad=14,
                           fill=BLUE_FILL, stroke=LINE)
        p.append(fr)
        p.append(text(x, mid_y + h / 2 + 26, tpl_note, size=12, color=MUTED))
        lf, lw, lh = textbox(x, leaf_y, leaf_label, size=14, pad=14,
                             fill=GREEN_FILL, stroke=LINE)
        p.append(lf)
        p.append(text(x, leaf_y + lh / 2 + 26, leaf_note, size=12, color=MUTED))
        p.append(arrow(430, root_y + root_h / 2, x, mid_y - h / 2 - 4))
        p.append(arrow(x, mid_y + h / 2 + 40, x, leaf_y - lh / 2 - 4))

    alt_fr, alt_w, alt_h = textbox(1145, root_y + 40,
                                   ["один запис від заліза:",
                                    "authenc-hmac-sha256-cbc-aes-caam",
                                    "пріоритет 3000"],
                                   size=13, pad=15, fill=GREY_FILL, stroke=MUTED, sw=1.4)
    p.append(alt_fr)
    p.append(line(1145 - alt_w / 2, root_y + 40, 430 + root_w / 2, root_y + 12,
                  color=MUTED, dash="6 5"))
    p.append(text(1145, root_y + 40 + alt_h / 2 + 30,
                  "те саме узагальнене ім'я", size=12, color=MUTED))

    p.append(text(W / 2, 610,
                  "Ядро вміє скласти алгоритм із шаблону й базового шифру на першу ж вимогу.",
                  size=13, color=MUTED))
    p.append(text(W / 2, 640,
                  "Але порівнює воно рядок цілком — тож рушій може зареєструвати всю конструкцію одним шматком.",
                  size=13, color=NEG))

    render(os.path.join(IMG, 'name-grammar.svg'), W, H, *p,
           title="Ім'я алгоритму — це вираз, а не ярлик")


# ── 3. Перетворення, запит і два шляхи результату ───────────────────────────
def fig_tfm_and_request():
    W, H = 1420, 680
    p = []

    tfm_fr, tfm_w, tfm_h = textbox(250, 300,
                                   ["tfm — перетворення",
                                    "алгоритм обрано за іменем",
                                    "ключ розгорнуто (setkey)",
                                    "живе довго, спільний"],
                                   size=13, pad=16, fill=BLUE_FILL, stroke=LINE)
    p.append(tfm_fr)
    p.append(text(250, 300 - tfm_h / 2 - 20, "дороге, робиться один раз",
                  size=12, color=MUTED))

    req_fr, req_w, req_h = textbox(700, 300,
                                   ["запит — одна операція",
                                    "вхід і вихід (scatterlist)",
                                    "початковий вектор",
                                    "колбек"],
                                   size=13, pad=16, fill=WARM_FILL, stroke=LINE)
    p.append(req_fr)
    p.append(text(700, 300 - req_h / 2 - 20, "дешеве, робиться щоразу",
                  size=12, color=MUTED))

    p.append(arrow(250 + tfm_w / 2, 300, 700 - req_w / 2 - 6, 300))

    ok_fr, ok_w, ok_h = textbox(1180, 165,
                                ["повертає 0", "шифротекст уже на місці"],
                                size=13, pad=14, fill=GREEN_FILL, stroke=LINE)
    p.append(ok_fr)
    p.append(text(1180, 165 - ok_h / 2 - 22, "переносна або векторна реалізація",
                  size=12, color=MUTED))

    async_fr, async_w, async_h = textbox(1180, 445,
                                         ["повертає −EINPROGRESS",
                                          "колбек прийде з переривання"],
                                         size=13, pad=14, fill=GREY_FILL, stroke=LINE)
    p.append(async_fr)
    p.append(text(1180, 445 + async_h / 2 + 26, "рушій у залізі",
                  size=12, color=MUTED))

    p.append(arrow(700 + req_w / 2, 285, 1180 - ok_w / 2 - 6, 175))
    p.append(arrow(700 + req_w / 2, 315, 1180 - async_w / 2 - 6, 435))

    p.append(text(W / 2, 575,
                  "Один tfm обслуговує тисячі запитів: ключ і вибір реалізації в нього вже вкладені.",
                  size=13, color=MUTED))
    p.append(text(W / 2, 605,
                  "Два можливі повернення — саме тому операція описана окремим об'єктом із колбеком.",
                  size=13, color=NEG))

    render(os.path.join(IMG, 'tfm-and-request.svg'), W, H, *p,
           title="Перетворення тримає ключ, запит несе дані")


# ── 4. Розкладка одного буфера під AEAD ─────────────────────────────────────
def fig_aead_buffer():
    W, H = 1400, 640
    p = []

    x0 = 210
    w_aad, w_msg, w_tag = 250, 470, 250
    xs = [x0, x0 + w_aad, x0 + w_aad + w_msg]
    hbar = 78

    p.append(text(W / 2, 62,
                  "один шматок із kmalloc: 16 + 64 + 16 = 96 байтів",
                  size=16, bold=True))
    p.append(text(W / 2, 92,
                  "sg_init_one описує його цілком — де закінчується зона, кажуть числа в запиті, а не список сегментів",
                  size=13, color=MUTED))

    y1 = 190
    p.append(text(x0, y1 - hbar / 2 - 20, "на вхід шифрування",
                  size=13, bold=True, anchor="start"))
    p.append(fitbox(xs[0], y1 - hbar / 2, w_aad, hbar,
                    ["заголовок (AAD)", "16 байтів"], size=13, fill=GREY_FILL))
    p.append(fitbox(xs[1], y1 - hbar / 2, w_msg, hbar,
                    ["відкритий текст", "64 байти"], size=13, fill=BLUE_FILL))
    p.append(fitbox(xs[2], y1 - hbar / 2, w_tag, hbar,
                    ["порожньо", "місце під тег"], size=13, fill=GREY_FILL))

    y2 = 370
    p.append(text(x0, y2 - hbar / 2 - 20, "на вихід шифрування",
                  size=13, bold=True, anchor="start"))
    p.append(fitbox(xs[0], y2 - hbar / 2, w_aad, hbar,
                    ["заголовок", "не змінився"], size=13, fill=GREY_FILL))
    p.append(fitbox(xs[1], y2 - hbar / 2, w_msg, hbar,
                    ["шифротекст", "64 байти"], size=13, fill=GREEN_FILL))
    p.append(fitbox(xs[2], y2 - hbar / 2, w_tag, hbar,
                    ["тег", "16 байтів"], size=13, fill=WARM_FILL))

    x_arrow = xs[1] + w_msg / 2
    p.append(arrow(x_arrow, y1 + hbar / 2 + 4, x_arrow, y2 - hbar / 2 - 4))
    p.append(text(x0 + 40, 285, "crypto_aead_encrypt()",
                  size=13, color=NEG, anchor="start"))

    p.append(text(W / 2, 490,
                  "aead_request_set_ad(req, 16) — скільки з початку лише автентифікуємо",
                  size=13, color=MUTED))
    p.append(text(W / 2, 520,
                  "aead_request_set_crypt(req, sg, sg, 64, iv) — шифруємо лише текст, тег ляже одразу за ним",
                  size=13, color=MUTED))
    p.append(text(W / 2, 556,
                  "на розшифрування те саме місце, але довжина вже 64 + 16 = 80: тег входить у неї",
                  size=13, color=POS))

    render(os.path.join(IMG, 'aead-buffer.svg'), W, H, *p,
           title="Одна зона пам'яті на всі три частини AEAD")


# ── 5. Хто виконує шифр і як від цього мінявся інтерфейс ────────────────────
def fig_executors_timeline():
    W, H = 1640, 720
    p = []

    cols = [
        (265, "2002 · 2.5.45",
         ["програма на процесорі", "й більше ніхто"],
         ["реєстр імен алгоритмів", "один тип шифру", "перший споживач — IPsec"]),
        (720, "2006–2007 · 2.6.19, 2.6.22",
         ["плата-рушій", "із власною чергою"],
         ["шаблони й cryptomgr", "cra_driver_name і пріоритет", "асинхронний контракт",
          "blkcipher, далі ablkcipher"]),
        (1140, "2011 · 2.6.38",
         ["той самий рушій,", "але викликає програма"],
         ["AF_ALG: сокет як вхід", "у той самий реєстр"]),
        (1495, "2015 → 2024",
         ["вектори всередині", "самого процесора"],
         ["4.3: єдиний skcipher", "5.5: близнюків прибрано", "6.7: лінійний lskcipher"]),
    ]

    y_line = 175
    p.append(line(150, y_line, W - 60, y_line, color=MUTED, sw=2))

    for x, era, who, gained in cols:
        p.append(circle(x, y_line, 7, fill=NEG, stroke=NEG))
        p.append(text(x, y_line - 28, era, size=14, bold=True))

        who_fr, who_w, who_h = textbox(x, 300, who, size=13, pad=14,
                                       fill=WARM_FILL, stroke=LINE)
        p.append(who_fr)
        p.append(line(x, y_line + 12, x, 300 - who_h / 2 - 4, color=MUTED))

        got_fr, got_w, got_h = textbox(x, 500, gained, size=13, pad=14,
                                       fill=BLUE_FILL, stroke=LINE)
        p.append(got_fr)
        p.append(arrow(x, 300 + who_h / 2 + 4, x, 500 - got_h / 2 - 6))

    p.append(text(30, 300, "хто виконує", size=12, bold=True, anchor="start"))
    p.append(text(30, 470, ["що додали", "в інтерфейс"], size=12, bold=True, anchor="start")) if False else p.append(mtext(30, 490, ["що додали", "в інтерфейс"], size=12, bold=True, anchor="start"))

    p.append(text(W / 2, 645,
                  "Інтерфейс міняли не тому, що він застарів, а тому, що з'являвся новий виконавець.",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'executors-timeline.svg'), W, H, *p,
           title="Кожне переписування — відповідь на новий клас виконавця")


if __name__ == '__main__':
    fig_registry_lookup()
    fig_name_grammar()
    fig_tfm_and_request()
    fig_aead_buffer()
    fig_executors_timeline()
    print("ok")
