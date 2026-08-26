# ⚙️ Повний драйвер аналогового захисту силового каскаду

У силових перетворювачах — від трифазних частотних приводів (BLDC/PMSM) до високовольтних синхронних перетворювачів напруги — критична аварійна ситуація розвивається швидше, ніж процесорне ядро здатне виконати навіть одну інструкцію входу в переривання. При короткому замиканні у фазі або наскрізному пробитті стійки напівмоста струм зростає зі швидкістю `di/dt = V_bus / L_stray`, де `L_stray` — паразитна індуктивність монтажу й виводів силового модуля. При напрузі шини `48 В` та індуктивності розсіювання `100 нГн` швидкість наростання струму становить `480 А/мкс`. Для кристала силового транзистора (MOSFET або GaN HEMT) допустимий час витримування струму короткого замикання не перевищує `1–2 мкс`.

Для гарантованого захисту силового каскаду вся послідовність «вимірювання струму → підсилення → порівняння з порогом → зняття імпульсів керування» реалізується виключно в апаратному кремнії без участі процесора. Нижче наведено повну реалізацію драйвера конфігурації вбудованих аналогових блоків: операційного підсилювача в режимі підсилювача з програмованим коефіцієнтом (PGA), швидкісного компаратора з опорним рівнем від внутрішнього цифро-аналогового перетворювача (DAC), таймера розширеного керування з функцією апаратного гальмування (TIM Break) та аналогового сторожового пса (ADC AWD) для контролю теплового дрейфу.

### 1. Апаратна топологія контуру захисту

Аналоговий сигнал знімається з чотирипровідного низькоомного [шунта Кельвіна](root:hw-sensing/kelvin-shunt) `R_shunt = 5 мОм`, установленого в нижньому плечі силової стійки. При номінальному струмі `10 А` падіння напруги на шунті становить `50 мВ`. Цей сигнал надходить на вхід внутрішнього ОП (`OPAMP1_VINP`).

Вбудований ОП конфігурується в режимі PGA з коефіцієнтом підсилення `16x`. Підсилений сигнал з амплітудою `0.8 В` внутрішньою кремнієвою шиною без виходу на зовнішні піни подається одночасно на два вузли:
1. **На вхід швидкісного АЦП (`ADC1_IN3`)**: оцифровує струм для векторного керування (FOC) і передає дані в блок [аналогового сторожового пса](root:hw-arch/analohovi-bloky), який формує вікно тривалого моніторингу перевантаження;
2. **На неінверсний вхід компаратора (`COMP1_INP`)**: порівнює сигнал з порогом аварійного струму від 12-бітного ЦАП (`DAC1_OUT1`). Вихід компаратора з'єднаний внутрішнім тригером з аварійним входом таймера `TIM1_BKIN`.

При перевищенні струму компаратор за `15–20 нс` перемикає свій вихід у високий рівень, логіка захисту таймера за `< 10 нс` скидає біт `MOE` (Main Output Enable) у регістрі `TIM1_BDTR`, і всі шість комплементарних затворів силових ключів вимикаються. Сумарний час захисту становить `25–30 нс`.

### 2. Реалізація драйвера на C та C++

У прикладі наведено низькорівневий драйвер ініціалізації та обслуговування аналогової периферії для змішано-сигнальної архітектури мікроконтролера.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Базові адреси периферійних блоків */
#define RCC_BASE        0x40021000UL
#define GPIOA_BASE      0x48000000UL
#define OPAMP_BASE      0x40007800UL
#define COMP_BASE       0x40010200UL
#define DAC1_BASE       0x40007400UL
#define TIM1_BASE       0x40012C00UL
#define ADC1_BASE       0x50000000UL

/* Зсуви регістрів OPAMP, COMP, DAC, TIM1, ADC */
#define OPAMP1_CSR      (*(volatile uint32_t *)(OPAMP_BASE + 0x00))
#define OPAMP1_OTR      (*(volatile uint32_t *)(OPAMP_BASE + 0x18))

#define COMP1_CSR       (*(volatile uint32_t *)(COMP_BASE + 0x00))

#define DAC1_CR         (*(volatile uint32_t *)(DAC1_BASE + 0x00))
#define DAC1_DHR12R1    (*(volatile uint32_t *)(DAC1_BASE + 0x08))

