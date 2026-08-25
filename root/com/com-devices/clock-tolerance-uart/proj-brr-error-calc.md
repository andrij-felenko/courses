# ⚙️ Розрахунок дільників BRR та верифікація бюджету похибки UART

Під час конфігурації апаратного периферійного модуля UART розробник записує розраховане значення дільника у спеціальний регістр швидкості (з англійської *Baud Rate Register*, `USART_BRR`). У перших поколіннях мікроконтролерів (зокрема класичних архітектурах 8051, PIC16 та ранніх AVR) дільник частоти був строго цілочисельним. При довільних тактових частотах процесора це породжувало велику похибку квантування, яка на стандартних швидкостях (наприклад, 115 200 бод при частоті ядра 8 МГц) сягала +8.5%, роблячи асинхронний зв'язок неможливим.

Сучасні 32-бітні мікроконтролери (зокрема сімейства STM32, ESP32, NXP LPC, SAM, TI MSPM0) оснащені апаратними генераторами швидкості з дробовим дільником (з англійської *fractional baud rate generator*). Вони дозволяють налаштовувати коефіцієнт ділення з роздільною здатністю в 1/16 або 1/64 частку такту. Проте неправильне розуміння апаратної структури регістрів, помилки в бітових масках або неврахування внутрішнього дрейфу RC-генератора призводять до спорадичних збоїв прийому, які вкрай важко локалізувати на етапі тестування.

Тут подано повний розбір схемотехніки дробових дільників різних мікроконтролерних платформ, механізмів налаштування нестандартних швидкостей у Linux (через `termios2` та `BOTHER`), апаратної конфігурації автовизначення швидкості (Auto-Baud), взаємодії з апаратним керуванням потоком (RTS/CTS), впливу розсинхронізації на потоки DMA та закінчену бібліотеку мовами C і C++, яка автоматизує обчислення бітів регістра `BRR`, оцінює сумарний бюджет похибки системи та формує інженерний вердикт щодо надійності зв'язку.

### Архітектура дільників швидкості в різних сімействах МК

Щоб написати універсальний калькулятор, необхідно розуміти, як різні виробники кремнію реалізують апаратне ділення тактової частоти.

#### 1. Архітектура з фіксованою комою (STM32 / ARM USART)
У мікроконтролерах компанії STMicroelectronics (серії STM32F1/F4/G4/H7) значення регістра `USART_BRR` є 16-бітним числом з фіксованою комою.
* У стандартному режимі передискретизації 16x (`OVER8 = 0`): старші 12 бітів (`BRR[15:4]`) містять цілу частину дільника (мантису), а молодші 4 біти (`BRR[3:0]`) — дробову частину з вагою `1/16 = 0.0625`.
* У швидкісному режимі передискретизації 8x (`OVER8 = 1`): мантиса зміщується, дробова частина займає лише 3 біти (`BRR[2:0]`) з вагою `1/8 = 0.125`, а біт `BRR[3]` повинен залишатися очищеним.

#### 2. Архітектура з генератором пропорційного пропуску (NXP LPC / FDR)
У мікроконтролерах NXP LPC застосовується двохетапне ділення: стандартний цілочисельний дільник `DLL/DLM` комбінується з дробовим дільником `FDR` (з англійської *Fractional Divider Register*). Регістр `FDR` містить два поля: `DIVADDVAL` (знаменник додавання) та `MULVAL` (множник). Коефіцієнт визначається як `1 + DIVADDVAL / MULVAL`. Генератор періодично поглинає або додає тактові імпульси, забезпечуючи точне середнє значення швидкості.

#### 3. Архітектура з акумулятором фази (ESP32 / TI CC13xx)
У бездротових контролерах ESP32 та TI CC13xx генератор бодрейту побудований на базі цифрового акумулятора фази (DDS). Регістр швидкості містить цілу частину дільника та 6-бітний або 8-бітний дріб. Апаратний лічильник накопичує дробову частину на кожному такті системної шини APB. Коли акумулятор переповнюється, тривалість поточного підтакту подовжується на один системний такт. Це забезпечує мінімальну похибку середньої швидкості (менше 0.05%), хоча окремі біти мають мікроскопічний фазовий джитер у межах одного такту APB.

