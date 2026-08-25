# 📋 Інтерфейси керування Bonding та Team: sysfs, rtnetlink та teamd JSON/DBus

Мережева агрегація в операційній системі Linux надає розробникам мережевих служб та системним інженерам комплексний набір програмних інтерфейсів для конфігурації, моніторингу стану та динамічної зміни параметрів об'єднаних мережевих пристроїв. Усі наявні інтерфейси розподіляються на два класи: низькорівневі ядрові інтерфейси (віртуальні файлові системи `sysfs` та `procfs`, системні бінарні сокети `rtnetlink`) та високорівневі інструменти простору користувача (JSON-конфігураційні схеми демона `teamd`, його IPC-інтерфейси на базі DBus та Unix domain сокетів).

---

## 1. Віртуальні файлові системи sysfs та procfs у Bonding

Класичний драйвер `bonding` відкриває свої внутрішні структури даних ядра через два текстових інтерфейси у віртуальних файлових системах `sysfs` та `procfs`.

### 1.1. Атрибути sysfs (`/sys/class/net/bondX/bonding/`)

При створенні логічного інтерфейсу `bondX` драйвер реєструє у каталозі `/sys/class/net/bondX/bonding/` серію віртуальних файлів атрибутів. Запис текстових значений у ці файли змінює стан драйвера в режимі реального часу. 

Кожен файл атрибута підтримує стандартні файлові операції `read()` та `write()`. Під час читання операційна система викликає внутрішній обробник `bonding_show_*()`, який зчитує поточне значення з ядрової структури `struct bonding` та форматує його у текстовий рядок. Під час запису викликається обробник `bonding_store_*()`, який виконує перевірку прав доступу, валідацію вхідних значень та атомарну модифікацію параметрів.

Переважна більшість критичних параметрів (наприклад, `mode`, `miimon` або `xmit_hash_policy`) вимагає попереднього переведення master-інтерфейсу у стан `DOWN` (`ip link set bond0 down`) перед внесенням змін. Це обмеження обумовлене тим, що зміна режиму або алгоритму хешування під час активного передавання трафіку викликала б десинхронізацію таблиць маршрутизації ядра та розрив існуючих TCP-сесій.

| Файл атрибута sysfs | Можливі значення / Формат | Опис та семантичні обмеження |
| :--- | :--- | :--- |
| `mode` | `balance-rr (0)`, `active-backup (1)`, `balance-xor (2)`, `broadcast (3)`, `802.3ad (4)`, `balance-tlb (5)`, `balance-alb (6)` | Встановлює режим обробки пакетів та розподілу трафіку. Зміна вимагає переведення `bond` у DOWN. |
| `slaves` | Рядок із назвами інтерфейсів через пробіл (наприклад: `+eth0 +eth1 -eth0`) | Запис `+<ifname>` приєднує slave-інтерфейс; запис `-<ifname>` вилучає його з групи. |
| `miimon` | Ціле число в мілісекундах (наприклад: `100`) | Інтервал моніторингу стану фізичного носія (MII). Значення `0` вимикає MII-моніторинг. |
| `updelay` | Ціле число в мілісекундах (кратне `miimon`) | Затримка перед включенням відновленого slave-інтерфейсу в активну групу (забігання flapping). |
| `downdelay` | Ціле число в мілісекундах (кратне `miimon`) | Затримка перед виключенням знову впавшого slave-інтерфейсу з активної групи. |
| `xmit_hash_policy` | `layer2 (0)`, `layer2+3 (1)`, `layer3+4 (2)`, `encap2+3 (3)`, `encap3+4 (4)` | Політика хешування вихідних кадрів у режимах `balance-xor` та `802.3ad`. |
| `active_slave` | Назва мережевого інтерфейсу (наприклад: `eth0`) | Повертає або примусово встановлює поточний активний інтерфейс у режимі `active-backup`. |
| `primary` | Назва мережевого інтерфейсу (наприклад: `eth0`) | Вказує відносно первинний пристрій, який стає активним відразу після відновлення зв'язку. |
| `primary_reselect` | `always (0)`, `better (1)`, `failure (2)` | Політика перепризначення primary-інтерфейсу після його відновлення з аварійного стану. |
| `arp_interval` | Ціле число в мілісекундах (наприклад: `1000`) | Інтервал відправки ARP-запитів для моніторингу L3-доступності цільових вузлів. |
| `arp_ip_target` | До 16 IPv4-адрес через кому (наприклад: `192.168.1.1,192.168.1.2`) | Цільові IP-адреси, на які ARP-монітор надсилає запити для перевірки цілісності каналу. |
| `lacp_rate` | `slow (0)` або `fast (1)` | Частота відправки пакетів LACPDU: `slow` — раз на 30 с; `fast` — щосекунди (що 1 с). |
| `ad_select` | `stable (0)`, `bandwidth (1)`, `count (2)` | Політика вибору активного агрегатора LACP у випадку наявності кількох груп 802.3ad. |

