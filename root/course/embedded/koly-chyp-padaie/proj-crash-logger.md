# ⚙️ Реалізація діагностичного обробника HardFault і збереження дампу

Коли мікроконтролер стикається з фатальною помилкою, стандартний обробник `HardFault_Handler`, згенерований середовищем розробки за замовчуванням, зазвичай містить лише нескінченний порожній цикл `while(1)`. У реальному польовому пристрої це призводить або до «мертвого зависання» з подальшим спрацюванням сторожового таймера (який скидає чип і безслідно стирає всі сліди аварії в регістрах ядра), або до неконтрольованої поведінки виконавчих механізмів.

Щоб перетворити фатальне падіння на вичерпний діагностичний звіт, інженерна прошивка потребує трирівневої системи реєстрації:
1. **Асемблерний місток (Naked Trampoline):** вилучає коректний покажчик на збережений апаратурою стек-фрейм (`MSP` або `PSP`) до того, як компілятор C/C++ встигне змінити покажчик стека власним прологом функції.
2. **Аналітичний обробник (Fault Decoder):** зчитує системні регістри ядра SCB, розпаковує стековий фрейм (регістри `R0`–`R3`, `R12`, `LR`, `PC`, `xPSR`) і формує компактну бінарну структуру аварійного дампу (*Crash Dump*).
3. **Енергонезалежне збереження та керований перезапуск:** записує сформований дамп у спеціальну ділянку пам'яті, що не ініціалізується при старті (`.noinit` RAM) або виводить його через прямий синхронний оверлей UART без використання переривань, після чого виконує контрольоване перезавантаження чипа через `NVIC_SystemReset()`.

## Чому чистий C/C++ обробник спотворює стек

Обробник винятку в ARM Cortex-M є звичайною функцією з точки зору компілятора. Коли компілятор генерує код функції, він створює стандартний **пролог** (*function prologue*), який модифікує регістр `SP` (наприклад, інструкцією `PUSH {r4-r7, lr}` або виділенням місця під локальні змінні `SUB sp, sp, #32`). 

Якщо написати `void HardFault_Handler(void)` чистою мовою C або C++, до моменту виконання першого рядка вашого діагностичного коду покажчик стека `SP` вже зміститься. Ба більше, якщо програма використовує операційну систему реального часу (RTOS, наприклад FreeRTOS), користувацький код задач виконується з використанням стека процесу `PSP` (*Process Stack Pointer*), тоді як сам обробник винятку автоматично запускається ядром на головному стеку переривань `MSP` (*Main Stack Pointer*). 

Якщо прочитати регістр `SP` звичайним кодом C, ви отримаєте адресу вершини головного стека `MSP`, тоді як збережені значення `PC` та робочих регістрів аварії лежать у стеку `PSP` тієї конкретної задачі, яка зазнала збою.

Єдиний надійний спосіб розв'язання цієї проблеми — оголосити `HardFault_Handler` із атрибутом `__attribute__((naked))`. У таких функціях компілятор гарантовано не генерує жодних інструкцій прологу й епілогу. Це дозволяє за чотири асемблерні інструкції перевірити біт 2 у регістрі `LR` (`EXC_RETURN`) і передати точну адресу стек-фрейму як перший аргумент (`R0`) у функцію аналізу на C/C++.

## Врахування кадру співпроцесора FPU

Якщо в мікроконтролері активовано апаратний блок плаваючої крапки (Cortex-M4F, Cortex-M7), ядро підтримує механізм лінивого збереження контексту (*Lazy Stacking*). Залежно від того, чи виконувалися FPU-інструкції перед збоєм, апаратура зберігає або базовий 8-слівний кадр (32 байти), або розширений 26-слівний кадр (104 байти), куди входять регістри `S0`–`S15`, `FPSCR` та резервне слово вирівнювання.

Стан збереження FPU кодується бітом 4 у значенні `EXC_RETURN`:
- `EXC_RETURN & (1 << 4) == 0`: Збережено розширений кадр (FPU активний).
- `EXC_RETURN & (1 << 4) != 0`: Збережено стандартний базовий кадр (FPU не використовувався).

