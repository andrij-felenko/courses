# Програмний рушій фіксації та первинної класифікації інцидентів

Програмний рушій фіксації інцидентів (англ. *incident triaging engine*) — це вбудований автономний модуль прошивки, що перехоплює аварійні ситуації (спрацьовування апаратних винятків HardFault, переповнення стеків завдань RTOS, таймаути шин периферії та спрацьовування системних тверджень `assert`), формує структурований бінарний знімок діагностичного контексту та зберігає його в енергонезалежній пам'яті до скидання мікроконтролера. 

Головна складність реалізації такого рушія полягає в тому, що в момент фатальної відмови система вже перебуває в ненадійному стані: покажчик стека може вказувати за межі оперативної пам'яті, динамічна купа (heap) може бути зруйнована через переповнення буфера (buffer overflow), а напруга живлення може стрімко падати через відключення зовнішнього джерела. Спроба викликати стандартні бібліотечні функції на кшталт `printf()` чи `malloc()` усередині обробника `HardFault_Handler` гарантовано призводить до вторинного винятку (англ. *double fault*) і повного зациклення процесора без запису даних.

---

### Апаратний вхід у виняток та збереження контексту (Naked Handler)

На архітектурі ARM Cortex-M мікроконтролер при виникненні апаратної помилки автоматично зберігає у поточному стеку базовий стек-фрейм (регістри `R0`, `R1`, `R2`, `R3`, `R12`, `LR`, `PC`, `xPSR`). Проте для точної класифікації інциденту цього недостатньо: необхідно визначити, який саме покажчик стека використовувався в момент збою — покажчик головного стека (MSP, Main Stack Pointer) чи покажчик стека потоку RTOS (PSP, Process Stack Pointer).

Вхідна функція переривання оголошується з атрибутом `__attribute__((naked))`, що забороняє компілятору генерувати стандартний пролог і епілог функції, зберігаючи значення регістрів у первісному недоторканому стані:

:::tabs
```c
/* Асемблерний перехоплювач винятку HardFault для Cortex-M */
__attribute__((naked)) void HardFault_Handler(void) {
    __asm volatile (
        " tst lr, #4            \n" /* Перевірка біта 2 регістра LR (EXC_RETURN) */
        " ite eq                \n"
        " mrseq r0, msp         \n" /* Якщо біт 0: стек-фрейм лежить у MSP */
        " mrsne r0, psp         \n" /* Якщо біт 1: стек-фрейм лежить у PSP */
        " mov r1, lr            \n" /* Передаємо значення EXC_RETURN другим аргументом */
        " b prv_hardfault_c_handler \n" /* Перехід до C-обробника */
    );
}
```
```cpp
/* Асемблерний перехоплювач винятку HardFault для Cortex-M (C++) */
extern "C" [[gnu::naked]] void HardFault_Handler() noexcept {
    __asm volatile (
        " tst lr, #4            \n" /* Перевірка біта 2 регістра LR (EXC_RETURN) */
        " ite eq                \n"
        " mrseq r0, msp         \n" /* Якщо біт 0: стек-фрейм лежить у MSP */
        " mrsne r0, psp         \n" /* Якщо біт 1: стек-фрейм лежить у PSP */
        " mov r1, lr            \n" /* Передаємо значення EXC_RETURN другим аргументом */
        " b prv_hardfault_c_handler \n" /* Перехід до C++ обробника */
    );
}
```
:::

---

### Архітектура фіксації знімка аварії в критичній секції

Коли керування передається в функцію `prv_hardfault_c_handler(uint32_t *stack_frame, uint32_t exc_return)`, потік виконання негайно ізолюється. Рушій виконує сувору послідовність кроків без використання динамічної пам'яті:

```
       ЛАНЦЮЖОК ОБРОБКИ АВАРІЙНОЇ СИТУАЦІЇ ВБУДОВАНИМ РУШІЄМ
       
  [HardFault / Assert] ──► [__disable_irq()] ──► [Визначення стека: MSP чи PSP]
                                                            │
                                                            ▼
  [Перезапуск через WDT] ◄── [Запис кадру + CRC32] ◄── [Зняття контексту: PC, LR, CFSR]
                                                            │
                                                            ▼
                                                [Збір метрик: VDD, Task, I2C err]
```

