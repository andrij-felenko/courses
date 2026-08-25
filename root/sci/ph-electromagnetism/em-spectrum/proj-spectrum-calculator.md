# ⚙️ Проєкт розрахунку спектральних параметрів та режимів поглинання

Для обчислення параметрів електромагнітної хвилі, оцінки скін-ефекту в провідниках, аналізу прозорості матеріалів та визначення спектрального діапазону потрібен спеціалізований розрахунковий модуль. У практичній інженерії радіочастотних пристроїв, силової електроніки, оптичних ліній та радіаційного захисту виникає постійна потреба конвертувати частоту `f` у довжину хвилі `λ`, обчислювати енергію кванту `E` (у джоулях та електронвольтах), визначати скін-шар у мідних чи алюмінієвих провідниках `δ` та встановлювати відповідну температуру абсолютно чорного тіла `T_peak` за законом зсуву Віна.

Нижче детально розібрано архітектуру, математичне підгрунтя, числову стійкість та програмну реалізацію такого калькулятора трьома мовами програмування: **C** (низькорівнева промислова реалізація для вбудованих систем із нульовим динамічним виділенням пам'яті), **C++** (строго типізований об'єктно-орієнтований модуль за стандартами C++17/C++20) та **Python** (скрипт аналізу даних із типізованими датакласами).

---

### Фізико-математичний алгоритм та числова стійкість

Калькулятор виконує перетворення за суворими фізичними константами CODATA:

1. **Швидкість світла у вакуумі:** `c = 299 792 458 м/с` (точне значення за визначенням SI).
2. **Стала Планка:** `h = 6.626 070 15 × 10⁻³⁴ Дж·с`.
3. **Елементарний заряд (конверсія еВ):** `1 еВ = 1.602 176 634 × 10⁻¹⁹ Дж`.
4. **Стала зсуву Віна:** `b = 2.897 771 95 × 10⁻³ м·К`.
5. **Електропровідність відпаленої міді (IACS):** `σ = 5.8 × 10⁷ См/м`.
6. **Магнітна стала вакууму:** `μ₀ = 4π × 10⁻⁷ Гн/м ≈ 1.256 637 06 × 10⁻⁶ Гн/м`.

#### Математична послідовність обчислень:
1. **Довжина хвилі у вакуумі:**
   ```
   λ = c / f
   ```
2. **Енергія фотона у джоулях та електронвольтах:**
   ```
   E_J = h · f
   E_eV = E_J / e
   ```
3. **Глибина скін-шару в міді:**
   ```
   ω = 2π · f
   δ = √( 2 / (ω · μ₀ · σ) )
   ```
4. **Температура максимуму випромінювання за Віном:**
   ```
   T_peak = b / λ
   ```
5. **Класифікація діапазону та біологічної дії:**
   - `f < 3 ГГц` → Радіохвилі (Radio)
   - `3 ГГц ≤ f < 300 ГГц` → Мікрохвилі (Microwave)
   - `300 ГГц ≤ f < 400 ТГц` → Інфрачервоне випромінювання (IR)
   - `400 ТГц ≤ f < 790 ТГц` → Видиме світло (Visible)
   - `790 ТГц ≤ f < 30 ПГц` → Ультрафіолет (UV)
   - `30 ПГц ≤ f < 30 ЕГц` → Рентгенівське випромінювання (X-Ray)
   - `f ≥ 30 ЕГц` → Гамма-випромінювання (Gamma)
   - **Критерій іонізації:** Якщо `E_eV ≥ 10.0 еВ` (середній УФ і вище), випромінювання класифікується як **іонізаційно небезпечне**, оскільки енергія фотона перевищує потенціал іонізації більшості хімічних зв'язків та атомів (водню, кисню, азоту).

#### Забезпечення числової стійкості (Numeric Precision):
Оскільки частота ЕМ-спектра покриває понад 24 порядки (від `1 Гц` до `10²⁴ Гц`), обчислення проводяться виключно у форматі з подвійною точністю `double` (64 біти IEEE 754), що забезпечує 15–17 значущих десяткових цифр. Це запобігає втраті точності при піднесенні до квадрата або добутку констант порядку `10⁻³⁴` та `10²⁴`.

---

### Архітектура програмних модулів у трьох мовних парадигмах

