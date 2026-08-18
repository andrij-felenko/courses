# ⚙️ Симуляція авторегулювання витягування та діаметра бульби

Ця вставка містить програмну реалізацію контуру зворотного зв'язку (ПІД-регулятора) для автоматичного управління швидкістю витягування монокристала та потужністю нагрівача печі Чохральського, що забезпечує підтримку сталого діаметра зливка кремнію на основі оптичних вимірювань меніска.

## Принцип автоматичного регулювання діаметра зливка

Вирощування монокристала кремнію діаметром 300 мм вимагає підтримки цільового радіуса `R_target` з точністю до `±0.5 мм` протягом 48–72 годин безперервного процесу. Устаткування працює у складних умовах нелінійної теплодинаміки та значної часової затримки відгуку на керуючі впливи.

Основними керуючими впливами у замкненому контурі є:
1. **Швидкість витягування `v_p`**: Збільшення швидкості витягування призводить до зменшення діаметра зливка, оскільки пришвидшене підняття фронту кристалізації зменшує час, протягом якого рідкий меніск встигає відводити теплоту кристалізації. Навпаки, зменшення швидкості витягування розширює ростучу бульбу.
2. **Потужність нагрівача `P_heat`**: Збільшення температури розплаву зменшує діаметр кристала через підплавлення міжфазної межі, а зниження температури нагрівача знижує температуру рідкого кремнію і прискорює кристалізацію.

Система керування отримує від оптичної CCD-камери поточне значення радіуса кристала `R_meas` та кута меніска `phi_meas`, обчислює відхилення від заданої траєкторії та коригує швидкість штока витягування і струм нагрівача.

Аналітичне рівняння помилки радіуса `e(t) = R_target - R_meas(t)` використовується для формування пропорційної, інтегральної та диференціальної складових керуючого сигналу:

```
u(t) = K_p · e(t) + K_i · ∫ e(τ) dτ + K_d · (de(t) / dt)
```

де `K_p` — пропорційний коефіцієнт підсилення, `K_i` — інтегральний коефіцієнт (усуває статичну помилку та компенсує поступову зміну рівня розплаву у тиглі), `K_d` — диференційний коефіцієнт (парує швидкі коливання та згладжує махові відхилення).

Фізичний зв'язок між швидкістю витягування `v_p` та зміною радіуса кристала `dR / dt` описується кінетичним рівнянням балансу маси на фронті кристалізації:

```
dR / dt = (v_p - v_target) · tan(φ - φ_0)
```

де `φ` — поточний кут нахилу рідкого меніска біля межі трифазного контакту, `φ_0 ≈ 11°` — характерний рівноважний кут росту кремнію. Якщо `φ = φ_0`, кут нахилу меніска відповідає строго циліндричному росту `dR / dt = 0`.

## Фільтрація вимірювальних шумів та Калманівська обробка

Оптичний сигнал від CCD-камери, націленої на якразне кільце меніска, піддається інтенсивному зашумленню через відблиски на поверхні розплаву, пульсації хвилювання та теплові коливання газового середовища. Пряме використання сирого сигналу `R_raw(t)` у ПІД-контролері викликало б хаотичні стрибки швидкості витягування, що призвело б до розмноження дислокацій.

Для очищення вимірювального сигналу перед передачею в алгоритм керування застосовується одновимірний фільтр Калмана або ковзна медіанна фільтрація. Фільтр Калмана оцінює істинний радіус `R_est` та швидкість його зміни `dR_est / dt` на основі подвійної моделі стану:

```
R_est(k) = R_est(k-1) + dt · dR_est(k-1)
dR_est(k) = dR_est(k-1) + K_kalman · (R_raw(k) - R_est(k))
```

де `K_kalman` — матричний коефіцієнт підсилення Калмана, що обчислюється на основі співвідношення дисперсії шуму вимірювань оптичної камери та дисперсії фізичних збурень розплаву.

## Програмна реалізація контролера у трьох мовах

