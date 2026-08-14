# Підсистема введення evdev та події /dev/input/eventX

<preknowlist>
- [Символьні та блокові пристрої](book:unix-linux/character-and-block-devices) — як ядро представляє пристрої в VFS через мажорні та мінорні номери та символьні файли `/dev/`.
- [Системний виклик ioctl](book:unix-linux/ioctl-interface) — механізм виклику керуючих команд для конфігурації пристроїв.
- [Правила udev](book:unix-linux/udev-rules) — динамічне створення вузлів пристроїв у `/dev` та розмежування прав доступу під час гарячого підключення.
</preknowlist>

Подвійний клік миші USB, дотик до ємнісного тачскріна I2C чи натискання фізичної кнопки на клавіатурі PS/2 генерують кардинально різні електричні сигнали й апаратні переривання. Якби кожен графічний додаток чи віконний менеджер мусив тримати власні драйвери для тисяч моделей клавіатур і сенсорів, розробка софту зупинилася б. Проблема ускладнюється тим, що рух миші — це відносний зсув (дельта по осях `X` та `Y`), а дотик до екрана — це абсолютна координата `(x, y)` з силою натискання, але обом потрібен спільний формат представлення подій у просторі користувача.

У підсистемі введення Linux (Input Subsystem) це завдання вирішено через розділення апаратного драйвера та обробника подій. Серцем цієї абстракції є обробник `evdev` (Event Device), який трансформує довільні сигнали від обладнання у стандартизований потік подій у символьних файлах `/dev/input/eventX`.

![Архітектура Input Subsystem](/reference/unix-linux/devices/input-evdev-subsystem/img/input-subsystem.svg)
*Архітектура підсистеми введення Linux: маршрутизація від апаратного драйвера через Input Core до обробника evdev та простору користувача.*

---

## 1. Архітектура підсистеми введення: три рівні абстракції

Підсистема введення ядра Linux складається з трьох послідовних рівнів, де кожен верхній шар абстрагує детальну специфіку нижнього:

1. **Драйвери апаратних шин та пристроїв (Device Drivers).** Драйвери рівня ядра (`usbhid`, `i2c-hid`, `psmouse`, `atkbd`, `hid-multitouch`) безпосередньо приймають переривання від контролерів шин USB, I2C, SPI чи PS/2. При надходженні апаратного переривання драйвер використовує асинхронні USB URB (USB Request Block) або виклики `request_threaded_irq()`, декодує сирий звіт (HID Report) або байти скан-коду і передає їх у шар Input Core через виклик `input_event()`.
2. **Ядро підсистеми введення (Input Core, `drivers/input/input.c`).** Виступає центральним мультиплексором та маршрутизатором. Ядро зберігає список зареєстрованих пристроїв (`struct input_dev`) та список зареєстрованих обробників подій (`struct input_handler`). Під час реєстрації нового пристрою Input Core викликає функцію зіставлення `input_match_device()`, порівнюючи бітові маски підтримуваних подій (`evbit`, `keybit`, `relbit`, `absbit`). При наявності збігу створюється зв'язуючий об'єкт `struct input_handle`.
3. **Обробники подій (Event Handlers).** Формують інтерфейси для простору користувача:
   - **`evdev` (Event Device):** Універсальний обробник (`drivers/input/evdev.c`). Створює символьні пристрої `/dev/input/eventX` (де `X` — порядковий номер від 0 до 31+). Повертає зріз сирих подій у вигляді двійкових структур `struct input_event`.
   - **`mousedev`:** Застарілий шар сумісності (`drivers/input/mousedev.c`), який транслює події будь-яких мишей та тачпадів у 3-байтовий протокол PS/2 через `/dev/input/mice`.
   - **`joydev`:** Застарілий обробник джойстиків (`/dev/input/jsX`), замінений у сучасних іграх на прямий доступ через `evdev`.

Історичні причини переходу від фрагментованих драйверів до уніфікованої архітектури `evdev` описані в [історичній вставці](book:unix-linux/input-evdev-subsystem/hist-input-subsystem-evolution.md).

---

## 2. Механізм зіставлення `input_match_device()` та топологія sysfs