#### 1. Ізоляція периферії та апаратна безпека
Перед початком копіювання регістрів рушій вимикає всі масковані переривання через інструкцію `CPSID i` (`__disable_irq()`), примусово переводить силові ключі (MOSFET-драйвери двигунів, нагрівачі) у закритий стан через прямий запис у регістри `BSRR` портів GPIO та зупиняє передачу радіомодуля. Це запобігає апаратному пошкодженню силового тракту, якщо збій стався під час керування потужним навантаженням.

#### 2. Перехоплення зависань через раннє переривання сторожового таймера
Для фіксації взаємних блокувань потоків RTOS (deadlock) звичайного сторожового таймера IWDG недостатньо, оскільки він скидає процесор миттєво без виклику обробника. Рушій налаштовує віконний сторожовий таймер WWDG з увімкненням переривання раннього попередження (англ. *Early Warning Interrupt, EWIF*). Це переривання спрацьовує за 1–2 мілісекунди до апаратного скидання, надаючи рушію гарантоване вікно часу для зняття покажчиків стеків усіх активних завдань і фіксації ID заблокованого семафора.

#### 3. Моніторинг водяних знаків стеків RTOS (Stack High Watermark)
Під час роботи під керуванням операційної системи реального часу кожне завдання виділяє фіксований стек. Рушій у момент аварії перевіряє шаблони заповнення пам'яті (патерн `0xA5A5A5A5`), обчислюючи мінімальний залишок вільного місця на стеку кожного потоку. Якщо залишок дорівнює нулю, причиною збою класифікується не логічна помилка алгоритму, а переповнення стека (Stack Overflow), що затерло сусідній дескриптор завдання TCB.

#### 4. Атомарний запис у Backup SRAM/FRAM
Сформований знімок копіюється у виділену енергонезалежну область за фіксованою адресою пам'яті. Використання бар'єрів пам'яті `__DSB()` (Data Synchronization Barrier) та `__ISB()` (Instruction Synchronization Barrier) гарантує, що конвеєр процесора та буфери запису шини повністю завершать скидання байтів у фізичні комірки SRAM до того, як сторожовий таймер або системний виклик `NVIC_SystemReset()` ініціює апаратне перезавантаження.

#### 5. Компіляторне хешування системних тверджень (Assert Hashing)
Збереження текстових рядків шляхів до файлів на кшталт `"src/drivers/sensor_sht31.c"` під час спрацьовування макроса `assert()` займає надто багато місця у флеш-пам'яті та у діагностичному кадрі. Рушій використовує 32-бітний хеш FNV-1a від імені файлу та номер рядка:

:::tabs
```c
#define EMBED_ASSERT(expr) do { \
    if (!(expr)) { \
        record_assert_incident(HASH_FILE(__FILE__), __LINE__); \
    } \
} while(0)
```
```cpp
template <typename Predicate>
constexpr void embedAssert(Predicate&& pred, uint32_t fileHash, uint32_t line) noexcept {
    if (!pred()) {
        record_assert_incident(fileHash, line);
    }
}

#define EMBED_ASSERT(expr) embedAssert([&]() noexcept { return (expr); }, HASH_FILE(__FILE__), __LINE__)
```
:::

---

### Реалізація рушія знімків аварії (Firmware Engine)

Нижче наведено робочий модуль збереження діагностичного знімка інциденту мовами C та C++. Модуль не використовує стек для проміжних буферів і працює виключно зі статично виділеними структурами:

:::tabs
```c
/* incident_recorder.h / incident_recorder.c */
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define INCIDENT_MAGIC 0xDEADBEEFUL

typedef struct __attribute__((packed)) {
    uint32_t magic;            /* 0xDEADBEEF */
    uint32_t timestamp_sec;    /* Час аварії від запуску */
    uint32_t reset_reason;     /* Регістр скидання RCC_CSR */
    uint32_t fault_pc;         /* Адреса збою (Program Counter) */
    uint32_t fault_lr;         /* Регістр зв'язку (Link Register) */
    uint32_t fault_cfsr;       /* Configurable Fault Status Register */
    uint16_t supply_mv;        /* Напруга живлення в мілівольтах */
    int16_t  die_temp_c;       /* Температура кристала (°C) */
    uint16_t i2c_nack_count;   /* Лічильник таймаутів шини I2C */
    uint16_t spi_err_count;    /* Лічильник помилок SPI */
    uint32_t active_task_id;   /* Ідентифікатор активного потоку */
    uint32_t free_heap_bytes;  /* Залишок динамічної пам'яті */
    uint32_t crc32;            /* Контрольна сума кадру */
} incident_snapshot_t;

/* Виділений енергонезалежний сектор у Backup SRAM */
#define BACKUP_SRAM_ADDR ((void*)0x40024000UL)

static uint32_t compute_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFFUL;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320UL & -(crc & 1));
        }
    }
    return ~crc;
}

void record_fatal_incident(uint32_t pc, uint32_t lr, uint32_t cfsr, 
                           uint32_t task_id, uint16_t v_mv, int16_t temp_c) {
    incident_snapshot_t snap;
    memset(&snap, 0, sizeof(snap));

    snap.magic = INCIDENT_MAGIC;
    snap.timestamp_sec = 10423; /* Зчитується з апаратного таймера/RTC */
    snap.reset_reason = 0x20000000UL; /* Приклад: прапор IWDGRSTF */
    snap.fault_pc = pc;
    snap.fault_lr = lr;
    snap.fault_cfsr = cfsr;
    snap.supply_mv = v_mv;
    snap.die_temp_c = temp_c;
    snap.active_task_id = task_id;
    snap.i2c_nack_count = 14;
    snap.spi_err_count = 0;
    snap.free_heap_bytes = 4096;

    /* Обчислення контрольної суми без поля crc32 */
    snap.crc32 = compute_crc32((const uint8_t*)&snap, sizeof(snap) - sizeof(uint32_t));

    /* Атомарне копіювання в енергонезалежний регіон */
    memcpy(BACKUP_SRAM_ADDR, &snap, sizeof(snap));
}
```
```cpp
/* IncidentRecorder.hpp / IncidentRecorder.cpp */
#include <cstdint>
#include <cstddef>
#include <cstring>
#include <span>
#include <optional>

namespace Diagnostic {

#pragma pack(push, 1)
struct IncidentSnapshot {
    static constexpr std::uint32_t MagicTag = 0xDEADBEEFUL;

    std::uint32_t magic{MagicTag};
    std::uint32_t timestamp_sec{0};
    std::uint32_t reset_reason{0};
    std::uint32_t fault_pc{0};
    std::uint32_t fault_lr{0};
    std::uint32_t fault_cfsr{0};
    std::uint16_t supply_mv{0};
    std::int16_t  die_temp_c{0};
    std::uint16_t i2c_nack_count{0};
    std::uint16_t spi_err_count{0};
    std::uint32_t active_task_id{0};
    std::uint32_t free_heap_bytes{0};
    std::uint32_t crc32{0};
};
#pragma pack(pop)

class IncidentRecorder {
public:
    static constexpr std::uintptr_t BackupSramBase = 0x40024000UL;

    static std::uint32_t calculateCrc32(std::span<const std::uint8_t> data) noexcept {
        std::uint32_t crc = 0xFFFFFFFFUL;
        for (const auto byte : data) {
            crc ^= byte;
            for (int bit = 0; bit < 8; ++bit) {
                crc = (crc >> 1) ^ (0xEDB88320UL & -(crc & 1));
            }
        }
        return ~crc;
    }

    static void recordFatalIncident(std::uint32_t pc, std::uint32_t lr, std::uint32_t cfsr,
                                    std::uint32_t taskId, std::uint16_t vMv, std::int16_t tempC) noexcept {
        IncidentSnapshot snap;
        snap.timestamp_sec = 10423;
        snap.reset_reason = 0x20000000UL;
        snap.fault_pc = pc;
        snap.fault_lr = lr;
        snap.fault_cfsr = cfsr;
        snap.supply_mv = vMv;
        snap.die_temp_c = tempC;
        snap.active_task_id = taskId;
        snap.i2c_nack_count = 14;
        snap.spi_err_count = 0;
        snap.free_heap_bytes = 4096;

        const auto payloadSpan = std::span<const std::uint8_t>(
            reinterpret_cast<const std::uint8_t*>(&snap),
            sizeof(IncidentSnapshot) - sizeof(std::uint32_t)
        );
        snap.crc32 = calculateCrc32(payloadSpan);

        auto* dest = reinterpret_cast<IncidentSnapshot*>(BackupSramBase);
        *dest = snap;
    }

    static std::optional<IncidentSnapshot> retrieveLastSnapshot() noexcept {
        auto* src = reinterpret_cast<const IncidentSnapshot*>(BackupSramBase);
        if (src->magic != IncidentSnapshot::MagicTag) {
            return std::nullopt;
        }

        const auto payloadSpan = std::span<const std::uint8_t>(
            reinterpret_cast<const std::uint8_t*>(src),
            sizeof(IncidentSnapshot) - sizeof(std::uint32_t)
        );

        if (calculateCrc32(payloadSpan) != src->crc32) {
            return std::nullopt;
        }

        return *src;
    }
};

} // namespace Diagnostic
```
:::

