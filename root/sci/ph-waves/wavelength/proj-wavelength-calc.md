# ⚙️ Обчислення довжини хвилі та резонансних режимів у різних середовищах

У практичній інженерії — від розробки ультразвукових датчиків відстані та медичних УЗД-сканерів до проектування НВЧ-антен, радіоліній зв'язку та волоконно-оптичних систем ущільнення WDM — виникає повсякденна потреба обчислювати довжину хвилі `λ` за частотою сигналу `f` та фізичними параметрами середовища. Оскільки фазова швидкість поширення хвилі залежить від температури газу, тиску, показника заломлення оптики, солоності води чи пружних модулів металу, точний інженерний перерахунок вимагає врахування фізичних властивостей конкретного середовища.

### 1. Фізико-математичні моделі та алгоритми розрахунку

Даний обчислювальний модуль реалізує три ключові інженерні задачі розрахунку просторових параметрів хвильових процесів:

#### А. Температурно залежна акустика повітря та газів

Швидкість поширення звукових хвиль в ідеальному газі визначається адіабатичним модулем об'ємної пружності `B = γ · P` та густиною газу `ρ = P · M / (R · T)`:

```
v = √(B / ρ) = √(γ · R · T / M)
```

де `γ` — показник адіабати (для двоатомних газів повітря `γ ≈ 1.40`), `R = 8.314` Дж/(моль·К) — універсальна газова стала, `M` — молярна маса газу (для сухого повітря `M ≈ 0.02896` кг/моль), `T` — абсолютна температура в кельвінах (`T = t_C + 273.15`).

Для сухого повітря колоатмосферного тиску це співвідношення надійно апроксимується термодинамічною формулою:

```
v(t_C) = 331.3 · √(1 + t_C / 273.15)  [м/с]
```

На основі розрахованої швидкості `v` алгоритм визначає просторовий період хвилі `λ = v / f` та хвильове число `k = 2π / λ`, яке задає просторовий зсув фази `Δφ = k · Δx`. Знання `k` є вирішальним для розрахунку фазованих акустичних антенних решіток та усунення інтерференційних спотворень у звукових системах.

#### Б. Оптичні хвилі у прозорих діелектриках та волоконних світловодах

При переході світла з вакууму у прозоре діелектричне середовище з показником заломлення `n` (наприклад, у кварцове скло `n ≈ 1.444` для інфрачервоного світла 1550 нм) фазова швидкість електромагнітної хвилі зменшується до:

```
v = c₀ / n = c₀ / √(ε_r · μ_r)
```

Оскільки часова частота світлового генератора (лазера) `f` задається квантовим переходом і є часовим інваріантом, довжина хвилі у середовищі стискається пропорційно показникові заломлення:

```
λ_medium = λ₀ / n
```

Модуль виконує розрахунок реальної довжини хвилі у волокні для стандартних телекомунікаційних частот оптичного ущільнення DWDM (зокрема, центральної частоти каналу C-band `f = 193.4` ТГц, що відповідає довжині хвилі у вакуумі `λ₀ ≈ 1550` нм).

#### В. Резонансні стоячі хвилі та просторове розташування вузлів

При додаванні двох гармонічних хвиль однакової амплітуди й частоти, що поширюються у протилежних напрямках (наприклад, падаючої та відбитої від акустичної чи електричної межі), утворюється стояча хвиля:

```
u(x, t) = 2A · sin(k·x) · cos(ω·t)
```

Точки простору, в яких амплітуда коливань постійно дорівнює нулю (`sin(k·x) = 0`), називаються **вузлами**. Вузли розташовані у точках `k·x_n = n·π`, звідки:

```
x_n = n · (π / k) = n · (λ / 2)      [де n = 0, 1, 2, 3...]
```

Інтервал між сусідніми вузлами є строго постійним і дорівнює рівно півхвилі `d = λ / 2`. Модуль розраховує повну послідовність просторових координат вузлів уздовж резонатора чи труби довжиною `L`.

### 2. Аналіз чисельних нюансів та обробки крайових випадків

При практичній інженерній реалізації обчислювальних алгоритмів важливо враховувати такі чисельні особливості:

1. **Запобігання накопиченню похибки плаваючої коми:** У чисельному типі подвійної точності (`double`) циклічне додавання кроку `pos += spacing` призводить до накопичення дрібної похибки округлення. Якщо останній вузол має перебувати строго на правому краї резонатора `pos = L`, через похибку float обчислене значення може становити `1.0000000000000002`. Традиційна перевірка `pos <= L` у такому разі поверне `false`, і останній вузол буде помилково втрачено. Для усунення цього дефекту до межі додається мала машинова поправка `1e-9`: `pos <= L + 1e-9`.
2. **Валідація фізичних меж та обробка помилок:** Частота `f`, швидкість `v` та показник заломлення `n` повинні бути строго додатними величинами (`> 0`). Передача нуля або від'ємного значення викликає фізично безглузді результати (ділення на нуль, уявна швидкість). У програмі передбачено строгий контроль вхідних даних: виняток `ValueError` у Python, обгортка `std::expected<WaveProperties, WaveError>` у C++23 та код стану у C.
3. **Керування пам'яттю у мові C:** Для запобігання виходу за межі масиву (Out-of-bounds write) у C-реалізації функція розрахунку вузлів приймає верхню межу розміру статичного буфера `max_nodes` та виконує перевірку `count < max_nodes`.

Нижче наведено повноцінні, ідіоматичні реалізації цього розрахункового модуля трьома мовами програмування.

