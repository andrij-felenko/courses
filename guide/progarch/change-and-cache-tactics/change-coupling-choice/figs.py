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


def fig_release_coupling_spectrum():
    """Спектр зчеплення релізів при змінах системи — від синхронного REST/gRPC
    до асинхронного Outbox та подійного логу."""
    W, H = 1040, 390
    f = []

    # Заголовок блоку
    f.append(fitbox(320, 35, 400, 38, "Спектр зчеплення релізів при змінах",
                    size=16, bold=True, fill=NEUT, stroke=INK))

    # Спектральна стрілка-ось
    f.append(line(80, 130, 960, 130, color=MUTED, sw=3))
    f.append(arrow(80, 130, 960, 130, color=INK, sw=3))
    f.append(text(80, 110, "Максимальне зчеплення (Lockstep)", size=12, color=NEG, anchor="start", bold=True))
    f.append(text(960, 110, "Максимальна автономія (Decoupled)", size=12, color=POS, anchor="end", bold=True))

    # Три позиції на спектрі
    # 1. REST / gRPC
    f.append(circle(180, 130, 10, fill=AMBER, stroke=INK, sw=2))
    f.append(fitbox(70, 160, 240, 180,
                    "Синхронний REST / gRPC\n\n• Часове зчеплення (1:1)\n• Негайне викликове залежність\n• Expand-Contract обов'язковий\n• Ризик каскадного lockstep",
                    size=13, fill=AMBER_T, stroke=AMBER))

    # 2. Pub/Sub Broker
    f.append(circle(520, 130, 10, fill=INK, stroke=INK, sw=2))
    f.append(fitbox(400, 160, 240, 180,
                    "Асинхронний Pub/Sub\n\n• Часова розв'язка\n• Буферизація в черзі\n• Незалежна швидкість читача\n• Лаг узгодженості (Eventual)",
                    size=13, fill=BLUE_T, stroke=INK))

    # 3. Transactional Outbox + Event Log
    f.append(circle(850, 130, 10, fill=POS, stroke=INK, sw=2))
    f.append(fitbox(730, 160, 240, 180,
                    "Outbox + Event Log\n\n• Повна релізна автономія\n• Транзакційний подвійний запис\n• Replay та DLQ ізоляція\n• Нульовий вплив при відкаті",
                    size=13, fill=GREEN_T, stroke=POS))

    render(os.path.join(OUT, 'release-coupling-spectrum.svg'), W, H, *f,
           title="Спектр зчеплення релізів при змінах системи")


def fig_lockstep_vs_independent():
    """Порівняння: синхронний каскад lockstep при деплої проти асинхронного буфера."""
    W, H = 1040, 420
    f = []

    # Лівий панель — Синхронний каскад (Lockstep)
    f.append(fitbox(40, 35, 450, 360, "", fill=BG, stroke=NEG, sw=1.5, dash="6 4"))
    f.append(fitbox(60, 50, 410, 32, "Синхронний REST/gRPC: Lockstep релізів",
                    size=14, bold=True, fill=RED_T, color=NEG, stroke=NEG))

    f.append(fitbox(80, 105, 160, 65, "Сервіс А (v2)\nВикачує нове поле", size=13, fill=NEUT, stroke=INK))
    f.append(fitbox(290, 105, 160, 65, "Сервіс Б (v1)\nСтарий контракт", size=13, fill=AMBER_T, stroke=AMBER))
    f.append(arrow(240, 137, 290, 137, color=NEG, sw=2))
    f.append(text(265, 125, "HTTP POST", size=11, color=NEG, anchor="middle"))

    f.append(fitbox(80, 210, 370, 70, "❌ ПОМИЛКА 400 Bad Request / Invalid Schema\nСервіс Б не знає нового поля або чекає іншого.\nВимагає одночасного (lockstep) деплою Б v2!",
                    size=12, fill=RED_T, stroke=NEG))

    f.append(fitbox(80, 305, 370, 65, "Наслідок: Сервіс А не можна викотити самостійно.\nЗрив незалежності релізів команд.",
                    size=12, fill=BG, color=MUTED, stroke="#d0d7de"))

    # Правий панель — Асинхронний буфер
    f.append(fitbox(550, 35, 450, 360, "", fill=BG, stroke=POS, sw=1.5))
    f.append(fitbox(570, 50, 410, 32, "Асинхронні Події: Незалежні релізи",
                    size=14, bold=True, fill=GREEN_T, color=POS, stroke=POS))

    f.append(fitbox(580, 105, 130, 65, "Сервіс А (v2)\nОпублікував\nEvent v2", size=13, fill=GREEN_T, stroke=POS))
    f.append(fitbox(730, 115, 90, 45, "Outbox /\nQueue", size=12, fill=BLUE_T, stroke=INK))
    f.append(fitbox(840, 105, 140, 65, "Сервіс Б (v1)\nЧитає застаріле\nабо чекає v2", size=13, fill=NEUT, stroke=INK))

    f.append(arrow(710, 137, 730, 137, color=POS, sw=2))
    f.append(arrow(820, 137, 840, 137, color=INK, sw=2))

    f.append(fitbox(580, 210, 400, 70, "✅ ПОДІЯ ЗБЕРЕЖЕНА В БУФЕРІ\nСервіс Б v1 може ігнорувати нове поле (Tolerant Reader)\nабо накопичувати події в черзі до свого релізу.",
                    size=12, fill=GREEN_T, stroke=POS))

    f.append(fitbox(580, 305, 400, 65, "Наслідок: Сервіс А релізиться в будь-який час.\nСервіс Б оновлюється за власним розкладом.",
                    size=12, fill=BG, color=POS, stroke=POS))

    render(os.path.join(OUT, 'lockstep-vs-independent.svg'), W, H, *f,
           title="Синхронний каскад проти асинхронного буфера при деплої")


