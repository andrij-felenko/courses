# 📋 Довідник параметрів, утиліт та Netlink API для Linux Bridge

Вичерпний технічний довідник параметрів ядра, утиліт керування (`iproute2` та `bridge-utils`), атрибутів бінарного протоколу RTNETLINK, механізмів апаратного вивантаження Switchdev та вузлів файлової системи `sysfs` для підсистеми програмної комутації Linux Bridge (IEEE 802.1D / IEEE 802.1Q).

Підсистема Linux Bridge надає ядру та простору користувача багаторівневий інтерфейс керування. Основним та найпродуктивнішим механізмом конфігурації є протокол RTNETLINK (сімейство сокетів `AF_NETLINK`, тип `NETLINK_ROUTE`). На відміну від застарілих блокувальних системних викликів `ioctl` (утиліта `brctl`), протокол Netlink забезпечує асинхронну передачу структурованих повідомлень (Type-Length-Value, TLV), транзакційність операцій, нотифікацію про топологічні зміни через мультикаст-групи ядра та пряму синхронізацію з апаратними комутаційними чіпами (ASIC) через фреймворк Switchdev. Для діагностики, моніторингу та швидкого скриптингу доступні дерево вузлів у віртуальній файловій системі `sysfs` та системні параметри фільтрації `sysctl` модуля `br_netfilter`.

---

## 1. Параметри конфігурації моста (`ip link` та `IFLA_BR_*`)

Створення, зміна та видалення екземпляра моста здійснюються утилітою `ip link` або надсиланням бінарних повідомлень `RTM_NEWLINK`, `RTM_SETLINK` та `RTM_DELLINK` із сімейством `AF_UNSPEC` (або `AF_BRIDGE`).

### 1.1. Синтаксис створення та модифікації через `iproute2`

```bash
# Створення нового екземпляра моста з явним заданням комутаційних параметрів
ip link add name <BRNAME> type bridge [vlan_filtering {0|1}] \
    [vlan_default_pvid <PVID>] [vlan_protocol {802.1q|802.1ad}] \
    [vlan_stats_enabled {0|1}] [vlan_stats_per_port {0|1}] \
    [stp_state {0|1|2}] [priority <PRIO>] \
    [forward_delay <TICKS>] [hello_time <TICKS>] [max_age <TICKS>] \
    [ageing_time <TICKS>] [group_fwd_mask <MASK>] [group_address <MAC>] \
    [mcast_snooping {0|1}] [mcast_querier {0|1}] [mcast_igmp_version {2|3}] \
    [mcast_mld_version {1|2}] [mcast_query_interval <TICKS>] \
    [mcast_query_response_interval <TICKS>] [mcast_membership_interval <TICKS>] \
    [mcast_startup_query_count <CNT>] [mcast_stats_enabled {0|1}] \
    [nf_call_iptables {0|1}] [nf_call_ip6tables {0|1}] [nf_call_arptables {0|1}]

# Модифікація параметрів наявного моста
ip link set dev <BRNAME> type bridge vlan_filtering 1 priority 16384 ageing_time 15000

# Видалення віртуального моста разом із усіма асоційованими прив'язками
ip link del dev <BRNAME>
```

### 1.2. Специфікація атрибутів моста (`IFLA_INFO_DATA` -> `IFLA_BR_*`)

Під час виклику Netlink заголовок `IFLA_LINKINFO` містить під-атрибут `IFLA_INFO_KIND` зі строковим значенням `"bridge"`, а конфігураційний блок параметрів передається у вкладеному контейнері `IFLA_INFO_DATA`. Ядро парсить ці атрибути функцією `br_changelink()` у файлі `net/bridge/br_netlink.c`.

| Параметр CLI (`ip link`) | Netlink-атрибут (`IFLA_BR_*`) | Тип даних ядра | Одиниці / Діапазон | Дефолт | Семантика ядра та вплив на комутацію |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `vlan_filtering` | `IFLA_BR_VLAN_FILTERING` | `__u8` | `0` (Off), `1` (On) | `0` | Активація перевірки та фільтрації тегів 802.1Q на портах. При `0` міст комутує кадри прозоро без перевірки внутрішньої таблиці VLAN. |
| `vlan_default_pvid` | `IFLA_BR_VLAN_DEFAULT_PVID` | `__u16` | `0` .. `4094` | `1` | VLAN ID, який автоматично призначається як PVID та Untagged новим slave-портам під час підключення до моста. Значення `0` вимикає автоматичне призначення. |
| `vlan_protocol` | `IFLA_BR_VLAN_PROTOCOL` | `__be16` | `0x8100` (802.1Q), `0x88A8` (802.1ad) | `0x8100` | Стандарт протоколу тегування: звичайні клієнтські C-VLAN (`0x8100`) або провайдерські S-VLAN / QinQ (`0x88A8`). |
| `vlan_stats_enabled` | `IFLA_BR_VLAN_STATS_ENABLED` | `__u8` | `0`, `1` | `0` | Увімкнення обліку лічильників пакетів та байтів окремо для кожного VLAN у комутаторі. |
| `vlan_stats_per_port` | `IFLA_BR_VLAN_STATS_PER_PORT`| `__u8` | `0`, `1` | `0` | Роздільний збір VLAN-статистики для кожного порту моста окремо. |
| `stp_state` | `IFLA_BR_STP_STATE` | `__u32` | `0`, `1`, `2` | `0` | Режим Spanning Tree: `0` (`BR_NO_STP`) — вимкнено (порти одразу у Forwarding); `1` (`BR_KERNEL_STP`) — вбудований у ядро 802.1D STP; `2` (`BR_USER_STP`) — делеговано простору користувача (RSTP/MSTP daemon, наприклад `mstpd`). |
| `priority` | `IFLA_BR_PRIORITY` | `__u16` | `0` .. `65535` | `32768` (`0x8000`) | Пріоритет моста в розрахунках STP. Визначає вибір Root Bridge (менше значення має вищий пріоритет). За стандартом задається з кроком 4096. |
| `forward_delay` | `IFLA_BR_FORWARD_DELAY` | `__u32` | `200` .. `3000` (соті с) | `1500` (15 с) | Час перебування порту у станах Listening та Learning перед переходом у Forwarding під час збіжності STP. |
| `hello_time` | `IFLA_BR_HELLO_TIME` | `__u32` | `100` .. `1000` (соті с) | `200` (2 с) | Інтервал періодичної відправки конфігураційних кадрів BPDU кореневим комутатором. |
| `max_age` | `IFLA_BR_MAX_AGE` | `__u32` | `600` .. `4000` (соті с) | `2000` (20 с) | Час зберігання BPDU до фіксації обриву лінка з Root Bridge. Повинно задовольняти умову: `2 * (forward_delay - 1) >= max_age >= 2 * (hello_time + 1)`. |
| `ageing_time` | `IFLA_BR_AGEING_TIME` | `__u32` | `0` .. `2^32 - 1` (соті с) | `30000` (300 с) | Час життя динамічно вивченого запису у FDB. При відсутності пакетів з цим Source MAC запис видаляється фоновим збирачем сміття `gc_timer`. |
| `group_fwd_mask` | `IFLA_BR_GROUP_FWD_MASK` | `__u16` | `0x0000` .. `0xFFFF` | `0x0000` | 16-бітна маска дозволу пересилання зарезервованих Link-Local адрес IEEE 802.1D (`01:80:C2:00:00:0X`). |
| `group_address` | `IFLA_BR_GROUP_ADDR` | 6 байтів | MAC-адреса | `01:80:c2:00:00:00` | MAC-адреса призначення для генерації та фільтрації службових кадрів STP BPDU. |
| `mcast_snooping` | `IFLA_BR_MCAST_SNOOPING` | `__u8` | `0`, `1` | `1` | Управління IGMP/MLD Snooping: `1` — фільтрація багатоадресного трафіку за базою MDB; `0` — лавинна розсилка (flood) мультикасту на всі порти. |
| `mcast_querier` | `IFLA_BR_MCAST_QUERIER` | `__u8` | `0`, `1` | `0` | Генерація періодичних запитів IGMP/MLD General Query мостом за відсутності апаратного мультикаст-маршрутизатора в L2-сегменті. |
| `mcast_igmp_version` | `IFLA_BR_MCAST_IGMP_VERSION` | `__u8` | `2`, `3` | `2` | Версія протоколу IGMP для обробки та генерації запитів мостом. |
| `mcast_mld_version` | `IFLA_BR_MCAST_MLD_VERSION` | `__u8` | `1`, `2` | `1` | Версія протоколу IPv6 Multicast Listener Discovery (MLD). |
| `mcast_query_interval` | `IFLA_BR_MCAST_QUERY_INTVL` | `__u64` | соті долі секунди | `12500` (125 с) | Інтервал між генераціями IGMP/MLD General Queries мостом у режимі `mcast_querier 1`. |
| `mcast_query_response_interval` | `IFLA_BR_MCAST_QUERY_RESPONSE_INTVL` | `__u64` | соті долі секунди | `1000` (10 с) | Максимальний очікуваний час відповіді хоста (Max Response Time) у запитах IGMP Query. |
| `mcast_membership_interval` | `IFLA_BR_MCAST_MEMBERSHIP_INTVL` | `__u64` | соті долі секунди | `26000` (260 с) | Час збереження активного стану групи в MDB без отримання нових звітів Membership Report. |
| `mcast_startup_query_count` | `IFLA_BR_MCAST_STARTUP_QUERY_CNT` | `__u32` | ціле число | `2` | Кількість швидких запитів IGMP Query, що відправляються під час запуску моста чи виборів Querier. |
| `mcast_stats_enabled` | `IFLA_BR_MCAST_STATS_ENABLED` | `__u8` | `0`, `1` | `0` | Збір детальної статистики мультикаст-трафіку та обробки IGMP/MLD груп. |
| `nf_call_iptables` | `IFLA_BR_NF_CALL_IPTABLES` | `__u8` | `0`, `1` | `0` (або `1` sysctl) | Локальний для екземпляра моста дозвіл перехоплення L2-трафіку хуками Netfilter IPv4. |
| `nf_call_ip6tables` | `IFLA_BR_NF_CALL_IP6TABLES` | `__u8` | `0`, `1` | `0` (або `1` sysctl) | Локальний дозвіл перехоплення L2-трафіку хуками Netfilter IPv6. |
| `nf_call_arptables` | `IFLA_BR_NF_CALL_ARPTABLES` | `__u8` | `0`, `1` | `0` (або `1` sysctl) | Локальний дозвіл перехоплення L2 ARP-кадрів хуками arptables. |
| `fdb_flush` | `IFLA_BR_FDB_FLUSH` | прапорець | порожній NLA | — | Очищення динамічних записів у таблиці FDB усього моста. |
| `multi_boolopt` | `IFLA_BR_MULTI_BOOLOPT` | `struct br_boolopt_multi` | бітові маски | — | Атомарне встановлення набору булевих опцій моста (`optval`, `optmask`). |

### 1.3. Детальний розбір бітової маски `group_fwd_mask`

Стандарт IEEE 802.1D резервує діапазон канальних адрес `01:80:C2:00:00:00` .. `01:80:C2:00:00:0F` для службових протоколів фізичного каналу. За замовчуванням міст поглинає ці кадри або передає локальному стеку хоста. Маска `group_fwd_mask` задає бітову карту адрес, які дозволено прозоро пересилати (Forward) через міст між портами:

```
Біт:    15  14  13  12  11  10   9   8   7   6   5   4   3   2   1   0
Адреса: 0F  0E  0D  0C  0B  0A  09  08  07  06  05  04  03  02  01  00
```

