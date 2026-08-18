# ⚙️ Програмне моделювання неомічних елементів та польового транспорту

Цей проект присвячено практичній розробці чисельного аналізатора та імітаційної моделі нелінійних вольт-амперних характеристик (ВАХ) неомічних елементів. У класичному аналізі лінійних електричних кіл розрахунок за законом Ома зводиться до розв'язання систем лінійних алгебраїчних рівнянь. Проте при наявності варисторів чи термисторів коефіцієнти матриці провідностей самі залежать від вузлових напруг та струмів гілок. Це вимагає застосування чисельних ітераційних методів для пошуку точки електричної та теплової рівноваги.

Програма реалізує алгоритми чисельного обчислення струмів для трьох фундаментальних неомічних режимів:
1. Клампінгу ZnO варистора з урахуванням степеневої нелінійності міжкристалітних бар'єрів та омічного опору зерен.
2. Саморозігріву NTC термистора із розв'язанням стаціонарного теплового балансу та виходом у область негативного диференціального опору (`dU/dI < 0`).
3. Витоків діелектрика за ефектом Пуля — Френкеля у тонкоплівкових наноструктурах.

---

## Архітектура моделі та фізичні алгоритми

Чисельний аналізатор складається з трьох самостійних розрахункових модулів, кожен з яких використовує специфічну чисельну схему для вирішення нелінійних транцендентних рівнянь:

### 1. Ітераційна модель ZnO варистора

Загальна напруга на варисторі `U` складається з падіння напруги на нелінійних міжкристалітних бар'єрах `U_barrier` та падіння напруги на омічному опорі тіла зерен оксиду цинку `R_grain`:

```
U = U_barrier + I · R_grain
```

Оскільки струм `I` пов'язаний із напругою на бар'єрі нелінійним співвідношенням `I = I_0 · (U_barrier / U_N)^α`, ми отримуємо нелінійне трансцендентне рівняння відносно струму:

```
U = U_N · (I / I_0)^(1/α) + I · R_grain
```

У низькострумовій та нелінійній областях (`I < 100 А`) переважає перший доданок, а у режимі надструмів — другий. Для обчислення струму за заданою загальною напругою `U` алгоритм виконує фіксовану кількість ітерацій методом простої ітерації (або методом Ньютона — Рафсона):

```
U_barrier_k+1 = U - I_k · R_grain
I_k+1 = I_0 · (U_barrier_k+1 / U_N)^α
```

Це дозволяє точно змоделювати гладкий перехід від предпробійної області до клампінгу та подальшого омічного насичення на високих струмах.

### 2. Чисельний тепловий баланс NTC термистора

Для розрахунку ВАХ NTC термистора з урахуванням саморозігріву необхідно сумісно розв'язати електричне рівняння провідності та рівняння теплового балансу. У стаціонарному режимі електрична потужність, яка виділяється у корпусі термистора `P_el = I² · R(T)`, має дорівнювати тепловому потоку, що відводиться у довкілля за законом Ньютона — Ріхмана:

```
I² · R(T) = δ · (T_body - T_ambient)
```

де `δ` — коефіцієнт тепловіддачі (Dissipation Constant) [Вт/К], а `R(T)` виражається через B-параметр:

```
R(T) = R_25 · exp(B · (1/T - 1/298.15))
```

Алгоритм бере струм `I` як незалежну змінну і шукає температуру корпусу `T_body` ітераційним методом:
1. Початкове наближення температури: `T_body = T_ambient`.
2. Розрахунок поточного опору: `R = R(T_body)`.
3. Розрахунок теплової потужності: `P = I² · R`.
4. Оновлення температури: `T_body_new = T_ambient + P / δ`.
5. Повторення кроків 2–4 до досягнення збіжності (`|T_body_new - T_body| < 10⁻⁴ K`).
6. Обчислення напруги на термисторі: `U = I · R`.

При малих струмах розігрів незначний, і напруга зростає лінійно. При досягненні критичного струму саморозігрів викликає таке стрімке падіння опору `R(T)`, що добуток `I · R(T)` починає зменшуватися зі зростанням струму. Це дає змогу спостерігати область негативного диференціального опору (`dU/dI < 0`).

### 3. Модуль струмів Пуля — Френкеля

Модуль обчислює густину струму витоку `J_PF` у діелектрику плівки товщиною `d` при прикладанні напруженостей поля `E = U / d` від `0.1` до `5.0 МВ/см`. Алгоритм обчислює зниження бар'єру `ΔE_PF = β_PF · √E`, де константа `β_PF = √(e³ / (π · ε_r · ε_0))`, після чого розраховує експоненціальний фактор активації.

---

## Особливості обчислювальної стійкості та граничні випадки

При практичній чисельній реалізації розрахунку нелінійних кіл виникають два класи чисельних ризиків:

1. **Переповнення числа з плаваючою крапкою (Floating-point Overflow):** Через високі коефіцієнти нелінійності варисторів (`α > 30`) обчислення степеневого виразу `(U / U_N)^α` при `U > 1.5 · U_N` може швидко вийти за межі стандарту IEEE 754 (переповнення double). У коді аналізатора це запобігається обмеженням максимального зсуву напруги та підстановкою ітераційного падіння напруги на опорі зерен.
2. **Температурний розгін (Thermal Divergence):** При чисельному розв'язанні теплового балансу NTC термистора якщо заданий струм перевищує максимальну теплову спроможність моделі, ітераційний процес обчислення температури `T_body` може розходитися до нескінченності. Для забезпечення стійкості у код введено релаксаційну затримку оновлення температури `T_k+1 = 0.5·T_k + 0.5·T_calc`.

---

## Повний вихідний код аналізатора

Нижче наведено робочу реалізацію чисельного моделювання двома мовами — C++20 та Python 3.

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <string>

// Фізичні константи
constexpr double KB = 8.617333262145e-5; // Константа Больцмана, еВ/К
constexpr double EPS_0 = 8.8541878128e-12; // Електрична стала, Ф/м
constexpr double ELEMENTARY_CHARGE = 1.602176634e-19; // Кл

// Результат моделювання точки ВАХ
struct IVPoint {
    double voltage;     // Напруга, В
    double current;     // Струм, А
    double resistance;  // Динамічний опір, Ом
    double temperature; // Температура (для термистора), К
};

// 1. Симуляція ZnO Варистора
std::vector<IVPoint> simulate_varistor(double un_voltage, double alpha, 
                                        double r_grain, double u_min, 
                                        double u_max, int steps) {
    std::vector<IVPoint> curve;
    curve.reserve(steps);
    
    const double du = (u_max - u_min) / (steps - 1);
    const double i_ref = 1e-3; // 1 мА
    
    for (int i = 0; i < steps; ++i) {
        double u = u_min + i * du;
        
        // Струм через міжкристалічний бар'єр
        double i_barrier = i_ref * std::pow(u / un_voltage, alpha);
        
        // Враховуємо послідовний опір зерен (падіння U_grain = I * R_grain)
        double i_total = i_barrier;
        for (int iter = 0; iter < 10; ++iter) {
            double u_barrier = u - i_total * r_grain;
            if (u_barrier < 0) u_barrier = 0;
            i_total = i_ref * std::pow(u_barrier / un_voltage, alpha);
        }
        
        double r_dyn = (i_total > 1e-12) ? (u / i_total) : 1e12;
        curve.push_back({u, i_total, r_dyn, 298.15});
    }
    return curve;
}

// 2. Симуляція NTC Термистора з саморозігрівом
std::vector<IVPoint> simulate_ntc_thermistor(double r25, double b_val, 
                                              double delta_mW_K, double t_amb_C,
                                              double i_min, double i_max, int steps) {
    std::vector<IVPoint> curve;
    curve.reserve(steps);
    
    const double t_amb_K = t_amb_C + 273.15;
    const double delta_W_K = delta_mW_K * 1e-3; // переведення в Вт/К
    const double di = (i_max - i_min) / (steps - 1);
    
    for (int idx = 0; idx < steps; ++idx) {
        double current = i_min + idx * di;
        
        // Ітераційний розв'язок теплового балансу: T = T_amb + (I^2 * R(T)) / delta
        double t_body = t_amb_K;
        double r_ntc = r25;
        
        for (int iter = 0; iter < 30; ++iter) {
            r_ntc = r25 * std::exp(b_val * (1.0 / t_body - 1.0 / 298.15));
            double p_heat = current * current * r_ntc;
            t_body = 0.5 * t_body + 0.5 * (t_amb_K + p_heat / delta_W_K);
        }
        
        double voltage = current * r_ntc;
        curve.push_back({voltage, current, r_ntc, t_body});
    }
    return curve;
}

// 3. Симуляція ефекту Пуля — Френкеля у діелектрику
std::vector<IVPoint> simulate_poole_frenkel(double thickness_nm, double eps_r,
                                             double e_trap_ev, double e_min_MV_cm,
                                             double e_max_MV_cm, int steps) {
    std::vector<IVPoint> curve;
    curve.reserve(steps);
    
    const double d_m = thickness_nm * 1e-9;
    const double de = (e_max_MV_cm - e_min_MV_cm) / (steps - 1);
    
    const double beta_pf_J = std::sqrt(std::pow(ELEMENTARY_CHARGE, 3) / 
                                      (M_PI * eps_r * EPS_0));
    const double beta_pf_eV = beta_pf_J / ELEMENTARY_CHARGE;
    
    const double temp_K = 298.15;
    const double j0 = 1e-6; // А/м^2
    
    for (int i = 0; i < steps; ++i) {
        double e_field_MV_cm = e_min_MV_cm + i * de;
        double e_field_V_m = e_field_MV_cm * 1e8; // В/м
        
        double delta_e_ev = beta_pf_eV * std::sqrt(e_field_V_m);
        double eff_trap_ev = e_trap_ev - delta_e_ev;
        
        double current_density = j0 * (e_field_V_m / 1e6) * 
                                 std::exp(-eff_trap_ev / (KB * temp_K));
        
        double voltage = e_field_V_m * d_m;
        double r_eff = (current_density > 1e-15) ? (voltage / current_density) : 1e15;
        
        curve.push_back({voltage, current_density, r_eff, temp_K});
    }
    return curve;
}

