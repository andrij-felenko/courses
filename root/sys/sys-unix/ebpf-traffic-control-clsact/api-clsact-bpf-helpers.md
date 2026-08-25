# 📋 Інтерфейс та хепери eBPF Traffic Control (clsact)

Цей довідник містить повну технічну специфікацію структури контексту `struct __sk_buff`, коди повернення дій `TC_ACT_*`, сигнатури та правила використання допоміжних функцій ядра (eBPF helpers), а також функціональний API бібліотеки `libbpf` для керування хуками `clsact` із користувацького простору.

## 1. Контекст виконання eBPF: `struct __sk_buff`

Під час виклику програми eBPF типу `BPF_PROG_TYPE_SCHED_CLS` у регістр ЦП `R1` передається вказівник на публічну структуру контексту `struct __sk_buff`. Вона є абстракцією ядра над внутрішньою громіздкою структурою `struct sk_buff` (socket buffer).

```c
struct __sk_buff {
    __u32 len;
    __u32 pkt_type;
    __u32 mark;
    __u32 queue_mapping;
    __u32 protocol;
    __u32 vlan_present;
    __u32 vlan_tci;
    __u32 vlan_proto;
    __u32 priority;
    __u32 ingress_ifindex;
    __u32 ifindex;
    __u32 tc_index;
    __u32 cb[5];
    __u32 hash;
    __u32 tc_classid;
    __u32 data;
    __u32 data_end;
    __u32 napi_id;
    __u32 family;
    __u32 remote_ip4;
    __u32 local_ip4;
    __u32 remote_ip6[4];
    __u32 local_ip6[4];
    __u32 remote_port;
    __u32 local_port;
    __u32 data_meta;
    __bpf_md_ptr(struct bpf_sock *, sk);
    __u32 tstamp;
    __u32 wire_len;
    __u32 gso_segs;
    __bpf_md_ptr(struct bpf_sock *, skb_gso_sk);
    __u32 gso_size;
    __u32 tstamp_type;
};
```

### Докладний розбір усіх полів структури `struct __sk_buff`:

- **`data` (`__u32`, лише читання):** 32-бітний зсув у пам'яті, що вказує на початок лінійних даних пакета (за замовчуванням — заголовок L2 Ethernet). Для прямого роздереферення вказівник зводиться до типу `(void *)(long)skb->data`.
- **`data_end` (`__u32`, лише читання):** 32-бітний зсув у пам'яті, що вказує на праворуч від межі лінійної області даних пакета. Будь-яке роздереферення вказівника на дані вимагає попереднього порівняння `(data + offset) <= data_end`.
- **`data_meta` (`__u32`, читання/запис у метаданих):** Початок спеціальної області метаданих, що розміщується у буфері перед `data` (headroom). Використовується для обміну користувацькими структурами між XDP та TC eBPF програмами.
- **`len` (`__u32`, лише читання):** Повна довжина пакета в байтах, включаючи лінійні та нелінійні (paged) фрагменти.
- **`pkt_type` (`__u32`, лише читання):** Тип призначення адреси пакета на канальному рівні. Основні значення: `PACKET_HOST` (для даного хоста), `PACKET_BROADCAST` (широковещательный), `PACKET_MULTICAST` (багатоадресний), `PACKET_OTHERHOST` (прослуховування в режимі promiscuous).
- **`mark` (`__u32`, читання і запис):** Поле системної мітки пакета (`skb->mark`). Використовується для обміну мітками між eBPF, Netfilter (iptables `-j MARK`), IPSec XFRM та таблицями маршрутизації policy routing (`ip rule add fwmark`).
- **`priority` (`__u32`, читання і запис):** Пріоритет Quality of Service (QoS) пакета, який враховується класичними вихідними дисциплінами черг (наприклад, `prio` чи `htb`).
- **`ifindex` (`__u32`, лише читання):** Системний індекс мережевого інтерфейсу Linux, на якому обробляється пакет.
- **`ingress_ifindex` (`__u32`, лише читання):** Початковий індекс мережевого інтерфейсу, через який пакет першопочатково потрапив у ядро.
- **`cb[5]` (`__u32[5]`, читання і запис):** Буфер контролю (Control Buffer), що надає 20 байтів вільного місця у пам'яті `skb->cb`. eBPF програма може використовувати `cb[]` для збереження проміжного стану між різними хуками під час проходження пакета крізь стек.
- **`hash` (`__u32`, читання і запис):** Кешоване значення 4-кортежного хешу L3/L4 (`skb->hash`), яке використовується для балансування RSS та ECMP.
- **`vlan_present`, `vlan_tci`, `vlan_proto` (`__u32`):** Поля апаратного знімання VLAN-тегів (VLAN offloading). Якщо `vlan_present == 1`, тег 802.1Q вилучено з кадра драйвером і збережено у `vlan_tci`.
- **`sk` (`struct bpf_sock *`, лише читання):** Вказівник на сокет ядра, до якого прив'язаний пакет (доступний на вихідному шляху `egress` або після виклику `bpf_skc_lookup_tcp`).
- **`remote_ip4`, `local_ip4` (`__u32`, лише читання):** IP-адреси у мережевому порядку байтів для швидкого доступу без розпарсування заголовків.
- **`remote_port`, `local_port` (`__u32`, лише читання):** Порти TCP/UDP у мережевому порядку байтів.
- **`tstamp` (`__u64`, читання і запис):** Часова мітка пакета у наносекундах (наприклад, для алгоритмів керування чергами EDT / FQ).
- **`wire_len` (`__u32`, лише читання):** Фізична довжина кадра у дротах (включаючи L2 CRC).
- **`gso_segs`, `gso_size` (`__u32`, лише читання):** Параметри розвантаження сегментації GSO (Generic Segmentation Offload) — кількість сегментів та розмір кожного MSS.

