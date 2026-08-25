# ⚙️ Алгоритм та програмування гетеродинного синтезатора частот (Fractional-N PLL)

Сучасні радіотракти від настроюваних трансиверів до програмно-визначених радіосистем (SDR) використовують гетеродини на основі цифрових ФАПЧ-синтезаторів із дробовим коефіцієнтом ділення (*Fractional-N PLL*). Вони дозволяють отримувати високу точність вихідної частоти гетеродина (крок сітки аж до частки герца) при використанні високої опорної частоти f_ref від кварцового генератора (TCXO).

Опис математики розрахунку коефіцієнтів ділення, аналіз дробових завад (*fractional spurs*), керування вихідним дільником RF_DIV, оптимізація зарядового насоса та реалізація модуля налаштування синтезатора частоти гетеродина на C та C++.

### Математична модель дільника Fractional-N

Вихідна частота гетеродина f_LO визначається рівнянням:

```
f_VCO = f_PFD · ( INT + FRAC / MOD )
f_LO  = f_VCO / RF_DIV
```

Де:
- f_PFD — частота порівняння частотно-фазового детектора (дорівнює f_ref / R_DIV, де R_DIV — вихідний дільник опори);
- INT — ціла частина коефіцієнта ділення петлі ФАПЧ (діапазон 23...65535);
- FRAC — чисельник дробової частини (діапазон 0...MOD-1);
- MOD — знаменник дробової частини (модуль точності, наприклад 4095 або 16777215);
- RF_DIV — дільник вихідного ВЧ-сигналу (зазвичай ступені двійки: 1, 2, 4, 8, 16, 32, 64).

Головне завдання програмного алгоритму — за заданою цільовою частотою `target_hz` обчислити оптимальне значення `RF_DIV`, щоб перенести вихідну частоту VCO у робочий діапазон генератора (наприклад, 2.2...4.4 ГГц), розрахувати цілу частину `INT` та спростити дріб `FRAC / MOD` за допомогою найбільшого спільного дільника (НСД/GCD) для мінімізації побічних завад.

### Архітектура дельта-сигма модулятора та подрібнення завад

При дробовому діленні коефіцієнт ділення лічильника перемикається між значеннями INT та INT+1. Усереднений у часі коефіцієнт дорівнює INT + FRAC/MOD. Проте періодичне перемикання створює сильні побічні піки на спектрі — **дробові завади** (*Fractional Spurs*).

Для придушення завад у сучасних чипах гетеродитів (MAX2870, ADF4351, SI5351) застосовують дельта-сигма модулятор (DSM) 3-го порядку. Дизеринг (*dithering*) псевдовипадковим чином зсуває фазу перемикання, перетворюючи тональну заваду на розподілений білий шум, який легко відфільтровується петльовим фільтром ФАПЧ.

### Розрахунок струму зарядового насоса (Charge Pump Current)

Для підтримки стабільності петлі ФАПЧ при зміні цілого коефіцієнта INT програмне забезпечення повинно динамічно коригувати струм зарядового насоса `I_CP`. 

Ширина смуги пропускання петльового фільтра f_loop визначається формулою:

```
f_loop ≈ (1 / 2π) · [ (I_CP · K_VCO) / (N · C1) ]^½
```

Де:
- K_VCO — крутизна характеристики генератора VCO (МГц/В);
- N = INT + FRAC/MOD — сумарний коефіцієнт ділення;
- C1 — ємність першого конденсатора петльового фільтра.

Коли коефіцієнт ділення N збільшується при переході на вищу частоту, коефіцієнт передачі петлі падає. Для збереження постійної смуги фільтра та оптимального часу захоплення фази мікроконтролер повинен пропорційно збільшувати значення струму `I_CP` в конфігураційному регістрі чипа.

### Програмна реалізація алгоритму налаштування

Приклад демонструє повний розрахунок коефіцієнтів гетеродина для опорного TCXO 26 МГц, перевірку меж VCO та генерацію параметрів конфігурації.