#### 4. Режим подвійної швидкості (AVR U2X)
У класичних мікроконтролерах AVR (ATmega328P, ATmega2560) дільник `UBRR` є строго цілочисельним. Проте регістр `UCSRnA` містить біт `U2Xn` (з англійської *Double the USART Transmission Speed*). Встановлення цього біта зменшує коефіцієнт передискретизації з 16 до 8, змінюючи формулу дільника з `F_cpu / (16 · Baud) - 1` на `F_cpu / (8 · Baud) - 1`. Це дозволяє вдвічі зменшити абсолютну похибку квантування для високих швидкостей ціною звуження вікна стробування.

### Апаратне автовизначення швидкості (Auto-Baud у STM32)

Сучасні модулі USART містять вбудований апаратний блок автокалібрування `ABR` (з англійської *Auto Baud Rate Detection*), керований бітом `USART_CR2_ABREN`. Контролер підтримує чотири режими вимірювання швидкості за допомогою бітів `ABRMODE[1:0]`:

* `00` (Mode 0) — вимірювання тривалості старт-біта від спадного до наростаючого фронту (інтервал `1 · T_bit`).
* `01` (Mode 1) — вимірювання інтервалу від спадного фронту старт-біта до наступного спадного фронту даних (корисно для фіксованих преамбул).
* `10` (Mode 2) — автокалібрування за кадром `0x7F` (послідовність з семи нулів та одиниці, тривалість `7 · T_bit`).
* `11` (Mode 3) — автокалібрування за символом `0x55` (чергування 01010101b, тривалість `8 · T_bit`).

Апаратний лічильник автоматично обчислює значення мантиси й дробу і безпосередньо перезаписує регістр `USART_BRR`, встановлюючи прапорець `USART_ISR_ABRF`. Це дозволяє підтримувати надійний зв'язок навіть при екстремальному дрейфі внутрішнього RC-генератора без участі основного процесора.

### Апаратне керування потоком (RTS/CTS) та помилки тактування

Поширена ілюзія серед розробників полягає в тому, що ввімкнення апаратного керування потоком (з англійської *Hardware Flow Control*, сигнали RTS/CTS) здатне вирішити проблеми з розсинхронізацією швидкості.

На практиці лінії RTS/CTS працюють на рівні цілих байтів:
* Передавач перевіряє лінію CTS перед початком передачі чергового кадру.
* Приймач піднімає лінію RTS, коли його вхідний апаратний буфер FIFO заповнений.

Апаратний потік запобігає переповненню буфера (`Overrun Error`), але не має жодного впливу на бітовий тайминг усередині самого кадру. Якщо тактова частота передавача відрізняється від приймача на 5%, строб все одно зсунеться в зону фронту на бітах D7 або Stop, викликавши помилку кадру (`Framing Error`), навіть за умови ідеальної роботи ліній RTS/CTS. Тому апаратний потік є засобом узгодження продуктивності програмного стека, а не заміною точного джерела тактування.

### Вплив помилок тактування на апаратний DMA

У високонавантажених системах прийом даних здійснюється через прямий доступ до пам'яті (DMA) у кільцевий буфер. Коли через накопичення похибки частоти виникає помилка обрамлення (`Framing Error`), апаратний модуль UART поводиться наступним чином:

1. Спотворений байт все одно поміщається в регістр даних `RDR` і передається контролеру DMA.
2. Контролер DMA записує байт у пам'ять і збільшує покажчик адреси.
3. Одночасно UART піднімає прапорець переривання помилки `FE` у регістрі статусу `ISR`.

Якщо прошивка не обробляє переривання помилок кадру, збій навіть одного байта зміщує зміщення структури пакета в пам'яті (зсув заголовків, довжини та CRC). Наступні цілком валідні байти записуються з фазовим зсувом на один байт, що призводить до відкидання всіх наступних пакетів контрольною сумою. Тому надійний драйвер UART з DMA завжди повинен скидати покажчик буфера при виникненні події `FE`.

### Нестандартні швидкості в операційній системі Linux (termios2)

У вбудованих комп'ютерах під керуванням Linux (Single Board Computers, SBC на базі Allwinner, Rockchip, i.MX, Raspberry Pi) стандартний інтерфейс POSIX `termios` обмежує вибір швидкості фіксованими константами (B9600, B115200, B921600). Якщо периферійний давач або мікроконтролер працює на специфічній частоті (наприклад, 250 000 бод для DMX512 або 100 000 бод для протоколу Futaba S.BUS), стандартний виклик `cfsetspeed()` повертає помилку `EINVAL`.

