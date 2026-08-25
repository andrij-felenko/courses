# 📋 Довідник інтерфейсу ethtool Netlink API

Цей довідник містить систематизоване описування констант, команд, ідентифікаторів атрибутів Netlink (NLA), типів бітових масивів та структур розширених помилок (`extack`), що складають програмний інтерфейс **Generic Netlink ethtool API** в ядрі Linux (визначений у заголовкових файлах `<linux/ethtool_netlink.h>` та `<linux/ethtool.h>`).

## 1. Специфікація сімейства Generic Netlink

Підсистема ethtool Netlink реєструється в базовій інфраструктурі Generic Netlink під час завантаження ядра. На відміну від класичного протоколу `rtnetlink`, який має фіксоване номерне сімейство (`NETLINK_ROUTE`), Generic Netlink виділяє номер сімейства (Family ID) динамічно з діапазону вищих номерів (зазвичай `0x0010`–`0x00ff`).

Простір користувача зобов'язаний перед початком будь-якої взаємодії відправити запит до системного контролера Generic Netlink (`GENL_ID_CTRL`) з рядковим іменем `"ethtool"`, щоб отримати поточний Family ID та ідентифікатор багатоадресної групи подій.

| Параметр / Константа | Значення | Опис |
| :--- | :--- | :--- |
| **Назва сімейства** (`ETHTOOL_GENL_NAME`) | `"ethtool"` | Рядковий ідентифікатор для запиту динамічного ID через `GENL_ID_CTRL` |
| **Версія API** (`ETHTOOL_GENL_VERSION`) | `1` | Поточна версія протоколу ethtool Netlink у ядрі Linux |
| **Multicast група** (`ETHTOOL_MCGRP_MONITOR`) | `"monitor"` | Група багатоадресної розсилки для отримання сповіщень `*_NTF` |

Мережеві додатки приєднуються до багатоадресної групи `"monitor"` шляхом виконання системного виклику `setsockopt(fd, SOL_NETLINK, NETLINK_ADD_MEMBERSHIP, &group_id, sizeof(group_id))`. Це дозволяє ядру відправляти копію будь-яких кадрів сповіщень (`ETHTOOL_MSG_*_NTF`) у сокет при зміні конфігурації з боку будь-якого процесу або при виникненні апаратних подій на мережевих адаптерах.

---

## 2. Анатомія та атрибути заголовка `ETHTOOL_A_HEADER`

Кожен запит від простору користувача до ядра та кожна відповідь ядра містить обов'язковий вкладений атрибут заголовка з типом `ETHTOOL_A_HEADER`. Цей заголовок виконує роль селектора пристрою та контексту виконання.

### Атрибути `ETHTOOL_A_HEADER_*`

| Атрибут | Тип NLA | Опис |
| :--- | :--- | :--- |
| `ETHTOOL_A_HEADER_DEV_INDEX` | `NLA_U32` | Унікальний індекс мережевого інтерфейсу в ядрі (`ifindex`, наприклад `2`) |
| `ETHTOOL_A_HEADER_DEV_NAME` | `NLA_NUL_STRING` | Текстове ім'я інтерфейсу (наприклад, `"eth0"`, `"enp3s0"`) |
| `ETHTOOL_A_HEADER_FLAGS` | `NLA_U32` | Бітова маска прапорців запиту (`ETHTOOL_FLAG_*`) |

Ядро реалізує двоваріантну схему адресації пристроїв:
* **За індексом (`DEV_INDEX`)**: Якщо в заголовку вказано `ETHTOOL_A_HEADER_DEV_INDEX`, ядро виконує пошук об'єкта `struct net_device` у вихідній хеш-таблиці мережевого простору імен за допомогою O(1) виклику `dev_get_by_index_rcu()`. Це є найшвидшим способом адресації для високопродуктивних систем.
* **За іменем (`DEV_NAME`)**: Якщо вказано `ETHTOOL_A_HEADER_DEV_NAME`, ядро знаходить пристрій через виклик `dev_get_by_name_rcu()`.