def fig_schema_evolution_coupling():
    """Еволюція схеми під час відкату: синхронний збій проти подійного відновлення."""
    W, H = 980, 380
    f = []

    f.append(fitbox(290, 30, 400, 36, "Поведінка системи при відкаті (Rollback)",
                    size=15, bold=True, fill=NEUT, stroke=INK))

    # Верхній блок — REST Rollback
    f.append(fitbox(50, 85, 880, 120, "", fill=RED_T, stroke=NEG))
    f.append(fitbox(70, 95, 480, 25, "Синхронний REST / gRPC при відкаті Сервісу Б з v2 на v1:", size=13, bold=True, color=NEG, fill=BG, anchor="start"))
    f.append(fitbox(70, 125, 250, 65, "1. Сервіс Б відкочено до v1\nчерез виявлений баг", size=12, fill=BG, stroke=NEG))
    f.append(arrow(320, 157, 365, 157, color=NEG, sw=2))
    f.append(fitbox(365, 125, 260, 65, "2. Запити від Сервісу А (v2)\nнегайно відхиляються (500/400)", size=12, fill=BG, stroke=NEG))
    f.append(arrow(625, 157, 670, 157, color=NEG, sw=2))
    f.append(fitbox(670, 125, 240, 65, "3. Аварійний відкат Сервісу А\nабо вимикання фіч-прапорця", size=12, fill=BG, stroke=NEG))

    # Нижній блок — Event Rollback
    f.append(fitbox(50, 225, 880, 130, "", fill=GREEN_T, stroke=POS))
    f.append(fitbox(70, 235, 480, 25, "Асинхронний Pub/Sub / Outbox при відкаті Сервісу Б з v2 на v1:", size=13, bold=True, color=POS, fill=BG, anchor="start"))
    f.append(fitbox(70, 265, 250, 75, "1. Сервіс Б відкочено до v1;\nСпоживач переводиться на DLQ\nабо зупиняє зсув (offset)", size=12, fill=BG, stroke=POS))
    f.append(arrow(320, 302, 365, 302, color=POS, sw=2))
    f.append(fitbox(365, 265, 260, 75, "2. Сервіс А (v2) працює беззупинно,\nпродовжуючи писати в Outbox/Log", size=12, fill=BG, stroke=POS))
    f.append(arrow(625, 302, 670, 302, color=POS, sw=2))
    f.append(fitbox(670, 265, 240, 75, "3. Після фиксу Б v2.1,\nподії вичитуються з черги.\nНуль втрачених даних!", size=12, fill=BG, stroke=POS))

    render(os.path.join(OUT, 'schema-evolution-coupling.svg'), W, H, *f,
           title="Поведінка системи при відкаті: REST проти подій")


if __name__ == '__main__':
    fig_release_coupling_spectrum()
    fig_lockstep_vs_independent()
    fig_schema_evolution_coupling()
    print("All figures generated successfully.")
