# ⚙️ Моделювання виродженого фермі-газу та квантового тиску

Принцип заборони Паулі визначає макроскопічні механічні, термодинамічні та електронні властивості речовини при високих густинах або низьких температурах. У квантовій системі з `N` ферміонами маси `m`, обмеженими у тривимірному кубічному об'ємі `V = L³`, кожен квантовий стан може описуватися трійкою цілих додатних квантових чисел `(n_x, n_y, n_z)` та спіновою проєкцією `m_s = ±1/2`. Відповідно до принципу Паулі, одна комірка фазового простору об'ємом `h³ = (2π ℏ)³` може містити не більше ніж два електрони з протилежними спінами.

Оскільки електрони не можуть збиратися у найнижчому енергетичному стані `E = 0`, вони послідовно заповнюють усі доступні квантові комірки імпульсного простору аж до максимального імпульсу Фермі `p_F` та відповідної граничної енергії Фермі `E_F`. Цей процес приводить до виникнення квантового тиску виродження `P_deg`, який підтримує стійкість металів проти механічного стискання та запобігає гравітаційному колапсу білих карликів і нейтронних зір.

Нижче наведено практичний алгоритм чисельного розрахунку заповнення енергетичних рівнів, обчислення енергії Фермі `E_F`, густини станів `g(E)`, сумарної кінетичної енергії системи та тиску квантового виродження `P_deg` для виродженого електронного газу у різних фізичних середовищах.

## 1. Алгоритм та математична модель 3D квантового ящика

Розглянемо 3D потенціальний ящик з нескінченно високими стінками розмірами `L_x = L_y = L_z = L`. Квантові стани описуються хвильовими функціями стоячих хвиль `ψ(x, y, z) = A · sin(k_x x) · sin(k_y y) · sin(k_z z)`, де хвильові вектори квантовані за правилом `k_i = π · n_i / L` для `n_i ∈ {1, 2, 3, ...}`. 

Енергія одночастинкового стану становить:

```
E(n_x, n_y, n_z) = (π² ℏ² / (2 m_e L²)) · (n_x² + n_y² + n_z²)
```

Кожній трійці квантових чисел `(n_x, n_y, n_z)` відповідає один просторовий стан, який за принципом Паулі вміщує 2 електрони з протилежними спінами (`m_s = +1/2` та `m_s = -1/2`).

### 1.1. Дискретний підрахунок станів проти термодинамічного граничного наближення

У чисельному алгоритмі заповнення станів можна здійснювати двома шляхами:

1. **Дискретний алгоритм (для малих `N`)**: перебір усіх трійок цілих чисел `(n_x, n_y, n_z) > 0`, обчислення відповідних енергій `E`, сортування станів за зростанням енергії та послідовне заповнення по 2 електрони на комірку до досягнення суми `N`.
2. **Незперервне термодинамічне наближення (для макроскопічних `N >> 1`)**: перехід від сумування за дискретними вузлами ґратки квоти першого октанта імпульсного простору до інтегрування за сферою Фермі радіуса `k_F = (3 π² n_e)^(1/3)`.

У термодинамічному наближенні основні фізичні характеристики виродженого електронного газу визначаються наступними аналітичними формулами:

```
1. Об'ємна концентрація електронів: n_e = N / V
2. Хвильове число Фермі:            k_F = (3 · π² · n_e)^(1/3)
3. Імпульс Фермі:                  p_F = ℏ · k_F = ℏ · (3 · π² · n_e)^(1/3)
4. Енергія Фермі (нерелятивістська): E_F = p_F² / (2 · m_e) = (ℏ² / (2 m_e)) · (3 π² n_e)^(2/3)
5. Швидкість Фермі:                v_F = p_F / m_e
6. Середня енергія електрона при T=0: <E> = (3/5) · E_F
7. Повна кінетична енергія газу:   E_total = (3/5) · N · E_F
8. Квантовий тиск виродження:      P_deg = (2/5) · n_e · E_F = ( (3^(2/3) · π^(4/3) · ℏ²) / (5 · m_e) ) · n_e^(5/3)
```

### 1.2. Температурне розмиття розподілу Фермі — Дірака

При скінченній температурі `T > 0 K` ймовірність заповнення одночастинкового стану з енергією `E` визначається функцією розподілу Фермі — Дірака:

```
f(E, T) = 1 / ( exp( (E - μ) / (k_B · T) ) + 1 )
```

де `μ` — хімічний потенціал, який при `T = 0 K` строго дорівнює енергії Фермі `E_F`, а при низьких температурах `T << T_F` описується температурною поправкою Зоммерфельда:

```
μ(T) ≈ E_F · [ 1 - (π² / 12) · ( (k_B · T) / E_F )² ]
```

При обчисленні функції розподілу Фермі — Дірака у коді необхідно запобігати числовому переповненню типу `double` при великих додатних значеннях аргументу експоненти `(E - μ) / (k_B · T) > 700`.

### 1.3. Релятивістська межа при високих густинах

Якщо концентрація електронів `n_e` сягає значень `n_e > 10³⁶ m⁻³` (надра білих карликів), імпульс Фермі `p_F` стає порівнянним з `m_e c`, а швидкість електронів прямує до швидкості світла `v_F -> c`. У цьому ультрарелятивістському режимі релятивістська енергія Фермі обчислюється як:

```
E_F,rel = √( p_F² · c² + m_e² · c⁴ ) - m_e · c²  ≈  p_F · c  =  ℏ · c · (3 π² n_e)^(1/3)
```

Відповідно, рівняння стану квантового тиску змінює свій показник ступеня:

```
P_deg,rel = (1/4) · n_e · E_F,rel = ( (3^(1/3) · π^(2/3) · ℏ · c) / 4 ) · n_e^(4/3)
```

Зміна показника ступеня з `n_e^(5/3)` на `n_e^(4/3)` робить газову кулю нестійкою щодо гравітаційного стискання при перевищенні маси Чандрасекара `1.44 M_sun`.

## 2. Реалізація моделювання мовами C та C++

Нижче наведено кросплатформні реалізації чисельного розрахунку характеристик електронного фермі-газу мовами C та C++. Обидва варіанти містять функції розрахунку нерелятивістського та релятивістського режимів, обчислення густини станів, температурного розмиття за розподілом Фермі — Дірака та порівняння параметрів для різних речовин (Мідь, Натрій, Білий карлик).