Коли апаратний драйвер виявляє новий пристрій (наприклад, підключення USB-миші), він виділяє пам'ять під структуру `struct input_dev`, заповнює ідентифікатори шини (`id.bustype`, `id.vendor`, `id.product`) та встановлює біти в масках можливостей (`evbit`, `keybit`, `relbit`). Після цього драйвер викликає функцію реєстрації ядра:

```text
input_register_device(struct input_dev *dev)
```

Усередині `input_register_device()` ядро виконує обхід глобального списку зареєстрованих обробників подій `input_handler_list`. Для кожного обробника (наприклад, `evdev_handler`, `mousedev_handler`, `kbd_handler`) викликається функція перевірки відповідності `input_match_device()`:

1. Ядро порівнює маску `handler->id_table` з параметрами `dev->id`.
2. Ядро виконує побітове поєднання `AND` між масками можливостей обробника та пристрою:
   ```text
   (dev->evbit & handler->evbit) == handler->evbit
   ```
3. Якщо всі потрібні біти збігаються, ядро викликає метод `handler->connect(handler, dev, id)`, який виділяє структуру `input_handle` та реєструє новий вузол пристрою у системній файловій системі `sysfs`.

У псевдофайловій системі `sysfs` кожен пристрій введення отримує власний каталог за адресою `/sys/class/input/eventX/`. У цьому каталозі ядро експортує текстові атрибути, які дозволяють підсистемі `udev` класифікувати пристрій без відкриття двійкового файлу:

- `/sys/class/input/eventX/device/name`: Текстова назва пристрою.
- `/sys/class/input/eventX/device/id/bus`: Шестинадцятковий тип шини.
- `/sys/class/input/eventX/device/capabilities/ev`: Шістнадцяткова бітова маска підтримуваних типів подій `evbit`.
- `/sys/class/input/eventX/device/capabilities/key`: Шістнадцяткова бітова маска підтримуваних клавіш `keybit`.

Правила `udev` зчитують ці маски під час підключення пристрою (Hotplug) і на основі бітів створюють симлінки у `/dev/input/by-id/` та `/dev/input/by-path/`, а також виставляють POSIX-права доступу для групи `input`.

---

## 3. Анатомія події: `struct input_event`

Кожен виклик `read()` з файлового дескриптора `/dev/input/eventX` повертає один або кілька екземплярів двійкової структури `input_event`, визначеної у заголовному файлі `<linux/input.h>`:

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
// Подання структури події подібне у C++ заголовку <linux/input.h>
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

Розмір структури становить 24 байти на 64-бітних архітектурах (8 байтів секунди + 8 байтів мікросекунди + 2 байти тип + 2 байти код + 4 байти значення) і 16 байтів на старіших 32-бітних ABI.

> [!NOTE]
> **Проблема 2038 року (y2038):** На 32-бітних архітектурах поле `struct timeval` містило 32-бітове число секунд, яке переповниться в січні 2038 року. Починаючи з ядра Linux 5.6, двійкову структуру було оновлено заміною `timeval` на поля `input_event_sec` та `input_event_usec`, які забезпечують 64-бітову монотонну мітку часу навіть на 32-бітних системах.

### Поля структури:

- **`time` (`input_event_sec` / `input_event_usec`):** Монотонна мітка часу (`CLOCK_MONOTONIC`), яка вказує на точну секунду та мікросекунду, коли драйвер ядра обробив переривання від пристрою.
- **`type`:** Загальна категорія події.
- **`code`:** Суб-код, який вказує на конкретний орган управління (наприклад, клавіша `KEY_A`, вісь `REL_X` чи кнопка миші `BTN_LEFT`).
- **`value`:** Значення події, інтерпретація якого залежить від `type` та `code`.

```
 Подія input_event (24 байти на 64-біт системі)
┌──────────────────────────────────┬──────────┬──────────┬───────────┐
│ time (tv_sec: 8B, tv_usec: 8B)   │ type(2B) │ code(2B) │ value(4B) │
└──────────────────────────────────┴──────────┴──────────┴───────────┘
```

### Основні типи подій (`type`):