Якщо в заголовку вказано обидва атрибути, ядро перевіряє їх на відповідність. У разі розбіжності між індексом та іменем запит відхиляється з помилкою `-EINVAL`.

### Прапорці керування заголовка (`ETHTOOL_A_HEADER_FLAGS`)

* `ETHTOOL_FLAG_COMPACT_BITSETS` (0x01): Наказує ядру повертати бітові карти режимів лінку та прапорців прискорення у компактному двійковому масиві слів `NLA_BITSET_VALUE`/`NLA_BITSET_MASK` замість розгортання повного списку текстових імен. Це оптимізує розмір кадру та знижує накладні витрати на виділення пам'яті.
* `ETHTOOL_FLAG_OMIT_REPLY` (0x02): Використовується у запитах модифікації `SET`. Наказує ядру не надсилати підтверджувальний кадр із оновленим станом, якщо операція успішна, обмежуючись лише стандартним ACK або відсутністю відповіді. Це суттєво зменшує навантаження на IPC в автоматизованих системах конфігурації.
* `ETHTOOL_FLAG_STATS` (0x04): Вимагає від ядра додатково приєднувати лічильники апаратної статистики до відповідей на запити `LINKINFO` чи `RINGS`.

---

## 3. Повна таблиця команд `ETHTOOL_MSG_*`

Повідомлення ethtool Netlink діляться на три логічні типи: запити читання (`GET`), запити зміни стану (`SET`) та асинхронні трансляції подій (`NTF`), що розсилаються ядрам у multicast-групу `"monitor"`.

| Команда GET / SET / NTF | ID Повідомлення | Опис функціональності |
| :--- | :--- | :--- |
| `ETHTOOL_MSG_STRSET_GET` | 1 | Отримання списків рядкових назв (строкових сетів для статистики чи прапорців) |
| `ETHTOOL_MSG_LINKINFO_GET` / `SET` / `NTF` | 2, 3, 4 | Фізичний порт, тип трансивера (copper/fiber), налаштування MDI/MDI-X |
| `ETHTOOL_MSG_LINKMODES_GET` / `SET` / `NTF` | 5, 6, 7 | Швидкість, дуплекс, автоузгодження та бітові карти режимів зв'язку |
| `ETHTOOL_MSG_LINKSTATE_GET` | 8 | Поточний стан лінку (Up/Down), причини відсутності зв'язку (ExtLinkState) |
| `ETHTOOL_MSG_DEBUG_GET` / `SET` / `NTF` | 9, 10, 11 | Маска драйверного налагодження (`msglevel`) |
| `ETHTOOL_MSG_WOL_GET` / `SET` / `NTF` | 12, 13, 14 | Режими Wake-on-LAN (Magic Packet, Unicast, SecureOn password) |
| `ETHTOOL_MSG_FEATURES_GET` / `SET` / `NTF` | 15, 16, 17 | Апаратні офлоади (TSO, GRO, LRO, RX/TX Checksum) |
| `ETHTOOL_MSG_PRIVFLAGS_GET` / `SET` / `NTF` | 18, 19, 20 | Приватні прапорці налаштування конкретного драйвера вендора |
| `ETHTOOL_MSG_RINGS_GET` / `SET` / `NTF` | 21, 22, 23 | Розміри кільцевих буферів дескрипторів RX та TX |
| `ETHTOOL_MSG_CHANNELS_GET` / `SET` / `NTF` | 24, 25, 26 | Кількість апаратних RX/TX/Combined каналів (переривань MSI-X / RSS) |
| `ETHTOOL_MSG_COALESCE_GET` / `SET` / `NTF` | 27, 28, 29 | Таймери та ліміти модерації переривань (Interrupt Coalescing) |
| `ETHTOOL_MSG_PAUSE_GET` / `SET` / `NTF` | 30, 31, 32 | Налаштування кадрів управління потоком IEEE 802.3x (Pause Frames) |
| `ETHTOOL_MSG_EEE_GET` / `SET` / `NTF` | 33, 34, 35 | Параметри енергозберігаючого Ethernet (Energy Efficient Ethernet) |
| `ETHTOOL_MSG_TSO_GET` / `SET` | 36, 37 | Статистика та налаштування Thermal Squelch / Transceiver |
| `ETHTOOL_MSG_FEC_GET` / `SET` / `NTF` | 38, 39, 40 | Режими корекції помилок (Forward Error Correction: Off, RS, BaseR) |
| `ETHTOOL_MSG_MODULE_EEPROM_GET` | 41 | Зчитування вмісту пам'яті EEPROM SFP/QSFP/QSFP-DD трансиверів |
| `ETHTOOL_MSG_STATS_GET` | 42 | Запит стандартизованої статистики IEEE 802.3 та RMON |
| `ETHTOOL_MSG_PHC_VCLKS_GET` / `SET` | 43, 44 | Віртуальні годинники апаратного PTP (IEEE 1588 Precision Time Protocol) |

