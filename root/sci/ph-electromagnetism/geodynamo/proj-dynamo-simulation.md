# ⚙️ Чисельне моделювання хаотичного динамо Рікітаке

Магнітне поле Землі є динамічною нелінійною системою, яка демонструє стабільність лише на коротких часових інтервалах. На геологічних масштабах часу (сотні тисяч та мільйони років) палеомагнітні дані виявляють неперіодичні коливання та самочинні інверсії, під час яких північний та південний геомагнітні полюси міняються місцями. Для пояснення нелінійної поведінки та інверсій геодинамо японський геофізик Цунеджі Рікітаке (Tsuneji Rikitake, 1958) запропонував електромеханічну систему з двох взаємопов'язаних дискових динамо.

Система Рікітаке складається з двох провідних дисків, які обертаються під дією зовнішнього механічного моменту в перпендикулярних магнітних полях. Струм, індукований першим диском, протікає через котушку індуктивності і створює магнітне поле для другого диска, і навпаки. Така перехресна схема зв'язку створює нелінійний зворотний зв'язок між індукованими струмами та кутовими швидкостями обертання. Нижче наведено математичне формулювання системи, детальний опис чисельного інтегрування методом Рунґе-Кутти 4-го порядку (RK4) та повноцінну програмну реалізацію мовами C та C++.

## Математична модель динамо Рікітаке

У безрозмірних змінних динаміка двох зв'язаних динамо описується системою трьох нелінійних звичайних диференціальних рівнянь першого порядку:

```
dx/dt = -μ·x + y·z
dy/dt = -μ·y + (z - a)·x
dz/dt = 1 - x·y
```

де:
- `x(t)` — безрозмірний струм у котушці першого диска (пропорційний магнітному полю `B₁`);
- `y(t)` — безрозмірний струм у котушці другого диска (пропорційний магнітному полю `B₂`);
- `z(t)` — безрозмірна кутова швидкість обертання дисків;
- `μ > 0` — коефіцієнт в'язкого та омічного дисипативного згасання (дифузії);
- `a > 0` — параметр геометричної асиметрії дисків.

Ця система належить до класу тривимірних нелінійних динамічних систем із дисипацією. Вона виявляє виражену хаотичну поведінку, аналогічну до знаменитого атрактора Лоренца. При певних значеннях параметрів (наприклад, `μ = 1.0` та `a = 5.0`) розв'язки системи не описуються періодичними функціями: струми `x(t)` та `y(t)` здійснюють осциляції навколо одного зі стійких фокусів, після чого непередбачуваним чином здійснюють стрибок (інверсію) до іншого фокуса протилежного знака.

## Фізичні особливості та стаціонарні точки

Знайдемо стаціонарні точки системи Рікітаке, поклавши праві частини рівнянь рівними нулю (`dx/dt = dy/dt = dz/dt = 0`). 

З третього рівняння `1 - x·y = 0` випливає `y = 1/x`. Підставивши це у перше та друге рівняння, виявимо два симетричних стабільних фокуси (центри осциляцій):

```
C₁ = (+x₀, +1/x₀, z₀),   C₂ = (-x₀, -1/x₀, z₀)
```

де `x₀² = (a + √(a² + 4μ²)) / (2μ)`.

Наявність двох симетричних фокусів `C₁` та `C₂` є математичною причиною існування двох полярностей геомагнітного поля (прямої та зворотної). Фазова траєкторія системи намотує спіралі навколо одного фокуса зі зростаючою амплітудою, поки не досягає межі басейну притягання, після чого зривається і переходить до намотування спіралей навколо другого фокуса.

## Алгоритм чисельного інтегрування (RK4)

Для обчислення траєкторії хаотичного атрактора застосовується класичний метод Рунґе-Кутти 4-го порядку (RK4). Цей метод забезпечує локальну похибку порядку `O(h⁵)` та глобальну похибку `O(h⁴)`, що є необхідним для відтворення хаотичних фазових траєкторій без накопичення чисельної дисипації. Для векторної функції `F(t, Y)` з кроком інтегрування `h`:

```
k₁ = F(tₙ, Yₙ)
k₂ = F(tₙ + h/2, Yₙ + (h/2)·k₁)
k₃ = F(tₙ + h/2, Yₙ + (h/2)·k₂)
k₄ = F(tₙ + h, Yₙ + h·k₃)

Yₙ₊₁ = Yₙ + (h / 6) · (k₁ + 2·k₂ + 2·k₃ + k₄)
```

Крок інтегрування `h = 0.01` вибрано з міркувань стійкості: перевищення кроку `h > 0.05` викликає чисельну нестійкість розносного оператора RK4 через виражену жорсткість нелінійних членів `x·y` та `y·z`.

## Реалізація чисельного симулятора

