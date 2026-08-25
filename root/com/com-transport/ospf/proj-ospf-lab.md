# ⚙️ Практикум OSPF: конфігурація FRR та аналіз пакетів на C і C++

На практиці протокол OSPF реалізується або спеціалізованими апаратними маршрутизаторами (Cisco IOS-XE, Juniper Junos, MikroTik RouterOS), або програмними демонами маршрутизації під операційні системи Linux/FreeBSD (FRRouting, BIRD). У цьому практикумі розглядається повний цикл розгортання багатозонної мережі OSPFv2 на базі відкритого стека FRRouting (FRR), покроковий аналіз топологічної бази LSDB через CLI `vtysh`, а також розробка низькорівневого мережевого парсера сирих бінарних пакетів OSPF мовами C та C++.

---

### 1. Архітектура лабораторного стенду в Linux

Лабораторна топологія моделює корпоративну мережу з трьома функціональними зонами:
- **R1 (ABR, Area Border Router):** прикордонний маршрутизатор, що з'єднує магістральну зону **Backbone Area 0** та філіальну тупикову зону **Stub Area 1**.
- **R2 (Core Router):** центральний магістральний комутатор-маршрутизатор ядра в зоні **Area 0**.
- **R3 (ASBR, Autonomous System Boundary Router):** маршрутизатор у спеціальній зоні **NSSA Area 2**, що підключає зовнішню автономну систему або статичний сегмент `172.16.0.0/16`.

```
[Stub Area 1]               [Backbone Area 0]               [NSSA Area 2]
 192.168.1.0/24               10.0.0.0/30                     10.0.1.0/30
     |                           |                               |
  [eth1]                      [eth0]                          [eth0]
+---------+  10.0.0.0/30   +---------+  10.0.1.0/30        +---------+
|   R1    | [eth0]====[eth0|   R2    | [eth1]====[eth0]     |   R3    |===> 172.16.0.0/16
|  (ABR)  |                | (Core)  |                      | (ASBR)  |    (Static External)
+---------+                +---------+                      +---------+
```

Для створення ізольованих вузлів маршрутизації в Linux використовуються мережеві простори імен (Network Namespaces). Кожен простір імен має власну незалежну таблицю маршрутизації, власний набір мережевих інтерфейсів та ізольований мережевий стек ядра. Маршрутизатори зв'язуються між собою за допомогою віртуальних Ethernet-пар (`veth`), які працюють як прямий віртуальний патч-корд між портами: пакет, переданий в один кінець пари, миттєво з'являється на іншому кінці в обробнику переривань ядра `NET_RX_SOFTIRQ`.

Мережеві простори імен ядра Linux забезпечують строгу ізоляцію системних таблиць маршрутизації, сокетів, правил міжмережевого екрана (iptables/nftables) та інтерфейсів. Коли віртуальний інтерфейс `veth` передає фрейм, ядро виділяє структуру буфера сокета `sk_buff` і без проходження через фізичний рівень викликає функцію прийому `netif_rx()`. Для увімкнення пересилання транзитних IP-пакетів між різними інтерфейсами в кожному просторі імен обов'язково активується прапорець ядра `net.ipv4.ip_forward = 1`.

#### Створення та налаштування мережевих просторів імен:

Усі команди виконуються з правами суперкористувача `root`. Спочатку створюються три простори імен `R1`, `R2` та `R3`, потім конфігуруються інтерфейси зв'язку:

```bash
# Створення просторів імен для трьох вузлів
ip netns add R1
ip netns add R2
ip netns add R3

# Створення з'єднувальних veth-пар
ip link add veth-r1-r2 type veth peer name veth-r2-r1
ip link add veth-r2-r3 type veth peer name veth-r3-r2

# Розподіл інтерфейсів по відповідних просторах імен
ip link set veth-r1-r2 netns R1
ip link set veth-r2-r1 netns R2
ip link set veth-r2-r3 netns R2
ip link set veth-r3-r2 netns R3

# Налаштування IP-адрес на R1
ip netns exec R1 ip addr add 10.0.0.1/30 dev veth-r1-r2
ip netns exec R1 ip link set veth-r1-r2 up
ip netns exec R1 ip link set lo up
ip netns exec R1 ip link add name lo-stub type dummy
ip netns exec R1 ip addr add 192.168.1.1/24 dev lo-stub
ip netns exec R1 ip link set lo-stub up

# Налаштування IP-адрес на R2
ip netns exec R2 ip addr add 10.0.0.2/30 dev veth-r2-r1
ip netns exec R2 ip addr add 10.0.1.1/30 dev veth-r2-r3
ip netns exec R2 ip link set veth-r2-r1 up
ip netns exec R2 ip link set veth-r2-r3 up
ip netns exec R2 ip link set lo up

# Налаштування IP-адрес на R3
ip netns exec R3 ip addr add 10.0.1.2/30 dev veth-r3-r2
ip netns exec R3 ip link set veth-r3-r2 up
ip netns exec R3 ip link set lo up

# Увімкнення IP Forwarding у ядрі для всіх просторів імен
ip netns exec R1 sysctl -w net.ipv4.ip_forward=1
ip netns exec R2 sysctl -w net.ipv4.ip_forward=1
ip netns exec R3 sysctl -w net.ipv4.ip_forward=1
```

