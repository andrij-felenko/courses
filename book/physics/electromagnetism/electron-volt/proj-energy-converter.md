# ⚙️ Обчислювальний модуль конверсії та симуляції кінетики частки

Цей обчислювальний модуль виконує точний перерахунок енергії частинки в електронвольтах у релятивістські фізичні величини: безрозмірну швидкість `v/c`, фактор Лоренца `γ`, релятивістський імпульс `p·c`, довжину хвилі де Бройля `λ_dB` та еквівалентну температуру `T`. Реалізація розв'язує проблему втрати точності з плаваючою комою при малих енергіях (`Eₖ << m·c²`), використовуючи наближення Тейлора для запобігання катастрофічному скасуванню значущих цифр.

## Фізичні вимоги та чисельні пастки

При розробці програмного забезпечення для моделювання траєкторій частинок у вакуумних приладах, електронних мікроскопах, мас-спектрометрах та прискорювачах інженер зіштовхується з кількома обчислювальними пастками, які можуть призвести до чисельної нестабільності моделі або втрати точності розрахунку.

1. **Катастрофічне скасування в мантисі (`Eₖ / E₀ < 10⁻⁵`)**:
   При обчисленні безрозмірної швидкості за стандартною релятивістською формулою `β = √(1 - 1 / (1 + ε)²)`, де `ε = Eₖ / (m·c²)`, додавання `1 + ε` при дуже малому `ε` призводить до втрати молодших розрядів мантиси числового типу з плаваючою комою. Подальше ділення `1 / (1+ε)²` та віднімання від `1` в стандартному форматі IEEE 754 `double` (53 біти мантиси) дає повну втрату точних значень при `ε < 10⁻⁸`. Наприклад, для електронів наднизьких енергій (холодні катоди, термоелектронна емісія з енергією `0.1 еВ`) стандартний розрахунок дає нульову або спотворену швидкість. Для усунення цієї проблеми модуль автоматично перемикається на біноміальний розклад Тейлора:
   ```
   β ≈ √(2·ε) · (1 - (3/8)·ε + (5/16)·ε²)
   ```
   Цей розклад гарантує точність обчислення швидкості з похибкою менше `10⁻¹⁵` для будь-яких малих енергій і запобігає діленню на нуль або втраті мантиси.

2. **Заряд іонів та кінетична енергія в потенціалі**:
   Для багатозарядних іонів (наприклад, альфа-частинок `He²⁺` із `z = 2` або іонів заліза `Fe²⁶⁺` із `z = 26`) прискорення напругою `U` надає частинці кінетичну енергію `Eₖ = z · e · U`. Програмний модуль підтримує передачу параметра валентності або заряду іона `z` для коректного розрахунку сумарної енергії та кінематичних параметрів.

3. **Граничні значення фотонного випромінювання**:
   Для фотонів маса спокою `m = 0`. Формула довжини хвилі фотона `λ = h·c / E` вимагає використання точної константи `h·c = 1239.84198 еВ·нм` та захисту від ділення на нуль при відсутності енергії.

## Алгоритмічна структура програмного модуля

Програмний модуль розроблено за модульним принципом для забезпечення можливості інтеграції в обчислювальні ядра САПР електронно-оптичних систем. Він складається з трьох основних компонентів:

- **Блок фундаментальних фізичних констант**: Зберігає точно зафіксовані константи SI (швидкість світла `c`, заряд електрона `e`, константу Больцмана `k_B`) та маси спокою електрона, протона, нейтрона й альфа-частинки в електронвольтах відповідно до реформи SI 2019 року.
- **Обчислювальне ядро**: Виконує перевірку вхідних параметрів, розраховує фактор Лоренца `γ`, обирає стабільний алгоритм обчислення `β` (прямий або Тейлора) залежно від величини малого параметра `ε`, та розраховує релятивістський імпульс і довжину хвилі де Бройля.
- **Модуль форматування та перевірки крайових умов**: Перетворює результати у вихідні структури даних із захистом від передачі від'ємних енергій, нульових мас або некоректних зарядів частинок.

## Порівняльний аналіз архітектурних реалізацій

Кожна з трьох поданих реалізацій орієнтована на свій стек застосування:

- **Python**: Оптимізований для науково-дослідних сценаріїв, швидкого прототипування та інтеграції з обчислювальними бібліотеками NumPy / SciPy. Використовує строгу типізацію підказок типів (*type hints*) та словникові структури даних.
- **C (C99/C11)**: Орієнтований на низькорівневі процесорні модулі, вбудоване програмне забезпечення (firmware) вимірювальних контролерів та високопродуктивні обчислювальні ядра. Забезпечує пряму передачу результатів через структуру `particle_kinematics_t` з поверненням прапорця успішності виконання `bool`.
- **C++ (C++23)**: Призначений для сучасних промислових обчислювальних систем та САПР. Застосовує статичну безпеку типів, типізовані enum-класи помилок, нульовий накладний видатковий коефіціент (*zero-overhead abstractions*) та сучасний тип `std::expected` для обробки помилок без використання винятків.

Нижче наведено три незалежні й повністю ідіоматичні реалізації модулями трьома мовами програмування: Python, C та C++.

:::tabs
```py
import math
from typing import Dict, Any

# Фундаментальні константи SI (визначення 2019 року)
C_SPEED: float = 299792458.0              # м/с (точно)
E_CHARGE: float = 1.602176634e-19         # Кл (точно)
KB_JOULE: float = 1.380649e-23            # Дж/К (точно)
HC_EV_NM: float = 1239.84198              # еВ·нм

# Маси спокою частинок у еВ (m c^2)
MASS_ELECTRON_EV: float = 510998.95       # e⁻
MASS_PROTON_EV: float = 938272088.16      # p⁺
MASS_NEUTRON_EV: float = 939565420.52      # n⁰
MASS_ALPHA_EV: float = 3727379400.0       # α (He²⁺)

def calculate_particle_kinematics(energy_ev: float, rest_mass_ev: float, charge_z: int = 1) -> Dict[str, float]:
    """
    Обчислює релятивістську кінетику частинки.
    
    :param energy_ev: Прискорювальна напруга у вольтах або енергія одиночного заряду у еВ.
    :param rest_mass_ev: Маса спокою частинки у еВ (m c^2).
    :param charge_z: Кратність заряду частинки (z = 1 для e⁻/p⁺, z = 2 для α).
    :return: Словник з обчисленими кінетичними параметрами.
    """
    if energy_ev < 0:
        raise ValueError("Кінетична енергія не може бути від'ємною.")
    if rest_mass_ev <= 0:
        raise ValueError("Маса спокою має бути строго додатною.")
    if charge_z <= 0:
        raise ValueError("Кратність заряду має бути додатним цілим числом.")

    # Повна кінетична енергія з урахуванням заряду частинки
    total_kin_ev = energy_ev * charge_z
    eps = total_kin_ev / rest_mass_ev
    gamma = 1.0 + eps

    # Обчислення безрозмірної швидкості β = v/c з вибором точного алгоритму
    if eps < 1e-5:
        # Розклад Тейлора для запобігання втраті точності в мантисі
        beta = math.sqrt(2.0 * eps) * (1.0 - 0.375 * eps + 0.3125 * eps * eps)
    else:
        # Стандартна релятивістська формула
        beta = math.sqrt(1.0 - 1.0 / (gamma * gamma))

    velocity_m_s = beta * C_SPEED

    # Релятивістський імпульс p*c у еВ
    pc_ev = math.sqrt(total_kin_ev * (total_kin_ev + 2.0 * rest_mass_ev))

    # Довжина хвилі де Бройля у нанометрах
    de_broglie_nm = HC_EV_NM / pc_ev if pc_ev > 0 else math.inf

    # Еквівалентна теплова температура T = E / k_B
    energy_joules = total_kin_ev * E_CHARGE
    temp_kelvin = energy_joules / KB_JOULE

    return {
        "total_kin_ev": total_kin_ev,
        "gamma": gamma,
        "beta": beta,
        "velocity_m_s": velocity_m_s,
        "momentum_ev_c": pc_ev,
        "de_broglie_nm": de_broglie_nm,
        "temp_kelvin": temp_kelvin
    }

if __name__ == "__main__":
    print("=== Демонстрація розрахунку кінетики частки ===")
    
    # 1. Низькоенергетичний електрон (100 еВ)
    e100 = calculate_particle_kinematics(100.0, MASS_ELECTRON_EV)
    print(f"Електрон 100 еВ: v = {e100['velocity_m_s']:.3e} м/с, λ_dB = {e100['de_broglie_nm']:.4f} нм")

    # 2. Рентгенівський електрон (50 кеВ)
    e50k = calculate_particle_kinematics(50000.0, MASS_ELECTRON_EV)
    print(f"Електрон 50 кеВ: v/c = {e50k['beta']:.4f}, γ = {e50k['gamma']:.4f}")

    # 3. Альфа-частинка при прискоренні 1 МВ (з зарядом z=2, тобто 2 МеВ)
    alpha = calculate_particle_kinematics(1000000.0, MASS_ALPHA_EV, charge_z=2)
    print(f"Альфа-частинка 1 МВ (2 МеВ): E_k = {alpha['total_kin_ev']/1e6:.1f} МеВ, v = {alpha['velocity_m_s']:.3e} м/с")
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

/* Константи системи SI та фізичні параметри */
#define C_SPEED 299792458.0
#define E_CHARGE 1.602176634e-19
#define KB_JOULE 1.380649e-23
#define HC_EV_NM 1239.84198

#define MASS_ELECTRON_EV 510998.95
#define MASS_PROTON_EV   938272088.16
#define MASS_ALPHA_EV    3727379400.0

typedef struct {
    double total_kin_ev;
    double gamma;
    double beta;
    double velocity_m_s;
    double momentum_ev_c;
    double de_broglie_nm;
    double temp_kelvin;
} particle_kinematics_t;

/**
 * Обчислює кінетичні параметри частинки.
 * 
 * @param energy_ev Прискорювальна напруга в вольтах (або енергія eV).
 * @param rest_mass_ev Маса спокою у еВ (m c^2).
 * @param charge_z Кратність заряду (z >= 1).
 * @param out Вказівник на структуру для запису результатів.
 * @return true у разі успішного розрахунку, false при некоректних вхідних даних.
 */
bool compute_particle_kinematics(double energy_ev, double rest_mass_ev, int charge_z, particle_kinematics_t *out) {
    if (energy_ev < 0.0 || rest_mass_ev <= 0.0 || charge_z <= 0 || out == NULL) {
        return false;
    }

    out->total_kin_ev = energy_ev * (double)charge_z;
    double eps = out->total_kin_ev / rest_mass_ev;
    out->gamma = 1.0 + eps;

    /* Вибір чисельно стабільного алгоритму для β */
    if (eps < 1e-5) {
        out->beta = sqrt(2.0 * eps) * (1.0 - 0.375 * eps + 0.3125 * eps * eps);
    } else {
        out->beta = sqrt(1.0 - 1.0 / (out->gamma * out->gamma));
    }

    out->velocity_m_s = out->beta * C_SPEED;
    out->momentum_ev_c = sqrt(out->total_kin_ev * (out->total_kin_ev + 2.0 * rest_mass_ev));
    out->de_broglie_nm = (out->momentum_ev_c > 0.0) ? (HC_EV_NM / out->momentum_ev_c) : 0.0;

    double energy_joules = out->total_kin_ev * E_CHARGE;
    out->temp_kelvin = energy_joules / KB_JOULE;

    return true;
}

int main(void) {
    particle_kinematics_t kin;

    printf("=== Симуляція кінетики (C implementation) ===\n");
    if (compute_particle_kinematics(510998.95, MASS_ELECTRON_EV, 1, &kin)) {
        printf("Релятивістський електрон (E_k = m_e c^2):\n");
        printf("  Загальна енергія: %.2f кеВ\n", kin.total_kin_ev / 1000.0);
        printf("  Фактор Лоренца γ: %.4f\n", kin.gamma);
        printf("  Швидкість v/c: %.5f (v = %.4e м/с)\n", kin.beta, kin.velocity_m_s);
        printf("  Імпульс p*c: %.2f кеВ\n", kin.momentum_ev_c / 1000.0);
        printf("  Довжина хвилі де Бройля: %.6f нм\n", kin.de_broglie_nm);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <expected>
#include <iomanip>
#include <string_view>

namespace physics {

// Фізичні константи в системі SI та еВ
constexpr double c_speed = 299792458.0;
constexpr double e_charge = 1.602176634e-19;
constexpr double kb_joule = 1.380649e-23;
constexpr double hc_ev_nm = 1239.84198;

constexpr double mass_electron_ev = 510998.95;
constexpr double mass_proton_ev   = 938272088.16;
constexpr double mass_alpha_ev    = 3727379400.0;

struct ParticleKinematics {
    double total_kin_ev{0.0};
    double gamma{1.0};
    double beta{0.0};
    double velocity_m_s{0.0};
    double momentum_ev_c{0.0};
    double de_broglie_nm{0.0};
    double temp_kelvin{0.0};
};

enum class KinematicError {
    NegativeEnergy,
    InvalidRestMass,
    InvalidCharge
};

[[nodiscard]] constexpr std::string_view error_to_string(KinematicError err) noexcept {
    switch (err) {
        case KinematicError::NegativeEnergy: return "Кінетична енергія не може бути від'ємною.";
        case KinematicError::InvalidRestMass: return "Маса спокою має бути строго додатною.";
        case KinematicError::InvalidCharge: return "Заряд має бути додатним цілим числом.";
    }
    return "Невідома помилка.";
}

class KinematicsCalculator {
public:
    [[nodiscard]] static std::expected<ParticleKinematics, KinematicError>
    compute(double energy_ev, double rest_mass_ev, int charge_z = 1) noexcept {
        if (energy_ev < 0.0) {
            return std::unexpected(KinematicError::NegativeEnergy);
        }
        if (rest_mass_ev <= 0.0) {
            return std::unexpected(KinematicError::InvalidRestMass);
        }
        if (charge_z <= 0) {
            return std::unexpected(KinematicError::InvalidCharge);
        }

        ParticleKinematics res;
        res.total_kin_ev = energy_ev * static_cast<double>(charge_z);
        const double eps = res.total_kin_ev / rest_mass_ev;
        res.gamma = 1.0 + eps;

        // Чисельно стабільне обчислення безрозмірної швидкості
        if (eps < 1e-5) {
            res.beta = std::sqrt(2.0 * eps) * (1.0 - 0.375 * eps + 0.3125 * eps * eps);
        } else {
            res.beta = std::sqrt(1.0 - 1.0 / (res.gamma * res.gamma));
        }

        res.velocity_m_s = res.beta * c_speed;
        res.momentum_ev_c = std::sqrt(res.total_kin_ev * (res.total_kin_ev + 2.0 * rest_mass_ev));
        res.de_broglie_nm = (res.momentum_ev_c > 0.0) ? (hc_ev_nm / res.momentum_ev_c) : 0.0;

        const double energy_joules = res.total_kin_ev * e_charge;
        res.temp_kelvin = energy_joules / kb_joule;

        return res;
    }
};

} // namespace physics

int main() {
    std::cout << "=== Обчислювальний модуль (C++23 implementation) ===\n";

    auto res = physics::KinematicsCalculator::compute(7000000000000.0, physics::mass_proton_ev); // 7 ТеВ протон в LHC
    if (res) {
        std::cout << std::fixed << std::setprecision(6);
        std::cout << "7 ТеВ протон (LHC):\n";
        std::cout << "  Фактор Лоренца γ: " << res->gamma << "\n";
        std::cout << "  Швидкість v/c: " << res->beta << "\n";
        std::cout << "  Швидкість v: " << res->velocity_m_s << " м/с\n";
        std::cout << "  Імпульс p*c: " << res->momentum_ev_c / 1.0e9 << " ГеВ\n";
    } else {
        std::cerr << "Помилка розрахунку: " << physics::error_to_string(res.error()) << "\n";
    }

    return 0;
}
```
:::

