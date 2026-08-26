# Чужа бібліотека від виробника

<preknowlist>
- [Драйвер чипа: від регістрової карти до значення у SI](root:embedded/draiver-chypa) — архітектура шарів драйвера, дескриптор пристрою та абстракція шини.
- [Послідовність ініціалізації: порядок, затримки, перевірка](root:embedded/poslidovnist-initsializatsii) — конфігураційні ланцюжки, часові затримки та перевірка готовності чипа.
- [Таймаут, повтор і відмова пристрою](root:embedded/taimaut-povtor-i-vidmova-prystroiu) — стратегії відновлення після комунікаційних збоїв на шині.
- [SPI і I2C як блоки мікроконтролера](root:embedded/spi-i-i2c-iak-bloky-mikrokontrolera) — організація транзакцій, керування лініями та буферизація.
- [Вибір: голий цикл, FreeRTOS, Zephyr](root:embedded/vybir-holyi-tsykl-freertos-zephyr) — контекст виконання задач, квантування часу та планувальник.
</preknowlist>

Коли на друковану плату встановлюють комбінований MEMS-давач довкілля чи складний інерційний модуль (наприклад, Bosch BME680, ST LSM6DSOX або оптичний далекомір Time-of-Flight від STMicroelectronics), розробник відкриває технічний опис мікросхеми (англ. *datasheet*) і виявляє півтори сотні сторінок опису регістрових карт, десятки формул поліноміальної компенсації з 64-бітними цілими числами та закриті алгоритми завантаження бінарних конфігураційних блоків в ASIC. Спроба написати такий драйвер власноруч із нуля забирає тижні на вичитування кожної математичної операції та налагодження калібрування. Виробник чипа пропонує альтернативу — завантажити готовий офіційний SDK (Bosch Sensor API, ST MEMS C Software Drivers чи Texas Instruments DriverLib), який обіцяє зчитування готових фізичних величин викликом двох функцій.

Але щойно цей вендорський C-код напряму інтегрують у багатозадачну прошивку під керуванням FreeRTOS або Zephyr, система стикається з прихованими дефектами: мікроконтролер спонтанно зависає через блокуючий цикл затримки на 100 мілісекунд усередині функції калібрування, високопріоритетні задачі втрачають радіопакети, а пам'ять безповоротно фрагментується через приховані виклики динамічного виділення. Без ретельного інженерного аудиту, архітектурної ізоляції та адаптації під операційну систему сторонній код стає найвразливішим місцем усієї прошивки.

## Анатомія вендорських SDK та драйверів: як вони влаштовані під капотом

Головна інженерна вимога до виробника чипа під час створення офіційного драйвера — максимальна переносність (англ. *portability*). Код виробника повинен без змін компілюватися як для 8-бітного мікроконтролера з тактовою частотою 8 МГц і 2 КБ оперативної пам'яті, так і для 32-бітного ARM Cortex-M чи 64-бітного процесора під керуванням Linux. Щоб досягти повної незалежності від конкретної апаратної архітектури мікроконтролера, розробники SDK відокремлюють апаратно-незалежні розрахунки від фізичного вводу-виводу за допомогою архітектурного шаблону Platform Abstraction Layer (PAL).

Ядро вендорської бібліотеки містить три фундаментальні складові:
1. **Регістрові карти та бітові маски**: константи адрес, бітові зміщення та макроси пакування/розпакування полів (наприклад, конфігурація цифрових фільтрів, дільників частоти вимірювання та режимів живлення).
2. **Алгоритми компенсації та математичної обробки**: перетворення сирих цілочисельних відліків АЦП у нормалізовані фізичні значення (градуси Цельсія, Паскалі, відсотки вологості або g-сили) за заводськими калібрувальними коефіцієнтами (Trim parameters), збереженими в одноразово програмованій пам'яті (OTP) або NVM сенсора.
3. **Дескриптор пристрою з таблицею вказівників на функції**: структура, через яку бібліотека взаємодіє із зовнішнім світом.

![Анатомія вендорського SDK: відокремлення ядра від апаратної платформи](/root/course/embedded/chuzha-biblioteka-vid-vyrobnyka/img/vendor-sdk-anatomy.svg)
*Анатомія вендорського SDK: апаратно-незалежне математичне ядро зв'язується з платформою через покажчики на функції read, write, delay та непрозорий контекст intf_ptr.*

Розглянемо, як виглядає інтерфейсний контракт у сучасних промислових SDK (зокрема Bosch Sensortec Sensor API v4 та STMicroelectronics Standard C Drivers):

