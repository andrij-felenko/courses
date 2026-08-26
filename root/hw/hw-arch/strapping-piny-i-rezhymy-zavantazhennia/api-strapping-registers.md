# 📋 Регістри засувок завантаження та Option Bytes

Апаратні логічні рівні на strapping-виводах опитуються кремнієвою логікою виключно у вузькому часовому вікні відпускання сигналу скидання. Щоб ці дані не втрачалися після переходу фізичних пінів у режим звичайного вводу-виводу (GPIO Matrix), контролер одразу зберігає їх у спеціальних системних регістрах апаратних засувок (Hardware Latches). Цей довідник надає повний опис карти пам'яті, адресних зміщень, масок бітових полів, процедур доступу та низькорівневих драйверів мовами C і C++ для зчитування стану завантаження на мікроконтролерах ESP32, STM32 та процесорах NXP i.MX RT.

---

### Фізична природа збереження засувок між доменами скидання

Системні регістри конфігурації завантаження прив'язані до найглибшого домену живлення кристала — домену *Power-On Reset (POR)* або домену постійного живлення *Always-On (AON)*. Це означає, що їхній вміст поводиться принципово інакше під час різних типів скидання:

1. **Холодний старт (Power-On Reset / Brownout Reset):** Напруга ядра з'являється вперше. Апаратна засувка відкривається у прозорий стан і за висхідним фронтом внутрішнього сигналу скидання перезаписує вміст регістра фактичними фізичними рівнями на зовнішніх пінах.
2. **М'який або програмний перезапуск (Software System Reset / Watchdog):** Якщо скидання ініційоване сторожовим таймером або викликом `NVIC_SystemReset()`, домен живлення AON не знеструмлюється. Більшість мікроконтролерів (зокрема STM32 та i.MX RT) зберігають попередньо зафіксовані біти засувок і не проводять повторного опитування зовнішніх пінів, якщо лінія зовнішнього апаратного скидання `NRST` не притискалася до нуля фізично.
3. **Вихід із глибокого сну (Deep Sleep Wakeup):** На чипах ESP32 контролер пробудження RTC перевіряє стан пінів відповідно до конфігурації в енергонезалежних регістрах RTC-домену, не скидаючи апаратний регулятор LDO Flash.

---

### ESP32: Системний регістр засувок GPIO_STRAP_REG

У класичному чипі ESP32 стан усіх конфігураційних виводів фіксується в 16-розрядному регістрі `GPIO_STRAP_REG`. Цей регістр розташований в адресному просторі периферійного модуля керування виводами (*GPIO Peripheral*) і доступний для ядра виключно в режимі читання (*Read-Only*). Спроба запису в цей регістр апаратно ігнорується.

#### Карта адрес та зміщень
- **Класичний ESP32 (ESP32-D0WDQ6, ESP32-WROOM):** базова адреса `0x3FF44038`
- **ESP32-S3 (Dual-Core Xtensa LX7):** базова адреса `0x60004038`
- **ESP32-C3 / ESP32-C6 (RISC-V ядро):** базова адреса `0x60004038`

#### Повний опис бітових полів (Класичний ESP32)

| Бітове поле | Назва макросу в ESP-IDF | Strapping Pin | Фізичне значення біта в засувці |
|:---:|:---|:---:|:---|
| `BIT(0)` | `GPIO_STRAP_BOOT_MODE` | `GPIO0` | `0`: Вхід у режим UART Download Mode (ROM чекає прошивку через COM-порт).<br>`1`: Нормальний запуск коду з SPI Flash. |
| `BIT(1)` | `GPIO_STRAP_UART_LOG` | `GPIO15` (`MTDO`) | `0`: Виведення налагоджувальних повідомлень ROM Bootloader у порт UART0 вимкнено.<br>`1`: Виведення початкового системного логу UART0 (115200 бод) увімкнено. |
| `BIT(2)` | `GPIO_STRAP_SDIO_PULL` | `GPIO2` | `0`: Нормальний режим для UART Download / SPI Flash Boot.<br>`1`: Разом із `GPIO0 = 0` перемикає чип у режим завантаження через SDIO Slave. |
| `BIT(3)` | `GPIO_STRAP_MTCK_FREQ` | `GPIO13` (`MTCK`) | Конфігурація дільника частоти тактування інтерфейсу SPI Flash під час виконання ROM-коду. |
| `BIT(4)` | `GPIO_STRAP_MTDO_PULL` | `GPIO15` (`MTDO`) | Задає таймінги затримки вихідних сигналів шини пам'яті (Flash driving delay). |
| `BIT(5)` | `GPIO_STRAP_VDD_SDIO` | `GPIO12` (`MTDI`) | `0`: Внутрішній регулятор LDO живить SPI Flash напругою **3.3 В** (штатний режим).<br>`1`: Внутрішній регулятор LDO перемикається на напругу **1.8 В** (Flash Brownout). |
| `BIT(15:6)` | `RESERVED` | — | Зарезервовано логікою кристала; при читанні повертає нулі. |

