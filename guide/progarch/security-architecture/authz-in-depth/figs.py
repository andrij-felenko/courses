# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

AMBER   = "#e08a1e"
RED_T   = "#fdecea"
AMBER_T = "#fdf0dd"
GREEN_T = "#e7f6ec"
BLUE_T  = "#eaf0fd"
NEUT    = "#eef2f6"


def fig_authz_models_evolution():
    """Еволюція моделей авторизації: RBAC (ролі) -> ABAC (атрибути та правила) -> ReBAC (реляційні графи)."""
    W, H = 1040, 420
    f = []

    # Title / Header areas
    f.append(fitbox(30, 25, 300, 34, "RBAC: Рольовий доступ", size=14, bold=True, fill=NEUT, stroke=INK))
    f.append(fitbox(370, 25, 300, 34, "ABAC: Доступ за атрибутами", size=14, bold=True, fill=NEUT, stroke=INK))
    f.append(fitbox(710, 25, 300, 34, "ReBAC: Граф стосунків", size=14, bold=True, fill=NEUT, stroke=INK))

    # --- Col 1: RBAC ---
    f.append(fitbox(30, 75, 300, 255, "", size=12, fill=BG, stroke="#c8ced6"))
    f.append(fitbox(45, 90, 110, 42, "Користувач\n(alice)", size=12, fill=BLUE_T, stroke=NEG))
    f.append(arrow(155, 111, 185, 111))
    f.append(fitbox(185, 90, 130, 42, "Роль\n(HomeOwner)", size=12, bold=True, fill=AMBER_T, stroke=AMBER))
    f.append(arrow(250, 132, 250, 165))
    f.append(fitbox(185, 165, 130, 42, "Право\n(camera:view)", size=12, fill=GREEN_T, stroke=FIELD))
    
    # Limitation box
    f.append(fitbox(45, 230, 270, 85, "Проблема: вибух ролей!\nGuest_Room1_Night,\nInstaller_TempAccess...\nНемає контексту об'єкта.", size=12, fill=RED_T, stroke=POS, color="#a00000"))

    # --- Col 2: ABAC ---
    f.append(fitbox(370, 75, 300, 255, "", size=12, fill=BG, stroke="#c8ced6"))
    f.append(fitbox(385, 90, 270, 65, "Вхідні атрибути:\n• Subj: role=guest, room=1\n• Res: camera=cam-704, room=1\n• Env: time=21:00", size=11, fill=BLUE_T, stroke=NEG))
    f.append(arrow(520, 155, 520, 180))
    f.append(fitbox(420, 180, 200, 45, "Рушій політик (OPA/Cedar)\nif S.room == R.room & E.time < 22:00", size=11, bold=True, fill=AMBER_T, stroke=AMBER))
    f.append(arrow(520, 225, 520, 250))
    f.append(fitbox(450, 250, 140, 34, "ALLOW / DENY", size=12, bold=True, fill=GREEN_T, stroke=FIELD))

    # Limitation note below col 2
    f.append(fitbox(385, 295, 270, 25, "Пастка: витягування атрибутів (PIP)", size=11, color=MUTED, fill=BG, stroke=MUTED))

    # --- Col 3: ReBAC ---
    f.append(fitbox(710, 75, 300, 255, "", size=12, fill=BG, stroke="#c8ced6"))
    f.append(fitbox(725, 90, 270, 95, "Кортежі стосунків:\n• home:101#owner@user:alice\n• cam:704#parent@home:101\n• cam:704#viewer@home:101#owner", size=11, fill=GREEN_T, stroke=FIELD))
    f.append(arrow(860, 185, 860, 210))
    f.append(fitbox(745, 210, 230, 45, "Обхід графа стосунків:\nuser:alice є в розгортанні viewer?", size=11, bold=True, fill=BLUE_T, stroke=NEG))
    f.append(arrow(860, 255, 860, 275))
    f.append(fitbox(790, 275, 140, 34, "ALLOW (є шлях)", size=12, bold=True, fill=GREEN_T, stroke=FIELD))

    # Bottom summary row
    f.append(fitbox(30, 350, 980, 50, "Резюме: RBAC розпадається під складністю домену; ABAC дає гнучкість ціною вибірок; ReBAC зводить перевірку до графа.", size=12, bold=True, fill=NEUT, stroke=INK))

    render(os.path.join(OUT, 'authz-models-evolution.svg'), W, H, *f,
           title="Еволюція моделей авторизації: RBAC, ABAC та ReBAC")


