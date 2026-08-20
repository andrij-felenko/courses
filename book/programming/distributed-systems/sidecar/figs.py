# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def box(cx, cy, s, size=13, pad=9, **kw):
    frag, w, h = textbox(cx, cy, s, size=size, pad=pad, **kw)
    return frag


# ── Фігура 1: Анатомія контейнерів у спільному просторі імен Pod ──────────────
def fig_sidecar_pod_namespaces():
    W, H = 1000, 560
    frags = []

    # Заголовок зверху
    frags.append(text(500, 30, "Анатомія супутніх контейнерів у спільному просторі імен Pod", size=16, bold=True))

    # Межа Pod (спільний ізоляційний контекст)
    frags.append(rect(40, 55, 920, 480, fill="#fbfcfd", stroke=LINE, sw=1.8, rx=10))
    frags.append(text(70, 82, "Контейнерний Pod (Спільні простори імен ядра Linux)", size=13, bold=True, color=INK, anchor="start"))

    # Спільний Network Namespace (горизонтальна панель зверху)
    frags.append(rect(65, 100, 870, 85, fill="#eef4ff", stroke=NEG, sw=1.4, rx=6))
    frags.append(text(85, 122, "Спільний Network Namespace (Мережевий простір імен: lo = 127.0.0.1, спільний стек сокетів)", size=11, bold=True, color=NEG, anchor="start"))
    frags.append(box(270, 153, "Основний сокет (порт :8080)", size=10, fill="#ffffff", stroke=NEG, min_w=180))
    frags.append(box(720, 153, "Sidecar сокет (порти :15001 / :9090)", size=10, fill="#ffffff", stroke=NEG, min_w=220))
    frags.append(line(370, 153, 595, 153, color=NEG, sw=1.6, dash="3 3"))
    frags.append(text(485, 143, "lo / Unix Socket", size=9, bold=True, color=NEG))

    # Ліва колонка: Основний контейнер (Main Application)
    frags.append(rect(65, 205, 415, 220, fill="#ffffff", stroke="#d97706", sw=1.5, rx=8))
    frags.append(text(85, 230, "Основний контейнер (Main App)", size=13, bold=True, color="#b45309", anchor="start"))
    frags.append(box(270, 270, "Бізнес-логіка (Go / Java / Python)\nОбробка прикладних транзакцій", size=11, bold=True, fill="#fffbeb", stroke="#d97706", min_w=280))
    frags.append(box(270, 345, "Власна cgroup (CPU: 2 core, RAM: 4GB)\nІзольована коренева FS (rootfs)", size=10, fill="#fef3c7", stroke=MUTED, min_w=280))
    frags.append(box(270, 395, "Запис логів / запитів на спільний диск", size=10, fill="#ffffff", stroke=MUTED, min_w=280))

    # Права колонка: Допоміжний контейнер (Sidecar Container)
    frags.append(rect(520, 205, 415, 220, fill="#ffffff", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(540, 230, "Супутній контейнер (Sidecar Proxy / Agent)", size=13, bold=True, color=FIELD, anchor="start"))
    frags.append(box(725, 270, "Інфраструктурна функція (Envoy / Fluentbit)\nШифрування, метрики, збір логів", size=11, bold=True, fill="#ecfdf5", stroke=FIELD, min_w=280))
    frags.append(box(725, 345, "Власна cgroup (CPU: 0.5 core, RAM: 256MB)\nІзольована коренева FS (rootfs)", size=10, fill="#d1fae5", stroke=MUTED, min_w=280))
    frags.append(box(725, 395, "Вичитка логів / відправка назовні", size=10, fill="#ffffff", stroke=MUTED, min_w=280))

    # Спільний Volume (Mount Namespace / emptyDir / tmpfs)
    frags.append(rect(65, 445, 870, 75, fill="#f8fafc", stroke=MUTED, sw=1.4, rx=6))
    frags.append(text(85, 467, "Спільний том (Shared Volume: emptyDir / tmpfs memory / IPC Namespace)", size=11, bold=True, color=INK, anchor="start"))
    frags.append(box(270, 495, "Точка монтування: /var/log/app", size=10, fill="#ffffff", stroke=MUTED, min_w=220))
    frags.append(box(725, 495, "Точка монтування: /var/log/app (ReadOnly)", size=10, fill="#ffffff", stroke=MUTED, min_w=240))
    frags.append(line(390, 495, 595, 495, color=FIELD, sw=1.8))
    frags.append(text(495, 487, "Page Cache", size=9, bold=True, color=FIELD))

    # Зв'язки між контейнерами та спільним томом
    frags.append(arrow(270, 415, 270, 475, color="#d97706", sw=1.5))
    frags.append(arrow(725, 475, 725, 415, color=FIELD, sw=1.5))

    return render(os.path.join(IMG, 'sidecar-pod-namespaces.svg'), W, H, *frags)


# ── Фігура 2: Тріада шаблонів: Sidecar, Ambassador та Adapter ─────────────────
def fig_sidecar_ambassador_adapter_triad():
    W, H = 1000, 580
    frags = []

    frags.append(text(500, 28, "Тріада архітектурних шаблонів: Sidecar, Ambassador та Adapter", size=16, bold=True))

    # 1. Шаблон Sidecar (Зліва)
    frags.append(rect(30, 55, 300, 500, fill="#ffffff", stroke="#d97706", sw=1.6, rx=8))
    frags.append(text(180, 80, "1. SIDECAR (Помічник)", size=13, bold=True, color="#b45309"))
    frags.append(text(180, 100, "Розширення функціональності без змін", size=10, color=MUTED))
    
    frags.append(box(180, 150, "Основний застосунок\n(Пише логи у файл)", size=11, bold=True, fill="#fffbeb", stroke="#d97706", min_w=210))
    frags.append(arrow(180, 185, 180, 225, color="#d97706", sw=1.5))
    frags.append(text(180, 208, "emptyDir (/var/log)", size=9, color=MUTED))
    
    frags.append(box(180, 260, "Sidecar Container\n(Fluentbit / Log Agent)", size=11, bold=True, fill="#fef3c7", stroke="#d97706", min_w=210))
    frags.append(arrow(180, 295, 180, 335, color=FIELD, sw=1.5))
    frags.append(text(180, 318, "HTTPS / TLS Batch", size=9, color=FIELD))
    
    frags.append(box(180, 370, "Централізований кластер\n(Elasticsearch / Loki)", size=11, fill="#f8fafc", stroke=MUTED, min_w=210))
    frags.append(box(180, 480, "Ключова роль:\nПаралельне виконання задач:\nзбір логів, ротація сертифікатів,\nсинхронізація файлів конфігурації.", size=10, fill="#fffdfa", stroke="#fcd34d", min_w=260))

    # 2. Шаблон Ambassador (Посередині)
    frags.append(rect(350, 55, 300, 500, fill="#ffffff", stroke=NEG, sw=1.6, rx=8))
    frags.append(text(500, 80, "2. AMBASSADOR (Посол)", size=13, bold=True, color=NEG))
    frags.append(text(500, 100, "Проксування вихідного трафіку", size=10, color=MUTED))

    frags.append(box(500, 150, "Основний застосунок\n(Клієнт HTTP :5000)", size=11, bold=True, fill="#eff6ff", stroke=NEG, min_w=210))
    frags.append(arrow(500, 185, 500, 225, color=NEG, sw=1.5))
    frags.append(text(500, 208, "127.0.0.1:5000 (lo)", size=9, color=NEG))

    frags.append(box(500, 260, "Ambassador Proxy\n(Envoy / gRPC Bridge)\nРетраї, Discovery, mTLS", size=11, bold=True, fill="#dbeafe", stroke=NEG, min_w=210))
    frags.append(arrow(500, 295, 500, 335, color=FIELD, sw=1.5))
    frags.append(text(500, 318, "mTLS / Sharded RPC", size=9, color=FIELD))

    frags.append(box(500, 370, "Зовнішній шар сервісів\n(Шардована БД / API)", size=11, fill="#f8fafc", stroke=MUTED, min_w=210))
    frags.append(box(500, 480, "Ключова роль:\nПриховує складність зовнішньої\nмережі: роутинг, шардування,\nавтентифікація, розрив ланцюгів.", size=10, fill="#f0f7ff", stroke="#93c5fd", min_w=260))

    # 3. Шаблон Adapter (Справа)
    frags.append(rect(670, 55, 300, 500, fill="#ffffff", stroke=FIELD, sw=1.6, rx=8))
    frags.append(text(820, 80, "3. ADAPTER (Адаптер)", size=13, bold=True, color=FIELD))
    frags.append(text(820, 100, "Стандартизація вхідного інтерфейсу", size=10, color=MUTED))

    frags.append(box(820, 150, "Сервер моніторингу\n(Prometheus Scraper)", size=11, fill="#f8fafc", stroke=MUTED, min_w=210))
    frags.append(arrow(820, 185, 820, 225, color=FIELD, sw=1.5))
    frags.append(text(820, 208, "GET /metrics (OpenMetrics)", size=9, color=FIELD))

    frags.append(box(820, 260, "Adapter Container\n(JMX / Status Exporter)\nТрансляція у стандартний формат", size=11, bold=True, fill="#d1fae5", stroke=FIELD, min_w=210))
    frags.append(arrow(820, 295, 820, 335, color=FIELD, sw=1.5))
    frags.append(text(820, 318, "lo: JMX / /custom_stat", size=9, color=MUTED))

    frags.append(box(820, 370, "Legacy / Нетиповий сервіс\n(Внутрішній бінарний формат)", size=11, bold=True, fill="#ecfdf5", stroke=FIELD, min_w=210))
    frags.append(box(820, 480, "Ключова роль:\nПриводить різнорідні інтерфейси\nдо єдиного корпоративного стандарту\nбез модифікації самого коду.", size=10, fill="#f2fbf6", stroke="#86efac", min_w=260))

    return render(os.path.join(IMG, 'sidecar-ambassador-adapter-triad.svg'), W, H, *frags)


# ── Фігура 3: Гонка життєвого циклу під час зупинки Pod ──────────────────────
def fig_sidecar_lifecycle_race():
    W, H = 1000, 520
    frags = []

    frags.append(text(500, 28, "Координація зупинки Pod: гонка сигналів SIGTERM та її усунення", size=16, bold=True))

    # Ліва половина: Некоординована зупинка (Аварійний сценарій)
    frags.append(rect(40, 55, 435, 440, fill="#fffaf9", stroke=POS, sw=1.5, rx=8))
    frags.append(text(257, 80, "Дефект: Одночасний SIGTERM (Без координації)", size=12, bold=True, color=POS))

    # Таймлайн часу
    frags.append(line(80, 110, 80, 430, color=MUTED, sw=1.5))
    frags.append(text(80, 105, "t = 0", size=10, color=MUTED))
    frags.append(text(80, 445, "Час", size=10, bold=True, color=MUTED))

    frags.append(box(270, 130, "Kubelet надсилає SIGTERM усім контейнерам", size=10, fill="#ffffff", stroke=POS, min_w=290))
    
    # Sidecar помирає швидко
    frags.append(box(270, 200, "Sidecar (Envoy / Egress Proxy)\nМиттєво закриває сокети та завершується", size=10, bold=True, fill="#fee2e2", stroke=POS, min_w=290))
    frags.append(line(80, 200, 120, 200, color=POS, sw=1.2))

    # Застосунок пробує виконати запити
    frags.append(box(270, 280, "Main App (Триває плавний drain транзакцій)\nСпроба відправити фінальний HTTP-запит", size=10, bold=True, fill="#fffbeb", stroke="#d97706", min_w=290))
    frags.append(line(80, 280, 120, 280, color="#d97706", sw=1.2))

    # Помилка з'єднання
    frags.append(box(270, 360, "ПОМИЛКА: Connection Refused на 127.0.0.1\nВихідні запити та логи втрачено!", size=10, bold=True, fill="#fef2f2", stroke=POS, min_w=290))
    frags.append(arrow(270, 315, 270, 335, color=POS, sw=1.5))

    frags.append(box(270, 455, "Результат: 502/503 помилки у клієнтів,\nнезбережені критичні транзакції.", size=10, fill="#ffffff", stroke=POS, min_w=310))

    # Права половина: Координована зупинка (preStop / Native Sidecar)
    frags.append(rect(525, 55, 435, 440, fill="#f7fbf8", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(742, 80, "Рішення: Впорядковане завершення (preStop / Native)", size=12, bold=True, color=FIELD))

    # Таймлайн часу
    frags.append(line(565, 110, 565, 430, color=MUTED, sw=1.5))
    frags.append(text(565, 105, "t = 0", size=10, color=MUTED))
    frags.append(text(565, 445, "Час", size=10, bold=True, color=MUTED))

    frags.append(box(755, 130, "Kubelet ініціює зупинку Pod", size=10, fill="#ffffff", stroke=FIELD, min_w=290))

    # Main App отримує сигнал першим
    frags.append(box(755, 200, "Main App отримує SIGTERM:\nПрипиняє прийом нових і завершує in-flight", size=10, bold=True, fill="#fffbeb", stroke="#d97706", min_w=290))
    frags.append(line(565, 200, 605, 200, color="#d97706", sw=1.2))

    # Sidecar тримає preStop паузу
    frags.append(box(755, 280, "Sidecar утримує preStop hook / чекає drain:\nКанал зв'язку та збір логів активні", size=10, bold=True, fill="#d1fae5", stroke=FIELD, min_w=290))
    frags.append(line(565, 280, 605, 280, color=FIELD, sw=1.2))

    # Успішне завершення
    frags.append(box(755, 360, "Main App завершується (код 0)\nSidecar скидає фінальний буфер і зупиняється", size=10, bold=True, fill="#ecfdf5", stroke=FIELD, min_w=290))
    frags.append(arrow(755, 235, 755, 255, color=FIELD, sw=1.5))
    frags.append(arrow(755, 315, 755, 335, color=FIELD, sw=1.5))

    frags.append(box(755, 455, "Результат: Нуль втрачених запитів,\nгарантована цілісність даних і логів.", size=10, fill="#ffffff", stroke=FIELD, min_w=310))

    return render(os.path.join(IMG, 'sidecar-lifecycle-race.svg'), W, H, *frags)


# ── Фігура 4: Порівняння архітектур: SDK vs Sidecar vs DaemonSet ───────────────
def fig_sidecar_vs_daemonset_tradeoffs():
    W, H = 1000, 500
    frags = []

    frags.append(text(500, 28, "Архітектурні компроміси: Бібліотека (SDK) vs Sidecar vs DaemonSet", size=16, bold=True))

    # Колонка 1: In-Process SDK
    frags.append(rect(40, 55, 290, 420, fill="#ffffff", stroke=MUTED, sw=1.5, rx=8))
    frags.append(text(185, 80, "In-Process SDK (Бібліотека)", size=12, bold=True, color=INK))
    frags.append(box(185, 125, "Код всередині процесу\n(Спільна пам'ять, нуль сокетів)", size=10, fill="#f8fafc", stroke=MUTED, min_w=250))
    
    frags.append(box(185, 195, "Плюси:\n+ Нульова затримка мережі\n+ Відсутність витрат на IPC\n+ Прямий доступ до пам'яті", size=10, fill="#ecfdf5", stroke=FIELD, min_w=250))
    frags.append(box(185, 305, "Мінуси:\n- Поліглотний податок (N мов)\n- Спільний blast radius падінь\n- Оновлення вимагає редеплою\n- Складність конфігурації", size=10, fill="#fff1f2", stroke=POS, min_w=250))
    frags.append(box(185, 415, "Оптимально:\nУльтранизька затримка (<100мкс),\nоднорідний мономовний стек.", size=10, fill="#f1f5f9", stroke=MUTED, min_w=250))

    # Колонка 2: Sidecar (Per-Pod)
    frags.append(rect(355, 55, 290, 420, fill="#ffffff", stroke=NEG, sw=1.8, rx=8))
    frags.append(text(500, 80, "Sidecar (На кожен Pod)", size=12, bold=True, color=NEG))
    frags.append(box(500, 125, "Окремий процес у Pod\n(Спільний netns / loopback)", size=10, fill="#eff6ff", stroke=NEG, min_w=250))

    frags.append(box(500, 195, "Плюси:\n+ Повна мовна незалежність\n+ Ізоляція cgroups (CPU/RAM)\n+ Незалежний релізний цикл\n+ Динамічний mTLS та інжекція", size=10, fill="#ecfdf5", stroke=FIELD, min_w=250))
    frags.append(box(500, 305, "Мінуси:\n- Витрати пам'яті (RAM × N Pods)\n- Затримка loopback (~1-2мс)\n- Складність зупинки / запуску\n- Вичерпання TIME_WAIT портів", size=10, fill="#fff1f2", stroke=POS, min_w=250))
    frags.append(box(500, 415, "Оптимально:\nМікросервіси, Service Mesh,\nротація mTLS, збір телеметрії.", size=10, fill="#eff6ff", stroke=NEG, min_w=250))

    # Колонка 3: DaemonSet (Per-Node)
    frags.append(rect(670, 55, 290, 420, fill="#ffffff", stroke="#d97706", sw=1.5, rx=8))
    frags.append(text(815, 80, "DaemonSet (Один на Ноду)", size=12, bold=True, color="#b45309"))
    frags.append(box(815, 125, "Один агент на фізичний вузол\n(Обслуговує всі Pods вузла)", size=10, fill="#fffbeb", stroke="#d97706", min_w=250))

    frags.append(box(815, 195, "Плюси:\n+ Мінімальний оверхед по RAM\n+ Фіксована кількість процесів\n+ Спільні ресурси на ноді\n+ Простота оновлення агента", size=10, fill="#ecfdf5", stroke=FIELD, min_w=250))
    frags.append(box(815, 305, "Мінуси:\n- Слабша ізоляція мультиаренди\n- Немає унікального mTLS ключа\n- Падіння вузла вражає всі Pods\n- Складніший роутинг через Unix sock", size=10, fill="#fff1f2", stroke=POS, min_w=250))
    frags.append(box(815, 415, "Оптимально:\nЗбір системних метрик (Node Exporter),\nхостові логи, eBPF моніторинг.", size=10, fill="#fffbeb", stroke="#d97706", min_w=250))

    return render(os.path.join(IMG, 'sidecar-vs-daemonset-tradeoffs.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_sidecar_pod_namespaces()
    fig_sidecar_ambassador_adapter_triad()
    fig_sidecar_lifecycle_race()
    fig_sidecar_vs_daemonset_tradeoffs()
    print("All figures generated successfully.")
