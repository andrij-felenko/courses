# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_stream_to_tokens():
    """Плаский потік символів ріжеться на потік токенів-ярликів."""
    W, H = 820, 360
    f = []

    f.append(text(W / 2, 34, 'Суцільний текст: потік символів', size=15, bold=True))

    src = "if(x>=10)"
    cw = 44
    x0 = (W - len(src) * cw) / 2
    y_row = 56
    ch_h = 42
    for i, ch in enumerate(src):
        x = x0 + i * cw
        f.append(rect(x, y_row, cw, ch_h, fill='#eef2ff', stroke='#b9c2e8', rx=3))
        f.append(text(x + cw / 2, y_row + ch_h / 2 + 6, ch, size=19, color='#1a1a1a'))
    # monospace hint via family override is not exposed; default font is fine and readable

    f.append(text(W / 2, y_row + ch_h + 30,
                  'лексер читає зліва направо, «відкушуючи» найдовший осмислений шматок',
                  size=12.5, color=MUTED))

    ax = W / 2
    f.append(arrow(ax, 158, ax, 196, sw=2))

    f.append(text(W / 2, 222, 'Потік токенів: осмислені «слова» з ярликами', size=15, bold=True))

    tokens = [
        ('KEYWORD', 'if', '#dcfce7', '#86c9a0'),
        ('LPAREN', '(', '#e5e7eb', '#b0b4bd'),
        ('IDENT', 'x', '#fde9d0', '#e2b57e'),
        ('OP', '>=', '#e0e7ff', '#a6b1e6'),
        ('NUMBER', '10', '#fce7f3', '#e0a6c8'),
        ('RPAREN', ')', '#e5e7eb', '#b0b4bd'),
    ]
    tw = 122
    gap = 10
    total = len(tokens) * tw + (len(tokens) - 1) * gap
    tx0 = (W - total) / 2
    ty = 250
    th = 64
    for i, (kind, val, fill, stroke) in enumerate(tokens):
        x = tx0 + i * (tw + gap)
        f.append(rect(x, ty, tw, th, fill=fill, stroke=stroke, sw=1.5, rx=6))
        f.append(text(x + tw / 2, ty + 24, kind, size=12, color='#333', bold=True))
        f.append(text(x + tw / 2, ty + 50, val, size=18, color='#1a1a1a'))

    render(os.path.join(OUT, 'stream-to-tokens.svg'), W, H, *f)


def fig_maximal_munch():
    """Найдовше збігання: докуди відкушувати ('>' vs '>=')."""
    W, H = 760, 340
    f = []

    f.append(text(W / 2, 32, 'Найдовше збігання: докуди «відкушувати»?', size=15, bold=True))

    src = ">=10;"
    cw = 48
    x0 = 70
    y_row = 56
    ch_h = 44
    for i, ch in enumerate(src):
        x = x0 + i * cw
        f.append(rect(x, y_row, cw, ch_h, fill='#eef2ff', stroke='#b9c2e8', rx=3))
        f.append(text(x + cw / 2, y_row + ch_h / 2 + 6, ch, size=19, color='#1a1a1a'))

    yb = y_row + ch_h + 16
    # ">" alone — a valid token, but keep going
    f.append(line(x0 + 4, yb, x0 + cw - 4, yb, color='#c98a2b', sw=2))
    f.append(text(x0 + cw / 2, yb + 20, '> вже токен…', size=11.5, color='#c98a2b'))
    # ">=" longer and also valid -> win
    yb2 = yb + 34
    f.append(line(x0 + 4, yb2, x0 + 2 * cw - 4, yb2, color=FIELD, sw=3))
    f.append(text(x0 + cw, yb2 + 20, '…але >= довше → беремо >=', size=12, color=FIELD, bold=True))

    # rule box, well clear of the input row (right side)
    body, bw, bh = textbox(560, 150, size=12.5, pad=13,
                           fill='#fff8ec', stroke='#e0b877',
                           s='Правило (жадібне):\nз кожної позиції бери\nНАЙДОВШИЙ префікс,\nщо ще лишається токеном.\nСтоп, коли наступний\nсимвол уже не влазить.')
    f.append(body)

    # bottom gotcha, full-width its own box
    body2, bw2, bh2 = textbox(W / 2, 292, size=12.5, pad=11,
                              fill='#fdecec', stroke='#e0a0a0',
                              s='Пастка C:  a---b  жадібно ріжеться як  (a--) - b , а не  a - (--b).')
    f.append(body2)

    render(os.path.join(OUT, 'maximal-munch.svg'), W, H, *f)


def fig_lex_lineage():
    """Родовід генераторів лексерів: FORTRAN → Lex → Software Tools → flex."""
    W, H = 900, 430
    f = []

    f.append(text(W / 2, 30, 'Родовід генераторів лексерів', size=16, bold=True))

    # дві колонки подій; кожна подія — рамка з роком і суттю
    events = [
        # (cx, cy, рік, рядки, fill, stroke)
        (170, 96, '1957', 'FORTRAN\nкоманда Бекуса, IBM\nсканування — окрема фаза',
         '#eef2ff', '#b9c2e8'),
        (170, 250, '1975', 'Lex\nЛеск і Шмідт, Bell Labs\nкомпаньйон до Yacc',
         '#dcfce7', '#86c9a0'),
        (600, 250, '1982', 'Software Tools lex\nПоскенцер, потім Пексон\nмовою Ratfor',
         '#fdecec', '#e0a0a0'),
        (600, 96, '1987', 'flex — Fast Lexical\nanalyzer generator\nПексон, LBL, чистий C',
         '#fce7f3', '#e0a6c8'),
    ]
    box_w, box_h = 280, 96
    for cx, cy, yr, body, fill, stroke in events:
        x, y = cx - box_w / 2, cy - box_h / 2
        f.append(rect(x, y, box_w, box_h, fill=fill, stroke=stroke, sw=1.6, rx=8))
        f.append(text(cx, y + 24, yr, size=17, color='#333', bold=True))
        f.append(mtext(cx, y + 44, body, size=12, color='#1a1a1a'))

    # стрілки родоводу
    f.append(arrow(170, 144, 170, 202, sw=2))                       # FORTRAN → Lex (ідея фази)
    f.append(text(190, 176, 'фаза → інструмент', size=11,
                  color=MUTED, anchor='start'))
    f.append(arrow(310, 250, 460, 250, sw=2))                       # Lex → Software Tools (незалежна лінія)
    f.append(text(385, 236, 'сумісний вхід,\nбез спільного коду', size=10.5,
                  color=MUTED))
    f.append(arrow(600, 202, 600, 144, sw=2))                       # Software Tools → flex (переклад у C)
    f.append(text(620, 176, 'Ratfor → C', size=11,
                  color=MUTED, anchor='start'))

    # підсумковий рядок
    body, bw, bh = textbox(W / 2, 392, size=12.5, pad=12,
                           fill='#fff8ec', stroke='#e0b877',
                           s='Lex і flex не ділять жодного рядка коду:\n'
                             'flex читає ті самі вхідні файли, але написаний з нуля й швидший.')
    f.append(body)

    render(os.path.join(OUT, 'lex-lineage.svg'), W, H, *f)


if __name__ == '__main__':
    fig_stream_to_tokens()
    fig_maximal_munch()
    fig_lex_lineage()
    print('ok')
