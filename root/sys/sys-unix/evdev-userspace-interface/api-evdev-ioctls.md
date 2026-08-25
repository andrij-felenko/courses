# 📋 Інтерфейс викликів ioctls підсистеми evdev та uinput

Цей довідник описує повний набір системних викликів `ioctl`, структур даних, макросів кодування команд та прапорців підсистеми `evdev` (`<linux/input.h>`) та модуля `uinput` (`<linux/uinput.h>`). Інтерфейс призначений для запиту системних властивостей пристроїв введення, читання бітових масок можливостей, налаштування зворотного зв'язку (Force Feedback) та створення віртуальних пристроїв у просторі користувача.

---

## 1. Механізми кодування та обробки ioctl у ядрі Linux

Усі системні виклики `ioctl` для пристроїв `/dev/input/eventX` дотримуються загальної схеми кодування макросів ядра Linux, визначеної у заголовному файлі `<asm-generic/ioctl.h>`. Системний виклик `ioctl(fd, request, arg)` упаковує метадані виклику в 32-бітове ціле число `request`.

### 1.1. Структура 32-бітового коду команди ioctl

Код команди `ioctl` розбитий на чотири бітові поля:

1. **`_IOC_DIR` (біти 30–31):** Напрямок передачі даних з точки зору простору користувача:
   - `_IOC_NONE` (`0x0`): Передача даних відсутня (команда є сигналом або вимикачем).
   - `_IOC_WRITE` (`0x1`): Простір користувача записує дані в ядро.
   - `_IOC_READ` (`0x2`): Ядро записує дані в простір користувача.
   - `_IOC_READ | _IOC_WRITE` (`0x3`): Двосторонній обмін даними.
2. **`_IOC_SIZE` (біти 16–29):** Розмір аргументу в байтах, обчислений через `sizeof(type)`. Ядро використовує цей розмір для автоматичної перевірки прав доступу до сторінок пам'яті (`access_ok()`).
3. **`_IOC_TYPE` (біти 8–15):** 8-бітовий магічний номер (magic number) підсистеми. Для підсистеми `evdev` це завжди символ `'E'` (`0x45`). Для модуля `uinput` магічним номером є символ `'U'` (`0x55`).
4. **`_IOC_NR` (біти 0–7):** Порядковий номер конкретної команди всередині даної підсистеми (наприклад, `0x01` для `EVIOCGVERSION`, `0x02` для `EVIOCGID`).

Стандартні допоміжні макроси кодують нові команди за такою схемою:
- `_IOR(type, nr, datatype)` — створює код для зчитування структури `datatype` з ядра.
- `_IOW(type, nr, datatype)` — створює код для запису структури `datatype` в ядро.
- `_IOC(dir, type, nr, size)` — створює код із довільними розмірами та напрямком.

### 1.2. Обробка ioctl у ядрі (`evdev_do_ioctl`)

Коли програма викликає `ioctl(fd, EVIOC..., arg)`, ядро Linux передає керування функції `evdev_do_ioctl()` в обробнику `drivers/input/evdev.c`. 

Схема диспетчеризації працює за наступними кроками:

1. **Перевірка стану пристрою:** Ядро перевіряє, чи пристрій не було фізично від'єднано (`client->evdev->exist`). Якщо пристрій видалено з системи, будь-який виклик повертає помилку `-ENODEV`.
2. **Перевірка прав та адреси пам'яті:** За допомогою функцій `copy_from_user()` та `copy_to_user()` ядро безпечно копіює дані між адресовим простором ядра та простором користувача.
3. **Обробка динамічного розміру `_IOC_SIZE`:** Для команд зчитування бітових масок та рядків (таких як `EVIOCGBIT` або `EVIOCGNAME`) довжина виділеного буфера обчислюється безпосередньо з коду команди за допомогою макросу `_IOC_SIZE(cmd)`. Якщо виділений буфер у просторі користувача менший за обсяг даних у ядрі, ядро не повертає помилку, а зрізає (truncate) копійований обсяг до розміру `_IOC_SIZE(cmd)` байтів.
4. **Сумісність 32-біт та 64-біт систем (Compat ioctl):** Якщо 32-бітна програма виконується на 64-бітному ядрі, системний виклик проходить через обробник `evdev_compat_ioctl()`. Це необхідно для коректної трансляції структур, чий розмір залежить від ширини машинного слова (зокрема, структури `input_event` із мітками часу `struct timeval`).

