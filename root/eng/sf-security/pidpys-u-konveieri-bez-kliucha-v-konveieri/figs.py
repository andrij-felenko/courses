# -*- coding: utf-8 -*-
import sys, os

# Шлях до scripts/ у корені репозиторію (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Кольорова палітра теми ──────────────────────────────────────────
CLR_ERR   = "#c0392b"     # Помилка, витік, загроза
CLR_ERR_F = "#fdecea"
CLR_OK    = "#27ae60"     # Безпечно, успіх, цілісність
CLR_OK_F  = "#eafaf0"
CLR_WARN  = "#d97706"     # Попередження, перевірка політик
CLR_WARN_F= "#fef3c7"
CLR_INFO  = "#2457d6"     # Інформація, OIDC токени, RPC
CLR_INFO_F= "#eaf0fd"
CLR_DATA  = "#4b5563"     # Артефакти, геші, дані
CLR_DATA_F= "#f3f4f6"
CLR_MATH  = "#6b21a8"     # Криптографія, HSM, підписи
CLR_MATH_F= "#f5f3ff"


# ── 1. Порівняння підходів до підпису в CI/CD ────────────────────────
def fig_traditional_vs_remote():
    W, H = 1040, 520
    p = []

    p.append(text(W / 2, 28, "Порівняння архітектури підпису: статичний ключ у раннері проти віддаленого HSM", size=16, color=INK, bold=True))

    # Ліва колонка: Антипідхід
    p.append(rect(40, 55, 460, 440, fill="#ffffff", stroke=CLR_ERR, sw=1.5, rx=8))
    p.append(text(270, 82, "Антипідхід: статичний приватний ключ у CI/CD", size=14, color=CLR_ERR, bold=True))
    p.append(text(270, 102, "Змінні середовища / runner secrets", size=11, color=MUTED, italic=True))

    p.append(fitbox(65, 120, 410, 55, "CI Runner (GitHub Actions / GitLab CI)\nВиконує збірку та сторонній код", size=12, fill=CLR_DATA_F, stroke=CLR_DATA))
    p.append(fitbox(90, 190, 360, 48, "Секрет у пам'яті: PRIVATE_KEY.pem\n(Довгоживучий ключ релізу)", size=12, fill=CLR_ERR_F, stroke=CLR_ERR, bold=True))
    p.append(fitbox(90, 250, 360, 48, "Локальна криптографія: OpenSSL sign\n(Підпис виконується на раннері)", size=12, fill=CLR_DATA_F, stroke=CLR_DATA))

    p.append(arrow(270, 310, 270, 345, color=CLR_ERR, sw=2.0))
    p.append(fitbox(65, 345, 410, 130, "Катастрофа компрометації:\n1. Вразливий npm/pip/cargo пакунок або шкідливий PR\n2. Читання змінних середовища чи пам'яті процесу\n3. Викрадення приватного ключа нападником\n4. Безстроковий підпис шкідливого софту", size=11, fill=CLR_ERR_F, stroke=CLR_ERR))

    # Права колонка: Віддалене підписання
    p.append(rect(540, 55, 460, 440, fill="#ffffff", stroke=CLR_OK, sw=1.5, rx=8))
    p.append(text(770, 82, "Віддалений підпис: ізольований сервіс + HSM", size=14, color=CLR_OK, bold=True))
    p.append(text(770, 102, "Zero-Trust для раннерів конвеєра", size=11, color=MUTED, italic=True))

    p.append(fitbox(565, 120, 410, 55, "CI Runner (Недовірене середовище)\nЗбирає артефакт, рахує лише SHA-256", size=12, fill=CLR_DATA_F, stroke=CLR_DATA))
    p.append(fitbox(590, 190, 360, 48, "Запит через mTLS: Digest + OIDC Token\n(Жодного закритого ключа в раннері)", size=12, fill=CLR_INFO_F, stroke=CLR_INFO, bold=True))

    p.append(arrow(770, 240, 770, 270, color=CLR_INFO, sw=1.8))

    p.append(fitbox(565, 270, 410, 65, "Signing Service (Ізольована зона)\n1. Перевірка OIDC токену (коміт, тег, автор)\n2. Перевірка політики (лише release-теги)", size=11, fill=CLR_WARN_F, stroke=CLR_WARN, bold=True))

    p.append(arrow(770, 337, 770, 365, color=CLR_MATH, sw=1.8))

    p.append(fitbox(565, 365, 410, 110, "Апаратний модуль безпеки (HSM / KMS):\nКлюч ніколи не експортується назовні.\nАпаратне обчислення цифрового підпису.\nПовернення лише signature у відповідь.", size=11, fill=CLR_OK_F, stroke=CLR_OK, bold=True))

    return render(os.path.join(OUT, "traditional-vs-remote-signing.svg"), W, H, *p)