Для налаштування довільної швидкості в сучасному ядрі Linux використовується розширений інтерфейс `termios2` через системний виклик `ioctl()` з прапорцем `BOTHER`:

:::tabs
```c
#include <asm/termbits.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdbool.h>

bool set_custom_baudrate_c(int fd, unsigned int custom_baud) {
    struct termios2 tio;
    if (ioctl(fd, TCGETS2, &tio) < 0) {
        return false;
    }
    
    /* Скидаємо маску стандартної швидкості та встановлюємо довільну */
    tio.c_cflag &= ~CBAUD;
    tio.c_cflag |= BOTHER;
    tio.c_ispeed = custom_baud;
    tio.c_ospeed = custom_baud;
    
    return (ioctl(fd, TCSETS2, &tio) >= 0);
}
```
```cpp
#include <asm/termbits.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <unistd.h>
#include <expected>
#include <string_view>

namespace linux_uart {

[[nodiscard]] std::expected<void, std::string_view> setCustomBaudrate(int fd, unsigned int customBaud) noexcept {
    termios2 tio{};
    if (::ioctl(fd, TCGETS2, &tio) < 0) {
        return std::unexpected{"Failed to get termios2 configuration"};
    }

    tio.c_cflag &= ~CBAUD;
    tio.c_cflag |= BOTHER;
    tio.c_ispeed = customBaud;
    tio.c_ospeed = customBaud;

    if (::ioctl(fd, TCSETS2, &tio) < 0) {
        return std::unexpected{"Failed to set custom baud rate via TCSETS2"};
    }
    return {};
}

} // namespace linux_uart
```
:::

Драйвер ядра Linux автоматично перераховує регістри дробового дільника апаратного контролера UART (наприклад, DesignWare APB UART або Cadence UART), мінімізуючи залишок квантування.

### Математичний алгоритм розрахунку регістра BRR

Нехай на периферійний модуль UART надходить тактова частота `F_pclk` (у герцах), необхідна швидкість обміну становить `Target_Baud`, а апаратний коефіцієнт передискретизації дорівнює `Oversampling` (16 або 8).

Ідеальне дійсне значення дільника:

```
DIV_exact = F_pclk / (Oversampling · Target_Baud)
```

Якщо `DIV_exact < 1.0`, обрана тактова частота шини є недостатньою для досягнення цільової швидкості (потрібно підвищити `F_pclk` або знизити швидкість).

Для переведення у формат із фіксованою комою з кількістю дробових бітів `FRACT_BITS` (де коефіцієнт масштабування `Scale = 2^(FRACT_BITS)`):

```
DIV_scaled = round(DIV_exact · Scale)
Mantissa   = DIV_scaled >> FRACT_BITS
Fraction   = DIV_scaled & (Scale - 1)
```

Застосування математичного округлення `round()` замість простого відсікання дробу `floor()` є критично важливим: воно гарантує вибір найближчого можливого апаратного значення та мінімізує залишок похибки квантування.

Фактична швидкість і відносна похибка обчислюються за формулами:

```
DIV_actual  = Mantissa + Fraction / Scale
Baud_actual = F_pclk / (Oversampling · DIV_actual)
Error_brr   = (Baud_actual - Target_Baud) / Target_Baud · 100%
```

### Реалізація калькулятора мовами C та C++

Наведений нижче програмний модуль реалізує повноцінний інженерний аналіз: він не лише розраховує бітові поля регістра `BRR`, але й зіставляє сумарну похибку вузлів (з урахуванням типу генератора, температури, старт-біт квантування та формату кадру) з теоретичною границею збою.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/* Тип джерела тактування вузла */
typedef enum {
    CLK_SOURCE_CRYSTAL_XTAL,  /* Кварцовий резонатор (±30 ppm) */
    CLK_SOURCE_CERAMIC_RES,   /* Керамічний резонатор (±0.5%) */
    CLK_SOURCE_INTERNAL_RC    /* Внутрішній RC-генератор (±2.5%) */
} clock_source_t;