Після підняття лінків вузли готові до запуску демонів динамічної маршрутизації FRRouting.

---

### 2. Конфігурація демона FRR OSPF (`ospfd.conf`)

Стек FRRouting розділяє функції управління та протоколів: демон `zebra` взаємодіє з ядром Linux через сокети Netlink і оновлює таблицю форвардингу ядра (FIB), а демон `ospfd` відповідає за протокольний обмін пакетами OSPF, побудову бази даних LSDB та розрахунок алгоритму Дейкстри. Взаємодія між `ospfd` та `zebra` відбувається локально через UNIX-сокет `/var/run/frr/zapi.sock` за бінарним протоколом ZAPI.

Архітектура взаємодії компонентів FRRouting базується на чіткому розділенні обов'язків:
1. Демон `zebra` виступає центральним менеджером бази інформації маршрутизації (RIB). Він збирає найкращі маршрути від усіх запущених протоколів (OSPF, BGP, IS-IS, статичні маршрути) та вирішує конфлікти за адміністративною відстанню (Administrative Distance). Обрані маршрути інсталюються в ядро операційної системи за допомогою системних повідомлень Netlink `RTM_NEWROUTE`.
2. Демон `ospfd` реалізує виключно протокольну логіку OSPFv2 (RFC 2328). Він встановлює зв'язки з сусідами, управляє базою даних стану каналів (LSDB) та періодично виконує розрахунок найкоротших шляхів за алгоритмом Дейкстри. Щойно алгоритм обчислює новий оптимальний шлях, `ospfd` передає повідомлення `ZEBRA_ROUTE_ADD` через локальний UNIX-сокет демону `zebra`.

#### Конфігурація R1 (ABR) у `/etc/frr/ospfd.conf`:
Прикордонний маршрутизатор R1 має інтерфейси у двох зонах. Він налаштований на роботу з криптографічною автентифікацією MD5 на магістральному інтерфейсі `veth-r1-r2`. Зона `0.0.0.1` оголошена як `stub`, що забороняє розповсюдження зовнішніх оголошень LSA Type 5:

```text
! Конфігурація OSPFv2 для R1 (Area Border Router)
frr version 8.5
frr defaults traditional
hostname R1-ABR
log syslog informational

interface veth-r1-r2
 description Link to Core R2 (Backbone Area 0)
 ip address 10.0.0.1/30
 ip ospf authentication message-digest
 ip ospf message-digest-key 1 md5 SecretKeyArea0
 ip ospf cost 10
 ip ospf hello-interval 10
 ip ospf dead-interval 40
!
interface lo-stub
 description Subnet in Stub Area 1
 ip address 192.168.1.1/24
 ip ospf cost 100
!
router ospf
 ospf router-id 1.1.1.1
 auto-cost reference-bandwidth 100000
 ! Прив'язка інтерфейсів до відповідних зон
 network 10.0.0.0/30 area 0.0.0.0
 network 192.168.1.0/24 area 0.0.0.1
 ! Оголошення зони 1 як Stub
 area 0.0.0.1 stub
!
line vty
```

#### Конфігурація R2 (Core Backbone) у `/etc/frr/ospfd.conf`:
Магістральний роутер R2 обслуговує лінки до R1 та R3. Інтерфейс у сторону R3 належить до спеціальної зони `nssa`:

```text
! Конфігурація OSPFv2 для R2 (Backbone Router)
frr version 8.5
hostname R2-Core
log syslog informational

interface veth-r2-r1
 description Link to R1 (Area 0)
 ip address 10.0.0.2/30
 ip ospf authentication message-digest
 ip ospf message-digest-key 1 md5 SecretKeyArea0
 ip ospf cost 10
!
interface veth-r2-r3
 description Link to R3 (NSSA Area 2)
 ip address 10.0.1.1/30
 ip ospf cost 10
!
router ospf
 ospf router-id 2.2.2.2
 auto-cost reference-bandwidth 100000
 network 10.0.0.0/30 area 0.0.0.0
 network 10.0.1.0/30 area 0.0.0.2
 ! Оголошення зони 2 як NSSA
 area 0.0.0.2 nssa
!
line vty
```

#### Конфігурація R3 (ASBR в NSSA) у `/etc/frr/ospfd.conf`:
Маршрутизатор R3 підключає зовнішню мережу `172.16.0.0/16` і редистрибує її як зовнішній маршрут типу 1 (`metric-type 1` з початковою вартістю `50`):

```text
! Конфігурація OSPFv2 для R3 (ASBR у зоні NSSA)
frr version 8.5
hostname R3-ASBR
log syslog informational

interface veth-r3-r2
 description Link to R2 (Area 2 NSSA)
 ip address 10.0.1.2/30
 ip ospf cost 10
!
router ospf
 ospf router-id 3.3.3.3
 auto-cost reference-bandwidth 100000
 network 10.0.1.0/30 area 0.0.0.2
 area 0.0.0.2 nssa
 ! Редистрибуція зовнішніх статичних маршрутів у OSPF
 redistribute static metric-type 1 metric 50
!
! Статичний маршрут для симуляції зовнішньої мережі
ip route 172.16.0.0/16 Null0
!
line vty
```

---

### 3. Діагностика та верифікація стану через `vtysh`

Оболонка `vtysh` надає Cisco-подібний уніфікований інтерфейс командного рядка для контролю та діагностики всіх запущених процесів маршрутизації.

#### 3.1. Перевірка сусідства OSPF:
```bash
ip netns exec R1 vtysh -c "show ip ospf neighbor"
```
```text
Neighbor ID     Pri State           Dead Time Address         Interface     RXmtL RtxL
2.2.2.2           1 Full/DR           00:00:34 10.0.0.2        veth-r1-r2:10.0.0.1  0    0
```
- Стан `Full/DR` свідчить про успішне завершення всіх стадій узгодження та повну синхронізацію топологічних баз між R1 та R2.
- `Dead Time: 00:00:34` вказує на коректний прийом пакетів Hello та скидання таймера мертвого сусіда (DeadInterval).

#### 3.2. Аналіз бази даних стану каналів (LSDB):
```bash
ip netns exec R1 vtysh -c "show ip ospf database"
```
```text
       OSPF Router with ID (1.1.1.1)

                Router Link States (Area 0.0.0.0)

Link ID         ADV Router      Age  Seq#       CkSum  Link count
1.1.1.1         1.1.1.1         412  0x80000004 0x7a2b 1
2.2.2.2         2.2.2.2         408  0x80000005 0x6e31 2

                Summary Link States (Area 0.0.0.0)

Link ID         ADV Router      Age  Seq#       CkSum
192.168.1.0     1.1.1.1         360  0x80000001 0x4f12
172.16.0.0      2.2.2.2         215  0x80000001 0x81fa

                Router Link States (Area 0.0.0.1)

Link ID         ADV Router      Age  Seq#       CkSum  Link count
1.1.1.1         1.1.1.1         412  0x80000003 0x821c 1

                Summary Link States (Area 0.0.0.1)

Link ID         ADV Router      Age  Seq#       CkSum
0.0.0.0         1.1.1.1         412  0x80000001 0x22ab
10.0.0.0        1.1.1.1         360  0x80000001 0x91df
```
З виводу чітко видно поведінку прикордонного маршрутизатора (ABR):
- У зоні `0.0.0.0` присутні Summary LSA Type 3 для мережі `192.168.1.0` (згенеровані R1) та для `172.16.0.0` (трансльовані R2 з NSSA).
- У зоні `0.0.0.1` (Stub) відсутні важкі зовнішні LSA Type 5; замість них R1 автоматично згенерував маршрут за замовчуванням `0.0.0.0/0` (Type 3 Summary).