:::tabs
```c
/* Типовий Platform Abstraction Layer сучасного вендорського C-драйвера */
typedef int8_t (*sensor_read_fptr_t)(uint8_t reg_addr, uint8_t *read_data, uint32_t len, void *intf_ptr);
typedef int8_t (*sensor_write_fptr_t)(uint8_t reg_addr, const uint8_t *write_data, uint32_t len, void *intf_ptr);
typedef void (*sensor_delay_us_fptr_t)(uint32_t period_us, void *intf_ptr);

struct sensor_dev {
    uint8_t chip_id;            /* Зчитаний ідентифікатор мікросхеми */
    void *intf_ptr;             /* Непрозорий вказівник користувача на контекст шини або об'єкт */
    sensor_read_fptr_t read;    /* Вказівник на системну функцію читання з шини */
    sensor_write_fptr_t write;  /* Вказівник на системну функцію запису в шину */
    sensor_delay_us_fptr_t delay_us; /* Вказівник на системну затримку в мікросекундах */
    
    /* Внутрішній стан чипа: калібрувальні коефіцієнти */
    struct {
        uint16_t dig_t1;
        int16_t  dig_t2;
        int16_t  dig_t3;
    } calib_data;
};
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>

/* C++ відображення вендорського Platform Abstraction Layer */
extern "C" {
    using SensorReadFn = int8_t (*)(uint8_t reg_addr, uint8_t *read_data, uint32_t len, void *intf_ptr);
    using SensorWriteFn = int8_t (*)(uint8_t reg_addr, const uint8_t *write_data, uint32_t len, void *intf_ptr);
    using SensorDelayUsFn = void (*)(uint32_t period_us, void *intf_ptr);

    struct VendorSensorCalib {
        uint16_t dig_t1;
        int16_t  dig_t2;
        int16_t  dig_t3;
    };

    struct VendorSensorDev {
        uint8_t chip_id;
        void *intf_ptr;
        SensorReadFn read;
        SensorWriteFn write;
        SensorDelayUsFn delay_us;
        VendorSensorCalib calib_data;
    };
}
```
:::

Ключовим полем у цій структурі є `void *intf_ptr` (непрозорий контекстний вказівник, англ. *opaque user pointer*). У ранніх версіях бібліотек виробників початку 2010-х років цього поля не існувало: функції `read` та `write` приймали лише адресу регістра, покажчик на буфер та довжину. Така сигнатура робила бібліотеку принципово непридатною для систем, де на одній платі встановлено два або більше однакових давачів на різних I2C-шинах або з різними адресами вибору кристала (Chip Select для SPI). Драйвер не мав можливості зрозуміти, з яким саме фізичним інтерфейсом він працює у даний момент, що змушувало інженерів вдаватися до потворних глобальних змінних стану.

Сучасні вендорські бібліотеки передають `intf_ptr` першим або останнім аргументом у кожен виклик читання, запису та очікування, повертаючи контроль над контекстом назад у системний код розробника.

## Інженерний аудит: приховані загрози та підводні камені

Офіційний статус бібліотеки від виробника мікросхеми часто створює у розробників хибне відчуття повної надійності коду. Проте виробники напівпровідників спеціалізуються на кремнії, а їхні програмні відділи зазвичай орієнтовані на швидке створення демонстраційних прикладів (Proof of Concept) для оціночних плат, а не на стандарти надійності бортового чи медичного програмного забезпечення (MISRA C, ISO 26262, IEC 61508).

Інженерний аудит будь-якої сторонньої бібліотеки перед її включенням у кодову базу проєкту повинен перевіряти чотири критичні зони ризику.

![Чотири головні підводні камені вендорського коду у вбудованих системах](/root/course/embedded/chuzha-biblioteka-vid-vyrobnyka/img/vendor-pitfalls-matrix.svg)
*Чотири головні підводні камені вендорського коду: динамічна пам'ять, блокуючі цикли затримок, глобальний стан та надмірне навантаження на стек.*

### 1. Приховане динамічне виділення пам'яті (malloc / free)

Найнебезпечніша пастка в коді SDK — неявні виклики функцій виділення динамічної пам'яті. Деякі бібліотеки (особливо графічні стеки дисплеїв, складні алгоритми орієнтації Sensor Fusion та стеки криптографії) викликають `malloc()` або `calloc()` під час ініціалізації для створення буферів обробки або математичних матриць.

У критичних вбудованих системах динамічна купа (англ. *heap*) несе катастрофічні ризики:
- **Недетермінований час виконання**: алгоритми виділення пам'яті залежать від поточної карти зайнятості блоків у купі. Час пошуку вільного фрагмента може коливатися від десятків до тисяч тактів CPU.
- **Фрагментація пам'яті (Heap Fragmentation)**: постійне виділення та звільнення дрібних структур різного розміру розбиває купу на дрібні ізольовані острівці. За кілька діб безперервної роботи пристрій вичерпує найбільший суцільний блок пам'яті, і черговий виклик `malloc()` повертає `NULL`, що призводить до аварійної зупинки.
- **Відсутність перевірки результату**: у багатьох зразках вендорського коду повернене значення `malloc` розіменовується без перевірки на нульовий покажчик, викликаючи миттєвий HardFault.