---

## 4. Деталізований розбір NLA атрибутів основних блоків

### 4.1. Режими зв'язку та фізичного лінку (`LINKMODES`)

Використовується для читання та встановлення параметрів швидкості, дуплексу та автоузгодження.

```text
ETHTOOL_A_LINKMODES_UNSPEC
ETHTOOL_A_LINKMODES_HEADER          /* Nested: ETHTOOL_A_HEADER */
ETHTOOL_A_LINKMODES_AUTONEG         /* NLA_U8: 0 = Off, 1 = On */
ETHTOOL_A_LINKMODES_OURS            /* Nested: Bitset підтримуваних і анонсованих локальних режимів */
ETHTOOL_A_LINKMODES_PEER            /* Nested: Bitset анонсованих режимів партнерського пристрою */
ETHTOOL_A_LINKMODES_SPEED           /* NLA_U32: Швидкість у Мбіт/с (наприклад 10000 для 10GbE) */
ETHTOOL_A_LINKMODES_DUPLEX          /* NLA_U8: 0x00 = Half Duplex, 0x01 = Full Duplex */
ETHTOOL_A_LINKMODES_MASTER_SLAVE_CFG/* NLA_U8: Налаштування Master/Slave для 1000BASE-T */
ETHTOOL_A_LINKMODES_LANES           /* NLA_U32: Кількість фізичних ліній (lanes, наприклад 4 для 100G) */
```

Атрибут `ETHTOOL_A_LINKMODES_OURS` містить три паралельні бітові маски:
1. `FORBIDDEN`: Режими, які примусово заблоковані конфігурацією.
2. `ACTUAL`: Підтримувані апаратні режими даного PHY-трансивера.
3. `ADVERTISED`: Режими, які анонсуються партнерському пристрою під час процедури автоузгодження.

### 4.2. Апаратні прискорення та офлоади (`FEATURES`)

Усі апаратні фічі передаються у вигляді чотирьох бітових карт для збереження повної картини стану прискорення в ядрі:

```text
ETHTOOL_A_FEATURES_HEADER          /* Nested: ETHTOOL_A_HEADER */
ETHTOOL_A_FEATURES_HW              /* Nested: Bitset усіх апаратно підтримуваних фіч */
ETHTOOL_A_FEATURES_WANTED          /* Nested: Bitset бажаного стану, який запросив користувач */
ETHTOOL_A_FEATURES_ACTIVE          /* Nested: Bitset поточних реально активних фіч у ядрі */
ETHTOOL_A_FEATURES_NOCHANGE        /* Nested: Bitset фіч, які заблоковані драйвером від змін */
```