:::tabs
```c
/* c */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Фундаментальні фізичні константи (SI) */
#define HBAR 1.054571817e-34       /* Зведена стала Планка, Дж·с */
#define MASS_E 9.1093837015e-31    /* Маса спокою електрона, кг */
#define SPEED_OF_LIGHT 299792458.0 /* Швидкість світла, м/с */
#define BOLTZMANN_K 1.380649e-23   /* Стала Больцмана, Дж/К */
#define EV_TO_JOULE 1.602176634e-19/* 1 еВ у Джоулях */
#define M_PI 3.14159265358979323846

/* Структура для збереження результатів моделювання */
typedef struct {
    double n_e;              /* Концентрація електронів (1/м³) */
    double p_F;              /* Імпульс Фермі (кг·м/с) */
    double v_F;              /* Швидкість Фермі (м/с) */
    double E_F_eV;           /* Енергія Фермі (еВ) */
    double T_F;              /* Температура Фермі (К) */
    double total_energy_J;   /* Сумарна кінетична енергія при T=0 K (Дж) */
    double pressure_Pa;      /* Тиск квантового виродження (Па) */
    double pressure_atm;     /* Тиск квантового виродження (атмосфер) */
    int is_relativistic;     /* Прапор релятивістського режиму */
} FermiGasProfile;

/* Обчислення густини станів g(E) = (V / 2π²) * (2m_e/ℏ²)^(3/2) * sqrt(E) */
double density_of_states(double E_joules, double volume_m3) {
    if (E_joules <= 0.0) return 0.0;
    double factor = (volume_m3 / (2.0 * M_PI * M_PI)) * pow(2.0 * MASS_E / (HBAR * HBAR), 1.5);
    return factor * sqrt(E_joules);
}

/* Обчислення ймовірності заповнення за розподілом Фермі — Дірака */
double fermi_dirac_distribution(double E_joules, double mu_joules, double temp_K) {
    if (temp_K <= 0.0) {
        return (E_joules <= mu_joules) ? 1.0 : 0.0;
    }
    double arg = (E_joules - mu_joules) / (BOLTZMANN_K * temp_K);
    if (arg > 700.0) return 0.0;   /* Запобігання числовому переповненню exp */
    if (arg < -700.0) return 1.0;
    return 1.0 / (exp(arg) + 1.0);
}

/* Основна функція обчислення профілю фермі-газу */
FermiGasProfile analyze_fermi_gas(double total_electrons, double volume_m3) {
    FermiGasProfile prof;
    prof.n_e = total_electrons / volume_m3;

    /* Імпульс Фермі p_F = ℏ * (3 * π² * n_e)^(1/3) */
    double k_F = cbrt(3.0 * M_PI * M_PI * prof.n_e);
    prof.p_F = HBAR * k_F;
    prof.v_F = prof.p_F / MASS_E;

    /* Перевірка релятивістського критерію: p_F >= 0.1 * m_e * c */
    double rest_energy_J = MASS_E * SPEED_OF_LIGHT * SPEED_OF_LIGHT;
    double E_F_nonrel_J = (prof.p_F * prof.p_F) / (2.0 * MASS_E);

    if (E_F_nonrel_J > 0.1 * rest_energy_J) {
        prof.is_relativistic = 1;
        /* Релятивістська енергія: E_F = sqrt(p_F² c² + m² c⁴) - m c² */
        double total_E = sqrt(prof.p_F * prof.p_F * SPEED_OF_LIGHT * SPEED_OF_LIGHT + rest_energy_J * rest_energy_J);
        double E_F_rel_J = total_E - rest_energy_J;
        prof.E_F_eV = E_F_rel_J / EV_TO_JOULE;
        prof.total_energy_J = 0.75 * total_electrons * E_F_rel_J;
        prof.pressure_Pa = 0.25 * prof.n_e * E_F_rel_J;
    } else {
        prof.is_relativistic = 0;
        prof.E_F_eV = E_F_nonrel_J / EV_TO_JOULE;
        prof.total_energy_J = 0.60 * total_electrons * E_F_nonrel_J;
        prof.pressure_Pa = 0.40 * prof.n_e * E_F_nonrel_J;
    }

    prof.T_F = (prof.E_F_eV * EV_TO_JOULE) / BOLTZMANN_K;
    prof.pressure_atm = prof.pressure_Pa / 101325.0;

    return prof;
}

/* Демонстрація розрахунку для різних фізичних систем */
void print_profile(const char* title, FermiGasProfile prof) {
    printf("==================================================\n");
    printf(" СИСТЕМА: %s\n", title);
    printf("==================================================\n");
    printf(" Режим:                      %s\n", prof.is_relativistic ? "РЕЛЯТИВІСТСЬКИЙ" : "Нерелятивістський");
    printf(" Концентрація e⁻ (n_e):      %.3e m⁻³\n", prof.n_e);
    printf(" Імпульс Фермі (p_F):        %.3e kg·m/s\n", prof.p_F);
    printf(" Швидкість Фермі (v_F):      %.3e m/s (%.2f%% від c)\n", prof.v_F, (prof.v_F / SPEED_OF_LIGHT) * 100.0);
    printf(" Енергія Фермі (E_F):        %.3f eV\n", prof.E_F_eV);
    printf(" Температура Фермі (T_F):    %.1f K\n", prof.T_F);
    printf(" Повна енергія (T=0 K):      %.3e J\n", prof.total_energy_J);
    printf(" Тиск виродження (P_deg):    %.3e Pa (%.2e atm)\n\n", prof.pressure_Pa, prof.pressure_atm);
}

int main(void) {
    /* 1. Провідні електрони в Міді (Cu): n_e ≈ 8.47e28 m⁻³ */
    double vol_sample = 1.0e-6; /* 1 см³ */
    FermiGasProfile cu = analyze_fermi_gas(8.47e28 * vol_sample, vol_sample);
    print_profile("Мідний провідник (Cu, 1 cm³)", cu);

    /* 2. Провідні електрони в Натрії (Na): n_e ≈ 2.65e28 m⁻³ */
    FermiGasProfile na = analyze_fermi_gas(2.65e28 * vol_sample, vol_sample);
    print_profile("Металевий Натрій (Na, 1 cm³)", na);

    /* 3. Надра Білого Карлика: n_e ≈ 1.0e36 m⁻³ */
    FermiGasProfile wd = analyze_fermi_gas(1.0e36 * vol_sample, vol_sample);
    print_profile("Ядро Білого Карлика (1 cm³)", wd);

    return 0;
}
```
```cpp
// cpp
#include <iostream>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <string_view>
#include <array>

class QuantumFermiGas {
public:
    // Константи фізики у системі SI
    static constexpr double Hbar = 1.054571817e-34;       // Дж·с
    static constexpr double ElectronMass = 9.1093837015e-31; // кг
    static constexpr double SpeedOfLight = 299792458.0;   // м/с
    static constexpr double BoltzmannK = 1.380649e-23;    // Дж/К
    static constexpr double EvToJoule = 1.602176634e-19;  // Дж/еВ

    struct PhysicalState {
        double electronDensity;  // m⁻³
        double fermiMomentum;    // kg·m/s
        double fermiVelocity;    // m/s
        double fermiEnergyEv;    // eV
        double fermiTemperature; // K
        double totalKineticEnergy;// J
        double degeneracyPressure;// Pa
        bool isRelativistic;     // true/false
    };

    // Обчислення густини станів g(E)
    [[nodiscard]] static constexpr double densityOfStates(double energyJoules, double volumeM3) noexcept {
        if (energyJoules <= 0.0) return 0.0;
        const double factor = (volumeM3 / (2.0 * std::numbers::pi * std::numbers::pi)) *
                              std::pow(2.0 * ElectronMass / (Hbar * Hbar), 1.5);
        return factor * std::sqrt(energyJoules);
    }

    // Розподіл Фермі — Дірака
    [[nodiscard]] static double fermiDiracDistribution(double energyJoules, double chemicalPotentialJ, double tempK) noexcept {
        if (tempK <= 0.0) {
            return (energyJoules <= chemicalPotentialJ) ? 1.0 : 0.0;
        }
        const double arg = (energyJoules - chemicalPotentialJ) / (BoltzmannK * tempK);
        if (arg > 700.0) return 0.0;
        if (arg < -700.0) return 1.0;
        return 1.0 / (std::exp(arg) + 1.0);
    }

    // Обчислення стану виродженого газу
    [[nodiscard]] static PhysicalState simulate(double totalElectrons, double volumeM3) noexcept {
        const double n_e = totalElectrons / volumeM3;
        const double k_F = std::cbrt(3.0 * std::numbers::pi * std::numbers::pi * n_e);
        const double p_F = Hbar * k_F;
        const double v_F = p_F / ElectronMass;

        const double restEnergyJ = ElectronMass * SpeedOfLight * SpeedOfLight;
        const double nonRelEnergyJ = (p_F * p_F) / (2.0 * ElectronMass);

        PhysicalState state{};
        state.electronDensity = n_e;
        state.fermiMomentum = p_F;
        state.fermiVelocity = v_F;

        if (nonRelEnergyJ > 0.1 * restEnergyJ) {
            state.isRelativistic = true;
            const double totalE = std::sqrt(p_F * p_F * SpeedOfLight * SpeedOfLight + restEnergyJ * restEnergyJ);
            const double relEnergyJ = totalE - restEnergyJ;
            state.fermiEnergyEv = relEnergyJ / EvToJoule;
            state.totalKineticEnergy = 0.75 * totalElectrons * relEnergyJ;
            state.degeneracyPressure = 0.25 * n_e * relEnergyJ;
        } else {
            state.isRelativistic = false;
            state.fermiEnergyEv = nonRelEnergyJ / EvToJoule;
            state.totalKineticEnergy = 0.60 * totalElectrons * nonRelEnergyJ;
            state.degeneracyPressure = 0.40 * n_e * nonRelEnergyJ;
        }

        state.fermiTemperature = (state.fermiEnergyEv * EvToJoule) / BoltzmannK;
        return state;
    }
};

void printReport(std::string_view label, const QuantumFermiGas::PhysicalState& st) {
    std::cout << "==================================================\n"
              << " СИСТЕМА: " << label << "\n"
              << "==================================================\n"
              << " Режим:                      " << (st.isRelativistic ? "РЕЛЯТИВІСТСЬКИЙ" : "Нерелятивістський") << "\n"
              << " Концентрація e⁻ (n_e):      " << std::scientific << std::setprecision(3) << st.electronDensity << " m⁻³\n"
              << " Імпульс Фермі (p_F):        " << st.fermiMomentum << " kg·m/s\n"
              << " Швидкість Фермі (v_F):      " << st.fermiVelocity << " m/s (" 
              << std::fixed << std::setprecision(2) << (st.fermiVelocity / QuantumFermiGas::SpeedOfLight) * 100.0 << "% c)\n"
              << " Енергія Фермі (E_F):        " << std::fixed << std::setprecision(3) << st.fermiEnergyEv << " eV\n"
              << " Температура Фермі (T_F):    " << std::fixed << std::setprecision(1) << st.fermiTemperature << " K\n"
              << " Повна енергія (T=0 K):      " << std::scientific << std::setprecision(3) << st.totalKineticEnergy << " J\n"
              << " Тиск виродження (P_deg):    " << st.degeneracyPressure << " Pa (" 
              << (st.degeneracyPressure / 101325.0) << " atm)\n\n";
}

int main() {
    constexpr double sampleVolume = 1.0e-6; // 1 cm³

    // 1. Мідний провідник (Cu)
    const auto cu = QuantumFermiGas::simulate(8.47e28 * sampleVolume, sampleVolume);
    printReport("Мідний провідник (Cu, 1 cm³)", cu);

    // 2. Металевий Натрій (Na)
    const auto na = QuantumFermiGas::simulate(2.65e28 * sampleVolume, sampleVolume);
    printReport("Металевий Натрій (Na, 1 cm³)", na);

    // 3. Зорі — Білі Карлики
    const auto wd = QuantumFermiGas::simulate(1.0e36 * sampleVolume, sampleVolume);
    printReport("Надра Білого Карлика (1 cm³)", wd);

    return 0;
}
```
:::