При побудові інженерного модуля аналізу спектра враховано вимоги до кожної мовної платформи:

- **Парадигма C (C99/C11):** Орієнтована на вбудовані мікроконтролери (STM32, ESP32, AVR, Zephyr OS). Використовує статичні структури `spectrum_info_t`, прості функції без виділення купи (`malloc`), чисті числові типи та явний захист від ділення на нуль.
- **Парадигма C++ (C++20):** Орієнтована на високоефективні інженерні пакети та системи моделювання. Використовує концепцію `constexpr` обчислень під час компіляції, строго типізовані `enum class SpectralBand`, простори імен `physics::em`, безалокаційні рядкові в'юшки `std::string_view` та константний доступ.
- **Парадигма Python (3.10+):** Орієнтована на наукові дослідження, обробку даних у Jupyter та швидке прототипування. Використовує строгі аннотації типів `dataclass(frozen=True)` для забезпечення незмінності обчислених параметрів.

---

### Програмна реалізація у трьох мовних парадигмах

:::tabs
```c
/* 
 * spectrum_calc.c — Повна промислова реалізація калькулятора ЕМ-спектра мовою C (C99/C11)
 * Модуль призначений для вбудованих систем, вимірювальних приладів та систем моніторингу.
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Фундаментальні фізичні константи */
#define C_SPEED     299792458.0         /* Швидкість світла в м/с (точна) */
#define H_PLANCK    6.62607015e-34      /* Константа Планка в Дж·с */
#define EV_JOULE    1.602176634e-19     /* 1 еВ у джоулях */
#define WIEN_CONST  2.89777195e-3       /* Константа зсуву Віна в м·К */
#define CU_SIGMA    5.8e7               /* Провідність міді у См/м */
#define MU_0        (4.0 * M_PI * 1e-7) /* Магнітна стала вакууму Гн/м */

/* Перелічуваний тип діапазонів спектра */
typedef enum {
    BAND_RADIO,
    BAND_MICROWAVE,
    BAND_INFRARED,
    BAND_VISIBLE,
    BAND_ULTRAVIOLET,
    BAND_XRAY,
    BAND_GAMMA
} em_band_t;

/* Структура паспортних даних ЕМ-сигналу */
typedef struct {
    double frequency_hz;      /* Частота в Гц */
    double wavelength_m;      /* Довжина хвилі у вакуумі в м */
    double energy_joules;     /* Енергія фотона у джоулях */
    double energy_ev;         /* Енергія фотона в електронвольтах */
    double skin_depth_cu_m;   /* Глибина скін-шару в міді в м */
    double wien_temp_k;       /* Еквівалентна температура чорного тіла в К */
    em_band_t band;           /* Спектральний діапазон */
    bool is_ionizing;         /* Прапор іонізуючої здатності */
    const char* band_name;    /* Назва діапазону українською */
} spectrum_info_t;

/* Повертає текстову назву діапазону */
const char* get_band_name(em_band_t band) {
    switch (band) {
        case BAND_RADIO:       return "Радіохвилі (Radio)";
        case BAND_MICROWAVE:   return "Мікрохвилі (Microwave / НВЧ)";
        case BAND_INFRARED:    return "Інфрачервоне випромінювання (IR)";
        case BAND_VISIBLE:     return "Видиме світло (Visible)";
        case BAND_ULTRAVIOLET: return "Ультрафіолет (UV)";
        case BAND_XRAY:        return "Рентгенівське випромінювання (X-Ray)";
        case BAND_GAMMA:       return "Гамма-випромінювання (Gamma)";
        default:               return "Невідомий діапазон";
    }
}

/* Обчислює паспортні дані сигналу за частотою */
spectrum_info_t calculate_by_frequency(double freq_hz) {
    spectrum_info_t info;
    if (freq_hz <= 0.0) {
        freq_hz = 1e-12; /* Захист від нульової чи від'ємної частоти */
    }

    info.frequency_hz = freq_hz;
    info.wavelength_m = C_SPEED / freq_hz;
    info.energy_joules = H_PLANCK * freq_hz;
    info.energy_ev = info.energy_joules / EV_JOULE;
    
    /* Обчислення скін-шару у мідному провіднику */
    double omega = 2.0 * M_PI * freq_hz;
    info.skin_depth_cu_m = sqrt(2.0 / (omega * MU_0 * CU_SIGMA));
    
    /* Розрахунок температури за законом зсуву Віна */
    info.wien_temp_k = WIEN_CONST / info.wavelength_m;

    /* Класифікація за частотою */
    if (freq_hz < 3.0e9) {
        info.band = BAND_RADIO;
    } else if (freq_hz < 3.0e11) {
        info.band = BAND_MICROWAVE;
    } else if (freq_hz < 4.0e14) {
        info.band = BAND_INFRARED;
    } else if (freq_hz < 7.9e14) {
        info.band = BAND_VISIBLE;
    } else if (freq_hz < 3.0e16) {
        info.band = BAND_ULTRAVIOLET;
    } else if (freq_hz < 3.0e19) {
        info.band = BAND_XRAY;
    } else {
        info.band = BAND_GAMMA;
    }

    /* Поріг іонізації прийнято на рівні 10 еВ (середній УФ) */
    info.is_ionizing = (info.energy_ev >= 10.0);
    info.band_name = get_band_name(info.band);

    return info;
}

/* Форматований вивід результатів у консоль */
void print_spectrum_card(const spectrum_info_t* info) {
    printf("\n==================================================\n");
    printf("   ПАСПОРТНА КАРТКА ЕЛЕКТРОМАГНІТНОГО СИГНАЛУ    \n");
    printf("==================================================\n");
    printf(" Частота (f):          %.4e Гц\n", info->frequency_hz);
    printf(" Довжина хвилі (λ):   %.4e м\n", info->wavelength_m);
    printf(" Енергія фотона (E):   %.4e еВ (%.4e Дж)\n", info->energy_ev, info->energy_joules);
    printf(" Скін-шар у міді (δ):  %.4e м\n", info->skin_depth_cu_m);
    printf(" Пікова темп. Віна:    %.2f K (%.2f °C)\n", info->wien_temp_k, info->wien_temp_k - 273.15);
    printf(" Спектральний діапазон: %s\n", info->band_name);
    printf(" Біологічна дія:      %s\n", info->is_ionizing ? "[!] ІОНІЗУЮЧЕ (Руйнує хімічні зв'язки)" : "[OK] Неіонізуюче (Безпечно)");
    printf("==================================================\n");
}

int main(void) {
    printf("Розрахунок тестових сигналів ЕМ-спектра (Мова C):\n");

    /* Тест 1: Радіо FM 100 МГц */
    spectrum_info_t fm_radio = calculate_by_frequency(100.0e6);
    print_spectrum_card(&fm_radio);

    /* Тест 2: Мобільний Wi-Fi 2.45 ГГц */
    spectrum_info_t wifi = calculate_by_frequency(2.45e9);
    print_spectrum_card(&wifi);

    /* Тест 3: Зелений лазер 532 нм */
    spectrum_info_t green_laser = calculate_by_frequency(C_SPEED / 532.0e-9);
    print_spectrum_card(&green_laser);

    /* Тест 4: Медичний рентген 30 ЕГц (3e19 Гц) */
    spectrum_info_t xray = calculate_by_frequency(3.0e19);
    print_spectrum_card(&xray);

    return 0;
}
```
```cpp
// 
// spectrum_calc.cpp — Об'єктно-орієнтований модуль аналізу спектра за стандартом C++20
// Модуль використовує constexpr обчислення, std::string_view, строго типізовані enum class
// 
#include <iostream>
#include <cmath>
#include <string_view>
#include <numbers>
#include <iomanip>
#include <array>

namespace physics::em {

// Фундаментальні константи у просторі імен
constexpr double c_speed    = 299792458.0;
constexpr double h_planck   = 6.62607015e-34;
constexpr double ev_joule   = 1.602176634e-19;
constexpr double wien_const = 2.89777195e-3;
constexpr double cu_sigma   = 5.8e7;
constexpr double mu_0       = 4.0 * std::numbers::pi * 1e-7;

enum class SpectralBand {
    Radio,
    Microwave,
    Infrared,
    Visible,
    Ultraviolet,
    XRay,
    Gamma
};

[[nodiscard]] constexpr std::string_view to_string(SpectralBand band) noexcept {
    switch (band) {
        case SpectralBand::Radio:       return "Радіохвилі (Radio)";
        case SpectralBand::Microwave:   return "Мікрохвилі (Microwave / НВЧ)";
        case SpectralBand::Infrared:    return "Інфрачервоне (IR)";
        case SpectralBand::Visible:     return "Видиме світло (Visible)";
        case SpectralBand::Ultraviolet: return "Ультрафіолет (UV)";
        case SpectralBand::XRay:        return "Рентгенівське (X-Ray)";
        case SpectralBand::Gamma:       return "Гамма-випромінювання (Gamma)";
    }
    return "Невідомий діапазон";
}

struct SpectrumRecord {
    double frequency_hz;
    double wavelength_m;
    double energy_ev;
    double skin_depth_cu_m;
    double wien_temp_k;
    SpectralBand band;
    bool is_ionizing;

    [[nodiscard]] static constexpr SpectrumRecord from_frequency(double freq_hz) noexcept {
        const double safe_freq = (freq_hz > 0.0) ? freq_hz : 1e-12;
        const double lambda = c_speed / safe_freq;
        const double energy_j = h_planck * safe_freq;
        const double energy_ev = energy_j / ev_joule;
        const double omega = 2.0 * std::numbers::pi * safe_freq;
        const double skin_m = std::sqrt(2.0 / (omega * mu_0 * cu_sigma));
        const double temp_k = wien_const / lambda;

        SpectralBand band = SpectralBand::Radio;
        if (safe_freq >= 3.0e19)      band = SpectralBand::Gamma;
        else if (safe_freq >= 3.0e16) band = SpectralBand::XRay;
        else if (safe_freq >= 7.9e14) band = SpectralBand::Ultraviolet;
        else if (safe_freq >= 4.0e14) band = SpectralBand::Visible;
        else if (safe_freq >= 3.0e11) band = SpectralBand::Infrared;
        else if (safe_freq >= 3.0e9)  band = SpectralBand::Microwave;

        return SpectrumRecord{
            .frequency_hz = safe_freq,
            .wavelength_m = lambda,
            .energy_ev = energy_ev,
            .skin_depth_cu_m = skin_m,
            .wien_temp_k = temp_k,
            .band = band,
            .is_ionizing = (energy_ev >= 10.0)
        };
    }

    [[nodiscard]] static constexpr SpectrumRecord from_wavelength(double wavelength_m) noexcept {
        const double safe_lambda = (wavelength_m > 0.0) ? wavelength_m : 1e-18;
        return from_frequency(c_speed / safe_lambda);
    }
};

void print_record(const SpectrumRecord& rec) {
    std::cout << "\n--------------------------------------------------\n";
    std::cout << "  ПАСПОРТНА КАРТКА СИГНАЛУ (C++20 Module)        \n";
    std::cout << "--------------------------------------------------\n";
    std::cout << std::scientific << std::setprecision(4);
    std::cout << " Частота:          " << rec.frequency_hz << " Гц\n";
    std::cout << " Довжина хвилі:   " << rec.wavelength_m << " м\n";
    std::cout << " Енергія фотона:  " << rec.energy_ev << " еВ\n";
    std::cout << " Скін-шар у міді: " << rec.skin_depth_cu_m << " м\n";
    std::cout << std::fixed << std::setprecision(2);
    std::cout << " Температура Віна: " << rec.wien_temp_k << " K\n";
    std::cout << " Діапазон:         " << to_string(rec.band) << "\n";
    std::cout << " Іонізуюче:        " << (rec.is_ionizing ? "ТАК [Вимоги захисту]" : "НІ [Безпечно]") << "\n";
    std::cout << "--------------------------------------------------\n";
}

} // namespace physics::em

int main() {
    using namespace physics::em;

    std::cout << "Спектральний аналіз (C++20):\n";

    // Тест 1: EUV Літографія 13.5 нм
    auto euv_chip = SpectrumRecord::from_wavelength(13.5e-9);
    print_record(euv_chip);

    // Тест 2: Позитронна анігіляція 511 кеВ (Гамма)
    constexpr double gamma_freq = (511.0e3 * ev_joule) / h_planck;
    auto gamma_annihilation = SpectrumRecord::from_frequency(gamma_freq);
    print_record(gamma_annihilation);

    return 0;
}
```
```py
# 
# spectrum_calc.py — Програмний аналізатор ЕМ-спектра мовою Python 3.10+
# Включає типізовані датакласи, форматований вивід та перевірку межі іонізації.
# 
import math
from dataclasses import dataclass
from enum import Enum

# Фізичні константи SI
C_SPEED = 299792458.0
H_PLANCK = 6.62607015e-34
EV_JOULE = 1.602176634e-19
WIEN_CONST = 2.89777195e-3
CU_SIGMA = 5.8e7
MU_0 = 4.0 * math.pi * 1e-7

class SpectralBand(Enum):
    RADIO = "Радіохвилі (Radio)"
    MICROWAVE = "Мікрохвилі (Microwave / НВЧ)"
    INFRARED = "Інфрачервоне (IR)"
    VISIBLE = "Видиме світло (Visible)"
    ULTRAVIOLET = "Ультрафіолет (UV)"
    XRAY = "Рентгенівське (X-Ray)"
    GAMMA = "Гамма-випромінювання (Gamma)"

@dataclass(frozen=True)
class SpectrumRecord:
    frequency_hz: float
    wavelength_m: float
    energy_ev: float
    skin_depth_cu_m: float
    wien_temp_k: float
    band: SpectralBand
    is_ionizing: bool

    @classmethod
    def from_frequency(cls, freq_hz: float) -> "SpectrumRecord":
        safe_freq = max(freq_hz, 1e-12)
        wavelength = C_SPEED / safe_freq
        energy_ev = (H_PLANCK * safe_freq) / EV_JOULE
        omega = 2.0 * math.pi * safe_freq
        skin_depth = math.sqrt(2.0 / (omega * MU_0 * CU_SIGMA))
        wien_temp = WIEN_CONST / wavelength

        if safe_freq >= 3.0e19:
            band = SpectralBand.GAMMA
        elif safe_freq >= 3.0e16:
            band = SpectralBand.XRAY
        elif safe_freq >= 7.9e14:
            band = SpectralBand.ULTRAVIOLET
        elif safe_freq >= 4.0e14:
            band = SpectralBand.VISIBLE
        elif safe_freq >= 3.0e11:
            band = SpectralBand.INFRARED
        elif safe_freq >= 3.0e9:
            band = SpectralBand.MICROWAVE
        else:
            band = SpectralBand.RADIO

        return cls(
            frequency_hz=safe_freq,
            wavelength_m=wavelength,
            energy_ev=energy_ev,
            skin_depth_cu_m=skin_depth,
            wien_temp_k=wien_temp,
            band=band,
            is_ionizing=(energy_ev >= 10.0)
        )

    @classmethod
    def from_wavelength(cls, wavelength_m: float) -> "SpectrumRecord":
        safe_lambda = max(wavelength_m, 1e-18)
        return cls.from_frequency(C_SPEED / safe_lambda)

def print_summary(rec: SpectrumRecord) -> None:
    print(f"\n--- Картка ЕМ-сигналу (Python) ---")
    print(f"Частота:         {rec.frequency_hz:.4e} Гц")
    print(f"Довжина хвилі:  {rec.wavelength_m:.4e} м")
    print(f"Енергія кванту: {rec.energy_ev:.4e} еВ")
    print(f"Скін-шар у міді: {rec.skin_depth_cu_m:.4e} м")
    print(f"Температура Віна: {rec.wien_temp_k:.2f} K")
    print(f"Діапазон:        {rec.band.value}")
    print(f"Іонізуюче:       {'ТАК' if rec.is_ionizing else 'НІ'}")
    print(f"----------------------------------")

if __name__ == "__main__":
    # Розрахунок червоного світлодіода 650 нм
    red_led = SpectrumRecord.from_wavelength(650e-9)
    print_summary(red_led)

    # Розрахунок промислового іонізатора 100 ПГц
    uv_c = SpectrumRecord.from_frequency(100e15)
    print_summary(uv_c)
```
:::