Структура `Bitset` передається у двох альтернативних форматах залежно від прапорця `ETHTOOL_FLAG_COMPACT_BITSETS`:
* **Компактний формат (Compact Bitset)**: Містить `ETHTOOL_A_BITSET_SIZE` (кількість бітів) та два бінарних масиви слів `ETHTOOL_A_BITSET_VALUE` й `ETHTOOL_A_BITSET_MASK`. Це дає мінімальний розмір пакета.
* **Розгорнутий формат (Verbose Bitset)**: Містить вкладену колекцію `ETHTOOL_A_BITSET_BITS`, де кожен біт описується окремим блоком з ідентифікатором `ETHTOOL_A_BITSET_BIT_INDEX` та текстовим іменем `ETHTOOL_A_BITSET_BIT_NAME` (наприклад, `"rx-checksum"`, `"tx-scatter-gather"`, `"tx-tcp-segmentation"`).

### 4.3. Кільцеві буфери (`RINGS`)

Дозволяє налаштовувати розмір кольорових буферів дескрипторів прямих каналів пам'яті DMA:

| Атрибут | Тип NLA | Значення |
| :--- | :--- | :--- |
| `ETHTOOL_A_RINGS_HEADER` | `Nested` | Стандартний заголовок із `ifindex` |
| `ETHTOOL_A_RINGS_RX_MAX` | `NLA_U32` | Максимально можливий розмір кільця прийому (чисто для читання) |
| `ETHTOOL_A_RINGS_RX` | `NLA_U32` | Поточний активний розмір кільця прийому (RX ring size) |
| `ETHTOOL_A_RINGS_TX_MAX` | `NLA_U32` | Максимально можливий розмір кільця передачі |
| `ETHTOOL_A_RINGS_TX` | `NLA_U32` | Поточний активний розмір кільця передачі (TX ring size) |
| `ETHTOOL_A_RINGS_RX_PUSH` | `NLA_U8` | Прапорець активації прямого проштовхування RX дескрипторів |

При встановленні нових розмірів кільцевих буферів ядро викликає метод драйвера `set_ringparam()`, який перерозподіляє пам'ять DMA в ядрі.

### 4.4. Стандартизована статистика (`STATS`)

Групує апаратні лічильники за міжнародними специфікаціями IEEE 802.3 та RMON:

```text
ETHTOOL_A_STATS_HEADER              /* Nested: ETHTOOL_A_HEADER */
ETHTOOL_A_STATS_GROUPS              /* NLA_U32: Бітова маска груп (ETH_PHY, ETH_MAC, ETH_CTRL, RMON) */
ETHTOOL_A_STATS_GRP                 /* Nested: Вкладена група лічильників */
  ├── ETHTOOL_A_STATS_GRP_ID        /* NLA_U32: Ідентифікатор групи */
  └── ETHTOOL_A_STATS_GRP_STAT      /* Nested: Конкретний лічильник */
        ├── ETHTOOL_A_STAT_NAME     /* NLA_STRING: Назва (наприклад "FramesDroppedDueToFilters") */
        └── ETHTOOL_A_STAT_VALUE    /* NLA_U64: Значення лічильника */
```

Група `ETHTOOL_A_STATS_ETH_MAC` містить стандартизовані 64-бітні лічильники `aFramesTransmittedOK`, `aFrameCheckSequenceErrors`, `aAlignmentErrors`, `aOctetsReceivedOK`, що дозволяє моніторинговим системам збирати метрики однакового формату незалежно від вендора мережевої карти.

---

## 5. Валідація атрибутів та правила NLA Політик (`nla_policy`)

Перед передачею даних до відповідних функцій обробки ядро перевіряє кожен NLA-атрибут через глобальний масив правил `struct nla_policy`. Валідатор перевіряє тип даних, мінімальну та максимальну довжину рядків, межі числових діапазонів та правильність прапорців.