- **`EV_SYN` (`0x00`):** Події синхронізації. Поділяють потік на окремі атомарні фрейми.
- **`EV_KEY` (`0x01`):** Зміна стану клавіші чи кнопки. Значення `value`: `1` — натиснуто, `0` — відпущено, `2` — автоповтор (генерується внутрішнім таймером ядра `dev->timer` при тривалому утриманні клавіші).
- **`EV_REL` (`0x02`):** Відносний зсув координат. Використовується мишами та трекболами. Значення `value` позначає величину зсуву (наприклад, `-4` або `+12` відліків оптичного датчика).
- **`EV_ABS` (`0x03`):** Абсолютна координата. Використовується сенсорними екранами, графічними планшетами та аналоговими джойстиками. Значення `value` вказує точне число в межах оцифрованого діапазону.
- **`EV_MSC` (`0x04`):** Додаткові апаратні події (наприклад, `MSC_SCAN` передає сирий скан-код контролера клавіатури).
- **`EV_SW` (`0x05`):** Перемикачі стану (наприклад, `SW_LID` — закриття кришки ноутбука, `SW_HEADPHONE_INSERT` — підключення штекера аудіо).
- **`EV_LED` (`0x11`):** Керування світлодіодами (`LED_CAPSL`, `LED_NUML`). Запис цієї події у `/dev/input/eventX` вмикає або вимикає індикатор на фізичній клавіатурі.
- **`EV_REP` (`0x14`):** Параметри автоповтору клавіш (`REP_DELAY` — затримка перед повтором у мс, `REP_PERIOD` — інтервал між повторами у мс).
- **`EV_FF` (`0x15`):** Силовий зворотний зв'язок (Force Feedback). Дозволяє надсилати ефекти вібрації та опору керма чи геймпада.

---

## 4. Підсистема силового зворотного зв'язку (Force Feedback: EV_FF)

Окрім читання подій введення, `evdev` підтримує двосторонній обмін даними для пристроїв із зворотним зв'язком (геймпади з вібромоторами, керма з сервоприводами).

Підсистема Force Feedback працює за завантажувальною схемою:

1. Простір користувача створює структуру ефекту `struct ff_effect` (наприклад, тип `FF_RUMBLE` з параметрами сили сильного та слабкого вібромоторів, або `FF_PERIODIC` з синусоїдальною хвилею віддачі).
2. За допомогою системного виклику `ioctl(fd, EVIOCSFF, &effect)` програма завантажує ефект у внутрішню пам'ять пристрою чи драйвера ядра. Вона отримує унікальний `effect.id`.
3. Для активації ефекту програма надсилає в `/dev/input/eventX` звичайну подію `input_event` з `type = EV_FF`, `code = effect.id` та `value = 1` (запуск) або `value = 0` (зупинка).
4. Після завершення використання ефект видаляється викликом `ioctl(fd, EVIOCRMFF, effect.id)`.

Така двоступенева схема дозволяє програмам завантажувати складні фізичні ефекти (опір треку, пружину, тертя) один раз, після чого активувати їх за одну мікросекунду без накладних витрат на передачу двійкового опису хвилі при кожному пострілі чи зіткненні в грі.

---

## 5. Протоколи Multi-Touch (MT Protocol Type A та Type B)

З появою сенсорних екранів, здатних відстежувати до 10 дотиків одночасно, стандартних осей `ABS_X` та `ABS_Y` виявилося недостатньо. Ядро Linux ввело розширення **Multi-Touch (MT Protocol)**, яке кодує координати через коди `ABS_MT_*`.

Існує два типи протоколів MT:

1. **Type A (для простих пристроїв без апаратного відстеження пальців):** Драйвер передає координати всіх контактних точок по черзі, розділяючи точки подією `EV_SYN SYN_MT_REPORT`. Простір користувача мусить самостійно зіставляти координати між кадрами, розпізнаючи, який палець куди перемістився.
2. **Type B (для сучасних тачскрінів з апаратними слотами):** Драйвер присвоює кожному контакту унікальний номер слота через `ABS_MT_SLOT` та ідентифікатор трекінгу `ABS_MT_TRACKING_ID`. Якщо палець рухається, ядро надсилає події лише для зміни слота:

```text
type = EV_ABS, code = ABS_MT_SLOT,        value = 0
type = EV_ABS, code = ABS_MT_POSITION_X, value = 420
type = EV_ABS, code = ABS_MT_POSITION_Y, value = 810
type = EV_ABS, code = ABS_MT_SLOT,        value = 1
type = EV_ABS, code = ABS_MT_POSITION_X, value = 950
type = EV_SYN, code = SYN_REPORT,        value = 0
```

Завдяки слотовому протоколу Type B передача даних мультитач стала в рази ефективнішою, оскільки незмінні координати сусідніх пальців не дублюються у потоці.

---

## 6. Механізм синхронізації `EV_SYN` та кільцевий буфер `evdev_client`

Пристрої введення часто надсилають кілька вимірів одночасно. Наприклад, при похилому русі миші оптичний датчик одночасно фіксує переміщення по горизонталі та вертикалі. Якби простір користувача прочитав зсув `REL_X` і відразу оновив позицію курсора до отримання `REL_Y`, це призвело б до «ступінчастого» ефекту (tearing) та викривлення обробки діагональних жестів.

![Потік подій evdev](/reference/unix-linux/devices/input-evdev-subsystem/img/evdev-event-flow.svg)
*Механізм атомарного фреймінгу через SYN_REPORT та обробка переповнення кільцевого буфера за допомогою SYN_DROPPED.*

### Атомарний фрейм `SYN_REPORT`

Щоб забезпечити атомарність updates, драйвер ядра надсилає серію подій `EV_REL` або `EV_ABS`, після чого додає фінальну розділову подію:

```text
type = EV_REL, code = REL_X, value = +15
type = EV_REL, code = REL_Y, value = -8
type = EV_SYN, code = SYN_REPORT, value = 0   <-- Транзакцію завершено!
```

Графічний сервер (Wayland compositor або X11) накопичує події у проміжному буфері та перераховує позицію курсора чи стан вікна **лише після отримання `SYN_REPORT`**.

### Кільцевий буфер та переповнення `SYN_DROPPED`

Кожен процес, який відкриває файл `/dev/input/eventX`, отримує в ядрі власну структуру `struct evdev_client` з кільцевим буфером `buffer` (типовий розмір — від 64 до 128 елементів `struct input_event`).

Якщо процес простору користувача заблокувався (наприклад, через важкі обчислення або затримку дискового I/O) і не встигає викликати `read()`, кільцевий буфер переповнюється. Коли ядро змушене перезаписати ще не прочитані події новими, воно скидає буфер клієнта й інжектує спеціальну подію:

```text
type = EV_SYN, code = SYN_DROPPED, value = 0
```

> [!CAUTION]
> Коли програма бачить `SYN_DROPPED`, вона повинна усвідомити, що безперервність потоку подій порушено. Програма зобов'язана очистити свій накопичений стан та за допомогою системних викликів `ioctl` (`EVIOCGKEY`, `EVIOCGABS`) заново опитати глобальний апаратний стан пристрою, щоб синхронізувати реальність.

---

## 7. Зчитування та обробка подій у коді (C та C++)

Приклад нижче показує відкриття файлу пристрою `/dev/input/eventX`, перевірку розміру структури та читання подій у циклі.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <linux/input.h>