---

## 2. Структури даних підсистеми evdev

### 2.1. Структура події `struct input_event`

Визначена у заголовному файлі `<linux/input.h>`. Кожен виклик `read()` з файлового дескриптора `/dev/input/eventX` повертає один або декілька послідовних екземплярів цієї структури.

:::tabs
```c
struct input_event {
#if (__BITS_PER_LONG == 32)
    __kernel_ulong_t input_event_sec;
    __kernel_ulong_t input_event_usec;
#else
    struct timeval time;
#endif
    __u16 type;
    __u16 code;
    __s32 value;
};
```
```cpp
// У C++ заголовку <linux/input.h> структура доступна у просторі імен ::input_event
struct input_event {
#if (__BITS_PER_LONG == 32)
    std::uint32_t input_event_sec;
    std::uint32_t input_event_usec;
#else
    struct timeval time;
#endif
    std::uint16_t type;
    std::uint16_t code;
    std::int32_t  value;
};
```
:::

Мітка часу `time` за замовчуванням вимірюється в монотонному часі ядра (`CLOCK_MONOTONIC`). Тип події `type` вказує категорію (`EV_KEY`, `EV_REL`, `EV_ABS`, `EV_SYN`), код `code` деталізує конкретний елемент управління (наприклад, `KEY_ENTER`, `REL_X`, `ABS_Y`), а `value` передає поточний стан або дельту (0 для відпускання, 1 для натискання, 2 для автоповтору).

### 2.2. Ідентифікація пристрою `struct input_id`

Запитується за допомогою команди `EVIOCGID`. Дозволяє системі класифікувати шину підключення та унікальні ідентифікатори виробника.

:::tabs
```c
struct input_id {
    __u16 bustype; // Тип шини (BUS_USB, BUS_I2C, BUS_BLUETOOTH, BUS_HOST, BUS_SPI)
    __u16 vendor;  // 16-бітовий ID виробника (Vendor ID)
    __u16 product; // 16-бітовий ID продукту (Product ID)
    __u16 version; // Версія прошивки або ревізія пристрою
};
```
```cpp
// Структура ідентифікації пристрою у C++
struct input_id {
    std::uint16_t bustype; // BUS_USB, BUS_I2C тощо
    std::uint16_t vendor;  // Vendor ID
    std::uint16_t product; // Product ID
    std::uint16_t version; // Версія прошивки
};
```
:::

Найбільш поширені значення поля `bustype`:

| Константа шини | Числове значення | Опис |
|---|---|---|
| `BUS_PCI` | `0x01` | Внутрішня шина PCI / PCIe |
| `BUS_ISAPNP` | `0x02` | Застаріла шина ISA Plug-and-Play |
| `BUS_USB` | `0x03` | Шина USB (Universal Serial Bus) |
| `BUS_HIL` | `0x04` | Hewlett-Packard Human Interface Loop |
| `BUS_BLUETOOTH` | `0x05` | Бездротова шина Bluetooth |
| `BUS_VIRTUAL` | `0x06` | Віртуальні пристрої (`uinput`, `vmmouse`) |
| `BUS_ISA` | `0x10` | Системна шина ISA |
| `BUS_I8042` | `0x11` | Контролер клавіатури/миші PS/2 |
| `BUS_XTKBD` | `0x12` | Давній протокол XT Keyboard |
| `BUS_RS232` | `0x13` | Послідовний порт RS-232 |
| `BUS_GAMEPORT` | `0x14` | Аналоговий Gameport |
| `BUS_PARPORT` | `0x15` | Паралельний порт LPT |
| `BUS_AMIGA` | `0x16` | Внутрішня шина Amiga |
| `BUS_ADB` | `0x17` | Apple Desktop Bus |
| `BUS_I2C` | `0x18` | Шина I2C (сенсорні панелі ноутбуків) |
| `BUS_HOST` | `0x19` | Вбудовані SOC-контролери та GPIO |
| `BUS_SPI` | `0x1C` | Послідовна шина SPI |

### 2.3. Параметри абсолютних осей `struct input_absinfo`

Запитується за допомогою команди `EVIOCGABS(axis)` та встановлюється через `EVIOCSABS(axis)`. Використовується для калібрування сенсорних екранів, джойстиків та планшетів.