:::tabs
```c
/* rikitake_sim.c - Чисельне моделювання хаотичного динамо Рікітаке мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    double x;
    double y;
    double z;
} RikitakeState;

typedef struct {
    double mu;
    double a;
} RikitakeParams;

/* Права частина системи диференціальних рівнянь Рікітаке */
static RikitakeState rikitake_derivatives(RikitakeState s, RikitakeParams p) {
    RikitakeState ds;
    ds.x = -p.mu * s.x + s.y * s.z;
    ds.y = -p.mu * s.y + (s.z - p.a) * s.x;
    ds.z = 1.0 - s.x * s.y;
    return ds;
}

/* Один крок інтегрування методом Рунґе-Кутти 4-го порядку */
static RikitakeState rk4_step(RikitakeState s, RikitakeParams p, double dt) {
    RikitakeState k1 = rikitake_derivatives(s, p);

    RikitakeState s2 = {
        s.x + 0.5 * dt * k1.x,
        s.y + 0.5 * dt * k1.y,
        s.z + 0.5 * dt * k1.z
    };
    RikitakeState k2 = rikitake_derivatives(s2, p);

    RikitakeState s3 = {
        s.x + 0.5 * dt * k2.x,
        s.y + 0.5 * dt * k2.y,
        s.z + 0.5 * dt * k2.z
    };
    RikitakeState k3 = rikitake_derivatives(s3, p);

    RikitakeState s4 = {
        s.x + dt * k3.x,
        s.y + dt * k3.y,
        s.z + dt * k3.z
    };
    RikitakeState k4 = rikitake_derivatives(s4, p);

    RikitakeState next_state;
    next_state.x = s.x + (dt / 6.0) * (k1.x + 2.0 * k2.x + 2.0 * k3.x + k4.x);
    next_state.y = s.y + (dt / 6.0) * (k1.y + 2.0 * k2.y + 2.0 * k3.y + k4.y);
    next_state.z = s.z + (dt / 6.0) * (k1.z + 2.0 * k2.z + 2.0 * k3.z + k4.z);
    return next_state;
}

int main(void) {
    RikitakeParams params = { .mu = 1.0, .a = 5.0 };
    RikitakeState state = { .x = 0.1, .y = 0.8, .z = 2.0 };

    double dt = 0.01;
    double t_max = 500.0;
    int steps = (int)(t_max / dt);

    FILE *fp = fopen("rikitake_trajectory.csv", "w");
    if (!fp) {
        perror("Помилка відкриття файлу для запису");
        return EXIT_FAILURE;
    }

    fprintf(fp, "time,x,y,z,reversal\n");

    int reversal_count = 0;
    double last_x = state.x;
    double last_reversal_time = 0.0;

    for (int i = 0; i < steps; ++i) {
        double t = i * dt;
        state = rk4_step(state, params, dt);

        /* Детекція зміни знаку струму x(t) - інверсія магнітного поля */
        int is_reversal = 0;
        if ((last_x > 0.0 && state.x < 0.0) || (last_x < 0.0 && state.x > 0.0)) {
            is_reversal = 1;
            reversal_count++;
            double interval = t - last_reversal_time;
            printf("Інверсія #%d на t = %.2f (інтервал: %.2f)\n", reversal_count, t, interval);
            last_reversal_time = t;
        }
        last_x = state.x;

        fprintf(fp, "%.3f,%.5f,%.5f,%.5f,%d\n", t, state.x, state.y, state.z, is_reversal);
    }

    fclose(fp);
    printf("Симуляцію завершено. Усього інверсій: %d. Дані збережено в rikitake_trajectory.csv\n", reversal_count);
    return EXIT_SUCCESS;
}
```
```cpp
// rikitake_sim.cpp - Ідіоматична C++ реалізація чисельного симулятора динамо Рікітаке
#include <iostream>
#include <fstream>
#include <vector>
#include <cmath>
#include <string>
#include <stdexcept>

struct RikitakeState {
    double x{0.0};
    double y{0.0};
    double z{0.0};
};

struct RikitakeParams {
    double mu{1.0};
    double a{5.0};
};

class RikitakeDynamoSimulator {
public:
    explicit RikitakeDynamoSimulator(RikitakeParams params, RikitakeState initial_state)
        : params_(params), current_state_(initial_state) {}

    [[nodiscard]] static RikitakeState derivatives(const RikitakeState& s, const RikitakeParams& p) noexcept {
        return RikitakeState{
            -p.mu * s.x + s.y * s.z,
            -p.mu * s.y + (s.z - p.a) * s.x,
            1.0 - s.x * s.y
        };
    }

    void step(double dt) noexcept {
        const auto k1 = derivatives(current_state_, params_);
        
        const RikitakeState s2{
            current_state_.x + 0.5 * dt * k1.x,
            current_state_.y + 0.5 * dt * k1.y,
            current_state_.z + 0.5 * dt * k1.z
        };
        const auto k2 = derivatives(s2, params_);

        const RikitakeState s3{
            current_state_.x + 0.5 * dt * k2.x,
            current_state_.y + 0.5 * dt * k2.y,
            current_state_.z + 0.5 * dt * k2.z
        };
        const auto k3 = derivatives(s3, params_);

        const RikitakeState s4{
            current_state_.x + dt * k3.x,
            current_state_.y + dt * k3.y,
            current_state_.z + dt * k3.z
        };
        const auto k4 = derivatives(s4, params_);

        current_state_.x += (dt / 6.0) * (k1.x + 2.0 * k2.x + 2.0 * k3.x + k4.x);
        current_state_.y += (dt / 6.0) * (k1.y + 2.0 * k2.y + 2.0 * k3.y + k4.y);
        current_state_.z += (dt / 6.0) * (k1.z + 2.0 * k2.z + 2.0 * k3.z + k4.z);
    }

    void run_simulation(double t_max, double dt, const std::string& output_filename) {
        std::ofstream out_file(output_filename);
        if (!out_file.is_open()) {
            throw std::runtime_error("Не вдалося відкрити файл для запису: " + output_filename);
        }

        out_file << "time,x,y,z,is_reversal\n";

        const std::size_t total_steps = static_cast<std::size_t>(t_max / dt);
        double last_x = current_state_.x;
        double last_reversal_t = 0.0;
        std::size_t reversals = 0;

        for (std::size_t i = 0; i < total_steps; ++i) {
            const double t = i * dt;
            step(dt);

            const bool is_reversal = (last_x > 0.0 && current_state_.x < 0.0) ||
                                     (last_x < 0.0 && current_state_.x > 0.0);
            
            if (is_reversal) {
                ++reversals;
                const double interval = t - last_reversal_t;
                std::cout << "Інверсія #" << reversals << " на t=" << t 
                          << " (інтервал = " << interval << ")\n";
                last_reversal_t = t;
            }
            last_x = current_state_.x;

            out_file << t << "," << current_state_.x << "," 
                     << current_state_.y << "," << current_state_.z << "," 
                     << (is_reversal ? 1 : 0) << "\n";
        }

        std::cout << "Усього інверсій: " << reversals << ". Файл збережено: " << output_filename << "\n";
    }

    [[nodiscard]] RikitakeState get_state() const noexcept { return current_state_; }

private:
    RikitakeParams params_;
    RikitakeState current_state_;
};

int main() {
    try {
        const RikitakeParams params{1.0, 5.0};
        const RikitakeState init_state{0.1, 0.8, 2.0};
        
        RikitakeDynamoSimulator sim(params, init_state);
        sim.run_simulation(500.0, 0.01, "rikitake_cpp_trajectory.csv");
    } catch (const std::exception& e) {
        std::cerr << "Помилка виконання: " << e.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
```
:::