int main(int argc, char *argv[]) {
    const char *dev_path = (argc > 1) ? argv[1] : "/dev/input/event0";
    int fd = open(dev_path, O_RDONLY);
    if (fd < 0) {
        perror("Не вдалося відкрити пристрій введення");
        return 1;
    }

    printf("Відкрито %s. Читання подій (натисніть Ctrl+C для виходу)...\n", dev_path);

    struct input_event ev;
    while (1) {
        ssize_t bytes_read = read(fd, &ev, sizeof(ev));
        if (bytes_read < 0) {
            if (errno == EINTR) continue;
            perror("Помилка читання з evdev");
            break;
        }

        if (bytes_read != sizeof(ev)) {
            fprintf(stderr, "Прочитано некоректну кількість байтів: %zd\n", bytes_read);
            continue;
        }

        if (ev.type == EV_KEY) {
            printf("[KEY] Код: %3d, Значення: %d (%s)\n",
                   ev.code, ev.value,
                   ev.value == 1 ? "Натиснуто" : ev.value == 0 ? "Відпущено" : "Автоповтор");
        } else if (ev.type == EV_REL) {
            printf("[REL] Осi: %3d, Зсув: %d\n", ev.code, ev.value);
        } else if (ev.type == EV_ABS) {
            printf("[ABS] Осi: %3d, Значення: %d\n", ev.code, ev.value);
        } else if (ev.type == EV_SYN) {
            if (ev.code == SYN_REPORT) {
                printf("--- SYN_REPORT (Кінець фрейму) ---\n");
            } else if (ev.code == SYN_DROPPED) {
                printf("⚠️ УВАГА: SYN_DROPPED! Буфер переповнено.\n");
            }
        }
    }

    close(fd);
    return 0;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <system_error>
#include <array>
#include <fcntl.h>
#include <unistd.h>
#include <linux/input.h>

class EvdevReader {
    int fd_{-1};
public:
    explicit EvdevReader(std::string_view path) {
        fd_ = ::open(path.data(), O_RDONLY);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to open evdev device");
        }
    }

    ~EvdevReader() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    EvdevReader(const EvdevReader&) = delete;
    EvdevReader& operator=(const EvdevReader&) = delete;

    void run_loop() {
        struct input_event ev{};
        while (true) {
            ssize_t bytes_read = ::read(fd_, &ev, sizeof(ev));
            if (bytes_read < 0) {
                if (errno == EINTR) continue;
                throw std::system_error(errno, std::generic_category(), "Read error from evdev");
            }

            if (bytes_read != sizeof(ev)) {
                std::cerr << "Incomplete input_event struct read\n";
                continue;
            }

            switch (ev.type) {
                case EV_KEY:
                    std::cout << "[KEY] Code: " << ev.code << ", Value: " << ev.value
                              << " (" << (ev.value == 1 ? "Pressed" : ev.value == 0 ? "Released" : "Repeat") << ")\n";
                    break;
                case EV_REL:
                    std::cout << "[REL] Axis: " << ev.code << ", Delta: " << ev.value << '\n';
                    break;
                case EV_ABS:
                    std::cout << "[ABS] Axis: " << ev.code << ", Value: " << ev.value << '\n';
                    break;
                case EV_SYN:
                    if (ev.code == SYN_REPORT) {
                        std::cout << "--- SYN_REPORT ---\n";
                    } else if (ev.code == SYN_DROPPED) {
                        std::cout << "⚠️ WARNING: SYN_DROPPED detected!\n";
                    }
                    break;
                default:
                    break;
            }
        }
    }
};