:::tabs
```c
/* C Implementation */
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#define MODULUS_FIXED 4095U  /* 12-бітний модуль дробової частини */

typedef struct {
    uint32_t f_ref_hz;   /* Частота опорного TCXO, Гц */
    uint32_t f_min_vco;  /* Мінімальна частота VCO (напр. 2200 МГц) */
    uint32_t f_max_vco;  /* Максимальна частота VCO (напр. 4400 МГц) */
} pll_config_t;

typedef struct {
    uint32_t int_val;    /* Ціле значення N */
    uint32_t frac_val;   /* Чисельник FRAC */
    uint32_t mod_val;    /* Знаменник MOD */
    uint32_t rf_div;     /* Коефіцієнт RF_DIV (1, 2, 4, ...) */
    uint32_t actual_hz;  /* Фактично отримана частота f_LO */
} pll_settings_t;

static uint64_t gcd64(uint64_t a, uint64_t b) {
    while (b != 0) {
        uint64_t t = b;
        b = a % b;
        a = t;
    }
    return a;
}

bool pll_calculate_lo(const pll_config_t* cfg, uint32_t target_hz, pll_settings_t* out) {
    if (!cfg || !out || target_hz == 0) return false;

    /* 1. Підбір вихідного дільника RF_DIV для входу в діапазон VCO */
    uint32_t rf_div = 1;
    uint64_t vco_freq = (uint64_t)target_hz;

    while (vco_freq < cfg->f_min_vco && rf_div <= 64) {
        rf_div *= 2;
        vco_freq = (uint64_t)target_hz * rf_div;
    }

    if (vco_freq > cfg->f_max_vco) {
        return false; /* Частота поза межами генератора VCO */
    }

    /* 2. Обчислення цілої та дробової частин */
    uint64_t pfd_freq = cfg->f_ref_hz;
    uint32_t int_part = (uint32_t)(vco_freq / pfd_freq);
    uint64_t remainder = vco_freq % pfd_freq;

    /* 3. Розрахунок FRAC при фіксованому MOD */
    uint64_t frac_part = (remainder * MODULUS_FIXED) / pfd_freq;
    uint32_t mod_part = MODULUS_FIXED;

    /* 4. Скорочення дробу FRAC / MOD через наибольший спільний дільник */
    if (frac_part > 0) {
        uint64_t g = gcd64(frac_part, mod_part);
        frac_part /= g;
        mod_part /= (uint32_t)g;
    } else {
        mod_part = 1;
    }

    /* 5. Обчислення фактичної реалізованої частоти */
    uint64_t calc_vco = (uint64_t)int_part * pfd_freq + (pfd_freq * frac_part) / mod_part;
    uint32_t actual_lo = (uint32_t)(calc_vco / rf_div);

    out->int_val = int_part;
    out->frac_val = (uint32_t)frac_part;
    out->mod_val = mod_part;
    out->rf_div = rf_div;
    out->actual_hz = actual_lo;

    return true;
}

int main(void) {
    pll_config_t chip = {
        .f_ref_hz = 26000000U,      /* TCXO 26 МГц */
        .f_min_vco = 2200000000U,   /* VCO Min 2.2 ГГц */
        .f_max_vco = 4400000000U    /* VCO Max 4.4 ГГц */
    };
    pll_settings_t res;

    uint32_t desired_lo = 433920000U; /* 433.92 МГц для LPD/LoRa */

    if (pll_calculate_lo(&chip, desired_lo, &res)) {
        printf("Target LO: %u Hz\n", desired_lo);
        printf("Actual LO: %u Hz (RF_DIV=%u, INT=%u, FRAC=%u, MOD=%u)\n",
               res.actual_hz, res.rf_div, res.int_val, res.frac_val, res.mod_val);
    } else {
        printf("Error: Frequency out of range!\n");
    }
    return 0;
}
```
```cpp
// C++ Implementation
#include <iostream>
#include <numeric>
#include <optional>
#include <cstdint>

class LocalOscillatorPLL {
public:
    struct Config {
        std::uint32_t ref_freq_hz{26'000'000};  // 26 MHz TCXO
        std::uint32_t vco_min_hz{2'200'000'000}; // 2.2 GHz
        std::uint32_t vco_max_hz{4'400'000'000}; // 4.4 GHz
    };

    struct Settings {
        std::uint32_t int_val;
        std::uint32_t frac_val;
        std::uint32_t mod_val;
        std::uint32_t rf_div;
        std::uint32_t actual_hz;
    };

    explicit LocalOscillatorPLL(Config cfg) : config_(cfg) {}

    [[nodiscard]] std::optional<Settings> calculate(std::uint32_t target_lo_hz) const {
        if (target_lo_hz == 0) return std::nullopt;

        std::uint32_t rf_div = 1;
        std::uint64_t vco_freq = target_lo_hz;

        while (vco_freq < config_.vco_min_hz && rf_div <= 64) {
            rf_div *= 2;
            vco_freq = static_cast<std::uint64_t>(target_lo_hz) * rf_div;
        }

        if (vco_freq > config_.vco_max_hz) {
            return std::nullopt;
        }

        const std::uint64_t pfd_freq = config_.ref_freq_hz;
        const auto int_part = static_cast<std::uint32_t>(vco_freq / pfd_freq);
        const std::uint64_t remainder = vco_freq % pfd_freq;

        constexpr std::uint32_t max_modulus = 4095;
        std::uint64_t frac_part = (remainder * max_modulus) / pfd_freq;
        std::uint32_t mod_part = max_modulus;

        if (frac_part > 0) {
            const auto g = std::gcd(frac_part, static_cast<std::uint64_t>(mod_part));
            frac_part /= g;
            mod_part /= static_cast<std::uint32_t>(g);
        } else {
            mod_part = 1;
        }

        const std::uint64_t calc_vco = int_part * pfd_freq + (pfd_freq * frac_part) / mod_part;
        const auto actual_lo = static_cast<std::uint32_t>(calc_vco / rf_div);

        return Settings{
            .int_val = int_part,
            .frac_val = static_cast<std::uint32_t>(frac_part),
            .mod_val = mod_part,
            .rf_div = rf_div,
            .actual_hz = actual_lo
        };
    }

private:
    Config config_;
};

int main() {
    LocalOscillatorPLL pll({.ref_freq_hz = 26'000'000});
    constexpr std::uint32_t target = 433'920'000; // 433.92 MHz

    if (const auto settings = pll.calculate(target)) {
        std::cout << "Target LO: " << target << " Hz\n"
                  << "Actual LO: " << settings->actual_hz << " Hz\n"
                  << "RF_DIV=" << settings->rf_div
                  << ", INT=" << settings->int_val
                  << ", FRAC=" << settings->frac_val
                  << ", MOD=" << settings->mod_val << '\n';
    } else {
        std::cerr << "Error: Frequency cannot be synthesised!\n";
    }
    return 0;
}
```
:::