#define TIM1_CR1        (*(volatile uint32_t *)(TIM1_BASE + 0x00))
#define TIM1_BDTR       (*(volatile uint32_t *)(TIM1_BASE + 0x44))
#define TIM1_SR         (*(volatile uint32_t *)(TIM1_BASE + 0x10))
#define TIM1_DIER       (*(volatile uint32_t *)(TIM1_BASE + 0x0C))

#define ADC1_CR         (*(volatile uint32_t *)(ADC1_BASE + 0x08))
#define ADC1_CFGR       (*(volatile uint32_t *)(ADC1_BASE + 0x0C))
#define ADC1_TR1        (*(volatile uint32_t *)(ADC1_BASE + 0x20))
#define ADC1_IER        (*(volatile uint32_t *)(ADC1_BASE + 0x04))
#define ADC1_ISR        (*(volatile uint32_t *)(ADC1_BASE + 0x00))

/* Бітові маски OPAMP */
#define OPAMP_CSR_OPAMPINTEN    (1UL << 30) /* Внутрішнє підключення виходу до ADC/COMP */
#define OPAMP_CSR_PGA_GAIN_16X  (0x3UL << 14)/* Коефіцієнт підсилення 16x */
#define OPAMP_CSR_VM_SEL_PGA    (0x2UL << 5) /* Інверсний вхід на внутрішній дільник PGA */
#define OPAMP_CSR_VP_SEL_INP0   (0x0UL << 2) /* Неінверсний вхід з зовнішнього піна */
#define OPAMP_CSR_OPAMPxEN      (1UL << 0)  /* Увімкнення підсилювача */
#define OPAMP_CSR_CALON         (1UL << 11) /* Запуск калібрування */
#define OPAMP_CSR_CALOUT        (1UL << 12) /* Вихід компаратора калібрування */

/* Бітові маски COMP */
#define COMP_CSR_LOCK           (1UL << 31) /* Блокування конфігурації регістра до Reset */
#define COMP_CSR_HYST_20MV      (0x2UL << 16)/* Гістерезис 20 мВ */
#define COMP_CSR_INPSEL_OPAMP   (0x1UL << 7) /* Неінверсний вхід підключений до OPAMP1_OUT */
#define COMP_CSR_INMSEL_DAC1_CH1(0x4UL << 4) /* Інверсний вхід підключений до DAC1_OUT1 */
#define COMP_CSR_COMPxEN        (1UL << 0)  /* Увімкнення компаратора */

/* Бітові маски TIM1 */
#define TIM_BDTR_MOE            (1UL << 15) /* Main Output Enable */
#define TIM_BDTR_AOE            (1UL << 14) /* Automatic Output Enable */
#define TIM_BDTR_BKE            (1UL << 12) /* Увімкнення входу Break */
#define TIM_BDTR_BKP            (0UL << 13) /* Полярність Break: високий рівень = аварія */
#define TIM_DIER_BIE            (1UL << 7)  /* Дозвіл переривання Break */
#define TIM_SR_BIF              (1UL << 7)  /* Прапорець переривання Break */

/* Калібрування зсуву нуля OPAMP */
void opamp_calibrate_offset(void) {
    /* 1. Увімкнення режиму калібрування для диференційного каскаду */
    OPAMP1_CSR |= OPAMP_CSR_CALON;

    /* Підбір тримінгу для транзисторів p-типу (TRIMOFFSETP) */
    uint32_t trim_p = 0;
    for (uint32_t i = 0; i < 32; ++i) {
        OPAMP1_OTR = (OPAMP1_OTR & ~0x1FUL) | (i & 0x1FUL);
        for (volatile int d = 0; d < 200; ++d); /* Затримка встановлення */
        if (OPAMP1_CSR & OPAMP_CSR_CALOUT) {
            trim_p = i;
            break;
        }
    }

    /* Підбір тримінгу для транзисторів n-типу (TRIMOFFSETN) */
    uint32_t trim_n = 0;
    for (uint32_t i = 0; i < 32; ++i) {
        OPAMP1_OTR = (OPAMP1_OTR & ~(0x1FUL << 8)) | ((i & 0x1FUL) << 8);
        for (volatile int d = 0; d < 200; ++d);
        if (OPAMP1_CSR & OPAMP_CSR_CALOUT) {
            trim_n = i;
            break;
        }
    }

    /* Завершення калібрування */
    OPAMP1_CSR &= ~OPAMP_CSR_CALON;
}