# ── 2. Повний потік ефемерної автентифікації та підпису ─────────────
def fig_oidc_signing_flow():
    W, H = 1060, 580
    p = []

    p.append(text(W / 2, 26, "Послідовність віддаленого підписання з OIDC-автентифікацією", size=16, color=INK, bold=True))

    # Стовпці учасників
    nodes = [
        (130, "CI Runner\n(GitHub / GitLab)", CLR_DATA_F, CLR_DATA),
        (370, "OIDC Provider\n(Identity IdP)", CLR_INFO_F, CLR_INFO),
        (610, "Signing Service\n(Policy Gate)", CLR_WARN_F, CLR_WARN),
        (850, "Hardware HSM\n(PKCS#11 Core)", CLR_MATH_F, CLR_MATH),
    ]

    for x, label, fcol, scol in nodes:
        p.append(fitbox(x - 90, 50, 180, 50, label, size=12, fill=fcol, stroke=scol, bold=True))
        p.append(line(x, 105, x, 550, color=LINE, sw=1.0, dash="4,4"))

    # Кроки протоколу
    steps = [
        (125, 130, 370, "1. Запит OIDC токену (aud: sig-service)", CLR_INFO),
        (165, 370, 130, "2. Підписаний JWT (repo, ref, sha)", CLR_INFO),
        (215, 130, 130, "3. Обчислення SHA-256(Artifact)", CLR_DATA),
        (265, 130, 610, "4. RPC Sign(Digest, OIDC_JWT)", CLR_INFO),
        (315, 610, 370, "5. Перевірка JWT через JWKS", CLR_WARN),
        (365, 610, 610, "6. Валідація політики: ref==refs/tags/v*", CLR_WARN),
        (415, 610, 850, "7. C_Sign(KeyHandle, Digest)", CLR_MATH),
        (465, 850, 610, "8. Raw Signature", CLR_MATH),
        (515, 610, 130, "9. SignResponse(Signature + Bundle)", CLR_OK),
    ]

    for y, x1, x2, msg, col in steps:
        if x1 == x2:
            # Внутрішня дія
            p.append(rect(x1 - 10, y - 12, 20, 24, fill=col, stroke=col, rx=4))
            p.append(textbox(x1 + 120, y, msg, size=11, fill="#ffffff", stroke=col, sw=1.2, pad=6)[0])
        else:
            p.append(arrow(x1, y, x2, y, color=col, sw=1.8))
            mid_x = (x1 + x2) / 2
            p.append(textbox(mid_x, y - 14, msg, size=11, fill="#ffffff", stroke=col, sw=1.0, pad=5)[0])

    return render(os.path.join(OUT, "oidc-signing-flow.svg"), W, H, *p)


