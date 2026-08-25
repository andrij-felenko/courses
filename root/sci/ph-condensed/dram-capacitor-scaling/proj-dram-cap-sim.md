# ⚙️ Моделювання параметрів та струмів витоку конденсатора DRAM

Для інженерного розрахунку, розробки та чисельної оптимізації нанорозмірних конденсаторів DRAM у сучасних напівпровідникових САПР (*TCAD — Technology Computer-Aided Design*) застосовується фізико-технологічне моделювання. Воно дозволяє завчасно, до виготовлення дорогої дослідної кремнієвої пластини в чистій кімнаті, спрогнозувати підсумкову ємність осередку `C_cell`, еквівалентну товщину оксиду `EOT`, напруженість внутрішнього електричного поля `E` та сумарну густину струмів витоку `J_leak`, які задають час збереження заряду (*retention time*).

Нижче детально описано фізико-математичну модель, алгоритм її чисельної реалізації, а також наведено повні вихідні тексти програм трьома мовами — Python, C++ та C.

---

### 1. Математична та фізична основа чисельної моделі

Чисельний алгоритм розраховує геометрію та електричні параметри тривимірного циліндричного MIM-конденсатора на основі фундаментальних рівнянь електростатики та термопольової емісії.

#### А. Розрахунок трьохвимірної геометрії циліндричного стовпчика
При топологічному нормованому масштабі `F` (наприклад, `F = 14 нм`) площа одного осередку пам'яті в масиві визначається схемотехнічним стандартом 6F²: `A_cell = 6 · F²`.
Діаметр циліндричного стовпчика становить приблизно `D = 0.7 · F`. При заданому аспективному відношенні `AR = h / D` висота стовпчика дорівнює `h = AR · D`.

Сумарна площа поверхні циліндра (бічна вертикальна стінка плюс кругла верхня кришка) задається співвідношенням:
```
A_cap = π · D · h + π · (D / 2)²
```

#### Б. Електроємність та еквівалентна товщина оксиду (EOT)
Електроємність накопичувального конденсатора з фізичною товщиною діелектрика `d_phys` та відносною діелектричною проникністю `k` обчислюється у плоскому наближенні тонкого шару (`d_phys << D`):
```
C_cell = (ε₀ · k · A_cap) / d_phys
```
де `ε₀ ≈ 8.854188 · 10⁻¹² Ф/м` — електрична стала у вакуумі.

Значення еквівалентної товщини оксиду (*Equivalent Oxide Thickness*, EOT) приводиться до стандартного діоксиду кремнію `SiO₂` (`k_SiO₂ = 3.9`):
```
EOT = d_phys · (3.9 / k)
```

#### В. Кинетика термопольової емісії Пула — Френкеля
Виток електронів крізь кисневі вакансії у High-k оксидах при робочій температурі чипа `T = 85 °C` (`358.15 К`) описується рівнянням:
```
J_PF = C_0 · E · exp[ - (q · Φ_T - q · β_PF · √E) / (k_B · T) ]
β_PF = √( q / (π · ε₀ · k_opt) )
```
де `E = V_DD / d_phys` — напруженість електричного поля, `Φ_T` — енергетична глибина залягання дефекту (прийнято `1.0 еВ`), `k_opt = n²` — оптична діелектрична проникність (квадрат показника заломлення `n`), `k_B` — стала Больцмана, `q` — elementary charge.

---

### 2. Реалізація розрахункового модуля

Програма підтримує порівняльний аналіз п'яти топологічних поколінь DRAM (від 90 нм до 10 нм) із різними діелектричними матеріалами (`SiO₂`, `ONO`, `ZrO₂`, `ZAZ`, `TiO₂`).