/* Ініціалізація вбудованого ОП у режимі PGA 16x */
void opamp_init_pga(void) {
    opamp_calibrate_offset();

    /* Налаштування: вхід INP0, зворотний зв'язок PGA 16x, вихід внутрішній */
    OPAMP1_CSR = OPAMP_CSR_OPAMPINTEN   |
                 OPAMP_CSR_PGA_GAIN_16X |
                 OPAMP_CSR_VM_SEL_PGA   |
                 OPAMP_CSR_VP_SEL_INP0  |
                 OPAMP_CSR_OPAMPxEN;
}

/* Ініціалізація опорного ЦАП для порогу струму (поріг 25 А) */
void dac_init_threshold(void) {
    /* 25 А * 5 мОм = 125 мВ. Підсилення 16x -> 2.0 В.
       Код ЦАП (12 біт, Vref = 3.3 В): (2.0 / 3.3) * 4095 = 2482 */
    DAC1_DHR12R1 = 2482;
    DAC1_CR |= (1UL << 0); /* Увімкнення каналу 1 ЦАП */
}

/* Ініціалізація компаратора COMP1 з прямим зв'язком до TIM1 Break */
void comp_init_protection(void) {
    COMP1_CSR = COMP_CSR_HYST_20MV       |
                COMP_CSR_INPSEL_OPAMP    |
                COMP_CSR_INMSEL_DAC1_CH1 |
                COMP_CSR_COMPxEN;

    /* Блокування регістра для захисту від випадкового збою коду */
    COMP1_CSR |= COMP_CSR_LOCK;
}

/* Ініціалізація аварійного гальмування таймера ШІМ */
void tim1_break_init(void) {
    /* Дозвіл Break, полярність High, без авто-перезапуску (Lock), увімкнення виходів */
    TIM1_BDTR |= TIM_BDTR_BKE;
    TIM1_DIER |= TIM_DIER_BIE; /* Дозвіл переривання для діагностики */
    TIM1_BDTR |= TIM_BDTR_MOE; /* Активація виходів ШІМ */
}

/* Ініціалізація аналогового сторожового пса АЦП (AWD) */
void adc_awd_init(void) {
    /* Верхній поріг: 20 А (1.6 В -> код 1985), Нижній поріг: 0.1 В -> код 124 */
    ADC1_TR1 = ((1985UL & 0xFFFUL) << 16) | (124UL & 0xFFFUL);
    
    /* Увімкнення AWD на каналі 3 (ADC1_IN3 - підключеному до OPAMP1_OUT) */
    ADC1_CFGR |= (1UL << 23) | (3UL << 26); /* AWD1EN + канал 3 */
    ADC1_IER  |= (1UL << 7);                 /* Дозвіл переривання AWD1IE */
}

/* Обробник апаратного переривання Break від компаратора */
void TIM1_BRK_IRQHandler(void) {
    if (TIM1_SR & TIM_SR_BIF) {
        /* Аварія надструму: виходи заблоковані апаратно на рівні кремнію */
        TIM1_SR &= ~TIM_SR_BIF; /* Скидання прапорця переривання */
        
        /* Логування та перевірка стану системи */
        /* Повторне увімкнення виходів MOE можливе лише після повної діагностики */
    }
}
```
```cpp
#include <cstdint>
#include <concepts>
#include <span>

namespace hw::analog {

/* Базові адреси периферійних модулів */
inline constexpr std::uintptr_t OPAMP_BASE = 0x40007800UL;
inline constexpr std::uintptr_t COMP_BASE  = 0x40010200UL;
inline constexpr std::uintptr_t DAC1_BASE  = 0x40007400UL;
inline constexpr std::uintptr_t TIM1_BASE  = 0x40012C00UL;
inline constexpr std::uintptr_t ADC1_BASE  = 0x50000000UL;

/* Режими коефіцієнта підсилення PGA */
enum class PgaGain : std::uint32_t {
    Gain2x  = 0x0UL << 14,
    Gain4x  = 0x1UL << 14,
    Gain8x  = 0x2UL << 14,
    Gain16x = 0x3UL << 14,
    Gain32x = 0x4UL << 14,
    Gain64x = 0x5UL << 14
};

/* Рівні гістерезису компаратора */
enum class Hysteresis : std::uint32_t {
    None   = 0x0UL << 16,
    Low    = 0x1UL << 16, // ~10 мВ
    Medium = 0x2UL << 16, // ~20 мВ
    High   = 0x3UL << 16  // ~40 мВ
};

/* Драйвер вбудованого операційного підсилювача */
class OpAmpPga {
private:
    struct Registers {
        volatile std::uint32_t CSR;
        volatile std::uint32_t RESERVED[5];
        volatile std::uint32_t OTR;
    };