> 🔧 **Навіщо це: аудит таблиці символів.**
> Щоб гарантувати відсутність прихованої динамічної пам'яті у вендорських файлах, перед інтеграцією перевірте об'єктні файли компілятора через утиліту `nm`:
> ```bash
> arm-none-eabi-nm -u vendor_driver.o | grep -E "malloc|free|calloc|realloc"
> ```
> Якщо команда повертає будь-які невизначені символи (прапорець `U`), цей код вимагає негайного виправлення на користь статично виділених дескрипторів, що передаються ззовні через конфігураційну структуру.

### 2. Глобальний стан і статичні змінні

Часто розробники вендорських драйверів оголошують проміжні буфери передачі даних або таблиці калібрування як статичні змінні всередині файлів C, що руйнує модульність.

:::tabs
```c
/* Небезпечний патерн: глобальний статичний буфер у вендорському коді */
static uint8_t temp_i2c_tx_buffer[64];
static uint8_t s_device_operating_mode;

void vendor_set_mode_unsafe(uint8_t mode) {
    s_device_operating_mode = mode;
    temp_i2c_tx_buffer[0] = 0xF4;
    temp_i2c_tx_buffer[1] = s_device_operating_mode;
    /* Відправка в шину без прив'язки до екземпляра */
}
```
```cpp
#include <cstdint>
#include <array>

/* Безпечний підхід: стан інкапсульовано всередині екземпляра класу */
class SafeSensorDevice {
public:
    void set_mode(uint8_t mode) {
        operating_mode_ = mode;
        tx_buffer_[0] = 0xF4;
        tx_buffer_[1] = operating_mode_;
        // Відправка через контекст конкретного екземпляра
    }

private:
    uint8_t operating_mode_{0};
    std::array<uint8_t, 64> tx_buffer_{};
};
```
:::

Такий підхід повністю руйнує властивість реентрантності (англ. *reentrancy*):
- Якщо дві різні задачі в операційній системі спробують одночасно скористатися функціями бібліотеки для двох різних фізичних мікросхем, вони будуть одночасно модифікувати один і той самий статичний буфер `temp_i2c_tx_buffer`, перезаписуючи байти транзакцій одна одної.
- Код стає принципово непотокобезпечним (англ. *thread-unsafe*) навіть за умови використання різних дескрипторів.

Вимога аудиту: уся інформація про стан сенсора, включаючи тимчасові буфери, конфігураційні регістри та змінні математичних інтерполяцій, повинна зберігатися виключно всередині екземпляра структури пристрою `struct sensor_dev`.

### 3. Блокуючі затримки та активне опитування (Busy-Wait)

Вендорські бібліотеки для багатьох давачів містять процедури скидання (Soft Reset) або самотестування (BIST — Built-in Self Test), які вимагають очікування стабілізації аналогових кіл кристала (наприклад, 10–100 мс після подачі команди пробудження).

:::tabs
```c
/* Небезпечний вендорський патерн: неконтрольований тривалий busy-wait */
int8_t bme280_soft_reset_raw(struct sensor_dev *dev) {
    uint8_t cmd = 0xB6;
    dev->write(0xE0, &cmd, 1, dev->intf_ptr);
    
    /* Блокуюча затримка: вендор викликає переданий колбек */
    dev->delay_us(100000, dev->intf_ptr); /* 100 мілісекунд спалювання CPU! */
    return 0;
}
```
```cpp
#include <chrono>

/* Безпечний патерн: передача кванта часу планувальнику операційної системи */
class SensorTimeAbstraction {
public:
    static void non_blocking_delay(std::chrono::microseconds duration) {
        if (duration >= std::chrono::milliseconds(1)) {
            // Виклик системного переведення задачі в сон: vTaskDelay / k_sleep
        } else {
            // Апаратний мікросекундний таймер DWT
        }
    }
};
```
:::

Якщо розробник реалізує `dev->delay_us` як звичайний порожній цикл `for (volatile int i = 0; ...)` або опитування лічильника `SysTick`, процесор виконує активне спалювання енергії протягом 100 мс. У системі з RTOS цей час повинен бути відданий іншим задачам через системний виклик переведення потоку в стан сну (`vTaskDelay()` у FreeRTOS або `k_msleep()` у Zephyr). Якщо ж затримка викликається з критичної секції або з монопольно захопленим м'ютексом шини, вона паралізує взаємодію з усією іншою периферією на платі.

### 4. Витрати стеку та масивні локальні масиви

У прагненні уникнути динамічної пам'яті автори вендорських бібліотек іноді впадають у протилежну крайність: виділяють великі масиви безпосередньо на стеку функцій.

