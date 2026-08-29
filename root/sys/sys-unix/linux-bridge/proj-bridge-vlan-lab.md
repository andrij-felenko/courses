# ⚙️ Практикум: конфігурація VLAN Filtering та керування FDB у Linux Bridge

У сучасних хмарних платформах, гіпервізорах віртуалізації та контейнерних середовищах виникає потреба ізолювати трафік багатьох клієнтів (Multi-Tenancy) на канальному рівні (L2) без виділення під кожного з них окремого фізичного обладнання або окремого віртуального моста. Історичний підхід зі створенням десятків окремих екземплярів `br10`, `br20` та прив'язкою віртуальних саб-інтерфейсів `eth0.10`, `eth0.20` призводив до надмірного споживання пам'яті ядром, просідання кешу процесора та високих накладних витрат на синхронізацію блокувань.

Механізм **VLAN Filtering** (`vlan_filtering 1`) перетворює єдиний екземпляр Linux Bridge на повноцінний VLAN-aware комутатор стандарту IEEE 802.1Q. Цей практикум демонструє повний інженерний цикл: побудову віртуальної топології на базі мережевих просторів імен (`netns`) та пар `veth`, конфігурацію Access і Trunk портів через утиліту `bridge vlan`, тестування ізоляції та міжсегментної маршрутизації, низькорівневе програмне інжектування статичних записів у таблицю комутації FDB через Netlink API на мовах C та C++, а також діагностику проходження кадрів за допомогою `tcpdump`, лічильників ядра та `dropwatch`.

---

## 1. Архітектура лабораторного стенду та модель віртуалізації L2

Лабораторний стенд моделює типову мережеву топологію вузла віртуалізації з двома ізольованими клієнтськими сегментами (Tenant Blue та Tenant Red) та маршрутизатором для міжсегментного обміну.

```
                           +-------------------------------------------------+
                           |              Linux Bridge br-core               |
                           |              (vlan_filtering = 1)               |
                           |  [ FDB: {MAC, VID} -> Port ] [ 802.1Q Filter ]  |
                           +----+---------------+---------------+------------+
                                | (PVID 10)     | (PVID 10)     | (PVID 20)  | (Trunk: VID 10,20)
                                | Untagged      | Untagged      | Untagged   | Tagged
                                v               v               v            v
                           [veth-b1-br]    [veth-b2-br]    [veth-r1-br] [veth-rt-br]
                                |               |               |            |
                           (veth pair)     (veth pair)     (veth pair)  (veth pair)
                                |               |               |            |
                                v               v               v            v
                            [ns-blue1]      [ns-blue2]      [ns-red1]   [ns-router]
                           192.168.10.1    192.168.10.2    192.168.20.1  eth0.10: 192.168.10.254
                            (VLAN 10)       (VLAN 10)       (VLAN 20)    eth0.20: 192.168.20.254
```

### Функціональні зони та вузли стенду

1. **Клієнтський сегмент Blue (VLAN 10)**:
   - Простір імен `ns-blue1` з адресою `192.168.10.1/24` (інтерфейс `eth0`).
   - Простір імен `ns-blue2` з адресою `192.168.10.2/24` (інтерфейс `eth0`).
   - Обидва вузли знаходяться в єдиному широкомовному домені L2 і мають безперешкодно обмінюватися даними.
2. **Клієнтський сегмент Red (VLAN 20)**:
   - Простір імен `ns-red1` з адресою `192.168.20.1/24` (інтерфейс `eth0`).
   - Прямий L2-обмін між вузлами Blue і Red суворо заблокований на канальному рівні моста.
3. **Маршрутизатор та шлюз за замовчуванням (`ns-router`)**:
   - Магістральний транковий вузол із субінтерфейсами IEEE 802.1Q: `eth0.10` (`192.168.10.254/24`) та `eth0.20` (`192.168.20.254/24`).
   - Підключений через транк-порт моста, який пропускає кадри обох VLAN у тегованому вигляді для забезпечення керованої L3-маршрутизації між орендарями.

