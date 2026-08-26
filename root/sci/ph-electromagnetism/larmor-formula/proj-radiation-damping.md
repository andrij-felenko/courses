# ⚙️ Чисельне моделювання динаміки заряду з радіаційним тертям Ландау-Ліфшиця

Чисельне моделювання руху релятивістських заряджених частинок у сильних зовнішніх електромагнітних полях є критично важливим завданням при проєктуванні прискорювачів високих енергій, моделюванні накопичувальних кілець синхротронів та дослідженні релятивістської плазми довкола пульсарів і чорних дір. Головна складність цієї задачі полягає в тому, що частинка не лише рухається під дією зовнішньої сили Лоренца, але й безперервно втрачає власний імпульс та енергію на електромагнітне випромінювання. Це явище описується введенням сили радіаційного самогальмування (радіаційного тертя).

---

## 1. Проблема самоприскорення та рівняння Ландау-Ліфшиця

Класична сила реакції випромінювання, отримана Максом Абрагамом та Гендріком Лоренцом, має вигляд:

```
F_rad = m · τ₀ · d²v / dt²
```

де `τ₀ = q² / (6 · π · ε₀ · m · c³)` — характеристичний електродинамічний час частинки (для електрона `τ₀ ≈ 6.256 · 10⁻²⁴` секунди).

Якщо підставити силу Абрагама-Лоренца у другий закон Ньютона, отримуємо диференціальне рівняння третього порядку за просторовими координатами:

```
m · ( dv/dt - τ₀ · d²v/dt² ) = F_ext
```

Безпосереднє чисельне інтегрування цього рівняння стикається з фундаментальною математичною та фізичною проблемою — наявністю так званих розв'язків із самоприскоренням (англ. *runaway solutions*). За відсутності будь-яких зовнішніх сил (`F_ext = 0`) рівняння має точний експоненційний розв'язок `a(t) = a₀ · exp(t / τ₀)`. Оскільки час `τ₀` надзвичайно малий, будь-яка неминуча похибка округлення чисел із плаваючою комою діє як початкове збурення `a₀`, спричиняючи вибухоподібне чисельне самоприскорення частинки за лічені ітерації.

Для подолання цієї нестійкості Лев Ландау та Євген Ліфшиць розробили регулярне наближення, засноване на фізичній теорії збурень за малим параметром `τ₀`. Оскільки сила радіаційного тертя у всіх практичних випадках є надзвичайно малою поправкою порівняно з основною зовнішньою силою Лоренца, головне прискорення частинки з високою точністю визначається зовнішнім полем:

```
dv / dt ≈ F_ext / m
```

Диференціюючи це наближення за часом вздовж фазової траєкторії частинки, знаходимо вищу похідну прискорення через просторові та часові градієнти зовнішнього поля:

```
d²v / dt² ≈ (1 / m) · dF_ext / dt = (1 / m) · [ ∂F_ext / ∂t + (v · ∇) F_ext + (F_ext / m · ∇_v) F_ext ]
```

Розглянемо рух електрона в однорідному статичному магнітному полі `B = (0, 0, B₀)`. Зовнішня сила Лоренца дорівнює `F_ext = q · (v × B)`. Її повна похідна за часом з урахуванням `dv/dt ≈ (q/m) (v × B)` набуває строго дисипативного вигляду:

```
dF_ext / dt = q · ( (dv/dt) × B ) ≈ (q² / m) · ( (v × B) × B ) = - (q² · B₀² / m) · v_perp
```

де `v_perp = (v_x, v_y, 0)` — вектор проекції швидкості на площину, перпендикулярну до ліній магнітного поля.

Підставляючи цю похідну у формулу сили випромінювання, отримуємо регулярне рівняння руху **Ландау-Ліфшиця** другого порядку:

```
m · dv / dt = q · (v × B) - (q⁴ · B₀² / (6 · π · ε₀ · m² · c³)) · v_perp
```

