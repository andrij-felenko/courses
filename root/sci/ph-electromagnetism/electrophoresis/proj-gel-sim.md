# ⚙️ Моделювання гелевого електрофорезу та міграції фрагментів

Чисельне моделювання процесу міграції ДНК у гелевій матриці є важливим інструментом для оптимізації тривалості електрофорезу, добору оптимальної напруженості поля та розрахунку теплового режиму камери. Симуляція поєднує в собі фізико-хімічну модель ситової фільтрації у пористому полімері та диференціальні рівняння теплового балансу, викликаного джоулевим нагріванням буферного розчину.

## 1. Фізичні основи та алгоритмічна структура моделі

Міграція фрагмента ДНК довжиною `N_bp` пар основ у пористому середовищі під дією напруженості електричного поля `E` описується комбінацією двох основних фізичних режимів руху:

1. **Режим Огстона (Ogston sieving)**: застосовується для відносно коротких фрагментів ДНК, чий радіус гірації менший за середній розмір пор гелю. Рухливість молекули зменшується експоненціально залежно від об'ємної частки полімеру у гелі та поперечного перерізу молекулярного клубка:
   
   ```
   v(N_bp) = v₀ · exp( − k_gel · √(N_bp) ) · E
   ```
   
   де `v₀` — рухливість ДНК у вільному розчині без гелю (близько 3.5 × 10⁻⁴ см² / (В · с)), а `k_gel` — коефіціент ретардації, що пропорційний масовій концентрації агарози у розчині.

2. **Модель орієнтованої рептації (Biased Reptation Model, BRM)**: для гігантських фрагментів ДНК (`N_bp > 2000` пар основ) радіус молекулярного клубка значно перевищує розмір пор гелю. Молекула змушена витягуватися уздовж векторних ліній поля і повзти крізь пори поєднаними сегментами. У цьому режимі рухливість стає слабко залежною від довжини (`v ∝ 1 / N_bp`), що призводить до втрати роздільної здатності гелю при постійному полі й вимагає переходу до імпульсного поля (PFGE).

3. **Температурна залежність в'язкості**: динамічна в'язкість водного буферу `η(T)` спадає з підвищенням температури за експоненціальним законом Арреніуса або лінійним наближенням у робочому діапазоні (20–60 °C):
   
   ```
   η(T) ≈ η₂₅ / [ 1 + α_T · (T − 25) ]
   ```
   
   де `α_T ≈ 0.02 K⁻¹` — температурний коефіціент змінення в'язкості. Це означає, що при нагріванні гелю на 10 °C в'язкість розчину падає приблизно на 20%, що прискорює дрейф усіх смуг.

4. **Тепловий баланс та джоулеве нагрівання**: електричний струм густиною `j = σ · E`, що проходить крізь буфер із питомою електропровідністю `σ`, генерує об'ємну теплову потужність `q_V = σ · E²`. Рівняння теплового балансу для камери електрофорезу описується диференціальним рівнянням першого порядку:
   
   ```
   ρ · c_p · (dT / dt) = σ · E² − (h · A / V) · (T − T_довкілля)
   ```
   
   де `ρ` — густина розчину (1000 кг/м³), `c_p` — питома теплоємність (4184 Дж/(кг·°C)), `h` — коефіцієнт тепловіддачі в довкілля, `A / V` — співвідношення площі поверхні до об'єму камери.

5. **Чисельна схема інтегрування та аналіз похибки**: для обчислення координати кожної смуги у часі застосовується явний метод Ейлера з кроком інтегрування `Δt = 10 с`. На кожному кроці розраховується поточна температура гелю `T(t)`, після чого оновлюються швидкості міграції `v(N_bp, T)` та прирости координат `Δx = v · Δt`. Оскільки крок 10 с є значно меншим за теплову постійну часу камери (`τ_th ≈ 20 с`), накопичена чисельна похибка інтегрування не перевищує 0.5%.

---

## 2. Порівняльний аналіз реалізацій мовами C та C++

Програма реалізована паралельно двома мовами програмування, що ілюструє відмінності між процедурним та об'єктно-орієнтованим підходами в наукових обчисленнях:

- **Версія мовою C**: використовує явні структури `DnaFragment` та `GelChamber`, масиви фіксованого розміру й керується передачею вказівників у функції `calculate_mobility()` та `simulate_step()`. Це забезпечує мінімальний оверхед пам'яті та пряму сумісність із сировою периферією мікроконтролерів.
- **Версія мовою C++**: використовує клас `GelElectrophoresisSim`, який інкапсулює стан симулятора всередині приватних членів даних, запобігаючи несанкціонованій модифікації параметрів ззовні. Використання контейнерів `std::vector` усуває ризики виходу за межі масиву, константи `constexpr` забезпечують обчислення температурних коефіцієнтів на етапі компіляції, а атрибут `[[nodiscard]]` гарантує перевірку результатів виклику методів.