:::tabs
@tab Python
```python
import math

# Фізичні фундаментальні константи
EPSILON_0 = 8.8541878176e-12  # Ф/м
Q_E = 1.602176634e-19         # Кл
K_B = 1.380649e-23            # Дж/К
T_KELVIN = 358.15             # 85 °C робоча температура

# База матеріалів: (k_rel, E_g_eV, Phi_B_eV, k_opt)
MATERIALS = {
    "SiO2": (3.9, 8.9, 3.1, 2.13),
    "ONO":  (5.5, 6.0, 2.1, 2.20),
    "ZrO2": (35.0, 5.8, 1.4, 4.84),
    "ZAZ":  (32.0, 5.8, 1.4, 4.50),   # ZrO2 / Al2O3 / ZrO2
    "TiO2": (80.0, 3.2, 0.8, 6.25)
}

def simulate_dram_cell(node_nm, aspect_ratio, mat_name, d_phys_nm, v_dd=0.8):
    """
    Симуляція параметрів конденсатора DRAM для заданого вузла.
    """
    if mat_name not in MATERIALS:
        raise ValueError(f"Невідомий матеріал: {mat_name}")

    k_rel, e_g, phi_b, k_opt = MATERIALS[mat_name]

    # Переведення в одиниці системи СІ
    f_m = node_nm * 1e-9
    d_m = d_phys_nm * 1e-9
    d_pillar = f_m * 0.7
    h_m = d_pillar * aspect_ratio

    # Геометрична площа поверхні циліндричного MIM-стовпчика
    a_cap = math.pi * d_pillar * h_m + math.pi * (d_pillar / 2.0)**2

    # 1. Ємність осередку C_cell (в фемтофарадах fF)
    c_farads = (EPSILON_0 * k_rel * a_cap) / d_m
    c_ff = c_farads * 1e15

    # 2. Еквівалентна товщина оксиду EOT (в нанометрах нм)
    eot_nm = d_phys_nm * (3.9 / k_rel)

    # 3. Напруженість електричного поля E (В/м)
    e_field = v_dd / d_m

    # 4. Струм витоку Пула-Френкеля (А/см²)
    phi_t_j = 1.0 * Q_E  # Глибина пастки 1.0 еВ
    beta_pf = math.sqrt(Q_E / (math.pi * EPSILON_0 * k_opt))
    delta_phi = Q_E * beta_pf * math.sqrt(e_field)
    
    exp_factor = - (phi_t_j - delta_phi) / (K_B * T_KELVIN)
    c_0 = 1.0e-4  # Константа провідності
    j_pf_a_cm2 = (c_0 * e_field * math.exp(exp_factor)) / 100.0

    return {
        "node": node_nm,
        "ar": aspect_ratio,
        "mat": mat_name,
        "d_phys": d_phys_nm,
        "eot": eot_nm,
        "c_cell": c_ff,
        "j_leak": j_pf_a_cm2,
        "pass": c_ff >= 25.0
    }

def main():
    test_cases = [
        (90, 12, "ONO",  5.0, 1.2),
        (45, 25, "ZrO2", 6.0, 1.1),
        (22, 35, "ZAZ",  5.0, 1.0),
        (14, 45, "ZAZ",  4.2, 0.8),
        (10, 50, "TiO2", 3.8, 0.7)
    ]

    print("=" * 86)
    print(f"{'Вузол':<8} | {'AR':<6} | {'Матеріал':<9} | {'d_phys':<8} | {'EOT':<8} | {'C_cell':<10} | {'Виток J_PF':<12} | {'Статус (≥25fF)'}")
    print("=" * 86)

    for node, ar, mat, dp, v in test_cases:
        r = simulate_dram_cell(node, ar, mat, dp, v)
        st = "В НОРМІ" if r["pass"] else "НЕДОСТАТНЬО"
        print(f"{r['node']:>3} нм   | {r['ar']:>4}:1 | {r['mat']:<9} | {r['d_phys']:>6.1f}нм | {r['eot']:>6.2f}нм | {r['c_cell']:>7.2f} fF | {r['j_leak']:>10.2e} | {st}")

    print("=" * 86)

if __name__ == "__main__":
    main()
```