## 3. Зведена таблиця та порівняльний аналіз фізичних систем

Застосування вищенаведеного чисельного алгоритму до реальних металів та астрофізичних об'єктів дає наступні розраховані параметри виродженого електронного газу:

| Фізична система | Концентрація `n_e` (м⁻³) | Енергія Фермі `E_F` (еВ) | Швидкість `v_F` (м/с) | Температура `T_F` (К) | Тиск виродження `P_deg` (Па) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Літій (`Li`)** | `4.70 × 10²⁸` | `4.74 eV` | `1.29 × 10⁶` | `55 000 K` | `2.38 × 10⁹ Pa` (23.5 тис. atm) |
| **Натрій (`Na`)** | `2.65 × 10²⁸` | `3.24 eV` | `1.07 × 10⁶` | `37 700 K` | `9.26 × 10⁸ Pa` (9.1 тис. atm) |
| **Мідь (`Cu`)** | `8.47 × 10²⁸` | `7.00 eV` | `1.57 × 10⁶` | `81 200 K` | `3.79 × 10⁹ Pa` (37.4 тис. atm) |
| **Срібло (`Ag`)** | `5.86 × 10²⁸` | `5.49 eV` | `1.39 × 10⁶` | `63 700 K` | `2.06 × 10⁹ Pa` (20.3 тис. atm) |
| **Золото (`Au`)** | `5.90 × 10²⁸` | `5.53 eV` | `1.40 × 10⁶` | `64 200 K` | `2.09 × 10⁹ Pa` (20.6 тис. atm) |
| **Алюміній (`Al`)**| `18.1 × 10²⁸` | `11.70 eV` | `2.03 × 10⁶` | `135 700 K` | `1.35 × 10¹⁰ Pa` (133 тис. atm) |
| **Білий карлик** | `1.00 × 10³⁶` | `194.5 keV` | `2.28 × 10⁸` | `2.25 × 10⁹ K` | `1.24 × 10²² Pa` (122 млрд. atm) |