    static Registers& regs() noexcept {
        return *reinterpret_cast<Registers*>(OPAMP_BASE);
    }

public:
    static void calibrate() noexcept {
        regs().CSR |= (1UL << 11); // CALON

        // Пошук зсуву диференціальної пари
        for (std::uint32_t i = 0; i < 32; ++i) {
            regs().OTR = (regs().OTR & ~0x1FUL) | (i & 0x1FUL);
            for (volatile int d = 0; d < 200; ++d);
            if (regs().CSR & (1UL << 12)) break;
        }

        regs().CSR &= ~(1UL << 11); // Вимкнення калібрування
    }

    static void init(PgaGain gain) noexcept {
        calibrate();

        constexpr std::uint32_t OPAMPINTEN  = (1UL << 30);
        constexpr std::uint32_t VM_SEL_PGA  = (0x2UL << 5);
        constexpr std::uint32_t VP_SEL_INP0 = (0x0UL << 2);
        constexpr std::uint32_t OPAMP_EN    = (1UL << 0);

        regs().CSR = OPAMPINTEN | static_cast<std::uint32_t>(gain) |
                     VM_SEL_PGA | VP_SEL_INP0 | OPAMP_EN;
    }
};

/* Драйвер компаратора аварійного струму */
class OvercurrentComparator {
private:
    struct Registers {
        volatile std::uint32_t CSR;
    };

    static Registers& regs() noexcept {
        return *reinterpret_cast<Registers*>(COMP_BASE);
    }

public:
    static void init(Hysteresis hyst) noexcept {
        constexpr std::uint32_t INPSEL_OPAMP    = (0x1UL << 7);
        constexpr std::uint32_t INMSEL_DAC1_CH1 = (0x4UL << 4);
        constexpr std::uint32_t COMP_EN         = (1UL << 0);
        constexpr std::uint32_t LOCK_BIT        = (1UL << 31);

        regs().CSR = static_cast<std::uint32_t>(hyst) |
                     INPSEL_OPAMP | INMSEL_DAC1_CH1 | COMP_EN;

        regs().CSR |= LOCK_BIT; // Апаратний захист від переконфігурації
    }
};

/* Керування аварійним гальмуванням ШІМ (TIM1 Break) */
class PwmBreakController {
private:
    struct Registers {
        volatile std::uint32_t CR1;
        volatile std::uint32_t RESERVED0[2];
        volatile std::uint32_t DIER;
        volatile std::uint32_t SR;
        volatile std::uint32_t RESERVED1[12];
        volatile std::uint32_t BDTR;
    };

    static Registers& regs() noexcept {
        return *reinterpret_cast<Registers*>(TIM1_BASE);
    }

public:
    static void enableBreakProtection(bool autoRestart = false) noexcept {
        constexpr std::uint32_t BKE = (1UL << 12);
        constexpr std::uint32_t AOE = (1UL << 14);
        constexpr std::uint32_t BIE = (1UL << 7);
        constexpr std::uint32_t MOE = (1UL << 15);

        std::uint32_t bdtrVal = regs().BDTR | BKE;
        if (autoRestart) bdtrVal |= AOE;
        else bdtrVal &= ~AOE;

        regs().BDTR = bdtrVal;
        regs().DIER |= BIE; // Дозвіл переривання
        regs().BDTR |= MOE; // Активація виходів
    }

    static bool isFaultActive() noexcept {
        return (regs().SR & (1UL << 7)) != 0;
    }

    static void clearFault() noexcept {
        regs().SR &= ~(1UL << 7);
    }

    static void rearmOutputs() noexcept {
        clearFault();
        regs().BDTR |= (1UL << 15); // MOE = 1
    }
};

/* Цифровий сторожовий пес АЦП */
class AnalogWatchdog {
private:
    struct Registers {
        volatile std::uint32_t ISR;
        volatile std::uint32_t IER;
        volatile std::uint32_t CR;
        volatile std::uint32_t CFGR;
        volatile std::uint32_t RESERVED[4];
        volatile std::uint32_t TR1;
    };