:::tabs
```c
/* Небезпечний патерн: виділення масивного буфера у стеку виклику */
int8_t vendor_parse_extended_data_hazard(struct sensor_dev *dev) {
    uint8_t raw_fifo_frame[1024]; /* 1 КБ на стеку потоку! */
    return dev->read(0x00, raw_fifo_frame, sizeof(raw_fifo_frame), dev->intf_ptr);
}
```
```cpp
#include <cstdint>
#include <span>

/* Безпечний підхід: буфер передається ззовні або належить структурі адаптера */
class SensorFrameParser {
public:
    int8_t parse_data(struct VendorSensorDev* dev, std::span<uint8_t> buffer) {
        if (buffer.size() < 1024) return -1;
        return dev->read(0x00, buffer.data(), static_cast<uint32_t>(buffer.size()), dev->intf_ptr);
    }
};
```
:::

У середовищі комп'ютера (Linux/Windows) виділення 1 КБ на стеку є непомітним, оскільки потік за замовчуванням має стек розміром 2–8 МБ. Але у вбудованих RTOS задачі зазвичай мають стек розміром 512–2048 байтів. Один такий виклик у вкладеному ланцюжку функцій миттєво переповнює виділений стек задачі (Stack Overflow), затирає сусідні структури даних ядра RTOS і призводить до важковловимих помилок поведінки прошивки.

## Ліцензійні аспекти, бінарні блоби та вендорний лок-ін

Окрім технічних характеристик коду, критичне значення мають юридичні та архітектурні обмеження ліцензування сторонніх драйверів.

### Ліцензійні пастки
Вендорський код поширюється під трьома основними категоріями ліцензій:
1. **Чисті ліцензії з відкритим кодом (BSD-3-Clause, Apache-2.0, MIT)**: найзручніший варіант для комерційної розробки. Дозволяє вільно модифікувати код, включати його в закриті прошивки та запускати на будь-яких процесорних архітектурах без обов'язку відкривати власний системний код (на відміну від вірусних ліцензій GPL). Більшість сучасних драйверів Bosch Sensor API та ST MEMS Drivers постачаються під ліцензією BSD-3-Clause.
2. **Обмежувальні ліцензії виробників (ST SLA0044, NXP/TI Software EULA)**: ліцензії, що юридично **забороняють** виконання коду на мікроконтролерах інших виробників. Наприклад, якщо алгоритм обробки ST Sensor Fusion або MotionFX захищено ліцензією SLA0044, використання цих C-файлів на мікроконтролері ESP32 чи Nordic nRF52 є прямим порушенням авторського права, що унеможливлює проходження юридичного аудиту комерційного продукту.
3. **Закриті бінарні блоби (.a / .lib)**: постачання драйвера у вигляді скомпільованої статичної бібліотеки без надання вихідного тексту.

> [!WARNING]
> Бінарні бібліотеки без вихідного коду несуть фундаментальні інженерні ризики:
> - **Несумісність ABI**: бінарний файл, скомпільований для апаратного модуля з плаваючою комою HardFP (ARM Cortex-M4F), не скомпонується з проєктом під SoftFP, або вимагатиме суворо визначеної версії компілятора GCC.
> - **Блокування оптимізації (LTO)**: компонувальник не може виконати наскрізну оптимізацію за часом компонування (Link-Time Optimization), інлайнінг дрібних функцій та видалення мертвого коду всередині бінарного блобу.
> - **Неможливість аудиту та виправлення багів**: виявлена помилка у розрахунках або переповнення буфера не може бути виправлена командою проєкту без офіційного оновлення від вендора, яке може зайняти місяці або не вийти ніколи.

### Подолання вендорного лок-іну (Vendor Lock-in)

Якщо бізнес-код прошивки (наприклад, модуль польотного контролера чи термостата) безпосередньо викликає вендорські функції `#include "bme280.h"` та оперує структурами `struct bme280_dev`, система потрапляє у жорстку залежність від конкретного постачальника чипа. Якщо через дефіцит на ринку або зняття мікросхеми з виробництва доведеться замінити сенсор Bosch на аналог від Sensirion чи Texas Instruments, інженерам доведеться переписати всі вищі модулі прошивки.

Правильний підхід полягає в ізоляції вендорського драйвера за системним інтерфейсом датчика через патерн проектування Адаптер (англ. *Adapter Pattern*).

## Патерн Адаптер (Adapter): повна ізоляція стороннього коду

Патерн Адаптер створює захисний бар'єр між системною архітектурою прошивки та пропрієтарним кодом виробника. Системний шар визначає чистий інтерфейс (абстрактний клас або структуру дескриптора), який оперує виключно стандартними одиницями SI та системними типами результатів помилок.

