# -*- coding: utf-8 -*-
"""Фігури до теми «DKMS: перезбирання й підписування позадеревних модулів»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

PKG  = "#eef4fb"   # пакетний менеджер і його тригер
BUILD = "#f2f7ef"  # автоматична частина DKMS
MOK  = "#fdf1ea"   # разова реєстрація ключа за межами ОС


def box(cx, cy, s, size=13, **kw):
    body, w, h = textbox(cx, cy, s, size=size, **kw)
    return body


# ── Тригер оновлення ядра, конвеєр DKMS і разова гілка MOK ──────────────────
def fig_dkms_workflow():
    W, H = 1080, 610
    f = []

    f.append(box(170, 70, "оновлення пакунків\n(новий linux-image)", fill=PKG))
    f.append(box(500, 70, "тригер після встановлення\n(hook пакетного менеджера)", fill=PKG))
    f.append(box(840, 70, "DKMS: AUTOINSTALL\nдля нової версії ядра", fill=PKG))
    f.append(arrow(255, 70, 389, 70, color=INK, sw=1.8))
    f.append(arrow(611, 70, 748, 70, color=INK, sw=1.8))

    f.append(box(840, 200, "збирання модуля: make\nу /usr/src/<пакет>-<версія>", fill=BUILD))
    f.append(box(840, 320, "підпис sign-file\nлокальним ключем MOK", fill=BUILD))
    f.append(box(840, 440, "встановлення .ko\nу /lib/modules/…/updates/dkms", fill=BUILD))
    f.append(arrow(840, 97, 840, 173, color=INK, sw=1.8))
    f.append(arrow(840, 227, 840, 293, color=INK, sw=1.8))
    f.append(arrow(840, 347, 840, 413, color=INK, sw=1.8))

    f.append(box(250, 320, "mokutil: запит на реєстрацію\nпублічного ключа", fill=MOK))
    f.append(box(250, 440, "перезавантаження →\nMokManager: Enroll MOK", fill=MOK))
    f.append(arrow(750, 320, 368, 320, color=POS, sw=1.8))
    f.append(text(559, 300, "лише перший раз: ключа ще нема в UEFI",
                  size=12, color=MUTED, italic=True))
    f.append(arrow(250, 347, 250, 413, color=POS, sw=1.8))

    f.append(box(545, 545, "ядро довіряє ключу: modprobe вантажить модуль\n"
                           "навіть із увімкненим Secure Boot", fill=BUILD))
    f.append(arrow(250, 467, 396, 517, color=INK, sw=1.8))
    f.append(arrow(840, 467, 694, 517, color=INK, sw=1.8))

    render(os.path.join(OUT, "dkms-workflow.svg"), W, H, *f,
           title="Оновлення ядра запускає перезбирання, а реєстрація MOK потрібна лише раз")


if __name__ == "__main__":
    fig_dkms_workflow()
    print("ok")
