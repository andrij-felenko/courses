# -*- coding: utf-8 -*-
import os
import sys

# scripts/ directory is 4 levels up: book/programming/security/supply-chain-security -> ../../../..
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. supply-chain-attack-vectors: Вектори атак на всіх фазах ланцюга ─────────
def fig_supply_chain_attack_vectors():
    W, H = 880, 360
    p = []

    # 4 фази ланцюга
    phases = [
        ("1. Джерела та залежності", 115, "#eef2ff", NEG),
        ("2. Збирання та CI/CD", 335, "#fef3c7", "#b45309"),
        ("3. Реєстр і збереження", 555, "#f0fdf4", FIELD),
        ("4. Розгортання й запуск", 765, "#fdf2f8", "#be185d"),
    ]

    for title, cx, bg_col, stroke_col in phases:
        p.append(rect(cx - 95, 45, 190, 290, fill=bg_col, stroke=stroke_col, sw=1.5, rx=8))
        p.append(text(cx, 70, title, size=12, color=stroke_col, bold=True))

    # З'єднувальні стрілки між фазами
    p.append(arrow(210, 100, 240, 100, color=LINE, sw=2))
    p.append(arrow(430, 100, 460, 100, color=LINE, sw=2))
    p.append(arrow(650, 100, 680, 100, color=LINE, sw=2))

    # Елементи фази 1
    b1, _, _ = textbox(115, 100, "Вихідний код + Git\nСторонні пакунки", size=11, color=INK,
                       fill="#ffffff", stroke=NEG, sw=1.2, min_w=170)
    p.append(b1)
    # Загрози фази 1
    p.append(rect(30, 150, 170, 170, fill="#fff5f5", stroke=POS, sw=1.2, rx=6))
    p.append(text(115, 172, "Вектори загроз:", size=11, color=POS, bold=True))
    p.append(text(115, 196, "• Typosquatting у пакунках", size=10, color=INK))
    p.append(text(115, 218, "• Dependency Confusion", size=10, color=INK))
    p.append(text(115, 240, "• Злам акаунта автора", size=10, color=INK))
    p.append(text(115, 262, "• Прихований бекдор у Git", size=10, color=INK))
    p.append(text(115, 284, "• Нефіксовані версії", size=10, color=MUTED))
    p.append(text(115, 304, "(SolarWinds, Event-Stream)", size=9, color=POS, italic=True))

    # Елементи фази 2
    b2, _, _ = textbox(335, 100, "Конвеєр CI / Runner\nКомпілятор і лінкер", size=11, color=INK,
                       fill="#ffffff", stroke="#b45309", sw=1.2, min_w=170)
    p.append(b2)
    # Загрози фази 2
    p.append(rect(250, 150, 170, 170, fill="#fff5f5", stroke=POS, sw=1.2, rx=6))
    p.append(text(335, 172, "Вектори загроз:", size=11, color=POS, bold=True))
    p.append(text(335, 196, "• Злам середовища збирання", size=10, color=INK))
    p.append(text(335, 218, "• Ін'єкція в процеси білду", size=10, color=INK))
    p.append(text(335, 240, "• Викрадення секретів CI", size=10, color=INK))
    p.append(text(335, 262, "• Недетерміністичний білд", size=10, color=INK))
    p.append(text(335, 284, "• Отруєння кешу залежностей", size=10, color=MUTED))
    p.append(text(335, 304, "(Codecov, XZ Utils)", size=9, color=POS, italic=True))

    # Елементи фази 3
    b3, _, _ = textbox(555, 100, "Реєстр артефактів\nOCI Image / Helm / Deb", size=11, color=INK,
                       fill="#ffffff", stroke=FIELD, sw=1.2, min_w=170)
    p.append(b3)
    # Загрози фази 3
    p.append(rect(470, 150, 170, 170, fill="#fff5f5", stroke=POS, sw=1.2, rx=6))
    p.append(text(555, 172, "Вектори загроз:", size=11, color=POS, bold=True))
    p.append(text(555, 196, "• Підміна бінарного образу", size=10, color=INK))
    p.append(text(555, 218, "• Зміна тегу (tag mutability)", size=10, color=INK))
    p.append(text(555, 240, "• Фальсифікація метаданих", size=10, color=INK))
    p.append(text(555, 262, "• Перехоплення трафіку MitM", size=10, color=INK))
    p.append(text(555, 284, "• Витік приватного ключа", size=10, color=MUTED))
    p.append(text(555, 304, "(Підпис без прозорості)", size=9, color=POS, italic=True))

    # Елементи фази 4
    b4, _, _ = textbox(765, 100, "Kubernetes / Вузол\nКонтролер допуску", size=11, color=INK,
                       fill="#ffffff", stroke="#be185d", sw=1.2, min_w=170)
    p.append(b4)
    # Загрози фази 4
    p.append(rect(680, 150, 170, 170, fill="#fff5f5", stroke=POS, sw=1.2, rx=6))
    p.append(text(765, 172, "Вектори загроз:", size=11, color=POS, bold=True))
    p.append(text(765, 196, "• Запуск неперевіреного образу", size=10, color=INK))
    p.append(text(765, 218, "• Обхід політик контролера", size=10, color=INK))
    p.append(text(765, 240, "• TOCTOU між перевіркою й пулом", size=10, color=INK))
    p.append(text(765, 262, "• Невідомий склад компонентів", size=10, color=INK))
    p.append(text(765, 284, "• Сліпа довіра без атестації", size=10, color=MUTED))
    p.append(text(765, 304, "(Експлуатація CVE в рантаймі)", size=9, color=POS, italic=True))

    render(os.path.join(OUT, "supply-chain-attack-vectors.svg"), W, H, *p,
           title="Вектори атак на фазах ланцюга постачання програмного забезпечення")