## 2. Коди дій підсистеми Traffic Control (TC Action Return Codes)

Програми типу `BPF_PROG_TYPE_SCHED_CLS`, прикріплені у режимі Direct-Action (`da`), повертають один із системних кодів повернення дій, визначених у заголовочному файлі `<linux/pkt_cls.h>`:

### `TC_ACT_OK` (Значення: `0`)
Пакет успішно пройшов фільтр eBPF. Ядро продовжує стандартну обробку кадра:
- На хуку `ingress`: пакет передається підсистемі Netfilter `NF_INET_PRE_ROUTING` та таблиці маршрутизації IP (`ip_rcv`).
- На хуку `egress`: пакет передається у TX Ring мережевого драйвера (`dev_hard_start_xmit`).

### `TC_ACT_SHOT` (Значення: `2`)
Пакет підлягає негайному скиданню. Ядро викликає `kfree_skb()`, вивільняє сокетний буфер та інкрементує лічильник скинутих пакетів (`drop counter`) на інтерфейсі. Жодні наступні фільтри, Netfilter чи сокети пакет не отримують.

### `TC_ACT_UNSPEC` (Значення: `-1`)
Невизначена дія. Сигналізує підсистемі TC про необхідність продовжувати виконання наступних фільтрів або правил у класичному ланцюжку `tc filter`.

### `TC_ACT_STOLEN` (Значення: `4`)
Пакет вилучено (перехоплено) програмою eBPF. Використовується, коли eBPF програма або хепер повністю взяли на себе управління пам'яттю пакета і відповідають за його подальшу відправку чи вивільнення.

### `TC_ACT_REDIRECT` (Значення: `7`)
Спеціальний код повернення, який генерується допоміжною функцією `bpf_redirect()`. Сигналізує ядру про необхідність негайно перенаправити пакет на інший мережевий інтерфейс або в інший мережевий простір імен, минаючи стек L3-маршрутизації.

### `TC_ACT_TRAP` (Значення: `8`)
Передає пакет у підсистему моніторингу ядра або логування (nlmon/bpftool), перериваючи подальше проходження пакета.

### `TC_ACT_RECLASSIFY` (Значення: `1`)
Вимагає перезапуску процесу класифікації пакета з початку ланцюжка фільтрів.

## 3. Допоміжні функції ядра (eBPF Helpers for TC)

### Функції читання та запису даних

#### `bpf_skb_store_bytes`
```c
long bpf_skb_store_bytes(struct __sk_buff *skb, u32 offset, const void *from, u32 len, u64 flags);
```
Записує `len` байтів із локального буфера `from` у пакет за зсувом `offset` від початку L2-заголовка.
- **`flags`:** 
  - `BPF_F_RECOMPUTE_CSUM`: Автоматично інкрементує контрольні суми.
  - `BPF_F_INVALIDATE_HASH`: Очищує кешований хеш `skb->hash`, змушуючи ядро перерахувати хеш для RSS.
- **Повертає:** `0` при успіху; від'ємний код помилки (`-EFAULT` при виході за межі пакета, `-ENOMEM` при помилці виділення пам'яті під час розклонування `skb_unshare`).

#### `bpf_skb_load_bytes`
```c
long bpf_skb_load_bytes(const struct __sk_buff *skb, u32 offset, void *to, u32 len);
```
Копіює `len` байтів із пакета за зсувом `offset` у буфер `to` на стеку eBPF програми. Необхідна для зчитування даних із нелінійних (paged) кадрів, де `data + offset > data_end`.

#### `bpf_skb_pull_data`
```c
long bpf_skb_pull_data(struct __sk_buff *skb, u32 len);
```
Примусово підтягує `len` байтів із нелінійних пагінованих сторінок `skb_shinfo(skb)->frags` у лінійну область пам'яті `skb->data`. Після виклику цього хепера вказівники `skb->data` та `skb->data_end` змінюються, тому програма мусить заново зчитати їх та перевірити межі.