/* Формат кадру UART */
typedef enum {
    UART_FRAME_8N1,           /* 10 бітів: Start, 8 Data, Stop */
    UART_FRAME_8E1_8O1_8N2,   /* 11 бітів: Start, 8 Data, Parity, Stop */
    UART_FRAME_9E1            /* 12 бітів: Start, 9 Data, Parity, Stop */
} uart_frame_format_t;

/* Результат розрахунку регістра BRR */
typedef struct {
    uint32_t mantissa;
    uint32_t fraction;
    uint32_t brr_reg_value;
    double actual_baud;
    double brr_error_percent;
    double total_system_error;
    double max_allowable_error;
    bool is_communication_reliable;
} uart_brr_calc_result_t;

/* Повертає типову нестабільність генератора у відсотках */
static double get_clock_drift_percent(clock_source_t source) {
    switch (source) {
        case CLK_SOURCE_CRYSTAL_XTAL: return 0.005; /* ±50 ppm */
        case CLK_SOURCE_CERAMIC_RES:  return 0.500; /* ±0.5% */
        case CLK_SOURCE_INTERNAL_RC:  return 2.500; /* ±2.5% */
        default:                      return 1.000;
    }
}

/* Повертає максимальну допустиму сумарну похибку для заданого формату кадру */
static double get_max_allowable_error(uart_frame_format_t format, uint32_t oversampling) {
    double n_bits;
    switch (format) {
        case UART_FRAME_8N1:         n_bits = 10.0; break;
        case UART_FRAME_8E1_8O1_8N2: n_bits = 11.0; break;
        case UART_FRAME_9E1:         n_bits = 12.0; break;
        default:                     n_bits = 10.0; break;
    }

    /* Ефективне напіввікно з урахуванням квантування старт-біта та апертури фільтра */
    double w_eff = (oversampling == 16) ? 0.40625 : 0.31250;
    return (w_eff / (n_bits - 0.5)) * 100.0;
}

/* Розрахунок параметрів регістра BRR та верифікація сумарної похибки */
bool calculate_uart_brr(uint32_t pclk_hz,
                        uint32_t target_baud,
                        uint32_t oversampling,
                        uint32_t fract_bits,
                        clock_source_t tx_clk,
                        clock_source_t rx_clk,
                        uart_frame_format_t frame_format,
                        uart_brr_calc_result_t *out_result) {
    if (out_result == NULL || pclk_hz == 0 || target_baud == 0) {
        return false;
    }
    if (oversampling != 8 && oversampling != 16) {
        return false;
    }

    /* 1. Ідеальний коефіцієнт ділення */
    double div_exact = (double)pclk_hz / ((double)oversampling * (double)target_baud);
    if (div_exact < 1.0) {
        /* Частота PCLK занизька для цієї швидкості */
        return false;
    }

    /* 2. Квантування у форматі з фіксованою комою */
    uint32_t fract_scale = 1u << fract_bits;
    uint32_t div_scaled = (uint32_t)round(div_exact * (double)fract_scale);

    out_result->mantissa = div_scaled >> fract_bits;
    out_result->fraction = div_scaled & (fract_scale - 1u);

    if (out_result->mantissa == 0) {
        return false;
    }

    /* Формування значення апаратного регістра (наприклад, USART_BRR для STM32) */
    out_result->brr_reg_value = (out_result->mantissa << fract_bits) | out_result->fraction;

    /* 3. Фактично згенерована швидкість та похибка квантування */
    double div_actual = (double)out_result->mantissa + ((double)out_result->fraction / (double)fract_scale);
    out_result->actual_baud = (double)pclk_hz / ((double)oversampling * div_actual);
    out_result->brr_error_percent = ((out_result->actual_baud - (double)target_baud) / (double)target_baud) * 100.0;

    /* 4. Сумарний розрахунок бюджету похибки */
    double tx_drift = get_clock_drift_percent(tx_clk);
    double rx_drift = get_clock_drift_percent(rx_clk);

    /* Сума похибок: дільник + генератор TX + генератор RX */
    out_result->total_system_error = fabs(out_result->brr_error_percent) + tx_drift + rx_drift;
    out_result->max_allowable_error = get_max_allowable_error(frame_format, oversampling);

    /* Запас надійності: система стабільна, якщо сумарна похибка нижча за критичну межу */
    out_result->is_communication_reliable = (out_result->total_system_error <= out_result->max_allowable_error);

    return true;
}

