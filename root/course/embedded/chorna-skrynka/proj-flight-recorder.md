# ⚙️ Модуль бортового реєстратора подій на C та C++

У вбудованих приладах критичного призначення (безпілотні апарати, системи керування акумуляторними батареями, медична техніка, промислова автоматика) виникнення апаратного виключення чи раптового перезавантаження вимагає збереження точного стану пристрою безпосередньо перед аварією. Нижче наведено завершену реалізацію модуля бортового реєстратора (Embedded Flight Recorder), спроєктовану для мікроконтролерів архітектур ARM Cortex-M та RISC-V. Модуль поєднує кільцеву буферизацію у незанулюваній пам'яті `.noinit` SRAM, прямий низькорівневий запис у FRAM або SPI Flash без очікування переривань, апаратний перехоплювач фатальних збоїв HardFault та інструмент автоматизованого декодування бінарних знімків на комп'ютері розробника.

---

## Архітектурний дизайн та принципи надійності

Модуль реєстратора спроєктовано з урахуванням суворих обмежень систем жорсткого реального часу, де стандартні засоби введення-виведення стають головним джерелом вторинних збоїв:

1. **Ізоляція та живучість пам'яті:** Буфер журналу розміщується у спеціальній компонувальній секції `.noinit`, яка виключається з процедури занулення стартовим кодом `crt0`. Завдяки цьому при програмному рестарті ядра (`NVIC_SystemReset()`) або скиданні за сторожовим таймером Watchdog накопичена хронологія подій залишається непошкодженою.
2. **Константна часова складність O(1):** Операція збереження кадру зводиться до копіювання фіксованих 16 байтів та атомарного інкременту лічильника. Для буфера з місткістю, що дорівнює ступеню двійки ($256 = 2^8$), обчислення наступного індексу замінюється порозрядною кон'юнкцією `(index + 1) & (CAPACITY - 1)`, що виконується за один такт процесора і займає менше 35 тактів сумарно.
3. **Безпека переривань (ISR Safety):** Запис подій може безпечно викликатися з обробників апаратних переривань будь-якого рівня вкладеності без використання блокувальних м'ютексів RTOS.
4. **Контроль цілісності:** Кожен 16-байтний двійковий кадр має індивідуальну контрольну суму [CRC-16/CCITT](root:com-modulation/crc), що дозволяє відновити валідні записи навіть при частковому спотворенні секторів пам'яті.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│             КАРТА ПАМ'ЯТІ ТА ПОТОКИ ДАНИХ БОРТОВОГО РЕЄСТРАТОРА                        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Потоковий запис (SRAM .noinit):                                                     │
│    Підсистеми (NAV, POWER, COM) ──[flight_recorder_log]──> Кільцевий буфер 4 КБ       │
│                                                                                        │
│ 2. Аварійне перехоплення (HardFault / PVD IRQ):                                        │
│    Регістри ядра (PC, LR, CFSR) ──[blackbox_panic]───────> Заморожування буфера (Freeze)│
│                                                                                        │
│ 3. Енергонезалежна фіксація (Flush):                                                   │
│    Заморожений буфер SRAM ───────[spi_emergency_write]───> SPI FRAM / Flash Слот       │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Реалізація ядра модуля мовою C

У наведеній реалізації мовою C структури даних упаковані з примусовим вирівнюванням за 4-байтною межею за допомогою атрибутів `__attribute__((packed, aligned(4)))`. Це повністю унеможливлює виникнення апаратних збоїв непарного доступу (`Unaligned Memory Access Trap`) на процесорах Cortex-M0/M0+.

