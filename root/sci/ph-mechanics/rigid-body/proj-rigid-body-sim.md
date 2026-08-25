# ⚙️ Чисельне інтегрування рівнянь руху абсолютно твердого тіла

Чисельне моделювання динаміки тривимірного абсолютно твердого тіла є основою сучасних фізичних рушіїв у комп'ютерній графіці (PhysX, Bullet, Havok), робототехнічних симуляторах (MuJoCo, Gazebo) та автопілотах аерокосмічних апаратів. 

Головна задача чисельного інтегратора — за відомими зовнішніми силами `F` та моментами `M` обчислити часову еволюцію стану тіла з часом `t`, гарантуючи збереження фізичних інваріантів (енергії, моменту імпульсу та норми кватерніона орієнтації).

### 1. Фізична модель та вектор стану

Повний стан абсолютно твердого тіла у просторі описується 13-вимірним вектором стану `S`:

```
S = [ pos(3), vel(3), quat(4), omega(3) ]ᵀ
```

Вектор стану розбивається на дві відокремлені фізичні частини: поступальну динаміку центру мас у світовій системі координат та обертальну динаміку у власній зв'язаній системі координат тіла:

1. **Поступальний рух центру мас:**
   - Похідна позиції дорівнює поступальній швидкості: `d(pos)/dt = vel`.
   - Похідна швидкості за другим законом Ньютона дорівнює прискоренню: `d(vel)/dt = F_ext / Mass`, де `F_ext` — результуючий вектор зовнішніх сил у світовій системі координат.

2. **Обертальний рух навколо центру мас:**
   - Похідна одиничного кватерніона орієнтації `quat` визначається кватерніонним добутком на кутову швидкість: `d(quat)/dt = ½ · quat ⊗ (0, omega_body)`.
   - Похідна вектора кутової швидкості `omega_body` виражається з динамічних рівнянь Ейлера у власних осях: `d(omega_body)/dt = I⁻¹ · (M_body - omega_body × (I · omega_body))`, де `I` — діагональна матриця головних моментів інерції `diag(I_xx, I_yy, I_zz)`, а `M_body` — сумарний момент зовнішніх сил у зв'язаній системі.

Такий поділ є ключовим з огляду на обчислювальну продуктивність: використання власної системи координат для обертання робить матрицю інерції `I` сталою у часі й діагональною, що повністю усуває потребу виконувати коштовну процедуру обернення матриць 3×3 на кожному підкроці інтегрування.

Якщо зовнішні сили прикладені у точках `r_k` відносно центру мас у світовій системі, сумарний момент сил у власній системі тіла обчислюється як:

```
M_body = ∑ Rᵀ(q) · (r_k × F_k)     [перетворення зовнішніх моментів у систему тіла]
```

де `Rᵀ(q)` — транспонована матриця обертання, яка переводить вектори зі світової системи у зв'язану систему координат тіла.

### 2. Математичний механізм інтегрування методом Рунге-Кутти 4-го порядку (RK4)

Для розв'язання нелінійної системи диференціальних рівнянь `dS/dt = f(t, S)` застосовують метод Рунге-Кутти 4-го порядку (RK4). Метод досягає високої локальної точності `O(dt⁵)` завдяки обчисленню чотирьох проміжних взважених оцінок похідних на кожному проміжку часового кроку `dt`:

1. **Оцінка `k₁` на початку кроку:**
   Обчислюється вектор похідних `k₁ = f(t, S_t)` у початковому стані `S_t`. Він визначає стартовий нахил фазової траєкторії.
2. **Оцінка `k₂` на півкроці:**
   Стан пробна зсувається на середину інтервалу `S_k2 = S_t + 0.5 · dt · k₁`. Кватерніон стану обов'язково нормується `q = q / ||q||`. Обчислюється похідна `k₂ = f(t + 0.5·dt, S_k2)`.
