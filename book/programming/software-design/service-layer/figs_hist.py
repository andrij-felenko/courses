# -*- coding: utf-8 -*-
# Фігури для історичної вставки hist-service-layer.md.
# Окремий файл, щоб не чіпати figs.py теми; пише у той самий ./img/ з іншими іменами.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_landscape():
    """Два стилі організації ділової логіки до 2002; сервісний шар — тонка межа над будь-яким."""
    W, H = 940, 470
    frags = []
    frags.append(text(W / 2, 34, "Два стилі організації ділової логіки — і тонка межа над кожним",
                      size=17, bold=True))

    # тонка смуга сервісного шару — тягнеться над обома стилями
    frags.append(rect(70, 78, W - 140, 66, fill="#fff7e6", stroke="#d68910", sw=2, rx=10))
    frags.append(text(W / 2, 104, "Сервісний шар — той самий перелік операцій над будь-яким стилем",
                      size=14, bold=True, color="#b9770e"))
    frags.append(text(W / 2, 127, "placeOrder() · cancelSubscription() · recognizeRevenue()",
                      size=12, color="#b9770e"))

    # дві стрілки вниз — до кожного стилю
    frags.append(arrow(300, 148, 260, 214, color=MUTED, sw=1.8))
    frags.append(arrow(640, 148, 690, 214, color=MUTED, sw=1.8))

    # ── ЛІВОРУЧ: Transaction Script ──
    frags.append(rect(90, 220, 320, 200, fill="#f4f6f8", stroke=LINE, sw=1.6, rx=10))
    frags.append(text(250, 248, "Транзакційний сценарій", size=14, bold=True))
    frags.append(text(250, 269, "(Transaction Script)", size=11, color=MUTED, italic=True))
    frags.append(text(250, 300, "одна процедура на операцію,", size=12))
    frags.append(text(250, 320, "лінійно згори вниз", size=12))
    frags.append(text(250, 352, "просто, доки правил мало;", size=11, color=MUTED))
    frags.append(text(250, 371, "плутається, коли правила", size=11, color=MUTED))
    frags.append(text(250, 390, "множаться й міняються", size=11, color=MUTED))

    # ── ПРАВОРУЧ: Domain Model ──
    frags.append(rect(530, 220, 320, 200, fill="#eafaf1", stroke=FIELD, sw=1.6, rx=10))
    frags.append(text(690, 248, "Модель домену", size=14, bold=True))
    frags.append(text(690, 269, "(Domain Model)", size=11, color=MUTED, italic=True))
    frags.append(text(690, 300, "мережа обʼєктів із поведінкою,", size=12))
    frags.append(text(690, 320, "правила поруч із даними", size=12))
    frags.append(text(690, 352, "тримає складні, мінливі", size=11, color=MUTED))
    frags.append(text(690, 371, "правила; дорожчий на старті,", size=11, color=MUTED))
    frags.append(text(690, 390, "окупається на обсязі", size=11, color=MUTED))

    render(os.path.join(IMG, "hist-landscape.svg"), W, H, *frags)


def fig_ejb_fork():
    """Розвилка епохи J2EE: сесійний бін проти POJO; порада Стаффорда — починай локально."""
    W, H = 900, 440
    frags = []
    frags.append(text(W / 2, 34, "Розвилка епохи J2EE: у чому втілити сервісний шар",
                      size=17, bold=True))

    # верх — сам шар
    svc, _, _ = textbox(W / 2, 90, "Сервісний шар: placeOrder(), …", size=13, bold=True,
                        min_w=380, fill="#fff7e6", stroke="#d68910")
    frags.append(svc)

    # дві гілки
    frags.append(arrow(W / 2 - 40, 116, 250, 168, color=MUTED, sw=1.8))
    frags.append(arrow(W / 2 + 40, 116, 650, 168, color=MUTED, sw=1.8))

    # ── ЛІВОРУЧ: session bean ──
    frags.append(rect(80, 176, 340, 190, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=10))
    frags.append(text(250, 204, "Сесійний бін (session bean)", size=13, bold=True, color=NEG))
    frags.append(text(250, 232, "транзакції веде контейнер", size=12))
    frags.append(text(250, 252, "можна кликати здалеку", size=12))
    frags.append(text(250, 284, "але: обʼєкти йдуть по мережі,", size=11, color=MUTED))
    frags.append(text(250, 303, "важче тестувати —", size=11, color=MUTED))
    frags.append(text(250, 322, "треба піднімати контейнер", size=11, color=MUTED))

    # ── ПРАВОРУЧ: POJO ──
    frags.append(rect(480, 176, 340, 190, fill="#f4f6f8", stroke=LINE, sw=1.6, rx=10))
    frags.append(text(650, 204, "Звичайний обʼєкт (POJO)", size=13, bold=True))
    frags.append(text(650, 232, "легко тестувати —", size=12))
    frags.append(text(650, 252, "без контейнера, в памʼяті", size=12))
    frags.append(text(650, 284, "але: складніше причепити", size=11, color=MUTED))
    frags.append(text(650, 303, "розподілені транзакції", size=11, color=MUTED))
    frags.append(text(650, 322, "контейнера", size=11, color=MUTED))

    # порада Стаффорда
    frags.append(text(W / 2, 400,
                      "Порада Стаффорда: починай із локального — віддаленість додаси, якщо колись знадобиться",
                      size=13, bold=True, color="#b9770e"))

    render(os.path.join(IMG, "hist-ejb-fork.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_landscape()
    fig_ejb_fork()
    print("ok")