---

### Аналіз практичних режимів та трасування параметрів

Протестуємо розраховані значення калькулятора на п'яти типових частотах, що охоплюють увесь спектр:

#### 1. Силова мережа (50 Гц)
```
f = 50 Гц
λ = 5.996 × 10⁶ м  (6000 км — розмір континенту!)
E = 2.068 × 10⁻¹³ еВ  (абсолютно невідчутна квантовість)
δ (мідь) = 9.35 мм
Діапазон: Радіохвилі (VLF)
```
На частоті 50 Гц довжина хвилі порівнянна з радіусом Землі. Усі кабелі та електроприлади працюють виключно у зоні ближнього поля (`r << λ`), де електричне й магнітне поля можна розструктуровувати статично. Скін-шар 9.35 мм означає, що мідний дріт діаметром до 18 мм пропускає струм рівномірно по всьому перерізу.

#### 2. Мобільний зв'язок Wi-Fi / 5G (2.45 ГГц)
```
f = 2.45 × 10⁹ Гц
λ = 0.1224 м  (12.24 см)
E = 1.013 × 10⁻⁵ еВ
δ (мідь) = 2.09 мкм
Діапазон: Мікрохвилі (НВЧ)
```
Довжина хвилі 12.24 см збігається з геометричними розмірами антен у смартфонах та роутерах (чвертьхвильовий вибратор має довжину `λ/4 ≈ 3 см`). Скін-шар 2.09 мкм показує, що високочастотний струм протікає виключно у найтоншому поверхневому шарі провідника. Саме тому у високочастотній техніці друковані доріжки покривають тонким шаром срібла чи золота: глибші шари міді взагалі не беруть участі у проведеному струмі.