### Механізм роботи віртуальних кабелів `veth`

Ізоляція просторів імен забезпечується віртуальними Ethernet-парами `veth` (драйвер `drivers/net/veth.c`). Кожна пара функціонує як двосторонній канальний тунель:

```
[ Простір імен ns-blue1 ]                         [ Кореневий простір хоста ]
+-----------------------+                         +-------------------------+
| eth0 (veth-b1)        |                         | veth-b1-br (Slave port) |
| dev_hard_start_xmit() | --- dev_forward_skb() -> | rx_handler =            |
|                       |                         |   br_handle_frame()     |
+-----------------------+                         +-------------------------+
```

Коли мережевий стек усередині `ns-blue1` надсилає кадр через інтерфейс `eth0`, драйвер викликає функцію `veth_xmit()`. Вона підміняє пристрій у структурі `sk_buff` на протилежний кінець пари (`veth-b1-br`) і викликає `dev_forward_skb()` або `netif_rx()`. Пакет миттєво з'являється у черзі прийому хостового інтерфейсу без проходження через фізичні кільцеві буфери DMA або апаратні переривання, після чого перехоплюється комутаційним обробником `rx_handler` (`br_handle_frame`) комутатора `br-core`.

---

## 2. Покрокове розгортання топології через утиліти `ip` та `bridge`

Розгортання тестового середовища виконується у п'ять послідовних кроків: від ініціалізації ядра комутатора до перевірки міжсегментної ізоляції.

### Крок 1. Створення комутатора з підтримкою VLAN Filtering

Під час створення моста параметр `vlan_filtering 1` активує внутрішній механізм обробки та перевірки тегів IEEE 802.1Q (`CONFIG_BRIDGE_VLAN_FILTERING`). Якщо створити звичайний міст без цього параметра, комутатор пропускатиме всі теговані кадри прозоро як звичайний нерозбірливий хаб, не виконуючи ізоляції портів за ідентифікаторами VLAN ID.

```bash
# 1. Створюємо інтерфейс моста з увімкненою фільтрацією VLAN
sudo ip link add name br-core type bridge vlan_filtering 1

# 2. Переводимо міст в активний робочий стан
sudo ip link set dev br-core up
```

Перевіримо активовані властивості створеного комутатора:

```bash
ip -d link show br-core
```

Вивід команди підтверджує наявність прапорця `vlan_filtering 1` та системного PVID за замовчуванням:

```
4: br-core: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP mode DEFAULT group default qlen 1000
    link/ether 52:54:00:12:34:56 brd ff:ff:ff:ff:ff:ff promiscuity 0 minmtu 68 maxmtu 65535
    bridge forward_delay 1500 hello_time 200 max_age 2000 ageing_time 30000 stp_state 0 priority 32768 vlan_filtering 1 vlan_protocol 802.1Q default_pvid 1
```

### Крок 2. Створення мережевих просторів імен та зв'язування veth-парами

Створимо ізольовані простори імен для клієнтів `ns-blue1`, `ns-blue2`, `ns-red1` та з'єднаємо їх з мостом `br-core` за допомогою віртуальних кабелів `veth`.

:::code proj-bridge-vlan-lab/sh/krok-2-stvorennia.sh

Додатково створимо магістральний простір імен `ns-router` для транкового підключення:

```bash
# Створюємо простір імен маршрутизатора
sudo ip netns add ns-router

# Створюємо транкову пару veth
sudo ip link add veth-rt type veth peer name veth-rt-br

# Переносимо клієнтський кінець у ns-router
sudo ip link set veth-rt netns ns-router

# Приєднуємо хостовий кінець до моста br-core і піднімаємо його
sudo ip link set veth-rt-br master br-core
sudo ip link set dev veth-rt-br up
```

Коли інтерфейс переноситься в простір імен командою `ip link set dev ... netns ...`, ядро змінює покажчик `dev_net(dev)` на цільову структуру `struct net`. Інтерфейс зникає з таблиць хоста й отримує власну ізольовану таблицю маршрутизації, ARP-кеш і таблицю сокетів.

