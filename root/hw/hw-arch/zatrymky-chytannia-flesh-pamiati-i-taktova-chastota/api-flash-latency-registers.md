# 📋 Регістри затримок Flash та конфігурація живлення

Цей довідник містить вичерпний апаратний опис регістрового інтерфейсу контролера вбудованої Flash-пам'яті (Flash Access Control Register, `FLASH_ACR`), його бітових полів керування затримками (Wait States), чергою попередньої вибірки (Prefetch Buffer), апаратним прискорювачем кешування інструкцій та даних (ART Accelerator), а також нормативні таблиці залежності затримок від напруги живлення ядра мікроконтролера. Безпосередній доступ до цих регістрів критично необхідний під час написання системного стартапу, низькорівневих драйверів керування тактуванням (RCC) та модулів динамічного масштабування енергоспоживання (DVFS).

## Карта регістрів інтерфейсу контролера Flash

Інтерфейс контролера Flash-пам'яті відображається у системний адресний простір мікроконтролера на швидкій шині AHB (типова базова адреса для платформ Cortex-M4/M7 становить `0x40023C00`). Керування розбите на шість 32-бітних регістрів зі спеціальним захистом від випадкового запису.

| Зсув | Регістр | Повна назва | Призначення та поведінка |
|---|---|---|---|
| `0x00` | `FLASH_ACR` | Flash Access Control Register | Налаштування тактів очікування (Latency), увімкнення Prefetch, I-Cache, D-Cache та програмне скидання кешів. Доступний для читання й запису без паролів. |
| `0x04` | `FLASH_KEYR` | Flash Key Register | Запис послідовності ключів розблокування (`KEY1 = 0x45670123`, `KEY2 = 0xCDEF89AB`) для зняття апаратного блокування запису в регістр `FLASH_CR`. |
| `0x08` | `FLASH_OPTKEYR`| Flash Option Key Register | Запис авторизаційних ключів для розблокування конфігураційних бітів Option Bytes (`OPTKEY1 = 0x08192A3B`, `OPTKEY2 = 0x4C5D6E7F`). |
| `0x0C` | `FLASH_SR` | Flash Status Register | Прапорці апаратного стану: зайнятість матриці (`BSY`), помилка вирівнювання (`PGAERR`), помилка захисту запису (`WRPERR`), помилка послідовності (`PGSERR`), прапорець завершення операції (`EOP`). |
| `0x10` | `FLASH_CR` | Flash Control Register | Керування операціями стирання секторів (`SER`), масового стирання всієї матриці (`MER`), розміром паралелізму запису (`PSIZE`) та запуском програмування (`STRT`). |
| `0x14` | `FLASH_OPTCR` | Flash Option Control Register | Налаштування апаратного рівня захисту від зчитування (RDP Level 0/1/2), апаратного сторожового таймера (WDG), рівнів детектора падіння напруги (BOR). |

## Детальний розбір бітових полів регістра FLASH_ACR

Регістр `FLASH_ACR` визначає часові параметри та конвеєрну поведінку контролера зчитування пам'яті. Зміна його полів набуває чинності протягом одного-двох тактів шини AHB.

```
 31             13   12     11     10     9      8     4   3       0
┌─────────────────┬──────┬──────┬──────┬──────┬──────┬───┬───────────┐
│    Зарезервовано│DCRST │ICRST │ DCEN │ ICEN │PRFTEN│res│  LATENCY  │
└─────────────────┴──────┴──────┴──────┴──────┴──────┴───┴───────────┘
```