Якщо діагностичний код має намір знімати стан регістрів плаваючої крапки, покажчик на додатковий блок обчислюється додаванням зсуву `sizeof(FaultStackFrame)` (32 байти) до початкового покажчика стека.

## Налаштування лінкера: секція .noinit RAM

Щоб сформований аварійний дамп зберігся після програмного перезавантаження мікроконтролера, його необхідно розмістити у спеціальній секції пам'яті, яку стартовий код не очищає нулями. Для компіляторів GCC/Clang у скрипті лінкера (`linker.ld`) додається окрема секція з прапорцем `NOLOAD`:

```
.noinit (NOLOAD) :
{
    . = ALIGN(4);
    *(.noinit*)
    . = ALIGN(4);
} > RAM
```

Перед записом дамп маркується унікальним магічним числом `0xDEADBEEF` та контрольною сумою CRC32. Після наступного перезавантаження функція `main()` перевіряє сигнатуру та валідність CRC: якщо цілісність підтверджена, прошивка вичитує збережений звіт і передає його системі моніторингу або записує у Flash-пам'ять журналів.

## Захист від циклічного перезавантаження (Crash Loop Guard)

Якщо аварія стається на ранньому етапі ініціалізації (наприклад, під час конфігурації периферії або монтування файлової системи), система може потрапити в нескінченний цикл аварійних перезапусків (*Bootloop*). Кожен перезапуск викликає новий HardFault через кілька мілісекунд, що унеможливлює підключення відладчика або оновлення прошивки по повітрю (OTA).

Для запобігання цій ситуації в структуру `.noinit` пам'яті додають лічильник послідовних збоїв `boot_crash_counter`. Якщо лічильник перевищує поріг (наприклад, 3 або 5 падінь поспіль без тривалого періоду нормальної роботи), прошивка перемикається в аварійний безпечний режим (*Safe Recovery Mode*):
- Вимикаються всі силові приводи та радіомодулі.
- Зупиняється запуск основних RTOS-задач.
- Запускається мінімальний завантажувач для оновлення прошивки через UART/USB.

## Повна реалізація аварійного реєстратора

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "stm32f4xx.h"

// Структура збереженого апаратурою базового кадру стека ARM Cortex-M
typedef struct {
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r12;
    uint32_t lr;
    uint32_t pc;
    uint32_t psr;
} __attribute__((packed)) FaultStackFrame;

// Повний діагностичний дамп аварії для збереження в .noinit RAM
typedef struct {
    uint32_t magic;          // Маркер валідності дампу (0xDEADBEEF)
    uint32_t crash_count;    // Лічильник послідовних падінь (Crash Loop Guard)
    uint32_t reset_reason;   // Прапорці скидання RCC->CSR
    uint32_t hfsr;           // SCB->HFSR
    uint32_t cfsr;           // SCB->CFSR (UFSR + BFSR + MMFSR)
    uint32_t mmfar;          // SCB->MMFAR
    uint32_t bfar;           // SCB->BFAR
    uint32_t shcsr;          // SCB->SHCSR
    uint32_t exc_return;     // Значення LR на вході в обробник
    FaultStackFrame frame;   // Регістри R0-R3, R12, LR, PC, PSR
    uint32_t crc;            // Контрольна сума
} CrashDump;

#define CRASH_MAGIC 0xDEADBEEF
#define MAX_CRASH_LOOP_THRESHOLD 3

// Розміщення в секції .noinit, яка не очищається під час Reset
__attribute__((section(".noinit")))
static volatile CrashDump g_crash_dump;

// Проста реалізація контрольної суми для перевірки цілісності дампу
static uint32_t CalcCRC32(const uint8_t *data, uint32_t length) {
    uint32_t crc = 0xFFFFFFFF;
    for (uint32_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (uint32_t j = 0; j < 8; ++j) {
            if (crc & 1) {
                crc = (crc >> 1) ^ 0xEDB88320;
            } else {
                crc >>= 1;
            }
        }
    }
    return ~crc;
}

// Прямий синхронний вивід символу через UART (без переривань і DMA!)
static void UART_SendCharBlocking(char c) {
    // Очікуємо готовності передавача (TXE прапорець)
    while (!(USART1->SR & USART_SR_TXE)) {}
    USART1->DR = (uint8_t)c;
}