### Функції модифікації розміру та заголовків

#### `bpf_skb_adjust_room`
```c
long bpf_skb_adjust_room(struct __sk_buff *skb, s32 len_diff, u32 mode, u64 flags);
```
Збільшує або зменшує розмір заголовків пакета.
- **`len_diff`:** Додатне значення додає байти (для інкапсуляції VLAN/VXLAN), від'ємне — видаляє байти (для декапсуляції).
- **`mode`:** `BPF_ADJ_ROOM_NET` (зміна на рівні L3), `BPF_ADJ_ROOM_MAC` (зміна на рівні L2).
- **`flags`:** `BPF_F_ADJ_ROOM_FIXED_GSO` (збереження налаштувань сегментації GSO).

#### `bpf_skb_change_proto`
```c
long bpf_skb_change_proto(struct __sk_buff *skb, __be16 proto, u64 flags);
```
Змінює протокол L3 пакета між IPv4 (`ETH_P_IP`) та IPv6 (`ETH_P_IPV6`), коригуючи розмір L3-заголовка та ініціалізуючи відповідні поля.

#### `bpf_skb_change_tail`
```c
long bpf_skb_change_tail(struct __sk_buff *skb, u32 len, u64 flags);
```
Збільшує або зменшує загальну довжину пакета до вказаного значення `len`. Використовується для відсікання корисного навантаження (truncation).

### Функції коригування контрольних сум

#### `bpf_l3_csum_replace`
```c
long bpf_l3_csum_replace(struct __sk_buff *skb, u32 offset, u64 from, u64 to, u64 size);
```
Інкрементально оновлює IPv4 контрольну суму у заголовочному полі за зсувом `offset`. `from` — старе значення поля, `to` — нове значення, `size` — розмір поля у байтах (2 або 4).

#### `bpf_l4_csum_replace`
```c
long bpf_l4_csum_replace(struct __sk_buff *skb, u32 offset, u64 from, u64 to, u64 flags);
```
Інкрементально оновлює TCP, UDP або ICMP контрольну суму.
- **`flags`:** Верхні 4 байти задають розмір поля (2 або 4 байти); прапорець `BPF_F_PSEUDO_HDR` вказує, що модифіковано поле псевдозаголовка IP.

#### `bpf_csum_diff`
```c
s64 bpf_csum_diff(__be32 *from, u32 from_size, __be32 *to, u32 to_size, __wsum seed);
```
Обчислює 16-бітову різницю контрольної суми між двома буферами пам'яті `from` та `to`.

### Функції перенаправлення трафіку

#### `bpf_redirect`
```c
long bpf_redirect(u32 ifindex, u64 flags);
```
Записує цільовий індекс інтерфейсу `ifindex` у метадані `skb` та повертає код `TC_ACT_REDIRECT`.
- **`flags`:** `0` — перенаправити на вихідний шлях (egress) інтерфейсу `ifindex`; `BPF_F_INGRESS` — перенаправити на вхідний шлях (ingress) інтерфейсу.

#### `bpf_redirect_neigh`
```c
long bpf_redirect_neigh(u32 ifindex, struct bpf_redir_neigh *params, int plen, u64 flags);
```
Перенаправляє пакет на інтерфейс `ifindex` із автоматичним вирішенням MAC-адреси L2 через внутрішню таблицю сусідів ARP/ND ядра Linux, оминаючи повний виклик `ip_finish_output2()`.

#### `bpf_redirect_peer`
```c
long bpf_redirect_peer(u32 ifindex, u64 flags);
```
Оптимізована функція перенаправлення для віртуальних пристроїв `veth`. Передає пакет безпосередньо у вхідну чергу парного інтерфейсу `veth` у сусідньому мережевому просторі імен (netns) без копіювання сокетного буфера.

#### `bpf_clone_redirect`
```c
long bpf_clone_redirect(struct __sk_buff *skb, u32 ifindex, u64 flags);
```
Створює клоновану копію пакета за допомогою `skb_clone()` і відправляє клон на вказаний інтерфейс `ifindex`. Оригінальний пакет продовжує рух стеком. Використовується для віддзеркалення трафіку (traffic mirroring / TAP).

### Функції тунелювання та VLAN

#### `bpf_skb_get_tunnel_key` та `bpf_skb_set_tunnel_key`
```c
long bpf_skb_get_tunnel_key(struct __sk_buff *skb, struct bpf_tunnel_key *key, u32 size, u64 flags);
long bpf_skb_set_tunnel_key(struct __sk_buff *skb, const struct bpf_tunnel_key *key, u32 size, u64 flags);
```
Зчитують або встановлюють метадані зовнішнього тунелю (VXLAN, GRE, GENEVE). Поля структури `struct bpf_tunnel_key` включають `tunnel_id` (VNI), `remote_ipv4`, `tunnel_ttl`, `tunnel_tos`.