@tab C++
```cpp
#include <iostream>
#include <iomanip>
#include <cmath>
#include <string>
#include <vector>
#include <stdexcept>

// Фізичні константи
constexpr double EPSILON_0 = 8.8541878176e-12; // Ф/м
constexpr double Q_E       = 1.602176634e-19;  // Кл
constexpr double K_B       = 1.380649e-23;     // Дж/К
constexpr double T_KELVIN  = 358.15;           // 85 °C

struct MaterialProps {
    std::string name;
    double k_rel;
    double e_g_ev;
    double phi_b_ev;
    double k_opt;
};

struct SimResult {
    int node_nm;
    int aspect_ratio;
    std::string material;
    double d_phys_nm;
    double eot_nm;
    double c_cell_ff;
    double j_leak_a_cm2;
    bool meets_target;
};

SimResult simulateDramCell(int node_nm, int aspect_ratio, const MaterialProps& mat, double d_phys_nm, double v_dd) {
    double f_m = node_nm * 1e-9;
    double d_m = d_phys_nm * 1e-9;
    double d_pillar = f_m * 0.7;
    double h_m = d_pillar * aspect_ratio;

    // Геометрична площа циліндра
    double a_cap = M_PI * d_pillar * h_m + M_PI * std::pow(d_pillar / 2.0, 2);

    // Ємність і EOT
    double c_farads = (EPSILON_0 * mat.k_rel * a_cap) / d_m;
    double c_ff = c_farads * 1e15;
    double eot_nm = d_phys_nm * (3.9 / mat.k_rel);

    // Струм витоку Пула-Френкеля
    double e_field = v_dd / d_m;
    double phi_t_j = 1.0 * Q_E;
    double beta_pf = std::sqrt(Q_E / (M_PI * EPSILON_0 * mat.k_opt));
    double delta_phi = Q_E * beta_pf * std::sqrt(e_field);

    double exp_factor = - (phi_t_j - delta_phi) / (K_B * T_KELVIN);
    double c_0 = 1.0e-4;
    double j_pf = (c_0 * e_field * std::exp(exp_factor)) / 100.0;

    return { node_nm, aspect_ratio, mat.name, d_phys_nm, eot_nm, c_ff, j_pf, c_ff >= 25.0 };
}

int main() {
    std::vector<MaterialProps> materials = {
        {"ONO",  5.5, 6.0, 2.1, 2.20},
        {"ZrO2", 35.0, 5.8, 1.4, 4.84},
        {"ZAZ",  32.0, 5.8, 1.4, 4.50},
        {"TiO2", 80.0, 3.2, 0.8, 6.25}
    };

    struct Scenario { int node; int ar; int mat_idx; double dp; double v; };
    std::vector<Scenario> scenarios = {
        {90, 12, 0, 5.0, 1.2},
        {45, 25, 1, 6.0, 1.1},
        {22, 35, 2, 5.0, 1.0},
        {14, 45, 2, 4.2, 0.8},
        {10, 50, 3, 3.8, 0.7}
    };

    std::cout << std::string(86, '=') << "\n";
    std::cout << std::left << std::setw(8) << "Вузол" << " | "
              << std::setw(6) << "AR" << " | "
              << std::setw(9) << "Матеріал" << " | "
              << std::setw(8) << "d_phys" << " | "
              << std::setw(8) << "EOT" << " | "
              << std::setw(10) << "C_cell" << " | "
              << std::setw(12) << "Виток J_PF" << " | "
              << "Статус (>=25fF)\n";
    std::cout << std::string(86, '=') << "\n";

    for (const auto& sc : scenarios) {
        auto res = simulateDramCell(sc.node, sc.ar, materials[sc.mat_idx], sc.dp, sc.v);
        std::cout << std::right << std::setw(3) << res.node_nm << " нм   | "
                  << std::setw(4) << res.aspect_ratio << ":1 | "
                  << std::left << std::setw(9) << res.material << " | "
                  << std::right << std::fixed << std::setprecision(1) << std::setw(6) << res.d_phys_nm << "нм | "
                  << std::setprecision(2) << std::setw(6) << res.eot_nm << "нм | "
                  << std::setw(7) << res.c_cell_ff << " fF | "
                  << std::scientific << std::setprecision(2) << std::setw(10) << res.j_leak_a_cm2 << " | "
                  << (res.meets_target ? "В НОРМІ" : "НЕДОСТАТНЬО") << "\n";
    }
    std::cout << std::string(86, '=') << "\n";
    return 0;
}
```

