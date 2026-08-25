# 📋 Інтерфейс Netlink та внутрішні структури WireGuard

Керування мережевим пристроєм WireGuard у ядрі Linux здійснюється через підсистему Generic Netlink (`NETLINK_GENERIC`). Цей API замінює застарілі системні виклики `ioctl` та забезпечує атомарне зчитування й оновлення конфігурації пірів, публічних ключів, портів слухання та криптографічних параметрів без зупинки мережевого трафіку.

Для забезпечення високої швидкості обробки пакета та підтримки паралелізму без блокувань (lock-free), модуль ядра WireGuard (`drivers/net/wireguard/`) покладається на чітко розроблену систему внутрішніх структур даних C, опис яких наведено нижче.

---

## 1. Внутрішні структури ядра Linux (`drivers/net/wireguard/`)

Усередині ядра Linux стан тунельного пристрою та прив'язаних до нього вузлів описується чотирма ключовими структурами C.

### 1.1. Пристрій: `struct wg_device`

Головний контейнер пристрою, який розширює стандартний `struct net_device` ядра.

```c
struct wg_device {
    struct net_device *dev;
    struct crypt_queue encrypt_queue;
    struct crypt_queue decrypt_queue;
    struct sock __rcu *sock4;
    struct sock __rcu *sock6;
    struct noise_static_identity static_identity;
    struct allowedips allowedips;
    struct mutex device_update_lock;
    struct list_head peer_list;
    atomic_t device_update_gen;
    u32 incoming_port;
    u32 fwmark;
};
```

Поля структури `struct wg_device` мають наступне призначення:

- `dev` — вказівник на екземпляр базової структури ядра `struct net_device`, який реєструє пристрій у системному списку мережевих адаптерів ОС.
- `encrypt_queue` — паралельна черга `padata`, що керує паралельним шифруванням вихідних пакетів на багатьох ядрах CPU.
- `decrypt_queue` — паралельна черга `padata`, що керує дешифрацією та перевіркою вхідних пакетів.
- `sock4` / `sock6` — RCU-захищені вказівники на сокети ядра `struct sock`, відкриті для прийому та відправки UDP-дейтаграм через простір адрес IPv4 та IPv6.
- `static_identity` — криптографічна ідентичність пристрою, що містить приватний та публічний ключі Curve25519. Для запобігання плутанині слід чітко розмежовувати розміри об'єктів: публічний ключ Curve25519 має розмір 32 байти, тоді як повний пакет ініціалізації рукостискання Noise_IK (`WG_MSG_INITIATION`) має довжину 148 байтів (разом із заголовком, ефемерним ключем, зашифрованим статичним ключем і тегами Poly1305).
- `allowedips` — корінь префіксного дерева (Radix Trie) для виконання пошуку піра за адресою призначення пакета (LPM — Longest Prefix Match).
- `device_update_lock` — м'ютекс для взаємного виключення паралельних конфігураційних операцій Netlink.
- `peer_list` — двозв'язний список усіх зконфігурованих пірів даного тунельного інтерфейсу.
- `device_update_gen` — атомарний лічильник поколінь конфігурації для виявлення паралельних змін.
- `incoming_port` — локальний UDP-порт, на якому пристрій слухає вхідний тунельний трафік (за замовчуванням 51820).
- `fwmark` — сокетна мітка файєрволу, що присвоюється вихідним UDP-пакетам ядра для коректної обробки у таблицях `iptables` / `nftables`.

### 1.2. Вузол (Пір): `struct wg_peer`

Описує віддалений вузол тунелю, його ефемерні ключі, лічильники та статус.

```c
struct wg_peer {
    struct wg_device *wg;
    struct noise_handshake handshake;
    struct noise_keypair __rcu *keypairs;
    struct endpoint endpoint;
    struct allowedips_node node;
    u64 rx_bytes, tx_bytes;
    struct timer_list timer_rekey_retry;
    struct timer_list timer_new_handshake;
    struct timer_list timer_zero_keymaterial;
    struct timer_list timer_persistent_keepalive;
    u16 persistent_keepalive_interval;
    bool timer_need_another_keepalive;
};
```

Поля структури `struct wg_peer`:

- `wg` — вказівник на батьківський пристрій `struct wg_device`.
- `handshake` — об'єкт стану рукостискання Noise IK, що містить тимчасові ефемерні ключі, контекстні хеші та таймштампи TAI64N.
- `keypairs` — RCU-захищений масив поточних сесійних ключів ChaCha20-Poly1305 (поточний ключ, попередній ключ і наступний завантажуваний ключ).
- `endpoint` — структура, що зберігає поточну зовнішню IP-адресу та UDP-порт віддаленого піра в мережі Інтернет.
- `rx_bytes` / `tx_bytes` — 64-бітні атомарні лічильники обсягу переданих та отриманих байтів трафіку.
- `timer_rekey_retry` — таймер повторного надсилання пакетів ініціації рукостискання при втраті відповідей.
- `timer_new_handshake` — таймер регулярного оновлення ключів після закінчення 120 секунд активності (`REKEY_AFTER_TIME`).
- `timer_zero_keymaterial` — таймер безпеки, що зануляє та вилучає сесійні ключі з пам'яті через 180 секунд (`REJECT_AFTER_TIME`).
- `timer_persistent_keepalive` — таймер періодичного надсилання порожніх підтримувальних пакетів (Keepalive) для підтримки відкритих трансляцій у NAT-роутерах.
- `persistent_keepalive_interval` — інтервал відправки Keepalive-пакетів у секундах (0 — вимкнено).

### 1.3. Префіксне дерево маршрутизації: `struct allowedips` та `struct allowedips_node`

Структури префіксного дерева, що реалізують алгоритм Longest Prefix Match (LPM) для прив'язки підмереж IP до відповідного `struct wg_peer`.

```c
struct allowedips_node {
    struct wg_peer __rcu *peer;
    struct allowedips_node __rcu *bit[2];
    u8 cidr;
    u8 bit_at;
    u8 ip[16];
};

struct allowedips {
    struct allowedips_node __rcu *root4;
    struct allowedips_node __rcu *root6;
    struct mutex mutex;
};
```

Детальний функціонал полів:

- `root4` / `root6` — RCU-захищені вказівники на кореневі вузли бінарного префіксного дерева для адрес IPv4 та IPv6.
- `bit[2]` — масив двох вказівників на дочірні вузли дерева (`bit[0]` для нульового біта адреси, `bit[1]` для одиничного біта).
- `cidr` — довжина мережевої маски префікса (наприклад, 24 для `192.168.1.0/24` або 32 для `/32`).
- `bit_at` — номер біта IP-адреси, який перевіряється у даному вузлі дерева під час спуску.
- `peer` — RCU-посилання на піра, якому належить даний IP-префікс.

### 1.4. Криптографічний стан рукостискання: `struct noise_handshake`

Зберігає проміжні ключі та контексний стан під час виконання рукостискання Noise IK:

```c
struct noise_handshake {
    struct noise_static_identity *static_identity;
    u8 prk[NOISE_HASH_LEN];
    u8 hash[NOISE_HASH_LEN];
    u8 chaining_key[NOISE_HASH_LEN];
    u8 remote_static[NOISE_PUBLIC_KEY_LEN];
    u8 remote_ephemeral[NOISE_PUBLIC_KEY_LEN];
    u8 ephemeral_private[NOISE_PUBLIC_KEY_LEN];
    u8 remote_preshared_key[NOISE_SYMMETRIC_KEY_LEN];
    enum handshake_state state;
    u32 local_index;
    u32 remote_index;
    u64 last_sent_handshake;
};
```

---

## 2. Специфікація Generic Netlink Protocol (`WG_GENL_NAME`)

WireGuard реєструється в підсистемі Generic Netlink як сімейство з ім'ям `"wireguard"` (`WG_GENL_NAME`) та версією `1` (`WG_GENL_VERSION`).

### 2.1. Команди протоколу (`enum wg_cmd`)

| Команда | Значення | Напрямок | Опис та семантика виконання |
| :--- | :--- | :--- | :--- |
| `WG_CMD_GET_DEVICE` | `1` | User -> Kernel / Kernel -> User | Запит стану пристрою. У відповідь ядро повертає дамп атрибутів пристрою, його публічний ключ, порт слухання та повний список пірів із лічильниками трафіку й часом останнього рукостискання. |
| `WG_CMD_SET_DEVICE` | `2` | User -> Kernel | Атомарна зміна або заміна налаштувань тунельного пристрою та його пірів без скидання активного з'єднання. |

### 2.2. Дерево атрибутів пристрою (`enum wgdevice_attribute`)

Нижче наведено повну ієрархічну структуру атрибутів Netlink, що передаються у повідомленнях:

```
[NLMSGHDR] Header (nlmsg_len, nlmsg_type, nlmsg_flags, nlmsg_seq, nlmsg_pid)
  └── [GENLMSGHDR] Generic Netlink Header (cmd = WG_CMD_SET_DEVICE, version = 1)
        ├── WGDEVICE_A_IFINDEX (U32) — системний індекс мережевого інтерфейсу (наприклад, 4)
        ├── WGDEVICE_A_IFNAME (STRING) — альтернативна назва інтерфейсу (наприклад, "wg0")
        ├── WGDEVICE_A_PRIVATE_KEY (BINARY, 32B) — новий приватний ключ Curve25519
        ├── WGDEVICE_A_PUBLIC_KEY (BINARY, 32B) — відповідний публічний ключ Curve25519
        ├── WGDEVICE_A_LISTEN_PORT (U16) — новий порт слухання UDP (наприклад, 51820)
        ├── WGDEVICE_A_FWMARK (U32) — мітка файєрволу для вихідних пакетів ядра
        ├── WGDEVICE_A_FLAGS (U32) — прапорці пристрою (WGDEVICE_F_REPLACE_PEERS)
        └── WGDEVICE_A_PEERS (NESTED) — вкладений список пірів
              └── [PEER_ENTRY] (NESTED)
                    ├── WGPEER_A_PUBLIC_KEY (BINARY, 32B) — публічний ключ піра (обов'язковий ID)
                    ├── WGPEER_A_PRESHARED_KEY (BINARY, 32B) — додатковий симетричний PSK-ключ
                    ├── WGPEER_A_ENDPOINT (SOCKADDR_IN / SOCKADDR_IN6) — зовнішній IP:Port
                    ├── WGPEER_A_PERSISTENT_KEEPALIVE_INTERVAL (U16) — інтервал Keepalive у секундах
                    ├── WGPEER_A_FLAGS (U32) — прапорці (WGPEER_F_REMOVE_ME | WGPEER_F_REPLACE_ALLOWEDIPS)
                    ├── WGPEER_A_RX_BYTES (U64) — атомарний лічильник отриманих байтів (тільки GET)
                    ├── WGPEER_A_TX_BYTES (U64) — атомарний лічильник переданих байтів (тільки GET)
                    ├── WGPEER_A_LAST_HANDSHAKE_TIME (STRUCT TIMESPEC) — час останнього рукостискання (тільки GET)
                    └── WGPEER_A_ALLOWEDIPS (NESTED) — список підмереж
                          └── [ALLOWEDIP_ENTRY] (NESTED)
                                ├── WGALLOWEDIP_A_FAMILY (U16) — сімейство адрес (AF_INET або AF_INET6)
                                ├── WGALLOWEDIP_A_IPADDR (BINARY, 4B або 16B) — IP-адреса підмережі
                                └── WGALLOWEDIP_A_CIDR_MASK (U8) — маска префікса (наприклад, 24 або 32)
```

### 2.3. Докладний аналіз типів та валідації атрибутів

Під час обробки виклику `WG_CMD_SET_DEVICE` ядро реалізує сувору перевірку типів і довжин атрибутів за допомогою вбудованої матриці валідації `nla_policy`:

- `WGDEVICE_A_IFINDEX` (тип `NLA_U32`): 32-бітне ціле число, що вказує унікальний системний номер адаптера у таблиці `net_device`.
- `WGDEVICE_A_IFNAME` (тип `NLA_NUL_STRING`, макс. довжина `IFNAMSIZ` = 16 байт): Рядок з замикаючим нульовим байтом, що містить назву тунелю (наприклад, `"wg0"` або `"wg-corporate"`).
- `WGDEVICE_A_PRIVATE_KEY` (тип `NLA_EXACT_LEN`, довжина строго 32 байти): Сирий бінарний масив 256-бітного приватного ключа Curve25519. При його зміні ядро автоматично перераховує відповідний публічний ключ та перезапускає стан ідентичності `static_identity`.
- `WGDEVICE_A_PUBLIC_KEY` (тип `NLA_EXACT_LEN`, довжина строго 32 байти): Публічний ключ Curve25519. Використовується при GET-запитах для зчитування поточного публічного ключа тунельного пристрою.
- `WGPEER_A_PUBLIC_KEY` (тип `NLA_EXACT_LEN`, довжина строго 32 байти): Унікальний ідентифікатор піра. Слугує головним первинним ключем для пошуку у хеш-таблиці пірів пристрою. Якщо пір з таким ключем відсутній у пам'яті ядра, ядро динамічно виділяє пам'ять через `kzalloc()` і реєструє нового піра.
- `WGPEER_A_PRESHARED_KEY` (тип `NLA_EXACT_LEN`, довжина 32 байти): Додатковий симетричний ключ для захисту від потенційних майбутніх квантових атак. При його наявності він підмішується у фінальний ланцюговий ключ HKDF під час рукостискання.
- `WGPEER_A_ENDPOINT` (тип `NLA_MIN_LEN`): Бінарна структура сокетної адреси `struct sockaddr_in` (16 байт для IPv4) або `struct sockaddr_in6` (28 байт для IPv6). Ядро перевіряє відповідність поля `sa_family` та валідує IP-адресу призначення.