3. **Оцінка `k₃` на півкроці за новим нахилом:**
   Стан пробна зсувається на середину інтервалу з використанням похідної `k₂`: `S_k3 = S_t + 0.5 · dt · k₂`. Кватерніон знову нормується, після чого обчислюється похідна `k₃ = f(t + 0.5·dt, S_k3)`.
4. **Оцінка `k₄` наприкінці кроку:**
   Стан зсувається на повний крок `S_k4 = S_t + dt · k₃`. Кватерніон нормується, обчислюється підсумкова похідна `k₄ = f(t + dt, S_k4)`.

Підсумковий стан розраховується як зважена середньозважена сума чотирьох оцінок:

```
S(t + dt) = S(t) + (dt / 6) · (k₁ + 2·k₂ + 2·k₃ + k₄)     [підсумковий крок RK4]
```

Обов'язковим завершальним етапом після обчислення `S(t + dt)` є примусове нормування кватерніона орієнтації `q = q / ||q||`, що гарантує збереження ортогональності базису й запобігає геометричним деформаціям 3D-об'єкта.

### 3. Двомовна реалізація чисельного інтегратора (C та C++)

Нижче наведено повністю працездатні реалізації фізичного інтегратора тривимірного твердого тіла мовами C та C++.

:::tabs
```c
/* C Implementation: 3D Rigid Body RK4 Physics Integrator */
#include <stdio.h>
#include <math.h>

typedef struct {
    double x, y, z;
} Vec3;

typedef struct {
    double w, x, y, z;
} Quat;

typedef struct {
    Vec3 pos;       /* Позиція центру мас у світі (m) */
    Vec3 vel;       /* Поступальна швидкість у світі (m/s) */
    Quat quat;      /* Орієнтація у вигляді одиничного кватерніона */
    Vec3 omega;     /* Кутова швидкість у власних осях тіла (rad/s) */
} RigidBodyState;

typedef struct {
    double mass;    /* Маса тіла (kg) */
    Vec3 I_diag;    /* Головні моменти інерції (I_xx, I_yy, I_zz) (kg·m²) */
} RigidBodyProps;

typedef struct {
    Vec3 force_world;   /* Зовнішня сила у світовій системі (N) */
    Vec3 torque_body;   /* Зовнішній момент у власній системі (N·m) */
} ExternalInputs;

typedef struct {
    Vec3 d_pos;
    Vec3 d_vel;
    Quat d_quat;
    Vec3 d_omega;
} StateDeriv;

/* Операції над векторами */
static inline Vec3 vec3_add(Vec3 a, Vec3 b) {
    return (Vec3){a.x + b.x, a.y + b.y, a.z + b.z};
}

static inline Vec3 vec3_scale(Vec3 v, double s) {
    return (Vec3){v.x * s, v.y * s, v.z * s};
}

static inline Vec3 vec3_cross(Vec3 a, Vec3 b) {
    return (Vec3){
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
}

/* Нормування кватерніона для запобігання чисельному дрейфу */
static inline Quat quat_normalize(Quat q) {
    double len = sqrt(q.w * q.w + q.x * q.x + q.y * q.y + q.z * q.z);
    if (len < 1e-12) return (Quat){1.0, 0.0, 0.0, 0.0};
    return (Quat){q.w / len, q.x / len, q.y / len, q.z / len};
}

/* Добуток кватерніона на кватерніон кутової швидкості (0, w_x, w_y, w_z) */
static inline Quat quat_deriv(Quat q, Vec3 w) {
    return (Quat){
        0.5 * (-q.x * w.x - q.y * w.y - q.z * w.z),
        0.5 * ( q.w * w.x + q.y * w.z - q.z * w.y),
        0.5 * ( q.w * w.y + q.z * w.x - q.x * w.z),
        0.5 * ( q.w * w.z + q.x * w.y - q.y * w.x)
    };
}

/* Обчислення похідних стану dS/dt */
StateDeriv compute_derivatives(const RigidBodyState *s, const RigidBodyProps *props, const ExternalInputs *in) {
    StateDeriv d;
    d.d_pos = s->vel;
    d.d_vel = vec3_scale(in->force_world, 1.0 / props->mass);
    d.d_quat = quat_deriv(s->quat, s->omega);

    /* Рівняння руху Ейлера: I · dω/dt = M - ω × (I · ω) */
    Vec3 Iw = {
        props->I_diag.x * s->omega.x,
        props->I_diag.y * s->omega.y,
        props->I_diag.z * s->omega.z
    };
    Vec3 gyro_torque = vec3_cross(s->omega, Iw);
    Vec3 net_torque = {
        in->torque_body.x - gyro_torque.x,
        in->torque_body.y - gyro_torque.y,
        in->torque_body.z - gyro_torque.z
    };

    d.d_omega = (Vec3){
        net_torque.x / props->I_diag.x,
        net_torque.y / props->I_diag.y,
        net_torque.z / props->I_diag.z
    };
    return d;
}

/* Інтегрування одного кроку за допомогою RK4 */
void rigid_body_step_rk4(RigidBodyState *state, const RigidBodyProps *props, const ExternalInputs *in, double dt) {
    StateDeriv k1 = compute_derivatives(state, props, in);

    RigidBodyState s_k2 = *state;
    s_k2.pos = vec3_add(state->pos, vec3_scale(k1.d_pos, dt * 0.5));
    s_k2.vel = vec3_add(state->vel, vec3_scale(k1.d_vel, dt * 0.5));
    s_k2.quat.w += k1.d_quat.w * dt * 0.5;
    s_k2.quat.x += k1.d_quat.x * dt * 0.5;
    s_k2.quat.y += k1.d_quat.y * dt * 0.5;
    s_k2.quat.z += k1.d_quat.z * dt * 0.5;
    s_k2.quat = quat_normalize(s_k2.quat);
    s_k2.omega = vec3_add(state->omega, vec3_scale(k1.d_omega, dt * 0.5));
    StateDeriv k2 = compute_derivatives(&s_k2, props, in);

    RigidBodyState s_k3 = *state;
    s_k3.pos = vec3_add(state->pos, vec3_scale(k2.d_pos, dt * 0.5));
    s_k3.vel = vec3_add(state->vel, vec3_scale(k2.d_vel, dt * 0.5));
    s_k3.quat.w += k2.d_quat.w * dt * 0.5;
    s_k3.quat.x += k2.d_quat.x * dt * 0.5;
    s_k3.quat.y += k2.d_quat.y * dt * 0.5;
    s_k3.quat.z += k2.d_quat.z * dt * 0.5;
    s_k3.quat = quat_normalize(s_k3.quat);
    s_k3.omega = vec3_add(state->omega, vec3_scale(k2.d_omega, dt * 0.5));
    StateDeriv k3 = compute_derivatives(&s_k3, props, in);

    RigidBodyState s_k4 = *state;
    s_k4.pos = vec3_add(state->pos, vec3_scale(k3.d_pos, dt));
    s_k4.vel = vec3_add(state->vel, vec3_scale(k3.d_vel, dt));
    s_k4.quat.w += k3.d_quat.w * dt;
    s_k4.quat.x += k3.d_quat.x * dt;
    s_k4.quat.y += k3.d_quat.y * dt;
    s_k4.quat.z += k3.d_quat.z * dt;
    s_k4.quat = quat_normalize(s_k4.quat);
    s_k4.omega = vec3_add(state->omega, vec3_scale(k3.d_omega, dt));
    StateDeriv k4 = compute_derivatives(&s_k4, props, in);

    /* Оновлення стану: S_{t+dt} = S_t + (dt/6) * (k1 + 2*k2 + 2*k3 + k4) */
    state->pos.x += (dt / 6.0) * (k1.d_pos.x + 2.0 * k2.d_pos.x + 2.0 * k3.d_pos.x + k4.d_pos.x);
    state->pos.y += (dt / 6.0) * (k1.d_pos.y + 2.0 * k2.d_pos.y + 2.0 * k3.d_pos.y + k4.d_pos.y);
    state->pos.z += (dt / 6.0) * (k1.d_pos.z + 2.0 * k2.d_pos.z + 2.0 * k3.d_pos.z + k4.d_pos.z);

    state->vel.x += (dt / 6.0) * (k1.d_vel.x + 2.0 * k2.d_vel.x + 2.0 * k3.d_vel.x + k4.d_vel.x);
    state->vel.y += (dt / 6.0) * (k1.d_vel.y + 2.0 * k2.d_vel.y + 2.0 * k3.d_vel.y + k4.d_vel.y);
    state->vel.z += (dt / 6.0) * (k1.d_vel.z + 2.0 * k2.d_vel.z + 2.0 * k3.d_vel.z + k4.d_vel.z);

    state->quat.w += (dt / 6.0) * (k1.d_quat.w + 2.0 * k2.d_quat.w + 2.0 * k3.d_quat.w + k4.d_quat.w);
    state->quat.x += (dt / 6.0) * (k1.d_quat.x + 2.0 * k2.d_quat.x + 2.0 * k3.d_quat.x + k4.d_quat.x);
    state->quat.y += (dt / 6.0) * (k1.d_quat.y + 2.0 * k2.d_quat.y + 2.0 * k3.d_quat.y + k4.d_quat.y);
    state->quat.z += (dt / 6.0) * (k1.d_quat.z + 2.0 * k2.d_quat.z + 2.0 * k3.d_quat.z + k4.d_quat.z);
    state->quat = quat_normalize(state->quat);

    state->omega.x += (dt / 6.0) * (k1.d_omega.x + 2.0 * k2.d_omega.x + 2.0 * k3.d_omega.x + k4.d_omega.x);
    state->omega.y += (dt / 6.0) * (k1.d_omega.y + 2.0 * k2.d_omega.y + 2.0 * k3.d_omega.y + k4.d_omega.y);
    state->omega.z += (dt / 6.0) * (k1.d_omega.z + 2.0 * k2.d_omega.z + 2.0 * k3.d_omega.z + k4.d_omega.z);
}

int main(void) {
    RigidBodyState state = {
        .pos = {0.0, 0.0, 10.0},
        .vel = {0.0, 0.0, 0.0},
        .quat = {1.0, 0.0, 0.0, 0.0},
        .omega = {1.0, 20.0, 0.1} /* Обертання навколо проміжної осі y (нестійке) */
    };

    RigidBodyProps props = {
        .mass = 2.0,
        .I_diag = {1.0, 2.0, 3.0} /* I_xx < I_yy < I_zz */
    };

    ExternalInputs in = {
        .force_world = {0.0, 0.0, -9.81 * 2.0}, /* Сила тяжіння */
        .torque_body = {0.0, 0.0, 0.0}          /* Вільне обертання */
    };

    double dt = 0.001;
    printf("Крок\t Час (s)\t Z-Позиція\t Omega_X\t Omega_Y\t Omega_Z\n");
    for (int step = 0; step <= 2000; step++) {
        if (step % 200 == 0) {
            printf("%d\t %.3f\t %.3f\t\t %.3f\t %.3f\t %.3f\n",
                   step, step * dt, state.pos.z, state.omega.x, state.omega.y, state.omega.z);
        }
        rigid_body_step_rk4(&state, &props, &in, dt);
    }
    return 0;
}
```
```cpp
// C++ Implementation: Object-Oriented 3D Rigid Body Simulator
#include <iostream>
#include <array>
#include <cmath>
#include <iomanip>

namespace physics {

struct Vec3 {
    double x{0.0}, y{0.0}, z{0.0};

    constexpr Vec3 operator+(const Vec3& o) const { return {x + o.x, y + o.y, z + o.z}; }
    constexpr Vec3 operator-(const Vec3& o) const { return {x - o.x, y - o.y, z - o.z}; }
    constexpr Vec3 operator*(double s) const { return {x * s, y * s, z * s}; }

    constexpr Vec3 cross(const Vec3& o) const {
        return {
            y * o.z - z * o.y,
            z * o.x - x * o.z,
            x * o.y - y * o.x
        };
    }
};

struct Quat {
    double w{1.0}, x{0.0}, y{0.0}, z{0.0};

    [[nodiscard]] Quat normalized() const {
        double len = std::sqrt(w * w + x * x + y * y + z * z);
        if (len < 1e-12) return {1.0, 0.0, 0.0, 0.0};
        return {w / len, x / len, y / len, z / len};
    }

    [[nodiscard]] Quat derivative(const Vec3& w_vec) const {
        return {
            0.5 * (-x * w_vec.x - y * w_vec.y - z * w_vec.z),
            0.5 * ( w * w_vec.x + y * w_vec.z - z * w_vec.y),
            0.5 * ( w * w_vec.y + z * w_vec.x - x * w_vec.z),
            0.5 * ( w * w_vec.z + x * w_vec.y - y * w_vec.x)
        };
    }
};

struct RigidBodyState {
    Vec3 pos{};
    Vec3 vel{};
    Quat quat{};
    Vec3 omega{};

    RigidBodyState operator+(const RigidBodyState& d) const {
        return {
            pos + d.pos,
            vel + d.vel,
            {quat.w + d.quat.w, quat.x + d.quat.x, quat.y + d.quat.y, quat.z + d.quat.z},
            omega + d.omega
        };
    }

    RigidBodyState scale(double dt) const {
        return {
            pos * dt,
            vel * dt,
            {quat.w * dt, quat.x * dt, quat.y * dt, quat.z * dt},
            omega * dt
        };
    }
};

struct MassProperties {
    double mass{1.0};
    Vec3 inertia_diag{1.0, 1.0, 1.0};
};

class RigidBody {
public:
    RigidBody(MassProperties props, RigidBodyState initial_state)
        : props_(props), state_(initial_state) {}

    void step_rk4(Vec3 force_world, Vec3 torque_body, double dt) {
        auto compute_deriv = [this, &force_world, &torque_body](const RigidBodyState& s) -> RigidBodyState {
            Vec3 d_pos = s.vel;
            Vec3 d_vel = force_world * (1.0 / props_.mass);
            Quat d_quat = s.quat.derivative(s.omega);

            Vec3 Iw{
                props_.inertia_diag.x * s.omega.x,
                props_.inertia_diag.y * s.omega.y,
                props_.inertia_diag.z * s.omega.z
            };
            Vec3 gyro = s.omega.cross(Iw);
            Vec3 net_torque = torque_body - gyro;

            Vec3 d_omega{
                net_torque.x / props_.inertia_diag.x,
                net_torque.y / props_.inertia_diag.y,
                net_torque.z / props_.inertia_diag.z
            };
            return {d_pos, d_vel, d_quat, d_omega};
        };

        RigidBodyState k1 = compute_deriv(state_);

        RigidBodyState s2 = state_ + k1.scale(dt * 0.5);
        s2.quat = s2.quat.normalized();
        RigidBodyState k2 = compute_deriv(s2);

        RigidBodyState s3 = state_ + k2.scale(dt * 0.5);
        s3.quat = s3.quat.normalized();
        RigidBodyState k3 = compute_deriv(s3);

        RigidBodyState s4 = state_ + k3.scale(dt);
        s4.quat = s4.quat.normalized();
        RigidBodyState k4 = compute_deriv(s4);

        RigidBodyState step_change = (k1 + (k2.scale(2.0)) + (k3.scale(2.0)) + k4).scale(dt / 6.0);
        state_ = state_ + step_change;
        state_.quat = state_.quat.normalized();
    }

    [[nodiscard]] const RigidBodyState& state() const { return state_; }

private:
    MassProperties props_;
    RigidBodyState state_;
};

} // namespace physics

int main() {
    using namespace physics;

    MassProperties props{
        .mass = 2.0,
        .inertia_diag = {1.0, 2.0, 3.0}
    };

    RigidBodyState init_state{
        .pos = {0.0, 0.0, 10.0},
        .vel = {0.0, 0.0, 0.0},
        .quat = {1.0, 0.0, 0.0, 0.0},
        .omega = {1.0, 20.0, 0.1}
    };

    RigidBody body(props, init_state);
    Vec3 gravity{0.0, 0.0, -9.81 * 2.0};
    Vec3 zero_torque{0.0, 0.0, 0.0};
    double dt = 0.001;

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Time(s)\t Z-Pos\t\t Omega_X\t Omega_Y\t Omega_Z\n";

    for (int step = 0; step <= 2000; ++step) {
        if (step % 200 == 0) {
            const auto& s = body.state();
            std::cout << step * dt << "\t " << s.pos.z << "\t\t "
                      << s.omega.x << "\t " << s.omega.y << "\t " << s.omega.z << "\n";
        }
        body.step_rk4(gravity, zero_torque, dt);
    }
    return 0;
}
```
:::