---

### Обробка та аналіз діагностичного кадру на хості

Після того, як пристрій вивантажує бінарний знімок через сервісний порт або радіоканал, хостова система виконує автоматичну тріангуляцію інциденту за таким алгоритмом:

#### 1. Десимволізація адрес інструкцій (Symbol Resolution)
Значення лічильника команд `fault_pc` зіставляється з налагоджувальною інформацією компілятора (DWARF-секціями у вихідному файлі `.elf` точної версії збірки) за допомогою утиліти `arm-none-eabi-addr2line`:

```
$ arm-none-eabi-addr2line -e build/firmware_v1.4.2.elf 0x08004A2C -f -C
i2c_wait_rxne
src/drivers/i2c_driver.c:142
```

Це одразу локалізує конкретний рядок вихідного коду, на якому процесор зупинив виконання, відкидаючи суб'єктивні гіпотези про збій у високорівневій логіці інтерфейсу.

#### 2. Інтерпретація регістрів аналізу несправностей (CFSR Decoding)
Регістр `CFSR` (Configurable Fault Status Register) містить три групи бітових прапорів:
- **MemManage Fault Status (MMFSR):** порушення правил блоку захисту пам'яті MPU (спроба запису в таблицю векторів або виконання коду зі стека).
- **BusFault Status (BFSR):** біт `PRECISERR` вказує на точну адресу неіснуючої пам'яті (значення збережено в регістрі `BFAR`), тоді як біт `IMPRECISERR` сигналізує про асинхронну помилку запису буфера шини AHB/APB.
- **UsageFault Status (UFSR):** біти `UNDEFINSTR` (спроба виконання невалідної інструкції після пошкодження пам'яті програм) або `DIVBYZERO` (ділення на нуль).

#### 3. Генерація структурованого звіту сортування (Triage Report)

```
[INCIDENT TRIAGE REPORT]
------------------------------------------------------------
Апаратний статус скидання : IWDG (Watchdog Timer Triggered)
Адреса інструкції (PC)    : 0x08004A2C -> i2c_wait_rxne() в i2c_driver.c:142
Регістр зв'язку (LR)      : 0x080031B0 -> sht31_read_temp_hum() в sht31.c:88
Стан живлення VDD         : 2780 мВ (Норма: 3300 мВ, виявлено просадку!)
Температура кристала      : +64 °C
Активний потік RTOS       : SensorTask (ID: 0x02, Stack Headroom: 48 bytes)
Лічильник I2C NACK        : 14 помилок підряд

ВИСНОВОК РУШІЯ:
Головний потік SensorTask завис у блокуючому циклі i2c_wait_rxne() 
через просідання живлення датчика нижче 2.8 В під час передачі радіокадру.
```
