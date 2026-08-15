# 📋 Інтерфейси ядерних структур та sysfs фреймворку USB Type-C

Підсистема ядра Linux USB Type-C Connector Class реалізує чіткий бінарний та програмний контракт між низькорівневими драйверами контролерів портів (TCPM, UCSI, TPS6598x) та простором користувача через систему sysfs. Драйвери роз'ємів реєструють порти за допомогою відповідних ядерних функцій API, після чого ядро автоматично будує деревну структуру атрибутів у файловій системі sysfs для динамічного моніторингу та управління.

## Ядерні структури даних (`include/linux/usb/typec.h`)

Для опису фізичного порту та його апаратних можливостей низькорівневий драйвер контролера заповнює структуру `struct typec_capability`. Ця структура передається підсистемі ядра під час ініціалізації порту:

```c
/* Скорочено за заголовком ядра include/linux/usb/typec.h */
struct typec_capability {
    enum typec_port_type    type;           /* TYPEC_PORT_SRC, TYPEC_PORT_SNK, TYPEC_PORT_DRP */
    enum typec_port_data    data;           /* TYPEC_PORT_DFP, TYPEC_PORT_UFP, TYPEC_PORT_DRD */
    u16                     revision;       /* Версія специфікації Type-C у BCD: 0x0130 = 1.3 */
    u16                     pd_revision;    /* Версія специфікації USB PD у BCD: 0x0300 = 3.0 */

    const struct typec_operations *ops;     /* Покажчик на функції зворотного виклику (callback ops) */
    
    struct fwnode_handle   *fwnode;         /* Зв'язок із вузлом Device Tree або ACPI */
    void                   *driver_data;    /* Приватні дані драйвера контролера */

    int                     prefer_role;    /* Бажана роль при підключенні: Try.SRC / Try.SNK */
};
```

Детальне призначення полів структури `struct typec_capability`:
- `type`: Визначає базовий електричний режим живлення порту. Значення `TYPEC_PORT_SRC` вказує, що порт може виступати лише джерелом живлення; `TYPEC_PORT_SNK` — лише споживачем; `TYPEC_PORT_DRP` — дворольовий порт (Dual-Role Power), здатний динамічно змінювати роль.
- `data`: Визначає підтримку передачі даних. Значення `TYPEC_PORT_DFP` вказує на режим Downstream Facing Port (USB Host); `TYPEC_PORT_UFP` — Upstream Facing Port (USB Device); `TYPEC_PORT_DRD` — Dual-Role Data порт.
- `ops`: Покажчик на таблицю функцій керування `struct typec_operations`. Якщо користувач записує нове значення у sysfs-атрибут `data_role` чи `power_role`, ядро викликає відповідний функціональний покажчик із цієї структури.

Структура операцій зворотного виклику `struct typec_operations`:

```c
/* Скорочено за заголовком ядра include/linux/usb/typec.h */
struct typec_operations {
    int (*try_role)(struct typec_port *port, int role);
    int (*dr_set)(struct typec_port *port, enum typec_data_role role);
    int (*pr_set)(struct typec_port *port, enum typec_power_role role);
    int (*vconn_set)(struct typec_port *port, enum typec_role role);
    int (*port_type_set)(struct typec_port *port, enum typec_port_type type);
};
```

Опис операцій зворотного виклику:
- `dr_set`: Викликається підсистемою ядра при спробі змінити роль даних (Data Role Swap). Драйвер контролера надсилає пакет `DR_Swap` через лінію CC і повертає `0` при успіху або від'ємний код помилки (`-EOPNOTSUPP`, `-ETIMEDOUT`).
- `pr_set`: Викликається для виконання Power Role Swap (переключення між `source` та `sink`).
- `vconn_set`: Запитує переключення джерела живлення для e-Marker чипа кабелю (VCONN Swap).
- `port_type_set`: Змінює поточний робочий режим DRP-порту (наприклад, примусово обмежує DRP-порт лише режимом `sink`).

## Функції реєстрації та управління об'єктами ядра

Підсистема ядра експортує наступні головні функції для використання у драйверах портів (`drivers/usb/typec/core.c`):

- `struct typec_port *typec_register_port(struct device *parent, const struct typec_capability *cap)`
  Реєструє новий фізичний порт у системі, створює структуру `/sys/class/typec/portX/` та повертає непрозорий покажчик `struct typec_port *`.

- `void typec_unregister_port(struct typec_port *port)`
  Вилучає порт із системи при розвантаженні драйвера.

- `struct typec_partner *typec_register_partner(struct typec_port *port, struct typec_partner_desc *desc)`
  Викликається менеджером порту (TCPM чи UCSI), коли на лініях CC виявлено підключення партнера. Створює піддиректорію `/sys/class/typec/portX-partner/`.

- `void typec_unregister_partner(struct typec_partner *partner)`
  Викликається при фізичному від'єднанні кабелю або втраті сигналу CC.

- `void typec_set_data_role(struct typec_port *port, enum typec_data_role role)`
  Оновлює внутрішній стан ролі даних порту у пам'яті ядра та сповіщає простір користувача через події `kobject_uevent`.

- `void typec_set_pwr_role(struct typec_port *port, enum typec_power_role role)`
  Оновлює відображення активної ролі живлення.

## Докладний довідник sysfs-атрибутів `/sys/class/typec/`

При реєстрації порту фреймворк автоматично створює в sysfs прозору об'єктну структуру. Нижче наведено детальний опис усіх експортованих атрибутів.

### Атрибути порту `/sys/class/typec/portX/`