### 1.2. Семантика додаткових параметрів sysfs

- **`num_grat_arp` (або `num_unsol_na`)**: Визначає кількість незапитаних ARP-відповідей (Gratuitous ARP) або повідомлень IPv6 Neighbor Advertisement, які драйвер відправляє в мережу після перемикання активного порту в режимі `active-backup`. За замовчуванням значення дорівнює `1`, але у мережах з повільним оновленням CAM-таблиць комутаторів рекомендується збільшувати його до `3`–`5`.
- **`fail_over_mac`**: Контролює спосіб обробки MAC-адрес при переключенні активного порту у режимі `active-backup`:
  - `none (0)` (за замовчуванням): Усі slave-інтерфейси отримують MAC-адресу майстра при прив'язці.
  - `active (1)`: MAC-адреса master-пристрою завжди збігається з MAC-адресою поточного активного slave-порту. При failover MAC-адреса майстра змінюється на MAC-адресу нового активного порту.
  - `follow (2)`: MAC-адреса master-пристрою призначається першому приєднаному slave, але при failover новий активний порт копіює цю MAC-адресу.
- **`resend_igmp`**: Кількість повторних повідомлень IGMP Membership Report, які надсилаються у мережу після перемикання порту для відновлення підписки на мультикаст-потоки (Multicast streams).

### 1.3. Простеження стану через `/proc/net/bonding/bondX`

Віртуальний файл `/proc/net/bonding/bondX` є головним засобом відлагодження у системному адмініструванні Linux. Він надає розширений зріз стану внутрішніх структур ядра (`struct bonding` та `struct slave`).

Типовий вивід файлу при роботі у режимі LACP (Mode 4):

```text
Ethernet Channel Bonding Driver: v3.7.1 (April 27, 2011)

Bonding Mode: IEEE 802.3ad Dynamic link aggregation
Transmit Hash Policy: layer3+4 (2)
MII Status: up
MII Polling Interval (ms): 100
Up Delay (ms): 200
Down Delay (ms): 200

802.3ad info
LACP rate: fast
Min links: 1
Aggregator selection policy: bandwidth
System priority: 65535
System MAC address: 52:54:00:12:34:56
Active Aggregator Info:
	Aggregator ID: 1
	Number of ports: 2
	Actor Key: 17
	Partner Key: 1
	Partner Mac Address: 00:1c:73:00:00:01

Slave Interface: eth0
MII Status: up
Speed: 10000 Mbps
Duplex: full
Link Failure Count: 0
Permanent HW addr: 52:54:00:ab:cd:01
Slave queue ID: 0
Aggregator ID: 1
Actor Churn State: none
Partner Churn State: none
Actor Partner State: flag 0x3d (LACP_ACTIVITY, AGGREGATION, SYNCHRONIZATION, COLLECTING, DISTRIBUTING)

Slave Interface: eth1
MII Status: up
Speed: 10000 Mbps
Duplex: full
Link Failure Count: 1
Permanent HW addr: 52:54:00:ab:cd:02
Slave queue ID: 0
Aggregator ID: 1
```