:::tabs
```c
struct input_absinfo {
    __s32 value;      // Поточне абсолютне значення осі
    __s32 minimum;    // Мінімальне апаратне значення (наприклад, 0)
    __s32 maximum;    // Максимальне апаратне значення (наприклад, 4096)
    __s32 fuzz;       // Похибка/шум аналогово-цифрового перетворювача (фільтр миготіння)
    __s32 flat;       // Розмір «мертвої зони» в центрі осі (для аналогових стиків джойстика)
    __s32 resolution; // Роздільна здатність осі у units/mm або units/radians
};
```
```cpp
// Параметри осі координат у C++
struct input_absinfo {
    std::int32_t value;      // Поточне значення
    std::int32_t minimum;    // Мін значення
    std::int32_t maximum;    // Макс значення
    std::int32_t fuzz;       // Похибка/шум
    std::int32_t flat;       // Мертва зона
    std::int32_t resolution; // Роздільна здатність
};
```
:::

Математичне значення полів `fuzz` та `flat`:
- **`fuzz`:** Визначає поріг чутливості. Зміни координати, менші за `fuzz`, ігноруються ядром і не генерують нових подій `EV_ABS`. Це фільтрує шуми аналогово-цифрового перетворювача (АЦП).
- **`flat`:** Визначає радіус центральної "мертвої зони" (dead zone). Якщо значення осі знаходиться в межах `[-flat, +flat]` відносно центру, ядро округлює його до нуля, відсікаючи люфт джойстика.

---

## 3. Глибокий аналіз бітових масок EVIOCGBIT

Один із найважливіших механізмів `evdev` — запит бітових масок можливостей пристрою через виклик `EVIOCGBIT`. Оскільки пристрої введення можуть підтримувати сотні різних клавіш і осей, ядро кодує їх у вигляді масивів бітових прапорців.

### 3.1. Макроси кодування EVIOCGBIT

Команда `EVIOCGBIT(ev_type, len)` визначається через макрос `_IOC`:

```c
#define EVIOCGBIT(ev, len) _IOC(_IOC_READ, 'E', 0x20 + (ev), len)
```

де:
- `ev` — тип подій (`0` для запиту підтримуваних типів подій, або `EV_KEY`, `EV_REL`, `EV_ABS`, `EV_LED`, `EV_SW`, `EV_MSC`, `EV_FF`, `EV_SND`).
- `len` — розмір виділеного буфера у просторі користувача (в байтах).

Ядро зберігає ці маски у внутрішній структурі `struct input_dev` у вигляді масивів типу `unsigned long`:

```c
unsigned long evbit[BITS_TO_LONGS(EV_CNT)];
unsigned long keybit[BITS_TO_LONGS(KEY_CNT)];
unsigned long relbit[BITS_TO_LONGS(REL_CNT)];
unsigned long absbit[BITS_TO_LONGS(ABS_CNT)];
```

Для маніпуляцій з бітовими масивами ядро та простір користувача використовують такі математичні макроси:

```c
#define BITS_PER_BYTE       8
#define BITS_TO_LONGS(nr)   DIV_ROUND_UP(nr, BITS_PER_BYTE * sizeof(long))
```

### 3.2. Алгоритм зчитування та перевірки бітів у просторі користувача

Оскільки структура `unsigned long` має різну ширину на 32-бітних (4 байти) та 64-бітних (8 байтів) системах, найстійкішим способом інспекції бітових масок у просторі користувача є робота з буфером як з масивом беззнакових байтів (`unsigned char` або `uint8_t`).

Для перевірки біта з кодом `code` у байтовому масиві `uint8_t mask[]` використовується формула:

```c
bool is_bit_set(const uint8_t *mask, int code) {
    return (mask[code / 8] & (1 << (code % 8))) != 0;
}
```

Якщо `ev_type = 0`, маска повертає перелік підтримуваних *категорій* подій. Програма спочатку запитує `EVIOCGBIT(0, sizeof(evbit))`, щоб дізнатися, чи підтримує пристрій категорію `EV_KEY`, і лише після цього викликає `EVIOCGBIT(EV_KEY, sizeof(keybit))` для зчитування маски конкретних клавіш.

### 3.3. Обрізання масок та заповнення буфера

Якщо програма передає буфер, менший за повний розмір маски ядра (наприклад, `len = 8` байтів замість `KEY_CNT / 8` = 96 байтів), ядро копіює лише перші `len` байтів і повертає значення `len` як результат `ioctl`. Незаповнені біти вищих індексів вважаються відсутніми.