/* Друк розгорнутого звіту розрахунку */
void print_uart_report(const uart_brr_calc_result_t *res, uint32_t pclk, uint32_t target_baud) {
    printf("============================================================\n");
    printf(" ЗВІТ РОЗРАХУНКУ ТАКТУВАННЯ ТА БЮДЖЕТУ ПОХИБКИ UART\n");
    printf("============================================================\n");
    printf(" Тактова частота PCLK     : %u Гц (%.3f МГц)\n", pclk, pclk / 1e6);
    printf(" Цільова швидкість (Baud) : %u бод\n", target_baud);
    printf(" Мантиса дільника         : %u\n", res->mantissa);
    printf(" Дробова частина          : %u / 16 (0x%X)\n", res->fraction, res->fraction);
    printf(" Регістр USART_BRR        : 0x%04X\n", res->brr_reg_value);
    printf(" Фактична швидкість       : %.2f бод\n", res->actual_baud);
    printf(" Похибка дільника BRR     : %+.3f %%\n", res->brr_error_percent);
    printf(" Сумарна похибка системи  : %.3f %%\n", res->total_system_error);
    printf(" Гранично допустима межа  : %.3f %%\n", res->max_allowable_error);
    printf("------------------------------------------------------------\n");
    if (res->is_communication_reliable) {
        printf(" ВЕРДИКТ: [ НАДІЙНО ] Зв'язок гарантовано стабільний.\n");
    } else {
        printf(" ВЕРДИКТ: [ НЕБЕЗПЕКА ] Ризик Framing Error! Перевищено допуск.\n");
    }
    printf("============================================================\n\n");
}
```
```cpp
#include <iostream>
#include <iomanip>
#include <cmath>
#include <cstdint>
#include <optional>
#include <string_view>

namespace uart_tools {

enum class ClockSource {
    CrystalXtal,    // Кварцовий резонатор (±30..50 ppm)
    CeramicRes,     // Керамічний резонатор (±0.5%)
    InternalRc      // Внутрішній RC-генератор (±2.5%)
};

enum class FrameFormat {
    Frame8N1,           // 10 бітів: Start, 8 Data, Stop
    Frame8E1_8O1_8N2,   // 11 бітів: Start, 8 Data, Parity, Stop
    Frame9E1            // 12 бітів: Start, 9 Data, Parity, Stop
};

struct CalculationConfig {
    uint32_t pclkHz{16'000'000};
    uint32_t targetBaud{115'200};
    uint32_t oversampling{16};
    uint32_t fractBits{4};
    ClockSource txClock{ClockSource::InternalRc};
    ClockSource rxClock{ClockSource::CrystalXtal};
    FrameFormat format{FrameFormat::Frame8N1};
};

struct BaudRateResult {
    uint32_t mantissa{0};
    uint32_t fraction{0};
    uint32_t rawRegisterValue{0};
    double actualBaud{0.0};
    double quantizationErrorPercent{0.0};
    double totalSystemErrorPercent{0.0};
    double maxAllowableErrorPercent{0.0};
    bool isReliable{false};
};

class BaudRateCalculator {
public:
    [[nodiscard]] static constexpr double getClockDriftPercent(ClockSource source) noexcept {
        switch (source) {
            case ClockSource::CrystalXtal: return 0.005; // ±50 ppm
            case ClockSource::CeramicRes:  return 0.500; // ±0.5%
            case ClockSource::InternalRc:  return 2.500; // ±2.5%
        }
        return 1.0;
    }

    [[nodiscard]] static constexpr double getMaxAllowableError(FrameFormat format, uint32_t oversampling) noexcept {
        const double nBits = [format]() {
            switch (format) {
                case FrameFormat::Frame8N1:         return 10.0;
                case FrameFormat::Frame8E1_8O1_8N2: return 11.0;
                case FrameFormat::Frame9E1:         return 12.0;
            }
            return 10.0;
        }();

        const double wEff = (oversampling == 16) ? 0.40625 : 0.31250;
        return (wEff / (nBits - 0.5)) * 100.0;
    }