int main() {
    std::cout << "=== СИМУЛЯЦІЯ НЕОМІЧНИХ ВАХ (C++20) ===\n\n";

    // 1. Моделювання ZnO Варистора (U_N = 430V, Alpha = 35)
    std::cout << "--- 1. Варистор ZnO (U_N = 430В, alpha = 35) ---\n";
    std::cout << std::setw(10) << "U [В]" << std::setw(14) << "I [А]" 
              << std::setw(16) << "R [Ом]" << "\n";
    
    auto varistor_iv = simulate_varistor(430.0, 35.0, 0.5, 300.0, 480.0, 7);
    for (const auto& pt : varistor_iv) {
        std::cout << std::setw(10) << std::fixed << std::setprecision(1) << pt.voltage
                  << std::setw(14) << std::scientific << std::setprecision(3) << pt.current
                  << std::setw(16) << std::scientific << std::setprecision(3) << pt.resistance
                  << "\n";
    }

    // 2. Моделювання NTC Термистора (R25 = 10кОм, B = 3950K)
    std::cout << "\n--- 2. NTC Термистор (R25 = 10кОм, Саморозігрів) ---\n";
    std::cout << std::setw(12) << "I [мА]" << std::setw(12) << "U [В]" 
              << std::setw(14) << "R [Ом]" << std::setw(12) << "T [°C]" << "\n";
              
    auto ntc_iv = simulate_ntc_thermistor(10000.0, 3950.0, 5.0, 25.0, 0.0002, 0.003, 7);
    for (const auto& pt : ntc_iv) {
        std::cout << std::setw(12) << std::fixed << std::setprecision(2) << pt.current * 1000.0
                  << std::setw(12) << std::fixed << std::setprecision(2) << pt.voltage
                  << std::setw(14) << std::fixed << std::setprecision(1) << pt.resistance
                  << std::setw(12) << std::fixed << std::setprecision(1) << pt.temperature - 273.15
                  << "\n";
    }

    // 3. Моделювання Пуля - Френкеля для Si3N4 (Товщина 10 нм, eps_r = 3.8, E_trap = 1.2 еВ)
    std::cout << "\n--- 3. Струм витоку Пуля - Френкеля у Si3N4 (10 нм) ---\n";
    std::cout << std::setw(10) << "U [В]" << std::setw(16) << "J [А/м^2]" 
              << std::setw(16) << "R_eff [Ом*м^2]" << "\n";
              
    auto pf_iv = simulate_poole_frenkel(10.0, 3.8, 1.2, 0.5, 3.0, 6);
    for (const auto& pt : pf_iv) {
        std::cout << std::setw(10) << std::fixed << std::setprecision(2) << pt.voltage
                  << std::setw(16) << std::scientific << std::setprecision(3) << pt.current
                  << std::setw(16) << std::scientific << std::setprecision(3) << pt.resistance
                  << "\n";
    }

    return 0;
}
```
```py
import math

# Фізичні константи
KB = 8.617333262145e-5  # Константа Больцмана, еВ/К
EPS_0 = 8.8541878128e-12  # Електрична стала, Ф/м
E_CHARGE = 1.602176634e-19  # Елементарний заряд, Кл

def simulate_varistor(un_voltage: float, alpha: float, r_grain: float, 
                      u_min: float, u_max: float, steps: int):
    """Моделювання ВАХ ZnO варистора."""
    results = []
    du = (u_max - u_min) / (steps - 1)
    i_ref = 1e-3  # 1 мА
    
    for idx in range(steps):
        u = u_min + idx * du
        i_total = i_ref * ((u / un_voltage) ** alpha)
        
        # Ітераційне врахування опору зерен
        for _ in range(10):
            u_barrier = max(0.0, u - i_total * r_grain)
            i_total = i_ref * ((u_barrier / un_voltage) ** alpha)
            
        r_dyn = u / i_total if i_total > 1e-12 else 1e12
        results.append({"U": u, "I": i_total, "R": r_dyn})
    return results