int main(int argc, char* argv[]) {
    const char* path = (argc > 1) ? argv[1] : "/dev/input/event0";
    try {
        std::cout << "Opening " << path << "...\n";
        EvdevReader reader(path);
        reader.run_loop();
    } catch (const std::exception& ex) {
        std::cerr << "Error: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
```
:::

---

## 8. Контроль та інспекція пристроїв через `ioctl`

Окрім звичайного потоку читання подій, `evdev` надає розширений інтерфейс керування `ioctl`.

Повний перелік команд, структур даних та кодів помилок наведено в [довіднику ioctl](book:unix-linux/input-evdev-subsystem/api-evdev-ioctls.md).

### 8.1. Запит назви та ідентифікаторів (`EVIOCGNAME`, `EVIOCGID`)

За допомогою `EVIOCGNAME` програма отримує зрозуміле людям ім'я пристрою, а `EVIOCGID` повертає структуру `input_id` із кодами виробника та продукту.

:::tabs
```c
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/input.h>

void print_device_info(int fd) {
    struct input_id id;
    char name[256] = "Unknown";

    if (ioctl(fd, EVIOCGNAME(sizeof(name)), name) >= 0 &&
        ioctl(fd, EVIOCGID, &id) >= 0) {
        printf("Пристрій: %s (Bus: 0x%04x, Vendor: 0x%04x, Product: 0x%04x)\n",
               name, id.bustype, id.vendor, id.product);
    }
}
```
```cpp
#include <iostream>
#include <array>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/input.h>

void print_device_info(int fd) {
    struct input_id id{};
    std::array<char, 256> name_buf{};
    name_buf.fill(0);

    if (::ioctl(fd, EVIOCGNAME(name_buf.size()), name_buf.data()) >= 0 &&
        ::ioctl(fd, EVIOCGID, &id) >= 0) {
        std::cout << "Device: " << name_buf.data()
                  << " (Bus: 0x" << std::hex << id.bustype
                  << ", Vendor: 0x" << id.vendor
                  << ", Product: 0x" << id.product << std::dec << ")\n";
    }
}
```
:::

### 8.2. Опитування можливостей через бітові маски (`EVIOCGBIT`)

Як графічний сервер дізнається, чи є пристрій `/dev/input/event3` мишею, клавіатурою чи тачскріном? Він опитує бітові маски можливостей за допомогою виклику **`EVIOCGBIT(ev_type, len)`**:

1. Запит `EVIOCGBIT(0, max_len)` повертає бітову маску *типів подій*, які підтримує пристрій (чи підтримуються `EV_KEY`, `EV_REL`, `EV_ABS`).
2. Запит `EVIOCGBIT(EV_KEY, max_len)` повертає бітову маску підтримуваних *клавіш та кнопок*.
3. Запит `EVIOCGBIT(EV_REL, max_len)` перевіряє наявність осей `REL_X` та `REL_Y`.

Пристрій класифікується як миша, якщо він підтримує `EV_REL` з осями `REL_X`/`REL_Y` та кнопки `BTN_LEFT`/`BTN_RIGHT`. Якщо пристрій має `EV_ABS` з осями `ABS_X`/`ABS_Y` та кнопку `BTN_TOUCH`, ядро та `udev` класифікують його як тачскрін.

### 8.3. Запит діапазонів абсолютних осей (`EVIOCGABS`)

Для сенсорних екранів та планшетів програма повинна знати фізичні межі координат для правильного масштабування подій на роздільну здатність монітора.

:::tabs
```c
#include <stdio.h>
#include <sys/ioctl.h>
#include <linux/input.h>

void print_abs_x_info(int fd) {
    struct input_absinfo abs_x;
    if (ioctl(fd, EVIOCGABS(ABS_X), &abs_x) == 0) {
        printf("Вісь X: Мін = %d, Макс = %d, Похибка = %d, Роздільна здатність = %d units/mm\n",
               abs_x.minimum, abs_x.maximum, abs_x.fuzz, abs_x.resolution);
    }
}
```
```cpp
#include <iostream>
#include <sys/ioctl.h>
#include <linux/input.h>

void print_abs_x_info(int fd) {
    struct input_absinfo abs_x{};
    if (::ioctl(fd, EVIOCGABS(ABS_X), &abs_x) == 0) {
        std::cout << "Axis X: Min = " << abs_x.minimum
                  << ", Max = " << abs_x.maximum
                  << ", Fuzz = " << abs_x.fuzz
                  << ", Resolution = " << abs_x.resolution << " units/mm\n";
    }
}
```
:::

### 8.4. Монопольне захоплення пристрою (`EVIOCGRAB`)

Виклик `ioctl(fd, EVIOCGRAB, 1)` встановлює монопольний режим доступу:

:::tabs
```c
#include <stdio.h>
#include <sys/ioctl.h>
#include <linux/input.h>

int grab_device(int fd, int enable) {
    if (ioctl(fd, EVIOCGRAB, enable ? 1 : 0) < 0) {
        perror("Помилка виконання EVIOCGRAB");
        return -1;
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <system_error>
#include <sys/ioctl.h>
#include <linux/input.h>

void set_device_grab(int fd, bool enable) {
    if (::ioctl(fd, EVIOCGRAB, enable ? 1 : 0) < 0) {
        throw std::system_error(errno, std::generic_category(), "EVIOCGRAB failed");
    }
}
```
:::

Сценарії застосування `EVIOCGRAB`:
- **Екрани блокування (Screen Lockers):** Утиліти на зразок `swaylock` або `i3lock` перехоплюють клавіатуру, щоб кейлоггери у фонових процесах не змогли підслухати пароль користувача.
- **Перепризначувачі клавіш (Key Remappers):** Демон перехоплює фізичні події клавіатури, трансформує їх та надсилає в систему через віртуальний пристрій `/dev/uinput`.
- **FULLSCREEN ігри:** Ігри захоплюють мишу, щоб курсор не вилітав за межі вікна на багатомоніторних конфігураціях.

---

## 9. Роль `libinput` у сучасному просторі користувача

Пряме читання подій з `/dev/input/eventX` чудово підходить для простих кнопок або клавіатур. Проте для тачпадів, сенсорних дисплеїв та графічних планшетів сирий потік `evdev` є занадто складним:

- Тачпади генерують дрібні коливання координат (аналоговий шум), які потребують гістерезису та згладжування.
- При наборі тексту долоня користувача випадково торкається тачпада (потрібен алгоритм Palm Rejection).
- Мультитач-жести (скролінг двома пальцями, pinch-to-zoom трьома пальцями, згортання вікон) вимагають складного автомата станів.

Щоб не дублювати ці алгоритми в кожному композиторі Wayland (Mutter у GNOME, KWin у KDE, Sway, Hyprland), спільнота freedesktop розробила уніфіковану бібліотеку **`libinput`**.

```
 [/dev/input/eventX] ──► [libinput] ──► (Згладжування, Palm Rejection, Жести) ──► [Wayland Compositor]
```

`libinput` відкриває дескриптори `evdev`, застосовує базу даних апаратних особливостей `udev hwdb`, фільтрує шум, обробляє прискорення курсора і надає композиторам готові високорівневі події (`LIBINPUT_EVENT_POINTER_MOTION`, `LIBINPUT_EVENT_GESTURE_PINCH_BEGIN`).

---

## 10. Віртуальні пристрої введення через `/dev/uinput`

У багатьох практичних задачах (програми віддаленого робочого столу VNC/RDP, макроси, емулятори геймпадів, Bluetooth-демони) виникає потреба програмно згенерувати події введення так, ніби вони надійшли від реального заліза.

Для цього використовується спеціальний драйвер **`uinput`** (`/dev/uinput`). Програма простору користувача виконує наступні кроки:

1. Відкриває `/dev/uinput` на запис.
2. Викликами `ioctl(UI_SET_EVBIT)` та `ioctl(UI_SET_KEYBIT)` оголошує можливості віртуального пристрою.
3. Заповнює структуру `struct uinput_setup` (назва, vendor ID, product ID) та надсилає її через `ioctl(UI_DEV_SETUP)`.
4. Викликає `ioctl(UI_DEV_CREATE)`. Ядро створює новий віртуальний пристрій `input_dev` та реєструє відповідний новий вузол `/dev/input/eventX`.
5. Пише структури `struct input_event` безпосередньо у дескриптор `/dev/uinput`.

Повний приклад створення утиліти-перепризначувача клавіш на базі `evdev` та `uinput` із обробкою сигналів очищення наведено у [практичному проекті](book:unix-linux/input-evdev-subsystem/proj-uinput-keyboard-mapper.md).

---

## 11. Діагностика та утиліти інспекції

Для тестування та налагодження пристроїв введення у Linux використовуються утиліти:

- **`evtest`:** Головний інструмент діагностики. Виводить список усіх пристроїв `/dev/input/event*`, запитує їхні властивості через ioctl та друкує потік подій у реальному часі із розшифровкою кодів та значень.
  ```bash
  sudo evtest /dev/input/event0
  ```
- **`libinput debug-events`:** Інструмент із пакету `libinput-tools`. Показує події після обробки та фільтрації бібліотекою `libinput` (корисно для перевірки розпізнавання жестів).
- **`udevadm info -a -p /sys/class/input/event0`:** Показує атрибути пристрою у дереві `sysfs` та правила `udev`, які впливають на призначення прав доступу.

---

## Висновки

Підсистема введення `evdev` є прикладом елегантної та стійкої архітектури Linux: вона абстрагує сотні різноманітних фізичних шин та драйверів за допомогою єдиного формата подій `struct input_event` та уніфікованих псевдофайлів `/dev/input/eventX`. Завдяки атомарному фреймінгу `EV_SYN`, багатому інтерфейсу `ioctl`, обробці гістерезису в `libinput` та можливостям віртуалізації через `uinput`, Linux надає розробникам потужний інструментарій для роботи з будь-якими пристроями людино-машинного інтерфейсу.