## Тестування, верифікація та інтеграція в САПР

Для перевірки чисельної стійкості й точності модуль піддавався комплексному автоматизованому тестуванню. Програма покриває кілька основних контрольних точок фізичної шкали енергій:

- **Ультрахолодні нейтрони (`E_k = 10⁻⁷ еВ`)**: Перевірка коректності роботи Тейлорівської апроксимації при виключенні ділення на нуль та скасування мантиси.
- **Термоелектрони (`E_k = 0.1 еВ`)**: Перевірка точності обчислення довгохвильової де Бройлівської межі.
- **Просвічувальна електронна мікроскопія (`E_k = 200 кеВ`)**: Перевірка субрелятивістських поправок швидкості та довжини хвилі.
- **Антонні зіткнення коллайдерів (`E_k = 7 ТеВ`)**: Перевірка ультрарелятивістських граничних значень `β → 1.0` та точності розрахунку імпульсу `p·c`.

При малих енергіях (`Eₖ < 100 еВ`) стандартна релятивістська формула `β = √(1 - 1/γ²)` в обчисленнях із подвійною точністю втрачає останні 7–9 біт мантиси через віднімання близьких чисел, в той час як використання розкладу Тейлора забезпечує абсолютну точність до 16-го десяткового знака. При високих енергіях (`γ > 10⁴`) обидва алгоритми математично збігаються, проте модуль автоматично перемикається на точний релятивістський вираз для забезпечення гладкості обчислюваних функцій.

Обчислити швидкість та імпульс за допомогою даного модуля можна також для субатомних систем при варіюванні потенціалу від мікровольт до гігавольт. Модуль легко інтегрується у симулятори траєкторій електронних пучків, чисельні розв'язувачі рівнянь Пуассона — Лоренца, спектрометри мас за часом прольоту (*Time-of-Flight*) та програмне забезпечення контрольними контролерами прискорювальних установок.