### Пастки реальної прошивки керування гетеродином

1. **Дробові завади дробового ділення (*Fractional Boundary Spurs*):** Якщо чисельник `FRAC` виявляється дуже малим значенням (наприклад, 1 або 2 при MOD=4095), у вихідному спектрі гетеродина виникають інтенсивні побічні піки на невеликій відбудові від несучої. Практичний алгоритм керування повинен перемикати синтезатор у цілочисельний режим (Integer-N Mode, `FRAC = 0`), якщо частота кратна `f_PFD`, або вмикати додатковий аналоговий дизеринг.
2. **Час захоплення фази та опитування готовності (*Lock Time & Lock Detect*):** Після запису нових значень регістрів по шині SPI внутрішній генератор VCO переходить на нову частоту не миттєво. Залежно від ширини смуги петльового фільтра ФАПЧ (типово від 10 кГц до 100 кГц) час стабілізації фази становить від 20 до 200 мікросекунд. Мікроконтролер повинен або аналізувати аппаратний цифровий сигнал `LOCK_DETECT` на виводі чипа, або витримувати обов'язкову затримку перед увімкненням передавача чи зчитуванням АЦП приймача.
3. **Автоматичне Калібрування Діапазонів VCO (*VCO Band Select*):** Сучасні широкодіапазонні VCO діляться всередині на 32...128 окремих перекривних частотних піддіапазонів. При зміні частоти синтезатор проводить автокалібрування (*auto-zero / band calibration*). Запис у конфігураційні регістри повинен дотримуватися чіткої послідовності (наприклад, спочатку регістр R0 з імпульсом перезапуску калібрування), інакше VCO залишиться на межі діапазону з підвищеним фазовим шумом.
4. **Послідовність програмування регістрів синтезатора:** Більшість радіочастотних синтезаторів вимагають запису регістрів у строго визначеному порядку: від вищих регістрів (R5, R4, R3) до регістру R0. Саме защелкивание регістру R0 ініціює перезапуск дільників та автокалібрування генератора VCO.