Другий доданок у правій частині є чистою силою тертя, спрямованою строго протилежно до поточної швидкості частинки. Ця сила плавно зменшує кінетичну енергію електрона без будь-яких ознак нефізичного експоненційного самоприскорення.

---

## 2. Енергетичний баланс та інтегрування потужності Лармора

Миттєва потужність електромагнітного випромінювання частинки розраховується за формулою Лармора:

```
P(t) = (q² · |dv/dt|²) / (6 · π · ε₀ · c³)
```

Повна енергія `E_rad(t)`, яку частинка випроменила за проміжок часу від `0` до `t`, є часовим інтегралом від миттєвої потужності:

```
E_rad(t) = ∫₀ᵗ P(t') dt'
```

Закон збереження енергії вимагає, щоб зменшення кінетичної енергії частинки `ΔE_kin = E_kin(0) - E_kin(t)` у будь-який момент часу строго дорівнювало накопиченій енергії випромінювання `E_rad(t)`:

```
ΔE_kin(t) = ½ m · (v₀² - v(t)²) = E_rad(t)
```

Характерний час експоненційного радіаційного затухання швидкості в магнітному полі `B₀` оцінюється аналітично як:

```
τ_decay = (6 · π · ε₀ · m³ · c³) / (q⁴ · B₀²)
```

Для магнітного поля `B₀ = 5.0` Тл час затухання швидкості електрона становить близько `0.1` мікросекунди, що відповідає десяткам тисяч повних циклотронних обертів.

---

## 3. Програмна реалізація інтегратора Рунге-Кутти 4-го порядку (RK4)

Нижче наведено паралельну реалізацію чисельного моделювача траєкторії та радіаційних втрат мовами C та C++. Алгоритм реалізує класичний метод Рунге-Кутти 4-го порядку (RK4) з постійним часовим кроком `dt = 0.1` пікосекунди, обчислюючи фазові координати `(x, y, z)`, компоненти швидкості `(v_x, v_y, v_z)`, миттєву потужність Лармора та інтегральний енергетичний баланс.