Нижче наведено три ідіоматичні реалізації чисельної симуляції ПІД-контролера діаметра бульби монокристала для печі Чохральського мовами C++, C та Python.

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <optional>

// Параметри теплового режиму печі та кристала
struct ProcessParams {
    double target_radius_m{0.150};    // Цільовий радіус зливка (150 мм = Ø 300 мм)
    double target_pull_rate_mps{2.0e-5}; // Базова швидкість витягування (1.2 мм/хв)
    double melt_temp_k{1690.0};       // Базова температура розплаву
    double latent_heat_j_kg{1.8e6};   // Прихована теплота плавлення Si
    double density_solid_kg_m3{2330.0}; // Густина твердого Si
    double thermal_cond_solid{22.0};  // Теплопровідність твердого Si (Вт/м·К)
};

// Стан контуру регулювання (ПІД)
class CzochralskiController {
public:
    explicit CzochralskiController(ProcessParams params)
        : params_(params), integral_err_(0.0), prev_err_(0.0) {}

    struct ControlOutput {
        double pull_rate_mps; // Скоригована швидкість витягування (м/с)
        double heater_power_kw; // Скоригована потужність нагрівача (кВт)
    };

    // Оновлення стану контролера за один крок часу dt
    [[nodiscard]] ControlOutput update(double measured_radius_m, double dt_sec) {
        const double error = params_.target_radius_m - measured_radius_m;
        integral_err_ += error * dt_sec;
        const double derivative_err = (error - prev_err_) / dt_sec;
        prev_err_ = error;

        // ПІД-коефіцієнти для швидкості витягування
        constexpr double Kp_v = 3.0e-4;
        constexpr double Ki_v = 1.0e-5;
        constexpr double Kd_v = 5.0e-5;

        // Відхилення від цільового радіуса коригує швидкість у протилежному напрямку:
        // якщо R занадто великий (error < 0), збільшуємо швидкість витягування.
        const double delta_v = -(Kp_v * error + Ki_v * integral_err_ + Kd_v * derivative_err);
        
        // Обмеження допустимої швидкості витягування (безпечний діапазон 0.2 .. 4.0 мм/хв)
        constexpr double min_pull = 0.33e-5; // ~0.2 мм/хв
        constexpr double max_pull = 6.67e-5; // ~4.0 мм/хв
        const double pull_rate = std::clamp(params_.target_pull_rate_mps + delta_v, min_pull, max_pull);

        // Розрахунок теплового балансу для визначення потрібної потужності
        // Q_solid = k_S * dT/dz = Q_melt + L_m * rho_S * v_p
        const double area = M_PI * measured_radius_m * measured_radius_m;
        const double latent_power_w = params_.latent_heat_j_kg * params_.density_solid_kg_m3 * area * pull_rate;
        const double base_heater_kw = 85.0; // 85 кВт базова потужність
        
        // Коригування потужності нагрівача: якщо кристал тоншає (error > 0), зменшуємо нагрів
        constexpr double Kp_p = 120.0;
        const double heater_kw = std::clamp(base_heater_kw - Kp_p * error, 50.0, 150.0);

        return ControlOutput{pull_rate, heater_kw};
    }

private:
    ProcessParams params_;
    double integral_err_;
    double prev_err_;
};

int main() {
    ProcessParams params{};
    CzochralskiController controller(params);

    std::cout << "--- Симуляція ПІД-контролера печі Чохральського ---\n";
    std::cout << "Час (хв) | Виміряний Ø (мм) | Швидкість v_p (мм/хв) | Потужність P (кВт)\n";

    double radius = 0.142; // Початковий радіус (142 мм замість 150 мм — зливок тонший)
    constexpr double dt = 5.0; // Крок симуляції 5 секунд

    for (int step = 0; step <= 24; ++step) {
        const double time_min = step * (dt / 60.0);
        const auto [v_p, p_kw] = controller.update(radius, dt);

        std::cout << time_min << " хв | "
                  << (radius * 2000.0) << " мм | "
                  << (v_p * 60000.0) << " мм/хв | "
                  << p_kw << " кВт\n";

        // Проста фізична модель динаміки радіуса під впливом v_p
        const double v_target = params.target_pull_rate_mps;
        radius += (v_target - v_p) * 0.05 * dt; // Зміна радіуса
    }
    return 0;
}
```
```c
#include <stdio.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double target_radius_m;
    double target_pull_rate_mps;
    double latent_heat_j_kg;
    double density_solid_kg_m3;
} ProcessParamsC;