| Біти | Назва | Тип | Скидання | Опис апаратної дії та крайові випадки |
|---|---|---|---|---|
| `3:0` | `LATENCY` | R/W | `0b0000` | Кількість тактів очікування шини (Wait States / Latency). Задає співвідношення між частотою системної шини HCLK та часом доступу до матриці. Значення від `0WS` (`0000`) до `15WS` (`1111`). Запис значення, що перевищує максимальну підтримку конкретного кристала, обрізається апаратурою до верхньої межі. |
| `7:4` | `RESERVED` | RO | `0` | Зарезервовано, під час запису повинно маскуватися нулями. |
| `8` | `PRFTEN` | R/W | `0` | Prefetch Enable. Дозвіл буфера попередньої вибірки (128-бітне випереджальне читання). Коли біт активний (`1`), контролер у фоновому режимі зчитує наступне 128-бітне слово матриці під час виконання поточного рядка. При скиданні в `0` фонове читання вимикається. |
| `9` | `ICEN` | R/W | `0` | Instruction Cache Enable. Увімкнення 64-рядкового асоціативного кешу інструкцій прискорювача ART. При `1` ядро отримує інструкції за 0WS при попаданні в тег. При `0` кеш пасивно пропускає всі запити без збереження. |
| `10` | `DCEN` | R/W | `0` | Data Cache Enable. Увімкнення 8-рядкового кешу констант і літералів шини D-Code. При `1` кешуються дані з пулів констант у Flash. При `0` кеш даних вимкнено. |
| `11` | `ICRST` | W1 | `0` | Instruction Cache Reset. Програмне скидання та очищення валідності всіх тегів кешу інструкцій. Записується `1` для очищення; біт може бути встановлений **виключно тоді, коли `ICEN = 0`**. Якщо спробувати записати `ICRST = 1` при увімкненому `ICEN = 1`, апаратура проігнорує команду. |
| `12` | `DCRST` | W1 | `0` | Data Cache Reset. Програмне скидання та очищення валідності тегів кешу даних. Записується `1` для очищення; біт може бути встановлений **виключно тоді, коли `DCEN = 0`**. |

## Діагностичні прапорці регістра FLASH_SR

Регістр статусу `FLASH_SR` відображає апаратні конфлікти та помилки доступу під час роботи з Flash-пам'яттю. Усі біти помилок очищаються записом логічної `1` (Write-1-to-Clear):

* `BSY` (Flash Busy, біт 16): Індикатор активної операції на рівні кремнієвої матриці (стирання блоку або запис слова). Поки `BSY = 1`, будь-яке звертання ядра чи DMA до Flash блокує системну шину AHB.
* `RDERR` (Read Protection Error, біт 8): Виникає при спробі читання з адресного простору Flash, захищеного бітами RDP або MPU.
* `PGSERR` (Programming Sequence Error, біт 7): Сигналізує про порушення порядку команд контролера програмування (наприклад, спроба запису даних до активації біта `PG` у `FLASH_CR`).
* `PGPERR` (Programming Parallelism Error, біт 6): Помилка невідповідності розміру шини програмування (біти `PSIZE`) напрузі живлення. Наприклад, спроба 32-бітного запису при напрузі нижче 2.7 В.
* `PGAERR` (Programming Alignment Error, біт 5): Виникає, якщо адреса запису даних не вирівняна за межею вибраного формату (16/32/64 біти).
* `WRPERR` (Write Protection Error, біт 4): Спроба стирання або запису в сектор Flash, захищений апаратними бітами `nWRPi`.
* `EOP` (End of Operation, біт 0): Прапорець успішного завершення операції запису або стирання. Може генерувати апаратне переривання.

## Нормативні таблиці залежності Wait States від частоти та напруги

Фізична швидкість перезаряджання ємностей бітових ліній Flash-матриці безпосередньо залежить від робочої напруги внутрішнього стабілізатора (Vdd). При зниженні напруги струми заряду та розряду зменшуються, тому для збереження стабільності читання на тій самій тактовій частоті ядра вимагається більше тактів очікування.

### Діапазон живлення 1: Vdd = 2.7 В – 3.6 В (Повна потужність і максимальна швидкість)

У цьому діапазоні внутрішні сенсорні підсилювачі та адресні декодери живляться від максимального рівня напруги. Час доступу матриці становить близько 28–30 нс.