#### `bpf_skb_vlan_push` та `bpf_skb_vlan_pop`
```c
long bpf_skb_vlan_push(struct __sk_buff *skb, __be16 vlan_proto, u16 vlan_tci);
long bpf_skb_vlan_pop(struct __sk_buff *skb);
```
Додають або вилучають тег 802.1Q VLAN із заголовка кадра.

### Функції пошуку сокетів та cgroups

#### `bpf_skb_cgrp_id`
```c
u64 bpf_skb_cgrp_id(struct __sk_buff *skb);
```
Повертає унікальний 64-бітний ідентифікатор контрольної групи (cgroup v2), якій належить сокет відправника/отримувача пакета.

#### `bpf_skc_lookup_tcp`
```c
struct bpf_sock *bpf_skc_lookup_tcp(struct __sk_buff *skb, struct bpf_sock_tuple *tuple,
                                     u32 tuple_size, u64 netns, u64 flags);
```
Шукає сокет TCP у ядрі за 4-кортежними даними (IP відправника/отримувача, порти).

#### `bpf_sk_assign`
```c
long bpf_sk_assign(struct __sk_buff *skb, struct bpf_sock *sk, u64 flags);
```
Прив'язує знайдений сокет `sk` безпосередньо до сокетного буфера `skb`, оминаючи стандартну таблицю сокетного хедшингу ядра.

## 4. Користувацький API бібліотеки `libbpf`

Для управління дисципліною `clsact` та прикріплення eBPF програм із користувацького простору бібліотека `libbpf` (`<bpf/libbpf.h>`) надає набір функцій та макросів ініціалізації:

```c
#include <bpf/libbpf.h>

// Опис точки підключення
struct bpf_tc_hook {
    size_t sz;
    int ifindex;
    enum bpf_tc_attach_point attach_point; // BPF_TC_INGRESS, BPF_TC_EGRESS, BPF_TC_CUSTOM
    __u32 parent;
};

// Опції прикріплення фільтра
struct bpf_tc_opts {
    size_t sz;
    int prog_fd;
    __u32 flags;
    __u32 prog_id;
    __u32 handle;
    __u32 priority;
};
```

### Основні функції `libbpf`:

1. **`bpf_tc_hook_create(struct bpf_tc_hook *hook)`:**
   Створює дисципліну черги `clsact` на мережевому інтерфейсі `hook->ifindex`. Функція є ідемпотентною: якщо `clsact` вже існує, функція повертає `-EEXIST`.

2. **`bpf_tc_attach(const struct bpf_tc_hook *hook, struct bpf_tc_opts *opts)`:**
   Прикріплює програму eBPF з файловим дескриптором `opts->prog_fd` до вказаного хука (`BPF_TC_INGRESS` або `BPF_TC_EGRESS`) у режимі Direct-Action (`da`). Повертає `0` при успіху.

3. **`bpf_tc_detach(const struct bpf_tc_hook *hook, struct bpf_tc_opts *opts)`:**
   Відкріплює BPF-фільтр за його `opts->handle` або `opts->priority`.

4. **`bpf_tc_hook_destroy(struct bpf_tc_hook *hook)`:**
   Повністю видаляє дисципліну черги `clsact` з інтерфейсу разом з усіма прикріпленими фільтрами ingress та egress.

5. **`bpf_tc_query(const struct bpf_tc_hook *hook, struct bpf_tc_opts *opts)`:**
   Запитує в ядра параметри прикріпленого BPF-фільтра на вказаному хуку, заповнюючи `opts->prog_id`, `opts->handle` та `opts->priority`.

## 5. Інструменти CLI: `tc` та `bpftool`

Управління хуками TC можна здійснювати за допомогою стандартних системних утиліт Linux.

### Команди `tc`:
```bash
# 1. Створення clsact qdisc на eth0
tc qdisc add dev eth0 clsact

# 2. Прикріплення eBPF програми до ingress
tc filter add dev eth0 ingress bpf da obj my_prog.o sec classifier

# 3. Перегляд прикріплених BPF фільтрів
tc filter show dev eth0 ingress

# 4. Видалення фільтра або clsact qdisc
tc filter del dev eth0 ingress pref 49152
tc qdisc del dev eth0 clsact
```

### Команди `bpftool`:
```bash
# Перегляд усіх BPF програм, прив'язаних до мережевих інтерфейсів
bpftool net show

# Перегляд завантажених програм типу sched_cls
bpftool prog show type sched_cls

# Зняття розпарсеного байт-коду BPF інструкцій
bpftool prog dump xlated id <PROG_ID>
```