- **Біт 0 (`0x0001`) — `01:80:C2:00:00:00`**: Bridge Group Address (STP BPDU). Ядро блокує встановлення цього біта, якщо на мості активовано `stp_state 1`.
- **Біт 1 (`0x0002`) — `01:80:C2:00:00:01`**: IEEE 802.3x Ethernet Pause Frames. Заборонено стандартами канального рівня; ядро ігнорує встановлення цього біта.
- **Біт 2 (`0x0004`) — `01:80:C2:00:00:02`**: LACP / Slow Protocols (IEEE 802.3ad). Дозволяє пропуск агрегації каналів крізь віртуальний комутатор.
- **Біт 3 (`0x0008`) — `01:80:C2:00:00:03`**: IEEE 802.1X Port-Based Network Access Control (кадри EAPOL). Необхідно для автентифікації клієнтів за віртуальними мостами.
- **Біт 14 (`0x4000`) — `01:80:C2:00:00:0E`**: LLDP (Link Layer Discovery Protocol, IEEE 802.1AB). Дозволяє віртуальним машинам та контейнерам обмінюватися топологічними даними з фізичними світчами.

**Типові значення маски на практиці:**
```bash
# Пропуск тільки протоколу LLDP (біт 14 = 0x4000)
ip link set dev br0 type bridge group_fwd_mask 0x4000

# Пропуск LLDP (0x4000) та 802.1X EAPOL (0x0008) -> 0x4008
ip link set dev br0 type bridge group_fwd_mask 0x4008

# Пропуск LLDP (0x4000), 802.1X (0x0008) та LACP (0x0004) -> 0x400C
ip link set dev br0 type bridge group_fwd_mask 0x400c
```

### 1.4. Булеві опції `struct br_boolopt_multi`

Для швидкого та атомарного встановлення бітових прапорців моста через Netlink-атрибут `IFLA_BR_MULTI_BOOLOPT` використовується структура:

```c
struct br_boolopt_multi {
    __u32 optval;  /* Значення бітових прапорців (0 або 1 для кожного біта) */
    __u32 optmask; /* Маска бітів, які підлягають модифікації */
};
```

Доступні бітові константи (визначені в `<linux/if_bridge.h>`):
- `BR_BOOLOPT_NO_LL_LEARN` (біт 0): заборона навчання MAC-адрес із кадрів Link-Local;
- `BR_BOOLOPT_MCAST_VLAN_SNOOPING` (біт 1): роздільне ведення бази MDB окремо для кожного VLAN у комутаторі;
- `BR_BOOLOPT_MST_ENABLE` (біт 2): активація підтримки Multiple Spanning Tree Protocol (MSTP).

---

## 2. Параметри slave-портів моста (`IFLA_PROTINFO` / `IFLA_BRPORT_*`)

Приєднання інтерфейсу до моста виконується через встановлення атрибута `IFLA_MASTER` (числовий індекс `ifindex` моста) у повідомленні `RTM_SETLINK`. Вилучення порту виконується встановленням `IFLA_MASTER = 0` (або `nomaster` у CLI).

```bash
# Приєднання фізичного інтерфейсу eth0 до моста br0
ip link set dev eth0 master br0

# Видалення інтерфейсу зі складу комутатора
ip link set dev eth0 nomaster
```

Налаштування специфічних прапорців порту передаються всередині вкладеного контейнера `IFLA_PROTINFO`. Обробка виконується функцією ядра `br_setport()` у `net/bridge/br_netlink.c`.

### 2.1. Специфікація атрибутів порту (`IFLA_BRPORT_*`)

| Параметр CLI (`bridge link` / `ip link`) | Netlink-атрибут (`IFLA_BRPORT_*`) | Тип | Діапазон | Дефолт | Технічне призначення та вплив на обробку трафіку |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `hairpin` (mode) | `IFLA_BRPORT_MODE` | `__u8` | `on` (`1`), `off` (`0`) | `off` (`0`) | **Reflective Relay**: дозвіл надсилати кадри назад у той самий порт, з якого їх було отримано. Необхідно для зв'язку між контейнерами через hairpin NAT, взаємодії VM на спільній віртуальній мережевій карті або для зовнішнього комутатора VEPA (802.1Qbg). |
| `guard` | `IFLA_BRPORT_GUARD` | `__u8` | `on` (`1`), `off` (`0`) | `off` (`0`) | **BPDU Guard**: якщо на цей порт надходить хоча б один кадр BPDU, ядро негайно переводить порт у стан `BR_STATE_DISABLED`, блокуючи порт. Захищає мережу від підключення несанкціонованих комутаторів. |
| `root_block` | `IFLA_BRPORT_PROTECT` | `__u8` | `on` (`1`), `off` (`0`) | `off` (`0`) | **Root Guard**: забороняє цьому порту бути обраним як Root Port. Якщо пристрій за цим портом починає оголошувати себе кращим кореневим мостом (superior BPDU), порт переводиться у стан блокування. |
| `learning` | `IFLA_BRPORT_LEARNING` | `__u8` | `on` (`1`), `off` (`0`) | `on` (`1`) | **MAC Learning**: автоматичне вивчення адрес відправників (`Source MAC`) та оновлення таблиці FDB. При `off` динамічні записи для цього порту не створюються (використовується для портів із суворо фіксованими статичними FDB). |
| `learning_sync` | `IFLA_BRPORT_LEARNING_SYNC` | `__u8` | `on` (`1`), `off` (`0`) | `on` (`1`) | Апаратна синхронізація вивчених адрес з апаратними комутаційними чіпами (Switchdev). |
| `flood` | `IFLA_BRPORT_UNICAST_FLOOD` | `__u8` | `on` (`1`), `off` (`0`) | `on` (`1`) | **Unknown Unicast Flood**: розсилка кадрів із невідомим Unicast Destination MAC на цей порт. Якщо вимкнено (`off`), невідомі кадри відкидаються комутатором замість лавинної розсилки. |
| `mcast_flood` | `IFLA_BRPORT_MCAST_FLOOD` | `__u8` | `on` (`1`), `off` (`0`) | `on` (`1`) | Розсилка невідомого багатоадресного трафіку на даний порт за відсутності підписки в таблиці MDB. |
| `bcast_flood` | `IFLA_BRPORT_BCAST_FLOOD` | `__u8` | `on` (`1`), `off` (`0`) | `on` (`1`) | Розсилка широкомовного трафіку (`FF:FF:FF:FF:FF:FF`) на цей порт. При `off` широкомовні кадри на порт не надсилаються. |
| `neigh_suppress` | `IFLA_BRPORT_NEIGH_SUPPRESS` | `__u8` | `on` (`1`), `off` (`0`) | `off` (`0`) | **ARP/ND Suppression**: придушення надсилання локальних ARP-запитів та IPv6 Neighbor Solicitation через тунельні порти при роботі з EVPN/VXLAN оверлеями. Міст самостійно генерує ARP Reply / Neighbor Advertisement із локальної бази сусідів, запобігаючи широкомовному затопленню ядра мережі. |
| `neigh_vlan_suppress` | `IFLA_BRPORT_NEIGH_VLAN_SUPPRESS` | `__u8` | `on` (`1`), `off` (`0`) | `off` (`0`) | **VLAN-Aware Neighbor Suppression**: виконання фільтрації та придушення ARP/ND окремо з прив'язкою до ідентифікатора VLAN вхідного кадру. |
| `vlan_tunnel` | `IFLA_BRPORT_VLAN_TUNNEL` | `__u8` | `on` (`1`), `off` (`0`) | `off` (`0`) | **VLAN-to-Tunnel Mapping**: активація трансляції внутрішніх 802.1Q VLAN у тунельні ключі (VNI у VXLAN / Geneve) за таблицею `tunnel_info`. Дозволяє підключати тунельний інтерфейс у режимі `external` та комутувати множинні L2-сегменти через один тунельний порт. |
| `mcast_to_unicast` | `IFLA_BRPORT_MCAST_TO_UCAST` | `__u8` | `on` (`1`), `off` (`0`) | `off` (`0`) | **Multicast-to-Unicast (M2U)**: конвертація вихідного мультикаст-трафіку в послідовність юнікаст-кадрів окремо для кожного підписаного клієнта з бази MDB. Усуває падіння швидкості передачі у бездротових мережах (Wi-Fi) та оптимізує передачу через оверлейні канали. |
| `group_fwd_mask` | `IFLA_BRPORT_GROUP_FWD_MASK` | `__u16` | `0x0000` .. `0xFFFF` | `0x0000` | Індивідуальна маска дозволу пропуску зарезервованих Link-Local адрес IEEE 802.1D для конкретного порту (перевизначає глобальне налаштування моста). |
| `isolated` | `IFLA_BRPORT_ISOLATED` | `__u8` | `on` (`1`), `off` (`0`) | `off` (`0`) | **Port Isolation (Private VLAN)**: порти з цим прапорцем не можуть передавати трафік безпосередньо один одному. Комутація можлива лише між ізольованим портом та неізольованим (шлюз / аплінк). |
| `locked` | `IFLA_BRPORT_LOCKED` | `__u8` | `on` (`1`), `off` (`0`) | `off` (`0`) | **802.1X Port Lock**: блокування комутації та вивчення адрес до проходження авторизації хоста зовнішнім демоном 802.1X (доступно з ядра 5.18). |
| `mab` | `IFLA_BRPORT_MAB` | `__u8` | `on` (`1`), `off` (`0`) | `off` (`0`) | **MAC Authentication Bypass**: створення заблокованих записів у FDB з прапорцем `locked` для сповіщення простору користувача про появу нового неавторизованого MAC. |
| `mcast_router` | `IFLA_BRPORT_MCAST_ROUTER` | `__u8` | `0`, `1`, `2` | `1` | Роль мультикаст-маршрутизатора: `0` — вимкнено; `1` — динамічне виявлення за запитами IGMP/MLD Query; `2` — порт примусово позначений як мультикаст-маршрутизатор (отримує копію всього мультикасту). |
| `fastleave` | `IFLA_BRPORT_FAST_LEAVE` | `__u8` | `on` (`1`), `off` (`0`) | `off` (`0`) | **IGMP Fast Leave**: негайне видалення порту з підписки MDB при отриманні повідомлення IGMP Leave без відправки уточнювального запису Last Member Query. |
| `cost` | `IFLA_BRPORT_COST` | `__u32` | `1` .. `2^32 - 1` | авто | Вартість шляху STP Path Cost для даного лінка. За замовчуванням ядро призначає вартість за швидкістю лінка (100M = 19, 1G = 4, 10G = 2, 40G = 1). |
| `priority` | `IFLA_BRPORT_PRIORITY` | `__u16` | `0` .. `63` | `32` | Пріоритет порту STP для вибору Root Port при наявності паралельних однакових лінків. |
| `state` | `IFLA_BRPORT_STATE` | `__u8` | `0` .. `4` | `0` | Примусовий стан STP: `0` (`BR_STATE_DISABLED`), `1` (`BR_STATE_LISTENING`), `2` (`BR_STATE_LEARNING`), `3` (`BR_STATE_FORWARDING`), `4` (`BR_STATE_BLOCKING`). Використовується просторовими демонами RSTP/MSTP. |
| `backup_port` | `IFLA_BRPORT_BACKUP_PORT` | `__u32` | `ifindex` | `0` | Індекс резервного інтерфейсу для швидкого апаратного або програмного перемикання трафіку (Fast Failover) у разі падіння несучої (Link Carrier Down). |
| `mrp_ring_role` | `IFLA_BRPORT_MRP_RING_ROLE` | `__u8` | `0` .. `3` | `0` | Роль порту у протоколі кільцевого резервування Media Redundancy Protocol (IEC 62439-2): `0` Disabled, `1` Manager, `2` Client. |
| `mrp_in_role` | `IFLA_BRPORT_MRP_IN_ROLE` | `__u8` | `0` .. `3` | `0` | Роль порту інтерконекту в розширеннях MRP Interconnection (IEC 62439-2). |
| `flush` | `IFLA_BRPORT_FLUSH` | прапорець | порожній NLA | — | Негайне очищення всіх динамічно вивчених записів FDB, прив'язаних до цього конкретного порту. Використовується при падінні лінка або зміні топології. |