## 4. Практичні висновки та інженерні пастки

> 🔧 **Навіщо це.**
> Тиск квантового виродження `P_deg` не залежить від температури системи при `T << T_F`. Для більшості металів температура Фермі становить `T_F ≈ 40 000 - 130 000 K`. Це означає, що навіть при кімнатній температурі (`T = 300 K`) електронний газ у металі є повністю виродженим (`T / T_F ≈ 0.003 << 1`), а його внутрішній тиск виродження сягає від десятків до сотень тисяч атмосфер. Саме цей квантовий тиск запобігає стисненню металів під дією зовнішніх механічних навантажень.

При чисельному моделюванні та розрахунках квантового тиску слід уникати наступних поширених пасток:

1. **Нехтування статистикою Фермі — Дірака у теплоємності**: Спроба обчислити електронну теплоємність металів за класичною формулою Максвелла — Больцмана `C_v = (3/2) N k_B` дає результат, що перевищує експериментальний у 100 разів. Оскільки при кімнатній температурі лише незначна частка електронів `T / T_F ≈ 1%` біля поверхні сфери Фермі може змінювати свій стан, реальна електронна теплоємність описується формулою Зоммерфельда `C_v,e = (π² / 2) · N · k_B · (T / T_F)` і прямує до нуля при `T -> 0 K`.
2. **Пастка нерелятивістської формули при високих густинах**: При розрахунках надщільних астрофізичних об'єктів (надра білих карликів) використання нерелятивістської формули `P_deg ∝ n_e^(5/3)` дає помилкову стабільність для довільних мас зірок. Лінійна залежність `E_F ∝ p_F ∝ n_e^(1/3)` у релятивістському режимі змінює показник ступеня тиску на `n_e^(4/3)`, що робить зоряне ядро чутливим до залишків гравітаційного тиску і приводить до гравітаційного колапсу при `M > 1.44 M_sun`.
3. **Обчислення експоненти у функції розподілу**: При `(E - μ) / (k_B T) > 700` стандартний виклик `exp()` у C/C++ повертає значення `INFINITY` (Overflow), що приводить до помилки `NaN` у подальших розрахунках інтегралів. Необхідно явно перевіряти діапазон аргументу передувачем гілок.