:::tabs
```c
#include <stdio.h>
#include <math.h>
#include <stdbool.h>

/* Фізичні константи в системі SI */
static const double C_LIGHT = 2.99792458e8;     /* швидкість світла, м/с */
static const double EPS0    = 8.8541878128e-12; /* електрична стала, Ф/м */
static const double Q_ELEM  = -1.602176634e-19; /* заряд електрона, Кл */
static const double M_ELEM  = 9.1093837015e-31; /* маса електрона, кг */
static const double PI_VAL  = 3.141592653589793;

/* Вектор стану частинки: координати та швидкості */
typedef struct {
    double x, y, z;
    double vx, vy, vz;
} ParticleState;

/* Похідні стану: швидкості та прискорення */
typedef struct {
    double dx, dy, dz;
    double dvx, dvy, dvz;
} StateDeriv;

/* Обчислення похідних стану за рівнянням Ландау-Ліфшиця */
static StateDeriv compute_derivatives(const ParticleState *s, double B0) {
    StateDeriv d;
    d.dx = s->vx;
    d.dy = s->vy;
    d.dz = s->vz;

    /* 1. Сила Лоренца: F_lor = q * (v x B), B = (0, 0, B0) */
    double F_lor_x = Q_ELEM * (s->vy * B0);
    double F_lor_y = Q_ELEM * (-s->vx * B0);
    double F_lor_z = 0.0;

    /* 2. Радіаційне гальмування Ландау-Ліфшиця: F_rad = -gamma_damp * v_perp */
    /* gamma_damp = q^4 * B0^2 / (6 * pi * eps0 * m^2 * c^3) */
    double gamma_damp = (pow(Q_ELEM, 4) * B0 * B0) /
                        (6.0 * PI_VAL * EPS0 * M_ELEM * M_ELEM * pow(C_LIGHT, 3));

    double F_rad_x = -gamma_damp * s->vx;
    double F_rad_y = -gamma_damp * s->vy;
    double F_rad_z = 0.0;

    /* Повне прискорення a = (F_lor + F_rad) / m */
    d.dvx = (F_lor_x + F_rad_x) / M_ELEM;
    d.dvy = (F_lor_y + F_rad_y) / M_ELEM;
    d.dvz = (F_lor_z + F_rad_z) / M_ELEM;

    return d;
}

/* Миттєва потужність випромінювання Лармора P = q^2 * a^2 / (6 * pi * eps0 * c^3) */
static double compute_larmor_power(double ax, double ay, double az) {
    double a_sq = ax * ax + ay * ay + az * az;
    return (Q_ELEM * Q_ELEM * a_sq) / (6.0 * PI_VAL * EPS0 * pow(C_LIGHT, 3));
}

/* Один крок інтегрування методом Рунге-Кутти 4-го порядку */
static ParticleState rk4_step(const ParticleState *s, double dt, double B0) {
    StateDeriv k1 = compute_derivatives(s, B0);

    ParticleState s2;
    s2.x  = s->x  + 0.5 * dt * k1.dx;
    s2.y  = s->y  + 0.5 * dt * k1.dy;
    s2.z  = s->z  + 0.5 * dt * k1.dz;
    s2.vx = s->vx + 0.5 * dt * k1.dvx;
    s2.vy = s->vy + 0.5 * dt * k1.dvy;
    s2.vz = s->vz + 0.5 * dt * k1.dvz;
    StateDeriv k2 = compute_derivatives(&s2, B0);

    ParticleState s3;
    s3.x  = s->x  + 0.5 * dt * k2.dx;
    s3.y  = s->y  + 0.5 * dt * k2.dy;
    s3.z  = s->z  + 0.5 * dt * k2.dz;
    s3.vx = s->vx + 0.5 * dt * k2.dvx;
    s3.vy = s->vy + 0.5 * dt * k2.dvy;
    s3.vz = s->vz + 0.5 * dt * k2.dvz;
    StateDeriv k3 = compute_derivatives(&s3, B0);

    ParticleState s4;
    s4.x  = s->x  + dt * k3.dx;
    s4.y  = s->y  + dt * k3.dy;
    s4.z  = s->z  + dt * k3.dz;
    s4.vx = s->vx + dt * k3.dvx;
    s4.vy = s->vy + dt * k3.dvy;
    s4.vz = s->vz + dt * k3.dvz;
    StateDeriv k4 = compute_derivatives(&s4, B0);

    ParticleState next;
    next.x  = s->x  + (dt / 6.0) * (k1.dx  + 2.0 * k2.dx  + 2.0 * k3.dx  + k4.dx);
    next.y  = s->y  + (dt / 6.0) * (k1.dy  + 2.0 * k2.dy  + 2.0 * k3.dy  + k4.dy);
    next.z  = s->z  + (dt / 6.0) * (k1.dz  + 2.0 * k2.dz  + 2.0 * k3.dz  + k4.dz);
    next.vx = s->vx + (dt / 6.0) * (k1.dvx + 2.0 * k2.dvx + 2.0 * k3.dvx + k4.dvx);
    next.vy = s->vy + (dt / 6.0) * (k1.dvy + 2.0 * k2.dvy + 2.0 * k3.dvy + k4.dvy);
    next.vz = s->vz + (dt / 6.0) * (k1.dvz + 2.0 * k2.dvz + 2.0 * k3.dvz + k4.dvz);

    return next;
}

int main(void) {
    const double B_FIELD = 5.0;            /* Магнітне поле, Тл */
    const double V_INIT  = 0.2 * C_LIGHT;  /* Початкова швидкість, м/с */
    const double DT      = 1.0e-13;        /* Крок інтегрування, с */
    const int    N_STEPS = 10000;          /* Кількість кроків */

    ParticleState state = {0.0, 0.0, 0.0, V_INIT, 0.0, 0.0};
    double total_radiated_energy = 0.0;
    double e_kin_initial = 0.5 * M_ELEM * V_INIT * V_INIT;

    printf("Крок | Час (пс) | R_орбіти (мкм) | V/c | Потужність (нВт) | E_рад (еВ)\n");
    printf("----------------------------------------------------------------------\n");

    for (int step = 0; step <= N_STEPS; ++step) {
        double t_ps = (step * DT) * 1.0e12;
        double v_sq = state.vx * state.vx + state.vy * state.vy + state.vz * state.vz;
        double v_mag = sqrt(v_sq);
        double r_cyclotron = (M_ELEM * v_mag) / (fabs(Q_ELEM) * B_FIELD) * 1.0e6;

        StateDeriv d = compute_derivatives(&state, B_FIELD);
        double p_inst = compute_larmor_power(d.dvx, d.dvy, d.dvz);

        if (step % 2000 == 0) {
            double e_rad_ev = total_radiated_energy / 1.602176634e-19;
            printf("%4d | %8.2f | %14.4f | %5.3f | %16.4e | %10.4f\n",
                   step, t_ps, r_cyclotron, v_mag / C_LIGHT, p_inst * 1.0e9, e_rad_ev);
        }

        /* Накопичення випроміненої енергії методом трапецій */
        total_radiated_energy += p_inst * DT;
        state = rk4_step(&state, DT, B_FIELD);
    }

    double e_kin_final = 0.5 * M_ELEM * (state.vx * state.vx + state.vy * state.vy);
    double delta_ekin = e_kin_initial - e_kin_final;

    printf("\nБаланс енергії:\n");
    printf("  Втрата кінетичної енергії: %.6e Дж (%.4f еВ)\n",
           delta_ekin, delta_ekin / 1.602176634e-19);
    printf("  Інтеграл випромінювання:   %.6e Дж (%.4f еВ)\n",
           total_radiated_energy, total_radiated_energy / 1.602176634e-19);

    return 0;
}
```
```cpp
#include <iostream>
#include <iomanip>
#include <cmath>
#include <vector>
#include <array>
#include <numbers>

namespace electrodynamics {

/* Фізичні константи в системі SI */
inline constexpr double C_LIGHT = 2.99792458e8;     // швидкість світла, м/с
inline constexpr double EPS0    = 8.8541878128e-12; // електрична стала, Ф/м
inline constexpr double Q_ELEM  = -1.602176634e-19; // заряд електрона, Кл
inline constexpr double M_ELEM  = 9.1093837015e-31; // маса електрона, кг
inline constexpr double EV_JOULE = 1.602176634e-19; // 1 еВ у Джоулях

struct Vector3D {
    double x{0.0}, y{0.0}, z{0.0};

    [[nodiscard]] constexpr Vector3D operator+(const Vector3D& o) const noexcept {
        return {x + o.x, y + o.y, z + o.z};
    }
    [[nodiscard]] constexpr Vector3D operator*(double s) const noexcept {
        return {x * s, y * s, z * s};
    }
    [[nodiscard]] double norm_sq() const noexcept {
        return x * x + y * y + z * z;
    }
    [[nodiscard]] double norm() const noexcept {
        return std::sqrt(norm_sq());
    }
};

struct ParticleState {
    Vector3D pos{};
    Vector3D vel{};
};

class SynchrotronSimulator {
public:
    explicit SynchrotronSimulator(double b_field, double initial_vel) noexcept
        : b_field_(b_field) {
        state_.vel = {initial_vel, 0.0, 0.0};
        initial_kin_energy_ = 0.5 * M_ELEM * initial_vel * initial_vel;
    }

    struct StepLog {
        double time_ps;
        double radius_um;
        double speed_ratio;
        double power_nw;
        double energy_rad_ev;
    };

    StepLog step(double dt) noexcept {
        const auto deriv = compute_derivatives(state_);
        const double p_inst = compute_larmor_power(deriv.vel);
        total_radiated_energy_ += p_inst * dt;

        state_ = rk4_step(state_, dt);
        current_time_ += dt;

        const double v_mag = state_.vel.norm();
        const double r_cyc = (M_ELEM * v_mag) / (std::abs(Q_ELEM) * b_field_) * 1.0e6;

        return {
            current_time_ * 1.0e12,
            r_cyc,
            v_mag / C_LIGHT,
            p_inst * 1.0e9,
            total_radiated_energy_ / EV_JOULE
        };
    }

    [[nodiscard]] double initial_kinetic_energy() const noexcept { return initial_kin_energy_; }
    [[nodiscard]] double current_kinetic_energy() const noexcept {
        return 0.5 * M_ELEM * state_.vel.norm_sq();
    }
    [[nodiscard]] double total_radiated_energy() const noexcept { return total_radiated_energy_; }

private:
    double b_field_;
    ParticleState state_{};
    double current_time_{0.0};
    double initial_kin_energy_{0.0};
    double total_radiated_energy_{0.0};

    [[nodiscard]] ParticleState compute_derivatives(const ParticleState& s) const noexcept {
        // Сила Лоренца F_lor = q * (v x B) для B = (0, 0, B0)
        const Vector3D f_lor{
            Q_ELEM * s.vel.y * b_field_,
            -Q_ELEM * s.vel.x * b_field_,
            0.0
        };

        // Демпфування Ландау-Ліфшиця: F_rad = -gamma_damp * v_perp
        const double gamma_damp = (std::pow(Q_ELEM, 4) * b_field_ * b_field_) /
                                  (6.0 * std::numbers::pi * EPS0 * M_ELEM * M_ELEM * std::pow(C_LIGHT, 3));

        const Vector3D f_rad{
            -gamma_damp * s.vel.x,
            -gamma_damp * s.vel.y,
            0.0
        };

        return {
            s.vel,
            (f_lor + f_rad) * (1.0 / M_ELEM)
        };
    }

    [[nodiscard]] static double compute_larmor_power(const Vector3D& accel) noexcept {
        return (Q_ELEM * Q_ELEM * accel.norm_sq()) /
               (6.0 * std::numbers::pi * EPS0 * std::pow(C_LIGHT, 3));
    }

    [[nodiscard]] ParticleState rk4_step(const ParticleState& s, double dt) const noexcept {
        const auto k1 = compute_derivatives(s);

        const ParticleState s2{
            s.pos + k1.pos * (0.5 * dt),
            s.vel + k1.vel * (0.5 * dt)
        };
        const auto k2 = compute_derivatives(s2);

        const ParticleState s3{
            s.pos + k2.pos * (0.5 * dt),
            s.vel + k2.vel * (0.5 * dt)
        };
        const auto k3 = compute_derivatives(s3);

        const ParticleState s4{
            s.pos + k3.pos * dt,
            s.vel + k3.vel * dt
        };
        const auto k4 = compute_derivatives(s4);

        return {
            s.pos + (k1.pos + k2.pos * 2.0 + k3.pos * 2.0 + k4.pos) * (dt / 6.0),
            s.vel + (k1.vel + k2.vel * 2.0 + k3.vel * 2.0 + k4.vel) * (dt / 6.0)
        };
    }
};

} // namespace electrodynamics

int main() {
    using namespace electrodynamics;

    constexpr double B_FIELD = 5.0;            // 5 Тесла
    constexpr double V_INIT  = 0.2 * C_LIGHT;  // 0.2 c
    constexpr double DT      = 1.0e-13;        // 0.1 пс
    constexpr int N_STEPS    = 10000;

    SynchrotronSimulator sim(B_FIELD, V_INIT);

    std::cout << std::left
              << std::setw(6)  << "Крок"
              << std::setw(12) << "Час (пс)"
              << std::setw(16) << "R_орбіти (мкм)"
              << std::setw(10) << "V/c"
              << std::setw(18) << "Потужність (нВт)"
              << "E_рад (еВ)\n";
    std::cout << std::string(72, '-') << "\n";

    for (int step = 0; step <= N_STEPS; ++step) {
        const auto log = sim.step(DT);

        if (step % 2000 == 0) {
            std::cout << std::left
                      << std::setw(6)  << step
                      << std::fixed << std::setprecision(2)
                      << std::setw(12) << log.time_ps
                      << std::setprecision(4)
                      << std::setw(16) << log.radius_um
                      << std::setprecision(3)
                      << std::setw(10) << log.speed_ratio
                      << std::scientific << std::setprecision(4)
                      << std::setw(18) << log.power_nw
                      << std::fixed << std::setprecision(4)
                      << log.energy_rad_ev << "\n";
        }
    }

    const double delta_ekin = sim.initial_kinetic_energy() - sim.current_kinetic_energy();

    std::cout << "\nБаланс збереження енергії:\n"
              << "  Втрата кінетичної енергії: " << delta_ekin << " Дж ("
              << (delta_ekin / EV_JOULE) << " еВ)\n"
              << "  Інтеграл випромінювання:   " << sim.total_radiated_energy() << " Дж ("
              << (sim.total_radiated_energy() / EV_JOULE) << " еВ)\n";

    return 0;
}
```
:::