#### 3.3. Перевірка таблиці маршрутизації IP ядра Linux:
```bash
ip netns exec R1 vtysh -c "show ip route ospf"
```
```text
Codes: K - kernel route, C - connected, S - static, R - RIP,
       O - OSPF, I - IS-IS, B - BGP, E - EIGRP, N - NHRP,
       T - Table, v - VNC, V - VNC-Direct, A - Babel, D - SHARP,
       F - PBR, f - OpenFabric,
       > - selected route, * - FIB route, q - queued, r - rejected, b - backup

O>* 10.0.1.0/30 [110/20] via 10.0.0.2, veth-r1-r2, weight 1, 00:06:48
O>* 172.16.0.0/16 [110/70] via 10.0.0.2, veth-r1-r2, weight 1, 00:03:12
```

Маршрутизатор R1 успішно встановив маршрут до зовнішньої підмережі `172.16.0.0/16` через шлюз `10.0.0.2` з повною метрикою `70` (внутрішня вартість каналів `10 + 10 = 20` плюс зовнішня метрика редистрибуції `50`).

---

### 4. Аналіз захопленого трафіку та діагностика несправностей

Під час налагодження протоколу OSPF інженери часто використовують утиліти `tcpdump` або Wireshark для перехоплення пакетів на інтерфейсі:

```bash
ip netns exec R1 tcpdump -vvv -s 0 -n -i veth-r1-r2 proto 89
```

Аналізуючи сирий бінарний дамп пакета OSPF Hello, отриманого на інтерфейсі `veth-r1-r2`, можна спостерігати точну послідовність заголовків:
1. Заголовок кадру Ethernet II: 6 байтів MAC-адреси призначення `01:00:5E:00:00:05` (стандартне відображення мультикаст-адреси `224.0.0.5` у канальний рівень), 6 байтів MAC-адреси джерела, 2 байти EtherType `0x0800` (IPv4).
2. Заголовок IPv4: 20 байтів. Поле Type of Service (ToS / DSCP) містить значення `0xC0` (CS6 / Network Control), що гарантує найвищий пріоритет обробки службового трафіку маршрутизації в чергах комутаторів. Поле Time-to-Live (TTL) суворо дорівнює `1` (пакети OSPF ніколи не маршрутизуються транзитом через інші вузли). Поле номера протоколу IP містить `89` (`IPPROTO_OSPF`).
3. Загальний заголовок OSPF: 24 байти. Версія `2`, тип `1` (Hello), довжина пакета `48` байтів, Router ID `2.2.2.2`, Area ID `0.0.0.0`, контрольна сума, AuType `2` (Cryptographic MD5).
4. Тіло Hello: 20 байтів. Маска `255.255.255.252`, HelloInterval `10`, біт опцій `E=1`, пріоритет `1`, RouterDeadInterval `40`, адреси DR `10.0.0.2` та BDR `10.0.0.1`, список активних сусідів.
5. Криптографічний трейлер MD5: Key ID `1`, довжина даних автентифікації `16` байтів, Cryptographic Sequence Number для захисту від атак повторного відтворення (Replay Attacks), 128-бітний хеш MD5.

#### Типові несправності встановлення сусідства (Troubleshooting):
1. **Невідповідність MTU (MTU Mismatch):** якщо на одному кінці лінку MTU встановлено в 1500 байтів, а на іншому — в 9000 (Jumbo frames), пакети Hello проходять успішно (вони короткі), але під час фази `ExStart` або `Exchange` великий пакет DBD відкидається мережевим драйвером. Маршрутизатори зависають у стані `ExStart/Exchange`.
2. **Розбіжність таймерів (Timer Mismatch):** якщо HelloInterval або DeadInterval не збігаються, маршрутизатор скидає сусідство відразу після завершення dead-інтервалу.
3. **Помилка автентифікації (Auth Mismatch):** якщо на одній стороні налаштовано MD5, а на іншій — відкритий текст або не збігається Key ID, пакети OSPF мовчки відкидаються на рівні вхідного аналізу заголовка.
4. **Неузгодженість маски підмережі (Subnet Mask Mismatch):** у широкомовних мережах Ethernet пакети Hello містять маску підмережі інтерфейсу. Якщо на одному маршрутизаторі налаштовано `/24`, а на сусідньому — `/25`, вони не перейдуть у стан 2-Way і сусідство буде відхилено.
5. **Дублювання Router ID (Duplicate RID):** якщо два маршрутизатори в одній зоні випадково отримали однаковий Router ID, їхні LSA почнуть постійно витісняти одне одного (LSA Flapping), спричиняючи перманентний перерахунок алгоритму Дейкстри.