typedef struct {
    ProcessParamsC params;
    double integral_err;
    double prev_err;
} CzochralskiControllerC;

typedef struct {
    double pull_rate_mps;
    double heater_power_kw;
} ControlOutputC;

void controller_init(CzochralskiControllerC *ctrl, ProcessParamsC params) {
    ctrl->params = params;
    ctrl->integral_err = 0.0;
    ctrl->prev_err = 0.0;
}

ControlOutputC controller_update(CzochralskiControllerC *ctrl, double measured_radius_m, double dt_sec) {
    double error = ctrl->params.target_radius_m - measured_radius_m;
    ctrl->integral_err += error * dt_sec;
    double derivative_err = (error - ctrl->prev_err) / dt_sec;
    ctrl->prev_err = error;

    double Kp_v = 3.0e-4;
    double Ki_v = 1.0e-5;
    double Kd_v = 5.0e-5;

    double delta_v = -(Kp_v * error + Ki_v * ctrl->integral_err + Kd_v * derivative_err);
    double pull_rate = ctrl->params.target_pull_rate_mps + delta_v;

    if (pull_rate < 0.33e-5) pull_rate = 0.33e-5;
    if (pull_rate > 6.67e-5) pull_rate = 6.67e-5;

    double Kp_p = 120.0;
    double heater_kw = 85.0 - Kp_p * error;
    if (heater_kw < 50.0) heater_kw = 50.0;
    if (heater_kw > 150.0) heater_kw = 150.0;

    ControlOutputC out = { pull_rate, heater_kw };
    return out;
}

int main(void) {
    ProcessParamsC params = { 0.150, 2.0e-5, 1.8e6, 2330.0 };
    CzochralskiControllerC ctrl;
    controller_init(&ctrl, params);

    printf("--- C Симуляція ПІД-контролера Чохральського ---\n");
    double radius = 0.142;
    double dt = 5.0;

    for (int step = 0; step <= 20; ++step) {
        double time_min = step * (dt / 60.0);
        ControlOutputC out = controller_update(&ctrl, radius, dt);

        printf("%.1f хв | Ø %.2f мм | v_p %.3f мм/хв | P %.1f кВт\n",
               time_min, radius * 2000.0, out.pull_rate_mps * 60000.0, out.heater_power_kw);

        radius += (params.target_pull_rate_mps - out.pull_rate_mps) * 0.05 * dt;
    }
    return 0;
}
```
```py
import math

class CzochralskiSimulator:
    def __init__(self, target_radius_mm=150.0, target_pull_rate_mm_min=1.2):
        self.target_r = target_radius_mm
        self.target_vp = target_pull_rate_mm_min / 60.0  # мм/с
        self.integral_err = 0.0
        self.prev_err = 0.0

    def step(self, measured_r_mm, dt_s=5.0):
        err = self.target_r - measured_r_mm
        self.integral_err += err * dt_s
        deriv_err = (err - self.prev_err) / dt_s
        self.prev_err = err

        # Коефіцієнти ПІД
        kp, ki, kd = 0.02, 0.0005, 0.003
        delta_vp = -(kp * err + ki * self.integral_err + kd * deriv_err)
        
        vp_mm_s = max(0.1 / 60.0, min(4.0 / 60.0, self.target_vp + delta_vp))
        heater_power_kw = max(50.0, min(150.0, 85.0 - 0.25 * err))

        return vp_mm_s * 60.0, heater_power_kw  # мм/хв, кВт