#### Специфіка сімейств ESP32-S3 та ESP32-C3
У новіших чипах призначення бітів у `GPIO_STRAP_REG` змінено:
- На **ESP32-S3** завантаження контролюється комбінацією `GPIO0` (`BIT(0)`) та `GPIO46` (`BIT(2)`). Якщо `GPIO0 = 0` та `GPIO46 = 0`, чип переходить у режим завантаження через вбудований USB-JTAG/Serial або UART.
- На **ESP32-C3** пін `GPIO8` (`BIT(1)`) разом із `GPIO9` (`BIT(2)`) визначає вибір між SPI Flash Boot (`GPIO9 = 1`) та ROM Serial Bootloader (`GPIO9 = 0`, `GPIO8 = 1`).

---

### STM32: Регістри конфігурації ремапу та Option Bytes

На платформі STM32 мікроконтролер не використовує єдиний опитуваний регістр стану пінів. Натомість логічний рівень на виводі `BOOT0` прямо керує комутацією внутрішньої системної шини (Memory Remap), що відображається у регістрах підсистеми `SYSCFG` та регістрах незмінної конфігурації Flash `FLASH->OPTR`.

#### 1. Регістр ремапу пам'яті (SYSCFG_MEMRMP)
Цей регістр відображає, яка саме фізична пам'ять спроєктована на адресу векторів скидання `0x00000000`.

- **Базова адреса (STM32F4/F7/G4/L4):** `0x40010000` (зсув `+0x00`)