:::tabs
=== "C"
```c
/* flight_recorder_core.h - Двійковий інтерфейс реєстратора (C) */
#ifndef FLIGHT_RECORDER_CORE_H
#define FLIGHT_RECORDER_CORE_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define BLACKBOX_MAGIC_HEADER   0x424F5831U /* 'BOX1' */
#define BLACKBOX_BUFFER_SIZE    256U        /* 256 подій * 16 байтів = 4096 байтів */
#define BLACKBOX_BUFFER_MASK    (BLACKBOX_BUFFER_SIZE - 1U)

typedef enum {
    SUBSYS_CORE     = 0x00,
    SUBSYS_POWER    = 0x01,
    SUBSYS_NAV      = 0x02,
    SUBSYS_ACTUATOR = 0x03,
    SUBSYS_COMM     = 0x04
} BlackBoxSubsystem_t;

typedef enum {
    EVT_NONE           = 0x00,
    EVT_BOOT_OK        = 0x01,
    EVT_FSM_TRANSITION = 0x02,
    EVT_BUS_NACK       = 0x03,
    EVT_BUS_TIMEOUT    = 0x04,
    EVT_VOLTAGE_WARN   = 0x05,
    EVT_TEMP_CRITICAL  = 0x06,
    EVT_HARDFAULT      = 0xFE,
    EVT_PANIC_ABORT    = 0xFF
} BlackBoxEventCode_t;

/* 16-байтний двійковий кадр події */
typedef struct __attribute__((packed, aligned(4))) {
    uint32_t timestamp_ms;
    uint8_t  subsystem;
    uint8_t  event_code;
    uint16_t fsm_state;
    uint8_t  payload[6];
    uint16_t crc16;
} BlackBoxFrame_t;

/* Заголовок та пам'ять тому реєстратора */
typedef struct __attribute__((packed, aligned(4))) {
    uint32_t magic;
    uint32_t boot_counter;
    uint32_t crash_counter;
    volatile uint32_t head_index;
    volatile uint32_t is_frozen;
    BlackBoxFrame_t frames[BLACKBOX_BUFFER_SIZE];
    uint16_t header_crc;
} BlackBoxStorage_t;

/* Функції керування та логування */
void blackbox_init(void);
void blackbox_record(BlackBoxSubsystem_t subsys, BlackBoxEventCode_t code, uint16_t fsm, const void* data, uint8_t len);
void blackbox_emergency_panic(uint8_t reason, uint32_t pc, uint32_t fault_addr);
bool blackbox_is_crash_dump_present(void);
const BlackBoxStorage_t* blackbox_get_storage_ptr(void);

#ifdef __cplusplus
}
#endif

#endif /* FLIGHT_RECORDER_CORE_H */
```

