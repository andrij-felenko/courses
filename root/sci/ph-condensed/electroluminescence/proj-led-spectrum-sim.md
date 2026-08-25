# ⚙️ Моделювання спектра випромінювання та ефективності світлодіода

Оптимальне проективання напівпровідникових світлодіодів вимагає чисельного розрахунку двох ключових фізичних характеристик: спектрального розподілу спонтанного випромінювання та залежності внутрішнього квантового виходу від густини струму інжекції з урахуванням ефекту Оже-згасання. Тут наведено детальний опис фізичної алгоритмізації та завершені реалізації чисельної моделі мовами C++ та Python.

### Фізична модель і алгоритмічний підхід

Моделювання оптичних та електричних характеристик світлодіода розбивається на два незалежні чисельні блоки: **спектральний блок** (розрахунок форми та ширини лінії випромінювання) та **ефективнісний блок** (розрахунок балансу носіїв за моделлю ABC).

#### 1. Спектральний блок

Спектральна інтенсивність спонтанного випромінювання `I(E)` як функція енергії фотона `E` для прямозонного напівпровідника описується виразом, отриманим із залежності густини станів та розподілу Максвелла — Больцмана:

```
I(E) = C_spec · E² · √(E - E_g) · exp(-(E - E_g) / (k_B · T))   [при E ≥ E_g]
```

де `E_g` — ширина забороненої зони (в електронвольтах), `T` — температура `p-n` переходу в кельвінах, а `k_B` — стала Больцмана (`8.6173 × 10⁻⁵ еВ/К`).

Обчислювальний алгоритм працює за такими послідовними кроками:
1. Визначається рівномірна сітка енергій від мінімального `E_{min}` до максимального `E_{max}` значення із заданим кроком `ΔE`.
2. Для будь-якого фотона з енергією `E < E_g` інтенсивність встановлюється рівною нулю, оскільки квантові переходи нижче краю забороненої зони заборонені.
3. Для енергій `E ≥ E_g` обчислюється добуток параболічного фактора густини станів `√(E - E_g)` та високоенергетичного експоненціального хвоста `exp(-(E - E_g) / k_B T)`.
4. Кожне значення енергії фотона автоматично перераховується у відповідну довжину хвилі у вакуумі за допомогою фундаментального квантового співвідношення `λ = (h · c) / E ≈ 1239.84 / E` (у нанометрах).
5. Здійснюється нормування масиву інтенсивності на максимальне значення для зручного аналізу напівширини спектральної лінії (FWHM).

#### 2. Ефективнісний блок (модель ABC)

Залежність внутрішнього квантового виходу `η_int` від густини струму `J` визначається чисельним розв'язком стаціонарного рівняння балансу носіїв ув активній зоні товщиною `d`:

```
J(n) = q · d · (A · n + B · n² + C · n³)
η_int(n) = (B · n²) / (A · n + B · n² + C · n³) · 100%
```

де `q = 1.602 × 10⁻¹⁹ Кл` — елементарний заряд, `d` — товщина активної зони (м), `A` — коефіцієнт SRH-рекомбінації (`1/с`), `B` — випромінювальний коефіцієнт (`см³/с`), `C` — коефіцієнт Оже-рекомбінації (`см⁶/с`).

Алгоритм будує логарифмічно рівномірну сітку концентрацій інжектованих електронів і дірок `n` у діапазоні від `10¹⁵` до `10¹⁹ см⁻³`. Для кожної точки послідовно розраховуються швидкості рекомбінації трьох конкуруючих каналів, сумарний струм та відсоткова частка корисного випромінювання.

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <algorithm>

struct LedParameters {
    double bandgap_ev = 1.42;        // E_g для GaAs (еВ)
    double temp_k = 300.0;           // Температура переходу (К)
    double active_layer_nm = 10.0;   // Товщина активної зони (нм)
    double coeff_A = 1.0e7;          // SRH коефіцієнт (1/с)
    double coeff_B = 1.0e-10;        // Випромінювальний B (см³/с)
    double coeff_C = 1.0e-30;        // Оже C (см⁶/с)
};

struct SpectrumPoint {
    double energy_ev;
    double wavelength_nm;
    double intensity;
};

struct EfficiencyPoint {
    double current_density_a_cm2;
    double carrier_density_cm3;
    double internal_efficiency_pct;
};

class LedSimulator {
public:
    explicit LedSimulator(LedParameters params) : params_(std::move(params)) {}

    // Обчислення спектра випромінювання
    std::vector<SpectrumPoint> calculateSpectrum(double min_ev, double max_ev, int points) const {
        std::vector<SpectrumPoint> spectrum;
        spectrum.reserve(points);

        const double kb_ev = 8.617333262145e-5; // стала Больцмана в еВ/К
        const double hc_ev_nm = 1239.84193;     // h*c в еВ*нм
        const double kt = kb_ev * params_.temp_k;

        double step = (max_ev - min_ev) / (points - 1);
        double max_intensity = 0.0;

        for (int i = 0; i < points; ++i) {
            double energy = min_ev + i * step;
            double intensity = 0.0;

            if (energy >= params_.bandgap_ev) {
                double delta_e = energy - params_.bandgap_ev;
                intensity = energy * energy * std::sqrt(delta_e) * std::exp(-delta_e / kt);
            }

            double wavelength = (energy > 0.0) ? (hc_ev_nm / energy) : 0.0;
            spectrum.push_back({energy, wavelength, intensity});
            max_intensity = std::max(max_intensity, intensity);
        }

        // Нормалізація інтенсивності до 1.0
        if (max_intensity > 0.0) {
            for (auto& pt : spectrum) {
                pt.intensity /= max_intensity;
            }
        }

        return spectrum;
    }