    [[nodiscard]] static std::optional<BaudRateResult> calculate(const CalculationConfig& cfg) noexcept {
        if (cfg.pclkHz == 0 || cfg.targetBaud == 0) {
            return std::nullopt;
        }
        if (cfg.oversampling != 8 && cfg.oversampling != 16) {
            return std::nullopt;
        }

        const double divExact = static_cast<double>(cfg.pclkHz) /
                                (static_cast<double>(cfg.oversampling) * static_cast<double>(cfg.targetBaud));
        if (divExact < 1.0) {
            return std::nullopt;
        }

        const uint32_t fractScale = 1u << cfg.fractBits;
        const auto divScaled = static_cast<uint32_t>(std::round(divExact * static_cast<double>(fractScale)));

        BaudRateResult res;
        res.mantissa = divScaled >> cfg.fractBits;
        res.fraction = divScaled & (fractScale - 1u);

        if (res.mantissa == 0) {
            return std::nullopt;
        }

        res.rawRegisterValue = (res.mantissa << cfg.fractBits) | res.fraction;

        const double divActual = static_cast<double>(res.mantissa) +
                                 (static_cast<double>(res.fraction) / static_cast<double>(fractScale));
        res.actualBaud = static_cast<double>(cfg.pclkHz) / (static_cast<double>(cfg.oversampling) * divActual);
        res.quantizationErrorPercent = ((res.actualBaud - static_cast<double>(cfg.targetBaud)) /
                                        static_cast<double>(cfg.targetBaud)) * 100.0;

        const double txDrift = getClockDriftPercent(cfg.txClock);
        const double rxDrift = getClockDriftPercent(cfg.rxClock);

        res.totalSystemErrorPercent = std::abs(res.quantizationErrorPercent) + txDrift + rxDrift;
        res.maxAllowableErrorPercent = getMaxAllowableError(cfg.format, cfg.oversampling);
        res.isReliable = (res.totalSystemErrorPercent <= res.maxAllowableErrorPercent);

        return res;
    }

