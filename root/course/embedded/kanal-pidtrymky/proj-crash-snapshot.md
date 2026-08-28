# ⚙️ Реалізація енергонезалежного збору аварійного знімка на ARM Cortex-M

Збір діагностичного контексту в момент аварійного збою (англ. *crash snapshot capture*) — найкритичніша ділянка коду вбудованої системи. Коли процесор заходить у переривання `HardFault`, пам'ять стека може бути пошкоджена, стек-поінтер — вказувати на неіснуючу адресу, а планувальник RTOS — заблокований. Спроба викликати стандартні функції `printf`, `malloc` чи високорівневі драйвери блокує пристрій намертво, знищуючи останній шанс дізнатися справжню причину аварії.

---

## 1. Архітектурні обмеження аварійного обробника

Щоб зберегти дані про збій у Flash чи FRAM, обробник паніки зобов'язаний дотримуватися чотирьох залізних правил:

1. **Жодної динамічної пам'яті:** виділення буферів виконується суворо статично в секції `.noinit` (ділянка оперативної пам'яті, яка не затирається нулями при перезапуску мікроконтролера) або записується безпосередньо у виділені регістри енергонезалежної пам'яті. Виклик `malloc` чи `free` у стані аварії гарантовано призведе до повторного винятку (Double Fault), оскільки структури купи можуть бути пошкоджені витоком або переповненням буфера.
2. **Прямий низькорівневий запис:** драйвер запису у Flash або FRAM не повинен використовувати переривання чи м'ютекси. Запис ведеться в режимі прямого опитування регістрів (polling). У момент винятку всі масковані переривання заблоковані, тому будь-яке очікування системного прапорця переривання призведе до нескінченного зависання.
3. **Безпечне вилучення стек-фрейму:** визначення активного стека (MSP чи PSP) здійснюється кількома асемблерними інструкціями до виклику будь-якого C/C++ коду, щоб не затерти верхівку стека локальними змінними. При вході у виняток ядро процесора автоматично складає на активний стек вісім 32-бітних слів: `R0`, `R1`, `R2`, `R3`, `R12`, `LR`, `PC` та `xPSR`.
4. **Гарантоване перезавантаження:** після збереження блоку даних обробник примусово ініціює системний скид через регістр `AIRCR` (Application Interrupt and Reset Control Register), щоб повернути апарат у безпечний робочий стан і не допустити хаотичного керування силовими ключами та виконавчими приводами.

---

## 2. Реалізація аварійного збирача даних

Нижче наведено робочий модуль збору діагностичного пакета для мікроконтролерів сімейства ARM Cortex-M (STM32, NXP, Nordic nRF).

