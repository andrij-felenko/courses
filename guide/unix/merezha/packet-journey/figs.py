# -*- coding: utf-8 -*-
import sys, os

# Додаємо scripts/ до шляху пошуку модулів
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
GREY_FILL = "#f4f6f8"
DARK_LINE = "#2c3e50"


# ── 1. Механізм кільцевого буфера RX, DMA та опитування NAPI ────────────────
def fig_rx_ring_dma_napi():
    W, H = 1240, 720
    p = []

    p.append(text(W / 2, 38, "Апаратне отримання пакета: кільцевий буфер RX, DMA та цикл NAPI", size=18, bold=True))

    # Ліва колонка: Апаратний мережевий адаптер (NIC)
    nx, ny, nw, nh = 40, 65, 340, 625
    p.append(rect(nx, ny, nw, nh, fill="#ffffff", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(nx + nw / 2, ny + 30, "Мережевий адаптер (NIC)", size=16, bold=True, color=INK))

    p.append(fitbox(nx + 20, ny + 50, 300, 60,
                    "Фізичний кабель / Оптика (PHY)\nКадри надходять зі швидкістю лінії (Line Rate)",
                    size=12, fill=WARM_FILL, stroke=LINE, sw=1.2))

    p.append(fitbox(nx + 20, ny + 120, 300, 65,
                    "RX FIFO та MAC-контролер\nПеревірка CRC (FCS), фільтрація MAC-адрес,\nрозподіл черг через RSS",
                    size=12, fill=WARM_FILL, stroke=LINE, sw=1.2))

    p.append(fitbox(nx + 20, ny + 195, 300, 150,
                    "Кільце дескрипторів RX (RX Ring)\n"
                    "• Head: позиція запису заліза\n"
                    "• Tail: межа виділених буферів\n"
                    "• Дескриптор містить фізичну адресу RAM,\n"
                    "  довжину кадру та прапорці контрольної суми\n"
                    "• Залізо перевіряє L3/L4 Checksum Offload",
                    size=12, fill=BLUE_FILL, stroke=LINE, sw=1.2))

    p.append(fitbox(nx + 20, ny + 355, 300, 130,
                    "Контролер переривань (MSI-X)\n"
                    "1. Запис кадру в RAM через PCIe DMA\n"
                    "2. Генерація переривання MSI-X на CPU\n"
                    "3. Тимчасове маскування ліній переривання",
                    size=12, fill=RED_FILL, stroke=POS, sw=1.2))

    p.append(fitbox(nx + 20, ny + 495, 300, 110,
                    "Апаратний DMA Master\n"
                    "Прямий запис пакета в пам'ять хоста без участі процесора",
                    size=12, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=1.5))

    # Середня колонка: Системна пам'ять RAM (DMA Буфери)
    mx, my, mw, mh = 420, 65, 380, 625
    p.append(rect(mx, my, mw, mh, fill="#ffffff", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(mx + mw / 2, my + 30, "Оперативна пам'ять хоста (RAM)", size=16, bold=True, color=INK))

    p.append(fitbox(mx + 20, my + 50, 340, 65,
                    "Буфери DMA (dma_alloc_coherent)\n"
                    "Виділені сторінки пам'яті для прямого доступу адаптера.\n"
                    "Фізичні адреси передані в дескриптори RX Ring.",
                    size=12, fill=BLUE_FILL, stroke=LINE, sw=1.2))

    p.append(fitbox(mx + 20, my + 125, 340, 85,
                    "Кадр Ethernet у буфері DMA\n"
                    "[ MAC Заголовок | IP Заголовок | TCP/UDP | Дані ]\n"
                    "Пакет лежить у пам'яті до того, як процесор починає\n"
                    "його опрацювання.",
                    size=12, fill=GREEN_FILL, stroke=FIELD, sw=1.2))

    p.append(fitbox(mx + 20, my + 220, 340, 140,
                    "Аллокація struct sk_buff (SKB)\n"
                    "Драйвер виділяє метаструктуру sk_buff або\n"
                    "використовує механізм Page Pool:\n"
                    "• skb->head, skb->data, skb->tail, skb->end\n"
                    "• Прив'язка до мережевого пристрою net_device\n"
                    "• Встановлення протоколу через eth_type_trans()",
                    size=12, fill=WARM_FILL, stroke=LINE, sw=1.2))

    p.append(fitbox(mx + 20, my + 370, 340, 235,
                    "Оновлення кільця RX та поповнення буферів\n"
                    "Після того як skb сформовано:\n"
                    "1. Драйвер виділяє новий вільний буфер пам'яті\n"
                    "2. Записує новий DMA-дескриптор у кільце RX\n"
                    "3. Зсуває покажчик Tail у регістрі адаптера (Doorbell)\n"
                    "4. Адаптер знову готовий приймати нові кадри",
                    size=12, fill=GREY_FILL, stroke=LINE, sw=1.2))

    # Права колонка: Процесор та підсистема NAPI в ядрі
    rx, ry, rw, rh = 840, 65, 360, 625
    p.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(rx + rw / 2, ry + 30, "Ядро та процесор (CPU SoftIRQ)", size=16, bold=True, color=INK))

    p.append(fitbox(rx + 20, ry + 50, 320, 80,
                    "1. Апаратне переривання (HardIRQ)\n"
                    "• Обробник драйвера вимикає переривання черги\n"
                    "• Викликає napi_schedule(&adapter->napi)\n"
                    "• Додає napi_struct до poll_list поточного CPU",
                    size=12, fill=RED_FILL, stroke=POS, sw=1.2))

    p.append(fitbox(rx + 20, ry + 140, 320, 75,
                    "2. Активація м'якого переривання\n"
                    "• raise_softirq_irqoff(NET_RX_SOFTIRQ)\n"
                    "• Апаратний обробник завершує роботу (< 1 мкс)\n"
                    "• CPU планує виконання функції net_rx_action()",
                    size=12, fill=WARM_FILL, stroke=LINE, sw=1.2))

    p.append(fitbox(rx + 20, ry + 225, 320, 135,
                    "3. Цикл опитування NAPI (napi->poll())\n"
                    "• net_rx_action() викликає функцію опитування\n"
                    "• Опрацювання пакетів партіями до вичерпання budget (300)\n"
                    "• Передача в стек: napi_gro_receive(skb)\n"
                    "• Запобігання блокуванню CPU іншими задачами",
                    size=12, fill=GREEN_FILL, stroke=FIELD, sw=1.2))

    p.append(fitbox(rx + 20, ry + 370, 320, 235,
                    "4. Завершення опитування NAPI\n"
                    "• Якщо черга порожня (пакетів < budget):\n"
                    "  napi_complete_done() -> вилучення з poll_list ->\n"
                    "  увімкнення апаратних переривань адаптера\n"
                    "• Якщо черга не порожня (ліміт budget вичерпано):\n"
                    "  napi лишається в списку, SoftIRQ поступається CPU,\n"
                    "  лічильник time_squeeze у softnet_stat інкрементується",
                    size=12, fill=BLUE_FILL, stroke=LINE, sw=1.2))

    # Стрілки між сусідніми колонками
    p.append(arrow(nx + nw, 200, mx, 200, color=FIELD, sw=2.0))
    p.append(arrow(mx + mw, 200, rx, 200, color=POS, sw=2.0))
    p.append(arrow(rx, 400, mx + mw, 400, color=LINE, sw=1.8))

    render(os.path.join(IMG, 'rx-ring-dma-napi.svg'), W, H, *p)


# ── 2. Анатомія struct sk_buff у пам'яті ────────────────────────────────────
def fig_skb_memory_layout():
    W, H = 1240, 660
    p = []

    p.append(text(W / 2, 38, "Анатомія struct sk_buff: керування заголовками без копіювання пам'яті", size=18, bold=True))

    # Верхня частина: Головна структура керування struct sk_buff
    p.append(rect(60, 65, 1120, 180, fill="#ffffff", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(620, 95, "Метаструктура struct sk_buff (керівні покажчики та службові поля)", size=16, bold=True, color=INK))

    p.append(fitbox(80, 115, 250, 110,
                    "Покажчики меж буфера:\n"
                    "• sk_buff_data_t head\n"
                    "• sk_buff_data_t data\n"
                    "• sk_buff_data_t tail\n"
                    "• sk_buff_data_t end",
                    size=12, fill=BLUE_FILL, stroke=LINE, sw=1.2))

    p.append(fitbox(350, 115, 260, 110,
                    "Розміри та довжини:\n"
                    "• unsigned int len (повна довжина)\n"
                    "• unsigned int data_len (розмір у фргаментах)\n"
                    "• unsigned int truesize (виділена RAM)\n"
                    "• unsigned int hdr_len",
                    size=12, fill=GREEN_FILL, stroke=FIELD, sw=1.2))

    p.append(fitbox(630, 115, 260, 110,
                    "Мережевий контекст:\n"
                    "• struct net_device *dev\n"
                    "• struct sock *sk\n"
                    "• struct dst_entry *_skb_refdst\n"
                    "• __be16 protocol (0x0800, 0x86dd)",
                    size=12, fill=WARM_FILL, stroke=LINE, sw=1.2))

    p.append(fitbox(910, 115, 250, 110,
                    "Зсуви рівнів (Offsets):\n"
                    "• __u16 mac_header\n"
                    "• __u16 network_header\n"
                    "• __u16 transport_header\n"
                    "• __u8 cb[48] (Control Block)",
                    size=12, fill=GREY_FILL, stroke=LINE, sw=1.2))

    # Середня частина: Лінійний буфер пам'яті
    p.append(rect(60, 275, 1120, 175, fill="#ffffff", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(620, 305, "Неперервний лінійний буфер даних (Allocated Memory Block)", size=16, bold=True, color=INK))

    # Ділянки лінійного буфера
    p.append(rect(90, 330, 160, 75, fill=GREY_FILL, stroke=LINE, sw=1.2))
    p.append(text(170, 360, "Запас нагорі (Headroom)", size=12, bold=True))
    p.append(text(170, 385, "skb_reserve() / skb_push()", size=11, color=MUTED))

    p.append(rect(250, 330, 180, 75, fill=WARM_FILL, stroke=LINE, sw=1.2))
    p.append(text(340, 360, "L2 Ethernet Заголовок", size=12, bold=True))
    p.append(text(340, 385, "14 байтів (MAC Src/Dst, Type)", size=11, color=MUTED))

    p.append(rect(430, 330, 180, 75, fill=BLUE_FILL, stroke=LINE, sw=1.2))
    p.append(text(520, 360, "L3 IP Заголовок", size=12, bold=True))
    p.append(text(520, 385, "20 байтів (IP Src/Dst, TTL)", size=11, color=MUTED))

    p.append(rect(610, 330, 180, 75, fill=GREEN_FILL, stroke=FIELD, sw=1.2))
    p.append(text(700, 360, "L4 TCP/UDP Заголовок", size=12, bold=True))
    p.append(text(700, 385, "20+ байтів (Ports, Seq, Ack)", size=11, color=MUTED))

    p.append(rect(790, 330, 200, 75, fill="#ffffff", stroke=LINE, sw=1.2))
    p.append(text(890, 360, "Корисні дані (Payload)", size=12, bold=True))
    p.append(text(890, 385, "HTTP, RPC, файл тощо", size=11, color=MUTED))

    p.append(rect(990, 330, 160, 75, fill=GREY_FILL, stroke=LINE, sw=1.2))
    p.append(text(1070, 360, "Запас унизу (Tailroom)", size=12, bold=True))
    p.append(text(1070, 385, "skb_put() для дозапису", size=11, color=MUTED))

    # Покажчики head, data, tail, end
    p.append(text(90, 425, "▲ head", size=13, bold=True, color=POS))
    p.append(text(250, 425, "▲ data (поточний шар)", size=13, bold=True, color=NEG))
    p.append(text(990, 425, "▲ tail", size=13, bold=True, color=FIELD))
    p.append(text(1150, 425, "▲ end", size=13, bold=True, color=POS))

    # Нижня частина: Нелінійні фрагменти (skb_shared_info) та операції очищення
    p.append(rect(60, 470, 1120, 165, fill="#ffffff", stroke=MUTED, sw=1.5, rx=8))

    p.append(fitbox(80, 490, 520, 125,
                    "Механізм «Зняття заголовків» (skb_pull):\n"
                    "• L2 обробка: data вказує на початок Ethernet-кадру\n"
                    "• Зняття L2: skb_pull(skb, 14) -> покажчик data зсувається вперед на 14 B\n"
                    "• L3 обробка: data вказує на початок IP-пакета (без копіювання пам'яті!)\n"
                    "• Зняття L3: skb_pull(skb, iph_len) -> data вказує на TCP-заголовок",
                    size=12, fill=GREEN_FILL, stroke=FIELD, sw=1.2))

    p.append(fitbox(640, 490, 520, 125,
                    "Нелінійні фрагменти сторінок (skb_shared_info):\n"
                    "• Розміщується в кінці виділеного блоку за покажчиком end\n"
                    "• skb_shinfo(skb)->nr_frags (кількість сторінок skb_frag_t)\n"
                    "• Дозволяє приймати Jumbo-кадри та TCP Superpackets (GRO/GSO)\n"
                    "• Нульове копіювання при передачі великих файлів (Zero-Copy Sendfile)",
                    size=12, fill=BLUE_FILL, stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'skb-memory-layout.svg'), W, H, *p)


# ── 3. Повний наскрізний конвеєр отримання пакета (Ingress Pipeline) ────────
def fig_packet_journey_ingress_pipeline():
    W, H = 1240, 820
    p = []

    p.append(text(W / 2, 35, "Наскрізний шлях вхідного пакета крізь ядро Linux (Ingress Pipeline)", size=18, bold=True))

    stages = [
        ("1. Апаратний рівень (NIC & DMA)",
         "Адаптер отримує кадр з лінії -> перевіряє FCS -> здійснює DMA запис у системну RAM -> генерує переривання MSI-X.",
         RED_FILL, POS),
        ("2. Ранній фільтр XDP (eXpress Data Path)",
         "Драйвер запускає eBPF програму XDP ДО виділення sk_buff:\n• XDP_DROP (миттєве скидання) • XDP_TX (зворотне відбиття) • XDP_REDIRECT (AF_XDP) • XDP_PASS.",
         WARM_FILL, LINE),
        ("3. Драйвер і NAPI Poll (SoftIRQ)",
         "Обробник HardIRQ маскує переривання і викликає napi_schedule(). У SoftIRQ net_rx_action() опитує кільце RX пакетами до вичерпання budget.",
         BLUE_FILL, LINE),
        ("4. Агрегація GRO та вхід у стек (__netif_receive_skb_core)",
         "Generic Receive Offload склеює TCP сегменти -> AF_PACKET (tcpdump/pcap) перехоплює копію -> TC Ingress (clsact / eBPF фільтри та політики).",
         GREEN_FILL, FIELD),
        ("5. Netfilter PREROUTING та маршрутизація FIB",
         "ip_rcv() валідує IP заголовок -> Netfilter Hook PREROUTING (conntrack, mangle, nat) -> Пошук маршруту у FIB (fib_lookup()): локальна доставка чи форвардинг.",
         BLUE_FILL, LINE),
        ("6. Netfilter INPUT та демультиплексування L4",
         "ip_local_deliver() збирає IP фрагменти (defrag) -> Netfilter Hook INPUT (таблиця filter) -> виклик обробника протоколу inet_protos[protocol] (tcp_v4_rcv / udp_rcv).",
         WARM_FILL, LINE),
        ("7. Транспортний рівень L4 (TCP / UDP State Machine)",
         "Пошук struct sock у хеш-таблиці inet_hashinfo за 4-tuple -> перевірка контрольної суми, Sequence/ACK, ковзного вікна -> генерація ACK -> черга sk_receive_queue.",
         GREEN_FILL, FIELD),
        ("8. Пробудження процесу та системний виклик read()",
         "sk->sk_data_ready() сповіщає чергу sk_wq -> пробудження epoll_wait() -> процес викликає recv() / read() -> копіювання даних у буфер процесу (copy_to_user()).",
         BLUE_FILL, LINE),
    ]

    sy = 65
    box_h = 78
    gap = 14

    for i, (title, desc, fill_c, stroke_c) in enumerate(stages):
        y = sy + i * (box_h + gap)
        p.append(rect(140, y, 960, box_h, fill=fill_c, stroke=stroke_c, sw=1.5, rx=8))
        p.append(text(160, y + 25, title, size=14, bold=True, color=INK, anchor="start"))
        p.append(fitbox(160, y + 32, 920, 42, desc, size=11, fill="none", stroke="none"))

        if i < len(stages) - 1:
            p.append(arrow(620, y + box_h, 620, y + box_h + gap, color=LINE, sw=1.8))

    render(os.path.join(IMG, 'packet-journey-ingress-pipeline.svg'), W, H, *p)


# ── 4. Зворотний шлях: передача пакета назовні (TX Egress Path) ──────────────
def fig_egress_packet_path():
    W, H = 1240, 720
    p = []

    p.append(text(W / 2, 38, "Зворотний шлях пакета: передача з процесу в мережевий дріт (TX Egress)", size=18, bold=True))

    steps = [
        ("Крок 1: Системний виклик користувача",
         "write(fd, buf, len) / sendmsg()\n"
         "Процес передає буфер у сокет. Ядро виділяє пам'ять під struct sk_buff з урахуванням квоти сокета wmem_alloc.\n"
         "Дані копіюються з простору користувача в лінійні або сторінкові буфери ядра через copy_from_user().",
         BLUE_FILL),
        ("Крок 2: Транспортний рівень L4 (TCP Segmentation & Congestion)",
         "tcp_sendmsg() / tcp_write_xmit()\n"
         "Формування TCP заголовка: порти, номери послідовності (SEQ), прапорці (PSH, ACK). Врахування алгоритмів керування\n"
         "перевантаженням (BBR, CUBIC), ковзного вікна відправника, таймера повторної передачі (RTO) та алгоритму Nagle.",
         GREEN_FILL),
        ("Крок 3: Мережевий рівень L3 та Netfilter OUTPUT",
         "ip_queue_xmit() -> NF_INET_LOCAL_OUT -> Пошук маршруту -> NF_INET_POST_ROUTING\n"
         "Побудова IPv4 заголовка (Src/Dst IP, TTL, Checksum). Проходження хука OUTPUT, вибір вихідного інтерфейсу у FIB,\n"
         "проходження хука POSTROUTING (трансляція SNAT / MASQUERADE) та резолюція L2 адреси через ARP/сусідів (Neighbor Table).",
         WARM_FILL),
        ("Крок 4: Диспетчеризація черг трафіку L2 (TC & Qdisc)",
         "dev_queue_xmit() -> __dev_xmit_skb() -> qdisc_run()\n"
         "Пакет потрапляє в чергу планувальника інтерфейсу (Qdisc: fq, cake, pfifo_fast). eBPF фільтри на TC Egress можуть змінити\n"
         "або перенаправити пакет. Планувальник сортує пакети згідно з пріоритетами, квотами пропускної здатності або FQ-лімітами.",
         GREY_FILL),
        ("Крок 5: Драйвер, кільце TX Ring та відправка залізом",
         "ndo_start_xmit() -> DMA Mapping -> PCI Doorbell -> PHY Wire\n"
         "Драйвер відображає skb у фізичну пам'ять (dma_map_single), заповнює дескриптор у кільці TX Ring і смикає Doorbell регістр.\n"
         "Адаптер вичитує дані через DMA, додає L2 Preamble/FCS і відправляє в лінію. Завершення генерує TX IRQ / NET_TX_SOFTIRQ для звільнення skb.",
         RED_FILL),
    ]

    sy = 70
    box_h = 108
    gap = 18

    for i, (title, desc, fill_c) in enumerate(steps):
        y = sy + i * (box_h + gap)
        p.append(rect(80, y, 1080, box_h, fill=fill_c, stroke=LINE, sw=1.5, rx=8))
        p.append(text(105, y + 26, title, size=14, bold=True, color=INK, anchor="start"))
        p.append(fitbox(105, y + 34, 1030, 64, desc, size=12, fill="none", stroke="none"))

        if i < len(steps) - 1:
            p.append(arrow(620, y + box_h, 620, y + box_h + gap, color=LINE, sw=1.8))

    render(os.path.join(IMG, 'egress-packet-path.svg'), W, H, *p)


if __name__ == '__main__':
    fig_rx_ring_dma_napi()
    fig_skb_memory_layout()
    fig_packet_journey_ingress_pipeline()
    fig_egress_packet_path()
    print("Всі фігури успішно скомпільовано в img/")