# ── 3. Структура OIDC клеймів та оцінка рушієм політик ───────────────
def fig_jwt_claims_policy():
    W, H = 1040, 520
    p = []

    p.append(text(W / 2, 28, "Анатомія OIDC JWT токену та оцінка умов у рушії політик підпису", size=16, color=INK, bold=True))

    # Лівий блок: Структура JWT токену
    p.append(rect(40, 55, 450, 440, fill="#ffffff", stroke=CLR_INFO, sw=1.5, rx=8))
    p.append(text(265, 80, "Структура OIDC токену раннера (JWT)", size=13, color=CLR_INFO, bold=True))

    jwt_text = (
        "{\n"
        '  "iss": "https://token.actions.githubusercontent.com",\n'
        '  "sub": "repo:acme-corp/firmware-app:ref:refs/tags/v2.4.0",\n'
        '  "aud": "https://signing.internal.acme.net",\n'
        '  "repository": "acme-corp/firmware-app",\n'
        '  "ref": "refs/tags/v2.4.0",\n'
        '  "ref_type": "tag",\n'
        '  "actor": "release-maintainer",\n'
        '  "job_workflow_ref": "acme-corp/firmware-app/.github/workflows/release.yml@refs/tags/v2.4.0",\n'
        '  "sha": "7f8b91a2c3d4e5f60718293a4b5c6d7e8f901234",\n'
        '  "exp": 1724810400\n'
        "}"
    )
    p.append(fitbox(55, 95, 420, 385, jwt_text, size=11, fill=CLR_INFO_F, stroke=CLR_INFO))

    # Правий блок: Рушій перевірки політик
    p.append(rect(530, 55, 470, 440, fill="#ffffff", stroke=CLR_WARN, sw=1.5, rx=8))
    p.append(text(765, 80, "Оцінка правил у Policy Engine", size=13, color=CLR_WARN, bold=True))

    rules = [
        (105, "1. Довірений Issuer (IdP)", 'iss == "https://token.actions.githubusercontent.com"', True),
        (180, "2. Цільовий сервіс (Audience)", 'aud == "https://signing.internal.acme.net"', True),
        (255, "3. Репозиторій проекту", 'repository == "acme-corp/firmware-app"', True),
        (330, "4. Захищений тег релізу", 'ref matches "^refs/tags/v[0-9]+\\.[0-9]+\\.[0-9]+$"', True),
        (405, "5. Довірений Workflow", 'job_workflow_ref contains ".github/workflows/release.yml"', True),
    ]

    for y, title, cond, ok in rules:
        col = CLR_OK if ok else CLR_ERR
        bg_col = CLR_OK_F if ok else CLR_ERR_F
        status = "✓ ДОЗВОЛЕНО" if ok else "✗ ВІДХИЛЕНО"
        p.append(rect(545, y, 440, 65, fill=bg_col, stroke=col, sw=1.2, rx=6))
        p.append(text(560, y + 22, title, size=12, color=INK, bold=True, anchor="start"))
        p.append(text(970, y + 22, status, size=11, color=col, bold=True, anchor="end"))
        p.append(text(560, y + 48, cond, size=11, color=MUTED, anchor="start"))

    return render(os.path.join(OUT, "jwt-claims-policy-evaluation.svg"), W, H, *p)