### Крок 3. Налаштування IP-адрес та мережевих стеків

Всередині кожного клієнтського простору імен віртуальний інтерфейс стандартизовано перейменовується на `eth0`. Також обов'язково активується петльовий інтерфейс `lo`, без якого локальні сокети та системні резолвери не зможуть відкривати дескриптори `127.0.0.1`.

:::code proj-bridge-vlan-lab/sh/krok-3-nalashtuvannia-ip.sh

Тепер сконфігуруємо маршрутизатор `ns-router`: перейменуємо інтерфейс на `eth0`, створимо теговані віртуальні саб-інтерфейси стандарту 802.1Q для VLAN 10 та VLAN 20, призначимо їм IP-адреси шлюзів і ввімкнемо форвардинг пакетів на рівні ядра:

```bash
# Активуємо loopback та піднімаємо базовий інтерфейс eth0
sudo ip -n ns-router link set lo up
sudo ip -n ns-router link set dev veth-rt name eth0
sudo ip -n ns-router link set dev eth0 up

# Створюємо саб-інтерфейси IEEE 802.1Q
sudo ip -n ns-router link add link eth0 name eth0.10 type vlan id 10
sudo ip -n ns-router link add link eth0 name eth0.20 type vlan id 20

# Призначаємо адреси шлюзів
sudo ip -n ns-router addr add 192.168.10.254/24 dev eth0.10
sudo ip -n ns-router addr add 192.168.20.254/24 dev eth0.20

# Піднімаємо саб-інтерфейси
sudo ip -n ns-router link set dev eth0.10 up
sudo ip -n ns-router link set dev eth0.20 up

# Вмикаємо IPv4-маршрутизацію всередині ns-router
sudo ip netns exec ns-router sysctl -w net.ipv4.ip_forward=1

# Прописуємо маршрути за замовчуванням у клієнтських просторах імен
sudo ip -n ns-blue1 route add default via 192.168.10.254
sudo ip -n ns-blue2 route add default via 192.168.10.254
sudo ip -n ns-red1 route add default via 192.168.20.254
```

### Крок 4. Налаштування членства у VLAN: Access проти Trunk

За замовчуванням при додаванні інтерфейсу до моста ядро призначає йому VLAN 1 із прапорцями `pvid` та `untagged`. Якщо залишити конфігурацію за замовчуванням, трафік між неналаштованими портами почне витікати у спільний домен VLAN 1. Тому першим обов'язковим кроком є видалення дефолтного VLAN 1 з усіх портів.

Семантика прапорців конфігурації `bridge vlan`:
- **`pvid` (Port VLAN ID)**: призначає внутрішній тег VLAN для будь-якого нетегованого (Untagged) кадру, що надходить у цей порт від клієнта;
- **`untagged`**: наказує комутатору знімати 4-байтний заголовок 802.1Q під час виходу кадру з цього порту у напрямку до клієнта (режим Access Port);
- **Відсутність `untagged`**: змушує міст зберігати 4-байтний заголовок 802.1Q на виході (режим Trunk Port).

Налаштуємо Access-порти клієнтів:

:::code proj-bridge-vlan-lab/sh/krok-4-nalashtuvannia.sh

Налаштуємо транковий порт для маршрутизатора `veth-rt-br`:

```bash
# Очищаємо дефолтний VLAN 1
sudo bridge vlan del dev veth-rt-br vid 1

# Додаємо членство у VLAN 10 та VLAN 20 у тегованому вигляді (Trunk)
sudo bridge vlan add dev veth-rt-br vid 10
sudo bridge vlan add dev veth-rt-br vid 20
```

Перевіримо підсумкову таблицю членства у віртуальних мережах:

```bash
bridge vlan show
```

Вивід демонструє чіткий розподіл ролей портів:

```
port              vlan-id  
br-core           1 PVID untagged
veth-b1-br        10 PVID untagged
veth-b2-br        10 PVID untagged
veth-r1-br        20 PVID untagged
veth-rt-br        10
                  20
```

### Крок 5. Перевірка канальної ізоляції та міжсегментного трафіку

Перевіримо коректність функціонування L2-комутації у межах одного сегмента, міжсегментної ізоляції та маршрутизованого обміну.

**1. Тестування зв'язку всередині одного VLAN 10 (вузол `ns-blue1` пінгує `ns-blue2`):**

```bash
sudo ip netns exec ns-blue1 ping -c 2 192.168.10.2
```

```
PING 192.168.10.2 (192.168.10.2) 56(84) bytes of data.
64 bytes from 192.168.10.2: icmp_seq=1 ttl=64 time=0.048 ms
64 bytes from 192.168.10.2: icmp_seq=2 ttl=64 time=0.035 ms

--- 192.168.10.2 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1024ms
rtt min/avg/max/mdev = 0.035/0.041/0.048/0.006 ms
```

Кадри проходять успішно: нетегований ARP-запит від `ns-blue1` маркується мостом як VID 10 завдяки `pvid`, реплікується на порт `veth-b2-br`, де правило `untagged` знімає тег перед передачею в `ns-blue2`.

**2. Тестування прямої канальної ізоляції між VLAN 10 та VLAN 20:**

Спробуємо звернутися з `ns-blue1` напряму до IP-адреси `192.168.20.1` без залучення шлюзу (за допомогою примусового ARP-запиту в локальний L2-сегмент):

```bash
sudo ip netns exec ns-blue1 arping -c 2 -I eth0 192.168.20.1
```

```
ARPING 192.168.20.1 from 192.168.10.1 eth0
Sent 2 probes (2 broadcast(s))
Received 0 response(s)
```

Широкомовний ARP-запит із тегом VID 10 скидається мостом під час спроби потрапити на порт `veth-r1-br`, оскільки цей порт не є членом VLAN 10. Клієнти різних VLAN повністю ізольовані на канальному рівні.

**3. Тестування міжмережевої маршрутизації через `ns-router`:**

```bash
sudo ip netns exec ns-blue1 ping -c 2 192.168.20.1
```

```
PING 192.168.20.1 (192.168.20.1) 56(84) bytes of data.
64 bytes from 192.168.20.1: icmp_seq=1 ttl=63 time=0.082 ms
64 bytes from 192.168.20.1: icmp_seq=2 ttl=63 time=0.061 ms

--- 192.168.20.1 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1018ms
rtt min/avg/max/mdev = 0.061/0.071/0.082/0.010 ms
```

Пакет успішно подолав повний маршрут: `ns-blue1` надіслав пакет шлюзу `192.168.10.254`, міст позначив його тегом VID 10 і передав тегованим на `veth-rt-br`. Всередині `ns-router` субінтерфейс `eth0.10` прийняв пакет, L3-стек ядра виконав маршрутизацію у субінтерфейс `eth0.20`, який додав тег VID 20. Міст прийняв тегований кадр VID 20 і спрямував його на порт `veth-r1-br`, знявши тег перед доставкою в `ns-red1`. Зменшення TTL з 64 до 63 підтверджує факт проходження через L3-маршрутизатор.

---

## 3. Програмне керування FDB через Netlink API

У високонавантажених SDN-контролерах, системах контейнерної оркестрації або агентах міграції віртуальних машин виконання зовнішніх CLI-команд (`bridge fdb add`) неприпустиме через колосальний оверхед системних викликів `fork()` та `execve()`. Пряме керування таблицею FDB здійснюється через сокети `AF_NETLINK` сімейства `NETLINK_ROUTE`.

### Формат бінарного повідомлення `RTM_NEWNEIGH`

Для додавання запису в FDB комутатора формується повідомлення `RTM_NEWNEIGH` із сімейством адресації `AF_BRIDGE`:

```
+-------------------------------------------------------------------------+
| struct nlmsghdr (nlmsg_len, nlmsg_type=RTM_NEWNEIGH, flags)            |
+-------------------------------------------------------------------------+
| struct ndmsg (ndm_family=AF_BRIDGE, ndm_ifindex, ndm_state, ndm_flags)  |
+-------------------------------------------------------------------------+
| struct rtattr (rta_type=NDA_LLADDR, rta_len=10) -> [ 6 байтів MAC ]     |
| [ 2 байти вирівнювання RTA_ALIGN ]                                      |
+-------------------------------------------------------------------------+
| struct rtattr (rta_type=NDA_VLAN, rta_len=6) -> [ 2 байти VID ]         |
| [ 2 байти вирівнювання RTA_ALIGN ]                                      |
+-------------------------------------------------------------------------+
```

Ключові поля та константи:
- **`ndm_state = NUD_PERMANENT`** (`0x80`): оголошує запис статичним. Такий запис не підлягає видаленню фоновим таймером застарівання (`ageing_time`);
- **`ndm_flags = NTF_MASTER`** (`0x04`): вказує ядру внести запис у таблицю FDB батьківського моста, а не в апаратну таблицю кінцевого драйвера мережевої карти;
- **`nlmsg_flags = NLM_F_REQUEST | NLM_F_CREATE | NLM_F_REPLACE | NLM_F_ACK`**: запит на створення або атомарне оновлення запису із обов'язковим поверненням квитанції `NLMSG_ERROR` (код 0 свідчить про успіх).

Макроси `NLMSG_ALIGN()` та `RTA_ALIGN()` забезпечують суворе вирівнювання зміщень по 4-байтній межі. Порушення вирівнювання призводить до того, що парсер ядра `nlmsg_parse()` відкидає повідомлення з помилкою `-EINVAL`.

:::tabs
:::code proj-bridge-vlan-lab/c/bridge_fdb_inject.c
:::code proj-bridge-vlan-lab/cpp/bridge_fdb_inject.cpp
:::

### Архітектура та особливості C++ реалізації

C++ версія демонструє ідіоматичні практики системного програмування:
1. **RAII-обгортка `NetlinkSocket`**: гарантує детерміноване закриття сокетного файлового дескриптора при виході з області видимості, блокує копіювання (`delete`) та дозволяє безпечне переміщення (`noexcept move`).
2. **Монадична обробка помилок `std::expected`**: функції `MacAddress::from_string()` та `BridgeController::add_static_fdb()` повертають типізовані результати або системні коди помилок `std::error_code`, виключаючи неконтрольовані винятки та невизначений стан пам'яті.
3. **Безпечна типізація MAC-адреси**: структура `MacAddress` інкапсулює `std::array<uint8_t, 6>`, що унеможливлює помилки розміру буфера при копіюванні у бінарні атрибути Netlink.

### Збірка та практична інжекція запису

Скомпілюємо обидва варіанти утиліти:

```bash
# Збірка версії C
gcc -O2 -Wall proj-bridge-vlan-lab/c/bridge_fdb_inject.c -o bridge_fdb_inject_c

# Збірка версії C++ (вимагає підтримки C++23)
g++ -O2 -Wall -std=c++23 proj-bridge-vlan-lab/cpp/bridge_fdb_inject.cpp -o bridge_fdb_inject_cpp
```

Інжектуємо статичний запис для віртуального пристрою з адресою `02:42:0a:00:00:99` у VLAN 10 на порту `veth-b1-br`:

```bash
sudo ./bridge_fdb_inject_cpp veth-b1-br 02:42:0a:00:00:99 10
```

```
Статичний запис FDB успішно додано.
```

Перевіримо стан таблиці комутації для порту `veth-b1-br`:

```bash
bridge fdb show dev veth-b1-br
```

```
02:42:0a:00:00:99 vlan 10 master br-core permanent
```

Прапорець `permanent` підтверджує, що запис зафіксовано як статичний і він більше не залежить від активності відправника.

---

## 4. Діагностика, налагодження та трасування канального рівня