---

## 3. Специфікація підсистеми утиліти `bridge`

Утиліта `bridge` (пакет `iproute2`) є основним інструментом конфігурації комутаційних параметрів портів, таблиці комутації FDB, членства у VLAN та багатоадресної бази MDB.

### 3.1. Керування прапорцями портів: `bridge link`

```bash
# Синтаксис команди bridge link set
bridge link set dev <DEV> [cost <COST>] [priority <PRIO>] [state <STATE>] \
    [guard {on|off}] [hairpin {on|off}] [fastleave {on|off}] [root_block {on|off}] \
    [learning {on|off}] [learning_sync {on|off}] [flood {on|off}] \
    [mcast_flood {on|off}] [bcast_flood {on|off}] [mcast_router <0|1|2>] \
    [isolated {on|off}] [neigh_suppress {on|off}] [neigh_vlan_suppress {on|off}] \
    [vlan_tunnel {on|off}] [mcast_to_unicast {on|off}] [group_fwd_mask <MASK>] \
    [locked {on|off}] [mab {on|off}] [backup_port <DEV>] [self] [master]

# Перегляд стану та властивостей портів моста
bridge link show [dev <DEV>]
```

**Практичні приклади конфігурації:**
```bash
# 1. Налаштування клієнтського ізольованого порту з захистом BPDU Guard
bridge link set dev veth-cust1 guard on isolated on flood off

# 2. Активація Hairpin на порту віртуальної машини для комутації між її vNIC
bridge link set dev tap0 hairpin on

# 3. Призначення аплінк-порту eth1 постійним мультикаст-маршрутизатором
bridge link set dev eth1 mcast_router 2

# 4. Активація ARP/ND Suppression та VLAN Tunneling на VXLAN-порті оверлею EVPN
bridge link set dev vxlan0 neigh_suppress on vlan_tunnel on

# 5. Активація конвертації Multicast-to-Unicast на Wi-Fi інтерфейсі ap0
bridge link set dev ap0 mcast_to_unicast on
```

---

### 3.2. Таблиця комутації FDB: `bridge fdb`

Команда `bridge fdb` взаємодіє з ядром через повідомлення `RTM_NEWNEIGH`, `RTM_DELNEIGH` та `RTM_GETNEIGH` із сімейством `AF_BRIDGE`.

```bash
# Синтаксис додавання / модифікації запису в FDB
bridge fdb { add | append | del | replace } <LLADDR> dev <DEV> \
    [ vlan <VID> ] [ pvid ] [ self ] [ master ] \
    [ static | permanent | dynamic | temp ] [ local ] \
    [ dst <IP> ] [ port <PORT> ] [ vni <VNI> ] [ via <DEV> ] \
    [ sticky ] [ router ]

# Відображення поточної таблиці FDB
bridge fdb show [ dev <DEV> ] [ br <BRNAME> ] [ brport <DEV> ] [ vlan <VID> ]

# Отримання запису для конкретної MAC-адреси
bridge fdb get <LLADDR> [ br <BRNAME> ] [ vlan <VID> ]
```

#### Стани та прапорці записів FDB

- **`permanent`** (`NUD_PERMANENT`, `0x80`): постійний статичний запис, створений адміністратором або SDN-контролером. Не застаріває і не видаляється збирачем сміття.
- **`static`** (`NUD_NOARP` / `NUD_STATIC`, `0x40`): статичний запис без перевірки ARP, створений Switchdev або ядром для прив'язки локальних портів.
- **`dynamic`** (`NUD_REACHABLE`, `0x02`): динамічно вивчений запис через механізм MAC Learning. Підлягає таймеру застарівання `ageing_time`.
- **`temp`** (`NUD_STALE`, `0x04`): тимчасовий запис з обмеженим часом життя.
- **`local`**: прапорець локальної доставки. Кадри з цим `Destination MAC` передаються локальному стеку ядра (L3). Створюється автоматично для MAC-адрес моста та його портів.
- **`master`** (`NTF_MASTER`, `0x04`): вносить запис у програмну таблицю FDB ядра Linux Bridge.
- **`self`** (`NTF_SELF`, `0x02`): вносить запис безпосередньо в апаратну таблицю мережевої карти або Switchdev ASIC.
- **`sticky`** (`NTF_STICKY`, `0x40`): забороняє автоматичну міграцію запису на інший порт при появі однакового Source MAC.
- **`router`** (`NTF_ROUTER`, `0x80`): адреса призначення належить маршрутизатору.
- **`extern_learn`** (`NTF_EXT_LEARNED`, `0x10`): запис внесено зовнішнім контролером (наприклад, FRR EVPN BGP або OVN).
- **`offload`** (`NTF_OFFLOADED`, `0x20`): комутаційне правило успішно вивантажено в апаратний чіп комутатора.

**Приклади використання `bridge fdb`:**
```bash
# 1. Додавання постійної статичної прив'язки MAC до порту veth1 у VLAN 100
bridge fdb add 52:54:00:12:34:56 dev veth1 master static vlan 100

# 2. Додавання запису віддаленого VTEP для тунелювання кадру у VXLAN (VNI 10000)
bridge fdb add 02:00:00:00:00:01 dev vxlan0 dst 192.168.1.50 port 4789 vni 10000 self

# 3. Видалення статичного запису
bridge fdb del 52:54:00:12:34:56 dev veth1 master vlan 100
```

---

### 3.3. Фільтрація VLAN: `bridge vlan`

Керування таблицею членства портів у віртуальних локальних мережах стандарту IEEE 802.1Q. Вимагає попередньої активації `vlan_filtering 1` на мості.

```bash
# Додавання та видалення членства у VLAN
bridge vlan { add | del } dev <DEV> vid <VID>[-<VID>] \
    [ pvid ] [ untagged ] [ self ] [ master ]

# Перегляд таблиці конфігурації VLAN
bridge vlan show [ dev <DEV> ] [ vid <VID> ]
```

#### Прапорці структури `struct bridge_vlan_info`

- **`pvid`** (`BRIDGE_VLAN_INFO_PVID`, `0x0002`): **Port VLAN ID**. Усі вхідні нетеговані кадри (Ingress Untagged), отримані на цьому порту, автоматично маркуються цим ідентифікатором VLAN під час внутрішньої обробки комутатором. На одному порту може бути призначений лише один PVID.
- **`untagged`** (`BRIDGE_VLAN_INFO_UNTAGGED`, `0x0004`): наказує мосту видаляти 4-байтний заголовок 802.1Q під час передачі кадру з цього порту (Egress). Використовується для створення портів доступу (Access Ports).
- **`master`** (`BRIDGE_VLAN_INFO_MASTER`, `0x0001`): запис застосовується до таблиці конфігурації програмного моста в ядрі.
- **`self`**: запис застосовується до апаратної таблиці драйвера мережевого адаптера або чіпа Switchdev.
- **Діапазони `vid VID_START-VID_END`**: використовують внутрішні бінарні прапорці `RANGE_BEGIN` (`0x0008`) та `RANGE_END` (`0x0010`) для оптимізованого додавання сотень VLAN одним Netlink-повідомленням.

**Приклади налаштування портів різних типів:**
```bash
# 1. Налаштування порту доступу (Access Port у VLAN 10):
# Видаляємо дефолтний VLAN 1, призначаємо VLAN 10 як PVID та Untagged
bridge vlan del dev veth-acc vid 1
bridge vlan add dev veth-acc vid 10 pvid untagged

# 2. Налаштування магістрального порту (Trunk Port, що пропускає VLAN 10, 20 та 100-110):
bridge vlan del dev eth0 vid 1
bridge vlan add dev eth0 vid 10
bridge vlan add dev eth0 vid 20
bridge vlan add dev eth0 vid 100-110

# 3. Налаштування гібридного порту (Hybrid Port: Untagged у VLAN 5, Tagged у VLAN 50):
bridge vlan del dev eth1 vid 1
bridge vlan add dev eth1 vid 5 pvid untagged
bridge vlan add dev eth1 vid 50

# 4. Налаштування інтерфейсу самого моста (L3 Management Interface хоста у VLAN 10):
bridge vlan add dev br0 vid 10 pvid untagged self
```

#### 3.3.1. Тунельний мапінг VLAN (VLAN-to-Tunnel Mapping: `tunnel_info`)

При інтеграції Linux Bridge з оверлейними тунелями VXLAN та Geneve у режимі зовнішніх метаданих (`ip link add vxlan0 type vxlan external`) один тунельний інтерфейс може одночасно передавати кадри сотень різних ізольованих L2-доменів. Для цього на slave-порті моста активується режим `vlan_tunnel on`, а зв'язок між внутрішніми 802.1Q тегами моста (`vid`) та зовнішніми ідентифікаторами віртуальних сегментів тунелю (`Tunnel ID` / `VNI`) задається через опцію `tunnel_info`:

```bash
# Синтаксис призначення тунельного мапінгу VLAN
bridge vlan { add | del } dev <DEV> vid <VID>[-<VID>] tunnel_info id <TUNNEL_ID>[-<TUNNEL_ID>]

# Перегляд поточної таблиці відповідності VLAN <-> Tunnel VNI
bridge vlan tunnelshow [ dev <DEV> ] [ vid <VID> ]
```

**Практичні приклади тунельного мапінгу:**
```bash
# 1. Прив'язка внутрішнього VLAN 100 моста до зовнішнього VXLAN VNI 10000 на slave-інтерфейсі vxlan0
bridge vlan add dev vxlan0 vid 100 tunnel_info id 10000

# 2. Атомарне призначення неперервного діапазону VLAN 200-250 на діапазон VNI 20200-20250
bridge vlan add dev vxlan0 vid 200-250 tunnel_info id 20200-20250

# 3. Перевірка налаштованих трансляцій для інтерфейсу vxlan0
bridge vlan tunnelshow dev vxlan0
# Вивід:
# port    vlan ids        tunnel id
# vxlan0  100             10000
#         200-250         20200-20250
```

---

### 3.4. Багатоадресна база даних: `bridge mdb`

База даних MDB (Multicast Database) містить динамічні та статичні записи про порти моста, за якими є активні отримувачі багатоадресного трафіку IPv4 (IGMPv1/v2/v3), IPv6 (MLDv1/v2) або канальних L2-мультикастів. Коли на мості увімкнено `mcast_snooping 1`, міст замість розсилки мультикасту на всі порти (Flooding) селективно копіює кадри виключно на slave-порти, зафіксовані в MDB для даної групи та VLAN.

```bash
# Синтаксис керування записами в MDB
bridge mdb { add | del | replace } dev <BRNAME> port <DEV> grp <GROUP_ADDR> \
    [ permanent | temp ] [ vid <VID> ] [ src <SOURCE_IP> ] \
    [ filter_mode { include | exclude } ] [ proto <PROTO> ]

# Відображення поточної таблиці багатоадресних підписок із деталізацією таймерів та джерел
bridge [-d] [-s] mdb show [ dev <BRNAME> ]
```

#### 3.4.1. Детальна специфікація параметрів та прапорців `bridge mdb`