![Патерн Адаптер: повна ізоляція стороннього драйвера від архітектури прошивки](/root/course/embedded/chuzha-biblioteka-vid-vyrobnyka/img/adapter-isolation-layer.svg)
*Архітектура патерна Адаптер: системні інтерфейси прошивки повністю ізольовані від заголовків виробника датчика через проміжний шар трансляції.*

Обов'язки Адаптера:
1. **Інкапсуляція структур вендора**: заголовні файли SDK (`bme280.h`) підключаються лише у файлі реалізації адаптера (`.c` чи `.cpp`), ніколи не потрапляючи в загальні заголовки системи.
2. **Зв'язування колбеків Platform Abstraction Layer**: адаптер надає статичні C-функції перехідники (`bridge callbacks`), які витягують контекст об'єкта через `intf_ptr` і викликають методи системної шини.
3. **Трансляція кодів помилок**: вендорські числові коди повернення (`BME280_E_COMM_FAIL`, `BME280_E_DEV_NOT_FOUND`) транслюються у типізовані системні типи помилок або `std::expected`.
4. **Управління ресурсами та життєвим циклом (RAII)**: автоматичне переведення чипа в режим сну (Sleep/Power-down) при знищенні об'єкта адаптера.

Розглянемо практичну реалізацію Адаптера двома мовами:

:::tabs
```c
/* =================== Файл: sensor_adapter.h =================== */
#ifndef SENSOR_ADAPTER_H
#define SENSOR_ADAPTER_H

#include <stdint.h>
#include <stdbool.h>

/* Системний результат без прив'язки до вендорських заголовків */
typedef struct {
    int32_t temperature_centi_c; /* 2550 = 25.50 °C */
    uint32_t pressure_pa;        /* 101325 Па */
} sys_env_sample_t;

typedef enum {
    SYS_SENSOR_OK = 0,
    SYS_SENSOR_ERR_COMM,
    SYS_SENSOR_ERR_NOT_FOUND,
    SYS_SENSOR_ERR_INVALID_PARAM
} sys_sensor_status_t;

/* Непрозорий дескриптор адаптера */
typedef struct sensor_adapter sensor_adapter_t;

/* Інтерфейс системної шини */
typedef struct {
    bool (*read)(void *bus_ctx, uint8_t dev_addr, uint8_t reg, uint8_t *buf, uint16_t len);
    bool (*write)(void *bus_ctx, uint8_t dev_addr, uint8_t reg, const uint8_t *buf, uint16_t len);
    void *bus_ctx;
} sys_bus_interface_t;

/* Оголошення функцій адаптера */
sensor_adapter_t* sensor_adapter_create(const sys_bus_interface_t *bus, uint8_t i2c_addr);
sys_sensor_status_t sensor_adapter_init(sensor_adapter_t *adapter);
sys_sensor_status_t sensor_adapter_read_data(sensor_adapter_t *adapter, sys_env_sample_t *out_sample);
void sensor_adapter_destroy(sensor_adapter_t *adapter);

#endif /* SENSOR_ADAPTER_H */

/* =================== Файл: sensor_adapter.c =================== */
#include "sensor_adapter.h"
#include <stdlib.h>

/* Вендорський заголовок підключається ВИКЛЮЧНО тут */
#include "bme280.h" 

struct sensor_adapter {
    struct bme280_dev dev;
    sys_bus_interface_t bus;
    uint8_t i2c_addr;
};

/* Статичні містки для виклику системної шини */
static int8_t c_bus_read(uint8_t reg_addr, uint8_t *data, uint32_t len, void *intf_ptr) {
    sensor_adapter_t *self = (sensor_adapter_t*)intf_ptr;
    if (!self || !data) return BME280_E_NULL_PTR;
    bool ok = self->bus.read(self->bus.bus_ctx, self->i2c_addr, reg_addr, data, (uint16_t)len);
    return ok ? BME280_OK : BME280_E_COMM_FAIL;
}

static int8_t c_bus_write(uint8_t reg_addr, const uint8_t *data, uint32_t len, void *intf_ptr) {
    sensor_adapter_t *self = (sensor_adapter_t*)intf_ptr;
    if (!self || !data) return BME280_E_NULL_PTR;
    bool ok = self->bus.write(self->bus.bus_ctx, self->i2c_addr, reg_addr, data, (uint16_t)len);
    return ok ? BME280_OK : BME280_E_COMM_FAIL;
}

static void c_bus_delay_us(uint32_t period_us, void *intf_ptr) {
    (void)intf_ptr;
    /* У реальній системі: виклик системної затримки */
}

sys_sensor_status_t sensor_adapter_init(sensor_adapter_t *adapter) {
    if (!adapter) return SYS_SENSOR_ERR_INVALID_PARAM;
    
    adapter->dev.intf_ptr = adapter;
    adapter->dev.read = c_bus_read;
    adapter->dev.write = c_bus_write;
    adapter->dev.delay_us = c_bus_delay_us;
    adapter->dev.intf = BME280_I2C_INTF;

    int8_t rslt = bme280_init(&adapter->dev);
    if (rslt == BME280_E_DEV_NOT_FOUND) return SYS_SENSOR_ERR_NOT_FOUND;
    if (rslt != BME280_OK) return SYS_SENSOR_ERR_COMM;

    /* Конфігурація режиму роботи сенсора */
    struct bme280_settings settings;
    settings.osr_h = BME280_OVERSAMPLING_1X;
    settings.osr_p = BME280_OVERSAMPLING_16X;
    settings.osr_t = BME280_OVERSAMPLING_2X;
    settings.filter = BME280_FILTER_COEFF_16;
    bme280_set_sensor_settings(BME280_SEL_ALL_SETTINGS, &settings, &adapter->dev);
    bme280_set_sensor_mode(BME280_POWERMODE_NORMAL, &adapter->dev);

    return SYS_SENSOR_OK;
}

sys_sensor_status_t sensor_adapter_read_data(sensor_adapter_t *adapter, sys_env_sample_t *out_sample) {
    if (!adapter || !out_sample) return SYS_SENSOR_ERR_INVALID_PARAM;
    
    struct bme280_data comp_data;
    int8_t rslt = bme280_get_sensor_data(BME280_ALL, &comp_data, &adapter->dev);
    if (rslt != BME280_OK) return SYS_SENSOR_ERR_COMM;

    out_sample->temperature_centi_c = (int32_t)(comp_data.temperature * 100.0f);
    out_sample->pressure_pa = (uint32_t)comp_data.pressure;
    return SYS_SENSOR_OK;
}
```
```cpp
/* =================== Файл: sensor_adapter.hpp =================== */
#pragma once

#include <cstdint>
#include <expected>
#include <span>
#include <memory>

enum class SensorError : uint8_t {
    CommunicationFailed,
    DeviceNotFound,
    InvalidParameter,
    Timeout
};

struct EnvironmentSample {
    float temperature_celsius;
    float pressure_hpa;
};

/* Чистий системний інтерфейс I2C */
class II2cBus {
public:
    virtual ~II2cBus() = default;
    virtual bool read_bytes(uint8_t dev_addr, uint8_t reg, std::span<uint8_t> dst) = 0;
    virtual bool write_bytes(uint8_t dev_addr, uint8_t reg, std::span<const uint8_t> src) = 0;
};

/* Інтерфейс датчика середовища */
class IEnvironmentSensor {
public:
    virtual ~IEnvironmentSensor() = default;
    virtual std::expected<void, SensorError> initialize() = 0;
    virtual std::expected<EnvironmentSample, SensorError> read_sample() = 0;
};

/* Фабрика створення адаптера */
std::unique_ptr<IEnvironmentSensor> create_bme280_adapter(II2cBus& bus, uint8_t i2c_addr);

/* =================== Файл: sensor_adapter.cpp =================== */
#include "sensor_adapter.hpp"

/* Вендорський C-заголовок заховано всередині одиниці трансляції */
extern "C" {
    #include "bme280.h"
}

namespace {

class Bme280Adapter final : public IEnvironmentSensor {
public:
    explicit Bme280Adapter(II2cBus& bus, uint8_t i2c_addr)
        : bus_(bus), i2c_addr_(i2c_addr) {
        dev_.intf_ptr = this;
        dev_.read = c_read_bridge;
        dev_.write = c_write_bridge;
        dev_.delay_us = c_delay_bridge;
        dev_.intf = BME280_I2C_INTF;
    }

    ~Bme280Adapter() override {
        /* RAII: гарантований перевід у режим низького енергоспоживання */
        bme280_set_sensor_mode(BME280_POWERMODE_SLEEP, &dev_);
    }

    /* Заборона копіювання: intf_ptr жорстко прив'язаний до адреси цього екземпляра */
    Bme280Adapter(const Bme280Adapter&) = delete;
    Bme280Adapter& operator=(const Bme280Adapter&) = delete;

    std::expected<void, SensorError> initialize() override {
        int8_t rslt = bme280_init(&dev_);
        if (rslt == BME280_E_DEV_NOT_FOUND) return std::unexpected(SensorError::DeviceNotFound);
        if (rslt != BME280_OK) return std::unexpected(SensorError::CommunicationFailed);

        struct bme280_settings settings{};
        settings.osr_h = BME280_OVERSAMPLING_1X;
        settings.osr_p = BME280_OVERSAMPLING_16X;
        settings.osr_t = BME280_OVERSAMPLING_2X;
        settings.filter = BME280_FILTER_COEFF_16;
        bme280_set_sensor_settings(BME280_SEL_ALL_SETTINGS, &settings, &dev_);
        bme280_set_sensor_mode(BME280_POWERMODE_NORMAL, &dev_);

        return {};
    }

    std::expected<EnvironmentSample, SensorError> read_sample() override {
        struct bme280_data comp_data{};
        int8_t rslt = bme280_get_sensor_data(BME280_ALL, &comp_data, &dev_);
        if (rslt != BME280_OK) return std::unexpected(SensorError::CommunicationFailed);

        return EnvironmentSample{
            .temperature_celsius = comp_data.temperature,
            .pressure_hpa = comp_data.pressure / 100.0f
        };
    }

private:
    static int8_t c_read_bridge(uint8_t reg_addr, uint8_t *data, uint32_t len, void *intf_ptr) {
        if (!intf_ptr || !data || len == 0) return BME280_E_NULL_PTR;
        auto* self = static_cast<Bme280Adapter*>(intf_ptr);
        std::span<uint8_t> dst(data, len);
        return self->bus_.read_bytes(self->i2c_addr_, reg_addr, dst) ? BME280_OK : BME280_E_COMM_FAIL;
    }

    static int8_t c_write_bridge(uint8_t reg_addr, const uint8_t *data, uint32_t len, void *intf_ptr) {
        if (!intf_ptr || !data || len == 0) return BME280_E_NULL_PTR;
        auto* self = static_cast<Bme280Adapter*>(intf_ptr);
        std::span<const uint8_t> src(data, len);
        return self->bus_.write_bytes(self->i2c_addr_, reg_addr, src) ? BME280_OK : BME280_E_COMM_FAIL;
    }

    static void c_delay_bridge(uint32_t period_us, void *intf_ptr) {
        (void)intf_ptr;
        /* Системна реалізація затримки */
    }

    II2cBus& bus_;
    uint8_t i2c_addr_;
    struct bme280_dev dev_{};
};

} // namespace

std::unique_ptr<IEnvironmentSensor> create_bme280_adapter(II2cBus& bus, uint8_t i2c_addr) {
    return std::make_unique<Bme280Adapter>(bus, i2c_addr);
}
```
:::

