# Налагодження на хості: gdb і санітайзери

<preknowlist>
- [Розбір HardFault](root:sf-devices/hardfault) — апаратний знімок стану МК, регістри відмови та збої пам'яті.
- [Невизначена поведінка](root:sf-lang/undefined-behavior) — оптимізації компілятора довкола UB у мовах C та C++.
- [printf на пристрої](root:sf-devices/printf-na-prystroi) — накладні витрати й спотворення часових параметрів у послідовному моніторі.
- [Модульне тестування](root:sf-release/unit-testing) — методологія ізоляції компонентів та автоматизовані тести.
</preknowlist>

Коли вбудована прошивка з десятком датчиків і мережевим протоколом зависає раз на добу, спроба локалізувати помилку безпосередньо на мікроконтролері перетворюється на виснажливе перешивання флеш-пам'яті через JTAG-адаптер. Кожна зміна коду вимагає перекомпіляції cross-тулчейном, запису бінарного образу розміром 500 КБ зі швидкістю 50–100 КБ/с та повторного запуску пристрою. Якщо тестовий набір містить двісті сценаріїв, повний прогін на залізі займає десятки хвилин, а будь-яка асинхронна подія або плаваючий контакт на макетній платі спотворюють результати вимірювань.

Гірше за повільність є фундаментальна апаратна сліпота мікроконтролера. Більшість процесорних ядер (Cortex-M0, Cortex-M3, Cortex-M4) позбавлені блоку управління віртуальною пам'яттю (MMU). Коли алгоритм фільтрації або парсер пакетів виходить за межі виділеного стекового масиву на 4 байти, процесор не генерує жодного сигналу аварії: він мовчки затирає сусідню змінну, покажчик зворотного виклику або лічильник циклу. Програма продовжує виконання, а катастрофічний збій відбувається через мільйони тактів в іншій підсистемі, де зчитується вже спотворене значення, залишаючи розробника перед безмовним апаратним збоєм [HardFault](root:sf-devices/hardfault) без зрозумілого стека викликів.

**Налагодження на хості** (*Host-Based Debugging*) вирішує цю проблему переносом усієї апаратно-незалежної логіки — протоколів, кінцевих автоматів, математичних фільтрів та бізнес-правил — у нативне середовище виконання комп'ютера розробника (Linux, macOS, Windows). Замість повільного прошивання фізичного чипа тести збираються нативним компілятором Clang або GCC за долі секунди й виконуються в захищеній пам'яті операційної системи. Підключення динамічних санітайзерів (AddressSanitizer, UndefinedBehaviorSanitizer) перетворює тихі руйнування пам'яті та невизначену поведінку на миттєве переривання процесу з точним зазначенням файлу, рядка й побайтового стану пам'яті.

---

## Економіка зворотного зв'язку: фізичний чип проти нативного процесу

Тривалість інженерного циклу між внесенням правки в код і отриманням відповіді «чи працює це» визначає якість архітектури. Якщо зворотний зв'язок триває хвилину, розробник пише код великими неперевіреними блоками. Якщо зворотний зв'язок триває 100 мілісекунд, стає можливим покрокове розроблення через тести (TDD), де кожен виправлений рядок одразу валідується сотнею автоматичних перевірок.

Розкладімо фізичні часові витрати обох підходів:

```
Цикл на цільовому чипі (Target):
Зміна коду ⟹ Cross-збірка (2–5 с) ⟹ JTAG/SWD Flash (15–30 с) ⟹ Перезапуск (0.5 с) ⟹ Тест наосліп (5–30 с)
Сумарно: 25–65 секунд на одну ітерацію перевірки

Цикл на хості (Host-Based):
Зміна коду ⟹ Нативна збірка Clang/GCC (0.2 с) ⟹ Запуск у RAM (0.005 с) ⟹ Звіт ASan/UBSan
Сумарно: 0.2–0.5 секунди на повний прогін сотні тестів
```

Прискорення у 100–1000 разів — це лише один бік медалі. Другий бік — діагностичні можливості робочої станції:

1. **Необмежені апаратні ресурси налагодження**:
   У типовому ядрі ARM Cortex-M модуль DWT (Data Watchpoint and Trace) містить лише від 2 до 4 апаратних компараторів для точок зупинки за записом у пам'ять (watchpoints), а модуль FPB (Flash Patch and Breakpoint) підтримує 6–8 точок зупинки за адресою інструкції. На хості відлагоджувач GDB через механізми ядра операційної системи (`ptrace`, сторінкові права `mprotect`, апаратні регістри `DR0`–`DR7` x86-64) підтримує тисячі точок спостереження без сповільнення роботи програми.