# ── 4. Захищений конверт та межі безпеки віддаленого підпису ─────────
def fig_remote_signing_envelope():
    W, H = 1040, 500
    p = []

    p.append(text(W / 2, 28, "Архітектура захищеного конверта та межа довіри віддаленого підпису", size=16, color=INK, bold=True))

    # Зона 1: CI/CD Раннер
    p.append(rect(40, 55, 300, 420, fill="#ffffff", stroke=CLR_DATA, sw=1.5, rx=8))
    p.append(text(190, 80, "Зона збірки (CI Runner)", size=13, color=CLR_DATA, bold=True))
    p.append(text(190, 98, "Недовірений контур виконання", size=10, color=MUTED, italic=True))

    p.append(fitbox(60, 115, 260, 50, "Вихідний артефакт\n(firmware.bin / app.tar.gz)", size=12, fill=CLR_DATA_F, stroke=CLR_DATA))
    p.append(arrow(190, 167, 190, 195, color=CLR_DATA))

    p.append(fitbox(60, 195, 260, 55, "Локальне гешування:\nSHA-256(Artifact)\n-> 32-байтовий дайджест", size=11, fill=CLR_DATA_F, stroke=CLR_DATA, bold=True))
    p.append(arrow(190, 252, 190, 280, color=CLR_DATA))

    p.append(fitbox(60, 280, 260, 50, "Отримання OIDC JWT\nвід провайдера CI", size=12, fill=CLR_INFO_F, stroke=CLR_INFO))
    p.append(arrow(190, 332, 190, 360, color=CLR_INFO))

    p.append(fitbox(60, 360, 260, 95, "RPC Клієнт підпису:\nПакування дайджесту,\nOIDC токену та Key-ID\nу захищений envelope", size=11, fill=CLR_INFO_F, stroke=CLR_INFO, bold=True))

    # Перехідний тунель mTLS
    p.append(arrow(345, 270, 415, 270, color=CLR_INFO, sw=2.5))
    p.append(textbox(380, 240, "Захищений канал\nmTLS + OIDC Bearer", size=11, fill="#ffffff", stroke=CLR_INFO, sw=1.0, pad=5)[0])

    # Зона 2: Signing Gateway
    p.append(rect(420, 55, 300, 420, fill="#ffffff", stroke=CLR_WARN, sw=1.5, rx=8))
    p.append(text(570, 80, "Signing Service (DMZ)", size=13, color=CLR_WARN, bold=True))
    p.append(text(570, 98, "Контроль доступу та політик", size=10, color=MUTED, italic=True))

    p.append(fitbox(440, 115, 260, 60, "Декодування envelope:\nПеревірка сигнатури OIDC\nта клеймів контексту", size=11, fill=CLR_INFO_F, stroke=CLR_INFO))
    p.append(arrow(570, 177, 570, 205, color=CLR_WARN))

    p.append(fitbox(440, 205, 260, 65, "Policy Engine:\nФільтрація за git-тегом,\nрепозиторієм та автором", size=11, fill=CLR_WARN_F, stroke=CLR_WARN, bold=True))
    p.append(arrow(570, 272, 570, 300, color=CLR_WARN))

    p.append(fitbox(440, 300, 260, 60, "Аудит та Rate-limit:\nЗапис події у tamper-evident\nжурнал операцій", size=11, fill=CLR_WARN_F, stroke=CLR_WARN))
    p.append(arrow(570, 362, 570, 390, color=CLR_MATH))

    p.append(fitbox(440, 390, 260, 65, "PKCS#11 Driver Call:\nПередача 32B дайджесту\nдо апаратного слоту HSM", size=11, fill=CLR_MATH_F, stroke=CLR_MATH, bold=True))

    # Перехід до HSM
    p.append(arrow(725, 270, 775, 270, color=CLR_MATH, sw=2.5))
    p.append(textbox(750, 240, "PCIe / HSM Bus\nPKCS#11 API", size=11, fill="#ffffff", stroke=CLR_MATH, sw=1.0, pad=5)[0])

    # Зона 3: HSM Core
    p.append(rect(780, 55, 220, 420, fill="#ffffff", stroke=CLR_MATH, sw=1.5, rx=8))
    p.append(text(890, 80, "HSM / KMS Core", size=13, color=CLR_MATH, bold=True))
    p.append(text(890, 98, "Апаратний анклав", size=10, color=MUTED, italic=True))

    p.append(fitbox(800, 120, 180, 90, "Апаратне сховище:\nНезмінний приватний ключ\n(ECDSA P-256 / Ed25519)\nNon-exportable", size=11, fill=CLR_MATH_F, stroke=CLR_MATH, bold=True))
    p.append(arrow(890, 212, 890, 250, color=CLR_MATH))

    p.append(fitbox(800, 250, 180, 80, "Криптопроцесор:\nАпаратний розрахунок\nпідпису над дайджестом:\nSign(PrivKey, Digest)", size=11, fill=CLR_MATH_F, stroke=CLR_MATH, bold=True))
    p.append(arrow(890, 332, 890, 370, color=CLR_OK))

    p.append(fitbox(800, 370, 180, 85, "Вихідний підпис:\n(r, s) / Ed25519 Sig\nПовертається клієнту\nу відповідь", size=11, fill=CLR_OK_F, stroke=CLR_OK, bold=True))

    return render(os.path.join(OUT, "remote-signing-envelope.svg"), W, H, *p)


if __name__ == "__main__":
    fig_traditional_vs_remote()
    fig_oidc_signing_flow()
    fig_jwt_claims_policy()
    fig_remote_signing_envelope()
    print("All figures generated successfully.")