    static void printReport(const CalculationConfig& cfg, const BaudRateResult& res) {
        std::cout << "============================================================\n";
        std::cout << " ЗВІТ РОЗРАХУНКУ ТАКТУВАННЯ ТА БЮДЖЕТУ ПОХИБКИ UART (C++)\n";
        std::cout << "============================================================\n";
        std::cout << std::fixed << std::setprecision(3);
        std::cout << " Тактова частота PCLK     : " << cfg.pclkHz << " Гц (" << (cfg.pclkHz / 1e6) << " МГц)\n";
        std::cout << " Цільова швидкість (Baud) : " << cfg.targetBaud << " бод\n";
        std::cout << " Мантиса дільника         : " << res.mantissa << "\n";
        std::cout << " Дробова частина          : " << res.fraction << " / 16\n";
        std::cout << " Регістр USART_BRR        : 0x" << std::hex << std::uppercase << res.rawRegisterValue << std::dec << "\n";
        std::cout << std::setprecision(2);
        std::cout << " Фактична швидкість       : " << res.actualBaud << " бод\n";
        std::cout << std::setprecision(3);
        std::cout << " Похибка дільника BRR     : " << std::showpos << res.quantizationErrorPercent << " %\n" << std::noshowpos;
        std::cout << " Сумарна похибка системи  : " << res.totalSystemErrorPercent << " %\n";
        std::cout << " Гранично допустима межа  : " << res.maxAllowableErrorPercent << " %\n";
        std::cout << "------------------------------------------------------------\n";
        if (res.isReliable) {
            std::cout << " ВЕРДИКТ: [ НАДІЙНО ] Зв'язок гарантовано стабільний.\n";
        } else {
            std::cout << " ВЕРДИКТ: [ НЕБЕЗПЕКА ] Ризик Framing Error! Перевищено допуск.\n";
        }
        std::cout << "============================================================\n\n";
    }
};

} // namespace uart_tools
```
:::

### Детальний розбір реальних інженерних сценаріїв

Розглянемо три типові ситуації, з якими стикаються розробники вбудованих систем, та проаналізуємо поведінку калькулятора.

#### Сценарій 1: STM32 на внутрішньому RC проти FTDI-перехідника на 921 600 бод
Розробник налагоджує швидкісну передачу телеметрії між мікроконтролером STM32G4 (`PCLK = 16 МГц` від внутрішнього HSI) та комп'ютером через адаптер FTDI FT232R на швидкості 921 600 бод (формат 8N1).

1. Розрахунок дільника:
   `DIV_exact = 16 000 000 / (16 · 921 600) = 1.085069`.
   Множимо на 16: `1.085069 · 16 = 17.361`. Округлюємо до 17 (`0x11`): мантиса `1`, дріб `1/16 = 0.0625`.
   Значення регістра: `USART_BRR = 0x0011`.
2. Фактична швидкість:
   `Baud_actual = 16 000 000 / (16 · 1.0625) = 941 176.47 бод`.
   Похибка квантування: `+2.124%`.
3. Оцінка бюджету:
   Власний температурний дрейф HSI при кімнатній температурі становить близько `±1.0%`, а при нагріванні чіпа зростає до `±2.5%`. Кварц FTDI дає похибку `< 0.01%`.
   Сумарна похибка: `2.124% + 2.500% = 4.624%`.
   Гранично допустима межа для 10-бітного кадру: `4.276%`.
4. Результат: пристрій періодично губить байти або піднімає прапорець `USART_ISR_FE` (Framing Error).
5. Інженерне рішення: перейти на передискретизацію 8x (`OVER8 = 1`), збільшити частоту шини `PCLK` через PLL до 64 МГц або встановити зовнішній кварцовий резонатор.

#### Сценарій 2: Довга промислова лінія Modbus RTU (RS-485, 11-бітний кадр 8E1)
У мережі Modbus RTU стандартним є кадр із бітом парності: 1 старт-біт, 8 бітів даних, 1 біт парності (Even), 1 стоп-біт (разом 11 бітів). Швидкість — 19 200 бод, тактова частота мікроконтролера — 48 МГц (кварц).

1. Розрахунок дільника:
   `DIV_exact = 48 000 000 / (16 · 19 200) = 156.250`.
   Мантиса `156` (`0x9C`), дріб `4/16 = 0.250` (`0x4`).
   Значення регістра: `USART_BRR = 0x09C4`.
   Похибка квантування дільника: строго `0.000%`.
2. Вплив лінії:
   Довгий кабель (300 метрів) з ємністю `50 пФ/м` формує завал фронтів через паразитну RC-ланку та оптопари гальванічної розв'язки (`ε_slew ≈ 8%`).
3. Оцінка бюджету:
   Завдяки нульовій похибці кварцу та ідеальному коефіцієнту ділення вся доступна смуга стробування залишається вільною для компенсації аналогових спотворень кабелю. Зв'язок працює надійно.

#### Сценарій 3: GPS/ГНСС модуль на швидкості 9600 бод при живленні від батареї
Автономний трекер на базі енергоефективного контролера тактується від низькочастотного генератора 4 МГц для економії заряду.

1. Розрахунок дільника:
   `DIV_exact = 4 000 000 / (16 · 9600) = 26.041666`.
   Мантиса `26` (`0x1A`), дріб `1/16 = 0.0625` (`0x1`).
   Значення регістра: `USART_BRR = 0x01A1`.
2. Фактична швидкість:
   `Baud_actual = 4 000 000 / (16 · 26.0625) = 9592.33 бод`.
   Похибка дільника: `-0.080%`.
3. Оцінка бюджету:
   Оскільки на низькій швидкості 9600 бод тривалість біта становить `104.17 мкс`, завал фронтів навіть у 1 мкс становить менше 1% від інтервалу. Система зберігає високу стійкість навіть при живленні від нестабільного джерела.

### Простеження та діагностика апаратних збоїв (Tracepoints)

Коли на лінії виникає розсинхронізація, контролер UART генерує апаратні прапорці стану. Розуміння їхньої природи дозволяє швидко локалізувати причину:

1. Прапорець `FE` (з англійської *Framing Error*): встановлюється, коли в момент стробування стоп-біта лінія перебуває на рівні логічного нуля замість обов'язкової одиниці. Це головний індикатор накопичення фазової похибки понад 4.5%.
2. Прапорець `NE` (з англійської *Noise Error*): встановлюється апаратним мажоритарним селектором (3-of-16), якщо три контрольні відліки (7, 8, 9) дали неоднаковий результат (наприклад, 0-1-1 або 1-0-1). Це сигналізує, що строб потрапив безпосередньо на фронт перехідного процесу.
3. Прапорець `ORE` (з англійської *Overrun Error*): виникає, коли новий байт прибув до того, як процесор встиг прочитати попередній з регістра `RDR`. Часто є наслідком того, що занадто швидкий передавач шле дані без міжкадрового інтервалу.

### Методика лабораторного вимірювання швидкості за допомогою осцилографа

Для перевірки реальної швидкості передавача на практиці застосовують наступну методику:
1. Передавач налаштовується на безперервну передачу тестового байта `0x55` (ASCII символ 'U').
2. На екрані цифрового осцилографа або логічного аналізатора захоплюється сигнал TX. Символ `0x55` формує рівномірний меандр з 5 періодів (включаючи старт-біт «0» та стоп-біт «1»).
3. Маркерами вимірюється сумарний час `T_8bits` між першим спадним фронтом старт-біта та останнім наростаючим фронтом стоп-біта (інтервал рівно 8 або 9 бітів).
4. Фактична швидкість розраховується як `Baud_meas = 8 / T_8bits`. Порівняння з номіналом дає точне значення похибки генератора передавача.

### Типові програмні та апаратні пастки

#### 1. Плутанина між SYSCLK та PCLK
У мікроконтролерах з розвиненою шинною матрицею (наприклад, шини `AHB`, `APB1`, `APB2` в архітектурі STM32) частота живлення периферійного блоку `PCLK` часто ділиться внутрішніми прескалерами шини (`RCC_CFGR_PPRE1`). Наприклад, при загальній частоті ядра `SYSCLK = 168 МГц` шина `APB1` може працювати на `42 МГц` (`PPRE1 = /4`). Якщо програміст використовує у формулі глобальну константу `SystemCoreClock` замість реальної частоти шини таймера, розрахована швидкість UART буде відрізнятися в 4 рази.

#### 2. Прямий запис без округлення (Integer Truncation)
Класична помилка при написанні власного коду ініціалізації полягає у відкиданні дробу цілочисельним діленням: при `PCLK = 8 МГц` та `Baud = 115200` маємо `8000000 / 1843200 = 4.3402`. Просте ділення дасть коефіцієнт 4 замість найближчого значення, що спричинить похибку швидкості +8.51%.

:::tabs
```c
/* Некоректно: усікання дробу (похибка +8.51%) */
uint32_t brr_bad = pclk / (16 * baud);

/* Коректно: цілочисельне округлення до найближчого цілого */
uint32_t brr_good = (pclk + (16 * baud) / 2) / (16 * baud);
```
```cpp
// Некоректно: усікання дробу
constexpr auto calcBrrTrunc(uint32_t pclk, uint32_t baud) noexcept -> uint32_t {
    return pclk / (16 * baud);
}

// Коректно: математичне округлення
constexpr auto calcBrrRound(uint32_t pclk, uint32_t baud) noexcept -> uint32_t {
    return (pclk + (16 * baud) / 2) / (16 * baud);
}
```
:::

#### 3. Некоректна маска бітів при перемиканні в режим OVER8
У контролерах STM32F4/F7/G4 біт `OVER8` у регістрі `USART_CR1` вмикає передискретизацію 8x. При цьому бітова структура регістра `BRR` модифікується: дробова частина займає біти `BRR[2:0]`, біт `BRR[3]` повинен залишатися в 0, а біти мантиси зсуваються на один розряд ліворуч (`BRR[15:4]` стає мантисою, але записується зі зміщенням). Якщо записати стандартне 4-бітне дробове значення, біт 3 спотворить молодший біт мантиси, викликавши стрибок швидкості.

#### 4. Неврахування затримки тактування при виході зі сплячих режимів (Stop / Sleep)
При пробудженні мікроконтролера за старт-бітом UART внутрішній RC-генератор (HSI/HSI16) потребує від 2 до 5 мікросекунд на стабілізацію амплітуди коливань (з англійської *oscillator startup time*). Якщо передавач починає передавати дані негайно після спаду лінії, перші 1–2 біти кадру будуть зчитані на нестабільній, заниженій частоті, що неминуче призведе до помилки кадру. Для запобігання цій проблемі протокол повинен передбачати преамбулу пробудження або затримку перед передачею корисного навантаження.