Повний приклад реалізації Адаптера з тестовим фреймворком та програмним емулятором шини наведено у вставці [Практична реалізація адаптера та модульне тестування вендорського драйвера](root:embedded/chuzha-biblioteka-vid-vyrobnyka/proj-vendor-driver-adapter.md).

## Потокобезпечність та інтеграція у FreeRTOS/Zephyr

У реальній вбудованій системі під керуванням операційної системи реального часу (RTOS) доступ до сенсора та шини відбувається конкурентно з різних потоків. Наприклад, потік телеметрії опитує температуру раз на 1 секунду, а потік контуру керування зчитує тиск 50 разів на секунду.

![Модель багатопотокової безпеки: м'ютекси та неблокуючі затримки в RTOS](/root/course/embedded/chuzha-biblioteka-vid-vyrobnyka/img/rtos-concurrency-model.svg)
*Організація багатопотокового доступу: роздільні м'ютекси пристрою та шини у поєднанні з трансляцією затримок у системний виклик vTaskDelay.*

Для забезпечення надійної інтеграції необхідно вирішити дві задачі: багаторівневе блокування та неблокуючі затримки.

### Дворівневе блокування: Bus Mutex проти Device Mutex

Поширена помилка розробників — захищати м'ютексом виключно апаратний драйвер шини (I2C/SPI). Проте взаємодія з MEMS-давачем часто є **складеною транзакцією** (англ. *compound transaction*), що складається з кількох кроків:
1. Запис у конфігураційний регістр команди запуску примусового вимірювання (Forced Mode).
2. Очікування готовності даних протягом 10 мілісекунд.
3. Пакетне зчитування 6 байтів результату.

Якщо захищено лише шину, інший потік (наприклад, опитування іншого датчика на тій же шині) може вклинитися між кроками 1 і 3 та перемкнути режим шини або змінити стан пристрою.

Правильна архітектура використовує два рівні синхронізації:
- **Device Mutex (М'ютекс пристрою)**: захоплюється адаптером на весь час виконання високорівневої операції `read_sample()` чи `configure()`. Це гарантує неподільність багатоетапного сеансу роботи з чипом.
- **Bus Mutex (М'ютекс шини)**: захоплюється драйвером I2C/SPI лише на час передачі одного пакета байтів по фізичних лініях SDA/SCL або MOSI/MISO. Це дозволяє іншим пристроям користуватися шиною під час пауз між вимірюваннями.

> [!IMPORTANT]
> Для запобігання взаємним блокуванням (Deadlocks) порядок захоплення м'ютексів завжди повинен бути суворо ієрархічним: спершу захоплюється `Device Mutex`, і лише всередині колбеків передачі — `Bus Mutex`. Захоплення у зворотному порядку заборонено. Обидва м'ютекси повинні підтримувати механізм успадкування пріоритетів (англ. *Priority Inheritance*) для уникнення явища інверсії пріоритетів (англ. *Priority Inversion*).

### Адаптація затримок delay_us під планувальник RTOS

Вендорський Platform Abstraction Layer вимагає функцію затримки `delay_us(uint32_t period_us)`.

У системі з RTOS ця функція повинна бути **гібридною**:
- **Короткі затримки (менше 1 кванта планувальника, зазвичай < 100–500 мкс)**: виконуються через апаратний таймер або лічильник циклів ядра DWT (Data Watchpoint and Trace). Перемикання контексту RTOS займає 2–10 мкс, тому віддавати квант заради паузи у 20 мкс невигідно через оверхед планувальника.
- **Тривалі затримки (≥ 1 мс)**: конвертуються у кванти RTOS і передаються в системний виклик блокування потоку:
  - У FreeRTOS: `vTaskDelay(pdMS_TO_TICKS(period_us / 1000));`
  - У Zephyr RTOS: `k_msleep(period_us / 1000);`

При цьому вбудований перехідник повинен містити перевірку контексту: якщо затримка викликається з обробника переривання (ISR), виклик блокуючого сну RTOS заборонений (викличе Kernel Panic), і функція зобов'язана використати апаратний лічильник.

## Тестування надійності, мокінг шини та захист від збоїв (Fault Injection)

Головний критерій якості адаптера — поведінка системи у випадку, коли підключений чип поводиться нештатно або виходить із ладу.

### Типові крайові випадки вендорського коду
При прямій інтеграції вендорські SDK часто ламаються на таких сценаріях:
1. **Чип відпаявся або не відповідає (Лінії I2C підтягнуті до VCC)**: функція читання шини зчитує суцільні байти `0xFF`. Якщо вендорська бібліотека не перевіряє значення калібрувальних коефіцієнтів, формули розрахунку можуть виконати **ділення на нуль**, викликавши апаратне виключення `UsageFault` (Divide by Zero Trap).
2. **Обрив зв'язку посеред транзакції (I2C NACK / SPI Timeout)**: вендорська функція повертає код помилки, але адаптер некоректно обробляє вихід із функції і **забуває звільнити захоплений м'ютекс**. У результаті шина назавжди блокується для всіх інших задач системи.
3. **Зациклення при очікуванні прапорця готовності**: якщо вендорський код містить внутрішній цикл `while (status & BUSY)` без лічильника таймауту, апаратне зависання сенсора призводить до вічного зависання потоку RTOS.

### Модульне тестування на хост-системі (Mock Testing)

Завдяки патерну Адаптер весь стек взаємодії з сенсором можна протестувати на комп'ютері розробника (x86_64) без наявності реальної плати. Для цього створюється клас або структура `MockI2cBus`, яка зберігає віртуальний масив регістрів сенсора у пам'яті.

Програма тестування повинна покривати обов'язковий набір сценаріїв впровадження збоїв (англ. *Fault Injection*):
- **Тест валідної ініціалізації**: перевірка коректного зчитування `Chip ID` та конфігурації регістрів.
- **Тест відмови шини на етапі ініціалізації**: генерація помилки NACK на першому ж байті — перевірка, що адаптер повертає код помилки `DeviceNotFound` і не переходить у неініціалізований стан.
- **Тест аварійного обриву під час вимірювання**: імітація таймауту шини в момент зчитування сирих даних — перевірка, що м'ютекс шини коректно звільняється, а система повертає `CommunicationFailed`.
- **Тест некоректних калібрувальних даних**: заповнення карти регістрів нулями `0x00` або одиницями `0xFF` — перевірка, що математичні формули не викликають ділення на нуль або генерації значень `NaN` (Not a Number) / нескінченності.

## Підсумок: правила безпечної інтеграції чужого коду

Інтеграція вендорських бібліотек у вбудовану систему підпорядковується суворим інженерним правилам:
1. **Ніколи не підключайте заголовки вендора у загальні заголовні файли проєкту**: уся взаємодія зі стороннім SDK інкапсулюється всередині модуля адаптера.
2. **Проводьте обов'язковий аудит на символи динамічної пам'яті та глобальний стан**: бібліотека повинна отримувати всю необхідну пам'ять статично через дескриптор.
3. **Ізолюйте затримки під планувальник RTOS**: тривалі очікування перетворюються на неблокуючий сон потоку, звільняючи процесор для інших задач.
4. **Використовуйте дворівневе блокування**: розділяйте м'ютекс монопольного володіння сенсором та м'ютекс фізичної шини передачі даних.
5. **Покривайте адаптер модульними тестами з ін'єкцією помилок шини**: прошивка повинна штатно реагувати на обриви ліній, некоректні ідентифікатори та зависання зовнішнього чипа.