---

### 5. Реалізація низькорівневого бінарного парсера OSPF на C та C++

Для глибокого розуміння протоколу нижче наведено робочий код утиліти, яка перехоплює службові пакети OSPF безпосередньо з мережевого сокета Linux за допомогою `SOCK_RAW` для номера протоколу IP `89` (`IPPROTO_OSPF`) та виконує бінарну десеріалізацію заголовків.

#### Архітектурні особливості реалізації:
1. **Вирівнювання структур:** заголовок OSPF має строгий бінарний формат. У мові C використовується директива `#pragma pack(push, 1)`, яка забороняє компілятору додавати автоматичне вирівнювання (padding) між полями структури. У мові C++ використовується атрибут `[[gnu::packed]]`.
2. **Мережевий порядок байтів:** усі багатобайтові цілі числа передаються у форматі Big-Endian. Функції `ntohs()` (Network to Host Short) та `ntohl()` (Network to Host Long) перетворюють поля довжини, контрольної суми, послідовних номерів та таймерів у порядок байтів хостового процесора (Little-Endian на архітектурах x86_64).
3. **Обробка помилок та безпека пам'яті:** версія на C++20 використовує безпечні обгортки ресурсів (RAII для сокетів), тип `std::span<const uint8_t>` для передачі незмінних зрізів пам'яті без копіювання та сучасний тип `std::expected` для явної обробки помилок парсингу без винятків.