# ── 2. slsa-levels-provenance: Архітектура SLSA та ланцюжок довіри ─────────────
def fig_slsa_levels_provenance():
    W, H = 880, 370
    p = []

    # 1. Вихідний комміт Git
    p.append(rect(20, 70, 160, 95, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(100, 96, "Git Repository", size=12, color=INK, bold=True))
    p.append(text(100, 120, "Фіксований комміт", size=10, color=MUTED))
    p.append(text(100, 142, "SHA: a8f93b2...", size=10, color=NEG))

    # Стрілка до збирача
    p.append(arrow(180, 115, 230, 115, color=LINE, sw=1.8))
    p.append(text(205, 105, "trigger", size=9, color=MUTED))

    # 2. Ізольований збирач SLSA L3
    p.append(rect(230, 50, 210, 135, fill="#eff6ff", stroke=NEG, sw=2, rx=10))
    p.append(text(335, 75, "Ізольований збирач", size=13, color=NEG, bold=True))
    p.append(text(335, 96, "(SLSA Build Level 3)", size=11, color=INK, bold=True))
    p.append(text(335, 120, "Герметичне середовище", size=10, color=MUTED))
    p.append(text(335, 142, "Одноразовий раннер CI", size=10, color=MUTED))
    p.append(text(335, 164, "Захист від підміни параметрів", size=9, color=FIELD, bold=True))

    # Стрілки виходу зі збирача: на бінарний артефакт і на атестацію
    p.append(arrow(440, 90, 490, 90, color=FIELD, sw=2))
    p.append(arrow(440, 145, 490, 145, color="#b45309", sw=2))

    # 3. Бінарний артефакт
    p.append(rect(490, 60, 170, 60, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(575, 85, "Бінарний артефакт", size=11, color=FIELD, bold=True))
    p.append(text(575, 105, "Digest: sha256:4c10...", size=9, color=INK))

    # 4. Атестація SLSA Provenance
    p.append(rect(490, 130, 170, 65, fill="#fffbeb", stroke="#b45309", sw=1.5, rx=6))
    p.append(text(575, 150, "SLSA Provenance", size=11, color="#b45309", bold=True))
    p.append(text(575, 168, "in-toto JSON Envelope", size=9, color=MUTED))
    p.append(text(575, 184, "builder.id + commit + flags", size=9, color=INK))

    # 5. Блок Sigstore (Cosign + Fulcio + Rekor)
    p.append(rect(230, 215, 430, 135, fill="#f5f3ff", stroke="#6d28d9", sw=2, rx=10))
    p.append(text(445, 238, "Інфраструктура безключового підпису (Sigstore)", size=12, color="#6d28d9", bold=True))

    p.append(rect(245, 255, 120, 80, fill="#ffffff", stroke="#6d28d9", sw=1.2, rx=6))
    p.append(text(305, 276, "OIDC (GitHub)", size=10, color=INK, bold=True))
    p.append(text(305, 296, "Identity Token", size=9, color=MUTED))
    p.append(text(305, 316, "workflow identity", size=9, color="#6d28d9"))

    p.append(arrow(365, 295, 395, 295, color="#6d28d9", sw=1.5))

    p.append(rect(395, 255, 120, 80, fill="#ffffff", stroke="#6d28d9", sw=1.2, rx=6))
    p.append(text(455, 276, "Fulcio CA", size=10, color=INK, bold=True))
    p.append(text(455, 296, "Короткоживучий", size=9, color=MUTED))
    p.append(text(455, 316, "X.509 сертифікат", size=9, color=FIELD, bold=True))

    p.append(arrow(515, 295, 545, 295, color="#6d28d9", sw=1.5))

    p.append(rect(545, 255, 105, 80, fill="#ffffff", stroke="#6d28d9", sw=1.2, rx=6))
    p.append(text(597, 276, "Rekor Log", size=10, color=INK, bold=True))
    p.append(text(597, 296, "Незмінний лог", size=9, color=MUTED))
    p.append(text(597, 316, "Merkle Tree", size=9, color=POS, bold=True))

    # Стрілка від атестації до Sigstore
    p.append(arrow(575, 195, 575, 215, color="#6d28d9", sw=1.5))

    # 6. Контролер допуску в Kubernetes
    p.append(rect(690, 60, 175, 290, fill="#faf5ff", stroke="#7e22ce", sw=2, rx=10))
    p.append(text(777, 85, "Admission Webhook", size=12, color="#7e22ce", bold=True))
    p.append(text(777, 105, "Kyverno / Gatekeeper", size=10, color=MUTED))

    # Перевірки всередині вебхука
    p.append(rect(702, 120, 150, 52, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    p.append(text(777, 140, "1. Валідація підпису", size=10, color=FIELD, bold=True))
    p.append(text(777, 158, "Fulcio Root + Rekor Log", size=9, color=INK))

    p.append(rect(702, 180, 150, 62, fill="#ffffff", stroke=NEG, sw=1, rx=4))
    p.append(text(777, 200, "2. Перевірка SLSA L3", size=10, color=NEG, bold=True))
    p.append(text(777, 218, "Власний builder.id", size=9, color=INK))
    p.append(text(777, 232, "Збіг хешу репозиторію", size=9, color=INK))

    p.append(rect(702, 250, 150, 52, fill="#ffffff", stroke=POS, sw=1, rx=4))
    p.append(text(777, 270, "3. Вердикт допуску", size=10, color=POS, bold=True))
    p.append(text(777, 288, "Allow Pod / Block Run", size=9, color=INK))

    # Стрілки від артефактів та Rekor до Admission Webhook
    p.append(arrow(660, 90, 690, 90, color=FIELD, sw=1.8))
    p.append(arrow(650, 295, 690, 295, color="#6d28d9", sw=1.8))

    render(os.path.join(OUT, "slsa-levels-provenance.svg"), W, H, *p,
           title="Архітектура SLSA Provenance та безключовий підпис артефактів через Sigstore")


# ── 3. sbom-vex-resolution: Зіставлення графа SBOM та статусів VEX ────────────
def fig_sbom_vex_resolution():
    W, H = 880, 350
    p = []

    # Лівий блок: Граф компонентів SBOM
    p.append(rect(20, 50, 270, 280, fill="#f8fafc", stroke=NEG, sw=1.8, rx=8))
    p.append(text(155, 75, "Граф компонентів SBOM", size=11, color=NEG, bold=True))

    # Вузли графа
    p.append(rect(80, 95, 150, 35, fill="#ffffff", stroke=NEG, sw=1.2, rx=6))
    p.append(text(155, 117, "Додаток: service-core:v2.1", size=10, color=INK, bold=True))

    p.append(rect(35, 155, 110, 35, fill="#ffffff", stroke=LINE, sw=1, rx=6))
    p.append(text(90, 177, "lib-crypto v1.4", size=9, color=INK))

    p.append(rect(165, 155, 110, 35, fill="#ffffff", stroke=LINE, sw=1, rx=6))
    p.append(text(220, 177, "lib-parser v3.0", size=9, color=INK))

    p.append(rect(35, 215, 110, 35, fill="#ffffff", stroke=LINE, sw=1, rx=6))
    p.append(text(90, 237, "transitive-util v0.8", size=9, color=INK))

    p.append(rect(165, 215, 110, 35, fill="#ffffff", stroke=LINE, sw=1, rx=6))
    p.append(text(220, 237, "transitive-net v2.2", size=9, color=INK))

    p.append(text(155, 280, "Повний перелік залежностей,", size=9, color=MUTED))
    p.append(text(155, 296, "хешів SHA-256 та ліцензій", size=9, color=MUTED))
    p.append(text(155, 314, "Разом: 120 компонентів", size=10, color=NEG, bold=True))

    # Стрілки дерева
    p.append(line(130, 130, 90, 155, color=LINE, sw=1.2))
    p.append(line(180, 130, 220, 155, color=LINE, sw=1.2))
    p.append(line(90, 190, 90, 215, color=LINE, sw=1.2))
    p.append(line(220, 190, 220, 215, color=LINE, sw=1.2))

    # Стрілка до сканера
    p.append(arrow(290, 170, 330, 170, color=LINE, sw=1.8))

    # Центральний блок: Сирий сканер CVE
    p.append(rect(330, 55, 210, 275, fill="#fff7ed", stroke="#ea580c", sw=1.8, rx=8))
    p.append(text(435, 80, "Сирий сканер CVE", size=12, color="#ea580c", bold=True))
    p.append(text(435, 100, "Пошук за базами NVD/OSV", size=9, color=MUTED))

    p.append(rect(345, 115, 180, 50, fill="#fee2e2", stroke=POS, sw=1, rx=4))
    p.append(text(435, 135, "Знайдено 42 вразливості", size=10, color=POS, bold=True))
    p.append(text(435, 153, "12 Critical, 30 High", size=9, color=POS))

    p.append(rect(345, 175, 180, 135, fill="#ffffff", stroke="#ea580c", sw=1, rx=4))
    p.append(text(435, 195, "Проблема «Шуму сповіщень»:", size=9, color="#ea580c", bold=True))
    p.append(text(435, 217, "• 85% коду не викликається", size=9, color=INK))
    p.append(text(435, 237, "• Вразливі функції не активні", size=9, color=INK))
    p.append(text(435, 257, "• Конвеєр блокує реліз даремно", size=9, color=INK))
    p.append(text(435, 277, "• Втома інженерів безпеки", size=9, color=MUTED))
    p.append(text(435, 297, "(Хибнопозитивні зупинки)", size=9, color=POS, italic=True))

    # Стрілка до VEX
    p.append(arrow(540, 170, 580, 170, color=LINE, sw=1.8))

    # Правий блок: Контекстна фільтрація VEX
    p.append(rect(580, 50, 280, 280, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(720, 75, "Фільтрація VEX (OpenVEX / CSAF)", size=11, color=FIELD, bold=True))

    p.append(rect(595, 95, 250, 52, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    p.append(text(720, 113, "CVE-2023-44487 (lib-parser)", size=9, color=INK, bold=True))
    p.append(text(720, 128, "Статус: not_affected (код недосяжний)", size=9, color=FIELD, bold=True))
    p.append(text(720, 140, "Обґрунтування: code_not_reachable", size=9, color=MUTED))

    p.append(rect(595, 155, 250, 52, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    p.append(text(720, 173, "CVE-2024-3094 (transitive-util)", size=9, color=INK, bold=True))
    p.append(text(720, 188, "Статус: not_affected (вимкнено прапорець)", size=9, color=FIELD, bold=True))
    p.append(text(720, 200, "Обґрунтування: vulnerable_code_not_used", size=9, color=MUTED))

    p.append(rect(595, 215, 250, 52, fill="#fff5f5", stroke=POS, sw=1.2, rx=4))
    p.append(text(720, 233, "CVE-2024-21626 (lib-crypto)", size=9, color=POS, bold=True))
    p.append(text(720, 248, "Статус: affected (вимагає виправлення!)", size=9, color=POS, bold=True))
    p.append(text(720, 260, "Дія: Термінове оновлення до v1.4.2", size=9, color=INK))

    p.append(rect(595, 275, 250, 48, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(720, 293, "Підсумок: 1 реальна загроза замість 42", size=9, color=FIELD, bold=True))
    p.append(text(720, 310, "Фокус інженерів на критичному шляху", size=9, color=INK))

    render(os.path.join(OUT, "sbom-vex-resolution.svg"), W, H, *p,
           title="Зіставлення графа компонентів SBOM та аналіз експлуатованості через VEX")


if __name__ == "__main__":
    fig_supply_chain_attack_vectors()
    fig_slsa_levels_provenance()
    fig_sbom_vex_resolution()
    print("Figures generated successfully.")