| Біти `MEM_MODE[2:0]` | Фізична область на адресі `0x00000000` | Апаратна конфігурація пінів |
|:---:|:---|:---|
| `000` | **Main Flash Memory** (початок з `0x08000000`) | `BOOT0 = 0` (нормальний запуск) |
| `001` | **System Memory ROM** (початок з `0x1FFF0000`) | `BOOT0 = 1`, `BOOT1 = 0` (DFU / UART завантажувач) |
| `010` | **FSMC / FMC Bank 1** (зовнішня пам'ять NOR/PSRAM) | Апаратне конфігурування шини |
| `011` | **Embedded SRAM** (початок з `0x20000000`) | `BOOT0 = 1`, `BOOT1 = 1` (налагодження в RAM) |

#### 2. Регістр Option Bytes (FLASH_OPTR) на сучасних STM32 (G0, G4, L4+, H7)
У сучасних лінійках STM32 фізичні піни замінено програмно-апаратними прапорцями, що зберігаються у виділеному захищеному секторі Flash:

- **Базова адреса `FLASH_OPTR` (STM32G4):** `0x40022020`

| Біт | Символічне ім'я | Призначення та поведінка апаратури |
|:---:|:---|:---|
| `[23]` | `nSWBOOT0` | **Вибір джерела BOOT0:**<br>`0`: Рівень береться з фізичного виводу `BOOT0`.<br>`1`: Фізичний пін ігнорується, рівень визначається бітом `nBOOT0`. |
| `[24]` | `nBOOT0` | **Програмний рівень BOOT0 (активний нуль):**<br>`1`: Завантаження з Main Flash пам'яті (еквівалент `BOOT0 = 0`).<br>`0`: Завантаження з System Memory / SRAM. |
| `[25]` | `nBOOT1` | **Програмний рівень BOOT1:**<br>`1`: System Memory DFU Bootloader.<br>`0`: Пряме завантаження з Embedded SRAM. |
| `[26]` | `BOOT_LOCK` | **Апаратне блокування завантажувача:**<br>`1`: Примусовий старт виключно з Main Flash. Вхід у System Memory або SRAM апаратно заблоковано назавжди. |

#### Процедура зміни Option Bytes у прошивці
Зміна бітів конфігурації вимагає виконання суворої послідовності зняття захисту:

1. Записати ключі розблокування в регістр `FLASH->KEYR`: спочатку `0x45670123`, потім `0xCDEF89AB`.
2. Записати ключі розблокування Option Bytes в регістр `FLASH->OPTKEYR`: спочатку `0x08192A3B`, потім `0x4C5D6E7F`.
3. Змінити значення у регістрах `FLASH->OPTR`.
4. Встановити біт `OPTSTRT` у регістрі `FLASH->CR` для запуску циклу запису.
5. Дочекатися скидання біта зайнятості `BSY`.
6. Встановити біт `OBL_LAUNCH` для примусового перезавантаження чипа з новою конфігурацією завантаження.

---

### NXP i.MX RT: Регістри контролера скидання SRC_SBMR1 та SRC_SBMR2

Процесори сімейства NXP i.MX RT (RT1050, RT1060, RT1170) зберігають стан конфігураційних ліній `BOOT_CFG` у регістрах підсистеми *System Reset Controller (SRC)*.

- **`SRC_SBMR1` (System Boot Mode Register 1):** адреса `0x400F8004`
- **`SRC_SBMR2` (System Boot Mode Register 2):** адреса `0x400F801C`

#### Розподіл полів у регістрі SRC_SBMR1 (Піни BOOT_CFG1..BOOT_CFG4)
- **`[7:0]` (`BOOT_CFG1`):** Вибір інтерфейсу завантаження (`0x00` = FlexSPI NOR Flash, `0x08` = SD-картка, `0x10` = eMMC, `0x20` = NAND).
- **`[15:8]` (`BOOT_CFG2`):** Конфігурація шини даних (1-bit / 4-bit / 8-bit Quad/Octal SPI, режим тактування DTR/STR).
- **`[23:16]` (`BOOT_CFG3`):** Налаштування початкової частоти тактування зчитування образу.
- **`[31:24]` (`BOOT_CFG4`):** Параметри безпечного відновлення (*Recovery Boot Parameters*).

#### Розподіл полів у регістрі SRC_SBMR2
- **`BIT(4)` (`BT_FUSE_SEL`):** Стан прапорця одноразового програмування (`0` = завантаження за зовнішніми пінами `BOOT_CFG`, `1` = завантаження виключно за конфігурацією з внутрішніх OTP eFuse).
- **`[25:24]` (`BOOT_MODE[1:0]`):** Зафіксований стан базових конфігураційних виводів:
  * `0b00` — *Boot From Fuses* (прямий старт з eFuse);
  * `0b01` — *Serial Downloader* (аварійне оновлення через USB OTG / UART);
  * `0b10` — *Internal Boot* (завантаження з носія, обраного через `BOOT_CFG`);
  * `0b11` — *Reserved*.

---

### Діагностика через апаратний відлагоджувач (GDB / OpenOCD)

Коли мікроконтролер не виходить на зв'язок або зависає до виклику першого рядка коду, стан конфігураційних засувок зчитують напряму через інтерфейс SWD або JTAG без участі прошивки.

Для зчитування фізичного регістра засувок у сесії GDB виконують пряме читання пам'яті за адресою:

```text
(gdb) target remote :3333
(gdb) monitor reset halt
(gdb) x/1xw 0x3FF44038       # ESP32: читання GPIO_STRAP_REG
0x3ff44038: 0x00000013       # Біти: 0x13 = 0b010011 -> Flash Boot, 3.3V, UART Log ON

(gdb) x/1xw 0x40022020       # STM32G4: читання FLASH_OPTR
0x40022020: 0xfbff97aa       # Перевірка бітів nBOOT0 / nSWBOOT0

(gdb) x/1xw 0x400F8004       # i.MX RT: читання SRC_SBMR1
0x400f8004: 0x000000d0       # Поточна конфігурація FlexSPI NOR Flash
```

Ця команда дозволяє миттєво локалізувати апаратний дефект монтажу: якщо замість `0x00000013` регістр повертає `0x00000033` (піднятий біт 5), це однозначно свідчить про наявність паразитної підтяжки на піні `GPIO12`.

---

### Програмний драйвер діагностики завантаження на C та C++

Наведений нижче модуль зчитує регістри засувок на етапі старту прошивки та виконує валідацію апаратного стану.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

#define ESP32_GPIO_STRAP_REG_ADDR  0x3FF44038U

#define STRAP_MASK_BOOT_MODE       (1U << 0)
#define STRAP_MASK_UART_LOG        (1U << 1)
#define STRAP_MASK_SDIO_BOOT       (1U << 2)
#define STRAP_MASK_FLASH_1V8       (1U << 5)

typedef enum {
    STRAP_BOOT_SPI_FLASH   = 0,
    STRAP_BOOT_UART_ROM    = 1,
    STRAP_BOOT_SDIO_SLAVE  = 2,
    STRAP_BOOT_UNKNOWN     = 3
} Esp32BootMode;

typedef struct {
    uint32_t raw_register_value;
    Esp32BootMode boot_mode;
    bool is_flash_voltage_1v8;
    bool is_uart_log_active;
    bool is_hardware_safe;
} Esp32StrapReport;

Esp32StrapReport esp32_analyze_strapping_state(void) {
    volatile const uint32_t *strap_reg = (volatile const uint32_t *)ESP32_GPIO_STRAP_REG_ADDR;
    uint32_t raw = *strap_reg;
    
    Esp32StrapReport report;
    report.raw_register_value = raw;
    report.is_flash_voltage_1v8 = ((raw & STRAP_MASK_FLASH_1V8) != 0U);
    report.is_uart_log_active = ((raw & STRAP_MASK_UART_LOG) != 0U);

    bool gpio0 = ((raw & STRAP_MASK_BOOT_MODE) != 0U);
    bool gpio2 = ((raw & STRAP_MASK_SDIO_BOOT) != 0U);

    if (gpio0) {
        report.boot_mode = STRAP_BOOT_SPI_FLASH;
    } else if (!gpio2) {
        report.boot_mode = STRAP_BOOT_UART_ROM;
    } else {
        report.boot_mode = STRAP_BOOT_SDIO_SLAVE;
    }

    // Безпечним вважається лише запуск з Flash за нормальної напруги 3.3V
    report.is_hardware_safe = (report.boot_mode == STRAP_BOOT_SPI_FLASH) && (!report.is_flash_voltage_1v8);

    return report;
}
```
```cpp
#include <cstdint>
#include <bitset>
#include <expected>
#include <span>

namespace SystemDiagnostic {

enum class BootTarget : uint8_t {
    SpiFlashNormal,
    UartDownloadMode,
    SdioSlaveMode,
    Unknown
};

enum class HardwareError : uint8_t {
    FlashVoltageBrownout1V8,
    UnexpectedDownloadMode,
    InvalidBusConfiguration
};

struct StartupReport {
    uint32_t rawValue{0};
    BootTarget target{BootTarget::Unknown};
    bool flashVoltage1V8{false};
    bool romLogEnabled{false};

    [[nodiscard]] constexpr bool isSafeForProduction() const noexcept {
        return (target == BootTarget::SpiFlashNormal) && (!flashVoltage1V8);
    }
};

class StrappingDiagnostic {
public:
    static constexpr uintptr_t kEsp32StrapRegister = 0x3FF44038U;

    [[nodiscard]] static std::expected<StartupReport, HardwareError> evaluateSystemHealth() noexcept {
        auto* regAddress = reinterpret_cast<volatile const uint32_t*>(kEsp32StrapRegister);
        const uint32_t raw = *regAddress;
        std::bitset<32> bits(raw);

        StartupReport report{};
        report.rawValue = raw;
        report.flashVoltage1V8 = bits.test(5);
        report.romLogEnabled = bits.test(1);

        const bool gpio0 = bits.test(0);
        const bool gpio2 = bits.test(2);

        if (gpio0) {
            report.target = BootTarget::SpiFlashNormal;
        } else if (!gpio2) {
            report.target = BootTarget::UartDownloadMode;
        } else {
            report.target = BootTarget::SdioSlaveMode;
        }

        if (report.flashVoltage1V8) {
            return std::unexpected(HardwareError::FlashVoltageBrownout1V8);
        }

        if (report.target != BootTarget::SpiFlashNormal) {
            return std::unexpected(HardwareError::UnexpectedDownloadMode);
        }

        return report;
    }
};

} // namespace SystemDiagnostic
```
:::