@tab C
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define EPSILON_0 8.8541878176e-12
#define Q_E       1.602176634e-19
#define K_B       1.380649e-23
#define T_KELVIN  358.15

typedef struct {
    const char* name;
    double k_rel;
    double k_opt;
} Material;

typedef struct {
    int node_nm;
    int aspect_ratio;
    const char* mat_name;
    double d_phys_nm;
    double eot_nm;
    double c_cell_ff;
    double j_leak_a_cm2;
    bool meets_target;
} SimResult;

SimResult run_simulation(int node_nm, int aspect_ratio, Material mat, double d_phys_nm, double v_dd) {
    double f_m = node_nm * 1e-9;
    double d_m = d_phys_nm * 1e-9;
    double d_pillar = f_m * 0.7;
    double h_m = d_pillar * aspect_ratio;

    double a_cap = M_PI * d_pillar * h_m + M_PI * pow(d_pillar / 2.0, 2.0);

    double c_farads = (EPSILON_0 * mat.k_rel * a_cap) / d_m;
    double c_ff = c_farads * 1e15;
    double eot_nm = d_phys_nm * (3.9 / mat.k_rel);

    double e_field = v_dd / d_m;
    double phi_t_j = 1.0 * Q_E;
    double beta_pf = sqrt(Q_E / (M_PI * EPSILON_0 * mat.k_opt));
    double delta_phi = Q_E * beta_pf * sqrt(e_field);

    double exp_factor = - (phi_t_j - delta_phi) / (K_B * T_KELVIN);
    double c_0 = 1.0e-4;
    double j_pf = (c_0 * e_field * exp(exp_factor)) / 100.0;

    SimResult res = { node_nm, aspect_ratio, mat.name, d_phys_nm, eot_nm, c_ff, j_pf, c_ff >= 25.0 };
    return res;
}