def main():
    sim = CzochralskiSimulator(target_radius_mm=150.0, target_pull_rate_mm_min=1.2)
    radius = 142.0  # Початковий діаметр 284 мм замість 300 мм
    print("--- Python симуляція контролю діаметра зливка Si ---")
    print("Час (хв) | Діаметр (мм) | v_p (мм/хв) | Потужність (кВт)")

    for t_step in range(21):
        t_min = t_step * 5.0 / 60.0
        vp_mm_min, power_kw = sim.step(radius, dt_s=5.0)
        print(f"{t_min:5.1f} хв | Ø {radius * 2:6.2f} мм | v_p {vp_mm_min:5.3f} мм/хв | P {power_kw:5.1f} кВт")
        radius += (1.2 - vp_mm_min) * 0.15

if __name__ == "__main__":
    main()
```
:::

## Аналіз стійкості замкненого контуру та крайові випадки

У реальній промисловій установці Чохральського передавальна функція об'єкта управління володіє істотним транспортним запізненням (порядок 30–90 секунд), пов'язаним із тепловою інерцією масивного графітового нагрівача та розплаву об'ємом понад 150 літрів. Для запобігання автоколиванням діаметра (ефект «гофрування» бічної поверхні зливка) у сучасних печах застосовується каскадне управління: швидкий внутрішній контур регулює швидкість витягування `v_p`, а повільний зовнішній контур плавно коригує потужність нагрівача `P_heat`.

Для забезпечення математичної стійкості каскадної системи передавальна функція розраховується у частотній області на основі критерію Найквіста-Боде. Запас по фазі формується на рівні не менше `45°`, а запас по амплітуді — не менше `6 дБ`. Це унеможливлює виникнення незгасаючих резонансних коливань при різких коливаннях напруги в живильній електромережі.

Крайові випадки та аварійні ситуації у контурі регулювання:

1. **Раптовий дислокаційний збій (Loss of Structure, LOS)**:
   При зародженні дислокації прихована теплота починає виділятися нерівномірно, а кут контакту меніска змінюється через втрату граней росту. Оптична система фіксує зникнення чітких світлових ребер («пелюсток» або граней `<100>`). При зафіксованому LOS алгоритм автоматично припиняє стаціонарне витягування, піднімає температуру розплаву, сплавляє дефектну ділянку зливка назад у розплав та повторно витягує шийку Деша.

2. **Замерзання дзеркала розплаву**:
   Якщо температура нагрівача впаде нижче критичної `1418 °C`, на поверхні розплаву утворюється суцільна кристалічна кірка. Щоб запобігти зрізанню витяжної вежі чи обриву штока, система автоматично переходить у аварійний режим «Thermal Flush», вимикає швидкісне витягування і подає імпульс підвищеної потужності на нагрівальні елементи.

3. **Вичерпання розплаву у тиглі**:
   У міру зменшення об'єму рідкого кремнію рівень розплаву знижується відносно нагрівальних елементів. Система автоматичного регулювання компенсує це підйомом тигля зі швидкістю `v_crucible = v_p · (D_crystal / D_crucible)²`. Якщо висота підйому досягає механічного кінцевого вимикача, контролер ініціює фінальну стадію звуження конуса хвоста (tail-off).

4. **Аварійне знеструмлення або збій системи охолодження**:
   При зупинці циркуляції охолоджувальної води у сорочці вакуумної камери або збої живлення нагрівача алгоритм контролера негайно переводить шток у режим швидкісного підйому для відриву кристала від розплаву до його повного застигання, запобігаючи руйнуванню вакуумної камери при розширенні кремнію під час замерзання (густина рідкого кремнію більша за твердий, тому кремній розширюється при кристалізації на 9%).

Використання C++20 у сучасному промисловому софті керування печею Чохральського дає високу точність обчислень без ризику виникнення витоків пам'яті та затримок на збирання сміття, що гарантує безвідмовну роботу реактора протягом багатьох діб.