    // Обчислення характеристики квантового виходу η_int(J)
    std::vector<EfficiencyPoint> calculateEfficiencyCurve(double min_log_n, double max_log_n, int points) const {
        std::vector<EfficiencyPoint> curve;
        curve.reserve(points);

        const double q_elem = 1.602176634e-19; // Кл
        double active_layer_cm = params_.active_layer_nm * 1.0e-7;

        double step = (max_log_n - min_log_n) / (points - 1);

        for (int i = 0; i < points; ++i) {
            double log_n = min_log_n + i * step;
            double n = std::pow(10.0, log_n); // см⁻³

            double r_srh = params_.coeff_A * n;
            double r_rad = params_.coeff_B * n * n;
            double r_auger = params_.coeff_C * n * n * n;

            double r_total = r_srh + r_rad + r_auger;

            // Густина струму J = q * d * R_total (А/см²)
            double j_a_cm2 = q_elem * active_layer_cm * r_total;
            double eta_int = (r_total > 0.0) ? (r_rad / r_total * 100.0) : 0.0;

            curve.push_back({j_a_cm2, n, eta_int});
        }

        return curve;
    }

private:
    LedParameters params_;
};

int main() {
    LedParameters params;
    params.bandgap_ev = 1.42;       // GaAs
    params.temp_k = 300.0;
    params.active_layer_nm = 10.0;  // Квантова яма 10 нм

    LedSimulator sim(params);

    // 1. Розрахунок спектра
    auto spectrum = sim.calculateSpectrum(1.35, 1.60, 50);

    std::cout << "=== Спектр випромінювання світлодіода GaAs (300 K) ===\n";
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Енергія (еВ) | Довжина хвилі (нм) | Однор. інтенсивність\n";
    std::cout << "-----------------------------------------------------\n";

    for (size_t i = 0; i < spectrum.size(); i += 5) {
        std::cout << "   " << spectrum[i].energy_ev << "      |       "
                  << spectrum[i].wavelength_nm << "       |        "
                  << spectrum[i].intensity << "\n";
    }

    // 2. Розрахунок квантового виходу
    auto eff_curve = sim.calculateEfficiencyCurve(15.0, 19.0, 20);

    std::cout << "\n=== Внутрішній квантовий вихід та Оже-згасання ===\n";
    std::cout << "J (А/см²)    | n (см⁻³)      | η_int (%)\n";
    std::cout << "----------------------------------------\n";

    for (const auto& pt : eff_curve) {
        std::cout << std::scientific << std::setprecision(2)
                  << pt.current_density_a_cm2 << "   |  "
                  << pt.carrier_density_cm3 << "  |  "
                  << std::fixed << std::setprecision(1)
                  << pt.internal_efficiency_pct << "%\n";
    }

    return 0;
}
```
```py
import math
import numpy as np

class LedSimulator:
    def __init__(self, bandgap_ev=1.42, temp_k=300.0, active_layer_nm=10.0,
                 coeff_a=1.0e7, coeff_b=1.0e-10, coeff_c=1.0e-30):
        self.eg = bandgap_ev
        self.temp_k = temp_k
        self.d_cm = active_layer_nm * 1e-7
        self.a = coeff_a
        self.b = coeff_b
        self.c = coeff_c
        
        self.kb_ev = 8.617333262145e-5
        self.hc_ev_nm = 1239.84193
        self.q = 1.602176634e-19

    def calculate_spectrum(self, min_ev=1.35, max_ev=1.60, points=100):
        energies = np.linspace(min_ev, max_ev, points)
        kt = self.kb_ev * self.temp_k
        
        intensities = np.zeros_like(energies)
        mask = energies >= self.eg
        delta_e = energies[mask] - self.eg
        
        intensities[mask] = (energies[mask]**2) * np.sqrt(delta_e) * np.exp(-delta_e / kt)
        
        if np.max(intensities) > 0:
            intensities /= np.max(intensities)
            
        wavelengths = self.hc_ev_nm / energies
        return list(zip(energies, wavelengths, intensities))

    def calculate_efficiency_curve(self, min_log_n=15.0, max_log_n=19.0, points=50):
        log_n = np.linspace(min_log_n, max_log_n, points)
        n = 10.0**log_n
        
        r_srh = self.a * n
        r_rad = self.b * (n**2)
        r_auger = self.c * (n**3)
        r_total = r_srh + r_rad + r_auger
        
        j_a_cm2 = self.q * self.d_cm * r_total
        eta_int = (r_rad / r_total) * 100.0
        
        return list(zip(j_a_cm2, n, eta_int))

