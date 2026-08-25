# -*- coding: utf-8 -*-
"""Фігура до теми «Landlock LSM: безпривілейоване обмеження файлового доступу»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

def fig_landlock_arch():
    W, H = 1000, 480
    f = []

    # Фонова область
    f.append(rect(20, 20, 960, 440, fill="#fafafa", stroke="#e0e0e0", rx=8))

    # Зона Користувацького простору (Userspace)
    f.append(rect(40, 60, 420, 380, fill="#f0f7ff", stroke=NEG, sw=1.5, rx=6))
    f.append(text(250, 90, "Користувацький простір (Userspace)", size=16, color=NEG, bold=True))

    # Блок процесу
    b1, _, _ = textbox(250, 145, "Процес додатка\n(Unprivileged Process)", size=14, fill="#ffffff", stroke=NEG, min_w=340)
    f.append(b1)

    # Кроки налаштування
    b2, _, _ = textbox(250, 235, "1. prctl(PR_SET_NO_NEW_PRIVS, 1)\n2. landlock_create_ruleset()\n3. landlock_add_rule(parent_fd, ...)", size=13, fill="#ffffff", stroke=LINE, min_w=360)
    f.append(b2)

    b3, _, _ = textbox(250, 340, "4. landlock_restrict_self(ruleset_fd)", size=13, fill="#eefbe7", stroke=FIELD, bold=True, min_w=360)
    f.append(b3)

    f.append(arrow(250, 175, 250, 195, color=LINE))
    f.append(arrow(250, 280, 250, 305, color=FIELD))

    # Зона Ядра (Kernel Space)
    f.append(rect(500, 60, 460, 380, fill="#fdf7f7", stroke=POS, sw=1.5, rx=6))
    f.append(text(730, 90, "Ядро Linux (Kernel / LSM)", size=16, color=POS, bold=True))

    # Кредити процесу та шари Landlock
    b4, _, _ = textbox(730, 155, "current->cred->security\n(Landlock Domain / Stacked Layers)", size=13, fill="#ffffff", stroke=POS, min_w=380)
    f.append(b4)

    # LSM VFS Hooks
    b5, _, _ = textbox(730, 250, "LSM Hooks (security_file_open)\nПеревірка доступів до inode / dentry", size=13, fill="#ffffff", stroke=LINE, min_w=380)
    f.append(b5)

    # Результати доступу
    b6, _, _ = textbox(630, 365, "Дозволений шлях\n(R_OK / X_OK)", size=12, fill="#eefbe7", stroke=FIELD, min_w=170)
    f.append(b6)

    b7, _, _ = textbox(830, 365, "Заборонений шлях\n-EACCES (Permission denied)", size=12, fill="#fdecea", stroke=POS, min_w=190)
    f.append(b7)

    # Зв'язки між процесом, ядром та LSM
    f.append(arrow(430, 340, 520, 160, color=FIELD, sw=2))
    f.append(text(485, 230, "замикання", size=12, color=FIELD, bold=True))

    f.append(arrow(730, 195, 730, 215, color=LINE))
    f.append(arrow(680, 290, 640, 335, color=FIELD))
    f.append(arrow(780, 290, 820, 335, color=POS))

    render(os.path.join(OUT, 'landlock-arch.svg'), W, H, *f, title="Загальна архітектура застосування Landlock LSM")

if __name__ == "__main__":
    fig_landlock_arch()