```c
/* flight_recorder_core.c - Реалізація функцій запису та контролю цілісності (C) */
#include "flight_recorder_core.h"
#include <string.h>

/* Розміщення в спеціальній незанулюваній секції оперативної пам'яті */
__attribute__((section(".noinit"))) static BlackBoxStorage_t g_bb_ram;

/* Апаратні системні виклики мікроконтролера */
extern uint32_t mcu_get_uptime_ms(void);
extern uint32_t mcu_enter_critical(void);
extern void mcu_exit_critical(uint32_t primask);

static uint16_t calculate_crc16(const uint8_t* buffer, size_t size) {
    uint16_t crc = 0xFFFFU;
    for (size_t i = 0; i < size; ++i) {
        crc ^= ((uint16_t)buffer[i] << 8);
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 0x8000U) {
                crc = (crc << 1) ^ 0x1021U;
            } else {
                crc = (crc << 1);
            }
        }
    }
    return crc;
}

void blackbox_init(void) {
    if (g_bb_ram.magic != BLACKBOX_MAGIC_HEADER) {
        /* Перше увімкнення після повного знеструмлення */
        g_bb_ram.magic = BLACKBOX_MAGIC_HEADER;
        g_bb_ram.boot_counter = 1;
        g_bb_ram.crash_counter = 0;
        g_bb_ram.head_index = 0;
        g_bb_ram.is_frozen = 0;
        memset((void*)g_bb_ram.frames, 0, sizeof(g_bb_ram.frames));
    } else {
        /* Перезапуск після програмного скидання або аварійного винятку */
        g_bb_ram.boot_counter++;
        g_bb_ram.is_frozen = 0; /* Розблокування буфера для нової сесії */
    }
}

void blackbox_record(BlackBoxSubsystem_t subsys, BlackBoxEventCode_t code, uint16_t fsm, const void* data, uint8_t len) {
    if (g_bb_ram.is_frozen != 0) {
        return; /* Запис заблоковано для збереження аварійного знімка */
    }

    uint32_t primask = mcu_enter_critical();
    uint32_t slot_idx = g_bb_ram.head_index;
    g_bb_ram.head_index = (slot_idx + 1U) & BLACKBOX_BUFFER_MASK;
    mcu_exit_critical(primask);

    BlackBoxFrame_t* frame = &g_bb_ram.frames[slot_idx];
    frame->timestamp_ms = mcu_get_uptime_ms();
    frame->subsystem = (uint8_t)subsys;
    frame->event_code = (uint8_t)code;
    frame->fsm_state = fsm;

    memset(frame->payload, 0, sizeof(frame->payload));
    if (data != NULL && len > 0) {
        uint8_t copy_size = (len > sizeof(frame->payload)) ? (uint8_t)sizeof(frame->payload) : len;
        memcpy(frame->payload, data, copy_size);
    }

    frame->crc16 = calculate_crc16((const uint8_t*)frame, 14);
}

void blackbox_emergency_panic(uint8_t reason, uint32_t pc, uint32_t fault_addr) {
    mcu_enter_critical();
    g_bb_ram.is_frozen = 1; /* Атомарне заморожування буфера */
    g_bb_ram.crash_counter++;

    uint32_t slot_idx = g_bb_ram.head_index;
    BlackBoxFrame_t* panic_frame = &g_bb_ram.frames[slot_idx];
    panic_frame->timestamp_ms = mcu_get_uptime_ms();
    panic_frame->subsystem = (uint8_t)SUBSYS_CORE;
    panic_frame->event_code = (uint8_t)EVT_HARDFAULT;
    panic_frame->fsm_state = (uint16_t)reason;

    memcpy(&panic_frame->payload[0], &pc, sizeof(uint32_t));
    memcpy(&panic_frame->payload[4], &fault_addr, 2);

    panic_frame->crc16 = calculate_crc16((const uint8_t*)panic_frame, 14);
}

bool blackbox_is_crash_dump_present(void) {
    return (g_bb_ram.magic == BLACKBOX_MAGIC_HEADER && g_bb_ram.crash_counter > 0);
}

const BlackBoxStorage_t* blackbox_get_storage_ptr(void) {
    return &g_bb_ram;
}
```
=== "C++"
```cpp
// FlightRecorderCore.hpp - Сучасний ідіоматичний реєстратор подій (C++20)
#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <concepts>
#include <algorithm>
#include <type_traits>

namespace embedded::diagnostics {

enum class Subsystem : uint8_t {
    Core     = 0x00,
    Power    = 0x01,
    Nav      = 0x02,
    Actuator = 0x03,
    Comm     = 0x04
};

enum class EventCode : uint8_t {
    None          = 0x00,
    BootOk        = 0x01,
    FsmTransition = 0x02,
    BusNack       = 0x03,
    BusTimeout    = 0x04,
    VoltageWarn   = 0x05,
    TempCritical  = 0x06,
    HardFault     = 0xFE,
    PanicAbort    = 0xFF
};

struct alignas(4) EventFrame {
    uint32_t  timestamp_ms{0};
    Subsystem subsystem{Subsystem::Core};
    EventCode event_code{EventCode::None};
    uint16_t  fsm_state{0};
    std::array<uint8_t, 6> payload{};
    uint16_t  crc16{0};

    [[nodiscard]] bool is_valid() const noexcept {
        return crc16 == compute_crc();
    }

    void update_crc() noexcept {
        crc16 = compute_crc();
    }

private:
    [[nodiscard]] uint16_t compute_crc() const noexcept {
        uint16_t crc = 0xFFFFU;
        const auto* raw = reinterpret_cast<const uint8_t*>(this);
        for (size_t i = 0; i < 14; ++i) {
            crc ^= static_cast<uint16_t>(raw[i]) << 8;
            for (uint8_t bit = 0; bit < 8; ++bit) {
                if (crc & 0x8000U) {
                    crc = (crc << 1) ^ 0x1021U;
                } else {
                    crc = (crc << 1);
                }
            }
        }
        return crc;
    }
};

template <size_t BufferCapacity = 256>
    requires ((BufferCapacity & (BufferCapacity - 1)) == 0) // Ємність має бути ступенем двійки
class FlightRecorderEngine {
public:
    static constexpr uint32_t MagicHeader = 0x424F5831U; // 'BOX1'
    static constexpr uint32_t BufferMask  = BufferCapacity - 1U;

    void init() noexcept {
        if (magic_ != MagicHeader) {
            magic_ = MagicHeader;
            boot_counter_ = 1;
            crash_counter_ = 0;
            head_index_ = 0;
            is_frozen_ = false;
            frames_.fill(EventFrame{});
        } else {
            boot_counter_++;
            is_frozen_ = false;
        }
    }

    template <typename TPayload>
        requires (sizeof(TPayload) <= 6 && std::is_trivially_copyable_v<TPayload>)
    void record(Subsystem subsys, EventCode code, uint16_t fsm, const TPayload& data) noexcept {
        std::array<uint8_t, 6> serialized{};
        const auto* src = reinterpret_cast<const uint8_t*>(&data);
        std::copy_n(src, sizeof(TPayload), serialized.begin());
        record_raw(subsys, code, fsm, serialized);
    }

    void record(Subsystem subsys, EventCode code, uint16_t fsm = 0) noexcept {
        record_raw(subsys, code, fsm, std::array<uint8_t, 6>{});
    }

    void emergency_panic(uint8_t reason, uint32_t pc, uint32_t fault_addr) noexcept {
        is_frozen_ = true;
        crash_counter_++;

        auto& panic_slot = frames_[head_index_];
        panic_slot.timestamp_ms = get_system_uptime();
        panic_slot.subsystem = Subsystem::Core;
        panic_slot.event_code = EventCode::HardFault;
        panic_slot.fsm_state = reason;

        std::copy_n(reinterpret_cast<const uint8_t*>(&pc), 4, panic_slot.payload.begin());
        std::copy_n(reinterpret_cast<const uint8_t*>(&fault_addr), 2, panic_slot.payload.begin() + 4);
        panic_slot.update_crc();
    }

    [[nodiscard]] bool has_crash_dump() const noexcept {
        return magic_ == MagicHeader && crash_counter_ > 0;
    }

    [[nodiscard]] std::span<const EventFrame> get_frames() const noexcept {
        return frames_;
    }

    [[nodiscard]] uint32_t boot_count() const noexcept { return boot_counter_; }
    [[nodiscard]] uint32_t crash_count() const noexcept { return crash_counter_; }
    [[nodiscard]] uint32_t head() const noexcept { return head_index_; }

private:
    void record_raw(Subsystem subsys, EventCode code, uint16_t fsm, const std::array<uint8_t, 6>& data) noexcept {
        if (is_frozen_) return;

        uint32_t current_idx = head_index_;
        head_index_ = (current_idx + 1U) & BufferMask;

        auto& slot = frames_[current_idx];
        slot.timestamp_ms = get_system_uptime();
        slot.subsystem = subsys;
        slot.event_code = code;
        slot.fsm_state = fsm;
        slot.payload = data;
        slot.update_crc();
    }

    [[nodiscard]] static uint32_t get_system_uptime() noexcept;

    uint32_t magic_{0};
    uint32_t boot_counter_{0};
    uint32_t crash_counter_{0};
    volatile uint32_t head_index_{0};
    volatile bool is_frozen_{false};
    std::array<EventFrame, BufferCapacity> frames_{};
};

} // namespace embedded::diagnostics
```
:::