### 2.4. Семантика прапорців (Flags)

- `WGDEVICE_F_REPLACE_PEERS` (`1 << 0`): Повністю видалити з ядра усіх наявних пірів пристрою перед додаванням нових пірів із вкладеного атрибута `WGDEVICE_A_PEERS`. Якщо прапорець не встановлено, нові піри об'єднуються з наявними.
- `WGPEER_F_REMOVE_ME` (`1 << 0`): Видалити конкретного піра з внутрішніх таблиць ядра.
- `WGPEER_F_REPLACE_ALLOWEDIPS` (`1 << 1`): Очистити наявний список `allowed-ips` даного піра перед додаванням нових IP-префіксів з атрибута `WGPEER_A_ALLOWEDIPS`.

---

## 3. Модель синхронізації та захист пам'яті в ядрі (RCU і Mutex)

Паралельні конфігураційні запити Netlink та обробка високонавантаженого мережевого трафіку вимагають ретельно розробленої схеми синхронізації в ядрі Linux.

### 3.1. Розмежування запису та читання

Зміна конфігурації пристрою викликом `WG_CMD_SET_DEVICE` виконується у контексті процесів під захистом м'ютексу `wg->device_update_lock`. Це запобігає стану змагання (race conditions), коли два користувацькі процеси одночасно намагаються оновити список пірів або змінити приватний ключ.

Однак вихідний трафік у `wg_xmit()` та вхідний трафік у `wg_receive()` обробляються у контексті переривань (softirq) і взагалі не беруть м'ютекс `device_update_lock`. Замість цього читання списку пірів `peer_list` та пошук у префіксному дереві `allowedips` захищені критичними секціями RCU (`rcu_read_lock()` та `rcu_read_unlock()`).

### 3.2. Безпечне видалення пірів через RCU

Коли демон користувача надсилає прапорець `WGPEER_F_REMOVE_ME`, ядро виконує наступну послідовність дій:

1. Захоплює м'ютекс `wg->device_update_lock`.
2. Вилучає вказівники на піра з бінарного префіксного дерева `allowedips` та зі списку `peer_list` за допомогою RCU-функцій `rcu_assign_pointer()`.
3. Звільняє м'ютекс `device_update_lock`.
4. Викликає `call_rcu()`, яка відкладає фактичне звільнення пам'яті `kfree(peer)` до завершення поточного періоду грації (grace period) RCU.

Це повністю гарантує, що жодне паралельне ядро CPU, яке у цей самий момент виконувало дешифрацію пакета для даного піра, не отримає помилки звернення до звільненої пам'яті (use-after-free).

---

## 4. Коди помилок системного виклику Netlink

При виконанні викликів `WG_CMD_SET_DEVICE` ядро проводити жорстку валідацію вхідних атрибутів і у випадку помилки повертає стандартні коди errno у заголовок Netlink ACK (`NLMSG_ERROR`):

- `EINVAL` — недійсний розмір ключа (наприклад, розмір наданого приватного ключа не становить точно 32 байти) або некоректна маска CIDR (понад 32 для IPv4 або понад 128 для IPv6).
- `ENODEV` — мережевий пристрій із вказаним `WGDEVICE_A_IFINDEX` або `WGDEVICE_A_IFNAME` не існує у ядрі.
- `EKEYREJECTED` — наданий публічний ключ є криптографічно недійсним або належить до точок малої хронологічної порядку еліптичної кривої Curve25519.
- `EADDRINUSE` — вказаний `WGDEVICE_A_LISTEN_PORT` вже зайнятий іншим сокетом у системі.
- `ENOMEM` — у ядрі недостатньо вільної оперативної пам'яті для виділення нових вузлів префіксного дерева `allowedips_node`.
- `EPERM` — процес користувача не володіє мережевим привілеєм `CAP_NET_ADMIN` у поточному мережевому просторі імен (netns).