### 4. Поглиблений розбір крайових випадків та інженерні рішення

При практичному впровадженні чисельного інтегратора тривимірної динаміки виникає низка специфічних обчислювальних проблем, виправлення яких вимагає чітких інженерних рішень:

#### 1. Чисельний дрейф норми кватерніона (Quaternion Drift)

Метод Рунге-Кутти додає похідні кватерніона скалярно. У результаті дискретизації квадрат евклідової норми кватерніона `||q||² = w² + x² + y² + z²` поступово відхиляється від 1.0. Якщо це відхилення не виправляти, матриця обертання `R(q)` втрачає ортогональність (`Rᵀ R ≠ I`), що візуально призводить до спотворення об'єкта у 3D-просторі (він починає нефізично розтягуватися чи стискатися).

*Інженерне рішення:* Обов'язкове вирівнювання норми кватерніона `q = q / ||q||` після кожного проміжного зсуву `k_i` у методі RK4 та наприкінці кожного підсумкового кроку.

#### 2. Вибір часового кроку `dt` та нестійкість за високих частот

Якщо кутова швидкість обертання тіла `||omega||` є дуже великою (наприклад, для роторів турбін або швидкорозкручених гіроскопів), період одного оберту `T = 2π / ||omega||` стає порівнянним із кроком симулятора `dt`. У цих умовах явний метод RK4 втрачає чисельну стійкість і починає підкачувати штучну кінетичну енергію, примушуючи рішення спрямовуватися до нескінченності.

