# 📋 Інтерфейси та структури USB Core

Цей довідник надає системний опис ключових ядерних структур даних, прапорців конфігурації, функцій реєстрації та механізмів маніпулювання пакетами URB, які надає підсистема `usbcore` для розробників драйверів пристроїв у ядрі Linux.

---

## Ключові структури даних ядерного API

### 1. Опис драйвера пристрою: `struct usb_driver`

Головна структура для опису драйвера USB-інтерфейсу (визначена у `<linux/usb.h>`). Драйвер описує свої можливості, функції реєстрації та обробники подій живлення:

```c
struct usb_driver {
    const char *name;
    int (*probe) (struct usb_interface *intf, const struct usb_device_id *id);
    void (*disconnect) (struct usb_interface *intf);
    int (*unlocked_ioctl) (struct usb_interface *intf, unsigned int code, void *buf);
    int (*suspend) (struct usb_interface *intf, pm_message_t message);
    int (*resume) (struct usb_interface *intf);
    int (*reset_resume) (struct usb_interface *intf);
    const struct usb_device_id *id_table;
    struct usb_dynids dynids;
    struct driver_driver_driver drvwrap;
    unsigned int supports_autosuspend:1;
    unsigned int disable_hub_initiated_lpm:1;
};
```

#### Семантика полів та функцій зворотного виклику

- `name`: Унікальне текстове ім'я драйвера в системній шині `usb`. Відображається в каталозі `/sys/bus/usb/drivers/`.
- `probe()`: Головна функція ініціалізації. Викликається підсистемою `usbcore`, коли виявлено новий пристрій, чий інтерфейс відповідає фільтру з `id_table`.
  - Приймає покажчик на `struct usb_interface` та рядок відповідності `struct usb_device_id`.
  - Повертає `0` при успішній прив'язці або від'ємний код помилки (наприклад, `-ENOMEM` або `-ENODEV`).
- `disconnect()`: Викликається підсистемою `usbcore` при фізичному вилученні пристрою з роз'єму або при вивантаженні модуля ядра.
  - Драйвер повинен зупинити всі активні обробники, скасувати всі відправлені URB за допомогою `usb_kill_anchored_urbs()` або `usb_kill_urb()` та звільнити виділені ресурси.
- `suspend()` та `resume()`: Обробники подій призупинення та відновлення живлення в рамках системного та вибіркового (Runtime PM) управління живленням.
- `reset_resume()`: Викликається у випадку, якщо під час перебування пристрою в стані сну відбувся портовий скид (Port Reset), і внутрішній стан пристрою було повністю скинуто до початкових дескрипторів.
- `id_table`: Покажчик на статичний масив структур `struct usb_device_id`, що визначає списки підтримуваних Vendor/Product ID або класів пристроїв. Масив обов'язково повинен завершуватися порожнім макросом-термінатором.
- `supports_autosuspend`: Бітовий прапорець. Встановлення в `1` сповіщає ядро `usbcore`, що даний драйвер коректно обробляє автопризупинення живлення при бездіяльності.

---

### 2. Таблиця відповідності пристроїв: `struct usb_device_id`

Структура описує правило зіставлення (Matching Rule) між пристроєм на шині та драйвером:

```c
struct usb_device_id {
    __u16 match_flags;
    __u16 idVendor;
    __u16 idProduct;
    __u16 bcdDevice_lo;
    __u16 bcdDevice_hi;
    __u8  bDeviceClass;
    __u8  bDeviceSubClass;
    __u8  bDeviceProtocol;
    __u8  bInterfaceClass;
    __u8  bInterfaceSubClass;
    __u8  bInterfaceProtocol;
    __u8  bInterfaceNumber;
    kernel_ulong_t driver_info;
};
```

#### Вспоміжні макроси заповнення

Для уникнення ручного запонювання прапорців `match_flags` ядро надає стандартні макроси:

- `USB_DEVICE(vendor, product)`: Створює правило для суворого збігу по ідентифікаторах виробника (`idVendor`) та продукту (`idProduct`).
- `USB_DEVICE_VER(vendor, product, lo, hi)`: Додає обмеження по версії прошивки пристрою (`bcdDevice`).
- `USB_INTERFACE_INFO(cl, sc, pr)`: Створює правило збігу по класу (`bInterfaceClass`), підкласу (`bInterfaceSubClass`) та протоколу (`bInterfaceProtocol`) інтерфейсу. Використовується класовими драйверами (наприклад, USB HID або USB Mass Storage).
- `USB_DEVICE_AND_INTERFACE_INFO(vendor, product, cl, sc, pr)`: Поєднує перевірку конкретного вендора та конкретного класового інтерфейсу.

---

### 3. Одиниця обміну даними: `struct urb` (USB Request Block)

Центральна структура даних для виконання будь-яких транзакцій на шині USB:

```c
struct urb {
    struct kref kref;
    void *hcpriv;
    atomic_t use_count;
    atomic_t reject;
    int unlinked;

    struct list_head urb_list;
    struct list_head anchor_list;
    struct usb_anchor *anchor;
    struct usb_device *dev;
    struct usb_host_endpoint *ep;
    unsigned int pipe;
    unsigned int stream_id;
    int status;
    unsigned int transfer_flags;
    void *transfer_buffer;
    dma_addr_t transfer_dma;
    struct scatterlist *sg;
    int num_sgs;
    u32 transfer_buffer_length;
    u32 actual_length;
    unsigned char *setup_packet;
    dma_addr_t setup_dma;
    int start_frame;
    int number_of_packets;
    int interval;
    int error_count;
    void *context;
    usb_complete_t complete;
    struct usb_iso_packet_descriptor iso_frame_desc[];
};
```

#### Важливі поля структури `struct urb`

- `dev`: Покажчик на цільовий пристрій `struct usb_device`, до якого адресовано транзакцію.
- `pipe`: Сформований бітовий канал передачі (тип передачі, номер кінцевої точки, напрямок IN/OUT).
- `status`: Поточний стан виконання транзакції. Заповнюється підсистемою `usbcore` або HCD перед викликом `complete`:
  - `0`: Транзакція завершилася успішно.
  - `-EINPROGRESS`: URB знаходиться в черзі HCD і чекає обробки на шині.
  - `-ENOENT`: URB було асинхронно скасовано через виклик `usb_unlink_urb()`.
  - `-ECONNRESET`: URB було синхронно зупинено через виклик `usb_kill_urb()`.
  - `-ESHUTDOWN`: Хост-контролер зупинено або пристрій відключено від шини.
  - `-EPIPE`: Кінцева точка відповіла сигналом STALL (потрібне скидання стану через `usb_clear_halt()`).
  - `-EOVERFLOW`: Отримано більше даних, ніж розмір буфера `transfer_buffer_length` (Babble error).
  - `-ETIME` / `-EPROTO`: Помилка таймауту або апаратного протоколу на фізичних лініях.
- `transfer_flags`: Бітові прапорці модифікації поведінки URB:
  - `URB_NO_TRANSFER_DMA_MAP`: Сповіщає ядро, що буфер вже відображено у DMA, і його фізична адреса записана у `transfer_dma`.
  - `URB_SHORT_NOT_OK`: Вважати короткий пакет (Short Packet) помилкою передачі.
  - `URB_ISO_ASAP`: Для ізохронних передач — запланувати пакет у найближчий вільний мікрокадр.
  - `URB_ZERO_PACKET`: Автоматично надіслати пакет нульової довжини (Zero-Length Packet, ZLP), якщо розмір передачі кратний `wMaxPacketSize`.
- `transfer_buffer`: Покажчик на віртуальну адресу буфера пам'яті (має бути виділений через `kmalloc` у системній купі).
- `transfer_dma`: Фізична адреса DMA-буфера (якщо використовується пряме відображення).
- `context`: Довільний покажчик на приватні дані драйвера. Передається як аргумент у функцію `complete`.
- `complete`: Функція зворотного виклику, що виконується в контексті `softirq` після завершення обміну.

---

## Основні функції реєстрації та управління драйвером

### Реєстрація та скасування драйвера

```c
int usb_register_driver(struct usb_driver *driver, struct module *owner, const char *mod_name);
void usb_deregister(struct usb_driver *driver);
```

Для макросного спрощення ініціалізації модулів ядра використовується макрос:

```c
module_usb_driver(my_usb_driver);
```

Він автоматично генерує функції `init_module()` та `cleanup_module()`, які реєструють та скасовують драйвер при завантаженні та вивантаженні модуля.

---

## Управління пам'яттю та створення URB

```c
struct urb *usb_alloc_urb(int iso_packets, gfp_t mem_flags);
void usb_free_urb(struct urb *urb);
struct urb *usb_get_urb(struct urb *urb);
```

- `usb_alloc_urb()`: Виділяє пам'ять під структуру `struct urb`. Аргумент `iso_packets` вказує кількість елементів у масиві `iso_frame_desc` (для Bulk, Control та Interrupt передач передається `0`). Аргумент `mem_flags` визначає прапорці розподільника пам'яті (`GFP_KERNEL` або `GFP_ATOMIC`).
- `usb_free_urb()`: Зменшує лічильник посилань на URB. Коли лічильник досягає нуля, пам'ять під URB звільняється.
- `usb_get_urb()`: Збільшує лічильник посилань на об'єкт URB.

---

## Функції ініціалізації (Helper Functions)

Перед відправленням URB у ядро його полях слід правильно заповнити. Для цього використовуються стаціонарні inline-функції:

```c
static inline void usb_fill_control_urb(
    struct urb *urb,
    struct usb_device *dev,
    unsigned int pipe,
    unsigned char *setup_packet,
    void *transfer_buffer,
    int buffer_length,
    usb_complete_t complete_fn,
    void *context
);

static inline void usb_fill_bulk_urb(
    struct urb *urb,
    struct usb_device *dev,
    unsigned int pipe,
    void *transfer_buffer,
    int buffer_length,
    usb_complete_t complete_fn,
    void *context
);

static inline void usb_fill_int_urb(
    struct urb *urb,
    struct usb_device *dev,
    unsigned int pipe,
    void *transfer_buffer,
    int buffer_length,
    usb_complete_t complete_fn,
    void *context,
    int interval
);
```

- `interval`: Інтервал опитування для переривальних (Interrupt) передач. Задається у кадрах (1 мс для Low/Full Speed) або мікрокадрах ($2^{interval-1} \times 125$ мкс для High/SuperSpeed).

---

## Відправка та скасування транзакцій

### 1. Асинхронне відправлення (`usb_submit_urb`)

```c
int usb_submit_urb(struct urb *urb, gfp_t mem_flags);
```

Передає URB до підсистеми `usbcore` та драйвера HCD.
- Виклик є **атомарним** і не блокує потік виконання.
- Аргумент `mem_flags`:
  - `GFP_ATOMIC`: Обов'язковий, якщо виклик виконується у функціях callback завершення URB, обробниках переривань або під утриманням spinlock.
  - `GFP_KERNEL`: Використовується у звичайному контексті процесів.
  - `GFP_NOIO`: Використовується у драйверах підсистеми збереження даних, щоб запобігти рекурсивному виклику операцій дискового I/O при виділенні сторінок пам'яті.

### 2. Скасування та зупинка URB

```c
int usb_unlink_urb(struct urb *urb);
void usb_kill_urb(struct urb *urb);
```

- `usb_unlink_urb()`: Асинхронно ініціює вилучення URB з апаратної черги HCD. Повертає керування негайно зі статусом `-EINPROGRESS`. Функцію `complete` буде викликано пізніше зі статусом `urb->status = -ENOENT`. Може безпечно викликатися в атомарному контексті.
- `usb_kill_urb()`: Синхронно очікує повного вилучення URB з апаратури та завершення роботи його callback. Гарантує, що після повернення з функції callback більше не виконується. **Заборонено викликати в атомарному контексті чи перериванні!**

---

## Механізм錨ування пакетами: `struct usb_anchor`

При обробці десятків паралельних асинхронних URB драйверу складно відстежувати їх життєвий цикл вручну при відключенні пристрою. Для цього ядро надає абстракцію **Anchor (Якір)**:

```c
void init_usb_anchor(struct usb_anchor *anchor);
void usb_anchor_urb(struct urb *urb, struct usb_anchor *anchor);
void usb_unanchor_urb(struct urb *urb);
void usb_kill_anchored_urbs(struct usb_anchor *anchor);
void usb_scuttle_anchored_urbs(struct usb_anchor *anchor);
int usb_wait_for_anchored_urbs(struct usb_anchor *anchor, int timeout);
```

### Принцип роботи якоря

1. Драйвер створює об'єкт `struct usb_anchor`.
2. Перед відправкою `usb_submit_urb()` драйвер додає URB до якоря за допомогою `usb_anchor_urb(urb, anchor)`.
3. Якщо пристрій відключається, драйвер викликає одну функцію `usb_kill_anchored_urbs(anchor)`, яка автоматично примусово скасовує та очікує завершення всіх прив'язаних URB.

---

## Синхронні блокуючі функції обміну

Для простих ініціалізаційних операцій `usbcore` надає виклики, які занурюють потік у сон до завершення обміну:

```c
int usb_control_msg(
    struct usb_device *dev,
    unsigned int pipe,
    __u8 request,
    __u8 requesttype,
    __u16 value,
    __u16 index,
    void *data,
    __u16 size,
    int timeout
);

int usb_bulk_msg(
    struct usb_device *dev,
    unsigned int pipe,
    void *data,
    int len,
    int *actual_length,
    int timeout
);

int usb_interrupt_msg(
    struct usb_device *dev,
    unsigned int pipe,
    void *data,
    int len,
    int *actual_length,
    int timeout
);
```

- `timeout`: Максимальний час очікування у мілісекундах (передайте `0` для нескінченного очікування).
- Повертають `0` або кількість переданих байтів при успіху, або від'ємний код помилки (наприклад, `-ETIMEDOUT`).

---

## Відновлення помилок та скидання пристрою

Якщо кінцева точка пристрою перейшла у стан помилки (STALL) або пристрій перестав відповідати на транзакції, `usbcore` надає функції відновлення:

```c
int usb_clear_halt(struct usb_device *dev, int pipe);
int usb_reset_device(struct usb_device *dev);
```

- `usb_clear_halt()`: Надсилає пристрою контрольний запит `CLEAR_FEATURE (ENDPOINT_HALT)` і скидає внутрішній стан послідовності тогла (Data Toggle Bit) каналу в ядрі та HCD.
- `usb_reset_device()`: Виконує повторне портове скидання (Port Reset) та реініціалізацію конфігурації пристрою без від'єднання драйвера.