Експлуатація мостів із фільтрацією VLAN вимагає розуміння інструментів інспекції внутрішнього стану ядра та пакетного аналізу на канальному рівні.

### Аналіз таблиці FDB та життєвого циклу записів

Таблиця FDB ядра Linux містить записи чотирьох різних типів:

```bash
bridge fdb show
```

```
52:54:00:12:34:56 dev br-core vlan 1 master br-core permanent
e6:22:8b:41:2a:11 dev veth-b1-br master br-core permanent
e6:22:8b:41:2a:11 dev veth-b1-br vlan 10 master br-core permanent
02:42:0a:00:00:01 dev veth-b1-br vlan 10 master br-core
02:42:0a:00:00:99 dev veth-b1-br vlan 10 master br-core permanent
```

Розбір структури виводу:
- `permanent` — статичний або системний локальний запис, згенерований ядром або інжектований адміністратором;
- `vlan 10` — прив'язка MAC-адреси до конкретного сегмента IEEE 802.1Q. Якщо один і той самий MAC з'явиться у VLAN 20, міст створить окремий незалежний запис у хеш-таблиці;
- Запис без прапорця `permanent` (наприклад, `02:42:0a:00:00:01`) — динамічно вивчений запис (Dynamic Learned). Він оновлюється при кожному вхідному пакеті та автоматично знищується через `ageing_time` (300 секунд за замовчуванням) за відсутності трафіку.

### Захоплення тегованих Ethernet-кадрів через `tcpdump`

Стандартний запуск `tcpdump -i <interface>` приховує службові L2-заголовки. Для спостереження за мітками 802.1Q обов'язково використовуються ключі `-e` (друк Ethernet-заголовка) та `-nn` (числове відображення адрес і портів).

Запустимо захоплення трафіку на транковому порті `veth-rt-br` під час передачі ICMP-пакета між `ns-blue1` та `ns-red1`:

```bash
sudo tcpdump -e -nn -vvv -i veth-rt-br
```

Детальний лог перехопленого кадру:

```
16:40:12.891230 02:42:0a:00:00:01 > 02:42:0a:00:00:fe, ethertype 802.1Q (0x8100), length 102: vlan 10, p 0, ethertype IPv4 (0x0800), 192.168.10.1 > 192.168.20.1: ICMP echo request, id 1, seq 1, length 64
16:40:12.891285 02:42:0a:00:00:fe > 02:42:14:00:00:01, ethertype 802.1Q (0x8100), length 102: vlan 20, p 0, ethertype IPv4 (0x0800), 192.168.10.1 > 192.168.20.1: ICMP echo request, id 1, seq 1, length 64
```

У лозі чітко простежується трансформація тегів:
1. Вхідний кадр має EtherType `0x8100` (стандарт IEEE 802.1Q), `vlan 10`, пріоритет `p 0` (PCP = 0).
2. Після маршрутизації у просторі імен `ns-router` вихідний кадр повертається на міст із міткою `vlan 20`.

### Моніторинг подій FDB у реальному часі

Команда `bridge monitor` підписується на мультикаст-групу `RTNLGRP_NEIGH` і транслює всі події зміни стану FDB:

```bash
bridge monitor fdb
```

Приклад виводу під час міграції віртуального інтерфейсу або появи нового пристрою в мережі:

```
02:42:0a:00:00:02 dev veth-b2-br vlan 10 master br-core NEW
Deleted 02:42:0a:00:00:02 dev veth-b2-br vlan 10 master br-core
```

Цей інструмент є незамінним для виявлення ефекту **MAC Flapping** (коли внаслідок топологічної петлі один і той самий MAC поперемінно надходить з двох різних портів з інтервалом у мілісекунди).

### Аналіз лічильників статистики та втрат пакетів (`ip -s link`)

Якщо комутація не працює, першим кроком діагностики є перевірка лічильників помилок і скидань на інтерфейсах моста:

```bash
ip -s link show dev veth-b1-br
```