Рекомендований порядок дій:
1. Перед викликом `ioctl` обнулити буфер пам'яті за допомогою `memset()`.
2. Викликати `ioctl(fd, EVIOCGBIT(ev_type, sizeof(buf)), buf)`.
3. Повернуте число байтів вказує, скільки байтів ядро реально записало в буфер.

---

## 4. Макроси зчитування рядкових ідентифікаторів: EVIOCGNAME, EVIOCGPHYS, EVIOCGUNIQ

Для отримання текстової інформації про пристрій `evdev` надає три макроси запиту рядків:

```c
#define EVIOCGNAME(len) _IOC(_IOC_READ, 'E', 0x06, len)
#define EVIOCGPHYS(len) _IOC(_IOC_READ, 'E', 0x07, len)
#define EVIOCGUNIQ(len) _IOC(_IOC_READ, 'E', 0x08, len)
```

### 4.1. Призначення рядкових команд

- **`EVIOCGNAME(len)`**: Повертає зрозумілу людям назву пристрою, сформовану драйвером (наприклад, `"Logitech USB Optical Mouse"` або `"AT Translated Set 2 keyboard"`).
- **`EVIOCGPHYS(len)`**: Повертає фізичний топологічний шлях пристрою в шині системи (наприклад, `"usb-0000:00:14.0-1.2/input0"` або `"isa0060/serio0/input0"`). Це дозволяє прив'язати події до конкретного фізичного порту контролера.
- **`EVIOCGUNIQ(len)`**: Повертає унікальний серійний номер пристрою (якщо він прописаний у прошивці USB/Bluetooth) або MAC-адресу бездротового адаптера. Для багатьох стандартних пристроїв цей рядок може бути порожнім.

### 4.2. Гарантії завершення та крайові випадки для рядків

1. **Повернене значення:** На відміну від багатьох викликів POSIX `read`, які повертають кількість записаних байтів, `ioctl(fd, EVIOCGNAME(len), buf)` у разі успіху повертає довжину повернутого рядка в байтах (включаючи завершальний NUL-символ `\0`).
2. **Гарантія NUL-термінації:** Ядро Linux гарантує, що якщо буфер `len > 0`, повернений рядок завжди завершується символом `\0`. Якщо оригінальна назва пристрою довша за `len - 1` символів, ядро обрізає рядок і ставить `\0` на позицію `len - 1`.
3. **Порожні рядки:** Якщо фізичний шлях або серійний номер відсутні в драйвері, `ioctl` повертає від'ємне значення з `errno = ENOENT` або повертає рядок довжиною 1 байт (`"\0"`).

---

## 5. Повний перелік команд ioctl для evdev (EVIOC*)

Нижче зведено всі команди `ioctl` підсистеми `evdev` із описом типу переданого аргументу, напрямку даних та їхнього системного призначення.

### 5.1. Інформаційні та ідентифікаційні команди

- **`EVIOCGVERSION(int *val)`**: Повертає 32-бітове число версії драйвера `evdev` ядра (наприклад, `0x010002` відповідає версії 1.0.2). Призначено для перевірки сумісності API.
- **`EVIOCGID(struct input_id *id)`**: Заповнює структуру `input_id` параметрами шини, Vendor ID, Product ID та версією прошивки.
- **`EVIOCGNAME(int len)`**: Команда зчитує текстову назву пристрою. Аргумент `len` вказує розмір символьного масиву в байтах.
- **`EVIOCGPHYS(int len)`**: Повертає фізичний шлях пристрою в системному дереві контролерів.
- **`EVIOCGUNIQ(int len)`**: Повертає унікальний серійний номер пристрою.
- **`EVIOCGPROP(int len)`**: Зчитує бітову маску властивостей пристрою (`INPUT_PROP_POINTER`, `INPUT_PROP_DIRECT`, `INPUT_PROP_BUTTONPAD`, `INPUT_PROP_SEMI_MT`, `INPUT_PROP_ACCELEROMETER`).

### 5.2. Запит можливостей та глобальних станів