def fig_pep_pdp_pip_architecture():
    """Анатомія авторизаційної інфраструктури: PEP, PDP, PIP, PAP."""
    W, H = 1000, 440
    f = []

    # Client / External
    f.append(fitbox(40, 170, 140, 60, "Клієнт\n(Запит до API)", size=13, bold=True, fill=NEUT, stroke=INK))
    f.append(arrow(180, 200, 250, 200))
    f.append(text(215, 190, "1. HTTP/RPC", size=11, color=MUTED, anchor="middle"))

    # PEP Box
    f.append(fitbox(250, 140, 180, 120, "PEP\n(Policy Enforcement Point)\n\nШлюз / Мідлвер", size=13, bold=True, fill=BLUE_T, stroke=NEG))

    # Service execution path arrow
    f.append(arrow(430, 200, 800, 200, color=FIELD, sw=2.5))
    f.append(text(615, 188, "4. Якщо ALLOW -> Виконання сервісу", size=11, bold=True, color=FIELD, anchor="middle"))

    # Arrow to PDP
    f.append(arrow(340, 260, 340, 320))
    f.append(text(275, 290, "2. Check(S, A, R)", size=11, color=MUTED, anchor="middle"))
    f.append(arrow(380, 320, 380, 260, color=FIELD))
    f.append(text(440, 290, "3. Allow / Deny", size=11, color=FIELD, anchor="middle"))

    # PDP Box
    f.append(fitbox(260, 320, 240, 90, "PDP\n(Policy Decision Point)\nРушій перевірки політик / графа", size=13, bold=True, fill=AMBER_T, stroke=AMBER))

    # PIP Box
    f.append(fitbox(640, 320, 240, 90, "PIP\n(Policy Information Point)\nБаза даних / Джерело атрибутів", size=13, bold=True, fill=GREEN_T, stroke=FIELD))
    f.append(arrow(500, 365, 640, 365))
    f.append(text(570, 350, "Запит стосунків /", size=11, color=MUTED, anchor="middle"))
    f.append(text(570, 380, "атрибутів", size=11, color=MUTED, anchor="middle"))

    # PAP Box (top)
    f.append(fitbox(520, 40, 240, 80, "PAP\n(Policy Administration Point)\nЗбереження політик та кортежів", size=13, bold=True, fill=NEUT, stroke="#708090"))
    f.append(line(550, 120, 430, 320, color=MUTED, sw=1.5, dash="5 5"))
    f.append(text(530, 210, "Публікація політик", size=11, color=MUTED, anchor="middle"))

    # Output to Client
    f.append(fitbox(800, 170, 160, 60, "Захищений\nРесурс / Сервіс", size=13, bold=True, fill=GREEN_T, stroke=FIELD))

    render(os.path.join(OUT, 'pep-pdp-pip-architecture.svg'), W, H, *f,
           title="Анатомія авторизації: взаємодія PEP, PDP, PIP та PAP")


def fig_authz_topologies_comparison():
    """Три топології розподіленої авторизації: децентралізована, централізована та гібридна."""
    W, H = 1040, 450
    f = []

    # --- Topo A ---
    f.append(fitbox(30, 35, 300, 34, "А. Децентралізована", size=14, bold=True, fill=NEUT, stroke=INK))
    f.append(fitbox(30, 80, 300, 320, "", size=12, fill=BG, stroke="#c8ced6"))

    f.append(fitbox(55, 100, 250, 75, "Сервіс А\n[Вбудована бібліотека PDP]\nЛокальні правила в DB A", size=11, fill=BLUE_T, stroke=NEG))
    f.append(fitbox(55, 200, 250, 75, "Сервіс Б\n[Вбудована бібліотека PDP]\nЛокальні правила в DB Б", size=11, fill=BLUE_T, stroke=NEG))

    f.append(fitbox(55, 300, 250, 80, "Плюси: 0 мс мережі, автономія.\nМінуси: дублювання коду,\nдрейф політик, важкий аудит.", size=11, fill=GREEN_T, stroke=FIELD))

    # --- Topo B ---
    f.append(fitbox(370, 35, 300, 34, "Б. Централізований PDP", size=14, bold=True, fill=NEUT, stroke=INK))
    f.append(fitbox(370, 80, 300, 320, "", size=12, fill=BG, stroke="#c8ced6"))

    f.append(fitbox(395, 100, 110, 60, "Сервіс А", size=11, fill=BLUE_T, stroke=NEG))
    f.append(fitbox(395, 180, 110, 60, "Сервіс Б", size=11, fill=BLUE_T, stroke=NEG))

    f.append(arrow(505, 130, 540, 150))
    f.append(arrow(505, 210, 540, 170))

    f.append(fitbox(540, 110, 115, 110, "Центральний\nPDP Сервіс\n(Zanzibar /\nOpenFGA)", size=11, bold=True, fill=AMBER_T, stroke=AMBER))

    f.append(fitbox(395, 300, 250, 80, "Плюси: єдина правда, аудит.\nМінуси: +хоп на кожен RPC,\nSPOF доступності всієї системи.", size=11, fill=AMBER_T, stroke=AMBER))

    # --- Topo C ---
    f.append(fitbox(710, 35, 300, 34, "В. Гібридна (Gateway + Sidecar)", size=14, bold=True, fill=NEUT, stroke=INK))
    f.append(fitbox(710, 80, 300, 320, "", size=12, fill=BG, stroke="#c8ced6"))

    f.append(fitbox(735, 95, 250, 45, "API Gateway (Coarse JWT / Roles)", size=11, fill=NEUT, stroke=INK))
    f.append(arrow(860, 140, 860, 165))

    f.append(fitbox(735, 165, 250, 110, "Мікросервіс з Sidecar PDP\n• Вбудований кєш / локальний граф\n• Асинхронна реплікація з PAP", size=11, fill=GREEN_T, stroke=FIELD))

    f.append(fitbox(735, 300, 250, 80, "Плюси: висока швидкість,\nавтономність сервісу + єдиний PAP.\nМінуси: складність реплікації.", size=11, fill=BLUE_T, stroke=NEG))

    render(os.path.join(OUT, 'authz-topologies-comparison.svg'), W, H, *f,
           title="Порівняння трьох топологій авторизації в мікросервісах")


if __name__ == '__main__':
    fig_authz_models_evolution()
    fig_pep_pdp_pip_architecture()
    fig_authz_topologies_comparison()
    print("All figures generated successfully.")