:::tabs
```c
/* ospf_sniffer.c — перехоплення та бінарний розбір пакетів OSPFv2 на C */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <sys/socket.h>

#define OSPF_PROTO 89

#pragma pack(push, 1)
typedef struct {
    uint8_t  version;
    uint8_t  type;
    uint16_t length;
    uint32_t router_id;
    uint32_t area_id;
    uint16_t checksum;
    uint16_t autype;
    uint64_t authentication;
} ospf_header_t;

typedef struct {
    uint32_t network_mask;
    uint16_t hello_interval;
    uint8_t  options;
    uint8_t  priority;
    uint32_t dead_interval;
    uint32_t dr;
    uint32_t bdr;
} ospf_hello_t;
#pragma pack(pop)

static const char* get_ospf_type_str(uint8_t type) {
    switch (type) {
        case 1: return "Hello";
        case 2: return "Database Description (DBD)";
        case 3: return "Link State Request (LSR)";
        case 4: return "Link State Update (LSU)";
        case 5: return "Link State Ack (LSAck)";
        default: return "Unknown";
    }
}

void process_ospf_packet(const uint8_t *payload, ssize_t len) {
    if (len < (ssize_t)sizeof(ospf_header_t)) {
        printf("Помилка: довжина пакета (%zd байтів) менша за заголовок OSPF.
", len);
        return;
    }

    const ospf_header_t *hdr = (const ospf_header_t *)payload;
    struct in_addr rid_addr, area_addr;
    rid_addr.s_addr = hdr->router_id;
    area_addr.s_addr = hdr->area_id;

    printf("
=== Отримано пакет OSPFv%u ===
", hdr->version);
    printf("Тип: %u [%s] | Загальна довжина: %u байтів
",
           hdr->type, get_ospf_type_str(hdr->type), ntohs(hdr->length));
    printf("Router ID: %s | Area ID: %s
", inet_ntoa(rid_addr), inet_ntoa(area_addr));
    printf("Тип автентифікації: %u | Контрольна сума: 0x%04X
",
           ntohs(hdr->autype), ntohs(hdr->checksum));

    if (hdr->type == 1 && len >= (ssize_t)(sizeof(ospf_header_t) + sizeof(ospf_hello_t))) {
        const ospf_hello_t *hello = (const ospf_hello_t *)(payload + sizeof(ospf_header_t));
        struct in_addr mask_addr, dr_addr, bdr_addr;
        mask_addr.s_addr = hello->network_mask;
        dr_addr.s_addr = hello->dr;
        bdr_addr.s_addr = hello->bdr;

        printf("--- Тіло пакета Hello ---
");
        printf("Маска підмережі: %s | Hello: %u с | Dead: %u с
",
               inet_ntoa(mask_addr), ntohs(hello->hello_interval), ntohl(hello->dead_interval));
        printf("Пріоритет вузла: %u | DR: %s | BDR: %s
",
               hello->priority, inet_ntoa(dr_addr), inet_ntoa(bdr_addr));
    }
}

int main(void) {
    int raw_sock = socket(AF_INET, SOCK_RAW, OSPF_PROTO);
    if (raw_sock < 0) {
        perror("Помилка створення raw-сокета (потрібні права root)");
        return 1;
    }

    printf("Прослуховування пакетів OSPF (IP-протокол 89)...
");
    uint8_t buffer[4096];

    while (1) {
        ssize_t received = recvfrom(raw_sock, buffer, sizeof(buffer), 0, NULL, NULL);
        if (received > 0) {
            /* Пропускаємо заголовок IPv4 (розмір визначається полем IHL) */
            uint8_t ip_ihl = (buffer[0] & 0x0F) * 4;
            if (received > ip_ihl) {
                process_ospf_packet(buffer + ip_ihl, received - ip_ihl);
            }
        }
    }

    close(raw_sock);
    return 0;
}
```
```cpp
// ospf_sniffer.cpp — ідіоматичний та безпечний парсер OSPFv2 на C++20
#include <iostream>
#include <iomanip>
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <expected>
#include <memory>
#include <cstring>
#include <arpa/inet.h>
#include <unistd.h>
#include <sys/socket.h>

enum class OspfType : uint8_t {
    Hello         = 1,
    DatabaseDesc  = 2,
    LinkStateReq  = 3,
    LinkStateUpd  = 4,
    LinkStateAck  = 5
};

constexpr std::string_view to_string(OspfType type) noexcept {
    switch (type) {
        case OspfType::Hello:        return "Hello";
        case OspfType::DatabaseDesc: return "Database Description (DBD)";
        case OspfType::LinkStateReq: return "Link State Request (LSR)";
        case OspfType::LinkStateUpd: return "Link State Update (LSU)";
        case OspfType::LinkStateAck: return "Link State Ack (LSAck)";
    }
    return "Unknown";
}

struct [[gnu::packed]] OspfHeaderLayout {
    uint8_t  version;
    uint8_t  type;
    uint16_t length;
    uint32_t router_id;
    uint32_t area_id;
    uint16_t checksum;
    uint16_t autype;
    uint64_t authentication;
};

struct [[gnu::packed]] OspfHelloLayout {
    uint32_t network_mask;
    uint16_t hello_interval;
    uint8_t  options;
    uint8_t  priority;
    uint32_t dead_interval;
    uint32_t dr;
    uint32_t bdr;
};

struct OspfParsedMessage {
    uint8_t     version;
    OspfType    type;
    uint16_t    length;
    std::string router_id;
    std::string area_id;
    uint16_t    checksum;
    uint16_t    auth_type;
};

class ScopedRawSocket {
    int fd_{-1};
public:
    explicit ScopedRawSocket(int proto) {
        fd_ = ::socket(AF_INET, SOCK_RAW, proto);
    }
    ~ScopedRawSocket() {
        if (fd_ >= 0) ::close(fd_);
    }
    ScopedRawSocket(const ScopedRawSocket&) = delete;
    ScopedRawSocket& operator=(const ScopedRawSocket&) = delete;

    [[nodiscard]] bool is_valid() const noexcept { return fd_ >= 0; }
    [[nodiscard]] int get() const noexcept { return fd_; }
};

std::string format_ipv4(uint32_t net_order_ip) {
    char str_buf[INET_ADDRSTRLEN];
    struct in_addr addr{net_order_ip};
    if (::inet_ntop(AF_INET, &addr, str_buf, sizeof(str_buf))) {
        return str_buf;
    }
    return "0.0.0.0";
}

std::expected<OspfParsedMessage, std::string_view> parse_header(std::span<const uint8_t> bytes) {
    if (bytes.size() < sizeof(OspfHeaderLayout)) {
        return std::unexpected("Розмір пакета менший за обов'язковий заголовок OSPF (24 байти)");
    }

    OspfHeaderLayout raw{};
    std::memcpy(&raw, bytes.data(), sizeof(OspfHeaderLayout));

    return OspfParsedMessage{
        .version   = raw.version,
        .type      = static_cast<OspfType>(raw.type),
        .length    = ntohs(raw.length),
        .router_id = format_ipv4(raw.router_id),
        .area_id   = format_ipv4(raw.area_id),
        .checksum  = ntohs(raw.checksum),
        .auth_type = ntohs(raw.autype)
    };
}

int main() {
    ScopedRawSocket sock(89);
    if (!sock.is_valid()) {
        std::cerr << "Не вдалося відкрити SOCK_RAW (89). Перевірте наявність прав суперкористувача (sudo).
";
        return 1;
    }

    std::cout << "Слухаємо інтерфейси на наявність трафіку OSPF...
";
    std::vector<uint8_t> rx_buffer(4096);

    while (true) {
        ssize_t bytes_read = ::recvfrom(sock.get(), rx_buffer.data(), rx_buffer.size(), 0, nullptr, nullptr);
        if (bytes_read <= 0) continue;

        uint8_t ip_hdr_len = (rx_buffer[0] & 0x0F) * 4;
        if (bytes_read <= ip_hdr_len) continue;

        std::span<const uint8_t> ospf_span(rx_buffer.data() + ip_hdr_len, bytes_read - ip_hdr_len);
        auto parsed = parse_header(ospf_span);

        if (parsed) {
            const auto& msg = *parsed;
            std::cout << "
[OSPFv" << static_cast<int>(msg.version) << " Пакет]
"
                      << "  Тип: " << to_string(msg.type)
                      << " (довжина " << msg.length << " байтів)
"
                      << "  Router ID: " << msg.router_id
                      << " | Area ID: " << msg.area_id << "
"
                      << "  AuthType: " << msg.auth_type
                      << " | Checksum: 0x" << std::hex << std::uppercase << msg.checksum << std::dec << "
";
        } else {
            std::cerr << "Помилка аналізу: " << parsed.error() << "
";
        }
    }
    return 0;
}
```
:::