```
6: veth-b1-br@if5: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master br-core state UP mode DEFAULT group default qlen 1000
    link/ether e6:22:8b:41:2a:11 brd ff:ff:ff:ff:ff:ff link-netns ns-blue1
    RX:  bytes packets errors dropped overrun mcast   
         1428      18      0       0       0     4
    TX:  bytes packets errors dropped carrier collsns 
         1260      16      0       0       0     0
```

Якщо поле `dropped` у секції RX зростає при спробі відправки кадрів, це означає, що кадри блокуються вхідним фільтром моста (Ingress Filtering) через невідповідність дозволеним VID або відсутність налаштованого PVID.

### Трасування скинутих пакетів ядра через `dropwatch` та `bpftrace`

Коли пакет відкидається ядром всередині комутатора, утиліта `dropwatch` фіксує виклики системної функції `kfree_skb()` та вказує точне ім'я функції ядра, де стався дроп:

```bash
sudo dropwatch -l kas
```

```
Inactivity timeout reached
1 drops at br_vlan_allowed+0x54 [bridge]
2 drops at br_handle_frame+0x182 [bridge]
```

Значення ключових точок скидання у підсистемі моста:
- `br_vlan_allowed()`: кадр містить VID, який відсутній у бітовій масці дозволених VLAN порту, або на порт надійшов нетегований кадр без налаштованого PVID;
- `br_handle_frame()`: порт перебуває у стані STP `DISABLED` або `BLOCKING`;
- `br_fdb_update()`: виявлено заборонену спробу перезапису статичного запису FDB іншим портом.

Для точкового перехоплення контексту пакета у реальному часі можна застосувати однорядковий скрипт `bpftrace`:

```bash
sudo bpftrace -e 'kprobe:br_vlan_allowed { printf("VLAN перевірка skb=%p на порті %s\n", arg0, ((struct net_bridge_port *)arg1)->dev->name); }'
```

---

## 5. Автоматизація розгортання та гарантоване очищення стенду

Для практичних лабораторних робіт та автоматизованого тестування у CI/CD пайплайнах розгортання та видалення ресурсів стенду загортають в єдиний ідемпотентний сценарій bash із перехопленням сигналів завершення (`trap ... EXIT SIGINT SIGTERM`).