- **`dev <BRNAME>`**: ім'я віртуального моста, що володіє базою MDB (`br0`);
- **`port <DEV>`**: slave-інтерфейс моста, до якого підключено отримувача багатоадресного трафіку (`eth1`, `veth-client`, `vxlan0`);
- **`grp <GROUP_ADDR>`**: багатоадресна адреса групи:
  - IPv4 Multicast: `224.0.0.0/4` (наприклад, `239.255.1.1`, `232.0.1.10`);
  - IPv6 Multicast: `ff00::/8` (наприклад, `ff0e::1`, `ff02::1:ff12:3456`);
  - L2 Multicast MAC: `01:00:5e:xx:xx:xx` (IPv4) або `33:33:xx:xx:xx:xx` (IPv6);
- **`permanent`**: статичний запис, створений вручну або SDN-контролером. Не застаріває і не видаляється таймерами;
- **`temp`**: динамічний запис, створений ядром під час снупінгу звітів IGMP/MLD Report. Оновлюється кожним новим звітом хоста і видаляється, якщо протягом інтервалу `mcast_membership_interval` звітів не надходило;
- **`vid <VID>`**: ідентифікатор VLAN ID (`1` .. `4094`). Дозволяє комутатору вести повністю ізольовані бази підписок MDB окремо для кожного віртуального сегмента (при активованій опції `mcast_vlan_snooping 1`);
- **`src <SOURCE_IP>`**: конкретна IP-адреса джерела мультикаст-потоку для фільтрації Source-Specific Multicast (SSM / IGMPv3 / MLDv2);
- **`filter_mode { include | exclude }`**: режим фільтрації джерел для групи:
  - `include` (`MCAST_INCLUDE`, `1`): пересилати кадри мультикаст-групи `grp` на даний порт **лише** тоді, коли IP-адреса відправника входить до переліку дозволених джерел (`src`);
  - `exclude` (`MCAST_EXCLUDE`, `2`): пересилати кадри мультикаст-групи від усіх джерел, **крім** вказаних у списку заблокованих (якщо список джерел порожній — це стан `(*, G)`, тобто прийом від будь-якого відправника);
- **`proto <PROTO>`**: ідентифікатор протоколу керування або маршрутизації, який створив запис (`static`, `kernel`, `bgp`, `mrouted` тощо).

#### 3.4.2. Практичні приклади конфігурації `bridge mdb`

```bash
# 1. Додавання статичного запису Any-Source Multicast (*, G) для потоку IPTV у VLAN 100
bridge mdb add dev br0 port eth1 grp 239.255.1.1 permanent vid 100

# 2. Додавання запису Source-Specific Multicast (S, G) для джерела 192.168.10.50 в IGMPv3
bridge mdb add dev br0 port eth2 grp 232.1.1.10 src 192.168.10.50 permanent vid 100 filter_mode include

# 3. Додавання IPv6 багатоадресної підписки MLDv2
bridge mdb add dev br0 port eth3 grp ff0e::1 permanent vid 20

# 4. Видалення статичного запису з MDB
bridge mdb del dev br0 port eth1 grp 239.255.1.1 vid 100

# 5. Детальний перегляд бази MDB з відображенням прапорців, таймерів та списків джерел
bridge -d -s mdb show dev br0
```

**Приклад розбору детального виводу `bridge -d -s mdb show`:**
```text
dev br0 port eth1 grp 239.255.1.1 vid 100 temp filter_mode exclude timer 245.12
    flags: offload
dev br0 port eth2 grp 232.1.1.10 vid 100 permanent filter_mode include
    src 192.168.10.50 timer 0.00 flags: permanent,offload
router port eth3 dev br0 master br0 type temp timer 180.45
```

- `temp filter_mode exclude timer 245.12`: динамічна підписка `(*, G)` зі зворотним відліком таймера життя (245.12 секунди до застарівання);
- `flags: offload`: запис успішно вивантажено в апаратну комутаційну матрицю ASIC через Switchdev;
- `router port eth3`: порт `eth3` автоматично визначено як порт мультикаст-маршрутизатора через отримані на ньому запити IGMP Query (усі мультикаст-пакети з інших портів безумовно реплікуються в `eth3`).

---

## 4. Порівняльна матриця: застарілий `brctl` проти сучасних `ip link` / `bridge`

Утиліта `brctl` (пакет `bridge-utils`) використовувала блокувальні системні виклики `ioctl` (`SIOCBRADDBR`, `SIOCDEVPRIVATE`), не підтримувала фільтрацію VLAN 802.1Q, не вміла працювати з Switchdev і була повністю виведена з експлуатації в сучасному мережевому стеку Linux.

| Операція керування | Застаріла утиліта `brctl` (`ioctl`) | Сучасна утиліта `iproute2` (`rtnetlink`) |
| :--- | :--- | :--- |
| **Створення моста** | `brctl addbr br0` | `ip link add name br0 type bridge` |
| **Видалення моста** | `brctl delbr br0` | `ip link del dev br0` |
| **Додавання порту** | `brctl addif br0 eth0` | `ip link set dev eth0 master br0` |
| **Вилучення порту** | `brctl delif br0 eth0` | `ip link set dev eth0 nomaster` |
| **Увімкнення STP** | `brctl stp br0 on` | `ip link set dev br0 type bridge stp_state 1` |
| **Вимкнення STP** | `brctl stp br0 off` | `ip link set dev br0 type bridge stp_state 0` |
| **Пріоритет моста STP** | `brctl setbridgeprio br0 4096` | `ip link set dev br0 type bridge priority 4096` |
| **Затримка Forward Delay** | `brctl setfd br0 15` | `ip link set dev br0 type bridge forward_delay 1500` *(соті с)* |
| **Інтервал Hello Time** | `brctl sethello br0 2` | `ip link set dev br0 type bridge hello_time 200` *(соті с)* |
| **Таймаут Max Age** | `brctl setmaxage br0 20` | `ip link set dev br0 type bridge max_age 2000` *(соті с)* |
| **Час застарівання FDB** | `brctl setageing br0 300` | `ip link set dev br0 type bridge ageing_time 30000` *(соті с)* |
| **Вартість шляху порту** | `brctl setpathcost br0 eth0 4` | `bridge link set dev eth0 cost 4` |
| **Пріоритет порту STP** | `brctl setportprio br0 eth0 32`| `bridge link set dev eth0 priority 32` |
| **Перегляд списку мостів** | `brctl show` | `ip link show type bridge` |
| **Перегляд стану STP** | `brctl showstp br0` | `ip -d link show dev br0` / `bridge -d link show` |
| **Перегляд таблиці FDB** | `brctl showmacs br0` | `bridge fdb show br br0` |
| **Фільтрація VLAN 802.1Q** | *Не підтримується* | `bridge vlan add dev eth0 vid 10 pvid untagged` |
| **Керування мультикастом MDB**| *Не підтримується* | `bridge mdb show` / `bridge mdb add ...` |
| **Ізоляція портів / Private VLAN**| *Не підтримується* | `bridge link set dev eth0 isolated on` |
| **Захист BPDU Guard** | *Не підтримується* | `bridge link set dev eth0 guard on` |
| **Режим Hairpin** | *Не підтримується* | `bridge link set dev eth0 hairpin on` |

---

## 5. Структури ядра та бінарний протокол RTNETLINK

Для прямої низькорівневої програмної взаємодії із простору користувача використовуються структури заголовків та атрибутів, визначені у заголовкових файлах `<linux/rtnetlink.h>`, `<linux/if_link.h>`, `<linux/if_bridge.h>`, `<linux/neighbour.h>` та `<linux/netlink.h>`.

### 5.1. Формат бінарного кадру Netlink (TLV-інкапсуляція)

Усі повідомлення RTNETLINK складаються з фіксованого заголовка `struct nlmsghdr`, після якого розміщується протокольний заголовок підсистеми (`struct ifinfomsg`, `struct ndmsg` або `struct br_port_msg`) та послідовність атрибутів Type-Length-Value (TLV), вирівняних по 4 байти за допомогою макросів `NLA_ALIGN()` / `RTA_ALIGN()`.

```c
struct nlmsghdr {
    __u32 nlmsg_len;   /* Повна довжина повідомлення включно із заголовком */
    __u16 nlmsg_type;  /* Тип операції: RTM_NEWLINK, RTM_SETLINK, RTM_NEWNEIGH тощо */
    __u16 nlmsg_flags; /* Прапорці запиту: NLM_F_REQUEST, NLM_F_ACK, NLM_F_CREATE тощо */
    __u32 nlmsg_seq;   /* Порядковий номер транзакції (sequence number) */
    __u32 nlmsg_pid;   /* Ідентифікатор сокетного порту відправника (0 для ядра) */
};

struct nlattr {
    __u16 nla_len;     /* Довжина атрибута (заголовок 4 байти + корисне навантаження) */
    __u16 nla_type;    /* Тип атрибута (бітова маска NLA_F_NESTED, NLA_F_NET_BYTEORDER) */
};
```

**Ключові прапорці заголовка `nlmsg_flags`:**
- `NLM_F_REQUEST` (`0x01`): обов'язковий прапорець для всіх запитів від простору користувача до ядра;
- `NLM_F_ACK` (`0x04`): вимога надіслати підтвердження успішного виконання (`NLMSG_ERROR` із кодом помилки `0`);
- `NLM_F_CREATE` (`0x400`): створити новий об'єкт (міст, запис FDB, VLAN), якщо він відсутній;
- `NLM_F_EXCL` (`0x200`): повернути помилку `-EEXIST`, якщо об'єкт уже існує;
- `NLM_F_REPLACE` (`0x100`): атомарно замінити наявний об'єкт новим;
- `NLM_F_DUMP` (`NLM_F_ROOT | NLM_F_MATCH` = `0x300`): отримати повний список об'єктів підсистеми.

---

### 5.2. Повідомлення Link Layer (`RTM_NEWLINK` / `RTM_SETLINK` / `RTM_DELLINK`)

Заголовок операцій конфігурації лінків використовує структуру `struct ifinfomsg`:

```c
struct ifinfomsg {
    unsigned char  ifi_family; /* AF_UNSPEC або AF_BRIDGE */
    unsigned char  __ifi_pad;
    unsigned short ifi_type;   /* Тип канального пристрою ARPHRD_* */
    int            ifi_index;  /* Числовий індекс інтерфейсу (ifindex, 0 при створенні) */
    unsigned int   ifi_flags;  /* Прапорці IFF_UP, IFF_BROADCAST, IFF_PROMISC тощо */
    unsigned int   ifi_change; /* Маска бітів у ifi_flags, які змінюються (0xFFFFFFFF) */
};
```

#### Ієрархія атрибутів при створенні моста (`RTM_NEWLINK` + `NLM_F_CREATE`)

Для створення екземпляра моста формується повідомлення з такою вкладеною структурою атрибутів:

```
[struct nlmsghdr] (nlmsg_type = RTM_NEWLINK, flags = NLM_F_REQUEST | NLM_F_ACK | NLM_F_CREATE | NLM_F_EXCL)
[struct ifinfomsg] (ifi_family = AF_UNSPEC, ifi_index = 0)
  ├── IFLA_IFNAME -> "br0" (рядок імені створюваного моста)
  └── IFLA_LINKINFO (вкладений контейнер типу інтерфейсу)
        ├── IFLA_INFO_KIND -> "bridge" (ідентифікатор модуля драйвера)
        └── IFLA_INFO_DATA (вкладений контейнер параметрів моста)
              ├── IFLA_BR_VLAN_FILTERING -> __u8 (1)
              ├── IFLA_BR_PRIORITY -> __u16 (16384)
              └── IFLA_BR_FORWARD_DELAY -> __u32 (1500)
```

#### Ієрархія атрибутів при підключенні та налаштуванні slave-порту (`RTM_SETLINK`)