2. **Захищений адресний простір**:
   На комп'ютері розробника кожен процес виконується у власній віртуальній пам'яті. Розіменування нульового покажчика миттєво генерує апаратний сигнал `SIGSEGV` на тій самій процесорній інструкції, де це сталося. На мікроконтролері адреса `0x00000000` часто відображає початок вектору переривань у Flash-пам'яті, тому читання за нульовим покажчиком повертає початковий вказівник стека `_estack`, маскуючи баг доти, доки алгоритм не спробує використати це число як адресу в RAM.

3. **Детермінізм тестового оточення**:
   Фізичні давачі схильні до шумів живлення, завад на довгих проводах та температурного дрейфу. Під час налагодження на платі складно відтворити ситуацію, коли давач завис рівно на 14-му байті пакета або видав невірну контрольну суму CRC. На хості програмний емулятор формує детермінований потік байтів із наперед заданими відхиленнями.

![Порівняння циклів налагодження на фізичному чипі та на хості](/root/eng/sf-devices/nalahodzhennia-na-khosti/img/host-vs-target-cycle.svg)
*Зліва — традиційний шлях з важкою прошивкою у Flash та німими HardFault на залізі; справа — миттєвий цикл виконання нативного процесу з повноцінним перехопленням дефектів пам'яті через санітайзери.*

---

## Архітектура ізоляції: межа HAL та підміна апаратури (Mocking)