```bash
#!/usr/bin/env bash
set -euo pipefail

BRIDGE_NAME="br-core"
NAMESPACES=("ns-blue1" "ns-blue2" "ns-red1" "ns-router")

cleanup() {
    echo "[*] Очищення ресурсів лабораторного стенду..."
    # 1. Видаляємо міст (автоматично відв'язує всі підпорядковані порти)
    if ip link show "${BRIDGE_NAME}" &>/dev/null; then
        ip link del dev "${BRIDGE_NAME}"
    fi

    # 2. Видаляємо простори імен (автоматично знищує пов'язані veth-пари)
    for ns in "${NAMESPACES[@]}"; do
        if ip netns list | grep -qw "${ns}"; then
            ip netns del "${ns}"
        fi
    done
    echo "[+] Лабораторне середовище успішно очищено."
}

# Встановлюємо гарантований обробник аварійного або штатного завершення
trap cleanup EXIT SIGINT SIGTERM

echo "[1/4] Створення моста br-core з VLAN Filtering..."
ip link add name "${BRIDGE_NAME}" type bridge vlan_filtering 1
ip link set dev "${BRIDGE_NAME}" up

echo "[2/4] Створення просторів імен та топології veth..."
for ns in "${NAMESPACES[@]}"; do
    ip netns add "${ns}"
done

# Клієнтські пари
ip link add veth-b1 type veth peer name veth-b1-br
ip link add veth-b2 type veth peer name veth-b2-br
ip link add veth-r1 type veth peer name veth-r1-br
ip link add veth-rt type veth peer name veth-rt-br

ip link set veth-b1 netns ns-blue1
ip link set veth-b2 netns ns-blue2
ip link set veth-r1 netns ns-red1
ip link set veth-rt netns ns-router

for port in veth-b1-br veth-b2-br veth-r1-br veth-rt-br; do
    ip link set "${port}" master "${BRIDGE_NAME}"
    ip link set dev "${port}" up
done

echo "[3/4] Конфігурація IP-адрес та саб-інтерфейсів..."
# ns-blue1
ip -n ns-blue1 link set lo up
ip -n ns-blue1 link set dev veth-b1 name eth0
ip -n ns-blue1 addr add 192.168.10.1/24 dev eth0
ip -n ns-blue1 link set dev eth0 up
ip -n ns-blue1 route add default via 192.168.10.254

# ns-blue2
ip -n ns-blue2 link set lo up
ip -n ns-blue2 link set dev veth-b2 name eth0
ip -n ns-blue2 addr add 192.168.10.2/24 dev eth0
ip -n ns-blue2 link set dev eth0 up
ip -n ns-blue2 route add default via 192.168.10.254

# ns-red1
ip -n ns-red1 link set lo up
ip -n ns-red1 link set dev veth-r1 name eth0
ip -n ns-red1 addr add 192.168.20.1/24 dev eth0
ip -n ns-red1 link set dev eth0 up
ip -n ns-red1 route add default via 192.168.20.254

# ns-router
ip -n ns-router link set lo up
ip -n ns-router link set dev veth-rt name eth0
ip -n ns-router link set dev eth0 up
ip -n ns-router link add link eth0 name eth0.10 type vlan id 10
ip -n ns-router link add link eth0 name eth0.20 type vlan id 20
ip -n ns-router addr add 192.168.10.254/24 dev eth0.10
ip -n ns-router addr add 192.168.20.254/24 dev eth0.20
ip -n ns-router link set dev eth0.10 up
ip -n ns-router link set dev eth0.20 up
ip netns exec ns-router sysctl -w net.ipv4.ip_forward=1 >/dev/null

echo "[4/4] Налаштування таблиці bridge vlan..."
# Blue Access (VLAN 10)
bridge vlan del dev veth-b1-br vid 1
bridge vlan add dev veth-b1-br vid 10 pvid untagged
bridge vlan del dev veth-b2-br vid 1
bridge vlan add dev veth-b2-br vid 10 pvid untagged

# Red Access (VLAN 20)
bridge vlan del dev veth-r1-br vid 1
bridge vlan add dev veth-r1-br vid 20 pvid untagged

# Router Trunk (VLAN 10, 20 Tagged)
bridge vlan del dev veth-rt-br vid 1
bridge vlan add dev veth-rt-br vid 10
bridge vlan add dev veth-rt-br vid 20

echo "[+] Стенд успішно розгорнуто. Запуск тестових перевірок:"
echo "--- Тест 1: Зв'язок Blue1 -> Blue2 (Intra-VLAN 10) ---"
ip netns exec ns-blue1 ping -c 2 192.168.10.2

echo "--- Тест 2: Зв'язок Blue1 -> Red1 через Router (Inter-VLAN) ---"
ip netns exec ns-blue1 ping -c 2 192.168.20.1

echo "[*] Тести пройдено успішно. Натисніть Ctrl+C для завершення та очищення."
sleep infinity
```

### Механізм каскадного видалення ресурсів у ядрі

Скрипт покладається на детерміновану поведінку мережевого стека Linux:
1. Коли виконується `ip netns del <ns>`, ядро знищує відповідний дескриптор `struct net` і починає дереєстрацію всіх інтерфейсів, що йому належали.
2. Дереєстрація інтерфейсу `veth` всередині простору імен автоматично викликає функцію драйвера `veth_dellink()`, яка негайно видаляє парний хостовий інтерфейс `veth-*-br` і коректно вивільняє асоційовані записи у таблиці FDB моста.
3. Видалення інтерфейсу моста `ip link del dev br-core` автоматично скидає обробник `dev->rx_handler` на всіх підпорядкованих інтерфейсах і повертає їх у нейтральний стан.