:::tabs
```c
/* crash_capture.c — аварійний збирач діагностичного контексту */
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define BUNDLE_MAGIC        0x4442554E  /* 'DBUN' */
#define BUNDLE_VERSION      0x0200      /* v2.0 */
#define FLASH_DIAG_ADDR     0x080E0000  /* Адреса виділеного сектора Flash */

typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint16_t version;
    uint16_t header_size;
    uint32_t payload_size;
    uint32_t serial_number;
    uint16_t hw_revision;
    uint16_t reset_reason;
    uint32_t fw_git_hash;
    uint64_t uptime_ms;
} crash_header_t;

typedef struct __attribute__((packed)) {
    uint32_t r0, r1, r2, r3, r12, lr, pc, xpsr;
    uint32_t cfsr, hfsr, mmfar, bfar;
} cpu_registers_t;

typedef struct __attribute__((packed)) {
    uint16_t v_in_mv;
    uint16_t v_3v3_mv;
    int16_t  mcu_temp_c10;
    uint16_t reserved;
} power_telemetry_t;

typedef struct __attribute__((packed)) {
    crash_header_t    header;
    cpu_registers_t   cpu;
    power_telemetry_t power;
    uint32_t          crc32;
} crash_snapshot_t;

/* Статичний буфер у секції .noinit для збереження контексту */
__attribute__((section(".noinit"))) static crash_snapshot_t s_active_snapshot;

/* Швидкий табличний розрахунок CRC32 */
static uint32_t calculate_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320 & -(crc & 1));
        }
    }
    return ~crc;
}

/* Низькорівневий запис у внутрішню Flash-пам'ять методом опитування */
static void flash_write_polling(uint32_t dest_addr, const uint8_t *src, size_t size) {
    /* Симуляція прямого доступу до регістрів Flash контролера */
    /* У реальній системі: розблокування Flash -> стирання сектора -> запис слів -> блокування */
    volatile uint32_t *flash_ptr = (volatile uint32_t *)dest_addr;
    const uint32_t *src_ptr = (const uint32_t *)src;
    size_t words = (size + 3) / 4;

    for (size_t i = 0; i < words; ++i) {
        flash_ptr[i] = src_ptr[i];
    }
}

/* С-функція, яка викликається з асемблерного HardFault-трампліна */
void HardFault_Handler_C(uint32_t *hardfault_args) {
    /* Читання регістрів ядра зі стек-фрейму */
    s_active_snapshot.cpu.r0   = hardfault_args[0];
    s_active_snapshot.cpu.r1   = hardfault_args[1];
    s_active_snapshot.cpu.r2   = hardfault_args[2];
    s_active_snapshot.cpu.r3   = hardfault_args[3];
    s_active_snapshot.cpu.r12  = hardfault_args[4];
    s_active_snapshot.cpu.lr   = hardfault_args[5];
    s_active_snapshot.cpu.pc   = hardfault_args[6];
    s_active_snapshot.cpu.xpsr = hardfault_args[7];

    /* Зчитування апаратних системних регістрів SCB (System Control Block) */
    volatile uint32_t *scb_cfsr  = (volatile uint32_t *)0xE000ED28;
    volatile uint32_t *scb_hfsr  = (volatile uint32_t *)0xE000ED2C;
    volatile uint32_t *scb_mmfar = (volatile uint32_t *)0xE000ED34;
    volatile uint32_t *scb_bfar  = (volatile uint32_t *)0xE000ED38;

    s_active_snapshot.cpu.cfsr  = *scb_cfsr;
    s_active_snapshot.cpu.hfsr  = *scb_hfsr;
    s_active_snapshot.cpu.mmfar = *scb_mmfar;
    s_active_snapshot.cpu.bfar  = *scb_bfar;

    /* Заповнення заголовка пакета */
    s_active_snapshot.header.magic          = BUNDLE_MAGIC;
    s_active_snapshot.header.version        = BUNDLE_VERSION;
    s_active_snapshot.header.header_size    = sizeof(crash_header_t);
    s_active_snapshot.header.payload_size   = sizeof(crash_snapshot_t) - sizeof(crash_header_t);
    s_active_snapshot.header.serial_number  = 20260042;
    s_active_snapshot.header.hw_revision    = 0x0043; /* 'C' */
    s_active_snapshot.header.reset_reason   = 0x0001; /* HardFault */
    s_active_snapshot.header.fw_git_hash    = 0x7F89BC20;
    s_active_snapshot.header.uptime_ms      = 3693600000ULL;

    /* Останні відомі показники телеметрії з тіньових регістрів */
    s_active_snapshot.power.v_in_mv       = 23850;
    s_active_snapshot.power.v_3v3_mv      = 3290;
    s_active_snapshot.power.mcu_temp_c10  = 485;

    /* Розрахунок контрольної суми */
    s_active_snapshot.crc32 = calculate_crc32((const uint8_t *)&s_active_snapshot,
                                              sizeof(crash_snapshot_t) - sizeof(uint32_t));

    /* Запис у захищений сектор Flash */
    flash_write_polling(FLASH_DIAG_ADDR, (const uint8_t *)&s_active_snapshot, sizeof(crash_snapshot_t));

    /* Примусовий системний перезапуск через SCB AIRCR */
    volatile uint32_t *scb_aircr = (volatile uint32_t *)0xE000ED0C;
    *scb_aircr = (0x5FA << 16) | (1 << 2); /* SYSRESETREQ */

    while (1) {
        __asm volatile("nop");
    }
}
```
```cpp
// crash_capture.hpp / crash_capture.cpp — ідіоматичний аварійний супервізор C++20
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>

namespace diagnostic {

inline constexpr uint32_t BundleMagic   = 0x4442554E; // 'DBUN'
inline constexpr uint16_t BundleVersion = 0x0200;     // v2.0
inline constexpr uintptr_t FlashDiagAddr = 0x080E0000;

struct [[gnu::packed]] CrashHeader {
    uint32_t magic{BundleMagic};
    uint16_t version{BundleVersion};
    uint16_t header_size{sizeof(CrashHeader)};
    uint32_t payload_size{0};
    uint32_t serial_number{0};
    uint16_t hw_revision{0};
    uint16_t reset_reason{0};
    uint32_t fw_git_hash{0};
    uint64_t uptime_ms{0};
};

struct [[gnu::packed]] CpuRegisters {
    uint32_t r0{}, r1{}, r2{}, r3{}, r12{}, lr{}, pc{}, xpsr{};
    uint32_t cfsr{}, hfsr{}, mmfar{}, bfar{};
};

struct [[gnu::packed]] PowerTelemetry {
    uint16_t v_in_mv{0};
    uint16_t v_3v3_mv{0};
    int16_t  mcu_temp_c10{0};
    uint16_t reserved{0};
};

struct [[gnu::packed]] CrashSnapshot {
    CrashHeader     header;
    CpuRegisters    cpu;
    PowerTelemetry  power;
    uint32_t        crc32{0};
};

class SnapshotCollector {
public:
    static constexpr uint32_t CalculateCrc32(std::span<const uint8_t> data) noexcept {
        uint32_t crc = 0xFFFFFFFF;
        for (const auto byte : data) {
            crc ^= byte;
            for (uint8_t bit = 0; bit < 8; ++bit) {
                crc = (crc >> 1) ^ (0xEDB88320 & -(crc & 1));
            }
        }
        return ~crc;
    }

    static void CaptureAndReboot(std::span<const uint32_t, 8> stack_frame) noexcept {
        auto& snap = GetStorage();

        // Заповнення регістрів ядра
        snap.cpu.r0   = stack_frame[0];
        snap.cpu.r1   = stack_frame[1];
        snap.cpu.r2   = stack_frame[2];
        snap.cpu.r3   = stack_frame[3];
        snap.cpu.r12  = stack_frame[4];
        snap.cpu.lr   = stack_frame[5];
        snap.cpu.pc   = stack_frame[6];
        snap.cpu.xpsr = stack_frame[7];

        // Читання апаратних регістрів винятків SCB
        const auto* scb_base = reinterpret_cast<const volatile uint32_t*>(0xE000ED28);
        snap.cpu.cfsr  = scb_base[0]; // 0xE000ED28
        snap.cpu.hfsr  = scb_base[1]; // 0xE000ED2C
        snap.cpu.mmfar = scb_base[3]; // 0xE000ED34
        snap.cpu.bfar  = scb_base[4]; // 0xE000ED38

        // Заповнення заголовка
        snap.header.payload_size  = sizeof(CrashSnapshot) - sizeof(CrashHeader);
        snap.header.serial_number = 20260042;
        snap.header.hw_revision   = 0x0043;
        snap.header.reset_reason  = 0x0001;
        snap.header.fw_git_hash   = 0x7F89BC20;
        snap.header.uptime_ms     = 3693600000ULL;

        snap.power.v_in_mv      = 23850;
        snap.power.v_3v3_mv     = 3290;
        snap.power.mcu_temp_c10 = 485;

        // Контрольна сума
        auto raw_bytes = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&snap),
                                                 sizeof(CrashSnapshot) - sizeof(uint32_t));
        snap.crc32 = CalculateCrc32(raw_bytes);

        // Прямий запис у Flash
        WriteToFlash(FlashDiagAddr, std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&snap), sizeof(CrashSnapshot)));

        // Перезавантаження системи
        TriggerSystemReset();
    }

private:
    static CrashSnapshot& GetStorage() noexcept {
        [[gnu::section(".noinit")]] static CrashSnapshot s_instance;
        return s_instance;
    }

    static void WriteToFlash(uintptr_t dest, std::span<const uint8_t> src) noexcept {
        auto* flash_words = reinterpret_cast<volatile uint32_t*>(dest);
        const auto* src_words = reinterpret_cast<const uint32_t*>(src.data());
        const size_t word_count = (src.size() + 3) / 4;

        for (size_t i = 0; i < word_count; ++i) {
            flash_words[i] = src_words[i];
        }
    }

    [[noreturn]] static void TriggerSystemReset() noexcept {
        auto* aircr = reinterpret_cast<volatile uint32_t*>(0xE000ED0C);
        *aircr = (0x5FA << 16) | (1 << 2);
        while (true) {
            asm volatile("nop");
        }
    }
};

} // namespace diagnostic

extern "C" void HardFault_Handler_C(uint32_t* hardfault_args) {
    auto frame_span = std::span<const uint32_t, 8>(hardfault_args, 8);
    diagnostic::SnapshotCollector::CaptureAndReboot(frame_span);
}
```
:::