*Інженерне рішення:* Крок інтегрування за часом мусить відповідати критичній умові стійкості `dt < 0.1 / ||omega_max||`. Для об'єктів із широким діапазоном швидкостей застосовують адаптивний вибір кроку за методом Рунге-Кутти-Фельберга (RKF45) або субінтегрування (Sub-stepping).

#### 3. Демонстрація нестійкості проміжної осі у виводі програми

У тестовому розрахунку `main()` початкова кутова швидкість задана переважно вздовж другої осі `omega = (1.0, 20.0, 0.1)` при моменті інерції `I = (1.0, 2.0, 3.0)`. Запустивши згенеровану програму, можна безпосередньо спостерігати чисельне втілення ефекту Джанібекова: компонента `Omega_Y` залишається близькою до 20.0 протягом перших кроків, після чого швидко спадає до нуля, а `Omega_X` та `Omega_Z` вибухово зростають, демонструючи регулярне перекидання тіла на 180 градусів у просторі.

#### 4. Порівняння з симплектичними інтеграторами

Класичний метод RK4 є явним інтегратором високої точності, але він не зберігає фазовий об'єм системи (не є симплектичним). При тривалому аерокосмічному моделюванні обертання астероїдів чи космічних апаратів протягом мільйонів кроків RK4 буде повільно накопичувати помилку збереження повної кінетичної енергії.

Для астродинамічних задач без опору середовища застосовують спеціальні **симплектичні інтегратори на групах Лі** (Lie group integrators або Symplectic Euler/Verlet), які будуються безпосередньо на геометричному многовиді групи `SO(3)`.