static void UART_SendStringBlocking(const char *str) {
    while (*str) {
        UART_SendCharBlocking(*str++);
    }
}

// C-частина обробника, яка отримує точний покажчик на стек
void HardFault_Handler_C(const FaultStackFrame *frame, uint32_t exc_return) {
    // Збільшуємо лічильник падінь або скидаємо, якщо магічне число пошкоджене
    uint32_t current_count = (g_crash_dump.magic == CRASH_MAGIC) ? g_crash_dump.crash_count + 1 : 1;

    // Заповнюємо дамп
    g_crash_dump.magic = CRASH_MAGIC;
    g_crash_dump.crash_count = current_count;
    g_crash_dump.reset_reason = RCC->CSR;
    g_crash_dump.hfsr = SCB->HFSR;
    g_crash_dump.cfsr = SCB->CFSR;
    g_crash_dump.mmfar = SCB->MMFAR;
    g_crash_dump.bfar = SCB->BFAR;
    g_crash_dump.shcsr = SCB->SHCSR;
    g_crash_dump.exc_return = exc_return;

    if (frame != NULL) {
        g_crash_dump.frame = *frame;
    }

    g_crash_dump.crc = CalcCRC32((const uint8_t *)&g_crash_dump, 
                                 sizeof(CrashDump) - sizeof(uint32_t));

    // Негайний синхронний вивід повідомлення для розробника
    UART_SendStringBlocking("\r\n[CRASH] Hardware fault captured, rebooting...\r\n");
    
    // Перезавантажуємо мікроконтролер для безпечного виходу з аварії
    NVIC_SystemReset();
}

// Асемблерний трамплін: визначає активний стек (MSP чи PSP)
__attribute__((naked)) void HardFault_Handler(void) {
    __asm volatile(
        "tst lr, #4                \n" // Перевіряємо біт 2 регістра LR (EXC_RETURN)
        "ite eq                    \n" // Якщо 0 (Equal) -> використовувався MSP
        "mrseq r0, msp             \n" // R0 = покажчик на стек MSP
        "mrsne r0, psp             \n" // Якщо 1 (Not Equal) -> R0 = покажчик PSP
        "mov r1, lr                \n" // R1 = значення EXC_RETURN
        "b HardFault_Handler_C     \n" // Перехід у функцію розбору з аргументами (R0, R1)
    );
}