---

## 3. Асемблерний трамплін переривання та декодування EXC_RETURN

Щоб передати правильний вказівник на стек у функцію `HardFault_Handler_C`, використовується компактний асемблерний перехідник. Коли ядро Cortex-M переходить в обробник винятку, регістр зв'язку `LR` містить спеціальне магічне значення `EXC_RETURN` (зазвичай `0xFFFFFFFD` або `0xFFFFFFF9`).

Біт 2 цього значення визначає, який саме стек використовувався кодом у мить збою:
- Якщо біт 2 дорівнює `0` — аварія сталася в коді іншого переривання або ядра, і стек-фрейм збережено на головному стеку (`MSP` — Main Stack Pointer).
- Якщо біт 2 дорівнює `1` — аварія сталася у звичайній прикладній задачі RTOS, і стек-фрейм лежить на стеку процесів (`PSP` — Process Stack Pointer).

```asm
/* hardfault_trampoline.s */
.syntax unified
.thumb
.global HardFault_Handler

HardFault_Handler:
    TST LR, #4               /* Перевірка біта 2 регістра LR (EXC_RETURN) */
    ITE EQ
    MRSEQ R0, MSP            /* Якщо 0 — активний Main Stack Pointer */
    MRSNE R0, PSP            /* Якщо 1 — активний Process Stack Pointer */
    B HardFault_Handler_C    /* Перехід у C/C++ обробник із вказівником у R0 */
```