1. `data_role` (доступ: `read / write`)
   - **Опис:** Поточна активна роль даних порту.
   - **Значення:** `host` (порт виступає USB DFP хостом), `device` (порт виступає USB UFP периферією).
   - **Поведінка запису:** Запис значення `host` або `device` активує процедуру Data Role Swap. Якщо запис успішний, ядро повертає кількість записаних байтів, а файл оновлює вміст. При відмові партнера запис повертає помилку `EOPNOTSUPP`.

2. `power_role` (доступ: `read / write`)
   - **Опис:** Поточна активна роль живлення порту.
   - **Значення:** `source` (порт виступає джерелом напруги VBUS), `sink` (порт споживає напругу від зовнішнього джерела).
   - **Поведінка запису:** Запис значення викликає процедуру Power Role Swap (`pr_set`).

3. `vconn_role` (доступ: `read / write`)
   - **Опис:** Поточний стан постачальника живлення VCONN для активних кабелів e-Marker.
   - **Значення:** `source` (порт живить мікросхему кабелю), `sink` (кабель живиться від протилежного пристрою).

4. `port_type` (доступ: `read / write`)
   - **Опис:** Конфігурація робочого режиму порту.
   - **Значення:** `source` (фіксоване джерело), `sink` (фіксований споживач), `dual` (дворольовий режим DRP).
   - **Застосування:** Дозволяє системному менеджеру живлення примусово вимкнути видачу струму на порт для економії батареї ноутбука.

5. `preferred_role` (доступ: `read / write`)
   - **Опис:** Переважна роль при початковому узгодженні згідно зі специфікацією Type-C.
   - **Значення:** `none`, `source` (алгоритм Try.SRC — порт намагається стати джерелом), `sink` (алгоритм Try.SNK — порт намагається стати споживачем).

6. `usb_power_delivery_revision` (доступ: `read-only`)
   - **Опис:** Підтримувана версія специфікації Power Delivery (наприклад, `2.0`, `3.0`, `3.1`).

7. `usb_typec_revision` (доступ: `read-only`)
   - **Опис:** Версія апаратної специфікації роз'єму Type-C (наприклад, `1.3`, `2.0`, `2.1`).

### Атрибути підключеного партнера `/sys/class/typec/portX-partner/`

Коли пристрій підключається до порту, у каталозі `portX` з'являється дочірній об'єкт `portX-partner`:

1. `supports_usb_power_delivery` (доступ: `read-only`)
   - **Значення:** `yes` або `no`. Вказує, чи підключений пристрій підтримує цифровий протокол узгодження Power Delivery BMC.

2. `accessory_mode` (доступ: `read-only`)
   - **Значення:** `none`, `analog_audio` (підключено аналоговий аудіо-адаптер 3.5мм), `debug` (підключено налагоджувальний пристрій).

3. `identity/id_header` (доступ: `read-only`)
   - **Опис:** 32-бітне значення заголовка VDM (Vendor Defined Message), зчитаного з партнера. Містить тип пристрою та USB Vendor ID.

4. `identity/product` (доступ: `read-only`)
   - **Опис:** 32-бітний Product VDO; у старших 16 бітах — USB Product ID (PID) підключеного обладнання.

5. `identity/cert_stat` (доступ: `read-only`)
   - **Опис:** Сертифікаційний ідентифікатор XID, присвоєний консорціумом USB-IF.

### Атрибути альтернативних режимів `/sys/class/typec/portX-partner.Y/`

Кожен оголошений партнером альтернативний режим створює піддиректорію вигляду `portX-partner.0`, `portX-partner.1`:

1. `svid` (доступ: `read-only`)
   - **Опис:** 16-бітний шістнадцятковий ідентифікатор стандарту (Standard / Vendor ID).
   - **Приклади:** `ff01` (DisplayPort, SVID VESA), `8087` (Thunderbolt 3 / USB4, SVID Intel).

2. `mode` (доступ: `read-only`)
   - **Опис:** Внутрішній індекс режиму, визначений специфікацією даного SVID (наприклад, `1` для стандартного DisplayPort).

3. `vdo` (доступ: `read-only`)
   - **Опис:** 32-бітне значення Vendor Defined Object, яке містить конфігураційні біти режиму (наприклад, розклад диференційних ліній DisplayPort: 2 лінії DP + USB 3.2 або 4 лінії DP).

4. `active` (доступ: `read / write`)
   - **Значення:** `yes` (режим активовано) або `no` (режим неактивний).
   - **Поведінка запису:** Запис значення `yes` надсилає партнеру VDM-команду `Enter Mode`, примусово активуючи альтернативний режим через крос-мультиплексор.

## Довідник підсистеми Power Delivery `/sys/class/usb_power_delivery/`

У сучасних ядрах Linux (починаючи з версії 6.0) узгоджені профілі живлення відображаються у виокремленій системній ієрархії `/sys/class/usb_power_delivery/pdX/`:

- `pdX/revision`: Версія протоколу PD активного з'єднання (`2.0`, `3.0`, `3.1`).
- `pdX/source-capabilities/`: Директорія із файлами `1:fixed`, `2:fixed`, `3:pps`, які описують профілі напруги та струму, оголошені джерелом:
  - `voltage`: Напруга профілю у мілівольтах (наприклад, `20000` для 20 В).
  - `maximum_current`: Максимальний струм у міліамперах (наприклад, `3250` для 3.25 А).
- `pdX/sink-capabilities/`: Директорія із профілями PDO, які споживач здатен прийняти.
- Пара директорій разом дає повну картину: що джерело пропонує і що споживач готовий прийняти. Який саме профіль урешті обрано, видно за поточною напругою й струмом у відповідному об'єкті класу `power_supply`.