- **`EVIOCGBIT(int ev_type, int len)`**: Команда запитує бітову маску підтримуваних кодів для заданого типу `ev_type`.
- **`EVIOCGKEY(int len)`**: Заповнює байтовий масив поточним станом усіх натиснутих клавіш у системі. Якщо біт з індексом `KEY_A` дорівнює 1, це означає, що клавіша 'A' утримується натиснутою в цей момент.
- **`EVIOCGLED(int len)`**: Заповнює бітову маску поточного стану світлодіодів (`LED_CAPSL`, `LED_NUML`, `LED_SCROLLL`).
- **`EVIOCGSW(int len)`**: Зчитує бітову маску перемикачів станів (наприклад, стан кришки ноутбука `SW_LID` або перемикач `SW_RFKILL_ALL`).
- **`EVIOCGMTSLOTS(int len)`**: Зчитує масив поточних параметрів слотів Multi-Touch для протоколу Type B.

### 5.3. Запит і налаштування абсолютних осей

- **`EVIOCGABS(int axis)`**: Приймає код осі (наприклад, `ABS_X` або `ABS_MT_POSITION_Y`) і заповнює структуру `struct input_absinfo`.
- **`EVIOCSABS(int axis)`**: Приймає вказівник на заповнену структуру `struct input_absinfo` і оновлює внутрішні параметри калібрування осі ядра (мінімум, максимум, fuzz, flat).

### 5.4. Монопольний доступ та анулювання

- **`EVIOCGRAB(int grab)`**: Передає цілочисельне значення `1` для захоплення монопольного доступу або `0` для його звільнення. Після успішного захоплення ядро виключає передачу подій від цього дескриптора всім іншим клієнтам у системі.
- **`EVIOCREVOKE(int reserved)`**: Анулює відкритий файловий дескриптор. Усі наступні спроби виконати `read()` повертатимуть помилку `-ENODEV`. Вживається дисплейними менеджерами при зміні користувацьких сесій.
- **`EVIOCSCLOCKID(int *clkid)`**: Встановлює тип годинника для міток часу подій (`CLOCK_REALTIME`, `CLOCK_MONOTONIC`, `CLOCK_BOOTTIME`).

### 5.5. Керування зворотним зв'язком (Force Feedback)

- **`EVIOCSFF(struct ff_effect *effect)`**: Відправляє новий ефект Force Feedback (вібрація, пружина, опір) у драйвер пристрою.
- **`EVIOCRMFF(int effect_id)`**: Видаляє раніше завантажений ефект за його ідентифікатором.
- **`EVIOCGEFFECTS(int *n_effects)`**: Запитує максимальну кількість ефектів, яку пристрій здатний одночасно зберігати в пам'яті.

---

## 6. Команди ioctl для модуля uinput (UI_*)

Модуль `uinput` надає можливість створювати віртуальні пристрої введення шляхом запису конфігурації у файловий дескриптор `/dev/uinput`.

### 6.1. Структура конфігурації `struct uinput_setup`

Визначена у `<linux/uinput.h>`. Використовується перед реєстрацією пристрою через команду `UI_DEV_SETUP`.

:::tabs
```c
struct uinput_setup {
    struct input_id id;         // Параметри Bustype, Vendor ID, Product ID, Version
    char name[UINPUT_MAX_NAME_SIZE]; // Текстова назва віртуального пристрою
    __u32 ff_effects_max;       // Максимальна кількість підтримуваних ефектів Force Feedback
};
```
```cpp
// Опис конфігурації віртуального пристрою у C++
struct uinput_setup {
    struct input_id id;         // Bustype, Vendor, Product, Version
    char name[UINPUT_MAX_NAME_SIZE]; // Текстова назва
    std::uint32_t ff_effects_max;    // Макс ефектів Force Feedback
};
```
:::

### 6.2. Послідовність викликів UI_*

1. **`UI_SET_EVBIT(int ev_type)`**: Декларує підтримку категорії подій (наприклад, `EV_KEY`, `EV_REL`, `EV_ABS`).
2. **`UI_SET_KEYBIT(int key_code)`**: Оголошує підтримку конкретної клавіші або кнопки (наприклад, `KEY_A`, `BTN_LEFT`).
3. **`UI_SET_RELBIT(int rel_code)`**: Оголошує підтримку конкретної відносної осі (`REL_X`, `REL_Y`).
4. **`UI_SET_ABSBIT(int abs_code)`**: Оголошує підтримку конкретної абсолютної осі (`ABS_X`, `ABS_Y`).
5. **`UI_SET_MSCBIT(int msc_code)`**: Оголошує підтримку службових кодів.
6. **`UI_DEV_SETUP(const struct uinput_setup *setup)`**: Передає ядру ім'я та ідентифікатори пристрою.
7. **`UI_DEV_CREATE(void)`**: Фіналізує конфігурацію та реєструє новий символьний пристрій `/dev/input/eventX` у системі.
8. **`UI_DEV_DESTROY(void)`**: Знищує віртуальний пристрій та видаляє відповідний вузол у `/dev/input/`.