---

## Прямий аварійний запис у FRAM або SPI Flash

Під час аварійного вимкнення живлення чи фатального винятку HardFault стандартні підсистеми драйверів (які покладаються на RTOS, черги DMA або переривання шини) стають недоступними. Будь-яка спроба зачекати прапорця переривання `SPI_I2S_FLAG_TXE` з увімкненим планувальником операційної системи спричиняє зависання ядра.

Для збереження аварійного знімка використовується автономна функція прямого побайтового опитування регістрів SPI (Polling Mode Direct Flush). Вона вимикає DMA, напряму маніпулює лінією Chip Select і записує дані безпосередньо у вихідний регістр FIFO передавача SPI:

:::tabs
=== "C"
```c
/* spi_emergency_dump.c - Прямий автономний запис дампа у SPI FRAM / Flash (C) */
#include "flight_recorder_core.h"

/* Пряма адресація регістрів апаратного SPI1 (на прикладі ARM Cortex-M) */
#define SPI1_BASE_ADDR   0x40013000U
#define SPI_CR1_REG      (*((volatile uint32_t*)(SPI1_BASE_ADDR + 0x00U)))
#define SPI_SR_REG       (*((volatile uint32_t*)(SPI1_BASE_ADDR + 0x08U)))
#define SPI_DR_REG       (*((volatile uint32_t*)(SPI1_BASE_ADDR + 0x0CU)))
#define GPIOA_BSRR_REG   (*((volatile uint32_t*)(0x40020000U + 0x18U)))

#define SPI_SR_TXE_FLAG  (1U << 1)
#define SPI_SR_BSY_FLAG  (1U << 7)
#define FRAM_OPCODE_WREN 0x06U
#define FRAM_OPCODE_WRITE 0x02U

static void emergency_cs_low(void)  { GPIOA_BSRR_REG = (1U << (4 + 16)); } /* CS = Low  (PA4) */
static void emergency_cs_high(void) { GPIOA_BSRR_REG = (1U << 4); }        /* CS = High (PA4) */

static uint8_t emergency_spi_transfer_byte(uint8_t data) {
    while (!(SPI_SR_REG & SPI_SR_TXE_FLAG)) {
        /* Очікування звільнення буфера передавача без затримки RTOS */
    }
    SPI_DR_REG = data;
    while (SPI_SR_REG & SPI_SR_BSY_FLAG) {
        /* Очікування завершення тактування байта на лініях SCK/MOSI */
    }
    return (uint8_t)SPI_DR_REG;
}

void blackbox_spi_emergency_flush(uint32_t flash_dst_addr) {
    const BlackBoxStorage_t* storage = blackbox_get_storage_ptr();
    const uint8_t* raw_bytes = (const uint8_t*)storage;
    size_t total_size = sizeof(BlackBoxStorage_t);

    /* 1. Дозвіл запису (Write Enable Latch) */
    emergency_cs_low();
    emergency_spi_transfer_byte(FRAM_OPCODE_WREN);
    emergency_cs_high();

    /* 2. Передача команди запису та 24-бітної адреси сховища */
    emergency_cs_low();
    emergency_spi_transfer_byte(FRAM_OPCODE_WRITE);
    emergency_spi_transfer_byte((uint8_t)(flash_dst_addr >> 16));
    emergency_spi_transfer_byte((uint8_t)(flash_dst_addr >> 8));
    emergency_spi_transfer_byte((uint8_t)(flash_dst_addr & 0xFFU));

    /* 3. Потокова передача 4096 байтів дампа зі швидкістю тактування SPI */
    for (size_t i = 0; i < total_size; ++i) {
        emergency_spi_transfer_byte(raw_bytes[i]);
    }
    emergency_cs_high();
}
```
=== "C++"
```cpp
// SpiEmergencyDump.hpp - Низькорівневий драйвер аварійного зливу (C++20)
#pragma once

#include <cstdint>
#include <cstddef>
#include <span>

namespace embedded::drivers {

class EmergencySpiFram {
public:
    static constexpr uint32_t Spi1Base = 0x40013000U;
    static constexpr uint8_t  OpcodeWren  = 0x06U;
    static constexpr uint8_t  OpcodeWrite = 0x02U;

    static void flush_buffer(uint32_t dest_address, std::span<const uint8_t> dump_data) noexcept {
        cs_assert(false);
        transfer_byte(OpcodeWren);
        cs_assert(true);

        cs_assert(false);
        transfer_byte(OpcodeWrite);
        transfer_byte(static_cast<uint8_t>(dest_address >> 16));
        transfer_byte(static_cast<uint8_t>(dest_address >> 8));
        transfer_byte(static_cast<uint8_t>(dest_address & 0xFFU));

        for (const uint8_t byte : dump_data) {
            transfer_byte(byte);
        }
        cs_assert(true);
    }

private:
    static void cs_assert(bool state) noexcept {
        auto* const bsrr = reinterpret_cast<volatile uint32_t*>(0x40020000U + 0x18U);
        *bsrr = state ? (1U << 4) : (1U << (4 + 16));
    }

    static uint8_t transfer_byte(uint8_t byte) noexcept {
        auto* const sr = reinterpret_cast<volatile uint32_t*>(Spi1Base + 0x08U);
        auto* const dr = reinterpret_cast<volatile uint32_t*>(Spi1Base + 0x0CU);

        while (!(*sr & (1U << 1))) { /* Очікування TXE */ }
        *dr = byte;
        while (*sr & (1U << 7))     { /* Очікування BSY */ }
        return static_cast<uint8_t>(*dr);
    }
};

} // namespace embedded::drivers
```
:::