| Значення LATENCY | Тактів очікування (WS) | Загальний час циклу (тактов) | Діапазон частоти HCLK |
|---|---|---|---|
| `0b0000` | 0 WS | 1 такт | `0 < f_cpu ≤ 30 МГц` |
| `0b0001` | 1 WS | 2 такти | `30 МГц < f_cpu ≤ 60 МГц` |
| `0b0010` | 2 WS | 3 такти | `60 МГц < f_cpu ≤ 90 МГц` |
| `0b0011` | 3 WS | 4 такти | `90 МГц < f_cpu ≤ 120 МГц` |
| `0b0100` | 4 WS | 5 тактів | `120 МГц < f_cpu ≤ 150 МГц` |
| `0b0101` | 5 WS | 6 тактів | `150 МГц < f_cpu ≤ 168 МГц` |
| `0b0110` | 6 WS | 7 тактів | `168 МГц < f_cpu ≤ 180 МГц` (із режимом Over-drive) |
| `0b0111` | 7 WS | 8 тактів | `180 МГц < f_cpu ≤ 216 МГц` (для ядер Cortex-M7) |

### Діапазон живлення 2: Vdd = 2.4 В – 2.7 В (Проміжний діапазон живлення)

Виникає при живленні системи від двох лужних батарей або розрядженого літій-залізо-фосфатного (LiFePO4) акумулятора. Час доступу матриці зростає до 38–42 нс.

| Значення LATENCY | Тактів очікування (WS) | Загальний час циклу | Діапазон частоти HCLK |
|---|---|---|---|
| `0b0000` | 0 WS | 1 такт | `0 < f_cpu ≤ 24 МГц` |
| `0b0001` | 1 WS | 2 такти | `24 МГц < f_cpu ≤ 48 МГц` |
| `0b0010` | 2 WS | 3 такти | `48 МГц < f_cpu ≤ 72 МГц` |
| `0b0011` | 3 WS | 4 такти | `72 МГц < f_cpu ≤ 96 МГц` |
| `0b0100` | 4 WS | 5 тактів | `96 МГц < f_cpu ≤ 120 МГц` |
| `0b0101` | 5 WS | 6 тактів | `120 МГц < f_cpu ≤ 144 МГц` |
| `0b0110` | 6 WS | 7 тактів | `144 МГц < f_cpu ≤ 168 МГц` |

### Діапазон живлення 3: Vdd = 2.1 В – 2.4 В

| Значення LATENCY | Тактів очікування (WS) | Загальний час циклу | Діапазон частоти HCLK |
|---|---|---|---|
| `0b0000` | 0 WS | 1 такт | `0 < f_cpu ≤ 18 МГц` |
| `0b0001` | 1 WS | 2 такти | `18 МГц < f_cpu ≤ 36 МГц` |
| `0b0010` | 2 WS | 3 такти | `36 МГц < f_cpu ≤ 54 МГц` |
| `0b0011` | 3 WS | 4 такти | `54 МГц < f_cpu ≤ 72 МГц` |
| `0b0100` | 4 WS | 5 тактів | `72 МГц < f_cpu ≤ 90 МГц` |
| `0b0101` | 5 WS | 6 тактів | `90 МГц < f_cpu ≤ 108 МГц` |
| `0b0110` | 6 WS | 7 тактів | `108 МГц < f_cpu ≤ 120 МГц` |

### Діапазон живлення 4: Vdd = 1.8 В – 2.1 В (Мінімальне енергоспоживання)

При живленні від повністю розрядженого елемента живлення час розряду бітових ліній збільшується більш ніж удвічі (до 55–60 нс). Однотактове зчитування (0WS) можливе лише до 16 МГц.