// Перевірка та друк збереженого дампу після перезапуску в main()
bool CrashDump_ProcessOnStartup(void) {
    if (g_crash_dump.magic != CRASH_MAGIC) {
        return false;
    }

    uint32_t calc_crc = CalcCRC32((const uint8_t *)&g_crash_dump, 
                                  sizeof(CrashDump) - sizeof(uint32_t));
    if (calc_crc != g_crash_dump.crc) {
        g_crash_dump.magic = 0; // Дамп пошкоджено
        return false;
    }

    // Якщо зафіксовано цикл падінь — перехід у безпечний режим
    if (g_crash_dump.crash_count >= MAX_CRASH_LOOP_THRESHOLD) {
        UART_SendStringBlocking("[CRASH-LOOP] Too many crashes! Entering recovery mode.\r\n");
    }

    // Дамп валідний: тут виконується логування на Flash або передача на сервер
    // Очищаємо маркер після успішного опрацювання
    g_crash_dump.magic = 0;
    return true;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <string_view>
#include "stm32f4xx.h"

namespace crash::handler {

struct alignas(4) StackFrame {
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r12;
    uint32_t lr;
    uint32_t pc;
    uint32_t psr;
};

struct alignas(4) DumpRecord {
    uint32_t magic;
    uint32_t crash_count;
    uint32_t reset_reason;
    uint32_t hfsr;
    uint32_t cfsr;
    uint32_t mmfar;
    uint32_t bfar;
    uint32_t shcsr;
    uint32_t exc_return;
    StackFrame frame;
    uint32_t crc;
};

inline constexpr uint32_t MagicKey = 0xDEADBEEF;
inline constexpr uint32_t MaxCrashThreshold = 3;

// Розміщення в .noinit пам'яті
__attribute__((section(".noinit")))
inline volatile DumpRecord g_retained_dump;

[[nodiscard]] constexpr uint32_t compute_crc32(std::span<const uint8_t> data) noexcept {
    uint32_t crc = 0xFFFFFFFF;
    for (uint8_t byte : data) {
        crc ^= byte;
        for (size_t bit = 0; bit < 8; ++bit) {
            crc = (crc & 1) ? ((crc >> 1) ^ 0xEDB88320) : (crc >> 1);
        }
    }
    return ~crc;
}

inline void uart_transmit_blocking(std::string_view text) noexcept {
    for (char c : text) {
        while (!(USART1->SR & USART_SR_TXE)) {}
        USART1->DR = static_cast<uint8_t>(c);
    }
}

extern "C" void HardFault_Handler_Cpp(const StackFrame *frame, uint32_t exc_return) noexcept {
    const uint32_t count = (g_retained_dump.magic == MagicKey) ? g_retained_dump.crash_count + 1 : 1;

    g_retained_dump.magic = MagicKey;
    g_retained_dump.crash_count = count;
    g_retained_dump.reset_reason = RCC->CSR;
    g_retained_dump.hfsr = SCB->HFSR;
    g_retained_dump.cfsr = SCB->CFSR;
    g_retained_dump.mmfar = SCB->MMFAR;
    g_retained_dump.bfar = SCB->BFAR;
    g_retained_dump.shcsr = SCB->SHCSR;
    g_retained_dump.exc_return = exc_return;

    if (frame != nullptr) {
        g_retained_dump.frame = *frame;
    }

    const auto dump_bytes = std::span<const uint8_t>(
        reinterpret_cast<const uint8_t*>(&g_retained_dump),
        sizeof(DumpRecord) - sizeof(uint32_t)
    );
    g_retained_dump.crc = compute_crc32(dump_bytes);

    uart_transmit_blocking("\r\n[CRASH] Hardware fault captured, rebooting...\r\n");

    NVIC_SystemReset();
}

[[nodiscard]] inline bool process_retained_dump() noexcept {
    if (g_retained_dump.magic != MagicKey) {
        return false;
    }

    const auto dump_bytes = std::span<const uint8_t>(
        reinterpret_cast<const uint8_t*>(&g_retained_dump),
        sizeof(DumpRecord) - sizeof(uint32_t)
    );

    if (compute_crc32(dump_bytes) != g_retained_dump.crc) {
        g_retained_dump.magic = 0;
        return false;
    }

    if (g_retained_dump.crash_count >= MaxCrashThreshold) {
        uart_transmit_blocking("[CRASH-LOOP] Too many crashes! Safe boot engaged.\r\n");
    }

    g_retained_dump.magic = 0;
    return true;
}

} // namespace crash::handler

// Асемблерний трамплін
extern "C" __attribute__((naked)) void HardFault_Handler(void) {
    __asm volatile(
        "tst lr, #4                \n"
        "ite eq                    \n"
        "mrseq r0, msp             \n"
        "mrsne r0, psp             \n"
        "mov r1, lr                \n"
        "b HardFault_Handler_Cpp   \n"
    );
}
```
:::

## Правила безпеки в аварійному обробнику

1. **Жодних викликів функцій RTOS:** Під час виконання `HardFault` планувальник RTOS може бути пошкодженим, а перемикання контексту заблоковано пріоритетом винятку. Будь-яка спроба захопити м'ютекс (`xSemaphoreTake`) чи надіслати подію в чергу викличе повторний фатальний збій (*Double Fault*) і переведе ядро в стан незворотного зависання `Lockup`.
2. **Тільки блокуючий ввід/вивід:** Драйвери периферії, що спираються на переривання (наприклад, кільцеві буфери UART з перериваннями `USART_IT_TXE`), не працюватимуть, оскільки переривання з нижчим пріоритетом маскуються під час виконання HardFault. Дозволяється виключно прямий побайтовий запис у регістри периферії з очікуванням прапорців готовності.
3. **Мінімальний розмір локальних змінних:** Якщо причиною HardFault стало переповнення стека, обробник запускається на самому краю доступної пам'яті. Виділення великих локальних масивів на стеку викличе черговий збій захисту MPU або пам'яті. Усі діагностичні буфери повинні бути статичними або глобальними.
