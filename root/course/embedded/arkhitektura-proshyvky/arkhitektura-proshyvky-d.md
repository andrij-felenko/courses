# Архітектура прошивки: шари, події, межі модулів

<preknowlist>
- [Super-loop](root:embedded/super-loop-limits) — межі лінійного неблокуючого циклу з millis(), комбінаторне зростання спагеті-прапорців.
- [Регістри периферії та HAL](root:embedded/hal-ll-registers) — прямий доступ до регістрів мікроконтролера проти переносних апаратних абстракцій.
- [Модель модуля](root:sf-devices/module-model) — відокремлення інтерфейсу від реалізації, приховування внутрішнього стану та інкапсуляція.
- [Шарова архітектура](root:sf-apps/layered-architecture) — організація коду за ієрархічними рівнями відповідальності з односпрямованим потоком залежностей.
- [Порти й адаптери](root:sf-apps/hexagonal-architecture) — інверсія залежностей та ізоляція бізнес-логіки від деталей периферійних інтерфейсів.
</preknowlist>

Команда інженерів готує до серійного виробництва промисловий логер вібрації та мікроклімату для насосних станцій. Прототип працює бездоганно: один файл `main.c` на 3000 рядків ініціалізує тактування `RCC`, напряму конфігурує регістри `I2C1->CR1`, зчитує покази акселерометра всередині головного циклу, розраховує середньоквадратичне відхилення, формує пакет і записує його у зовнішню флеш-пам'ять через виклики `HAL_SPI_Transmit(&hspi2, ...)`. Коли через дефіцит компонентів фабрика змінює апаратну ревізію — мікроконтролер STM32F401 замінюють на ESP32-S3, а замість давача температури SHT30 встановлюють BME280 на іншій шині — проєкт раптово зупиняється на чотири місяці.

Прямі виклики вендорних функцій та звернення до регістрів конкретного чипа виявляються розмазаними по всіх 3000 рядках. Математика розрахунку спектра вібрації намертво прив'язана до формату буфера DMA конкретного АЦП. Спроба протестувати логіку аварійного вимкнення при критичному перегріві вимагає фізичного нагрівання плати термофеном на лабораторному столі, бо скомпілювати цей код на комп'ютері розробника під керуванням x86-64 Linux чи Windows неможливо: компілятор GCC вимагає апаратних заголовків `stm32f4xx.h`.

Ця катастрофа — класичний наслідок «монолітної спагеті-прошивки». Єдиний спосіб захистити вбудований продукт від апаратних змін, забезпечити безперервне автоматичне тестування (CI/CD) та зберегти керованість кодової бази при зростанні команди — це сувора **шарувата архітектура** (*Layered Firmware Architecture*) з чіткими межами модулів та подійно-орієнтованою взаємодією.