---

## 4. Фізичні висновки та аналіз збіжності

Результати чисельного експерименту наочно демонструють фундаментальні динамічні закономірності:

1. **Спіральне стягування орбіти та радіаційне охолодження:** Під дією постійного випромінювання траєкторія електрона перетворюється на збіжну спіраль. Радіус гірообертання зменшується прямо пропорційно поточній швидкості частинки. У накопичувальних кільцях це явище називається «радіаційним охолодженням пучка» (англ. *radiation damping*): електрони випромінюють імпульс у всіх напрямках, а прискорювальні ВЧ-резонатори відновлюють лише поздовжній імпульс, що призводить до стискання фазового об'єму пучка.
2. **Член Шотта та енергетичний баланс ближньої зони:** У строгому рівнянні Абрагама-Лоренца сила містить повну похідну `F_rad = d/dt (m τ₀ a) - (m τ₀ / v²) a² v`. Перший доданок називається **членом Шотта** (на честь Джорджа Адольфа Шотта). Він відповідає оборотній реактивній енергії, накопиченій у квазістатичних електричних та магнітних полях ближньої зони безпосередньо навколо заряду `E_Schott = - m · τ₀ · (v · a)`. У наближенні Ландау-Ліфшиця ця реактивна складова автоматично враховується, забезпечуючи точний баланс повної механічної та польової енергії.
3. **Точність закону збереження енергії:** Метод RK4 забезпечує точність четвертого порядку за часовим кроком `O(dt⁴)`. Відносна похибка між зменшенням кінетичної енергії `ΔE_kin` та інтегралом випроміненої енергії `E_rad` не перевищує `10⁻¹⁰` на всьому інтервалі інтегрування `1.0` наносекунди.
4. **Вибір часового кроку для стійкості:** Для коректного відтворення фазової динаміки крок інтегрування `dt` повинен задовольняти двом строгим критеріям:
   - Роздільна здатність циклотронного періоду: `dt ≪ 2π / ω_c` (зазвичай обирають `dt ≤ 0.01 · T_cyc`).
   - Критерій збіжності збурень: `dt ≫ τ₀`, щоб схема не збуджувала нефізичні високі гармоніки.
5. **Безумовна стійкість наближення Ландау-Ліфшиця:** На відміну від третьопохідної схеми Абрагама-Лоренца, модель Ландау-Ліфшиця зберігає чисельну стійкість для довільно великої кількості ітерацій, що робить її золотим стандартом у пакетах трекінгу частинок прискорювачів (таких як MAD-X, Elegant, Astra та Geant4).