```
[struct nlmsghdr] (nlmsg_type = RTM_SETLINK, flags = NLM_F_REQUEST | NLM_F_ACK)
[struct ifinfomsg] (ifi_family = AF_UNSPEC, ifi_index = eth0_ifindex)
  ├── IFLA_MASTER -> __u32 (br0_ifindex)
  └── IFLA_PROTINFO (вкладений контейнер специфічних параметрів порту)
        ├── IFLA_BRPORT_LEARNING -> __u8 (1)
        ├── IFLA_BRPORT_UNICAST_FLOOD -> __u8 (0)
        ├── IFLA_BRPORT_GUARD -> __u8 (1)
        └── IFLA_BRPORT_ISOLATED -> __u8 (1)
```

---

### 5.3. Повідомлення керування FDB (`RTM_NEWNEIGH` / `RTM_DELNEIGH` / `RTM_GETNEIGH`)

Підсистема FDB комутатора інтегрована в підсистему Neighbor ядра. Заголовок повідомлення містить структуру `struct ndmsg`:

```c
struct ndmsg {
    __u8  ndm_family;   /* Обов'язково AF_BRIDGE */
    __u8  ndm_pad1;
    __u16 ndm_pad2;
    __s32 ndm_ifindex;  /* Індекс slave-порту (або моста для локальних адрес) */
    __u16 ndm_state;    /* Стан запису: NUD_PERMANENT, NUD_REACHABLE, NUD_NOARP */
    __u8  ndm_flags;    /* Прапорці обробки: NTF_MASTER, NTF_SELF, NTF_EXT_LEARNED */
    __u8  ndm_type;     /* Тип маршруту (RTN_UNICAST) */
};
```

#### Детальна специфікація станів `ndm_state` (Neighbor States)

- **`NUD_PERMANENT` (`0x80`)**: статичний постійний запис. Ніколи не видаляється таймером застарівання `ageing_time`. Кадри пересилаються на `ndm_ifindex` безумовно.
- **`NUD_NOARP` (`0x40`)**: статичний запис без перевірки валідності. Використовується ядром для фіксації локальних MAC-адрес slave-інтерфейсів комутатора.
- **`NUD_REACHABLE` (`0x02`)**: динамічно вивчений запис у стані валідності. При отриманні нових кадрів із цим Source MAC оновлюється позначка `updated = jiffies`. Якщо активність відсутня протягом `ageing_time`, ядро переводить запис у `NUD_STALE` або видаляє з таблиці.
- **`NUD_STALE` (`0x04`)**: застарілий запис, який очікує очищення збирачем сміття.
- **`NUD_FAILED` (`0x20`)**: стан помилки або заблокований запис.

#### Детальна специфікація прапорців `ndm_flags` (Neighbor Flags)

- **`NTF_MASTER` (`0x04`)**: наказує застосувати операцію до програмної хеш-таблиці FDB моста в оперативній пам'яті ядра (`struct net_bridge`).
- **`NTF_SELF` (`0x02`)**: наказує передати команду безпосередньо драйверу пристрою або апаратному комутаційному чіпу Switchdev.
- **`NTF_EXT_LEARNED` (`0x10`)**: позначка того, що запис вивчено зовнішнім просторовим контролером (BGP EVPN, OVN, FRRouting). Ядро не скидає такі записи за стандартним таймером `ageing_time`.
- **`NTF_OFFLOADED` (`0x20`)**: повертається ядром у відповідях `RTM_GETNEIGH` / подіях `RTM_NEWNEIGH`, сигналізуючи про успішне вивантаження комутаційного правила в апаратну таблицю TCAM чіпа.
- **`NTF_STICKY` (`0x40`)**: блокує автоматичну міграцію MAC-адреси на інший порт при отриманні підроблених або дублюючих кадрів.
- **`NTF_ROUTER` (`0x80`)**: вказує, що хост за цією MAC-адресою є L3-маршрутизатором.

#### Специфікація атрибутів FDB (`NDA_*`)

Після заголовка `struct ndmsg` передаються специфічні атрибути:

| Атрибут (`NDA_*`) | Числовий код | Тип даних ядра | Семантика та технічне призначення |
| :--- | :---: | :--- | :--- |
| `NDA_UNSPEC` | `0` | — | Невизначений тип атрибута. |
| `NDA_DST` | `1` | `__be32` або `struct in6_addr` | IP-адреса призначення віддаленого VTEP (для записів оверлейних мереж VXLAN / Geneve). |
| `NDA_LLADDR` | `2` | 6 байтів | Фізична MAC-адреса вузла (`00:11:22:33:44:55`). |
| `NDA_CACHEINFO` | `3` | `struct nda_cacheinfo` | Статистика часу життя: `ndm_confirmed`, `ndm_used`, `ndm_updated` (у jiffies) та `ndm_refcnt`. |
| `NDA_PROBES` | `4` | `__u32` | Кількість спроб зондування стану сусідів. |
| `NDA_VLAN` | `5` | `__u16` | Ідентифікатор VLAN ID (`1` .. `4094`), до якого прив'язана ця MAC-адреса у комутаторі. |
| `NDA_PORT` | `6` | `__be16` | Номер UDP-порту віддаленого VTEP (дефолт `4789` для VXLAN) у мережевому порядку байтів. |
| `NDA_VNI` | `7` | `__u32` | Ідентифікатор віртуального сегмента VXLAN Network Identifier (24 біти). |
| `NDA_IFINDEX` | `8` | `__u32` | Вихідний інтерфейс пересилання (підлеглий порт моста). |
| `NDA_MASTER` | `9` | `__u32` | Індекс `ifindex` батьківського моста, що володіє цією таблицею FDB. |
| `NDA_LINK_NETNSID`| `10` | `__s32` | Ідентифікатор мережевого простору імен (netns ID). |
| `NDA_FLAGS_EXT` | `14` | `__u32` | Розширені прапорці: `NTF_EXT_LOCKED` (`0x01`) для портів із контролем доступу 802.1X. |

---

### 5.4. Підсистема VLAN Filtering через Netlink

Керування таблицею членства у VLAN здійснюється надсиланням повідомлень `RTM_SETLINK` (для додавання) або `RTM_DELLINK` (для видалення) з атрибутом `IFLA_AF_SPEC`.

#### Структура Netlink-запиту для VLAN Filtering

Контейнер `IFLA_AF_SPEC` містить один або декілька вкладених атрибутів:
1. `IFLA_BRIDGE_FLAGS` (`__u16`): прапорці цілі призначення:
   - `BRIDGE_FLAGS_MASTER` (`1`): застосувати конфігурацію до ядра моста;
   - `BRIDGE_FLAGS_SELF` (`2`): передати драйверу фізичної мережевої карти або Switchdev.
2. `IFLA_BRIDGE_VLAN_INFO`: бінарна структура `struct bridge_vlan_info`.

```c
struct bridge_vlan_info {
    __u16 flags; /* Бітові прапорці BRIDGE_VLAN_INFO_* */
    __u16 vid;   /* Номер VLAN ID (1..4094) або початковий VID діапазону */
};
```

#### Специфікація прапорців `flags` у `struct bridge_vlan_info`

| Прапорець | Бітове значення | Числовий код | Семантика обробки трафіку ядром |
| :--- | :---: | :---: | :--- |
| `BRIDGE_VLAN_INFO_MASTER` | `1 << 0` | `0x0001` | Операція застосовується до внутрішньої таблиці моста в ядрі. |
| `BRIDGE_VLAN_INFO_PVID` | `1 << 1` | `0x0002` | **Port VLAN ID**: усім вхідним нетегованим кадрам на цьому порту призначається цей `vid`. На кожному порту може бути лише один активний PVID. |
| `BRIDGE_VLAN_INFO_UNTAGGED` | `1 << 2` | `0x0004` | **Egress Untagged**: заголовок 802.1Q видаляється з кадру під час передачі через цей порт. |
| `BRIDGE_VLAN_INFO_RANGE_BEGIN` | `1 << 3` | `0x0008` | Початок неперервного діапазону VLAN ID. |
| `BRIDGE_VLAN_INFO_RANGE_END` | `1 << 4` | `0x0010` | Кінець неперервного діапазону VLAN ID. |
| `BRIDGE_VLAN_INFO_BRENTRY` | `1 << 5` | `0x0020` | Запис відноситься до самого віртуального інтерфейсу моста (глобальний контекст комутатора `struct net_bridge_vlan`). |
| `BRIDGE_VLAN_INFO_ONLY_OPTS` | `1 << 6` | `0x0040` | Модифікувати лише додаткові опції VLAN (наприклад, стан IGMP Snooping для цього VLAN) без зміни членства портів. |

#### Додавання діапазону VLAN одним повідомленням

Для атомарного додавання діапазону (наприклад, VLAN 100-200) формується блок із двох послідовних атрибутів `IFLA_BRIDGE_VLAN_INFO` всередині одного контейнера `IFLA_AF_SPEC`:
- Перший атрибут: `flags = BRIDGE_VLAN_INFO_RANGE_BEGIN`, `vid = 100`;
- Другий атрибут: `flags = BRIDGE_VLAN_INFO_RANGE_END`, `vid = 200`.

Ядро розгортає цей діапазон у циклі функції `br_vlan_add()`, суттєво заощаджуючи час на передачу Netlink-повідомлень через системні виклики.

#### 5.4.3. Специфікація атрибутів VLAN Tunneling (`IFLA_BRIDGE_VLAN_TUNNEL_INFO`)

Для реалізації мапінгу 802.1Q VLAN у тунельні сегменти VXLAN / Geneve повідомлення `RTM_SETLINK` передає всередині `IFLA_AF_SPEC` контейнер `IFLA_BRIDGE_VLAN_TUNNEL_INFO`:

| Netlink-атрибут | Тип даних ядра | Семантика та технічне призначення |
| :--- | :---: | :--- |
| `IFLA_BRIDGE_VLAN_TUNNEL_ID` | `__u32` | 24-бітний ідентифікатор оверлейного тунелю (VXLAN Network Identifier, VNI або Geneve Tunnel Key). |
| `IFLA_BRIDGE_VLAN_TUNNEL_VID` | `__u16` | Внутрішній ідентифікатор VLAN ID (`1` .. `4094`) комутатора Linux Bridge. |
| `IFLA_BRIDGE_VLAN_TUNNEL_FLAGS` | `__u16` | Бітові прапорці для діапазонів (`BRIDGE_VLAN_INFO_RANGE_BEGIN`, `BRIDGE_VLAN_INFO_RANGE_END`). |

**Механізм трансляції в ядрі (`net/bridge/br_vlan_tunnel.c`):**
1. **Вхідний шлях (Ingress з VXLAN-порту):**  
   Коли тунельний драйвер (`vxlan`, створений з опцією `external`) приймає декапсульований Ethernet-кадр, він заповнює службові метадані `skb_tunnel_info(skb)`. Функція `br_vlan_tunnel_lookup()` знаходить відповідний `tunnel_id` у таблиці `vlan_tunnel_info` порту моста і заміщує його внутрішнім тегом `vlan_tci = vid`. Кадр надходить у комутаційну матрицю моста вже з внутрішнім VLAN.
2. **Вихідний шлях (Egress у VXLAN-порт):**  
   Функція `br_handle_vlan()` перевіряє внутрішній VID кадру. Якщо на вихідному порту активний `vlan_tunnel 1`, міст виконує зворотний пошук `vid -> tunnel_id`, формує метадані призначення `dst_metadata` для вихідного тунелю та видаляє внутрішній заголовок 802.1Q (якщо виставлено `BRIDGE_VLAN_INFO_UNTAGGED`).

---

### 5.5. Підсистема багатоадресної бази MDB (`RTM_NEWMDB` / `RTM_DELMDB` / `RTM_GETMDB`)

Програмний інтерфейс Netlink для керування багатоадресною базою комутатора забезпечує додавання статичних підписок, моніторинг динамічно вивчених груп IGMP/MLD, отримання стану мультикаст-маршрутизаторів та вивантаження правил у комутаційні чіпи Switchdev.