| Значення LATENCY | Тактів очікування (WS) | Загальний час циклу | Діапазон частоти HCLK |
|---|---|---|---|
| `0b0000` | 0 WS | 1 такт | `0 < f_cpu ≤ 16 МГц` |
| `0b0001` | 1 WS | 2 такти | `16 МГц < f_cpu ≤ 32 МГц` |
| `0b0010` | 2 WS | 3 такти | `32 МГц < f_cpu ≤ 48 МГц` |
| `0b0011` | 3 WS | 4 такти | `48 МГц < f_cpu ≤ 64 МГц` |
| `0b0100` | 4 WS | 5 тактів | `64 МГц < f_cpu ≤ 80 МГц` |
| `0b0101` | 5 WS | 6 тактів | `80 МГц < f_cpu ≤ 96 МГц` |
| `0b0110` | 6 WS | 7 тактів | `96 МГц < f_cpu ≤ 112 МГц` |
| `0b0111` | 7 WS | 8 тактів | `112 МГц < f_cpu ≤ 128 МГц` |

## Апаратні особливості та зв'язок із регулятором напруги (VOS)

Сучасні мікроконтролери використовують внутрішній імпульсний або лінійний стабілізатор напруги ядра, який підтримує режими масштабування напруги (Voltage Output Scaling, `VOS`). Управління масштабуванням здійснюється через біти `PWR_CR.VOS`:
1. **Scale 1 Mode (Висока продуктивність):** Внутрішня напруга ядра підтримується на рівні 1.2–1.3 В. Дозволяє роботу на максимальних частотах (168–180 МГц) за умови відповідних затримок Flash.
2. **Scale 2 Mode (Збалансований режим):** Внутрішня напруга знижується до 1.0–1.1 В. Максимальна тактова частота обмежується (наприклад, до 144 МГц).
3. **Scale 3 Mode (Глибоке енергозбереження):** Внутрішня напруга ядра знижується до мінімально можливих 0.9 В. Максимальна частота ядра не повинна перевищувати 120 МГц.

Якщо в прошивці змінюється режим енергоспоживання через `PWR_CR`, процедура переналаштування обов'язково повинна враховувати відповідну зміну затримок `FLASH_ACR.LATENCY`.

## Архітектурні обмеження читання під час запису (Read-While-Write)

У мікроконтролерах із єдиним банком Flash-пам'яті (Single-Bank Flash) матриця комірок є неподільним фізичним ресурсом. Будь-яка операція стирання сектору або запису слова блокує всю пам'ять: адресні дешифратори та сенсорні підсилювачі зайняті високовольтними генераторами підкачки заряду. Якщо ядро спробує прочитати інструкцію або константу з Flash під час активного біта `FLASH_SR.BSY`, шинна матриця AHB перейде в нескінченний стан очікування (Bus Stall), що повністю паралізує виконання програми.

Для безпечного оновлення прошивки на однобанківських чіпах весь код драйвера програмування Flash, таблиця векторів переривань та обробники переривань обов'язково розміщуються в оперативній пам'яті (SRAM / CCMRAM). У двобанківських чіпах (Dual-Bank Flash) дозволено виконання коду з банку 1 під час стирання або запису банку 2 (Read-While-Write, RWW), що спрощує архітектуру завантажувачів.

## Програмний інтерфейс драйвера Flash на C та C++

Нижче наведено модульний низькорівневий драйвер для безпечного налаштування затримок, конфігурації прискорювача та інвалідації кешів.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

#define FLASH_BASE_ADDR      0x40023C00U
#define FLASH_ACR_REG        (*(volatile uint32_t *)(FLASH_BASE_ADDR + 0x00U))

#define FLASH_ACR_LATENCY_MASK  (0x0FU)
#define FLASH_ACR_PRFTEN_BIT    (1U << 8)
#define FLASH_ACR_ICEN_BIT      (1U << 9)
#define FLASH_ACR_DCEN_BIT      (1U << 10)
#define FLASH_ACR_ICRST_BIT     (1U << 11)
#define FLASH_ACR_DCRST_BIT     (1U << 12)