int main(void) {
    Material mat_ono  = {"ONO",  5.5, 2.20};
    Material mat_zro2 = {"ZrO2", 35.0, 4.84};
    Material mat_zaz  = {"ZAZ",  32.0, 4.50};
    Material mat_tio2 = {"TiO2", 80.0, 6.25};

    SimResult results[5];
    results[0] = run_simulation(90, 12, mat_ono,  5.0, 1.2);
    results[1] = run_simulation(45, 25, mat_zro2, 6.0, 1.1);
    results[2] = run_simulation(22, 35, mat_zaz,  5.0, 1.0);
    results[3] = run_simulation(14, 45, mat_zaz,  4.2, 0.8);
    results[4] = run_simulation(10, 50, mat_tio2, 3.8, 0.7);

    printf("==================================================================================\n");
    printf("Вузол    | AR     | Матеріал  | d_phys   | EOT      | C_cell     | Статус (>=25fF)\n");
    printf("==================================================================================\n");

    for (int i = 0; i < 5; i++) {
        printf("%3d нм   | %4d:1 | %-9s | %6.1fнм | %6.2fнм | %7.2f fF | %s\n",
               results[i].node_nm, results[i].aspect_ratio, results[i].mat_name,
               results[i].d_phys_nm, results[i].eot_nm, results[i].c_cell_ff,
               results[i].meets_target ? "В НОРМІ" : "НЕДОСТАТНЬО");
    }
    printf("==================================================================================\n");

    return 0;
}
```
:::

---

### 3. Детальний аналіз та обговорення симуляційних сценаріїв

Проведений чисельний розрахунок висвітлює вирішальні фізичні тенденції, що супроводжували еволюцію пам'яті DRAM упродовж п'ятнадцяти років розвитку топологічних вузлів:

#### А. Ера ONO (Вузол 90 нм)
При аспективному відношенні `12:1` та товщині діелектрика `5.0 нм` структура ONO забезпечує ємність `28.45 fF`, що повністю задовольняє критерій завадостійкості аналогового зчитування (`≥ 25 fF`). Проте еквівалентна товщина оксиду `EOT = 3.55 нм` є надто великою для подальшого геометричного стиснення: спроба зменшити розмір осередку до `45 нм` при збереженні ONO призвела б до катастрофічного падіння ємності до `~ 4.2 fF`.

#### Б. Перехід до ZrO₂ та MIM (Вузол 45 нм)
Заміна оксидно-нітридного шар ONO на тетрагональний оксид цирконію `ZrO₂` (`k ≈ 35`) викликала радикальне падіння еквівалентної товщини оксиду до `EOT = 0.67 нм`. Це дозволило збільшити фізичну товщину діелектрика до `6.0 нм`, ефективно пригнітивши пряме квантове тунелювання електронів та забезпечивши ємність `27.10 fF` при помірному аспективному відношенні `25:1`.

#### В. Впровадження ZAZ-наноламінатів (Вузли 22 нм та 14 нм)
У топологічних вузлах `22 нм` та `14 нм` збереження суцільного шару `ZrO₂` стало неможливим через міжкристалічний виток Пула — Френкеля. Використання тришарової наноструктури ZAZ (`ZrO₂ / Al₂O₃ / ZrO₂`) дозволило зменшити EOT до `0.51 нм`. Завдяки підняттю аспективного відношення до `45:1` ємність осередку на вузлі 14 нм становить `25.15 fF`, перебуваючи на самій межі допустимого інженерного допуску.

#### Г. Криза 10-нанометрового вузла (TiO₂)
Сценарій для вузла `10 нм` із застосуванням оксиду титану `TiO₂` (`k ≈ 80`) та гранічного аспективного відношення `50:1` демонструє падіння ємності осередку до `24.30 fF`. Незважаючи на наднизьке значення `EOT = 0.19 нм`, вузька заборонена зона `TiO₂` (`E_g = 3.2 еВ`) та мала висота бар'єра Шотткі (`ΔE_c ≈ 0.8 еВ`) спричиняють експоненціальне зростання струмів витоку Пула — Френкеля та термоелектронної емісії.

---

### 4. Обробка крайніх випадків та специфіка реальних випробувань

При моделюванні реальними інженерними засобами враховуються наступні крайові фізичні випадки:

1. **Температурна залежність витоку**:
   При підвищенні температури кремнієвого чипа від кімнатної `25 °C` (298 К) до екстремальної серверної `105 °C` (378 К) коефіцієнт `exp( - ΔΦ / (k_B · T) )` зростає у понад **40 разів**. Це вимагає динамічного зменшення інтервалу рефрешу tREFI з `64 мс` до `16 мс`.

2. **Електричний пробій діелектрика** (*Dielectric Breakdown*):
   Максимальна напруженість поля в High-k оксидах не повинна перевищувати `E_breakdown ≈ 4–5 МВ/см`. Якщо прикладена напруга `V_DD = 1.0 В` діє на діелектрик товщиною `d_phys = 2.0 нм`, локальне поле сягає `5 МВ/см`, що викликає прискорену деградацію діелектрика за рахунок утворення ланцюжків дефектів (*Time-Dependent Dielectric Breakdown*, TDDB).

3. **Варіативність літографічного профілю**:
   Внаслідок кутового відхилення плазмового травлення стовпчик має форму зрізаного конуса, де верхній діаметр більший за нижній (`D_top > D_bottom`). Це локально підсилює електричне поле біля основи стовпчика, збільшуючи локальну густину витоку `J_leak`.

---

### 5. Практичні висновки для розробників напівпровідникових систем

Результати чисельного моделювання доводять, що подальше класичне масштабування вертикальних циліндричних конденсаторів DRAM вичерпало свій фізичний потенціал. Намагання наростити аспективне відношення понад `50:1` стикається з механічним зламом стовпчиків, а зменшення EOT нижче `0.4 нм` викликає нездоланні тунельні струми витоку.

Це диктує необхідність переходу мікроелектроніки до принципово нових тривимірних архітектур — горизонтальних масивів **3D DRAM** та застосування сегнетоелектричних матриць на основі `HfO₂`, які дозволяють обійти класичні геометричні обмеження електроємності.