#### 5.5.1. Типи повідомлень MDB Netlink

- **`RTM_NEWMDB` (`84` / `0x54`)**: створення нового або оновлення наявного запису підписки на багатоадресну групу;
- **`RTM_DELMDB` (`85` / `0x55`)**: вилучення запису групи або конкретного джерела з бази MDB;
- **`RTM_GETMDB` (`86` / `0x56`)**: запит на отримання (дамп) повної таблиці MDB моста разом зі списками джерел SSM та портами мультикаст-маршрутизаторів.

#### 5.5.2. Структури даних заголовків та записів MDB

Кожне повідомлення MDB починається з протокольного заголовка `struct br_port_msg`:

```c
struct br_port_msg {
    __u8  family;   /* Обов'язково AF_BRIDGE (7) */
    __u8  pad1;
    __u16 pad2;
    __s32 ifindex;  /* Індекс віртуального моста (br0 ifindex) */
};
```

Опис підписки передається через структуру `struct br_mdb_entry`:

```c
struct br_mdb_entry {
    __u32 ifindex;  /* Індекс slave-порту моста (eth1, veth0 тощо) */
    __u8  state;    /* Стан запису: MDB_TEMPORARY (0) або MDB_PERMANENT (1) */
    __u16 vid;      /* Ідентифікатор VLAN ID (0, якщо vlan_filtering вимкнено) */
    struct {
        union {
            __be32          ip4; /* IPv4 мультикаст-адреса (наприклад, 239.255.1.1) */
            struct in6_addr ip6; /* IPv6 мультикаст-адреса (наприклад, ff0e::1) */
            unsigned char   mac_addr[ETH_ALEN]; /* Канальний мультикаст MAC */
        } u;
        __be16          proto;   /* ETH_P_IP (0x0800), ETH_P_IPV6 (0x86DD) або ETH_P_ALL */
    } addr;
};
```

Для обліку джерел у Source-Specific Multicast (IGMPv3 / MLDv2) ядро використовує структуру `struct br_mdb_src_entry`:

```c
struct br_mdb_src_entry {
    struct {
        union {
            __be32          ip4; /* IP-адреса джерела мультикаст-потоку */
            struct in6_addr ip6; /* IPv6-адреса джерела */
        } u;
        __be16          proto;   /* ETH_P_IP (0x0800) або ETH_P_IPV6 (0x86DD) */
    } addr;
    __u32 timer;                 /* Залишок часу життя джерела (у jiffies / clock ticks) */
    __u8  flags;                 /* Прапорці стану джерела (BR_SGRP_F_DELETE, BR_SGRP_F_SEND) */
};
```

#### 5.5.3. Ієрархія TLV-атрибутів у дампах та запитах MDB

Під час виконання `RTM_GETMDB` ядро повертає повну структуру бази у вигляді вкладених контейнерів `MDBA_MDB` та `MDBA_ROUTER`:

```
[struct nlmsghdr] (nlmsg_type = RTM_NEWMDB, flags = NLM_F_MULTI)
[struct br_port_msg] (family = AF_BRIDGE, ifindex = br0_ifindex)
  ├── MDBA_MDB (вкладений контейнер записів підписок на порти)
  │     └── MDBA_MDB_ENTRY (окремий контейнер для кожної групи/порту/VLAN)
  │           ├── MDBA_MDB_ENTRY_INFO -> struct br_mdb_entry
  │           ├── MDBA_MDB_EATTR_TIMER -> __u32 (залишок часу життя групи в jiffies)
  │           ├── MDBA_MDB_EATTR_GROUP_MODE -> __u8 (MCAST_INCLUDE = 1, MCAST_EXCLUDE = 2)
  │           ├── MDBA_MDB_EATTR_FLAGS -> __u8 (бітова маска MDB_PG_FLAGS_*)
  │           ├── MDBA_MDB_EATTR_RTPROT -> __u8 (RTPROT_KERNEL, RTPROT_STATIC тощо)
  │           └── MDBA_MDB_EATTR_SRC_LIST (вкладений контейнер джерел SSM)
  │                 └── MDBA_MDB_SRCLIST_ENTRY (запис для кожного Source IP)
  │                       └── MDBA_MDB_SRCLIST_ENTRY_INFO -> struct br_mdb_src_entry
  └── MDBA_ROUTER (вкладений контейнер портів мультикаст-маршрутизаторів)
        └── MDBA_ROUTER_PORT -> __u32 (ifindex slave-порту маршрутизатора)
              ├── MDBA_ROUTER_PATTR_TIMER -> __u32 (залишок часу активності роутера)
              ├── MDBA_ROUTER_PATTR_TYPE -> __u8 (MDB_RTR_TYPE_*)
              ├── MDBA_ROUTER_PATTR_INET_TIMER -> __u32 (таймер для IPv4 IGMP querier)
              └── MDBA_ROUTER_PATTR_INET6_TIMER -> __u32 (таймер для IPv6 MLD querier)
```

#### 5.5.4. Специфікація атрибутів `MDBA_MDB_EATTR_*` та прапорців групи

| Netlink-атрибут | Числовий код | Тип даних ядра | Призначення та семантика |
| :--- | :---: | :--- | :--- |
| `MDBA_MDB_EATTR_TIMER` | `1` | `__u32` | Залишок часу активності підписки у тактах таймера ядра (`jiffies`). При спливанні таймера ядро видаляє групу або ініціює запит Last Member Query. |
| `MDBA_MDB_EATTR_SRC_LIST` | `2` | Вкладений NLA | Список джерел (Source List) для IGMPv3/MLDv2 SSM. |
| `MDBA_MDB_EATTR_GROUP_MODE`| `3` | `__u8` | Режим фільтрації: `MCAST_INCLUDE` (`1`) або `MCAST_EXCLUDE` (`2`). |
| `MDBA_MDB_EATTR_SOURCE` | `4` | IP-адреса | Адреса джерела в повідомленнях `RTM_NEWMDB` / `RTM_DELMDB`. |
| `MDBA_MDB_EATTR_FLAGS` | `5` | `__u8` | Бітові прапорці підписки `MDB_PG_FLAGS_*`. |
| `MDBA_MDB_EATTR_RTPROT` | `6` | `__u8` | Джерело походження запису (протокол `RTPROT_*`). |

**Бітові прапорці підписки `MDB_PG_FLAGS_*`:**
- **`MDB_PG_FLAGS_PERMANENT` (`0x01`)**: постійний статичний запис, захищений від видалення таймерами;
- **`MDB_PG_FLAGS_OFFLOAD` (`0x02`)**: правило успішно запрограмовано в апаратну таблицю Switchdev ASIC;
- **`MDB_PG_FLAGS_FAST_LEAVE` (`0x04`)**: для даного порту активовано швидке видалення при отриманні IGMP Leave;
- **`MDB_PG_FLAGS_STAR_EXCL` (`0x08`)**: порт перебуває у стані `(*, G)` EXCLUDE (прийом від будь-якого джерела, окрім заблокованих);
- **`MDB_PG_FLAGS_BLOCKED` (`0x10`)**: багатоадресний трафік даної групи заблоковано для передачі на цей порт.

**Типи портів мультикаст-маршрутизаторів `MDB_RTR_TYPE_*`:**
- **`MDB_RTR_TYPE_DISABLED` (`0`)**: порт не є портом маршрутизатора;
- **`MDB_RTR_TYPE_TEMP_QUERY` (`1`)**: порт динамічно виявлено як маршрутизатор через отримані IGMP/MLD Query;
- **`MDB_RTR_TYPE_PERM` (`2`)**: порт примусово призначено маршрутизатором адміністратором (`mcast_router 2`);
- **`MDB_RTR_TYPE_TEMP` (`3`)**: тимчасовий динамічний статус порту.

#### 5.5.5. Семантика фільтрації IGMPv3 / MLDv2 SSM у ядрі

Протоколи IGMPv3 (RFC 3376) та MLDv2 (RFC 3810) вводять розширений механізм фільтрації на основі Source-Specific Multicast. Міст підтримує два незалежні таймери для кожної підписки: **Group Timer (GT)** та **Source Timer (ST)** для кожного джерела.

1. **Режим `EXCLUDE` (фільтрація виключення):**
   - Хост надсилає запит `EXCLUDE {S1, S2}`.
   - Якщо список джерел порожній — це стан `(*, G)`: міст реплікує пакети групи `G` від будь-якого відправника, а `Group Timer` скидається в значення `mcast_membership_interval`.
   - Якщо вказано джерела `{S1, S2}`, міст блокує трафік від `S1` та `S2`, але пересилає трафік від усіх інших IP-адрес.
   - Коли `Group Timer` спливає (`GT == 0`), комутатор автоматично переводить підписку в режим `INCLUDE` для тих джерел, чиї індивідуальні таймери `Source Timer` ще активні (`ST > 0`). Якщо всі `ST == 0`, запис повністю видаляється з MDB.
2. **Режим `INCLUDE` (фільтрація включення):**
   - Хост надсилає запит `INCLUDE {S1, S2}`.
   - Міст пересилає пакети групи `G` **виключно** тоді, коли IP-адреса джерела збігається з `S1` або `S2`, і відповідний `Source Timer` не сплив (`ST > 0`).
   - Пакети від будь-яких інших джерел негайно відкидаються комутатором на етапі перевірки порту.

**Комутаційне рішення у Fast Path (`net/bridge/br_multicast.c`):**
1. Якщо Destination IP знаходиться у зарезервованому діапазоні `224.0.0.0/24` (Link-Local Multicast), міст ігнорує MDB і виконує лавинну розсилку на всі порти, оскільки службові протоколи (OSPF, RIPv2, VRRP, mDNS) не повинні блокуватися снупінгом;
2. Для інших мультикаст-адрес міст шукає пару `(VID, Group)` у внутрішній хеш-таблиці `br->mdb_hash_tbl`;
3. Для кожного порту зі знайденого списку перевіряється відповідність фільтра:
   - Якщо порт у `EXCLUDE`: відправити кадр, якщо Source IP не заблокований у `src_list`;
   - Якщо порт у `INCLUDE`: відправити кадр, якщо Source IP присутній у `src_list` з `ST > 0`;
4. Кадр обов'язково дублюється на всі активні порти мультикаст-маршрутизаторів (`router ports`).

---

### 5.6. Апаратне вивантаження Switchdev та прапорці оффлоаду

Фреймворк Switchdev забезпечує прозоре вивантаження логіки комутації Linux Bridge в апаратні комутаційні матриці (ASIC) мережевих світчів (Mellanox Spectrum, Marvell Prestera, Broadcom тощо). Драйвери комутаторів реєструють обробники блокувальних сповіщень ядра `register_switchdev_blocking_notifier()`.

```
                    +--------------------------------+
                    |    Linux Bridge Core (Kernel)  |
                    |   [ net/bridge/br_switchdev.c] |
                    +---------------+----------------+
                                    |
            Switchdev Notifiers     |  Hardware Offload Calls
            (SWITCHDEV_ATTR_*)      |  (SWITCHDEV_OBJ_*)
                                    v
                    +--------------------------------+
                    |    Switchdev Driver (e.g. mlxsw)|
                    +---------------+----------------+
                                    |
                                    v
                    +--------------------------------+
                    |   Hardware Switch ASIC / TCAM  |
                    +--------------------------------+
```

#### Ключові механізми взаємодії Linux Bridge та Switchdev

1. **Синхронізація прапорців портів (`SWITCHDEV_ATTR_ID_PORT_BRIDGE_FLAGS`)**:  
   Коли простір користувача змінює прапорці порту через `IFLA_BRPORT_*` (наприклад, `learning`, `flood`, `isolated`), функція `br_setport()` викликає `switchdev_port_attr_set()`. Драйвер апаратного світча конфігурує відповідні регістри порту ASIC.