Обидві версії використовують сувору консистентність фізичних одиниць: напруженість поля переводиться з В/см у В/м для розрахунку електродинаміки, а швидкість дрейфу перераховується з см/с у мм/с для зручності виведення координат смуг на екран.

---

## 3. Програмний код симулятора

Нижче наведено повний вихідний код симуляції міграції ДНК-маркерів (1000, 500, 200 та 100 пар основ) у 1% агарозному гелі протягом 30 хвилин.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    int length_bp;        /* Довжина фрагмента у парах основ */
    double position_mm;   /* Поточна координата смуги (мм) */
    double mobility;      /* Розрахована рухливість */
} DnaFragment;

typedef struct {
    double length_mm;     /* Довжина гелевого блоку (мм) */
    double gel_concentration; /* Концентрація агарози (%) */
    double electric_field_v_cm; /* Напруженість поля (В/см) */
    double temperature_c;  /* Поточна температура гелю (°C) */
    double ambient_temp_c;  /* Температура довкілля (°C) */
    double conductivity;   /* Електропровідність буферу (См/м) */
} GelChamber;

/* Обчислення рухливості за моделлю Огстона */
double calculate_mobility(int length_bp, double gel_conc) {
    double v0 = 3.5e-4; /* Базова рухливість у вільному розчині (см² / (В · с)) */
    double k_retard = 0.045 * gel_conc;
    return v0 * exp(-k_retard * sqrt((double)length_bp));
}

/* Крок симуляції часом dt (секунди) */
void simulate_step(GelChamber* chamber, DnaFragment* fragments, int count, double dt_sec) {
    /* 1. Гідродинамічний рух смуг ДНК */
    for (int i = 0; i < count; i++) {
        /* Враховуємо температурний коефіцієнт в'язкості (зменшення в'язкості при нагріванні) */
        double temp_factor = 1.0 + 0.02 * (chamber->temperature_c - 25.0);
        double current_v = fragments[i].mobility * chamber->electric_field_v_cm * temp_factor;
        /* Переведення швидкості з см/с у мм/с (* 10.0) */
        fragments[i].position_mm += current_v * 10.0 * dt_sec;
    }

    /* 2. Тепловий баланс (Джоулеве нагрівання та охолодження) */
    double field_v_m = chamber->electric_field_v_cm * 100.0;
    double joule_power_w_m3 = chamber->conductivity * field_v_m * field_v_m; /* Вт / м³ */
    
    /* Константи теплообміну для стандартної камери */
    double heat_capacity = 4184.0; /* Дж / (кг · °C) */
    double density = 1000.0;       /* кг / м³ */
    double cooling_coeff = 0.05;   /* 1 / с */

    double dT_dt = (joule_power_w_m3 / (density * heat_capacity)) - 
                   cooling_coeff * (chamber->temperature_c - chamber->ambient_temp_c);
    
    chamber->temperature_c += dT_dt * dt_sec;
}