```text
/* Приклад опису політики атрибутів заголовка в ядрі Linux */
const struct nla_policy ethnl_header_policy[ETHTOOL_A_HEADER_MAX + 1] = {
    [ETHTOOL_A_HEADER_DEV_INDEX] = { .type = NLA_U32 },
    [ETHTOOL_A_HEADER_DEV_NAME]  = { .type = NLA_NUL_STRING, .len = IFNAMSIZ - 1 },
    [ETHTOOL_A_HEADER_FLAGS]     = { .type = NLA_U32 },
};
```

Якщо користувач надсилає ім'я пристрою, яке перевищує константу `IFNAMSIZ - 1` (15 символів для мережевого інтерфейсу в Linux) або передає атрибут із невірним типом даних, парсер Generic Netlink зупиняє розбірку кадру. При цьому ядро викликає макрос `NL_SET_ERR_MSG_ATTR()`, записуючи в структуру `extack` текстову помилку та зсув атрибута, що не пройшов перевірку.

---

## 6. Протокольні інваріанти: Послідовність (`nlmsg_seq`) та Мультипакетність (`NLM_F_MULTI`)

При обміні повідомленнями через сокети `AF_NETLINK` клієнтський додаток керується двома ключовими протокольними інваріантами:

1. **Ідентифікація запитів через `nlmsg_seq`**: Кожен запит від простору користувача містить монотонно зростаючий порядковий номер `nlmsg_seq` у заголовку `nlmsghdr`. Ядро дублює цей номер у кадрі відповіді. Це дозволяє асинхронному моніторинговому додатові співвідносити відповіді з вихідними запитами навіть тоді, коли кадри відповідей повертаються не в порядку надсилання або перемішуються зі сповіщеннями від multicast-групи.
2. **Багаточастинні відповіді (`NLM_F_MULTI`)**: Якщо додаток виконує масовий запит стану пристроїв (запит `GET` із прапорцем `NLM_F_DUMP`), ядро відправляє серію окремих кадрів. Кожен кадр містить прапорець `NLM_F_MULTI`. Послідовність кадрів завершується службовим повідомленням із типом `NLMSG_DONE`.

---

## 7. Формат відповідей про помилки Extack (`NLMSGERR_ATTR_*`)

Механізм Extended ACK (`extack`) дає можливість ядру повертати вичерпний текстовий контекст відмови та вказувати точне місце помилки в надісланому кадрі NLA.

```text
NLMSGERR_ATTR_MSG       /* NLA_NUL_STRING: Текстове пояснення від драйвера або ядра */
NLMSGERR_ATTR_OFFS      /* NLA_U32: Зсув байта в оригінальному запиті, де знайдено помилку */
NLMSGERR_ATTR_COOKIE    /* NLA_BINARY: Внутрішній кукі-ідентифікатор запиту */
NLMSGERR_ATTR_POLICY    /* Nested: Правила валідації NLA, порушені запитом */
```

Приклад структури розшифрованого розширеного підтвердження у випадку передачі непідтримуваної швидкості:

```text
[NLMSG_ERROR] len=100 type=3 flags=0x0 seq=17 pid=1042
  error: -95 (EOPNOTSUPP - Operation not supported)
  [NLMSGERR_ATTR_MSG] = "Requested speed 1000000 Mbps exceeds PHY capability"
  [NLMSGERR_ATTR_OFFS] = 48 (вказує на атрибут ETHTOOL_A_LINKMODES_SPEED)
```

Коли розробник драйвера мережевої карти викликає у коді ядра `NL_SET_ERR_MSG_ATTR(info->extack, speed_attr, "Requested speed exceeds PHY capability")`, макрос автоматично розраховує зсув `NLMSGERR_ATTR_OFFS` від початку кадру Netlink і записує текстове повідомлення у `NLMSGERR_ATTR_MSG`. Простір користувача отримує повну інформацію для швидкого зневадження без необхідності вивчення виводу `dmesg`.