2. **Апаратне вивчення та скидання FDB**:
   - Коли ASIC вивчає нову MAC-адресу на апаратному порті, драйвер надсилає в ядро подію `SWITCHDEV_FDB_ADD_TO_BRIDGE`. Ядро вносить запис у програмну таблицю з прапорцем `NTF_OFFLOADED`.
   - Коли топологія змінюється (подія STP Topology Change або падіння несучої), надсилання атрибута `IFLA_BRPORT_FLUSH` призводить до виклику `SWITCHDEV_OBJ_ID_PORT_FDB` для миттєвого апаратного скидання кешу FDB порту.
3. **Фільтрація VLAN (`SWITCHDEV_OBJ_ID_PORT_VLAN`)**:  
   Додавання або видалення тегів через `IFLA_BRIDGE_VLAN_INFO` транслюється у виклики додавання/видалення записів у таблиці VLAN ASIC (VLAN Table).
4. **Нерозбірливий режим `BR_PROMISC`**:  
   Якщо на порті моста активується перехоплення пакетів (наприклад, `tcpdump` або дзеркалювання трафіку), ядро виставляє прапорець `BR_PROMISC` у `struct net_bridge_port`. Це змушує апаратний драйвер дублювати всі кадри в чергу CPU Port.

---

### 5.7. Мультикаст-групи асинхронних подій RTNETLINK

Системні демони, SDN-контролери та мережеві агенти підписуються на топологічні події моста через бітову маску поля `nl_groups` структури `struct sockaddr_nl` під час системного виклику `bind()`:

```c
struct sockaddr_nl sa;
memset(&sa, 0, sizeof(sa));
sa.nl_family = AF_NETLINK;
sa.nl_groups = RTMGRP_LINK | RTMGRP_NEIGH | (1 << (RTNLGRP_BRVLAN - 1));
bind(nl_fd, (struct sockaddr *)&sa, sizeof(sa));
```

- **`RTNLGRP_LINK`** (`RTMGRP_LINK`): сповіщення `RTM_NEWLINK` / `RTM_DELLINK` про зміну стану лінка (Carrier Up/Down), зміну станів STP (Listening -> Forwarding), приєднання або відключення портів;
- **`RTNLGRP_NEIGH`** (`RTMGRP_NEIGH`): асинхронні повідомлення `RTM_NEWNEIGH` / `RTM_DELNEIGH` про появу нових MAC-адрес у FDB, міграцію віртуальних машин між портами або застарівання записів;
- **`RTNLGRP_BRVLAN`**: нотифікації про модифікацію таблиці членства у VLAN на портах;
- **`RTNLGRP_MDB`**: події додавання/видалення підписок на багатоадресні групи IGMP/MLD.

---

### 5.8. Коди помилок ядра та Extended ACK

