# -*- coding: utf-8 -*-
import sys
import os

# scripts/ directory is 4 levels up: book/programming/security/zero-trust -> ../../../..
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. castle-moat-vs-zero-trust: Периметрова безпека проти Нульової довіри ───
def fig_castle_moat_vs_zero_trust():
    W, H = 840, 360
    p = []

    # Ліва колонка: Традиційна периметрова модель ("Замок і рів")
    p.append(rect(20, 20, 385, 320, fill="#fdf2f2", stroke="#e05252", sw=1.8, rx=10))
    p.append(text(212, 45, "Периметрова модель («Замок і рів»)", size=13, color="#991b1b", bold=True))
    p.append(text(212, 65, "Довіра за мережевим розташуванням (L3/VPN)", size=10, color=MUTED))

    # Периметровий фаєрвол
    p.append(rect(35, 85, 355, 36, fill="#fee2e2", stroke="#ef4444", sw=1.5, rx=6))
    p.append(text(212, 107, "Корпоративний периметр (VPN / Firewall / DMZ)", size=11, color="#b91c1c", bold=True))

    # Внутрішня плоска мережа
    p.append(rect(35, 135, 355, 190, fill="#fff5f5", stroke="#fca5a5", sw=1.2, rx=6))
    p.append(text(212, 155, "Внутрішня «довірена» мережа (Flat LAN)", size=11, color=INK, bold=True))

    # Скомпрометований вузол
    p.append(rect(50, 175, 130, 60, fill="#fecaca", stroke="#dc2626", sw=1.5, rx=6))
    p.append(text(115, 198, "Скомпрометований", size=10, color="#991b1b", bold=True))
    p.append(text(115, 216, "вузол / ноутбук", size=10, color="#991b1b"))

    # Сервіс А та Сервіс Б
    p.append(rect(240, 175, 135, 60, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(307, 198, "Внутрішній сервіс A", size=10, color=INK, bold=True))
    p.append(text(307, 216, "без автентифікації", size=9, color=MUTED))

    p.append(rect(145, 255, 145, 60, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(217, 278, "База даних / Секрети", size=10, color=INK, bold=True))
    p.append(text(217, 296, "статичні паролі", size=9, color=MUTED))

    # Червоні стрілки латерального руху
    p.append(arrow(180, 205, 235, 205, color="#dc2626", sw=2))
    p.append(arrow(115, 235, 150, 255, color="#dc2626", sw=2))
    p.append(text(195, 170, "Вільний рух (Lateral Movement)", size=9, color="#dc2626", bold=True))


    # Права колонка: Архітектура нульової довіри (Zero Trust)
    p.append(rect(435, 20, 385, 320, fill="#f0fdf4", stroke="#16a34a", sw=1.8, rx=10))
    p.append(text(627, 45, "Архітектура нульової довіри (Zero Trust)", size=13, color="#166534", bold=True))
    p.append(text(627, 65, "Жодної неявної довіри: перевірка кожного виклику", size=10, color=MUTED))

    # Мікропериметри навколо кожного ресурсу
    # Вузол 1
    p.append(rect(450, 90, 160, 105, fill="#ffffff", stroke="#86efac", sw=1.5, rx=6))
    p.append(text(530, 110, "Клієнт / Ворклоад", size=10, color=INK, bold=True))
    p.append(rect(460, 125, 140, 30, fill="#dcfce7", stroke="#22c55e", sw=1, rx=4))
    p.append(text(530, 143, "SVID / mTLS Client", size=9, color="#15803d", bold=True))
    p.append(text(530, 180, "Постійна атестація", size=9, color=MUTED))

    # Вузол 2
    p.append(rect(645, 90, 160, 105, fill="#ffffff", stroke="#86efac", sw=1.5, rx=6))
    p.append(text(725, 110, "Сервіс API", size=10, color=INK, bold=True))
    p.append(rect(655, 125, 140, 30, fill="#dcfce7", stroke="#22c55e", sw=1, rx=4))
    p.append(text(725, 143, "L7 PEP / Envoy Proxy", size=9, color="#15803d", bold=True))
    p.append(text(725, 180, "Перевірка токена й прав", size=9, color=MUTED))

    # Канал mTLS між ними
    p.append(arrow(610, 140, 640, 140, color="#16a34a", sw=2))
    p.append(text(627, 128, "mTLS", size=9, color="#16a34a", bold=True))

    # Центральний блок PDP / Policy Engine
    p.append(rect(450, 220, 355, 105, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=8))
    p.append(text(627, 242, "Контрольна площина: PDP / Identity Provider", size=11, color="#0369a1", bold=True))
    p.append(text(627, 262, "Динамічна оцінка контексту: стан пристрою, роль, ризик", size=9, color=INK))

    p.append(arrow(530, 195, 530, 215, color="#0284c7", sw=1.5))
    p.append(arrow(725, 195, 725, 215, color="#0284c7", sw=1.5))
    p.append(text(627, 295, "Короткоживучі сертифікати й правила Just-In-Time", size=9, color="#0369a1", italic=True))

    render(os.path.join(OUT, "castle-moat-vs-zero-trust.svg"), W, H, *p,
           title="Порівняння периметрової моделі та Zero Trust")


# ── 2. nist-zta-control-data-plane: Логічна архітектура NIST SP 800-207 ──────
def fig_nist_zta_control_data_plane():
    W, H = 840, 390
    p = []

    # Верхня область: Control Plane (Площина керування)
    p.append(rect(20, 20, 800, 200, fill="#f0f9ff", stroke="#0284c7", sw=1.8, rx=10))
    p.append(text(160, 42, "ПЛОЩИНА КЕРУВАННЯ (Control Plane)", size=12, color="#0369a1", bold=True))

    # Блок PDP (Policy Decision Point)
    p.append(rect(40, 60, 380, 145, fill="#ffffff", stroke="#0ea5e9", sw=1.5, rx=8))
    p.append(text(230, 82, "PDP (Точка ухвалення рішень)", size=12, color="#0369a1", bold=True))

    # PE і PA всередині PDP
    p.append(rect(55, 95, 160, 95, fill="#e0f2fe", stroke="#38bdf8", sw=1.2, rx=6))
    p.append(text(135, 118, "Policy Engine (PE)", size=11, color=INK, bold=True))
    p.append(text(135, 138, "Рушій оцінки правил", size=9, color=MUTED))
    p.append(text(135, 158, "обчислює вердикт", size=9, color="#0369a1"))
    p.append(text(135, 175, "allow / deny / challenge", size=9, color="#0369a1", italic=True))

    p.append(rect(240, 95, 165, 95, fill="#e0f2fe", stroke="#38bdf8", sw=1.2, rx=6))
    p.append(text(322, 118, "Policy Admin (PA)", size=11, color=INK, bold=True))
    p.append(text(322, 138, "Адміністратор політик", size=9, color=MUTED))
    p.append(text(322, 158, "генерація / відкликання", size=9, color="#0369a1"))
    p.append(text(322, 175, "облікових даних та сесій", size=9, color="#0369a1", italic=True))

    p.append(arrow(215, 142, 235, 142, color="#0284c7", sw=1.5))

    # Блок PIP (Policy Information Point) - Джерела контексту
    p.append(rect(450, 60, 350, 145, fill="#ffffff", stroke="#0ea5e9", sw=1.5, rx=8))
    p.append(text(625, 82, "PIP (Джерела контексту й телеметрії)", size=12, color="#0369a1", bold=True))

    p.append(rect(465, 95, 155, 45, fill="#f8fafc", stroke=LINE, sw=1, rx=4))
    p.append(text(542, 112, "IdP / Каталог суб'єктів", size=9, color=INK, bold=True))
    p.append(text(542, 128, "ролі, групи, MFA", size=9, color=MUTED))

    p.append(rect(635, 95, 150, 45, fill="#f8fafc", stroke=LINE, sw=1, rx=4))
    p.append(text(710, 112, "EDR / MDM стан пристрою", size=9, color=INK, bold=True))
    p.append(text(710, 128, "патчі, диск, антивірус", size=9, color=MUTED))

    p.append(rect(465, 145, 155, 45, fill="#f8fafc", stroke=LINE, sw=1, rx=4))
    p.append(text(542, 162, "SIEM / Threat Intel", size=9, color=INK, bold=True))
    p.append(text(542, 178, "індикатори загроз", size=9, color=MUTED))

    p.append(rect(635, 145, 150, 45, fill="#f8fafc", stroke=LINE, sw=1, rx=4))
    p.append(text(710, 162, "Мережева телеметрія", size=9, color=INK, bold=True))
    p.append(text(710, 178, "геолокація, IP, поведінка", size=9, color=MUTED))

    p.append(arrow(450, 130, 425, 130, color="#0284c7", sw=1.5))
    p.append(text(437, 120, "Сигнали", size=9, color="#0369a1"))


    # Нижня область: Data Plane (Площина даних)
    p.append(rect(20, 240, 800, 130, fill="#f8fafc", stroke="#64748b", sw=1.8, rx=10))
    p.append(text(140, 260, "ПЛОЩИНА ДАНИХ (Data Plane)", size=12, color="#334155", bold=True))

    # Суб'єкт (Клієнт / Ворклоад)
    p.append(rect(40, 275, 160, 75, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    p.append(text(120, 302, "Суб'єкт (Subject)", size=11, color=INK, bold=True))
    p.append(text(120, 322, "користувач / мікросервіс", size=9, color=MUTED))

    # Точка застосування політики (PEP)
    p.append(rect(290, 270, 240, 85, fill="#fef3c7", stroke="#d97706", sw=1.8, rx=8))
    p.append(text(410, 292, "PEP (Точка застосування)", size=12, color="#92400e", bold=True))
    p.append(text(410, 312, "Шлюз / Ingress Proxy / Sidecar", size=10, color=INK))
    p.append(text(410, 332, "зупиняє запит і застосовує вердикт", size=9, color="#92400e", italic=True))

    # Захищений ресурс
    p.append(rect(620, 275, 180, 75, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    p.append(text(710, 302, "Корпоративний ресурс", size=11, color=INK, bold=True))
    p.append(text(710, 322, "API / База даних / Файли", size=9, color=MUTED))

    # Стрілки в Data Plane
    p.append(arrow(200, 312, 285, 312, color=INK, sw=2))
    p.append(text(242, 302, "Запит", size=10, color=INK))

    p.append(arrow(530, 312, 615, 312, color="#16a34a", sw=2))
    p.append(text(572, 302, "Дозволено", size=9, color="#16a34a", bold=True))

    # Зв'язок між PA і PEP (Контрольний канал)
    p.append(arrow(322, 190, 375, 265, color="#d97706", sw=1.8))
    p.append(arrow(410, 270, 355, 195, color="#0369a1", sw=1.8))
    p.append(text(460, 230, "Контрольний протокол (SVID / команди сесії)", size=9, color="#92400e", bold=True))

    render(os.path.join(OUT, "nist-zta-control-data-plane.svg"), W, H, *p,
           title="Логічна архітектура NIST SP 800-207: Control Plane та Data Plane")


# ── 3. spiffe-workload-attestation-flow: Атестація та видача SVID у SPIFFE/SPIRE ───
def fig_spiffe_workload_attestation_flow():
    W, H = 840, 370
    p = []

    # Блок 1: Робоче навантаження (Workload Process)
    p.append(rect(30, 40, 210, 290, fill="#f8fafc", stroke="#64748b", sw=1.8, rx=10))
    p.append(text(135, 65, "Робоче навантаження", size=12, color=INK, bold=True))
    p.append(text(135, 85, "Процес у контейнері / Pod", size=10, color=MUTED))

    p.append(rect(45, 110, 180, 50, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(135, 128, "Клієнтська бібліотека", size=10, color=INK, bold=True))
    p.append(text(135, 146, "SPIFFE Workload API Client", size=9, color=MUTED))

    p.append(rect(45, 180, 180, 65, fill="#dcfce7", stroke="#22c55e", sw=1.2, rx=6))
    p.append(text(135, 200, "Отриманий X.509-SVID", size=10, color="#15803d", bold=True))
    p.append(text(135, 218, "spiffe://prod/ns/app/sa/web", size=9, color=INK))
    p.append(text(135, 234, "Термін дії: 1 година", size=9, color=MUTED))

    p.append(rect(45, 260, 180, 55, fill="#ffffff", stroke="#3b82f6", sw=1.2, rx=6))
    p.append(text(135, 280, "mTLS з'єднання", size=10, color="#1d4ed8", bold=True))
    p.append(text(135, 298, "криптографічний тунель L4/L7", size=9, color=MUTED))


    # Блок 2: SPIRE Agent (Вузловий агент)
    p.append(rect(310, 40, 230, 290, fill="#eff6ff", stroke="#3b82f6", sw=1.8, rx=10))
    p.append(text(425, 65, "SPIRE Agent (Вузол)", size=12, color="#1d4ed8", bold=True))
    p.append(text(425, 85, "Працює як демонізований процес", size=10, color=MUTED))

    p.append(rect(325, 110, 200, 60, fill="#ffffff", stroke="#60a5fa", sw=1.2, rx=6))
    p.append(text(425, 128, "Workload Attestation", size=10, color="#1d4ed8", bold=True))
    p.append(text(425, 145, "Перевірка cgroup, PID, UID,", size=9, color=INK))
    p.append(text(425, 160, "K8s ServiceAccount токена", size=9, color=MUTED))

    p.append(rect(325, 185, 200, 60, fill="#ffffff", stroke="#60a5fa", sw=1.2, rx=6))
    p.append(text(425, 203, "Локальний кеш SVID", size=10, color=INK, bold=True))
    p.append(text(425, 222, "автоматична ротація ключів", size=9, color=MUTED))
    p.append(text(425, 236, "без звернення до сервера", size=9, color="#1d4ed8", italic=True))

    p.append(rect(325, 260, 200, 55, fill="#ffffff", stroke="#60a5fa", sw=1.2, rx=6))
    p.append(text(425, 280, "Node Attestation", size=10, color=INK, bold=True))
    p.append(text(425, 298, "TPM / AWS IID / GCP Token", size=9, color=MUTED))


    # Блок 3: SPIRE Server (Центральний сервер сертифікації)
    p.append(rect(610, 40, 200, 290, fill="#fdf4ff", stroke="#a855f7", sw=1.8, rx=10))
    p.append(text(710, 65, "SPIRE Server", size=12, color="#7e22ce", bold=True))
    p.append(text(710, 85, "Центр довіри організації", size=10, color=MUTED))

    p.append(rect(625, 110, 170, 60, fill="#ffffff", stroke="#c084fc", sw=1.2, rx=6))
    p.append(text(710, 130, "Реєстр правил селекторів", size=10, color=INK, bold=True))
    p.append(text(710, 148, "k8s:ns=app -> spiffe ID", size=9, color="#7e22ce"))
    p.append(text(710, 162, "docker:image_id=sha256", size=9, color=MUTED))

    p.append(rect(625, 190, 170, 60, fill="#ffffff", stroke="#c084fc", sw=1.2, rx=6))
    p.append(text(710, 210, "SPIFFE CA (Root / Interm)", size=10, color="#7e22ce", bold=True))
    p.append(text(710, 228, "Підпис X.509 сертифікатів", size=9, color=INK))
    p.append(text(710, 242, "та JWT токенів", size=9, color=MUTED))

    p.append(rect(625, 265, 170, 50, fill="#ffffff", stroke="#c084fc", sw=1.2, rx=6))
    p.append(text(710, 285, "Синхронізація Bundle", size=9, color=INK, bold=True))
    p.append(text(710, 302, "довірені кореневі ключі", size=9, color=MUTED))


    # Стрілки взаємодії між блоками
    p.append(arrow(240, 135, 305, 135, color="#1d4ed8", sw=2))
    p.append(text(275, 125, "UNIX сокет", size=9, color="#1d4ed8", bold=True))

    p.append(arrow(310, 200, 245, 200, color="#15803d", sw=2))
    p.append(text(275, 190, "SVID + Key", size=9, color="#15803d", bold=True))

    # Зв'язок між агентом і сервером по gRPC mTLS
    p.append(arrow(540, 140, 605, 140, color="#7e22ce", sw=2))
    p.append(arrow(610, 215, 545, 215, color="#7e22ce", sw=2))
    p.append(text(575, 130, "gRPC CSR", size=9, color="#7e22ce", bold=True))
    p.append(text(575, 205, "SVID Bundle", size=9, color="#7e22ce", bold=True))

    render(os.path.join(OUT, "spiffe-workload-attestation-flow.svg"), W, H, *p,
           title="Послідовність атестації та видачі SVID у SPIFFE/SPIRE")


# ── 4. continuous-adaptive-trust-lifecycle: Цикл неперервної адаптивної оцінки довіри ───
def fig_continuous_adaptive_trust_lifecycle():
    W, H = 840, 360
    p = []

    # 4 послідовні фази адаптивної довіри
    # Фаза 1: Початкова автентифікація
    p.append(rect(25, 40, 175, 270, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(112, 65, "1. Початковий вхід", size=11, color=INK, bold=True))
    p.append(text(112, 85, "Автентифікація", size=10, color=MUTED))

    p.append(rect(35, 105, 155, 60, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    p.append(text(112, 125, "FIDO2 / WebAuthn", size=10, color=INK, bold=True))
    p.append(text(112, 145, "Апаратний ключ + Біометрія", size=9, color=MUTED))

    p.append(rect(35, 180, 155, 60, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    p.append(text(112, 200, "Перевірка TPM / MDM", size=10, color=INK, bold=True))
    p.append(text(112, 220, "Шифрування диска, патчі", size=9, color=MUTED))

    p.append(rect(35, 255, 155, 45, fill="#dcfce7", stroke="#22c55e", sw=1, rx=4))
    p.append(text(112, 275, "Базовий Trust Score: 95", size=9, color="#15803d", bold=True))


    # Фаза 2: Безперервний моніторинг телеметрії
    p.append(rect(225, 40, 180, 270, fill="#f0f9ff", stroke="#0ea5e9", sw=1.5, rx=8))
    p.append(text(315, 65, "2. Телеметрія в реальному часі", size=11, color="#0369a1", bold=True))
    p.append(text(315, 85, "Постійний моніторинг", size=10, color=MUTED))

    p.append(rect(235, 105, 160, 50, fill="#ffffff", stroke="#7dd3fc", sw=1, rx=4))
    p.append(text(315, 123, "Зміна IP / Мережі", size=9, color=INK, bold=True))
    p.append(text(315, 140, "Нетипова ASN чи країна", size=9, color=MUTED))

    p.append(rect(235, 165, 160, 50, fill="#ffffff", stroke="#7dd3fc", sw=1, rx=4))
    p.append(text(315, 183, "EDR Сигнал тривоги", size=9, color=INK, bold=True))
    p.append(text(315, 200, "Вимкнено файрвол / вірус", size=9, color=MUTED))

    p.append(rect(235, 225, 160, 75, fill="#ffffff", stroke="#7dd3fc", sw=1, rx=4))
    p.append(text(315, 243, "Поведінкові аномалії", size=9, color=INK, bold=True))
    p.append(text(315, 260, "Масове скачування даних", size=9, color=MUTED))
    p.append(text(315, 278, "Швидкість запитів > 100/с", size=9, color="#0369a1"))


    # Фаза 3: Динамічний перерахунок ризику (PDP)
    p.append(rect(430, 40, 185, 270, fill="#fffbeb", stroke="#f59e0b", sw=1.5, rx=8))
    p.append(text(522, 65, "3. Обчислення довіри", size=11, color="#b45309", bold=True))
    p.append(text(522, 85, "Байєсів / Зважений аналіз", size=10, color=MUTED))

    p.append(rect(440, 105, 165, 60, fill="#ffffff", stroke="#fcd34d", sw=1, rx=4))
    p.append(text(522, 125, "Зважування факторів", size=9, color=INK, bold=True))
    p.append(text(522, 145, "Score = Σ(w_i · x_i)", size=9, color="#b45309", italic=True))

    p.append(rect(440, 175, 165, 60, fill="#ffffff", stroke="#fcd34d", sw=1, rx=4))
    p.append(text(522, 195, "Оцінка порогу ризику", size=9, color=INK, bold=True))
    p.append(text(522, 215, "Score впав з 95 до 42", size=9, color="#dc2626", bold=True))

    p.append(rect(440, 245, 165, 55, fill="#fee2e2", stroke="#ef4444", sw=1, rx=4))
    p.append(text(522, 265, "CAEP / SSF Подія", size=9, color="#991b1b", bold=True))
    p.append(text(522, 282, "Сповіщення всіх PEP точок", size=9, color="#991b1b"))


    # Фаза 4: Адаптивна реакція безпеки
    p.append(rect(640, 40, 175, 270, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=8))
    p.append(text(727, 65, "4. Адаптивна дія", size=11, color="#991b1b", bold=True))
    p.append(text(727, 85, "Автоматичне реагування", size=10, color=MUTED))

    p.append(rect(650, 105, 155, 55, fill="#ffffff", stroke="#fca5a5", sw=1, rx=4))
    p.append(text(727, 123, "Step-up MFA", size=10, color="#991b1b", bold=True))
    p.append(text(727, 142, "Запит повторної перевірки", size=9, color=MUTED))

    p.append(rect(650, 170, 155, 55, fill="#ffffff", stroke="#fca5a5", sw=1, rx=4))
    p.append(text(727, 188, "Звуження привілеїв", size=9, color=INK, bold=True))
    p.append(text(727, 208, "Лише читання публічних даних", size=9, color=MUTED))

    p.append(rect(650, 235, 155, 65, fill="#fee2e2", stroke="#dc2626", sw=1.2, rx=4))
    p.append(text(727, 255, "Негайний відклик", size=10, color="#991b1b", bold=True))
    p.append(text(727, 272, "Анулювання SVID / JWT токена", size=9, color=INK))
    p.append(text(727, 288, "Розірвання активної сесії", size=9, color="#991b1b", italic=True))


    # Стрілки між фазами
    p.append(arrow(200, 170, 220, 170, color=INK, sw=1.8))
    p.append(arrow(405, 170, 425, 170, color=INK, sw=1.8))
    p.append(arrow(615, 170, 635, 170, color=INK, sw=1.8))

    # Зворотний зв'язок (цикл)
    p.append(line(727, 310, 727, 340, color="#64748b", sw=1.5, dash="4,3"))
    p.append(line(727, 340, 112, 340, color="#64748b", sw=1.5, dash="4,3"))
    p.append(arrow(112, 340, 112, 315, color="#64748b", sw=1.5))
    p.append(text(420, 332, "Безперервний зворотний зв'язок та адаптація сесії", size=9, color=MUTED, bold=True))

    render(os.path.join(OUT, "continuous-adaptive-trust-lifecycle.svg"), W, H, *p,
           title="Цикл безперервної адаптивної оцінки довіри")


if __name__ == "__main__":
    fig_castle_moat_vs_zero_trust()
    fig_nist_zta_control_data_plane()
    fig_spiffe_workload_attestation_flow()
    fig_continuous_adaptive_trust_lifecycle()
    print("Figures generated successfully.")