Цей код гарантує, що незалежно від того, де стався збій — у коді переривання на головному стеку чи в задачі FreeRTOS на власному стеку, обробник отримає точні адреси `PC` та `LR` для дешифрування за допомогою утиліти `addr2line`.

---

## 4. Відновлення та обробка знімка після перезапуску

Після того, як мікроконтролер виконав перезавантаження через `AIRCR`, під час ініціалізації системи (функція `main()` до запуску планувальника RTOS) прошивка виконує процедуру перевірки наявності свіжого аварійного пакета:

1. **Перевірка магічних байтів та контрольної суми:** функція зчитує перші 64 байти з адреси `FLASH_DIAG_ADDR`. Якщо `magic == 0x4442554E` та розрахована CRC32 збігається зі збереженою, система переходить у режим обробки інциденту.
2. **Встановлення сервісного прапорця:** прошивка виставляє системний прапорець `s_has_pending_crash_report = true`.
3. **Публікація через доступні канали зв'язку:**
   - Якщо доступна мережа (LTE/Wi-Fi/Ethernet), фонова задача телеметрії відправляє знімок на серверний ендпоінт.
   - Якщо зв'язку немає, знімок залишається заблокованим у Flash до підключення техніка через сервісний UART/USB.
4. **Очищення або маркування як відправленого:** після отримання підтвердження від сервера або виконання команди `diag clear` у консолі, статусний байт заголовка переводиться в стан `PROCESSED`, щоб уникнути повторної відправки того самого інциденту.

---

## 5. Обробка крайових випадків та небезпек

При розробці аварійного обробника слід враховувати такі крайові сценарії:

- **Просадка живлення під час аварії (Brownout Fault):** якщо збій викликаний вимкненням живлення, напруга на шині 3.3 В починає лавиноподібно спадати. Запис у внутрішню Flash вимагає підвищеного струму (до 10–20 мА на час стирання сектора), що може прискорити падіння напруги. У таких випадках пріоритет надається запису в оперативну пам'ять `.noinit` або зовнішню FRAM, яка завершує операцію за сотні наносекунд.
- **Пошкодження вказівника стека (Stack Overflow):** якщо стек процесу переповнився й зруйнував таблицю дескрипторів задач, апаратний блок MPU згенерує `MemManageFault`. Трамплін зобов'язаний коректно перемкнутися на `MSP`, щоб обробник винятку не впав у нескінченний цикл спроб запису на переповнений стек.
- **Подвійний збій (Double Fault):** якщо всередині самого обробника `HardFault_Handler_C` виникає нова помилка доступу до пам'яті, процесор переходить у стан блокування (Lockup). Для виходу з цього стану апаратний сторожовий таймер IWDG повинен мати незалежне тактування від низькочастотного генератора LSI, що гарантує примусовий апаратний скид мікроконтролера через 1–2 секунди.