При виникненні помилки ядро повертає пакет `NLMSG_ERROR` із числовим кодом у полі `struct nlmsgerr.error` (від'ємне значення `errno`). Якщо встановлено прапорець сокета `NETLINK_EXT_ACK`, ядро додає TLV-атрибути з текстовим роз'ясненням причини:
- `NLMSGERR_ATTR_MSG`: розгорнуте строкове повідомлення про помилку від підсистеми моста;
- `NLMSGERR_ATTR_OFFS`: точний байтовий зсув у вхідному пакеті, де виявлено некоректний атрибут.

**Типові коди помилок у підсистемі Bridge:**
- **`EINVAL` (`-22`)**: некоректний діапазон параметрів (наприклад, `vid > 4094`, некоректне співвідношення таймерів `max_age >= 2 * (forward_delay - 1)`, або непідтримуваний протокол тегування);
- **`EBUSY` (`-16`)**: інтерфейс уже приєднаний до іншого master-пристрою (іншого моста, bonding чи team);
- **`EEXIST` (`-17`)**: спроба створити міст із наявним ім'ям або внести дублюючий запис FDB без прапорця `NLM_F_REPLACE`;
- **`ENOENT` / `ENODEV` (`-19`)**: вказаний у запиті числовий `ifindex` не знайдено в системі;
- **`EOPNOTSUPP` (`-95`)**: дія не підтримується апаратним драйвером (наприклад, відсутність підтримки Switchdev для специфічного прапорця);
- **`ERANGE` (`-34`)**: спроба задати діапазон `BRIDGE_VLAN_INFO_RANGE_END`, менший за початковий `RANGE_BEGIN`.

---

## 6. Вузли віртуальної файлової системи `sysfs` та параметри `sysctl`

Файлова система `sysfs` надає людиночитабельний інтерфейс для діагностики, моніторингу та скриптового налаштування комутатора без використання бінарних сокетів.

### 6.1. Параметри моста: `/sys/class/net/<BRNAME>/bridge/`

| Вузол sysfs | Права | Одиниці | Семантика ядра |
| :--- | :---: | :--- | :--- |
| `ageing_time` | `rw` | clock ticks (соті с) | Поточний час життя динамічних записів у FDB. |
| `bridge_id` | `ro` | hex-рядок | 8-байтний STP Bridge ID (2 байти пріоритету + 6 байтів MAC-адреси). |
| `stp_state` | `rw` | `0`, `1`, `2` | Поточний стан підсистеми Spanning Tree. |
| `vlan_filtering` | `rw` | `0`, `1` | Стан активності механізму фільтрації тегів 802.1Q. |
| `default_pvid` | `rw` | `0` .. `4094` | Дефолтний PVID для нових підключених портів. |
| `vlan_protocol` | `rw` | `0x8100`, `0x88a8` | Шістнадцятковий код активного протоколу тегування. |
| `group_fwd_mask` | `rw` | hex-число | 16-бітна маска пропуску службових групових адрес IEEE 802.1D. |
| `root_port` | `ro` | ціле число | Номер внутрішнього порту моста, через який іде зв'язок із Root Bridge. |
| `root_path_cost` | `ro` | ціле число | Сумарна метрика STP Path Cost до кореневого моста. |
| `hello_time` | `rw` | clock ticks (соті с) | Інтервал генерації кадрів BPDU кореневим комутатором. |
| `forward_delay` | `rw` | clock ticks (соті с) | Затримка переходів між станами STP Listening та Learning. |
| `max_age` | `rw` | clock ticks (соті с) | Максимальний вік збереження конфігурації BPDU. |
| `multicast_snooping` | `rw` | `0`, `1` | Стан механізму перехоплення IGMP/MLD повідомлень. |
| `multicast_querier` | `rw` | `0`, `1` | Режим активного генератора запитів IGMP/MLD Query. |

### 6.2. Параметри портів: `/sys/class/net/<BRNAME>/brif/<PORTNAME>/`

| Вузол sysfs | Права | Значення | Опис |
| :--- | :---: | :--- | :--- |
| `hairpin_mode` | `rw` | `0`, `1` | Дозвіл надсилання кадру назад у вхідний порт (Reflective Relay). |
| `learning` | `rw` | `0`, `1` | Прапорець динамічного вивчення MAC-адрес з трафіку порту. |
| `unicast_flood` | `rw` | `0`, `1` | Дозвіл розсилки невідомого одноадресного трафіку (Unknown Unicast Flood). |
| `multicast_flood` | `rw` | `0`, `1` | Дозвіл розсилки невідомого багатоадресного трафіку. |
| `broadcast_flood` | `rw` | `0`, `1` | Дозвіл реплікації широкомовних кадрів на даний порт. |
| `isolated` | `rw` | `0`, `1` | Режим ізоляції порту (заборона комутації з іншими ізольованими портами). |
| `bpdu_guard` | `rw` | `0`, `1` | Захист BPDU Guard (вимикання порту при отриманні BPDU). |
| `root_block` | `rw` | `0`, `1` | Захист Root Guard (заборона порту ставати кореневим). |
| `state` | `ro` | `0` .. `4` | Поточний числовий стан порту в STP (`0` Disabled, `1` Listening, `2` Learning, `3` Forwarding, `4` Blocking). |
| `path_cost` | `rw` | ціле число | Вартість лінка для розрахунків STP Spanning Tree. |
| `priority` | `rw` | `0` .. `63` | Пріоритет порту в розрахунках STP. |

### 6.3. Системні параметри ядра `sysctl` модуля `br_netfilter`

Коли модуль ядра `br_netfilter` завантажено, комутатор може передавати транзитні кадри канального рівня для обробки мережевим фільтром Netfilter (L3/L4):

| Змінна `sysctl` | Дефолт | Опис та вплив на пакетний фільтр |
| :--- | :---: | :--- |
| `net.bridge.bridge-nf-call-iptables` | `1` | Перехоплення транзитних IPv4-пакетів моста правилами `iptables` / `nftables` у хуках PREROUTING, FORWARD та POSTROUTING. При `0` комутація виконується суто на L2 без втручання файрволу. |
| `net.bridge.bridge-nf-call-ip6tables` | `1` | Перехоплення транзитних IPv6-пакетів моста правилами `ip6tables`. |
| `net.bridge.bridge-nf-call-arptables` | `1` | Дозвіл фільтрації транзитних кадрів протоколу ARP через таблиці `arptables`. |
| `net.bridge.bridge-nf-filter-vlan-tagged` | `0` | Дозвіл розбору та фільтрації вмісту пакетів із мітками 802.1Q правилами Netfilter. |
| `net.bridge.bridge-nf-filter-pppoe-tagged`| `0` | Дозвіл фільтрації інкапсульованих кадрів PPPoE. |
| `net.bridge.bridge-nf-pass-vlan-input-dev`| `0` | Передача у правила Netfilter імені відповідного віртуального VLAN-інтерфейсу замість загального імені моста. |

---

## 7. Фільтрація та пакетний фаєрволінг моста: `ebtables`, `nftables bridge` та `br_netfilter`

Фільтрація трафіку на рівні L2-комутатора в Linux реалізується двома принципово різними архітектурними підходами:
1. **Чиста фільтрація канального рівня (`ebtables` / `nftables bridge family`)**: аналіз та модифікація полів Ethernet-кадрів (MAC-адреси, теги 802.1Q, поля заголовків ARP/IP) безпосередньо в хуках моста без залучення підсистем мережевого рівня (L3) ядра;
2. **Міжрівневе перехоплення (`br_netfilter`)**: примусове передавання транзитних Ethernet-кадрів у хуки мережевого фільтра L3/L4 (IPv4/IPv6 `iptables` та `nftables inet family`), що уможливлює повноцінне відстеження станів з'єднань (Connection Tracking / conntrack) та трансляцію мережевих адрес (NAT) для мостового трафіку.

---

### 7.1. Архітектура хуків Netfilter для канального рівня (Bridge Hooks)

Підсистема Linux Bridge інтегрована у фреймворк Netfilter через шість фіксованих точок перехоплення (хуків), визначених у `<linux/netfilter_bridge.h>`:

```
[Вхідний порт] ───> [NF_BR_PRE_ROUTING] ───> [Перевірка FDB / VLAN] ───> [NF_BR_FORWARD] ───> [NF_BR_POST_ROUTING] ───> [Вихідний порт]
                           │                                                 │
                  (Локальний MAC моста)                                (Локальний вивід)
                           v                                                 ^
                    [NF_BR_LOCAL_IN]                                  [NF_BR_LOCAL_OUT]
                           │                                                 │
                           v                                                 │
                  [L3/L4 Стек Хоста] ────────────────────────────────────────┘
```

| Хук ядра | Числовий код | Точка спрацьовування у життєвому циклі кадру |
| :--- | :---: | :--- |
| `NF_BR_PRE_ROUTING` | `0` | Викликається у функції `br_handle_frame()` негайно після отримання кадру з черги RX, до виконання пошуку в таблиці FDB та до перевірки прав членства у VLAN. |
| `NF_BR_LOCAL_IN` | `1` | Спрацьовує, якщо `Destination MAC` збігається з власною MAC-адресою моста чи його портів, або є широкомовним/мультикаст-кадром, призначеним для локального стека хоста. |
| `NF_BR_FORWARD` | `2` | Викликається у `br_forward_finish()` для транзитних кадрів, що комутуються між двома slave-портами моста. |
| `NF_BR_LOCAL_OUT` | `3` | Перехоплює кадри, згенеровані локальними сокетами хоста, що надсилаються через віртуальний інтерфейс моста у комутаційний домен. |
| `NF_BR_POST_ROUTING` | `4` | Фінальний етап перевірки перед відправкою кадру у драйвер вихідного порту (`br_dev_queue_push_xmit`). |
| `NF_BR_BROUTING` | `-1` | Спеціальний хук перехоплення broute (утиліта `ebtables -t broute`). Дозволяє правилом повернути вердикт `DROP`, що змушує міст передати кадр безпосередньо у L3-маршрутизацію хоста без комутації (Routing замість Bridging). |

---

### 7.2. Метадані кадрів L2 та селектори фільтрації

Пакетні фільтри канального рівня оперують структурою `sk_buff` та спеціальними розширеннями полів:

1. **Канальні адреси та типи (Ethernet Header):**
   - `ether saddr` / `ether daddr`: 48-бітні фізичні MAC-адреси джерела та призначення;
   - `ether type`: 16-бітний протокольний ідентифікатор EtherType (`0x0800` IPv4, `0x86DD` IPv6, `0x0806` ARP, `0x8100` 802.1Q VLAN, `0x88A8` 802.1ad Service VLAN, `0x88CC` LLDP, `0x888E` 802.1X EAPOL).
2. **Параметри тегів віртуальних мереж (IEEE 802.1Q / 802.1ad):**
   - `vlan id`: номер віртуальної мережі (`1` .. `4094`);
   - `vlan pcp`: 3-бітний пріоритет черги Priority Code Point (`0` .. `7`);
   - `vlan dei` (CFI): 1-бітний прапорець придатності до скидання при заторах (Drop Eligible Indicator).
3. **Метадані моста та slave-портів:**
   - `meta ibrname` / `meta obrname`: строкове ім'я екземпляра моста входу та виходу (`br0`);
   - `meta ibrport` / `meta obrport`: строкове ім'я конкретного slave-порту входу та виходу (`eth0`, `veth-cust1`, `tap0`).
4. **Поля протоколу ARP (Address Resolution Protocol):**
   - `arp operation`: тип операції (`request` / `1`, `reply` / `2`);
   - `arp saddr ip` / `arp daddr ip`: IPv4-адреси відправника та цілі запиту;
   - `arp saddr ether` / `arp daddr ether`: апаратні MAC-адреси відправника та цілі.

---

### 7.3. Конфігурація правил через `nftables` (Bridge Family)

Сучасний мережевий фільтр `nftables` надає спеціальне сімейство правил `table bridge`, яке виконує інспекцію L2-трафіку на максимальній швидкості ядра без накладних витрат на емуляцію L3-маршрутизації.

```nft
# Конфігурація таблиці фільтрації канального рівня /etc/nftables.conf
table bridge filter {
    # Ланцюг вхідної фільтрації перед комутацією
    chain prerouting {
        type filter hook prerouting priority -200; policy accept;

        # 1. Захист від підробки MAC-адрес (Port Security / Anti-Spoofing):
        # Дозволити порту veth-cust1 надсилати кадри лише з його легітимним MAC
        iif "veth-cust1" ether saddr != 52:54:00:12:34:56 drop

        # 2. Блокування неавторизованих DHCP-серверів на клієнтських портах (Rogue DHCP Server Protection):
        # Скидати відповіді DHCP (UDP src port 67) від клієнтських інтерфейсів
        iif "veth-cust1" udp sport 67 drop

        # 3. Динамічна інспекція ARP (Dynamic ARP Inspection, DAI):
        # Захист від ARP-Cache Poisoning: перевірка відповідності IP та MAC в ARP-відповідях
        iif "veth-cust1" arp operation reply arp saddr ip 192.168.1.100 arp saddr ether != 52:54:00:12:34:56 drop

        # 4. Блокування службових протоколів маршрутизації від ненадійних клієнтів
        iif "veth-cust1" ip daddr 224.0.0.5 drop  # OSPF
        iif "veth-cust1" ip daddr 224.0.0.18 drop # VRRP
    }

    # Ланцюг комутації між портами моста
    chain forward {
        type filter hook forward priority 0; policy accept;

        # 5. Мікросегментація: повна заборона прямого L2-обміну між ізольованими клієнтами
        iif "veth-cust1" oif "veth-cust2" drop
        iif "veth-cust2" oif "veth-cust1" drop

        # 6. Фільтрація за тегами 802.1Q (VLAN ACL):
        # Дозволити пересилання лише для затверджених VLAN 10, 20 та 100
        vlan id { 10, 20, 100 } accept
        vlan id != 0 drop
    }
}
```

---

### 7.4. Механізм `br_netfilter` та міжрівневе проходження (L2 -> L3/L4)

Модуль ядра `br_netfilter` реалізує гібридну схему обробки: транзитний Ethernet-кадр під час руху крізь міст тимчасово підіймається у мережевий рівень (L3) і проходить стандартні хуки Netfilter IPv4/IPv6 (`NF_INET_PRE_ROUTING`, `NF_INET_FORWARD`, `NF_INET_POST_ROUTING`).

```
                              Хук NF_BR_PRE_ROUTING
                                       │
                br_nf_pre_routing()    │  (Виявлено IPv4/IPv6 пакет)
                                       v
                             [NF_INET_PRE_ROUTING]  <── iptables/nftables PREROUTING & DNAT
                                       │
                      ip_defrag()      │  (Створення fake_rtable, дефрагментація)
                                       v
                             [Комутація моста FDB]
                                       │
                      br_nf_forward_ip()
                                       v
                              [NF_INET_FORWARD]     <── iptables/nftables FORWARD (L3/L4 фільтрація)
                                       │
                                       v
                             [NF_BR_FORWARD (L2)]
                                       │
                     br_nf_post_routing()
                                       v
                             [NF_INET_POST_ROUTING] <── iptables/nftables POSTROUTING & SNAT
                                       │
                                       v
                            [NF_BR_POST_ROUTING (L2)]
                                       │
                                       v
                                 [Вихідний порт]
```

#### Ключові етапи обробки в `br_netfilter`:
1. **Виділення фіктивного маршруту `fake_rtable`:**  
   Оскільки транзитний L2-кадр не проходить класичну таблицю маршрутизації хоста `ip_route_input_noref()`, підсистема створює тимчасову структуру `struct rtable` (або `struct rt6_info`), яка вказує на інтерфейс моста. Це запобігає збою у хуках L3, які очікують обов'язкової наявності `skb_dst(skb)`;
2. **Дефрагментація IP-пакетів (`ip_defrag()`):**  
   Для інспекції портів L4 (TCP/UDP) та коректної роботи Connection Tracking ядро дефрагментує фрагментовані IP-пакети безпосередньо всередині L2-моста перед викликом `NF_INET_PRE_ROUTING`. Після фільтрації пакет повторно фрагментується перед виходом у фізичний лінк;
3. **Повернення в L2:**  
   Після завершення перевірок L3 пакет повертається в комутаційний конвеєр `br_forward()`.

---

### 7.5. Відстеження з'єднань (`conntrack`), L2 NAT та модуль `xt_physdev`

Завдяки модулю `br_netfilter` системний фаєрвол може застосовувати повноцінні stateful-правила до віртуальних машин та контейнерів, підключених до спільного L2-моста.

#### Відстеження станів TCP/UDP у мості
```bash
# Дозвіл транзитного трафіку лише для встановлених та пов'язаних сесій
iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Блокування невалідних пакетів або сесій, що порушують стан TCP-автомата
iptables -A FORWARD -m conntrack --ctstate INVALID -j DROP
```

#### Модуль узгодження фізичних портів `xt_physdev`
Під час проходження L3-хуків звичайні селектори `-i` та `-o` у `iptables` бачать лише ім'я самого моста (`-i br0 -o br0`), втрачаючи інформацію про те, через який саме фізичний порт або віртуальний інтерфейс (`veth`, `tap`) надійшов кадр. Модуль `xt_physdev` відновлює доступ до інформації про порти:

| Прапорець `xt_physdev` | Семантика фільтрації |
| :--- | :--- |
| `--physdev-in <DEV>` | Вхідний slave-порт моста, з якого було прийнято Ethernet-кадр (`eth0`, `veth-vm1`). |
| `--physdev-out <DEV>` | Цільовий slave-порт моста, у який комутується кадр після пошуку в FDB (`eth1`, `tap2`). |
| `--physdev-is-bridged` | Умова обов'язкової комутації кадру мостом (виключає кадри, адресовані локальному L3-стеку хоста). |
| `--physdev-is-in` | Кадр надійшов через підлеглий slave-порт моста. |
| `--physdev-is-out` | Кадр буде передано через підлеглий slave-порт моста. |

**Приклад конфігурації фаєрволу для віртуальної машини через `xt_physdev`:**
```bash
# Дозволити вихідний трафік від віртуальної машини tap0 у зовнішній світ
iptables -A FORWARD -m physdev --physdev-in tap0 --physdev-out eth0 -j ACCEPT

# Дозволити лише вхідні відповіді з Інтернету на віртуальну машину tap0
iptables -A FORWARD -m physdev --physdev-in eth0 --physdev-out tap0 \
    -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Заборонити віртуальній машині tap0 прямий доступ до внутрішньої підмережі бази даних на порту eth1
iptables -A FORWARD -m physdev --physdev-in tap0 --physdev-out eth1 -j DROP
```

---

### 7.6. Архітектурне порівняння: `nftables bridge` проти `br_netfilter`

| Характеристика | Чистий `nftables` (`table bridge`) | Модуль `br_netfilter` + `iptables/nftables inet` |
| :--- | :--- | :--- |
| **Рівень обробки** | Суворо канальний рівень (L2). | Гібридний міжрівневий стек (L2 -> L3 -> L4 -> L2). |
| **Продуктивність (Throughput / PPS)** | **Максимальна (Line Rate)**. Відсутні накладні витрати на підсистеми L3. | **Знижена на 20-45%**. Значні накладні витрати на дефрагментацію IP та fake routing. |
| **Відстеження станів (Conntrack)** | Не підтримується (Stateless фільтрація заголовків). | **Повноцінний Stateful Conntrack** для всіх TCP/UDP/ICMP сесій усередині моста. |
| **Підтримка NAT** | Лише Stateless переписування MAC-адрес (`ether saddr set ...`). | **Повноцінний Stateful L3 NAT** (DNAT / SNAT / Masquerade) на мості. |
| **Ізоляція просторів імен (Netns)** | Повна ізоляція. Правила виконуються суворо у межах свого `netns`. | Ризик витоку пакетів та конфліктів глобальних хуків у складних схемах контейнеризації. |
| **Асиметрична маршрутизація** | Працює стабільно без збоїв. | Можливе блокування зворотного трафіку через відсутність записів у conntrack на даному хості. |
| **Основні сценарії застосування** | Високонавантажені комутатори, телеком, NFV, базовий захист портів (Anti-Spoofing, DAI, DHCP Guard). | Фаєрволінг віртуальних машин KVM/QEMU (libvirt nwfilter), застарілі плагіни Kubernetes CNI. |