---

## 2. Протокол Rtnetlink у ядрі Linux (Атрибути IFLA_BOND)

Сучасні утиліти (`iproute2`, `NetworkManager`) та програмні контролери взаємодіють з драйвером Bonding через сокети `AF_NETLINK` (протокольний сімейство `NETLINK_ROUTE`).

Створення пристрою виконується повідомленням `RTM_NEWLINK`. Параметри передаються у вкладеному контейнері `IFLA_LINKINFO`, де атрибут `IFLA_INFO_KIND` має значення `"bond"`, а самі налаштування пакуються у контейнер `IFLA_INFO_DATA`.

### 2.1. Перелік атрибутів `IFLA_BOND_*` (згідно з `<linux/if_bonding.h>`)

Ядро розбирає вкладений атрибут `IFLA_INFO_DATA` за допомогою внутрішньої функції `nla_parse_nested()`, очікуючи наступні константи:

```c
enum {
    IFLA_BOND_UNSPEC,
    IFLA_BOND_MODE,                /* u8: режим bonding (0-6) */
    IFLA_BOND_ACTIVE_SLAVE,         /* u32: ifindex активного slave пристрою */
    IFLA_BOND_MIIMON,               /* u32: інтервал MII моніторингу у мс */
    IFLA_BOND_UPDELAY,              /* u32: затримка увімкнення лінка у мс */
    IFLA_BOND_DOWNDELAY,            /* u32: затримка вимкнення лінка у мс */
    IFLA_BOND_USE_CARRIER,          /* u8: перевірка carrier netif (0/1) */
    IFLA_BOND_ARP_INTERVAL,         /* u32: інтервал відправки ARP у мс */
    IFLA_BOND_ARP_IP_TARGET,        /* вкладений контейнер IP-адрес targets */
    IFLA_BOND_ARP_VALIDATE,         /* u32: режим валідації вхідних ARP */
    IFLA_BOND_ARP_ALL_TARGETS,      /* u32: критерій доступності ARP цілей */
    IFLA_BOND_PRIMARY,              /* u32: ifindex первинного slave */
    IFLA_BOND_PRIMARY_RESELECT,     /* u8: режим переобрання primary */
    IFLA_BOND_FAIL_OVER_MAC,        /* u8: політика обробки MAC при failover */
    IFLA_BOND_XMIT_HASH_POLICY,     /* u8: політика хешування (0-4) */
    IFLA_BOND_RESEND_IGMP,          /* u32: кількість повторних IGMP пакетів */
    IFLA_BOND_NUM_PEER_NOTIF,       /* u8: кількість gratuitous ARP пакетів */
    IFLA_BOND_ALL_SLAVES_ACTIVE,    /* u8: обробка дубльованого трафіку */
    IFLA_BOND_MIN_LINKS,            /* u32: мін. кількість лінків для 802.3ad */
    IFLA_BOND_LP_INTERVAL,          /* u32: інтервал навчальних пакетів (tlb/alb) */
    IFLA_BOND_PACKETS_PER_SLAVE,    /* u32: кількість пакетів на slave (mode 0) */
    IFLA_BOND_AD_LACP_RATE,         /* u8: швидкість LACPDU (0=slow, 1=fast) */
    IFLA_BOND_AD_SELECT,            /* u8: режим вибору агрегатора LACP */
    IFLA_BOND_AD_INFO,              /* вкладений атрибут з деталями 802.3ad */
    IFLA_BOND_AD_ACTOR_SYS_PRIO,    /* u16: пріоритет Actor системи */
    IFLA_BOND_AD_USER_PORT_PRIO,    /* u16: пріоритет порту користувача */
    IFLA_BOND_AD_ACTOR_SYSTEM,      /* 6 байт: системна MAC-адреса Actor */
    IFLA_BOND_TLB_DYNAMIC_LB,       /* u8: динамічне балансування tlb (0/1) */
    __IFLA_BOND_MAX
};
```