![Порівняння монолітної та модульної зв'язності](/root/course/embedded/arkhitektura-proshyvky/img/monolith-vs-modular-coupling.svg)
*Ліворуч — монолітний код із хаотичними зв'язками між бізнес-логікою, регістрами та драйверами, де зміна будь-якого компонента руйнує всю систему. Праворуч — модульна архітектура з односпрямованим потоком викликів, яка дозволяє тестувати 100% логіки на хостовому ПК.*

---

### Анатомія монолітного коду: чому спагеті вбиває вбудовані проєкти

У типовому монолітному проєкті весь життєвий цикл системи концентрується в одній точці — нескінченному циклі `while(1)`. Усередині цього циклу одночасно вирішуються чотири принципово різні завдання, які за своєю природою належать до різних інженерних доменів:
1. **Низькорівневе маніпулювання апаратурою**: встановлення бітів у регістрах `GPIOA->BSRR`, перевірка прапорців готовності `USART_SR_RXNE`, керування лініями Chip Select (CS) через пряме смикання виводів.
2. **Протокольний обмін з мікросхемами**: надсилання послідовностей ініціалізаційних байтів у регістри конфігурації датчика, розрахунок контрольних сум CRC-8, очікування стабілізації живлення через блокуючі затримки `HAL_Delay()`.
3. **Обробка та фільтрація даних**: відсікання шумів, калібрувальні коефіцієнти, перетворення «сирих» кодів АЦП у градуси Цельсія, паскалі чи g-сили.
4. **Бізнес-правила системи**: ухвалення рішень про перехід у глибокий сон, генерація аварійних тривог, протоколи зв'язку з хмарою, збереження налаштувань.

```
┌─────────────────────────────────────────────────────────────────┐
│ Смертельний клубок монолітного коду (main.c):                   │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ void loop() {                                               │ │
│ │   HAL_I2C_Mem_Read(&hi2c1, 0x68<<1, 0x3B, 1, raw, 6, 100);  │ │
│ │   int16_t ax = (raw[0]<<8)|raw[1]; // Сирі байти датчика    │ │
│ │   float g = (float)ax / 16384.0f;  // Математика сенсора    │ │
│ │   if (g > 2.5f) {                  // Бізнес-політика       │ │
│ │       HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0, GPIO_PIN_SET);   │ │
│ │       Flash_Write_Alert(&g);       // Робота з носієм       │ │
│ │   }                                                         │ │
│ │ }                                                           │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

Коли ці рівні перемішані, виникають три фундаментальні проблеми:

#### 1. Апаратне замкнення (Hardware Lock-in)
Програмна логіка виявляється жорстко «припаяною» до конкретної розводки друкованої плати та конкретної моделі мікроконтролера. Якщо інженер-схемотехнік переніс лінію `CS` флеш-пам'яті з піна `PA4` на `PB12` для оптимізації трасування швидкісних ліній, розробник прошивки змушений вручну шукати та редагувати магічні макроси в десятках файлів.

#### 2. Неможливість модульного тестування (Unit Testing)
У сучасній розробці надійність гарантується автоматичними тестами, які запускаються при кожному коміті в репозиторій (CI/CD пайплайн). У монолітній прошивці функцію розрахунку аварійного стану неможливо протестувати без фізичного мікроконтролера, бо вона всередині викликає `HAL_I2C_Mem_Read`. Спроба скомпілювати цей файл локальним компілятором `gcc` на комп'ютері розробника завершується помилкою: компілятор не знає типів `I2C_HandleTypeDef` та адрес периферійних регістрів.

#### 3. Непередбачувані перегони в перериваннях (ISR Race Conditions)
Коли обробники переривань від таймерів чи UART починають напряму змінювати глобальні змінні бізнес-логіки або викликати важкі функції обчислень, система стає вразливою до важковловлюваних помилок пошкодження пам'яті. Переривання спрацьовує посеред оновлення багатобайтної структури даних, викликаючи випадкові збої під час роботи пристрою у польових умовах.

> 🔧 **Навіщо це.** Шарувата архітектура розриває цей моноліт на незалежні пласти. Кожен шар вирішує виключно одну задачу і надає сусідам чіткий абстрактний інтерфейс. Зміна заліза зачіпає лише найнижчий шар (HAL), зміна моделі сенсора — лише драйвер (BSP), а вся бізнес-логіка, алгоритми фільтрації та протоколи зв'язку залишаються на 100% недоторканими й продовжують виконуватися на будь-якому новому чипі.

Детальніше про те, як індустрія вбудованих систем проходила шлях від монолітних лінійних програм до промислових стандартів OSEK, MISRA та AUTOSAR, читайте у вставці [Еволюція архітектури прошивок: від спагеті 8051 до модульних стандартів](root:embedded/arkhitektura-proshyvky/hist-firmware-spaghetti-to-layers.md).

---

### Чотири канонічні рівні прошивки: HAL, BSP, Services, Application

Канонічна архітектура професійного вбудованого програмного забезпечення поділяється на чотири строго визначені шари з односпрямованим потоком викликів згори донизу.

![Чотирирівнева архітектура вбудованої системи](/root/course/embedded/arkhitektura-proshyvky/img/firmware-layers-stack.svg)
*Чотири рівні абстракції прошивки: прямі виклики функцій відбуваються суворо згори донизу, а сповіщення про події та готовність даних піднімаються вгору через черги та механізми зворотних викликів.*

#### Шар 1: Рівень апаратної абстракції чипа (Hardware Abstraction Layer / HAL & LL)
Шар HAL ізолює мікроконтролерне ядро та його внутрішню периферію.
- **Що робить**: керує регістрами GPIO, контролерами шин I2C, SPI, UART, блоками прямого доступу до пам'яті (DMA), системними таймерами (TIM), аналого-цифровими перетворювачами (ADC) та контролером переривань (NVIC).
- **Головний принцип**: HAL абстрагує **кремній мікроконтролера**, а не зовнішню плату. HAL для шини I2C вміє лише передати масив байтів на задану 7-бітну адресу й прийняти відповідь.
- **Суворе табу**: HAL **нічого не знає** про те, що саме підключено до шини (чи це давач BME280, чи мікросхема годинника реального часу DS3231). HAL не містить жодних формул перетворення температур чи бізнес-логіки.

#### Шар 2: Пакет підтримки плати та драйвери пристроїв (Board Support Package / BSP)
Шар BSP знає конкретну електричну схему вашої друкованої плати та мікросхеми, що на ній розпаяні.
- **Що робить**: реалізує драйвери конкретних зовнішніх компонентів (давачі температури, гіроскопи, мікросхеми Flash-пам'яті, РК-індикатори, контролери заряду батареї, кнопки та реле).
- **Головний принцип**: драйвер BSP приймає як аргумент інтерфейс шини (наприклад, дескриптор `hal_i2c_bus_t`) і спілкується з фізичною мікросхемою за її протоколом регістрів, описаним у datasheet.
- **Рівень абстракції**: шар BSP транслює сирі байти мікросхеми у зрозумілі **фізичні величини**: замість коду АЦП `0x4FA2` функція повертає структуру з температурою `23.85f` у градусах Цельсія або тиском `1013.25f` гПа.
- **Суворе табу**: драйвер BSP не ухвалює рішень, що робити з цими даними (не вмикає обігрівач і не надсилає SMS про аварію).

#### Шар 3: Системні служби та проміжне програмне забезпечення (Services / Middleware)
Рівень служб надає загальносистемні алгоритмічні інструменти, повністю абстраговані від апаратного забезпечення.
- **Що робить**:
  - Кільцеві буфери (*Ring Buffers*) та черги повідомлень (*Event Queues*);
  - Файлові системи для Flash-носіїв (LittleFS, FatFS);
  - Протоколи пакування, серіалізації та контролю цілісності (COBS, CBOR, Protocol Buffers, CRC32);
  - Криптографічні модулі (AES-128, SHA-256, mbedTLS);
  - Диспетчери завдань і планувальники сну (або ядро FreeRTOS / Zephyr);
  - Менеджер енергонезалежних налаштувань (NVM key-value storage) та підсистема журналювання (Logger).
- **Головний принцип**: шар служб є **100% переносним платформонезалежним кодом**. Він однаково компілюється і працює як на 32-бітному ARM Cortex-M4, так і на 64-бітному процесорі x86 чи серверному ARM64.

#### Шар 4: Рівень застосунку та бізнес-логіки (Application Layer)
Вершина піраміди, де зосереджена вся унікальна цінність продукту.
- **Що робить**: реалізує сценарії використання пристрою:
  - Кінцеві автомати режимів роботи (*Application State Machines*);
  - Алгоритми автоматичного регулювання (PID-регулятори температури, стабілізація польоту дрона);
  - Логіку збору, фільтрації та відправки телеметрії за розкладом;
  - Політику реагування на аварії та інтерфейс користувача (HMI).
- **Головний принцип**: застосунок оперує виключно сутностями високого рівня. Він викликає методи BSP (`sensor_read()`, `led_set_mode()`) та користується службами Middleware (`event_queue_post()`, `storage_save_record()`). Застосунок не містить жодного рядка, що згадує регістри процесора чи апаратні адреси шин.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER                               │
│  (Telemetry FSM, PID Controller, Alarm Policies, User Workflows)       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ виклики вниз (Services / BSP)
                                    ▼
┌───────────────────────────────────┴────────────────────────────────────┐
│                       SERVICES & MIDDLEWARE                            │
│  (Event Queue, LittleFS, Packet Serializer, RingBuffer, Crypto, Logs)  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ виклики вниз (BSP API)
                                    ▼
┌───────────────────────────────────┴────────────────────────────────────┐
│                    BOARD SUPPORT PACKAGE (BSP)                         │
│  (BME280 Driver, W25Q Flash Driver, SSD1306 OLED, Power Gauge, Buttons)│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ виклики вниз (HAL Bus Ops)
                                    ▼
┌───────────────────────────────────┴────────────────────────────────────┐
│                HARDWARE ABSTRACTION LAYER (HAL / LL)                   │
│  (GPIO Pins, I2C Master Ops, SPI DMA Engine, UART Driver, NVIC, Clocks)│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ доступ до регістрів
                                    ▼
┌───────────────────────────────────┴────────────────────────────────────┐
│                         PHYSICAL HARDWARE                              │
│       (ARM Cortex-M Silicon, Off-chip Sensors, Flash ICs, Buses)       │
└────────────────────────────────────────────────────────────────────────┘
```

---

### Патерни інкапсуляції в C та C++: як будувати непробивні межі

Архітектура залишається лише малюнком на папері, якщо мова програмування не підтримує примусової ізоляції модулів. Мови C та C++ надають класичні інструменти для побудови жорстких кордонів між шарами: **непрозорі покажчики** (*Opaque Pointers*), **таблиці віртуальних операцій** (*Interface Function Tables*) та **інтерфейсні класи**.

#### 1. Патерн непрозорого покажчика (Opaque Pointer / Handle Pattern) у C
Принцип приховування інформації за Девідом Парнасом (*David Parnas, 1972*) стверджує: модуль повинен відкривати у своєму заголовному файлі лише те, що необхідно для взаємодії, і повністю приховувати структури даних, які можуть змінитися при зміні внутрішньої реалізації.

У мові C заголовочний файл експортує лише неповне оголошення типу структури (Incomplete Type) та покажчик на неї. Вся внутрішня будова структури (адреси шини, проміжні змінні калібрування, дескриптори таймерів) декларується виключно у файлі реалізації `.c`.

:::tabs
```c
// bsp_sensor.h — Публічний заголовок: чистий інтерфейс для шарів вище
#ifndef BSP_SENSOR_H
#define BSP_SENSOR_H

#include <stdbool.h>
#include <stdint.h>

// Неповний тип: клієнтський код не знає розміру й полів структури
typedef struct bsp_sensor_handle bsp_sensor_t;

typedef struct {
    float temperature_c;
    float pressure_kpa;
} bsp_sensor_data_t;

// Функції життєвого циклу
bsp_sensor_t* bsp_sensor_create(uint8_t bus_id, uint8_t i2c_address);
bool bsp_sensor_read_data(bsp_sensor_t* dev, bsp_sensor_data_t* out_data);
void bsp_sensor_destroy(bsp_sensor_t* dev);

#endif // BSP_SENSOR_H
```
```cpp
// bsp_sensor.hpp — Ідіоматичний еквівалент на сучасному C++
#pragma once
#include <cstdint>
#include <optional>
#include <memory>

namespace bsp {

struct SensorData {
    float temperature_c{0.0f};
    float pressure_kpa{0.0f};
};

class ISensor {
public:
    virtual ~ISensor() = default;
    virtual bool init() = 0;
    virtual std::optional<SensorData> read_data() = 0;
};

// Фабрична функція, що повертає унікальний покажчик на інтерфейс
std::unique_ptr<ISensor> create_environment_sensor(uint8_t bus_id, uint8_t i2c_address);

} // namespace bsp
```
:::

У файлі реалізації C структура отримує повне визначення:

:::tabs
```c
// bsp_sensor.c — Приватна реалізація, прихована від застосунку
#include "bsp_sensor.h"
#include <stdlib.h>

struct bsp_sensor_handle {
    uint8_t bus_id;
    uint8_t address;
    int16_t calib_t1;
    int16_t calib_t2;
    uint32_t last_poll_timestamp;
};

bsp_sensor_t* bsp_sensor_create(uint8_t bus_id, uint8_t i2c_address) {
    bsp_sensor_t* dev = (bsp_sensor_t*)malloc(sizeof(bsp_sensor_t));
    if (!dev) return NULL;
    dev->bus_id = bus_id;
    dev->address = i2c_address;
    dev->calib_t1 = 0;
    dev->calib_t2 = 0;
    dev->last_poll_timestamp = 0;
    return dev;
}

bool bsp_sensor_read_data(bsp_sensor_t* dev, bsp_sensor_data_t* out_data) {
    if (!dev || !out_data) return false;
    // Логіка зчитування через HAL-шину з використанням dev->bus_id
    out_data->temperature_c = 24.5f;
    out_data->pressure_kpa = 101.3f;
    return true;
}

void bsp_sensor_destroy(bsp_sensor_t* dev) {
    if (dev) {
        free(dev);
    }
}
```
```cpp
// bsp_sensor.cpp — Приватна реалізація класу в C++
#include "bsp_sensor.hpp"

namespace bsp {

class Bme280Sensor final : public ISensor {
public:
    Bme280Sensor(uint8_t bus_id, uint8_t address)
        : bus_id_(bus_id), address_(address) {}

    bool init() override {
        // Ініціалізація регістрів датчика
        return true;
    }

    std::optional<SensorData> read_data() override {
        SensorData data{
            .temperature_c = 24.5f,
            .pressure_kpa = 101.3f
        };
        return data;
    }

private:
    uint8_t bus_id_;
    uint8_t address_;
    int16_t calib_t1_{0};
    int16_t calib_t2_{0};
};

std::unique_ptr<ISensor> create_environment_sensor(uint8_t bus_id, uint8_t i2c_address) {
    return std::make_unique<Bme280Sensor>(bus_id, i2c_address);
}

} // namespace bsp
```
:::

#### 2. Таблиця операцій віртуальної шини (Interface Ops / Dependency Inversion)
Щоб драйвер пристрою (BSP) не залежав від конкретного вендорного HAL, драйвер підключається до шини не через виклики функцій на кшталт `HAL_I2C_Master_Transmit()`, а через **структуру покажчиків на функції** (таблицю операцій):

:::tabs
```c
// hal_i2c_interface.h — Інверсія залежностей для шини I2C у C
#ifndef HAL_I2C_INTERFACE_H
#define HAL_I2C_INTERFACE_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct {
    bool (*write)(void* user_ctx, uint8_t dev_addr, const uint8_t* data, size_t len);
    bool (*read)(void* user_ctx, uint8_t dev_addr, uint8_t* data, size_t len);
    bool (*write_read)(void* user_ctx, uint8_t dev_addr, const uint8_t* wdata, 
                       size_t wlen, uint8_t* rdata, size_t rlen);
} hal_i2c_ops_t;

typedef struct {
    const hal_i2c_ops_t* ops;
    void* user_ctx; // Вказівник на I2C_HandleTypeDef на STM32 або Mock-об'єкт у тестах
} hal_i2c_bus_t;

#endif // HAL_I2C_INTERFACE_H
```
```cpp
// hal_i2c_interface.hpp — Інтерфейс шини I2C у сучасному C++
#pragma once
#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>

namespace hal {

enum class BusStatus {
    Ok,
    ErrorNack,
    ErrorTimeout
};

class II2cMaster {
public:
    virtual ~II2cMaster() = default;
    virtual std::expected<void, BusStatus> write(uint8_t dev_addr, 
                                                 std::span<const uint8_t> data) = 0;
    virtual std::expected<void, BusStatus> read(uint8_t dev_addr, 
                                                std::span<uint8_t> data) = 0;
    virtual std::expected<void, BusStatus> write_read(uint8_t dev_addr, 
                                                      std::span<const uint8_t> wdata, 
                                                      std::span<uint8_t> rdata) = 0;
};

} // namespace hal
```
:::

Завдяки такій структурі драйвер давача стає **чистим компонентом**: йому байдуже, чи функція `ops->write` смикає апаратний контролер I2C1 мікроконтролера STM32, чи програмний емулятор I2C Bit-Banging на мікроконтролері PIC, чи заповнює масив у пам'яті комп'ютера розробника під час виконання юніт-тесту.

---

### Подійно-орієнтований обмін між шарами (Event-Driven Decoupling)

Традиційний синхронний виклик (коли функція переривання UART викликає парсер, парсер викликає збереження у Flash, а Flash викликає перемальовування дисплея) створює глибокий стек викликів, блокує процесор і призводить до переповнення пам'яті вбудованого чипа.

У подійно-орієнтованій архітектурі (*Event-Driven Architecture*) шари розв'язуються за **часом** і **контекстом виконання**.

![Подійно-орієнтований конвеєр обробки](/root/course/embedded/arkhitektura-proshyvky/img/event-driven-pipeline.svg)
*Генератори подій (переривання від кнопок, таймери, прийом пакетів по UART) публікують компактні події в чергу. Головний цикл послідовно витягує події та викликає зареєстровані диспетчери автоматів станів.*

#### Структура універсальної події
Подія є легковаговим об'єктом фіксованого розміру (зазвичай 8–16 байтів), що складається з ідентифікатора типу події, часової мітки та об'єднання (*union*) корисного навантаження:

:::tabs
```c
// event_types.h
#ifndef EVENT_TYPES_H
#define EVENT_TYPES_H

#include <stdint.h>

typedef enum {
    EVT_ID_NONE = 0,
    EVT_ID_TICK_100MS,
    EVT_ID_BUTTON_CLICK,
    EVT_ID_SENSOR_DATA_READY,
    EVT_ID_ALARM_OVERTEMP,
    EVT_ID_COMMS_PACKET_RX
} event_id_t;

typedef struct {
    event_id_t id;
    uint32_t timestamp_ms;
    union {
        uint8_t button_pin;
        struct {
            float temp_c;
            float pressure_kpa;
        } sensor_payload;
        struct {
            uint16_t len;
            const uint8_t* p_data;
        } rx_packet;
    } data;
} sys_event_t;

#endif // EVENT_TYPES_H
```
```cpp
// event_types.hpp
#pragma once
#include <cstdint>
#include <variant>
#include <span>

namespace events {

enum class EventId : uint16_t {
    None = 0,
    Tick100ms,
    ButtonClick,
    SensorDataReady,
    AlarmOvertemp,
    CommsPacketRx
};

struct SensorPayload {
    float temp_c{0.0f};
    float pressure_kpa{0.0f};
};

struct PacketPayload {
    std::span<const uint8_t> buffer;
};

struct SystemEvent {
    EventId id{EventId::None};
    uint32_t timestamp_ms{0};
    std::variant<std::monostate, uint8_t, SensorPayload, PacketPayload> payload{};
};

} // namespace events
```
:::

#### Потік подій між шарами
1. **Генерація події в ISR**: коли на ніжці мікроконтролера спрацьовує переривання від кнопки, обробник переривання `EXTI0_IRQHandler()` не виконує затримок і не малює графіку на дисплеї. Він лише формує подію `EVT_ID_BUTTON_CLICK` і записує її в потокобезпечну кільцеву чергу за 20–30 тактів процесора:

:::tabs
```c
// Переривання EXTI0 у мові C
void EXTI0_IRQHandler(void) {
    if (EXTI->PR & (1 << 0)) {
        EXTI->PR = (1 << 0); // Скидання прапорця переривання
        sys_event_t evt = {
            .id = EVT_ID_BUTTON_CLICK,
            .timestamp_ms = sys_get_tick_ms(),
            .data.button_pin = 0
        };
        event_queue_post_from_isr(&g_main_queue, &evt);
    }
}
```
```cpp
// Переривання EXTI0 з викликом черги C++
extern "C" void EXTI0_IRQHandler() {
    if (EXTI->PR & (1 << 0)) {
        EXTI->PR = (1 << 0); // Скидання прапорця переривання
        events::SystemEvent evt{
            .id = events::EventId::ButtonClick,
            .timestamp_ms = board::get_tick_ms(),
            .payload = static_cast<uint8_t>(0)
        };
        board::get_main_queue().push_from_isr(evt);
    }
}
```
:::

2. **Диспетчеризація в головному циклі**: головний цикл застосунку витягує події з черги й передає їх у кінцевий автомат:

:::tabs
```c
// main.c — Головний диспетчер у C
int main(void) {
    board_hardware_init();
    event_queue_init(&g_main_queue);
    app_coordinator_init();

    while (1) {
        sys_event_t evt;
        if (event_queue_pop(&g_main_queue, &evt, TIMEOUT_MAX)) {
            app_coordinator_dispatch(&evt);
        } else {
            // Якщо подій немає, переходимо в режим збереження енергії до наступного переривання
            __WFI(); // Wait For Interrupt
        }
    }
}
```
```cpp
// main.cpp — Головний диспетчер у C++
int main() {
    board::init();
    services::EventQueue<32> queue;
    app::Coordinator coordinator;

    while (true) {
        if (auto evt = queue.pop()) {
            coordinator.dispatch(*evt);
        } else {
            asm volatile("wfi"); // Перехід ядра Cortex-M у сон
        }
    }
}
```
:::

Така схема гарантує:
- **Часову розв'язку**: швидкі апаратні переривання ніколи не затримуються тривалою обробкою логіки.
- **Відсутність блокувань**: прошивка не марнує енергію акумулятора в порожніх циклах `delay()`, а спить за інструкцією `__WFI()`, коли черга подій порожня.
- **Ізоляцію модулів**: модуль обробки радіозв'язку не знає, хто згенерував телеметричний пакет — таймер, кнопка користувача чи сигнал аварії. Він лише слухає свій тип подій.

---

### Повний архітектурний каркас модульної прошивки для Cortex-M

Розглянемо реальну структуру проєкту комерційного рівня, призначеного для збірки як під мікроконтролери STM32/Cortex-M через кроскомпілятор `arm-none-eabi-gcc`, так і для запуску модульних тестів на комп'ютері розробника через `gcc`/`clang`.

```
project_root/
├── include/                   [Загальносистемні типи та конфігурація]
│   └── sys_config.h
├── hal/                       [Абстрактні інтерфейси апаратних шин]
│   ├── hal_gpio.h
│   └── hal_i2c.h
├── bsp/                       [Драйвери компонентів плати]
│   ├── bsp_led.h / bsp_led.c
│   └── bsp_bme280.h / bsp_bme280.c
├── services/                  [Платформонезалежні системні служби]
│   ├── event_queue.h / event_queue.c
│   └── ring_buffer.h / ring_buffer.c
├── app/                       [Прикладна бізнес-логіка та FSM]
│   ├── app_fsm.h / app_fsm.c
│   └── app_telemetry.h / app_telemetry.c
└── ports/                     [Платформозалежні реалізації HAL]
    ├── stm32f4/               [Реалізація для реального заліза]
    │   ├── stm32_hal_gpio.c
    │   ├── stm32_hal_i2c.c
    │   └── startup_stm32f401xe.s
    └── host_mock/             [Тестові заглушки для ПК]
        ├── mock_hal_gpio.c
        └── mock_hal_i2c.c
```

#### Крок 1: Оголошення абстракції шини I2C у шарі HAL

:::tabs
```c
// hal/hal_i2c.h
#ifndef HAL_I2C_H
#define HAL_I2C_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef enum {
    HAL_I2C_STATUS_OK = 0,
    HAL_I2C_STATUS_NACK,
    HAL_I2C_STATUS_BUS_ERROR,
    HAL_I2C_STATUS_TIMEOUT
} hal_i2c_status_t;

typedef struct {
    hal_i2c_status_t (*mem_read)(void* ctx, uint8_t dev_addr, uint8_t reg_addr, 
                                 uint8_t* p_data, size_t size);
    hal_i2c_status_t (*mem_write)(void* ctx, uint8_t dev_addr, uint8_t reg_addr, 
                                  const uint8_t* p_data, size_t size);
} hal_i2c_driver_t;

typedef struct {
    const hal_i2c_driver_t* driver;
    void* context;
} hal_i2c_bus_t;

#endif // HAL_I2C_H
```
```cpp
// hal/hal_i2c.hpp
#pragma once
#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>

namespace hal {

enum class I2cError {
    Nack,
    BusError,
    Timeout
};

class II2cBus {
public:
    virtual ~II2cBus() = default;
    virtual std::expected<void, I2cError> mem_read(uint8_t dev_addr, uint8_t reg_addr, 
                                                   std::span<uint8_t> data) = 0;
    virtual std::expected<void, I2cError> mem_write(uint8_t dev_addr, uint8_t reg_addr, 
                                                    std::span<const uint8_t> data) = 0;
};

} // namespace hal
```
:::

#### Крок 2: Драйвер давача температури в шарі BSP

Драйвер BME280 використовує таблицю операцій `hal_i2c_bus_t`. Він виділяє всю пам'ять статично (без виклику `malloc`), що критично для вбудованих систем із жорсткими вимогами до надійності:

:::tabs
```c
// bsp/bsp_bme280.h
#ifndef BSP_BME280_H
#define BSP_BME280_H

#include "hal/hal_i2c.h"

typedef struct bsp_bme280_dev bsp_bme280_t;

typedef struct {
    uint8_t memory_pool[48]; // Статичний буфер для дескриптора
} bsp_bme280_storage_t;

typedef struct {
    float temperature_c;
    float humidity_rh;
    float pressure_hpa;
} bsp_bme280_readings_t;

bsp_bme280_t* bsp_bme280_init(bsp_bme280_storage_t* storage, 
                              const hal_i2c_bus_t* bus, 
                              uint8_t i2c_addr);

bool bsp_bme280_measure(bsp_bme280_t* dev, bsp_bme280_readings_t* out_readings);

#endif // BSP_BME280_H
```
```cpp
// bsp/bsp_bme280.hpp
#pragma once
#include "hal/hal_i2c.hpp"
#include <optional>

namespace bsp {

struct EnvironmentalData {
    float temperature_c{0.0f};
    float humidity_rh{0.0f};
    float pressure_hpa{0.0f};
};

class Bme280Driver {
public:
    Bme280Driver(hal::II2cBus& bus, uint8_t address = 0x76)
        : bus_(bus), address_(address) {}

    bool init();
    std::optional<EnvironmentalData> measure();

private:
    hal::II2cBus& bus_;
    uint8_t address_;
    uint16_t dig_t1_{0};
    int16_t dig_t2_{0};
    int16_t dig_t3_{0};
};

} // namespace bsp
```
:::

#### Крок 3: Реалізація координатора застосунку (Application)

Застосунок зв'язує сенсор з диспетчером подій і реалізує бізнес-правила:

:::tabs
```c
// app/app_coordinator.c
#include "bsp/bsp_bme280.h"
#include "services/event_queue.h"

typedef struct {
    bsp_bme280_t* sensor;
    event_queue_t* queue;
    float temp_limit_c;
} app_context_t;

static app_context_t g_app;

void app_init(bsp_bme280_t* sensor, event_queue_t* queue, float limit_c) {
    g_app.sensor = sensor;
    g_app.queue = queue;
    g_app.temp_limit_c = limit_c;
}

void app_handle_tick_event(void) {
    bsp_bme280_readings_t readings;
    if (bsp_bme280_measure(g_app.sensor, &readings)) {
        if (readings.temperature_c > g_app.temp_limit_c) {
            sys_event_t alert = {
                .id = EVT_ID_ALARM_OVERTEMP,
                .timestamp_ms = 0,
                .data.sensor_payload = {
                    .temp_c = readings.temperature_c,
                    .pressure_kpa = readings.pressure_hpa / 10.0f
                }
            };
            event_queue_post(g_app.queue, &alert);
        }
    }
}
```
```cpp
// app/app_coordinator.cpp
#include "bsp/bsp_bme280.hpp"
#include "services/event_queue.hpp"

namespace app {

class TelemetryCoordinator {
public:
    TelemetryCoordinator(bsp::Bme280Driver& sensor, 
                         services::EventQueue<16>& queue, 
                         float temp_limit_c)
        : sensor_(sensor), queue_(queue), temp_limit_c_(temp_limit_c) {}

    void on_tick() {
        auto readings = sensor_.measure();
        if (readings.has_value() && readings->temperature_c > temp_limit_c_) {
            events::SystemEvent alert{
                .id = events::EventId::AlarmOvertemp,
                .timestamp_ms = 0,
                .payload = events::SensorPayload{
                    .temp_c = readings->temperature_c,
                    .pressure_kpa = readings->pressure_hpa / 10.0f
                }
            };
            queue_.push(alert);
        }
    }

private:
    bsp::Bme280Driver& sensor_;
    services::EventQueue<16>& queue_;
    float temp_limit_c_;
};

} // namespace app
```
:::

Повну робочу збірку цього каркаса з можливістю запуску юніт-тестів на хостовому комп'ютері та детальною інжекцією помилок шини I2C дивіться у практичній вставці [Каркас модульної прошивки для Cortex-M із хостовим тестуванням](root:embedded/arkhitektura-proshyvky/proj-layered-firmware-skeleton.md).

---

### Інженерний компроміс: ціна абстракцій проти ціни негнучкості

У вбудованих системах кожне архітектурне рішення має фізичну ціну у кілобайтах пам'яті Flash, байтах RAM та тактах процесора. Розглянемо реальні накладні витрати шаруватого підходу:

| Параметр | Монолітне спагеті (Прямий доступ) | Шарувата архітектура (HAL + Ops) | Різниця та вплив на систему |
|---|---|---|---|
| **Витрата Flash-пам'яті** | Базова (100%) | +1.5–3.5 КБ | Витрачається на структури дескрипторів та проміжні функції викликів |
| **Витрата RAM** | Базова (глобальні змінні) | +64–256 байтів | Екземпляри дескрипторів `handle` та кільцеві буфери черг подій |
| **Затримка виклику шини** | 1 пряма інструкція `BL` (1–2 такти) | Непрямий виклик `BLX` через покажчик (3–5 тактів) | Різниця < 0.05 мкс при тактовій частоті ядра Cortex-M 72–168 МГц |
| **Час портування на новий чип** | 4–12 тижнів тотального переписування | 1–3 дні на написання нового драйвера HAL | Економія 95% часу інженерної команди |
| **Покриття автоматичними тестами** | 0% (тести лише на платі з осцилографом) | До 95% бізнес-логіки на Host PC (CI/CD) | Усунення 90% прихованих регресійних помилок до виробництва |

#### Правила вибору межі абстракції:
1. **Для швидкісних контурів керування (DSP / FOC-керування двигунами на 50 кГц)**:
   Тут затримка непрямого виклику функції через покажчик у таблиці `ops` є неприпустимою. У таких критичних вузлах використовують **статичний поліморфізм** на етапі компіляції (C++ шаблони або макроси прямого доступу в ізольованому HAL-модулі).
2. **Для стандартних датчиків, шин зв'язку, файлових систем і бізнес-логіки**:
   Накладні витрати у 4 такти процесора на фоні передачі байта по повільній шині I2C (де один біт передається сотні мікросекунд) становлять менше 0.001% загального часу. Тут динамічна абстракція через покажчики є абсолютно виправданою і необхідною.

Шарувата архітектура перетворює розробку прошивки з хаотичного підганяння коду під регістри конкретної плати на професійне конструювання надійних, масштабованих та довговічних інженерних систем.