:::tabs
```py
import math
from dataclasses import dataclass
from typing import List

# Фізична константа швидкості світла у вакуумі (м/с)
SPEED_OF_LIGHT_VACUUM: float = 299792458.0

@dataclass
class WaveProperties:
    """Структура даних для збереження розрахованих параметрів хвилі."""
    frequency_hz: float
    speed_m_s: float
    wavelength_m: float
    wavenumber_k: float  # просторова частота, рад/м
    period_s: float

def acoustic_speed_in_air(temperature_celsius: float) -> float:
    """Обчислення швидкості звуку в сухому повітрі при заданій температурі (°C)."""
    return 331.3 * math.sqrt(1.0 + temperature_celsius / 273.15)

def em_wavelength_in_medium(frequency_hz: float, refractive_index: float) -> WaveProperties:
    """Обчислення параметрів електромагнітної хвилі в середовищі з показником заломлення n."""
    if frequency_hz <= 0.0 or refractive_index <= 0.0:
        raise ValueError("Частота та показник заломлення мусять бути додатними числами")
    
    speed = SPEED_OF_LIGHT_VACUUM / refractive_index
    wavelength = speed / frequency_hz
    wavenumber = 2.0 * math.pi / wavelength
    period = 1.0 / frequency_hz
    
    return WaveProperties(
        frequency_hz=frequency_hz,
        speed_m_s=speed,
        wavelength_m=wavelength,
        wavenumber_k=wavenumber,
        period_s=period
    )

def calculate_standing_wave_nodes(length_m: float, wavelength_m: float) -> List[float]:
    """Обчислення координат вузлів стоячої хвилі на відрізку довжиною L."""
    if wavelength_m <= 0.0 or length_m < 0.0:
        return []
    
    node_spacing = wavelength_m / 2.0
    nodes = []
    current_pos = 0.0
    # Мала поправка 1e-9 запобігає втраті останнього вузла через округлення float
    while current_pos <= length_m + 1e-9:
        nodes.append(current_pos)
        current_pos += node_spacing
    return nodes

def main() -> None:
    # 1. Акустична хвиля 40 кГц (ультразвуковий дальномір) у повітрі при 20°C
    f_us = 40000.0
    v_air = acoustic_speed_in_air(20.0)
    lambda_air = v_air / f_us
    k_air = 2.0 * math.pi / lambda_air
    
    print(f"=== 1. Акустика (40 кГц у повітрі при 20°C) ===")
    print(f"Швидкість звуку: {v_air:.2f} м/с")
    print(f"Довжина хвилі:   {lambda_air * 1000.0:.3f} мм")
    print(f"Хвильове число:  {k_air:.2f} рад/м")

    # 2. Оптична хвиля 1550 нм у кварцовому волокні (n = 1.444)
    f_opt = 193.4e12  # 193.4 ТГц (C-band)
    em_prop = em_wavelength_in_medium(f_opt, refractive_index=1.444)
    
    print(f"\n=== 2. Волоконна оптика (193.4 ТГц, C-band) ===")
    print(f"Швидкість у волокні: {em_prop.speed_m_s / 1e8:.4f} × 10⁸ м/с")
    print(f"Довжина хвилі:       {em_prop.wavelength_m * 1e9:.2f} нм")
    print(f"Хвильове число k:    {em_prop.wavenumber_k / 1e6:.4f} × 10⁶ рад/м")

    # 3. Вузли стоячої хвилі у трубі довжиною 1.0 м на частоті 500 Гц
    v_sound = acoustic_speed_in_air(20.0)
    lambda_500 = v_sound / 500.0
    nodes = calculate_standing_wave_nodes(1.0, lambda_500)
    print(f"\n=== 3. Вузли стоячої хвилі (500 Гц, L = 1.0 м) ===")
    print(f"Довжина хвилі λ: {lambda_500:.3f} м (крок між вузлами λ/2 = {lambda_500/2:.3f} м)")
    print(f"Координати вузлів (м): {[round(n, 3) for n in nodes]}")

if __name__ == "__main__":
    main()
```
```c
#include <stdio.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define SPEED_OF_LIGHT_VACUUM 299792458.0

typedef struct {
    double frequency_hz;
    double speed_m_s;
    double wavelength_m;
    double wavenumber_k;
    double period_s;
} WaveProperties;

/* Обчислення швидкості звуку у сухому повітрі (°C) */
double acoustic_speed_in_air(double temp_celsius) {
    return 331.3 * sqrt(1.0 + temp_celsius / 273.15);
}

/* Обчислення параметрів хвилі з валідацією вхідних даних */
int calculate_wave_properties(double frequency_hz, double speed_m_s, WaveProperties* out_prop) {
    if (frequency_hz <= 0.0 || speed_m_s <= 0.0 || !out_prop) {
        return 0;
    }
    out_prop->frequency_hz = frequency_hz;
    out_prop->speed_m_s = speed_m_s;
    out_prop->wavelength_m = speed_m_s / frequency_hz;
    out_prop->wavenumber_k = (2.0 * M_PI) / out_prop->wavelength_m;
    out_prop->period_s = 1.0 / frequency_hz;
    return 1;
}

/* Розрахунок вузлів стоячої хвилі у статичний масив */
int calculate_standing_wave_nodes(double length_m, double wavelength_m, double* out_nodes, size_t max_nodes) {
    if (wavelength_m <= 0.0 || length_m < 0.0 || !out_nodes) {
        return 0;
    }
    double spacing = wavelength_m / 2.0;
    size_t count = 0;
    for (double pos = 0.0; pos <= length_m + 1e-9 && count < max_nodes; pos += spacing) {
        out_nodes[count++] = pos;
    }
    return (int)count;
}

int main(void) {
    WaveProperties prop;
    double v_air = acoustic_speed_in_air(20.0);
    
    if (calculate_wave_properties(40000.0, v_air, &prop)) {
        printf("=== 1. Акустика (40 кГц у повітрі 20°C) ===\n");
        printf("Швидкість: %.2f м/с\n", prop.speed_m_s);
        printf("Довжина хвилі: %.3f мм\n", prop.wavelength_m * 1000.0);
        printf("Хвильове число k: %.2f рад/м\n", prop.wavenumber_k);
    }

    double em_speed = SPEED_OF_LIGHT_VACUUM / 1.444; // кварцове волокно n = 1.444
    if (calculate_wave_properties(193.4e12, em_speed, &prop)) {
        printf("\n=== 2. Волоконна оптика (193.4 ТГц) ===\n");
        printf("Швидкість у волокні: %.4e м/с\n", prop.speed_m_s);
        printf("Довжина хвилі: %.2f нм\n", prop.wavelength_m * 1e9);
        printf("Хвильове число k: %.4e рад/м\n", prop.wavenumber_k);
    }

    double nodes[16];
    double lambda_500 = v_air / 500.0;
    int node_count = calculate_standing_wave_nodes(1.0, lambda_500, nodes, 16);
    printf("\n=== 3. Вузли стоячої хвилі (500 Гц, L = 1.0 м) ===\n");
    for (int i = 0; i < node_count; ++i) {
        printf("Вузол %d: %.3f м\n", i + 1, nodes[i]);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <format>
#include <expected>

constexpr double SPEED_OF_LIGHT_VACUUM = 299792458.0;

struct WaveProperties {
    double frequency_hz;
    double speed_m_s;
    double wavelength_m;
    double wavenumber_k; // просторова частота, рад/м
    double period_s;
};

enum class WaveError {
    InvalidFrequency,
    InvalidSpeed,
    InvalidRefractiveIndex
};

class WaveCalculator {
public:
    // Обчислення швидкості звуку у сухий атмосфері (°C)
    [[nodiscard]] static constexpr double acoustic_speed_air(double temp_celsius) noexcept {
        return 331.3 * std::sqrt(1.0 + temp_celsius / 273.15);
    }

    // Обчислення параметрів хвилі з використанням std::expected (C++23)
    [[nodiscard]] static std::expected<WaveProperties, WaveError> compute(double frequency_hz, double speed_m_s) noexcept {
        if (frequency_hz <= 0.0) return std::unexpected(WaveError::InvalidFrequency);
        if (speed_m_s <= 0.0) return std::unexpected(WaveError::InvalidSpeed);

        const double wavelength = speed_m_s / frequency_hz;
        const double wavenumber = (2.0 * std::numbers::pi) / wavelength;
        const double period = 1.0 / frequency_hz;

        return WaveProperties{
            .frequency_hz = frequency_hz,
            .speed_m_s = speed_m_s,
            .speed_m_s = speed_m_s,
            .wavelength_m = wavelength,
            .wavenumber_k = wavenumber,
            .period_s = period
        };
    }

    // Генерація списку координат вузлів стоячої хвилі
    [[nodiscard]] static std::vector<double> standing_wave_nodes(double length_m, double wavelength_m) {
        std::vector<double> nodes;
        if (wavelength_m <= 0.0 || length_m < 0.0) return nodes;

        const double spacing = wavelength_m / 2.0;
        for (double pos = 0.0; pos <= length_m + 1e-9; pos += spacing) {
            nodes.push_back(pos);
        }
        return nodes;
    }
};

int main() {
    const double v_air = WaveCalculator::acoustic_speed_air(20.0);
    auto us_res = WaveCalculator::compute(40000.0, v_air);

    if (us_res) {
        std::cout << "=== 1. Акустика (40 кГц у повітрі 20°C) ===\n";
        std::cout << "Швидкість звуку: " << us_res->speed_m_s << " м/с\n";
        std::cout << "Довжина хвилі: " << (us_res->wavelength_m * 1000.0) << " мм\n";
        std::cout << "Хвильове число k: " << us_res->wavenumber_k << " рад/м\n";
    }

    const double em_speed = SPEED_OF_LIGHT_VACUUM / 1.444;
    auto opt_res = WaveCalculator::compute(193.4e12, em_speed);
    if (opt_res) {
        std::cout << "\n=== 2. Волоконна оптика (193.4 ТГц) ===\n";
        std::cout << "Довжина хвилі: " << (opt_res->wavelength_m * 1e9) << " нм\n";
        std::cout << "Хвильове число k: " << opt_res->wavenumber_k << " рад/м\n";
    }

    const double lambda_500 = v_air / 500.0;
    auto nodes = WaveCalculator::standing_wave_nodes(1.0, lambda_500);
    std::cout << "\n=== 3. Вузли стоячої хвилі (500 Гц, L = 1.0 м) ===\n";
    for (size_t i = 0; i < nodes.size(); ++i) {
        std::cout << "Вузол " << (i + 1) << ": " << nodes[i] << " м\n";
    }

    return 0;
}
```
:::