---

### 6. Архітектурний аналіз життєвого циклу мережевих пакетів у ядрі Linux

Для глибокого розуміння того, як ядро Linux обробляє пакети в мережевих просторах імен, корисно простежити шлях структури буфера сокета `sk_buff` від фізичного або віртуального інтерфейсу до кінцевого процесу OSPF у просторі користувача.

Коли фрейм Ethernet надходить на віртуальний інтерфейс `veth-r1-r2`, мережевий драйвер формує об'єкт `skb` і викликає функцію планувальника черги пакетів `netif_receive_skb()`. Ядро виконує послідовну обробку:
1. **Канальний рівень (L2):** перевіряється MAC-адреса призначення. Якщо фрейм адресовано мультикаст-групі `01:00:5E:00:00:05` або конкретному інтерфейсу, поле `skb->protocol` передається мережевому стеку IPv4.
2. **Мережевий рівень (L3 Ingress):** функція `ip_rcv()` перевіряє цілісність заголовка IPv4 та його контрольну суму. Далі пакет проходить ланцюжок хуків Netfilter `NF_INET_PRE_ROUTING`.
3. **Маршрутизація та розгалуження (FIB Lookup):** функція `ip_route_input_noref()` звертається до таблиці пересилання ядра (FIB) поточного простору імен. Якщо пакет адресовано самому маршрутизатору або підписаній групі мультикасту, викликається `ip_local_deliver()`.
4. **Доставка до Raw-сокетів:** функція `raw_local_deliver()` шукає всі відкриті сокети `SOCK_RAW`, у яких номер протоколу збігається з полем протоколу в заголовку IP (`89`). Ядро клонує структуру `skb` і поміщає її в чергу прийому сокета процесу `ospfd` або нашого аналізатора пакетів.

Така багаторівнева обробка гарантує повну апаратну прозорість: програмні маршрутизатори на базі Linux демонструють продуктивність у мільйони пакетів за секунду при використанні оптимізацій XDP (eXpress Data Path) та апаратного розвантаження черг комутаторів.

---

### 7. Низькорівневе програмування та оптимізація сокетів SOCK_RAW у Linux

Під час розробки високопродуктивних аналізаторів протоколів чи демонів маршрутизації робота з raw-сокетами вимагає врахування низки системних оптимізацій:
- **Управління буферами сокета:** за замовчуванням розмір буфера прийому сокета обмежений значенням ядра `net.core.rmem_default`. Під час спалахів лавинної розсилки оновлень (LSA Flooding Storms) буфер може переповнюватися, спричиняючи втрату пакетів. Збільшення розміру буфера виконується викликом `setsockopt(sock, SOL_SOCKET, SO_RCVBUF, &buf_size, sizeof(buf_size))`.
- **Фільтрація через Classic BPF або eBPF:** щоб уникнути копіювання непотрібних пакетів з простору ядра в простір користувача, до raw-сокета можна приєднати скомпільований фільтр BPF за допомогою параметра `SO_ATTACH_FILTER`. Фільтр виконується безпосередньо в обробнику переривань ядра і відкидає пакети з невідповідним типом OSPF (наприклад, фільтруючи лише пакети LSU для моніторингу топологічних змін).
- **Підписка на групові адреси (Multicast Membership):** для гарантованого прийому пакетів, адресованих `224.0.0.5` та `224.0.0.6`, на конкретному інтерфейсі додаток формує структуру `struct ip_mreqn` і передає її через `setsockopt(sock, IPPROTO_IP, IP_ADD_MEMBERSHIP, ...)`.