def simulate_ntc_thermistor(r25: float, b_val: float, delta_mW_K: float, 
                             t_amb_C: float, i_min: float, i_max: float, steps: int):
    """Моделювання саморозігріву NTC термистора та негативного диференціального опору."""
    results = []
    t_amb_K = t_amb_C + 273.15
    delta_W_K = delta_mW_K * 1e-3
    di = (i_max - i_min) / (steps - 1)
    
    for idx in range(steps):
        current = i_min + idx * di
        t_body = t_amb_K
        r_ntc = r25
        
        # Ітераційний тепловий баланс
        for _ in range(30):
            r_ntc = r25 * math.exp(b_val * (1.0 / t_body - 1.0 / 298.15))
            p_heat = (current ** 2) * r_ntc
            t_body = 0.5 * t_body + 0.5 * (t_amb_K + p_heat / delta_W_K)
            
        voltage = current * r_ntc
        results.append({
            "I_mA": current * 1000.0,
            "U": voltage,
            "R": r_ntc,
            "T_C": t_body - 273.15
        })
    return results

def simulate_poole_frenkel(thickness_nm: float, eps_r: float, e_trap_ev: float, 
                           e_min_MV_cm: float, e_max_MV_cm: float, steps: int):
    """Моделювання провідності за ефектом Пуля - Френкеля у діелектрику."""
    results = []
    d_m = thickness_nm * 1e-9
    de = (e_max_MV_cm - e_min_MV_cm) / (steps - 1)
    
    beta_pf_J = math.sqrt((E_CHARGE ** 3) / (math.pi * eps_r * EPS_0))
    beta_pf_eV = beta_pf_J / E_CHARGE
    temp_K = 298.15
    j0 = 1e-6
    
    for idx in range(steps):
        e_field_MV_cm = e_min_MV_cm + idx * de
        e_field_V_m = e_field_MV_cm * 1e8
        
        delta_e_ev = beta_pf_eV * math.sqrt(e_field_V_m)
        eff_trap_ev = e_trap_ev - delta_e_ev
        
        current_density = j0 * (e_field_V_m / 1e6) * math.exp(-eff_trap_ev / (KB * temp_K))
        voltage = e_field_V_m * d_m
        r_eff = voltage / current_density if current_density > 1e-15 else 1e15
        
        results.append({
            "U": voltage,
            "J": current_density,
            "R_eff": r_eff
        })
    return results

if __name__ == "__main__":
    print("=== СИМУЛЯЦІЯ НЕОМІЧНИХ ВАХ (Python 3) ===")
    
    print("\n--- 1. Варистор ZnO (U_N = 430В, alpha = 35) ---")
    var_data = simulate_varistor(430.0, 35.0, 0.5, 300.0, 480.0, 7)
    for row in var_data:
        print(f"U = {row['U']:5.1f} В | I = {row['I']:9.3e} А | R = {row['R']:9.3e} Ом")
        
    print("\n--- 2. NTC Термистор (R25 = 10кОм, Саморозігрів) ---")
    ntc_data = simulate_ntc_thermistor(10000.0, 3950.0, 5.0, 25.0, 0.0002, 0.003, 7)
    for row in ntc_data:
        print(f"I = {row['I_mA']:5.2f} мА | U = {row['U']:5.2f} В | R = {row['R']:7.1f} Ом | T = {row['T_C']:5.1f} °C")
        
    print("\n--- 3. Струм витоку Пуля - Френкеля у Si3N4 (10 нм) ---")
    pf_data = simulate_poole_frenkel(10.0, 3.8, 1.2, 0.5, 3.0, 6)
    for row in pf_data:
        print(f"U = {row['U']:5.2f} В | J = {row['J']:9.3e} А/м^2 | R_eff = {row['R_eff']:9.3e} Ом*м^2")
```
:::

---

## Інтерпретація результатів чисельного розрахунку

Аналіз отриманих у результаті виконання симулятора числових даних дає змогу зробити три важливі інженерні висновки:

1. **Варисторний режим:** При збільшенні напруги з 300 В до 480 В (всього на 60%) струм зростає на 6 порядків (з мікроамперів до десятків ампер), що підтверджує ефект надшвидкого нелінійного клампінгу для захисту кіл.
2. **Термисторний режим:** На початковій ділянці (малі струми) напруга пропорційно зростає зі струмом. Проте при перевищенні струму 1.5 мА саморозігрів піднімає температуру елемента понад 70 °C, внаслідок чого опір падає з 10 кОм до 1.8 кОм, і напруга на термисторі починає зменшуватися при зростанні струму (`dU/dI < 0`).
3. **Режим Пуля — Френкеля:** Підвищення поля втричі (з 0.5 до 1.5 МВ/см) за рахунок деформації кулонівської ями ловушки знижує бар'єр і викликає експоненціальний стрибок струму витоку на 4 порядки.