### 3. Інженерні пастки та аналіз розрахованих режимів

При застосуванні розрахованих довжин хвиль у реальних апаратних комплексах виникають такі типові проблеми:

1. **Температурний дрейф у сонарних вимірювальних системах:** П'єзокерамічний диск ультразвукового датчика має фіксовані геометричні розміри, які визначають його резонансну частоту `f = 40 кГц`. Якщо температура довкілля змінюється від -10°C до +40°C, швидкість звуку змінюється від `325.2 м/с` до `354.8 м/с`. Відповідно, довжина хвилі змінюється від `8.13 мм` до `8.87 мм`. Якщо мікроконтролер обчислює відстань до перешкоди `D = v · t_delay / 2` за зафіксованим у прошивці значенням швидкості при +20°C (`343 м/с`), похибка вимірювання відстані сягне `±4.5%` (що становить майже 9 см на відстані 2 метри). Для точних вимірювань необхідно вносити динамічну температурну компенсацію швидкості звуку перед обчисленням відстані.
2. **Період волоконних брегівських решіток (FBG):** Волоконно-оптичний брегівський датчик являє собою ділянку одномодового світловоду із періодично нанесеним ультрафіолетом покажчиком заломлення. Резонансне відбивання світла виникає на брегівській довжині хвилі `λ_Bragg = 2 · n_eff · Λ`, де `n_eff` — ефективний показник заломлення модального поля, `Λ` — просторовий період решітки. При проектуванні решітки для телекомунікаційного лазера з довжиною хвилі у вакуумі `1550 нм` її фізичний геометричний крок у склі має становити всього `Λ = 1550 / (2 · 1.444) ≈ 536.7 нм`. При розтягуванні волокна деформацією на `0.1%` крок `Λ` зростає на `0.53 нм`, що зсуває спектр відбивання на `1.55 нм` — саме на цьому явищі засновано надчутливі волоконно-оптичні тензодатчики.
3. **Межові умови акустичних трубок (відкриті та закриті кінці):** У розрахунку стоячих хвиль передбачено закріплені межі або закриті кінці трубки (де утворюються вузли зміщення). Якщо ж один кінець трубки відкритий, на ньому утворюється пучність зміщення (вузол тиску), а найнижчий резонансний режим виникає на довжині хвилі `λ = 4L` (четвертьхвильовий резонатор). У такому разі перший вузол розташований на закритому кінці `x = 0`, а найближча пучність — на зрізі труби `x = L = λ / 4`.
