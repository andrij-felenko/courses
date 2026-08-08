# -*- coding: utf-8 -*-
"""Фігури до теми «Дайджест-автентифікація»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

SOFT = "#eef3fb"
WARM = "#fdf3e6"
PAPER = "#ffffff"


def box(cx, cy, s, size=13, fill=FILL, bold=False, stroke=LINE):
    body, w, h = textbox(cx, cy, s, size=size, fill=fill, bold=bold, stroke=stroke)
    return body, w / 2.0, h / 2.0


# ─────────────────────────────────────────────────────────────────────────────
# 1. Два оберти: порожній запит → виклик 401 → той самий запит із доказом → 200.
# ─────────────────────────────────────────────────────────────────────────────
def fig_challenge_flow():
    W, H = 1180, 700
    f = []
    xc, xs = 130, 1010
    top, bot = 96, 660

    for x, name in ((xc, "Клієнт"), (xs, "Сервер")):
        b, _, _ = box(x, 58, name, size=13, bold=True)
        f.append(b)
        f.append(line(x, top - 14, x, bot, color=MUTED, sw=1.2, dash="5,5"))

    def msg(y, x1, x2, label, color=INK):
        f.append(arrow(x1, y, x2, y, color=color))
        f.append(text((x1 + x2) / 2.0, y - 11, label, size=12, color=color))

    msg(128, xc, xs, "GET /api/v1/measurements — без жодних облікових даних")
    msg(184, xs, xc, "401 Unauthorized — «спершу доведи»", color=POS)

    ch, _, _ = box(570, 280,
                   'WWW-Authenticate: Digest\n'
                   'realm="api.example.org", qop="auth", algorithm=SHA-256\n'
                   'nonce="SG9wZUZvclNwcmluZzE3NTQ2MDA", opaque="a7c2"',
                   size=11, fill=WARM, stroke="#e6d3b3")
    f.append(ch)
    f.append(text(570, 350, "виклик: одноразове число та правила гри",
                  size=11, color=MUTED))

    msg(420, xc, xs, "GET /api/v1/measurements — той самий запит, тепер із доказом")

    au, _, _ = box(570, 540,
                   'Authorization: Digest username="olena", realm="api.example.org",\n'
                   'uri="/api/v1/measurements", nonce="SG9wZUZvclNwcmluZzE3NTQ2MDA",\n'
                   'nc=00000001, cnonce="0a4f113b7f0b1c2d", qop=auth, opaque="a7c2",\n'
                   'response="48e9d37f4495058ee48036d0586bfbe3d1b1bbf6ba6021f8d7713674b54d5d7f"',
                   size=11, fill=SOFT, stroke="#c8d6ea")
    f.append(au)

    msg(636, xs, xc, "200 OK", color=FIELD)

    f.append(text(70, 690,
                  "Пароля немає в жодному з цих чотирьох повідомлень — "
                  "у мережу їде тільки геш, дійсний рівно для цього виклику",
                  size=12, color=FIELD, anchor="start"))

    render(os.path.join(OUT, 'challenge-flow.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Кожен складник доказу закриває свою дірку.
# ─────────────────────────────────────────────────────────────────────────────
def fig_ingredients():
    W, H = 1240, 760
    f = []

    head, _, _ = box(620, 66,
                     "response = H( H(A1) : nonce : nc : cnonce : qop : H(A2) )",
                     size=15, fill=WARM, stroke="#e6d3b3", bold=True)
    f.append(head)
    f.append(text(620, 132, "Шість складників — шість різних загроз",
                  size=12, color=MUTED))

    rows = [
        ("H(A1) = H(ім'я : realm : пароль)",
         "Сервер тримає не пароль, а цей геш;\nrealm розводить один пароль\nна різні служби"),
        ("nonce — число від сервера",
         "Доказ живе рівно один виклик:\nпідслухане завтра вже мертве"),
        ("cnonce — число від клієнта",
         "Сервер не підсуне виклик,\nпід який має готову таблицю\nвідповідей"),
        ("nc — лічильник запитів",
         "Та сама відповідь удруге\nвидає повтор одразу"),
        ("qop — рівень захисту",
         "Всередині геша, тож посередник\nне зіб'є його на слабший"),
        ("H(A2) = H(метод : URI)",
         "Доказ прив'язаний до дії:\nперехоплений GET не стане\nDELETE над іншим ресурсом"),
    ]

    y = 210
    for left, right in rows:
        lb, lw, lh = box(300, y, left, size=12, fill=SOFT, stroke="#c8d6ea")
        rb, rw, rh = box(890, y, right, size=11, fill=PAPER)
        f += [lb, rb]
        f.append(arrow(300 + lw + 6, y, 890 - rw - 6, y, color=MUTED))
        y += 100

    render(os.path.join(OUT, 'response-ingredients.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Межа захисту: що схема закриває і що лишається відкритим.
# ─────────────────────────────────────────────────────────────────────────────
def fig_boundary():
    W, H = 1240, 700
    f = []

    f.append(rect(50, 46, 1140, 190, fill=SOFT, stroke="#c8d6ea", sw=1.2, rx=10))
    cl, clw, _ = box(180, 142, "Клієнт", size=13, bold=True)
    sv, svw, _ = box(1060, 142, "Сервер", size=13, bold=True)
    f += [cl, sv]
    f.append(arrow(180 + clw, 142, 1060 - svw, 142))
    f.append(text(620, 92, "Заголовок із доказом — захищено", size=12, color=FIELD))
    f.append(text(620, 186,
                  "Метод, шлях, заголовки, тіло запиту й уся відповідь — відкритим текстом",
                  size=12, color=POS))

    cols = [
        (250, "Хто слухає канал",
         "Бачить nonce і response.\nПовторити не може — але може\nвдома перебирати паролі\nмільярдами за секунду,\nдоки не збіжиться геш."),
        (620, "Хто вкрав файл сервера",
         "У файлі лежить H(A1) —\nцього досить, щоб увійти.\nПовільний солений геш сюди\nне вставити: формула вимагає\nрівно H(A1) з обох боків."),
        (990, "Хто сидить посередині",
         "Підміняє виклик Digest\nна Basic — і браузер віддає\nпароль відкрито.\nСхема цього не бачить,\nрятує лише впертість клієнта."),
    ]

    for x, title, body in cols:
        f.append(arrow(x, 240, x, 300, color=MUTED))
        tb, _, th = box(x, 340, title, size=13, fill=WARM, stroke="#e6d3b3", bold=True)
        bb, _, _ = box(x, 470, body, size=11, fill=PAPER)
        f += [tb, bb]

    f.append(text(620, 636,
                  "Схема боронить передавання секрету, а не сам секрет:",
                  size=13, color=INK))
    f.append(text(620, 664,
                  "слабкий пароль лишається слабким, а сховище сервера — беззахисним",
                  size=13, color=INK))

    render(os.path.join(OUT, 'protection-boundary.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Що кожен бік мусить пам'ятати між запитами (до вставки з кодом).
# ─────────────────────────────────────────────────────────────────────────────
def fig_state_kept():
    W, H = 1180, 620
    f = []
    f.append(text(W / 2.0, 40, "Стан, який кожен бік тримає між запитами",
                  size=17, bold=True))

    panels = (
        (300, "Клієнт", (
            "лічильник nc на КОЖЕН виклик окремо —\n"
            "скільки запитів уже пішло з цим nonce\n"
            "\n"
            "для -sess: ключ сеансу і той самий cnonce,\n"
            "поки живе виклик\n"
            "\n"
            "сам виклик — щоб наступного разу\n"
            "не марнувати зайвий оберт на 401")),
        (880, "Сервер", (
            "секрет підпису — один на всі машини;\n"
            "виклик перевіряє сам себе, таблиці немає\n"
            "\n"
            "H(A1) ОКРЕМО на кожен алгоритм:\n"
            "інший геш — інше значення у сховищі\n"
            "\n"
            "найбільший прийнятий nc на кожен виклик")),
    )

    for x, name, body in panels:
        hb, _, _ = box(x, 96, name, size=14, fill=WARM, stroke="#e6d3b3", bold=True)
        bb, _, _ = box(x, 270, body, size=12, fill=PAPER)
        f += [hb, bb]
        f.append(arrow(x, 128, x, 172, color=MUTED))

    f.append(line(590, 80, 590, 400, color=MUTED, sw=1.2, dash="5,5"))

    note, _, _ = box(W / 2.0, 500, (
        "Самоперевірний виклик прибирає таблицю виданих чисел — але не звірку nc.\n"
        "Захист від повтору без пам'яті не буває: забудьте вжиті номери —\n"
        "і перехоплений запит пройде вдруге, хоч би яким свіжим був виклик."),
        size=13, fill=SOFT, stroke="#c7d5ea")
    f.append(note)

    render(os.path.join(OUT, 'state-kept.svg'), W, H, *f)


if __name__ == '__main__':
    fig_challenge_flow()
    fig_ingredients()
    fig_boundary()
    fig_state_kept()
    print("ok")