typedef enum {
    FLASH_LATENCY_0WS = 0,
    FLASH_LATENCY_1WS = 1,
    FLASH_LATENCY_2WS = 2,
    FLASH_LATENCY_3WS = 3,
    FLASH_LATENCY_4WS = 4,
    FLASH_LATENCY_5WS = 5,
    FLASH_LATENCY_6WS = 6,
    FLASH_LATENCY_7WS = 7
} flash_latency_t;

/* Встановлення затримки з обов'язковим опитуванням бітів підтвердження */
bool flash_set_latency(flash_latency_t latency) {
    uint32_t acr = FLASH_ACR_REG;
    acr &= ~FLASH_ACR_LATENCY_MASK;
    acr |= ((uint32_t)latency & FLASH_ACR_LATENCY_MASK);
    FLASH_ACR_REG = acr;

    /* Цикл підтвердження запису: очікуємо, поки логіка Flash зафіксує затримку */
    uint32_t timeout = 1000U;
    while ((FLASH_ACR_REG & FLASH_ACR_LATENCY_MASK) != (uint32_t)latency) {
        if (--timeout == 0U) {
            return false; /* Апаратна помилка або збій шини */
        }
    }
    return true;
}

/* Увімкнення черги випереджального читання та кешів ART */
void flash_enable_accelerators(bool prefetch, bool icache, bool dcache) {
    uint32_t acr = FLASH_ACR_REG;
    if (prefetch) acr |= FLASH_ACR_PRFTEN_BIT; else acr &= ~FLASH_ACR_PRFTEN_BIT;
    if (icache)   acr |= FLASH_ACR_ICEN_BIT;   else acr &= ~FLASH_ACR_ICEN_BIT;
    if (dcache)   acr |= FLASH_ACR_DCEN_BIT;   else acr &= ~FLASH_ACR_DCEN_BIT;
    FLASH_ACR_REG = acr;
}

/* Примусова інвалідація кешів після оновлення Flash (IAP / Flash write) */
void flash_invalidate_caches(void) {
    /* Скидання кешів дозволено лише при вимкнених бітах ICEN / DCEN */
    FLASH_ACR_REG &= ~(FLASH_ACR_ICEN_BIT | FLASH_ACR_DCEN_BIT);
    
    /* Запис 1 в біти скидання */
    FLASH_ACR_REG |= (FLASH_ACR_ICRST_BIT | FLASH_ACR_DCRST_BIT);
    
    /* Біти скидання автоматично очищаються апаратурою; вмикаємо кеші назад */
    FLASH_ACR_REG &= ~(FLASH_ACR_ICRST_BIT | FLASH_ACR_DCRST_BIT);
    FLASH_ACR_REG |= (FLASH_ACR_ICEN_BIT | FLASH_ACR_DCEN_BIT);
}
```
```cpp
#include <cstdint>
#include <span>

namespace mcu::flash {

enum class Latency : uint32_t {
    Ws0 = 0,
    Ws1 = 1,
    Ws2 = 2,
    Ws3 = 3,
    Ws4 = 4,
    Ws5 = 5,
    Ws6 = 6,
    Ws7 = 7
};

enum class VoltageRange {
    High_2V7_3V6,
    Medium_2V4_2V7,
    Low_2V1_2V4,
    VeryLow_1V8_2V1
};

struct FlashRegisters {
    volatile uint32_t ACR;
    volatile uint32_t KEYR;
    volatile uint32_t OPTKEYR;
    volatile uint32_t SR;
    volatile uint32_t CR;
    volatile uint32_t OPTCR;
};

class FlashController {
private:
    static constexpr uintptr_t BaseAddress = 0x40023C00U;
    static constexpr uint32_t LatencyMask = 0x0FU;
    static constexpr uint32_t PrftenBit   = 1U << 8;
    static constexpr uint32_t IcenBit     = 1U << 9;
    static constexpr uint32_t DcenBit     = 1U << 10;
    static constexpr uint32_t IcrstBit    = 1U << 11;
    static constexpr uint32_t DcrstBit    = 1U << 12;