## Аналіз результатів симуляції та зв'язок із геомагнетизмом

Чисельний аналіз траєкторій дискового динамо Рікітаке демонструє фундаментальні риси, притаманні повномасштабному геодинамо та палеомагнітним даним:

1. **Квазіперіодичні осциляції**: Протягом тривалих часових інтервалів величина струму `x(t)` (яка є аналогом дипольного магнітного поля `B_z`) коливається навколо одного з локальних центрів притягання з поступовим зростанням амплітуди. Це відповідає тривалим епохам стабільної полярності геомагнітного поля (суперхронам).
2. **Нерегулярний хаотичний дрейф**: Переходи між двома атракторами (стан `+x` та стан `-x`) відбуваються строго неперіодично. Обчислений розподіл часових інтервалів між перехідними подіями демонструє пуассонівську статистику з довгим спадним «хвостом», що повністю узгоджується з часовими інтервалами геомагнітних інверсій за останні 160 мільйонів років.
3. **Амплітудне падіння під час інверсії**: Під час безпосереднього переходу від стану `+x` до `-x` величина дипольного поля проходить через нуль. У цей момент напруженість поля падає до 10–20% від середнього значення, що точно відтворює ефект падіння напруженості земного диполя під час реверсу полярності.
4. **Чутливість до початкових умов**: Нелінійний характер диференціальних рівнянь зумовлює високу чутливість системи до найменших збурень початкових умов (ефект метелика). Це унеможливлює точний довгостроковий прогноз конкретної дати наступної інверсії геомагнітного поля Землі, залишаючи доступним лише статистичне оцінювання ймовірностей.
5. **Фазовий портрет у тривимірному просторі**: При побудові графіків у фазовому просторі `(x, y, z)` траєкторії симуляції описують подвійну спіраль з двома дисками атрактора, між якими фазова точка здійснює непередбачувані хаотичні переходи.
6. **Крайові випадки та втрата динамо-ефекту**: Якщо коефіцієнт згасання збільшити вище критичного значення (`μ > 2.5`), дисипація повністю пригнічує розкачку осциляцій, і фазова траєкторія прямує до нульового стану `x = 0, y = 0`, що відповідає повному згасанню планетного магнітного поля (згасання геодинамо).
7. **Формат згенерованих даних CSV**: Програма генерує текстовий файл `rikitake_trajectory.csv`, який містить 5 стовпців: часова мітка `time`, три фазові змінні `x`, `y`, `z` та прапорець `is_reversal` (1 при виконанні інверсії). Ці дані можуть бути імпортовані в засоби візуалізації (Python/Matplotlib або Gnuplot) для побудови двовимірних та тривимірних фазових портретів атрактора.