### 2.2. Атрибути підпорядкованих пристроїв `IFLA_BOND_SLAVE_*`

При прив'язці або опитуванні стану підпорядкованого пристрою (slave) за допомогою `RTM_NEWLINK` атрибут `IFLA_INFO_KIND` містить рядок `"bond_slave"`, а параметри порту розміщуються у контейнері `IFLA_INFO_DATA`:

```c
enum {
    IFLA_BOND_SLAVE_UNSPEC,
    IFLA_BOND_SLAVE_STATE,          /* u8: стан slave (0=ACTIVE, 1=BACKUP) */
    IFLA_BOND_SLAVE_MII_STATUS,     /* u8: статус MII (0=LINK_UP, 1=LINK_FAIL) */
    IFLA_BOND_SLAVE_LINK_FAILURE_COUNT, /* u32: лічильник аварійних падінь лінка */
    IFLA_BOND_SLAVE_PERM_HWADDR,    /* 6 байт: оригінальна MAC-адреса карти */
    IFLA_BOND_SLAVE_QUEUE_ID,       /* u16: ідентифікатор черги передачі */
    IFLA_BOND_SLAVE_AD_AGGREGATOR_ID,/* u16: ідентифікатор агрегатора LACP */
    IFLA_BOND_SLAVE_AD_ACTOR_OPER_PORT_STATE, /* u8: стан автомата LACP Actor */
    IFLA_BOND_SLAVE_AD_PARTNER_OPER_PORT_STATE, /* u8: стан автомата LACP Partner */
    __IFLA_BOND_SLAVE_MAX
};
```

### 2.3. Вкладений атрибут `IFLA_BOND_AD_INFO`

При запиті інформації про стан режиму 802.3ad ядро повертає вкладений атрибут `IFLA_BOND_AD_INFO`, який містить під-атрибути стану LACP:
- `IFLA_BOND_AD_INFO_AGGREGATOR` (`u16`): Ідентифікатор поточного активного агрегатора LACP.
- `IFLA_BOND_AD_INFO_NUM_PORTS` (`u16`): Кількість фізичних портів, об'єднаних в активний агрегатор.
- `IFLA_BOND_AD_INFO_ACTOR_KEY` (`u16`): Операційний ключ Actor, сформований на основі швидкості та дуплексу.
- `IFLA_BOND_AD_INFO_PARTNER_KEY` (`u16`): Операційний ключ Partner (комутатора).
- `IFLA_BOND_AD_INFO_PARTNER_MAC` (`6 байт`): Системна MAC-адреса комутатора.

---

## 3. Схема конфігурації Team (JSON Schema для teamd)

На відміну від Bonding, підсистема Team керується демоном `teamd` у просторі користувача. Конфігурація задається у стандартному форматі JSON.

### 3.1. Детальний опис JSON-полів конфігураційного файла

- `device` (string): Назва віртуального мережевого пристрою у просторі ядра (наприклад, `"team0"`).
- `hwaddr` (string): Фіксована MAC-адреса логічного пристрою у форматі `XX:XX:XX:XX:XX:XX`.
- `runner` (object): Об'єкт налаштування алгоритму агрегації трафіку.
  - `name` (string): Назва алгоритму (`"roundrobin"`, `"activebackup"`, `"broadcast"`, `"loadbalance"`, `"lacp"`).
  - `active` (boolean): Активація виконання режиму.
  - `fast_rate` (boolean): Для LACP: надсилання LACPDU кожну секунду (`true`) замість 30 секунд (`false`).
  - `tx_hash` (array of strings): Масив елементів для обчислення хешу при BPF-балансуванні (`"eth"`, `"ipv4"`, `"ipv6"`, `"tcp"`, `"udp"`).
- `link_watch` (object): Глобальний монітор стану мережевих лінків.
  - `name` (string): Модуль опитування (`"ethtool"`, `"arp_ping"`, `"nsna_ping"`).
  - `interval` (number): Періодичність опитування в мілісекундах.
  - `delay_up` / `delay_down` (number): Затримки стабілізації лінка.