#### 3. Видиме зелене світло (532 нм, лазер)
```
f = 5.635 × 10¹⁴ Гц
λ = 5.32 × 10⁻⁷ м  (532 нм)
E = 2.33 еВ
δ (мідь) = 2.79 нм  (кілька атомних шарів — метал повністю відбиває світло)
T_peak = 5447 K  (температура поверхні зірок класу Сонця)
Діапазон: Видиме світло
```
Енергія кванту 2.33 еВ відповідає енергії хімічних зв'язків у білкових молекулах сітківки ока. Фотон поглинається родопсином, змушуючи молекулу змінювати конформацію, що генерує нервовий імпульс.

#### 4. EUV-літографія мікросхем (13.5 нм)
```
f = 2.221 × 10¹⁶ Гц
λ = 1.35 × 10⁻⁸ м  (13.5 нм)
E = 91.84 еВ
Діапазон: Екстремальний УФ (EUV)
Іонізуюче: ТАК (E > 10 еВ)
```
Енергії фотона 91.84 еВ достатньо, щоб вибити електрони з будь-якого матеріалу. На цій довжині хвилі повітря та звичайне скло є повністю непрозорими (світло поглинається на відстані кількох мікрометрів). Тому літографічні установки ASML працюють у глибокому вакуумі, а замість лінз використовують спеціальні багатошарові дзеркала з молібдену та кремнію.