    static auto& regs() noexcept {
        return *reinterpret_cast<FlashRegisters*>(BaseAddress);
    }

public:
    /* Обчислення мінімальної затримки під час компіляції */
    static constexpr Latency calculate_latency(uint32_t hclk_hz, VoltageRange vrange) noexcept {
        switch (vrange) {
            case VoltageRange::High_2V7_3V6:
                if (hclk_hz <= 30'000'000U)  return Latency::Ws0;
                if (hclk_hz <= 60'000'000U)  return Latency::Ws1;
                if (hclk_hz <= 90'000'000U)  return Latency::Ws2;
                if (hclk_hz <= 120'000'000U) return Latency::Ws3;
                if (hclk_hz <= 150'000'000U) return Latency::Ws4;
                if (hclk_hz <= 168'000'000U) return Latency::Ws5;
                if (hclk_hz <= 180'000'000U) return Latency::Ws6;
                return Latency::Ws7;

            case VoltageRange::Medium_2V4_2V7:
                if (hclk_hz <= 24'000'000U)  return Latency::Ws0;
                if (hclk_hz <= 48'000'000U)  return Latency::Ws1;
                if (hclk_hz <= 72'000'000U)  return Latency::Ws2;
                if (hclk_hz <= 96'000'000U)  return Latency::Ws3;
                if (hclk_hz <= 120'000'000U) return Latency::Ws4;
                if (hclk_hz <= 144'000'000U) return Latency::Ws5;
                return Latency::Ws6;

            case VoltageRange::Low_2V1_2V4:
                if (hclk_hz <= 18'000'000U)  return Latency::Ws0;
                if (hclk_hz <= 36'000'000U)  return Latency::Ws1;
                if (hclk_hz <= 54'000'000U)  return Latency::Ws2;
                if (hclk_hz <= 72'000'000U)  return Latency::Ws3;
                if (hclk_hz <= 90'000'000U)  return Latency::Ws4;
                if (hclk_hz <= 108'000'000U) return Latency::Ws5;
                return Latency::Ws6;

            case VoltageRange::VeryLow_1V8_2V1:
                if (hclk_hz <= 16'000'000U)  return Latency::Ws0;
                if (hclk_hz <= 32'000'000U)  return Latency::Ws1;
                if (hclk_hz <= 48'000'000U)  return Latency::Ws2;
                if (hclk_hz <= 64'000'000U)  return Latency::Ws3;
                if (hclk_hz <= 80'000'000U)  return Latency::Ws4;
                if (hclk_hz <= 96'000'000U)  return Latency::Ws5;
                if (hclk_hz <= 112'000'000U) return Latency::Ws6;
                return Latency::Ws7;
        }
        return Latency::Ws7;
    }

    static bool set_latency(Latency lat) noexcept {
        auto val = regs().ACR;
        val &= ~LatencyMask;
        val |= static_cast<uint32_t>(lat);
        regs().ACR = val;

        uint32_t timeout = 1000U;
        while ((regs().ACR & LatencyMask) != static_cast<uint32_t>(lat)) {
            if (--timeout == 0U) return false;
        }
        return true;
    }

    static void configure_accelerator(bool prefetch, bool icache, bool dcache) noexcept {
        auto val = regs().ACR;
        if (prefetch) val |= PrftenBit; else val &= ~PrftenBit;
        if (icache)   val |= IcenBit;   else val &= ~IcenBit;
        if (dcache)   val |= DcenBit;   else val &= ~DcenBit;
        regs().ACR = val;
    }

    /* Безпечне скидання та інвалідація кешів */
    static void flush_caches() noexcept {
        regs().ACR &= ~(IcenBit | DcenBit);
        regs().ACR |= (IcrstBit | DcrstBit);
        regs().ACR &= ~(IcrstBit | DcrstBit);
        regs().ACR |= (IcenBit | DcenBit);
    }
};

} // namespace mcu::flash
```
:::