---

## 7. Крайові випадки та інваріанти підсистеми ioctl

При розробці системного ПЗ для роботи з `evdev` необхідно враховувати фундаментальні інваріанти підсистеми та крайові випадки апаратної динаміки.

### 7.1. Крайові випадки (Edge Cases)

1. **Запит буферів нульової довжини (`len = 0`):** Якщо програма викликає `ioctl(fd, EVIOCGBIT(ev, 0), buf)`, ядро повертає `0` без копіювання даних і без помилки. Це дозволяє перевірити факт підтримки ioctl без виділення пам'яті.
2. **Робота з неблокуючими файловими дескрипторами (`O_NONBLOCK`):** Прапор `O_NONBLOCK` впливає лише на виклики `read()` та `write()`. Виклики `ioctl()` завжди виконуються синхронно в контексті викликаючого потоку, незалежно від наявності `O_NONBLOCK`.
3. **Фізичне від'єднання пристрою (Hotplug Unplug):** Якщо пристрій USB чи Bluetooth висмикнуто під час виконання `ioctl`, виклик повертає `-1`, а `errno` встановлюється в `ENODEV`. Наступні виклики до цього дескриптора негайно завершуються помилкою `ENODEV`.
4. **Зміна джерела часу (`EVIOCSCLOCKID`):** Зміна годинника з `CLOCK_REALTIME` на `CLOCK_MONOTONIC` стосується лише *нових* подій, які надходитимуть після виклику `ioctl`. Події, які вже знаходяться в кільцевому буфері (ring buffer) клієнта, зберігають старі мітки часу.
5. **Конкурентні виклики `EVIOCGRAB`:** Якщо два процеси одночасно намагаються викликати `EVIOCGRAB(1)` на тому самому символьному пристрої, лише один виклик завершиться успішно (`0`). Другий потік негайно отримає помилку `EBUSY`.
6. **Анулювання дескриптора через `EVIOCREVOKE`:** Виклик `EVIOCREVOKE` є односторонньою незворотною операцією. Після її виконання файловий дескриптор стає "мертвим": будь-які `read()`, `write()` та `ioctl()` повертають `ENODEV`. Відновити дескриптор неможливо, програма мусить закрити його через `close()`.

### 7.2. Інваріанти підсистеми (Invariants)

1. **Атомарність зчитування стану:** Запит бітової маски через `EVIOCGBIT` або зчитування стану клавіш через `EVIOCGKEY` виконується під захистом внутрішнього спін-лока драйвера (`dev->event_lock`). Простір користувача завжди отримує узгоджений зріз стану пристрою на момент виклику.
2. **Немутуючий характер запитів (`Query Non-Mutability`):** Жоден з викликів зчитування `EVIOCG*` не змінює внутрішній стан драйвера чи черги подій. Вони не вилучають події з буфера `read()`.
3. **Ізоляція монопольного захоплення:** Після успішного `EVIOCGRAB(1)` ядро гарантує, що жоден інший клієнт підсистеми `evdev` не отримає жодної події від цього пристрою до виклику `EVIOCGRAB(0)` або закриття файлового дескриптора.
4. **Сувора послідовність конфігурації `uinput`:** Неможливо викликати `UI_DEV_CREATE` без попереднього виконання `UI_DEV_SETUP` (або заповнення застарілої структури `uinput_user_dev`). Спроба порушити порядок повертає `EINVAL`.

---

## 8. Коди помилок системних викликів (errno)

При некоректному виклику `ioctl` системний виклик повертає значення `-1`, а системна змінна `errno` встановлюється в один із наступних кодів:

- **`EBUSY`**: Спроба виконати `EVIOCGRAB` на пристрої, який вже захоплений іншим процесом.
- **`EINVAL`**: Передано недійсний код осі, невідомий макрос `ioctl`, або некоректні параметри `uinput_setup`.
- **`EFAULT`**: Вказівник у просторі користувача посилається на недоступну адресу пам'яті (невдала перевірка `access_ok()`).
- **`ENODEV`**: Фізичний пристрій було від'єднано від шини, або дескриптор було анульовано через `EVIOCREVOKE`.
- **`EPERM` / `EACCES`**: Відсутні права доступу на відкриття `/dev/input/eventX` чи `/dev/uinput` (необхідні права `root` або приналежність до групи `input`).
- **`ENOTTY`**: Переданий файловий дескриптор не належить символьному пристрою або передано невідомий код `ioctl`.
- **`ENOSYS`**: Функціональність не підтримується даною версією ядра або конкретним драйвером пристрою.

---

## 9. Повний практичний приклад інспекції пристрою

Наведений нижче приклад відкриває символьний пристрій `/dev/input/event0`, запитує версію API, назву, ідентифікатори, перевіряє підтримку осей та клавіш і зчитує діапазони абсолютних осей.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/input.h>
#include <errno.h>

static int check_bit(const unsigned char *mask, int bit) {
    return (mask[bit / 8] & (1 << (bit % 8))) != 0;
}