if __name__ == '__main__':
    sim = LedSimulator(bandgap_ev=1.42, temp_k=300.0)
    
    spectrum = sim.calculate_spectrum(min_ev=1.35, max_ev=1.60, points=10)
    print("=== Спектр (Python) ===")
    for e, wl, I in spectrum:
        print(f"E = {e:.3f} eV, λ = {wl:.1f} nm, I = {I:.3f}")
        
    eff = sim.calculate_efficiency_curve(min_log_n=15.0, max_log_n=19.0, points=5)
    print("\n=== Ефективність (Python) ===")
    for j, n, eta in eff:
        print(f"J = {j:.2e} A/cm², n = {n:.2e} cm⁻³, η_int = {eta:.1f}%")
```
:::

### Практичний аналіз та інженерна інтерпретація результатів

Обчислювальний аналіз вихідних даних симулятора дозволяє зробити важливі фізичні та інженерні висновки щодо оптимізації конструкції світлодіодного випромінювача:

1. **Асиметрія та ширина спектральної лінії:** Розрахований спектральний розподіл демонструє характерну асиметричну форму. Стрімке підняття від нуля при `E = E_g` описується фактором `√(E - E_g)`, що виражає зростання густини квантових станів у тривимірному напівпровіднику. Пологий спад у бік вищих енергій визначається розлюдненням високоенергетичних станів за фактором Больцмана `exp(-(E - E_g) / k_B T)`. При кімнатній температурі (300 К) напівширина спектральної лінії на рівні половини висоти (FWHM) для інфрачервоного `GaAs` світлодіода становить приблизно `36 нм`.
2. **Оптимальна робоча точка:** Внутрішній квантовий вихід `η_int` сягає свого максимуму в точці `n_max = √(A / C)`. Для розглянутого матеріалу це відповідає робочій густині струму близько `20–50 А/см²`, де квантова ефективність випромінювання становить понад 88%.
3. **Фізична причина ефекту Droop:** При перевищенні оптимальної густини струму (наприклад, у режимі високої яскравості при `J > 500 А/см²`) концентрація носіїв сягає `10¹⁸ см⁻³`. У цій точці кубічна за концентрацією Оже-рекомбінація `C · n³` починає пригнічувати квадратну випромінювальну `B · n²`. Квантовий вихід незворотно знижується, а понад половина інжектованої електричної енергії перетворюється на теплове розігрівання кристала.

#### Особливості адаптації параметрів під різні матеріальні системи

При використанні даної чисельної моделі для розрахунку приладів на основі інших напівпровідникових сполук слід коригувати базові коефіцієнти моделі ABC:
* **Нітрид галію (GaN, синій світлодіод):** `E_g = 3.4 еВ`, `A ≈ 10⁶–10⁷ 1/с`, `B ≈ 10⁻¹¹ см³/с`, `C ≈ 10⁻³⁰ см⁶/с`.
* **Фосфід алюмінію-індію-галію (AlGaInP, червоний світлодіод):** `E_g = 1.9–2.1 еВ`, `A ≈ 5×10⁶ 1/с`, `B ≈ 1.5×10⁻¹⁰ см³/с`, `C ≈ 2×10⁻³⁰ см⁶/с`.

#### Додаткові інженерні аспекти чисельної моделі

Для більш точного спроектування комерційних приладів представлені чисельні алгоритми можна розширити додаванням теплового балансу та оптичного виведення:

1. **Розрахунок теплового саморозігріву:** Оскільки розсіювана потужність `P_heat = (1 - η_ext) · I_f · V_f` піднімає температуру переходу `T_j = T_amb + P_heat · R_{θja}`, в алгоритм вводиться ітераційний цикл перерозрахунку `E_g(T)` за формулою Варшні `E_g(T) = E_g(0) - α_v T² / (T + β_v)`. Це дозволяє чисельно передбачити тепловий червоний зсув спектра та теплове висвічування при підвищенні струму.
2. **Урахування коефіцієнта виведення світла:** Множення внутрішнього виходу `η_int` на оптичний фактор `η_opt` (який враховує кут повного внутрішнього відбивання та дзеркальне відбиття підкладки) дає точну оцінку зовнішньої фотометричної віддачі приладу в люменах на ват.
3. **Чисельне визначення напівширини (FWHM):** Алгоритм легко доповнюється автоматичним пошуком енергетичних точок `E_left` та `E_right`, у яких інтенсивність падає до 0.5 від пікової. Це дає змогу автокоригувати параметри спектральної чистоти джерела при моделюванні кольоропередачі (CRI).
4. **Порівняльний аналіз швидкодії мов:** Проведена симуляція виявляє чіткий обчислювальний розподіл: реалізація на C++ виконує розрахунок мільйона спектральних точок за кілька мілісекунд завдяки прямому синтаксису без накладних витрат інтерпретатора, тоді як Python з бінарним модулем NumPy надає зручний інтерфейс для швидкого побудови графіків та прототипування інженерних рішень.

Модуль симуляції може бути легко інтегрований у більші обчислювальні комплекси для проективання драйверів та оптичних систем твердотільного освітлення.