#### 5. Медична гамма-діагностика (511 кеВ)
```
f = 1.236 × 10²⁰ Гц
λ = 2.426 × 10⁻¹² м  (2.426 пикометра)
E = 511 000 еВ  (511 кеВ)
Діапазон: Гамма-випромінювання
Іонізуюче: ТАК [Екстремальна небезпека]
```
Енергія фотона 511 кеВ дорівнює енергії спокою електрона (`m_e · c²`). Такі кванти народжуються при анігіляції позитронів у позитронно-емісійній томографії (ПЕТ). Вони легко пробивають тіло людини наскрізь і реєструються зовнішніми сцинтиляційними детекторами.

---

### Крайові випадки та обробка винятків

При інженерному використанні калькулятора слід враховувати фізичні межі застосовності:

1. **Нульова та від'ємна частота:** Фізична частота коливань `f` завжди додатна (`f > 0`). У разі передачі `f = 0` (постійний струм DC) довжина хвилі прямує до нескінченності `λ → ∞`, а скін-шар `δ → ∞`. У коді передбачено перевірку та захист від ділення на нуль.
2. **Нерелятивістське наближення середовища:** Калькулятор обчислює довжину хвилі у вакуумі. При поширенні в діелектрику з відносною проникністю `ε_r` довжина хвилі зменшується в `n = √ε_r` разів: `λ_medium = λ_vacuum / n`.
3. **Межа застосовності класичного скін-ефекту:** Формула `δ = √(2/(ωμσ))` справедлива лише тоді, коли скін-шар значно більший за довжину вільного пробігу електрона в металі (`l_e ≈ 40 нм` для міді при 300 K). На надвисоких частотах та при кріогенних температурах виникає **аномальний скін-ефект**, який вимагає квантово-механічного розрахунку.