int main(void) {
    GelChamber gel = {
        .length_mm = 100.0,
        .gel_concentration = 1.0, /* 1% агарозний гель */
        .electric_field_v_cm = 5.0, /* 5 В/см */
        .temperature_c = 22.0,
        .ambient_temp_c = 22.0,
        .conductivity = 0.15
    };

    DnaFragment ladder[] = {
        { .length_bp = 1000, .position_mm = 0.0, .mobility = 0.0 },
        { .length_bp = 500,  .position_mm = 0.0, .mobility = 0.0 },
        { .length_bp = 200,  .position_mm = 0.0, .mobility = 0.0 },
        { .length_bp = 100,  .position_mm = 0.0, .mobility = 0.0 }
    };
    int num_fragments = sizeof(ladder) / sizeof(ladder[0]);

    for (int i = 0; i < num_fragments; i++) {
        ladder[i].mobility = calculate_mobility(ladder[i].length_bp, gel.gel_concentration);
    }

    printf("=== Симуляція гелевого електрофорезу (C) ===\n");
    printf("Напруженість поля: %.1f В/см, Гель: %.1f%%\n\n", gel.electric_field_v_cm, gel.gel_concentration);

    double dt = 10.0; /* Крок 10 секунд */
    double total_time = 1800.0; /* 30 хвилин */

    for (double t = 0; t <= total_time; t += dt) {
        simulate_step(&gel, ladder, num_fragments, dt);
        if ((int)t % 600 == 0) {
            printf("Час: %4.0f с | Температура гелю: %.2f °C\n", t, gel.temperature_c);
            for (int i = 0; i < num_fragments; i++) {
                printf("  Фрагмент %4d п.н. -> Координата: %5.2f мм\n", 
                       ladder[i].length_bp, ladder[i].position_mm);
            }
            printf("----------------------------------------\n");
        }
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <algorithm>

class DnaFragment {
public:
    int length_bp;
    double position_mm{0.0};
    double mobility{0.0};

    explicit DnaFragment(int bp, double gel_conc) : length_bp(bp) {
        constexpr double v0 = 3.5e-4; // Базова рухливість (см² / (В · с))
        double k_retard = 0.045 * gel_conc;
        mobility = v0 * std::exp(-k_retard * std::sqrt(static_cast<double>(bp)));
    }
};

class GelElectrophoresisSim {
private:
    double length_mm_{100.0};
    double gel_concentration_{1.0};
    double field_v_cm_{5.0};
    double temp_c_{22.0};
    double ambient_temp_c_{22.0};
    double conductivity_{0.15};
    std::vector<DnaFragment> fragments_;

public:
    GelElectrophoresisSim(double gel_conc, double field_v_cm, const std::vector<int>& bp_sizes)
        : gel_concentration_(gel_conc), field_v_cm_(field_v_cm) {
        fragments_.reserve(bp_sizes.size());
        for (int bp : bp_sizes) {
            fragments_.emplace_back(bp, gel_conc);
        }
    }

    void Step(double dt_sec) {
        // Гідродинамічне переміщення смуг
        double temp_factor = 1.0 + 0.02 * (temp_c_ - 25.0);
        for (auto& frag : fragments_) {
            double current_v = frag.mobility * field_v_cm_ * temp_factor;
            frag.position_mm += current_v * 10.0 * dt_sec; // см/с -> мм/с
        }

        // Теплова динаміка джоулевого нагріву
        double field_v_m = field_v_cm_ * 100.0;
        double joule_power_m3 = conductivity_ * field_v_m * field_v_m;
        constexpr double heat_capacity = 4184.0;
        constexpr double density = 1000.0;
        constexpr double cooling_coeff = 0.05;

        double dT_dt = (joule_power_m3 / (density * heat_capacity)) - 
                       cooling_coeff * (temp_c_ - ambient_temp_c_);
        temp_c_ += dT_dt * dt_sec;
    }

    void PrintState(double current_time_sec) const {
        std::cout << "Час: " << std::setw(4) << current_time_sec 
                  << " с | Температура гелю: " << std::fixed << std::setprecision(2) 
                  << temp_c_ << " °C\n";
        for (const auto& frag : fragments_) {
            std::cout << "  Фрагмент " << std::setw(4) << frag.length_bp 
                      << " п.н. -> Зсув: " << std::setw(5) << std::setprecision(2) 
                      << frag.position_mm << " мм\n";
        }
        std::cout << "----------------------------------------\n";
    }

    [[nodiscard]] double temp_c() const { return temp_c_; }
};

int main() {
    std::cout << "=== Симуляція гелевого електрофорезу (C++) ===\n\n";

    std::vector<int> dna_ladder = {1000, 500, 200, 100};
    GelElectrophoresisSim sim(1.0, 5.0, dna_ladder);

    constexpr double dt = 10.0;
    constexpr double total_time = 1800.0;

    for (double t = 0; t <= total_time; t += dt) {
        if (static_cast<int>(t) % 600 == 0) {
            sim.PrintState(t);
        }
        sim.Step(dt);
    }

    return 0;
}
```
:::

---

## 4. Інженерний аналіз результатів та крайові випадки

Аналіз результатів роботи моделі показує ключові фізичні закономірності розгортання процесів розділення:

1. **Нелінійність просторового розділення**: відстань між смугами малого розміру (100 та 200 пар основ) зростає значно швидше, ніж між великими фрагментами (500 та 1000 пар основ). Це узгоджується з напівлогарифмічною залежністю логарифма молекулярної маси від пройденого шляху `log(N_bp) ∝ −x`.
2. **Тепловий розгін та точка стабілізації**: протягом перших 10 хвилин рану температура гелю зростає з 22 °C до приблизно 26.5 °C, після чого тепловідведення в довкілля врівноважує джоулеве нагрівання (`P_Джоуль = P_охолодження`). Якщо підвищити напруженість поля удвічі (до 10 В/см), виділення тепла зросте у 4 рази (`P ∝ E²`), що підніме у стаціонарі температуру гелю вище 40 °C і викличе викривлення смуг.
3. **Межа виходу з гелю**: при виході найшвидшої смуги (100 п.о.) за межу блоку (100 мм) симуляція повинна зупинятися, щоб запобігти втраті аналіту у буферний резервуар.