    static Registers& regs() noexcept {
        return *reinterpret_cast<Registers*>(ADC1_BASE);
    }

public:
    static void configureWindow(std::uint16_t lowThresh, std::uint16_t highThresh, std::uint8_t channel) noexcept {
        regs().TR1 = ((static_cast<std::uint32_t>(highThresh) & 0xFFFUL) << 16) |
                     (static_cast<std::uint32_t>(lowThresh) & 0xFFFUL);

        regs().CFGR |= (1UL << 23) | (static_cast<std::uint32_t>(channel & 0x1F) << 26);
        regs().IER  |= (1UL << 7); // AWD1IE
    }
};

} // namespace hw::analog
```
:::

### 3. Критичні підводні камені та інженерні нюанси

#### Черговість увімкнення блоків (Startup Race Condition)
У силовій схемотехніці суворо заборонено активувати виходи таймера (`MOE = 1`) до повної стабілізації аналогового тракту. Послідовність запуску повинна бути такою:
1. Запуск опорних джерел (`VREFINT` та ЦАП `DAC1`);
2. Калібрування та активація вбудованого ОП (`OPAMP1`);
3. Активація компаратора `COMP1` та блокування його регістра бітом `LOCK`;
4. Конфігурація входу `TIM1_BKIN` у таймері;
5. І лише останнім кроком — встановлення біта `MOE = 1` для дозволу подачі імпульсів на затвори ключів.

Якщо порушити цей порядок і ввімкнути таймер раніше, зарядний перехідний процес на вхідній ємності ОП може згенерувати імпульсний сплеск напруги на виході, що викличе хибне спрацювання компаратора та заблокує таймер ще до початку генерації ШІМ.

#### Фільтрація комутаційного дзвіну (Blanking Window)
У момент відкриття нижнього транзистора через паразитну ємність сток-витік `C_oss` та індуктивність монтажу в контурі шунта виникає високочастотний коливальний процес — дзвін перемикання (Switching Ringing). Амплітуда першого викиду напруги може багаторазово перевищувати аварійний поріг компаратора протягом `50–150 нс`.

Для запобігання хибному аварійному відключенню в мікроконтролері активують механізм апаратного стробування компаратора (Comparator Output Blanking). Таймер ШІМ формує внутрішній імпульс маскування `TIM1_OC4_Blanking`, який блокує передачу сигналу з виходу компаратора на вхід `BKIN` протягом перших `100–200 нс` після кожного фронту перемикання транзистора.

#### Узгодження часу встановлення OPAMP (Settling Time)
При виборі коефіцієнта підсилення PGA `16x` або `64x` добуток смуги пропускання на коефіцієнт підсилення (GBW, Gain Bandwidth Product) вбудованого підсилювача обмежує швидкість наростання вихідної напруги (Slew Rate). Час встановлення вихідного рівня з точністю до `1%` становить близько `200–300 нс`.

Якщо запустити вибірку АЦП (ADC Trigger) безпосередньо у момент відкриття ключа, вимірювання зафіксує перехідний процес, а не реальний струм фази. Момент запуску АЦП затримують апаратним таймером на час `t_delay = t_deadtime + t_settling`, що забезпечує оцифрування струму строго в середині імпульсу ШІМ.

#### Двостороннє вимірювання струму при рекуперації
Під час рекуперативного гальмування двигуна струм через нижнє плече тече у зворотному напрямку, створюючи негативну напругу на шунті відносно землі (`-50 мВ`). Однополярне живлення вбудованого ОП (`VDD = 3.3 В`, `VSS = 0 В`) не дозволяє підсилювати від'ємні потенціали (вихід ОП сяде в насичення біля нуля).

Для вимірювання знакозмінного струму інверсний вхід PGA комутують не на `GND`, а на джерело віртуальної середньої точки (Bias Voltage), сформоване внутрішнім ЦАП або дільником `1/2 VREFINT` (`1.65 В`). Тоді нульовий струм відповідає напрузі `1.65 В` на виході ОП, позитивний струм зміщує сигнал вгору до `3.3 В`, а негативний — вниз до `0 В`. Компаратор аварії в цьому випадку налаштовується на два пороги за допомогою віконного режиму (Window Mode).