- `ports` (object): Словник підпорядкованих фізичних портів із їхніми індивідуальними налаштуваннями пріоритетів та локальних моніторів.

```json
{
  "device": "team0",
  "hwaddr": "52:54:00:12:34:56",
  "runner": {
    "name": "lacp",
    "active": true,
    "fast_rate": true,
    "select_policy": "bandwidth",
    "sys_prio": 65535,
    "tx_hash": ["eth", "ipv4", "ipv6", "tcp", "udp"],
    "tx_balancer": {
      "name": "basic"
    }
  },
  "link_watch": {
    "name": "ethtool",
    "interval": 10,
    "delay_up": 200,
    "delay_down": 200
  },
  "ports": {
    "eth0": {
      "prio": 100,
      "sticky": true,
      "link_watch": {
        "name": "arp_ping",
        "interval": 100,
        "target_host": "192.168.1.1",
        "source_host": "192.168.1.100",
        "init_drop_pings": 3
      }
    },
    "eth1": {
      "prio": 50,
      "link_watch": {
        "name": "nsna_ping",
        "interval": 100,
        "target_host": "fe80::1%eth1"
      }
    }
  }
}
```

### 3.2. Довідник типів плагінів (Runners) та моніторів (Link Watchers)

#### Виконавці (Runners):
- `roundrobin`: Послідовне кругове розсилання пакетів через усе розмаїття доступних портів.
- `activebackup`: Передача трафіку лише через один активний порт; інші знаходяться у резерві.
- `broadcast`: Одночасне дублювання всіх пакетів на всі активні порти.
- `random`: Випадковий вибір порту для кожного вихідного пакету.
- `loadbalance`: Динамічне або статичне хешування пакетів на основі BPF (Berkeley Packet Filter) з підтримкою збору статистики трафіку.
- `lacp`: Реалізація стандарту IEEE 802.3ad LACP з обробкою контрольних кадрів LACPDU.

#### Монітори зв'язку (Link Watchers):
- `ethtool`: Перевірка стану фіксованого носія (carrier state) через драйвер мережевої карти.
- `arp_ping`: Відправка та очікування відповіді на ARP-запити до цільового IP-вузла.
- `nsna_ping`: Перевірка доступності вузлів IPv6 за допомогою повідомлень ICMPv6 Neighbor Solicitation / Neighbor Advertisement.
- `ports_check`: Моніторинг стану інших підпорядкованих портів для формування комбінованих умов доступності.

---

## 4. Протокол IPC у Team (DBus та Unix Control Socket)

Демон `teamd` відкриває Unix Domain Socket за шляхом `/var/run/teamd/team0.sock` або реєструє сервіс на системній шині DBus `org.libteam.teamd.team0`.

### 4.1. Формат повідомлень Unix IPC

Керуюча утиліта `teamdctl` надсилає запити до демона у вигляді JSON-структур згідно з протоколом `teamd IPC`:

#### Запит стану порту (Get Port State):
```json
{
  "method": "port_list_get"
}
```

#### Відповідь демона:
```json
{
  "result": {
    "eth0": {
      "linkup": true,
      "runner_port_data": {
        "state": "current",
        "key": 1,
        "prio": 100
      },
      "speed": 10000,
      "duplex": "full"
    },
    "eth1": {
      "linkup": true,
      "runner_port_data": {
        "state": "current",
        "key": 1,
        "prio": 50
      },
      "speed": 10000,
      "duplex": "full"
    }
  }
}
```

#### Динамічна зміна параметрів "на льоту":
Для зміни налаштувань без перезапуску демона надсилається команда `option_set`:
```json
{
  "method": "option_set",
  "params": {
    "name": "mode",
    "value": "activebackup"
  }
}
```

Ця вичерпна специфікація атрибутів та форматів надає системному інженеру всі необхідні дані для взаємодії з драйверами агрегації каналів на будь-якому рівні абстракції.