---

## Інтеграція з апаратним обробником Cortex-M HardFault

Коли мікроконтролер стикається з фатальним виключенням (розіменування невалідного покажчика, виконання забороненого коду інструкції чи помилка шини пам'яті), апаратна логіка ядра ARM Cortex-M автоматично зберігає 8 базових регістрів (R0–R3, R12, LR, PC, xPSR) у поточний активний стек.

Обробник виключення повинен визначити, який саме стек використовувався в момент аварії: стек переривань ядра (Main Stack Pointer, MSP) чи стек потоку операційної системи (Process Stack Pointer, PSP). Це визначається перевіркою 2-го біта спеціального коду повернення `EXC_RETURN`, збереженого в регістрі `LR`:

:::tabs
=== "C"
```c
/* hardfault_trap.c - Апаратний перехоплювач винятків ARM Cortex-M (C) */
#include "flight_recorder_core.h"

void prvGetRegistersFromStack(uint32_t* pulFaultStackAddress) {
    /* Регістри апаратного стекового кадру */
    uint32_t r0  = pulFaultStackAddress[0];
    uint32_t r1  = pulFaultStackAddress[1];
    uint32_t r2  = pulFaultStackAddress[2];
    uint32_t r3  = pulFaultStackAddress[3];
    uint32_t r12 = pulFaultStackAddress[4];
    uint32_t lr  = pulFaultStackAddress[5]; /* Адреса повернення */
    uint32_t pc  = pulFaultStackAddress[6]; /* Адреса інструкції збою */
    uint32_t psr = pulFaultStackAddress[7];

    /* Регістри конфігурації збоїв Cortex-M (CFSR, HFSR, MMFAR, BFAR) */
    volatile uint32_t cfsr = (*((volatile uint32_t*)0xE000ED28));
    volatile uint32_t bfar = (*((volatile uint32_t*)0xE000ED38));

    /* Фіксація аварії в чорній скриньці */
    blackbox_emergency_panic((uint8_t)(cfsr & 0xFF), pc, bfar);

    /* Програмне перезавантаження ядра для виходу з аварійного стану */
    volatile uint32_t* aircr = (volatile uint32_t*)0xE000ED0C;
    *aircr = 0x05FA0000U | (1U << 2); /* NVIC_SystemReset */
    while (1) { __asm volatile("nop"); }
}

/* Асемблерний перехоплювач: вибирає MSP або PSP залежно від EXC_RETURN */
__attribute__((naked)) void HardFault_Handler(void) {
    __asm volatile(
        "tst lr, #4\n"
        "ite eq\n"
        "mrseq r0, msp\n"
        "mrsne r0, psp\n"
        "b prvGetRegistersFromStack\n"
    );
}
```
=== "C++"
```cpp
// HardFaultTrap.cpp - Перехоплювач аварійних винятків (C++20)
#include "FlightRecorderCore.hpp"

extern "C" void prvGetRegistersFromStackCpp(uint32_t* stack_frame) noexcept {
    const uint32_t pc = stack_frame[6];
    const auto cfsr = *reinterpret_cast<volatile uint32_t*>(0xE000ED28);
    const auto bfar = *reinterpret_cast<volatile uint32_t*>(0xE000ED38);

    // Звернення до глобального екземпляра реєстратора
    extern embedded::diagnostics::FlightRecorderEngine<256> g_flight_recorder;
    g_flight_recorder.emergency_panic(static_cast<uint8_t>(cfsr & 0xFF), pc, bfar);

    // Ініціація рестарту ядра
    auto* const aircr = reinterpret_cast<volatile uint32_t*>(0xE000ED0C);
    *aircr = 0x05FA0000U | (1U << 2);
    while (true) { asm volatile("nop"); }
}

extern "C" [[gnu::naked]] void HardFault_Handler() noexcept {
    asm volatile(
        "tst lr, #4\n"
        "ite eq\n"
        "mrseq r0, msp\n"
        "mrsne r0, psp\n"
        "b prvGetRegistersFromStackCpp\n"
    );
}
```
:::

Регістр `CFSR` (Configurable Fault Status Register, адреса `0xE000ED28`) дає вичерпну інформацію про природу збою:
- **`IACCVIOL` (біт 0):** Спроба вибірки інструкції з недійсної або забороненої області пам'яті (наприклад, перехід за нульовим покажчиком).
- **`DACCVIOL` (біт 1):** Спроба читання або запису даних за адресою, заблокованою блоком захисту пам'яті MPU.
- **`UNALIGNED` (біт 24):** Непарний доступ до пам'яті при увімкненому біті `UNALIGN_TRP` у регістрі `CCR`.
- **`DIVBYZERO` (біт 25):** Спроба апаратного ділення на нуль при увімкненому прапорці `DIV_0_TRP`.

---

## Хостовий інструмент декодування та символьної кореляції

Зчитаний програматором або через діагностичний інтерфейс бінарний файл містить 4096 байтів сирих двійкових структур. Для відновлення цілісної хронологічної картини використовується утиліта на мові Python.

Скрипт сортує кільцевий буфер так, щоб події йшли у строгому часовому порядку від найдавніших до моменту катастрофи, перевіряє цілісність кожного кадру за алгоритмом CRC-16 та автоматично викликає утиліту `arm-none-eabi-addr2line` для перетворення шістнадцяткових адрес Program Counter (PC) на точні назви функцій і номери рядків сирцевого коду C/C++:

```python
#!/usr/bin/env python3
# decode_blackbox.py - Декодер двійкових знімків бортового реєстратора
import struct
import subprocess
import sys

SUBSYSTEMS = {
    0x00: "CORE",
    0x01: "POWER",
    0x02: "NAV",
    0x03: "ACTUATOR",
    0x04: "COMM"
}

EVENTS = {
    0x00: "NONE",
    0x01: "BOOT_OK",
    0x02: "FSM_TRANSITION",
    0x03: "BUS_NACK",
    0x04: "BUS_TIMEOUT",
    0x05: "VOLTAGE_WARN",
    0x06: "TEMP_CRITICAL",
    0xFE: "HARDFAULT",
    0xFF: "PANIC_ABORT"
}

def crc16_ccitt(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= (b << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc

def resolve_symbol(elf_path: str, address: int) -> str:
    if not elf_path:
        return f"0x{address:08X}"
    try:
        cmd = ["arm-none-eabi-addr2line", "-e", elf_path, "-f", "-C", f"0x{address:08X}"]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = res.stdout.strip().split("\n")
        return f"{lines[0]} ({lines[1]})" if len(lines) >= 2 else f"0x{address:08X}"
    except Exception:
        return f"0x{address:08X}"

def parse_dump(dump_file: str, elf_file: str = ""):
    with open(dump_file, "rb") as f:
        raw = f.read()

    if len(raw) < 20:
        print("Помилка: файл занадто малий для тому реєстратора")
        return

    magic, boot_cnt, crash_cnt, head_idx, frozen = struct.unpack_from("<IIIII", raw, 0)
    if magic != 0x424F5831:
        print(f"Помилка: невідомий магічний заголовок 0x{magic:08X} (очікувався 'BOX1')")
        return

    print("=" * 75)
    print(f"ЗВІТ БОРТОВОГО РЕЄСТРАТОРА: Boots={boot_cnt}, Crashes={crash_cnt}, Head={head_idx}, Frozen={frozen}")
    print("=" * 75)

    offset = 20
    frame_size = 16
    total_frames = 256

    frames = []
    for i in range(total_frames):
        chunk = raw[offset + i * frame_size : offset + (i + 1) * frame_size]
        if len(chunk) < 16:
            break
        ts, sub, evt, fsm, p0, p1, p2, p3, p4, p5, crc = struct.unpack("<IBBH6BH", chunk)
        calc_crc = crc16_ccitt(chunk[:14])
        is_ok = (crc == calc_crc)
        payload = bytes([p0, p1, p2, p3, p4, p5])
        frames.append((i, ts, sub, evt, fsm, payload, is_ok))

    # Сортування кільцевого буфера у хронологічному порядку
    ordered_frames = frames[head_idx:] + frames[:head_idx]

    for slot, ts, sub, evt, fsm, payload, valid in ordered_frames:
        if ts == 0 and sub == 0 and evt == 0:
            continue # Порожній неініціалізований слот

        sub_name = SUBSYSTEMS.get(sub, f"0x{sub:02X}")
        evt_name = EVENTS.get(evt, f"0x{evt:02X}")
        status_str = "OK" if valid else "CRC_ERR"

        extra_info = ""
        if evt == 0xFE: # HardFault
            pc_addr = struct.unpack("<I", payload[:4])[0]
            fault_sym = resolve_symbol(elf_file, pc_addr)
            extra_info = f" | CRASH AT: {fault_sym}"
        else:
            extra_info = f" | Payload: {payload.hex()}"

        print(f"[{ts:8d} мс] [{sub_name:8s}] {evt_name:16s} (FSM=0x{fsm:04X}) [{status_str}]{extra_info}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Використання: python decode_blackbox.py <blackbox_dump.bin> [firmware.elf]")
        sys.exit(1)
    elf = sys.argv[2] if len(sys.argv) > 2 else ""
    parse_dump(sys.argv[1], elf)
```

---

## Інженерні пастки реалізації

1. **Когерентність кешу даних (D-Cache на ARM Cortex-M7):** Якщо на швидких мікроконтролерах (STM32F7, STM32H7, i.MX RT) увімкнено процесорний кеш даних D-Cache, ядро записує кадри подій у швидкий кеш, а не безпосередньо у фізичні комірки SRAM. Якщо аварійне скидання у SPI Flash виконується через автономний блок або контролер DMA, на носій будуть збережені застарілі дані з пам'яті. Перед передачею обов'язково викликається примусове очищення ліній кешу: `SCB_CleanDCache_by_Addr((uint32_t*)&g_bb_ram, sizeof(g_bb_ram))`.
2. **Використання покажчика стека в HardFault:** Найчастішою причиною аварійного виключення у програмах із FreeRTOS/Zephyr є переповнення стека потоку користувача (Process Stack Pointer, PSP). Якщо спробувати обробляти помилку всередині того ж стека PSP, ядро миттєво згенерує вторинний збій стекування (Stacking Fault) і впаде в стан мертвого зависання Lockup. Асемблерний перехідник `HardFault_Handler` завжди витягує збережений кадр і перемикається на гарантовано безпечний стек ядра (Main Stack Pointer, MSP).
3. **Гонки оновлення індексу в багатоядерних SoC (ESP32, RP2040):** У системах із двома незалежними ядрами стандартна функція блокування переривань `__disable_irq()` захищає критичну секцію лише на поточному ядрі, залишаючи можливість паралельного запису з другого ядра. Для атомарного захоплення слота буфера необхідно використовувати апаратний спінлок (Hardware Spinlock на RP2040) або атомарні операції `std::atomic<uint32_t>::fetch_add()` з бар'єром пам'яті `std::memory_order_acq_rel`.