int main(int argc, char *argv[]) {
    const char *dev_path = (argc > 1) ? argv[1] : "/dev/input/event0";

    int fd = open(dev_path, O_RDONLY);
    if (fd < 0) {
        perror("Помилка відкриття пристрою evdev");
        return EXIT_FAILURE;
    }

    // 1. Запит версії драйвера evdev
    int version = 0;
    if (ioctl(fd, EVIOCGVERSION(&version)) < 0) {
        perror("Помилка EVIOCGVERSION");
        close(fd);
        return EXIT_FAILURE;
    }
    printf("Версія evdev API: %d.%d.%d\n",
           version >> 16, (version >> 8) & 0xff, version & 0xff);

    // 2. Зчитування ідентифікаторів пристрою (bustype, vendor, product, version)
    struct input_id id;
    if (ioctl(fd, EVIOCGID(&id)) == 0) {
        printf("ID: Bus=0x%04x Vendor=0x%04x Product=0x%04x Version=0x%04x\n",
               id.bustype, id.vendor, id.product, id.version);
    }

    // 3. Зчитування назви пристрою
    char name[256] = "Невідомий пристрій";
    if (ioctl(fd, EVIOCGNAME(sizeof(name)), name) >= 0) {
        printf("Назва: %s\n", name);
    }

    // 4. Зчитування фізичного шляху
    char phys[256] = "N/A";
    if (ioctl(fd, EVIOCGPHYS(sizeof(phys)), phys) >= 0) {
        printf("Фізичний шлях: %s\n", phys);
    }

    // 5. Перевірка підтримуваних типів подій (evbit)
    unsigned char evbit[(EV_MAX / 8) + 1];
    memset(evbit, 0, sizeof(evbit));
    if (ioctl(fd, EVIOCGBIT(0, sizeof(evbit)), evbit) < 0) {
        perror("Помилка зчитання EVIOCGBIT(0)");
        close(fd);
        return EXIT_FAILURE;
    }

    printf("Підтримувані типи подій:\n");
    if (check_bit(evbit, EV_KEY)) printf("  - EV_KEY (Клавіші/Кнопки)\n");
    if (check_bit(evbit, EV_REL)) printf("  - EV_REL (Відносні осі)\n");
    if (check_bit(evbit, EV_ABS)) printf("  - EV_ABS (Абсолютні осі)\n");
    if (check_bit(evbit, EV_MSC)) printf("  - EV_MSC (Службові події)\n");
    if (check_bit(evbit, EV_SW))  printf("  - EV_SW  (Перемикачі)\n");
    if (check_bit(evbit, EV_LED)) printf("  - EV_LED (Світлодіоди)\n");
    if (check_bit(evbit, EV_FF))  printf("  - EV_FF  (Force Feedback)\n");

    // 6. Якщо підтримуються абсолютні осі, запитуємо деталі ABS_X
    if (check_bit(evbit, EV_ABS)) {
        unsigned char absbit[(ABS_MAX / 8) + 1];
        memset(absbit, 0, sizeof(absbit));
        if (ioctl(fd, EVIOCGBIT(EV_ABS, sizeof(absbit)), absbit) >= 0) {
            if (check_bit(absbit, ABS_X)) {
                struct input_absinfo abs;
                if (ioctl(fd, EVIOCGABS(ABS_X), &abs) == 0) {
                    printf("Вісь ABS_X: min=%d, max=%d, fuzz=%d, flat=%d, res=%d\n",
                           abs.minimum, abs.maximum, abs.fuzz, abs.flat, abs.resolution);
                }
            }
        }
    }

    close(fd);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <array>
#include <cstdint>
#include <cstring>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/input.h>

// RAII обгортка для файлового дескриптора evdev
class EvdevDevice {
private:
    int fd_{-1};

public:
    explicit EvdevDevice(const std::string& path) {
        fd_ = ::open(path.c_str(), O_RDONLY);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити " + path);
        }
    }

    ~EvdevDevice() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    EvdevDevice(const EvdevDevice&) = delete;
    EvdevDevice& operator=(const EvdevDevice&) = delete;

    EvdevDevice(EvdevDevice&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    EvdevDevice& operator=(EvdevDevice&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }

    [[nodiscard]] std::uint32_t get_version() const {
        int version = 0;
        if (::ioctl(fd_, EVIOCGVERSION(&version)) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка EVIOCGVERSION");
        }
        return static_cast<std::uint32_t>(version);
    }

    [[nodiscard]] ::input_id get_id() const {
        ::input_id id{};
        if (::ioctl(fd_, EVIOCGID(&id)) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка EVIOCGID");
        }
        return id;
    }

    [[nodiscard]] std::string get_name() const {
        std::array<char, 256> buf{};
        if (::ioctl(fd_, EVIOCGNAME(buf.size()), buf.data()) < 0) {
            return "Невідомо";
        }
        return std::string(buf.data());
    }

    [[nodiscard]] std::vector<std::uint8_t> get_bitmask(int ev_type, std::size_t max_bytes) const {
        std::vector<std::uint8_t> mask(max_bytes, 0);
        if (::ioctl(fd_, EVIOCGBIT(ev_type, mask.size()), mask.data()) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка EVIOCGBIT");
        }
        return mask;
    }

    [[nodiscard]] ::input_absinfo get_abs_info(int axis) const {
        ::input_absinfo abs{};
        if (::ioctl(fd_, EVIOCGABS(axis), &abs) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка EVIOCGABS");
        }
        return abs;
    }
};

static bool check_bit(const std::vector<std::uint8_t>& mask, int bit) {
    std::size_t byte_idx = static_cast<std::size_t>(bit) / 8;
    if (byte_idx >= mask.size()) return false;
    return (mask[byte_idx] & (1U << (static_cast<std::size_t>(bit) % 8))) != 0;
}

int main(int argc, char* argv[]) {
    const std::string dev_path = (argc > 1) ? argv[1] : "/dev/input/event0";

    try {
        EvdevDevice dev(dev_path);

        auto ver = dev.get_version();
        std::cout << "Версія evdev API: "
                  << (ver >> 16) << "." << ((ver >> 8) & 0xff) << "." << (ver & 0xff) << "\n";

        auto id = dev.get_id();
        std::cout << "ID: Bus=0x" << std::hex << id.bustype
                  << " Vendor=0x" << id.vendor
                  << " Product=0x" << id.product
                  << " Version=0x" << id.version << std::dec << "\n";

        std::cout << "Назва: " << dev.get_name() << "\n";

        auto evbit = dev.get_bitmask(0, (EV_MAX / 8) + 1);
        std::cout << "Підтримувані типи подій:\n";
        if (check_bit(evbit, EV_KEY)) std::cout << "  - EV_KEY (Клавіші)\n";
        if (check_bit(evbit, EV_REL)) std::cout << "  - EV_REL (Відносні осі)\n";
        if (check_bit(evbit, EV_ABS)) std::cout << "  - EV_ABS (Абсолютні осі)\n";

        if (check_bit(evbit, EV_ABS)) {
            auto absbit = dev.get_bitmask(EV_ABS, (ABS_MAX / 8) + 1);
            if (check_bit(absbit, ABS_X)) {
                auto abs = dev.get_abs_info(ABS_X);
                std::cout << "Вісь ABS_X: min=" << abs.minimum
                          << ", max=" << abs.maximum
                          << ", fuzz=" << abs.fuzz
                          << ", flat=" << abs.flat << "\n";
            }
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка виконання: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::