---

### 8. Промисловий моніторинг стану OSPF за допомогою Prometheus та Grafana

У сучасних виробничих інфраструктурах та хмарних дата-центрах контроль за стабільністю протоколу динамічної маршрутизації автоматизується за допомогою експортерів метрик:
- `frr-exporter` підключається до сокета `vtysh` і транслює статистику в формат метрик Prometheus.
- Ключова метрика `ospf_neighbor_state` зі значенням `8` (Full) сигналізує про нормальний стан лінку. Будь-яке падіння значення нижче 8 автоматично генерує сповіщення черговому інженеру (SRE Alert).
- Метрика лічильника перерахунків `ospf_spf_runs_total` дозволяє вчасно виявити коливання фізичних каналів (Flapping Detection) та локалізувати дефектний оптичний трансивер до того, як деградація вплине на час відгуку клієнтських сервісів.

---

### 9. Використання протоколу BFD для субсекундної збіжності

Хоча стандартний таймер DeadInterval у OSPF становить 40 секунд (або 4 секунди при мінімальному налаштуванні `hello-interval 1`), сучасні сервіси реального часу вимагають виявлення обриву оптичного зв'язку за 50–100 мілісекунд.

Для досягнення надшвидкої збіжності OSPF інтегрується з протоколом двонаправленого виявлення пересилань (BFD, англ. *Bidirectional Forwarding Detection*, RFC 5880):
- Сесія BFD встановлюється між двома сусідніми маршрутизаторами з інтервалом опитування 50 мс.
- У разі втрати трьох послідовних контрольних пакетів BFD (через 150 мс), протокол BFD миттєво сповіщає демон `ospfd` про розрив каналу.
- Демон `ospfd` не чекає завершення 40-секундного OSPF DeadInterval, а негайно переводить стан сусідства в `Down`, розсилає аварійний Router-LSA та ініціює локальний перерахунок SPF, мінімізуючи втрату транзитного трафіку.

---

### 10. Інженерні патерни проектування відмовостійких систем на базі Anycast OSPF

У масштабованих архітектурах DNS-серверів (BIND, PowerDNS) та розподілених балансувальників навантаження (HAProxy, Envoy) широко застосовується технологія Anycast OSPF:
- Кілька фізичних серверів у різних стійках налаштовують однакову IP-адресу сервісу (наприклад, `192.0.2.1/32`) на віртуальному петльовому інтерфейсі `dummy0`.
- Кожен сервер запускає локальний демон OSPF і анонсує цей префікс у магістральну зону Area 0.
- Мережеві комутатори сприймають сервери як кілька рівнозначних шляхів ECMP і розподіляють запити клієнтів за допомогою апаратного 5-tuple гешування.
- Якщо сервісний процес на одному з серверів виходить з ладу, локальний скрипт перевірки працездатності (Healthcheck) негайно опускає інтерфейс `dummy0`. Демон OSPF за частки мілісекунди відкликає LSA, і комутатори автоматично перенаправляють нові з'єднання на сусідні справні сервери кластера без простою в обслуговуванні.
---

### 11. Політики фільтрації та безпека взаємодії з BGP

Під час редистрибуції маршрутів між OSPF та протоколами зовнішньої маршрутизації (BGP) критично важливо використовувати карти маршрутів (Route-Maps) та списки префіксів (Prefix-Lists). Пряма безконтрольна редистрибуція без фільтрації здатна перенести тисячі глобальних інтернет-маршрутів BGP у внутрішню базу даних LSDB OSPF, що спричинить вичерпання оперативної пам'яті комутаторів та колапс локальної мережі. Для запобігання зворотного витоку маршрутів інженери маркують імпортовані префікси спеціальними 32-бітними числовими мітками (Route Tags), які автоматично блокуються на інших прикордонних вузлах ASBR.