Щоб скомпілювати код під архітектуру x86-64 або ARM64 вашого ПК, у ньому не повинно бути прямого доступу до регістрів [відображеної пам'яті MMIO](root:hw-arch/memory-mapped-io) мікроконтролера, асемблерних інструкцій ядра (`__WFI()`, `__disable_irq()`) та заголовкових файлів вендора (`stm32f4xx.h`, `esp_system.h`).

Це вимагає суворого архітектурного поділу системи на два незалежні шари:
- **Апаратно-незалежний шар (Core Logic)**: бізнес-логіка, кінцеві автомати (FSM), фільтри Калмана, ковзні середні, парсери бінарних та текстових протоколів (NMEA, Modbus, CoAP), кодеки та регулятори.
- **Шар абстракції апаратури (HAL - Hardware Abstraction Layer)**: тонкий шар адаптерів, що перетворює виклики читання/запису абстрактних шин (I2C, SPI, UART, CAN, GPIO) на конкретні дії з апаратурою або тестовим моком.

![Архітектура ізоляції бізнес-логіки від апаратних регістрів через межу HAL](/root/eng/sf-devices/nalahodzhennia-na-khosti/img/hal-mock-architecture.svg)
*Межа HAL відокремлює алгоритми від заліза: у прошивці підключається Target Backend (MMIO регістри), а під час тестів на ПК — Host Mock Backend (віртуальна пам'ять з ін'єкцією збоїв).*

### Шаблони реалізації межі HAL на C та C++

У мові C межа абстракції зазвичай оформлюється у вигляді структур з покажчиками на функції (віртуальна таблиця інтерфейсу) або через підміну символів під час компонування (link-time substitution). У C++ використовують або абстрактні інтерфейсні класи, або compile-time поліморфізм через шаблони та концепти C++20, що повністю усуває накладні витрати на непрямі виклики.

Розгляньмо приклад проєктування драйвера давача через межу абстракції шини I2C:

:::tabs
```c
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* Результати операцій шини */
typedef enum {
    HAL_BUS_OK = 0,
    HAL_BUS_ERR_NACK = -1,
    HAL_BUS_ERR_TIMEOUT = -2,
    HAL_BUS_ERR_OVERRUN = -3
} hal_bus_status_t;

/* Інтерфейс шини: структура з покажчиком на функцію передачі */
typedef struct hal_i2c_interface {
    hal_bus_status_t (*transfer)(struct hal_i2c_interface *self,
                                 uint8_t dev_addr,
                                 const uint8_t *tx_buf, size_t tx_len,
                                 uint8_t *rx_buf, size_t rx_len);
    void *driver_ctx;
} hal_i2c_interface_t;

/* Драйвер периферійного пристрою */
typedef struct {
    hal_i2c_interface_t *bus;
    uint8_t device_address;
    int16_t last_raw_value;
} ambient_sensor_t;

hal_bus_status_t ambient_sensor_read(ambient_sensor_t *dev, int16_t *output) {
    uint8_t reg = 0x02; /* Регістр даних */
    uint8_t raw_data[2] = {0};

    hal_bus_status_t status = dev->bus->transfer(dev->bus, dev->device_address,
                                                 &reg, 1, raw_data, 2);
    if (status != HAL_BUS_OK) {
        return status;
    }

    *output = (int16_t)((raw_data[0] << 8) | raw_data[1]);
    dev->last_raw_value = *output;
    return HAL_BUS_OK;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>

namespace hal {

enum class BusStatus : int8_t {
    Ok = 0,
    ErrNack = -1,
    ErrTimeout = -2,
    ErrOverrun = -3
};

class II2cInterface {
public:
    virtual ~II2cInterface() = default;
    virtual BusStatus transfer(uint8_t dev_addr,
                               std::span<const uint8_t> tx,
                               std::span<uint8_t> rx) = 0;
};

} // namespace hal

namespace devices {

class AmbientSensor {
public:
    explicit AmbientSensor(hal::II2cInterface& bus, uint8_t dev_addr) noexcept
        : bus_(bus), dev_addr_(dev_addr), last_raw_value_(0) {}

    [[nodiscard]] std::expected<int16_t, hal::BusStatus> read_value() {
        const uint8_t reg = 0x02;
        const std::span<const uint8_t> tx{&reg, 1};
        uint8_t raw[2] = {0, 0};
        const std::span<uint8_t> rx{raw, 2};

        const hal::BusStatus status = bus_.transfer(dev_addr_, tx, rx);
        if (status != hal::BusStatus::Ok) {
            return std::unexpected(status);
        }

        const auto val = static_cast<int16_t>((raw[0] << 8) | raw[1]);
        last_raw_value_ = val;
        return val;
    }

    [[nodiscard]] int16_t last_value() const noexcept { return last_raw_value_; }

private:
    hal::II2cInterface& bus_;
    uint8_t dev_addr_;
    int16_t last_raw_value_;
};

} // namespace devices
```
:::

У фізичній прошивці мікроконтролера метод `transfer` буде звертатися до регістрів `I2C1->DR` або викликати функції SDK. У тестовому середовищі на комп'ютері замість реального заліза підставляється програмний мок, що імітує віртуальний банк регістрів у пам'яті. Повний приклад такого стенда з ін'єкцією збоїв наведено в [повному проекті тестового каркаса з емуляцією датчика](root:sf-devices/nalahodzhennia-na-khosti/proj-sensor-mock-framework.md).

---

## AddressSanitizer (ASan): анатомія тіньової пам'яті та детекція пам'яттєвих аварій

Найбільш підступні помилки мов C та C++ у вбудованих системах пов'язані з пам'яттю: вихід за межі масивів (Buffer Overflow), доступ до локальних змінних після завершення функції (Use-After-Return) та використання пам'яті після її звільнення (Use-After-Free). Компілятори за замовчуванням не генерують жодних перевірок меж масивів заради максимальної швидкодії.

**AddressSanitizer** (ASan) — це інструмент динамічного аналізу, розроблений для швидкого виявлення помилок пам'яті з мінімальними накладними витратами (сповільнення виконання приблизно у 2 рази, збільшення споживання RAM приблизно на 70%). Він складається з двох фундаментальних компонентів:
1. **Інструментація компілятора**: компілятор під час створення машинного коду додає захисні зони (**Redzones**) довкола всіх стекових і глобальних масивів, а також вставляє перевірку стану пам'яті перед кожною операцією читання чи запису за покажчиком.
2. **Бібліотека часу виконання (Runtime library)**: підміняє стандартні функції виділення пам'яті (`malloc`, `free`, оператори `new`/`delete`), оточуючи кожен блок купи захисними отруєними зонами та керуючи карантином звільненої пам'яті.

### Принцип роботи Shadow Memory

AddressSanitizer відображає кожен байт віртуального адресного простору програми на так звану **тіньову пам'ять** (Shadow Memory). Співвідношення фіксоване: **8 байтів звичайної пам'яті кодуються 1 байтом тіньової пам'яті**.

Оскільки адреси пам'яті вирівняні за 8 байтами, пряме лінійне відображення обчислюється однією операцією бітового зсуву та додавання бази:

```
Shadow_Address = (App_Address >> 3) + Shadow_Offset
```

Для 64-бітної архітектури Linux x86-64 значення `Shadow_Offset` зазвичай дорівнює `0x7fff8000` (або `0x00007fff8000`).

![Структура Shadow Memory та виявлення переповнення буфера через Redzone](/root/eng/sf-devices/nalahodzhennia-na-khosti/img/asan-shadow-memory.svg)
*Кожні 8 байтів пам'яті програми кодуються 1 байтом у Shadow Memory: 0x00 — блок повністю валідний, 0x01..0x07 — доступні перші k байтів, від'ємні значення (0xFA..0xFF) позначають отруєні захисні зони Redzone.*

### Значення байтів тіньової пам'яті

Один байт тіні описує доступність відповідного 8-байтового блоку:
- **`0x00`**: усі 8 байтів доступні для читання та запису.
- **`0x01` – `0x07`**: доступні лише перші `k` байтів, а решта `8 - k` байтів заблоковані. Це виникає, коли розмір масиву чи структури не кратний 8. Наприклад, для масиву з 19 байтів перші два 8-байтові блоки мають тіньові значення `0x00`, а третій блок (де лежать останні 3 байти) має тіньове значення `0x03`.
- **Від'ємні значення (`0x80` – `0xFF`)**: блок повністю «отруєний» (poisoned), звернення до нього заборонено:
  - `0xFA` — червона зона стека (Stack left/right redzone).
  - `0xFB` — червона зона глобальної змінної (Global redzone).
  - `0xFD` — звільнена пам'ять купи (Heap Use-After-Free).
  - `0xFE` — червона зона виділеної купи (Heap redzone).

### Інструментація доступу до пам'яті

Щойно ви компілюєте код із прапорцем `-fsanitize=address`, компілятор перед кожним розіменуванням покажчика вставляє перевірку.

Погляньмо, як компілятор транслює простий запис у пам'ять:

:::tabs
```c
/* Вихідний код на C */
void store_val(int *address, int val) {
    *address = val;
}
```
```cpp
// Вихідний код на C++
void store_val(int *address, int val) noexcept {
    *address = val;
}
```
:::

Компілятор перетворює цей доступ на інструментований блок перевірки стану тіні:

:::tabs
```c
/* Інструментований компілятором C-код */
void store_val_instrumented(int *address, int val) {
    int8_t *shadow = (int8_t*)(((uintptr_t)address >> 3) + 0x7fff8000);
    int8_t shadow_val = *shadow;
    if (shadow_val != 0) {
        int8_t last_byte = (int8_t)((uintptr_t)address & 7);
        if (last_byte >= shadow_val) {
            __builtin_trap(); /* Негайний краш і звіт ASan */
        }
    }
    *address = val;
}
```
```cpp
// Інструментований компілятором C++ код
void store_val_instrumented(int *address, int val) noexcept {
    auto *shadow = reinterpret_cast<int8_t*>(((reinterpret_cast<uintptr_t>(address) >> 3) + 0x7fff8000));
    const int8_t shadow_val = *shadow;
    if (shadow_val != 0) {
        const auto last_byte = static_cast<int8_t>(reinterpret_cast<uintptr_t>(address) & 7);
        if (last_byte >= shadow_val) {
            __builtin_trap(); // Негайний краш і звіт ASan
        }
    }
    *address = val;
}
```
:::

У машинному коді x86-64 ця перевірка займає лише 3–4 інструкції (`shr`, `mov`, `test`, `jne`), що забезпечує колосальну швидкодію порівняно з повною емуляцією процесора.

---

## UndefinedBehaviorSanitizer (UBSan): пошук прихованих мін оптимізатора

У мовах C та C++ стандарт визначає великий клас операцій як **невизначену поведінку** (Undefined Behavior, UB). Головна небезпека UB полягає не в тому, що процесор зламається, а в тому, як сучасний оптимізуючий компілятор трактує стандарт. Оптимізатор GCC або Clang виходить із припущення: *програміст ніколи не пише код, що викликає UB*. Якщо певна математична умова може стати істинною лише в разі виникнення UB, компілятор просто видаляє всю гілку перевірки як недосяжну.

**UndefinedBehaviorSanitizer** (UBSan) інструментує вихідний код перевірками арифметичних операцій, розіменувань та бітових зсувів безпосередньо перед їх виконанням.

Ключові дефекти вбудованого коду, які виявляє UBSan:

1. **Знакове переповнення цілих чисел (`-fsanitize=signed-integer-overflow`)**:
   У C переповнення беззнакового числа (`uint32_t`) строго визначене як операція за модулем 2³². Але переповнення знакового числа (`int32_t`) — це UB.
   Приклад критичного багу в алгоритмі калібрування:

:::tabs
```c
int32_t scale_raw_value(int32_t raw, int32_t coeff) {
    /* Якщо raw * coeff перевищує INT32_MAX, виникає UB */
    int32_t scaled = raw * coeff;
    if (scaled < 0) { /* Цю перевірку оптимізатор може повністю видалити! */
        return 0;
    }
    return scaled / 1000;
}
```
```cpp
constexpr int32_t scale_raw_value(int32_t raw, int32_t coeff) noexcept {
    // Якщо raw * coeff перевищує INT32_MAX, виникає UB
    const int32_t scaled = raw * coeff;
    if (scaled < 0) { // Цю перевірку оптимізатор може повністю видалити!
        return 0;
    }
    return scaled / 1000;
}
```
:::

   UBSan миттєво генерує попередження: `runtime error: signed integer overflow: 50000 * 50000 cannot be represented in type 'int'`.

2. **Невалідні бітові зсуви (`-fsanitize=shift`)**:
   Зсув числа на кількість бітів, що дорівнює або перевищує розрядність типу (наприклад, `1U << 32` для 32-бітного числа), або зсув на від'ємне число (`val << -1`) є суворим UB. На мікроконтролерах ARM апаратний блок зсуву бере лише молодші 5 бітів аргументу (виконуючи `val << (shift & 31)`), через що `1U << 32` перетворюється на `1U << 0 = 1`. UBSan ловить такі помилки на хості до того, як вони потраплять у прошивку.

3. **Розіменування незіставлених покажчиків (`-fsanitize=alignment`)**:
   Зчитування 32-бітного числа `uint32_t` за адресою, не кратною 4 (наприклад, `0x20000003`), на архітектурі ARM Cortex-M0 або Cortex-M0+ викликає апаратне переривання `HardFault` (оскільки ядро не має апаратної підтримки unaligned access). На процесорах x86-64 такий доступ підтримується апаратно і зазвичай проходить непоміченим. UBSan інструментує кожне розіменування перевіркою молодших бітів адреси й попереджає про небезпечний доступ: `runtime error: load of misaligned address 0x... for type 'uint32_t', which requires 4 byte alignment`.

4. **Розіменування нульових покажчиків та невалідні посилання (`-fsanitize=null`)**:
   Перехоплює спроби передачі або читання через `nullptr`.

5. **Вихід за межі діапазону перелічень (Enum Out of Bounds) (`-fsanitize=enum`)**:
   Виявляє ситуації, коли в змінну типу `enum` записується ціле число, для якого немає відповідного іменованого значення (наприклад, стан FSM, отриманий із пошкодженого пакета UART).

---

## Інтерактивне налагодження: GDB на хості проти апаратного JTAG

Налагодження коду через фізичний інтерфейс SWD або JTAG з використанням серверів на кшталт OpenOCD чи J-Link GDB Server неминуче стикається з затримками передачі даних через USB. Зчитування стека викликів або дампу пам'яті розміром у кілька кілобайтів займає секунди.

На хості відлагоджувач GDB працює безпосередньо з системними викликами ядра ОС, що дає миттєвий відгук і доступ до розширеного арсеналу команд:

### Зворотне трасування та інспекція стека
Команда `backtrace full` миттєво розгортає повне дерево викликів із відображенням значень усіх локальних змінних на кожному рівні вкладеності:

```gdb
(gdb) backtrace full
#0  sensor_parse_packet (ctx=0x7fffffffd430, payload=0x7fffffffd450 "\002", len=12) at sensor_parser.c:48
        calculated_crc = 0xAA
        packet_crc = 0xAB
        temp_buffer = {0, 0, 0, 0}
#1  0x00005555555552a4 in sensor_process_event (event=EVENT_DATA_READY) at sensor_manager.c:112
        status = DRIVER_OK
#2  0x00005555555553b1 in main () at test_runner.c:25
```

### Інтеграція GDB з санітайзерами
За замовчуванням санітайзери під час виявлення помилки друкують звіт у консоль і викликають `exit(1)` або `abort()`. Щоб відлагоджувач GDB автоматично зупиняв виконання програми **в точці виникнення дефекту** (до того, як процес завершиться), встановлюють змінну оточення `ASAN_OPTIONS`:

```bash
export ASAN_OPTIONS="abort_on_error=1:disable_coredump=0"
gdb ./my_host_test
(gdb) run
```

Коли ASan зафіксує невалідний доступ, він згенерує сигнал `SIGABRT`. GDB миттєво зупинить потік на проблемному рядку коду, дозволяючи вам дослідити змінні, регістри та адреси тіньової пам'яті через виклик діагностичних функцій:

```gdb
(gdb) print __asan_describe_address(target_ptr)
```

---

## Автоматизація в CI/CD: Valgrind Memcheck та звітність покриття (gcov/lcov)

AddressSanitizer вирішує практично всі задачі контролю меж пам'яті, але має одну сліпу зону: він **не відстежує читання неініціалізованої пам'яті** всередині вже виділеного валідного блоку. Якщо ви виділили масив із 10 елементів на стеку і прочитали `array[3]`, не записавши туди значення, ASan промовчить, оскільки доступ відбувся в межах дозволеної пам'яті.

### Valgrind Memcheck: відстеження неініціалізованих бітів

Інструмент **Valgrind Memcheck** працює через динамічну двійкову трансляцію (JIT). Він підтримує так звані **V-bits (Value bits)** для кожного окремого біта пам'яті та регістрів процесора (0 — біт ініціалізований, 1 — біт містить випадкове сміття), а також **A-bits (Address bits)** для валідності адрес.

Memcheck генерує попередження лише тоді, коли неініціалізоване значення безпосередньо впливає на логіку програми — наприклад, бере участь в умові розгалуження `if` або передається системному виклику:

```bash
valgrind --leak-check=full --track-origins=yes ./my_host_test
```

Приклад звіту Valgrind про читання неініціалізованого поля структури конфігурації:
```text
[Звіт Valgrind про читання неініціалізованої пам'яті]
Conditional jump or move depends on uninitialised value(s)
   at 0x1091A4: sensor_configure (sensor_driver.c:34)
   by 0x1092F0: test_sensor_setup (test_runner.c:45)
 Uninitialised value was created by a stack allocation
   at 0x109280: test_sensor_setup (test_runner.c:38)
```

### Аналіз покриття коду (gcov та lcov)

Справжня цінність модульного тестування полягає у вимірюванні того, які саме шляхи виконання коду були реально перевірені. Інструменти `gcov` та `lcov` дозволяють з точністю до рядка й окремої умови побудувати карту покриття.

Для генерації профілю покриття код компілюється з прапорцем `--coverage` (еквівалент `-fprofile-arcs -ftest-coverage`):

```bash
gcc -Wall -O0 -g --coverage sensor_driver.c test_runner.c -o test_runner
./test_runner
lcov --capture --directory . --output-file coverage.info
genhtml coverage.info --output-directory coverage_html
```

Під час компіляції створюються файли `.gcno` (структура графів базових блоків), а під час виконання тестів — файли `.gcda` (лічильники проходження кожної дуги графа).

У вбудованих системах критично важливим є розрізнення двох типів покриття:
1. **Покриття рядків (Line Coverage / Statement Coverage)**: показує, чи виконувався рядок коду хоча б один раз.
2. **Покриття гілок (Branch Coverage)**: показує, чи були перевірені **всі можливі наслідки** кожної умови `if` або `switch` (істинне та хибне значення).

Розгляньмо умовний вираз:

:::tabs
```c
if (is_sensor_ready && retry_count < 3) {
    read_data();
} else {
    handle_error();
}
```
```cpp
if (is_sensor_ready && retry_count < 3) {
    read_data();
} else {
    handle_error();
}
```
:::

Якщо в тестах перевірити лише випадок повної готовності давача (`true && true`) та випадок помилки (`false`), лінійне покриття покаже 100%, але гілка, де `is_sensor_ready == true`, а лічильник перевищено `retry_count >= 3`, залишиться непокритою. Аналіз `branch coverage` у звітах `lcov` виявляє такі прогалини.

![Автоматизований конвеєр перевірки вбудованого коду в CI/CD](/root/eng/sf-devices/nalahodzhennia-na-khosti/img/ci-coverage-pipeline.svg)
*Повний цикл верифікації в CI/CD: збірка з санітайзерами, прогон швидких тестів, перевірка Valgrind на неініціалізовані дані та жорсткий шлюз за критерієм покриття гілок.*

---

## Worked-Example: виявлення трьох критичних багів у драйвері цифрового датчика

Продемонструймо потужність хост-налагодження на реалістичному прикладі. Наведений нижче модуль обробки телеметрії цифрового барометра-термометра містить три приховані дефекти, типові для C/C++ прошивок:
1. **Stack Buffer Overflow**: вихід за межі локального стекового масиву ковзного середнього під час заповнення історії.
2. **Signed Integer Overflow**: переповнення 32-бітного знакового числа під час розрахунку тиску за поліномом компенсації.
3. **Uninitialized Memory Read**: використання неініціалізованого прапорця стану фільтра.

### Реалізація драйвера та тестового сценарію

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define HISTORY_DEPTH 4

typedef struct {
    int32_t history[HISTORY_DEPTH];
    uint8_t count;
    bool is_calibrated; /* Якщо не ініціалізувати — сміття на стеку */
} telemetry_filter_t;

/* Обчислення тиску в Паскалях за формулою компенсації */
int32_t calculate_compensated_pressure(int32_t raw_adc, int32_t calib_p1, int32_t calib_p2) {
    /* БАГ 1 (UBSan): Знакове переповнення при великих значеннях raw_adc та calib_p1 */
    int32_t intermediate = raw_adc * calib_p1; 
    int32_t pressure_pa = (intermediate / 100) + calib_p2;
    return pressure_pa;
}

/* Додавання заміру до фільтра ковзного середнього */
void telemetry_filter_add(telemetry_filter_t *filter, int32_t sample) {
    /* БАГ 2 (ASan): Відсутність захисту від перевищення індексу масиву */
    filter->history[filter->count] = sample; 
    filter->count++;
}

int32_t telemetry_filter_get_average(const telemetry_filter_t *filter) {
    /* БАГ 3 (Valgrind): Перевірка неініціалізованого поля is_calibrated */
    if (!filter->is_calibrated) {
        return 0;
    }

    if (filter->count == 0) {
        return 0;
    }

    int64_t sum = 0;
    uint8_t limit = filter->count > HISTORY_DEPTH ? HISTORY_DEPTH : filter->count;
    for (uint8_t i = 0; i < limit; ++i) {
        sum += filter->history[i];
    }
    return (int32_t)(sum / limit);
}

int main(void) {
    printf("=== Запуск демонстраційного драйвера ===\n");

    /* Тест 1: Перевірка формули тиску (викликає Signed Integer Overflow) */
    int32_t p = calculate_compensated_pressure(60000, 50000, 101325);
    printf("Обчислений тиск: %d Па\n", p);

    /* Тест 2: Заповнення фільтра (викликає Stack Buffer Overflow та Uninitialized Read) */
    telemetry_filter_t filter;
    /* Навмисно не викликаємо memset, щоб поля count та is_calibrated містили сміття */
    filter.count = 0; 
    /* filter.is_calibrated не ініціалізовано! */

    for (int i = 0; i < 6; ++i) { /* 6 ітерацій при розмірі масиву 4! */
        telemetry_filter_add(&filter, 1000 + i * 10);
    }

    int32_t avg = telemetry_filter_get_average(&filter);
    printf("Середній тиск: %d\n", avg);

    return 0;
}
```
```cpp
#include <cstdint>
#include <array>
#include <numeric>
#include <span>
#include <iostream>
#include <optional>

namespace telemetry {

constexpr size_t HistoryDepth = 4;

class TelemetryFilter {
public:
    TelemetryFilter() = default; // Члени ініціалізуються значеннями за замовчуванням

    // Метод з навмисно закладеним багом виходу за межі для демонстрації ASan
    void add_sample_buggy(int32_t sample) {
        // Прямий доступ за сирим індексом без перевірки розміру
        history_buffer_[count_] = sample;
        ++count_;
    }

    // Безпечний ідіоматичний метод C++
    bool add_sample_safe(int32_t sample) noexcept {
        if (count_ >= HistoryDepth) {
            return false;
        }
        history_buffer_[count_++] = sample;
        return true;
    }

    [[nodiscard]] std::optional<int32_t> get_average() const noexcept {
        if (!is_calibrated_ || count_ == 0) {
            return std::nullopt;
        }
        const size_t limit = std::min(count_, HistoryDepth);
        const int64_t sum = std::accumulate(history_buffer_.begin(),
                                            history_buffer_.begin() + limit,
                                            int64_t{0});
        return static_cast<int32_t>(sum / limit);
    }

    void set_calibrated(bool state) noexcept { is_calibrated_ = state; }

private:
    std::array<int32_t, HistoryDepth> history_buffer_{};
    size_t count_{0};
    bool is_calibrated_{false};
};

[[nodiscard]] int32_t calculate_pressure_buggy(int32_t raw_adc, int32_t calib_p1, int32_t calib_p2) noexcept {
    // Навмисне знакове переповнення (демонстрація UBSan)
    const int32_t intermediate = raw_adc * calib_p1;
    return (intermediate / 100) + calib_p2;
}

[[nodiscard]] constexpr int32_t calculate_pressure_safe(int32_t raw_adc, int32_t calib_p1, int32_t calib_p2) noexcept {
    // Безпечне обчислення через 64-бітний проміжний тип
    const auto intermediate = static_cast<int64_t>(raw_adc) * calib_p1;
    return static_cast<int32_t>((intermediate / 100) + calib_p2);
}

} // namespace telemetry

int main() {
    std::cout << "=== Запуск демонстраційного C++20 драйвера ===\n";

    // Тест 1: Знакове переповнення
    const int32_t p = telemetry::calculate_pressure_buggy(60000, 50000, 101325);
    std::cout << "Обчислений тиск: " << p << " Па\n";

    // Тест 2: Вихід за межі масиву
    telemetry::TelemetryFilter filter;
    filter.set_calibrated(true);

    for (int i = 0; i < 6; ++i) {
        filter.add_sample_buggy(1000 + i * 10);
    }

    if (const auto avg = filter.get_average()) {
        std::cout << "Середній тиск: " << *avg << "\n";
    }

    return 0;
}
```
:::

### Результати перевірки санітайзерами

#### 1. Запуск під UndefinedBehaviorSanitizer
Компілюємо з перевіркою UB:
```bash
clang -fsanitize=undefined telemetry_driver.c -o test_ubsan
./test_ubsan
```
Вивід компілятора фіксує переповнення на точному рядку коду:
```text
telemetry_driver.c:16:35: runtime error: signed integer overflow: 60000 * 50000 cannot be represented in type 'int'
SUMMARY: UndefinedBehaviorSanitizer: undefined-behavior telemetry_driver.c:16:35
```

#### 2. Запуск під AddressSanitizer
Компілюємо з перевіркою пам'яті:
```bash
clang -fsanitize=address -g telemetry_driver.c -o test_asan
./test_asan
```
Під час виконання п'ятої ітерації циклу (`i = 4`), коли програма намагається записати елемент `filter->history[4]` (при розмірі масиву 4 елементи, тобто індекси 0..3), AddressSanitizer миттєво перериває процес:

```text
[Звіт AddressSanitizer про переповнення стекового буфера]
ERROR: AddressSanitizer: stack-buffer-overflow on address 0x7ffd98b04ea0
WRITE of size 4 at 0x7ffd98b04ea0 thread T0
    #0 in telemetry_filter_add telemetry_driver.c:24
    #1 in main telemetry_driver.c:54

Address 0x7ffd98b04ea0 is located in stack of thread T0 at offset 48 in frame
    #0 in main telemetry_driver.c:42

  This frame has 1 object(s):
    [32, 48) 'filter' <== Memory access at offset 48 overflows this variable
Shadow bytes around the buggy address:
  0x100033158970: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
  0x100033158980: f1 f1 f1 f1 00 00 f3 f3 00 00 00 00 00 00 00 00
  0x100033158990: 00 00 00 00 f3 f3 f3 f3 00 00 00 00 00 00 00 00
Shadow byte legend (one shadow byte represents 8 application bytes):
  Addressable:           00
  Stack left redzone:    f1
  Stack right redzone:   f3
```
Звіт ASan наочно демонструє, що доступ за зміщенням 48 байтів потрапив у байт тіні `f3` (Stack right redzone) — захисну зону, яку компілятор створив праворуч від структури `filter`.

#### 3. Запуск під Valgrind Memcheck
Компілюємо чистий бінарник без ASan і запускаємо під Valgrind:
```bash
gcc -g telemetry_driver.c -o test_native
valgrind --track-origins=yes ./test_native
```
Valgrind фіксує читання неініціалізованої змінної в функції `telemetry_filter_get_average`:
```text
[Звіт Valgrind про читання неініціалізованого значення]
Conditional jump or move depends on uninitialised value(s)
   at 0x1091F8: telemetry_filter_get_average (telemetry_driver.c:30)
   by 0x109312: main (telemetry_driver.c:57)
 Uninitialised value was created by a stack allocation
   at 0x109270: main (telemetry_driver.c:42)
```

На фізичному мікроконтролері без MMU та санітайзерів ці три помилки призвели б до тихих спотворень оперативної пам'яті, дефектних показників датчика або періодичних безпричинних перезавантажень ядра. На хості всі три дефекти локалізуються за 200 мілісекунд з точністю до рядка у вихідному файлі.

---

## Інженерні межі: де закінчується хост-налагодження

Попри колосальну швидкість і діагностичну силу хост-тестування, воно не є повною заміною випробувань на реальному залізі. Інженер повинен чітко розрізняти межі застосовності обох рівнів:

1. **Що слід на 100% тестувати на хості**:
   - Математичні алгоритми, цифрову фільтрацію, розрахунок контрольних сум (CRC, Fletcher, Adler).
   - Парсери бінарних пакетів та текстових протоколів (перевірка на переповнення буферів, невалідні заголовки, фаззинг).
   - Логіку кінцевих автоматів (FSM), таблиці переходів станів.
   - Бізнес-правила системи та сценарії обробки відмов (NACK шини, обрив зв'язку, перевищення таймаутів).

2. **Що неможливо перевірити на хості**:
   - **Жорсткі часові характеристики реального часу (Hard Real-Time)**: на хості операційна система загального призначення керує планувальником потоків, тому час відгуку варіюється від мікросекунд до мілісекунд. Перевірку джиттеру переривань та часу реакції на зовнішній фронт сигналу проводять лише на чипі за допомогою логічного аналізатора чи осцилографа.
   - **Апаратні дефекти кремнію (Silicon Errata)**: помилки в реалізації DMA або SPI контролерів конкретної ревізії мікроконтролера не відображаються у віртуальному моку.
   - **Фізичний рівень сигналів**: аналогові шуми, недостатня підтяжка ліній I2C (Pull-Up резистори), дзвін на довгих лініях SPI та падіння напруги живлення під час увімкнення радіомодуля вимагають фізичного вимірювання на платі.

Найбільш ефективна інженерна стратегія — **дворівнева піраміда тестування**: 90% часу розробки присвячується написанню чистого коду з тестами на хості під ASan, UBSan та Valgrind у безперервному CI-конвеєрі, а фінальні 10% часу відводяться на інтеграційну валідацію на реальному апаратному стенді.
