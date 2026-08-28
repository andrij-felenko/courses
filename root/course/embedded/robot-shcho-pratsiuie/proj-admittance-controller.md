# ⚙️ Реалізація адмітансного контролера на C та C++

У системах фізичної взаємодії з невідомим довкіллям робот не може покладатися на чистий позиційний контур: найменша неточність у визначенні геометрії поверхні або температурне розширення деталі призводить до створення аварійних сил реакції. Адмітансний контролер розв'язує цю проблему, трансформуючи виміряну зовнішню силу в динамічне зміщення цільової траєкторії в реальному часі.

Нижче наведено практичну реалізацію 6-осьового адмітансного контролера для контуру жорсткого реального часу (1 кГц), призначеного для роботи з силовими давачами на зап'ястку маніпулятора.

## 1. Структура алгоритму та дискретна динаміка

Контролер виконує обчислення щотакту з фіксованим періодом `dt = 0.001` с (1000 Гц). Розрахунковий цикл складається з п'яти послідовних етапів:

1. **Фільтрація та тарування (Filtering & Taring):** сировинні покази тензодатчиків містять високочастотний шум комутації силових транзисторів інвертора (FOC PWM noise) на частотах 10–40 кГц та структурні вібрації механіки. Сигнал пропускається крізь цифровий фільтр низьких частот першого порядку. Перед початком роботи виконується тарування зміщення нуля (Zero Tare), що накопичується через температурний нагрів п'єзорезистивних мостів.
2. **Зона нечутливості (Deadband):** відфільтроване значення очищається від зони нечутливості. Це гарантує, що під час руху у вільному просторі дрібні шуми датчика не інтегруватимуться у фальшивий дрейф координат інструмента.
3. **Чисельне інтегрування динаміки адмітансу:** класичне диференціальне рівняння другого порядку перетворюється на дискретну форму за напівнеявним методом Ейлера (Semi-implicit Euler):
   ```text
   a(t) = M_d^(-1) · ( -F_filt(t) - D_d · v(t) - K_d · p(t) )
   v(t + dt) = v(t) + a(t) · dt
   p(t + dt) = p(t) + v(t + dt) · dt
   ```
   На відміну від стандартного явного методу Ейлера, де координата інтегрується за старою швидкістю `v(t)`, напівнеявний метод використовує оновлену швидкість `v(t + dt)`. Це зберігає фазовий об'єм системи (симплектична властивість) і усуває штучну чисельну нестійкість, яка інакше розгойдувала б віртуальну пружину.
4. **Обмеження ходу та захист від інтегрального насичення (Anti-Windup Clamping):** декартове зміщення податливості `p` та швидкість `v` жорстко обмежуються безпечним діапазоном. Якщо інструмент досягає максимального зміщення, швидкість у бік упору обнуляється, запобігаючи неконтрольованому накопиченню кінетичної енергії.
5. **Скінченний автомат безпеки (Safety State Machine):** модуль безперервно відстежує амплітуду сил. При перевищенні порогу `F_max` активується стан аварійного відтягування (Emergency Retract), що відводить маніпулятор назад уздовж нормалі контакту.

## 2. Реалізація мовами C та C++

:::tabs
@tab C
```c
#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#define DOF_CARTESIAN 6
#define DT_SEC 0.001f
#define TARE_SAMPLES 500

typedef enum {
    ADMITTANCE_STATE_IDLE = 0,
    ADMITTANCE_STATE_TARING = 1,
    ADMITTANCE_STATE_ACTIVE = 2,
    ADMITTANCE_STATE_FORCE_EXCEEDED = 3,
    ADMITTANCE_STATE_RETRACT = 4,
    ADMITTANCE_STATE_FAULT = 5
} admittance_mode_t;

typedef struct {
    float m_d[DOF_CARTESIAN];         /* Віртуальна маса (кг, кг·м²) */
    float d_d[DOF_CARTESIAN];         /* Віртуальне демпфування (Н·с/м, Н·м·с/рад) */
    float k_d[DOF_CARTESIAN];         /* Віртуальна жорсткість (Н/м, Н·м/рад) */
    float filter_alpha;               /* Коефіцієнт згладжування фільтра сили */
    float deadband[DOF_CARTESIAN];    /* Зона нечутливості датчика (Н, Н·м) */
    float max_force[DOF_CARTESIAN];   /* Аварійний ліміт сили (Н, Н·м) */
    float max_disp[DOF_CARTESIAN];    /* Максимальне зміщення податливості (м, рад) */
    float retract_speed;              /* Швидкість аварійного відведення (м/с) */
} admittance_config_t;

typedef struct {
    float f_raw_offset[DOF_CARTESIAN]; /* Калібрувальне зміщення нуля */
    float f_filt[DOF_CARTESIAN];       /* Відфільтрована сила */
    float disp[DOF_CARTESIAN];         /* Поточне зміщення податливості */
    float vel[DOF_CARTESIAN];          /* Поточна швидкість зміщення */
    uint32_t tare_counter;             /* Лічильник вибірок тарування */
    float tare_accumulator[DOF_CARTESIAN];
    admittance_mode_t mode;
} admittance_context_t;

void admittance_init(admittance_context_t *ctx) {
    if (!ctx) return;
    for (int i = 0; i < DOF_CARTESIAN; ++i) {
        ctx->f_raw_offset[i] = 0.0f;
        ctx->f_filt[i] = 0.0f;
        ctx->disp[i] = 0.0f;
        ctx->vel[i] = 0.0f;
        ctx->tare_accumulator[i] = 0.0f;
    }
    ctx->tare_counter = 0;
    ctx->mode = ADMITTANCE_STATE_IDLE;
}

void admittance_start_tare(admittance_context_t *ctx) {
    if (!ctx) return;
    for (int i = 0; i < DOF_CARTESIAN; ++i) {
        ctx->tare_accumulator[i] = 0.0f;
    }
    ctx->tare_counter = 0;
    ctx->mode = ADMITTANCE_STATE_TARING;
}

admittance_mode_t admittance_step(
    const admittance_config_t *cfg,
    admittance_context_t *ctx,
    const float f_raw[DOF_CARTESIAN],
    const float x_nominal[DOF_CARTESIAN],
    const float v_nominal[DOF_CARTESIAN],
    float x_cmd[DOF_CARTESIAN],
    float v_cmd[DOF_CARTESIAN]
) {
    if (!cfg || !ctx || !f_raw || !x_nominal || !v_nominal || !x_cmd || !v_cmd) {
        return ADMITTANCE_STATE_FAULT;
    }

    /* 1. Режим калібрування нуля датчика */
    if (ctx->mode == ADMITTANCE_STATE_TARING) {
        for (int i = 0; i < DOF_CARTESIAN; ++i) {
            ctx->tare_accumulator[i] += f_raw[i];
            x_cmd[i] = x_nominal[i];
            v_cmd[i] = v_nominal[i];
        }
        ctx->tare_counter++;
        if (ctx->tare_counter >= TARE_SAMPLES) {
            for (int i = 0; i < DOF_CARTESIAN; ++i) {
                ctx->f_raw_offset[i] = ctx->tare_accumulator[i] / (float)TARE_SAMPLES;
                ctx->disp[i] = 0.0f;
                ctx->vel[i] = 0.0f;
                ctx->f_filt[i] = 0.0f;
            }
            ctx->mode = ADMITTANCE_STATE_ACTIVE;
        }
        return ctx->mode;
    }

    /* 2. Обробка аварійного стану відтягування */
    if (ctx->mode == ADMITTANCE_STATE_FORCE_EXCEEDED || ctx->mode == ADMITTANCE_STATE_RETRACT) {
        ctx->mode = ADMITTANCE_STATE_RETRACT;
        for (int i = 0; i < DOF_CARTESIAN; ++i) {
            /* Плавне повернення податливості до нуля */
            if (ctx->disp[i] > 0.0001f) {
                ctx->disp[i] -= cfg->retract_speed * DT_SEC;
            } else if (ctx->disp[i] < -0.0001f) {
                ctx->disp[i] += cfg->retract_speed * DT_SEC;
            } else {
                ctx->disp[i] = 0.0f;
            }
            ctx->vel[i] = 0.0f;
            x_cmd[i] = x_nominal[i] + ctx->disp[i];
            v_cmd[i] = v_nominal[i];
        }
        return ctx->mode;
    }

    /* 3. Основний розрахунковий контур адмітансу */
    for (int i = 0; i < DOF_CARTESIAN; ++i) {
        /* Компенсація зсуву нуля */
        float f_unbiased = f_raw[i] - ctx->f_raw_offset[i];

        /* Експоненційна низькочастотна фільтрація */
        ctx->f_filt[i] = (1.0f - cfg->filter_alpha) * ctx->f_filt[i] +
                         cfg->filter_alpha * f_unbiased;

        /* Перевірка аварійного ліміту сили */
        if (fabsf(ctx->f_filt[i]) > cfg->max_force[i]) {
            ctx->mode = ADMITTANCE_STATE_FORCE_EXCEEDED;
            return ctx->mode;
        }

        /* Відсікання зони нечутливості */
        float f_active = 0.0f;
        if (ctx->f_filt[i] > cfg->deadband[i]) {
            f_active = ctx->f_filt[i] - cfg->deadband[i];
        } else if (ctx->f_filt[i] < -cfg->deadband[i]) {
            f_active = ctx->f_filt[i] + cfg->deadband[i];
        }

        /* Динаміка адмітансу: M_d * a + D_d * v + K_d * p = -F_active */
        float accel = (-f_active - cfg->d_d[i] * ctx->vel[i] - cfg->k_d[i] * ctx->disp[i]) / cfg->m_d[i];

        /* Напівнеявний метод Ейлера */
        ctx->vel[i] += accel * DT_SEC;
        ctx->disp[i] += ctx->vel[i] * DT_SEC;

        /* Насичення ходу та захист від інтегрального розгону */
        if (ctx->disp[i] > cfg->max_disp[i]) {
            ctx->disp[i] = cfg->max_disp[i];
            if (ctx->vel[i] > 0.0f) ctx->vel[i] = 0.0f;
        } else if (ctx->disp[i] < -cfg->max_disp[i]) {
            ctx->disp[i] = -cfg->max_disp[i];
            if (ctx->vel[i] < 0.0f) ctx->vel[i] = 0.0f;
        }

        /* Формування вихідних координат */
        x_cmd[i] = x_nominal[i] + ctx->disp[i];
        v_cmd[i] = v_nominal[i] + ctx->vel[i];
    }

    ctx->mode = ADMITTANCE_STATE_ACTIVE;
    return ADMITTANCE_STATE_ACTIVE;
}
```

@tab C++
```cpp
#include <array>
#include <span>
#include <cmath>
#include <expected>
#include <algorithm>

namespace robotics::control {

inline constexpr size_t kDofCartesian = 6;
inline constexpr float kDtSec = 0.001f;
inline constexpr uint32_t kTareSamples = 500;

enum class AdmittanceMode : uint8_t {
    Idle = 0,
    Taring = 1,
    Active = 2,
    ForceExceeded = 3,
    Retract = 4,
    Fault = 5
};

struct AdmittanceConfig {
    std::array<float, kDofCartesian> m_d{};         // Віртуальна маса (кг, кг·м²)
    std::array<float, kDofCartesian> d_d{};         // Віртуальне демпфування (Н·с/м, Н·м·с/рад)
    std::array<float, kDofCartesian> k_d{};         // Віртуальна жорсткість (Н/м, Н·м/рад)
    float filter_alpha{0.1f};                      // Коефіцієнт згладжування фільтра
    std::array<float, kDofCartesian> deadband{};    // Зона нечутливості датчика (Н, Н·м)
    std::array<float, kDofCartesian> max_force{};   // Аварійний ліміт сили (Н, Н·м)
    std::array<float, kDofCartesian> max_disp{};    // Максимальне зміщення податливості (м, рад)
    float retract_speed{0.05f};                    // Швидкість аварійного відведення (м/с)
};

struct CompliantOutput {
    std::array<float, kDofCartesian> x_cmd{};
    std::array<float, kDofCartesian> v_cmd{};
};

class AdmittanceController {
public:
    explicit constexpr AdmittanceController(const AdmittanceConfig& config) noexcept
        : config_(config) {}

    void reset() noexcept {
        f_raw_offset_.fill(0.0f);
        f_filt_.fill(0.0f);
        disp_.fill(0.0f);
        vel_.fill(0.0f);
        tare_accum_.fill(0.0f);
        tare_counter_ = 0;
        mode_ = AdmittanceMode::Idle;
    }

    void start_tare() noexcept {
        tare_accum_.fill(0.0f);
        tare_counter_ = 0;
        mode_ = AdmittanceMode::Taring;
    }

    [[nodiscard]] auto step(
        std::span<const float, kDofCartesian> f_raw,
        std::span<const float, kDofCartesian> x_nominal,
        std::span<const float, kDofCartesian> v_nominal
    ) noexcept -> std::expected<CompliantOutput, AdmittanceMode> {
        CompliantOutput out{};

        // 1. Обробка тарування
        if (mode_ == AdmittanceMode::Taring) {
            for (size_t i = 0; i < kDofCartesian; ++i) {
                tare_accum_[i] += f_raw[i];
                out.x_cmd[i] = x_nominal[i];
                out.v_cmd[i] = v_nominal[i];
            }
            if (++tare_counter_ >= kTareSamples) {
                for (size_t i = 0; i < kDofCartesian; ++i) {
                    f_raw_offset_[i] = tare_accum_[i] / static_cast<float>(kTareSamples);
                    disp_[i] = 0.0f;
                    vel_[i] = 0.0f;
                    f_filt_[i] = 0.0f;
                }
                mode_ = AdmittanceMode::Active;
            }
            return out;
        }

        // 2. Обробка аварійного відведення
        if (mode_ == AdmittanceMode::ForceExceeded || mode_ == AdmittanceMode::Retract) {
            mode_ = AdmittanceMode::Retract;
            for (size_t i = 0; i < kDofCartesian; ++i) {
                if (disp_[i] > 0.0001f) {
                    disp_[i] -= config_.retract_speed * kDtSec;
                } else if (disp_[i] < -0.0001f) {
                    disp_[i] += config_.retract_speed * kDtSec;
                } else {
                    disp_[i] = 0.0f;
                }
                vel_[i] = 0.0f;
                out.x_cmd[i] = x_nominal[i] + disp_[i];
                out.v_cmd[i] = v_nominal[i];
            }
            return out;
        }

        // 3. Основний розрахунковий контур
        for (size_t i = 0; i < kDofCartesian; ++i) {
            const float f_unbiased = f_raw[i] - f_raw_offset_[i];
            f_filt_[i] = (1.0f - config_.filter_alpha) * f_filt_[i] +
                         config_.filter_alpha * f_unbiased;

            if (std::abs(f_filt_[i]) > config_.max_force[i]) {
                mode_ = AdmittanceMode::ForceExceeded;
                return std::unexpected(AdmittanceMode::ForceExceeded);
            }

            float f_active = 0.0f;
            if (f_filt_[i] > config_.deadband[i]) {
                f_active = f_filt_[i] - config_.deadband[i];
            } else if (f_filt_[i] < -config_.deadband[i]) {
                f_active = f_filt_[i] + config_.deadband[i];
            }

            const float accel = (-f_active - config_.d_d[i] * vel_[i] - config_.k_d[i] * disp_[i]) / config_.m_d[i];

            // Напівнеявне інтегрування
            vel_[i] += accel * kDtSec;
            disp_[i] += vel_[i] * kDtSec;

            // Захист від інтегрального розгону на межі робочого простору
            if (disp_[i] > config_.max_disp[i]) {
                disp_[i] = config_.max_disp[i];
                if (vel_[i] > 0.0f) vel_[i] = 0.0f;
            } else if (disp_[i] < -config_.max_disp[i]) {
                disp_[i] = -config_.max_disp[i];
                if (vel_[i] < 0.0f) vel_[i] = 0.0f;
            }

            out.x_cmd[i] = x_nominal[i] + disp_[i];
            out.v_cmd[i] = v_nominal[i] + vel_[i];
        }

        mode_ = AdmittanceMode::Active;
        return out;
    }

    [[nodiscard]] AdmittanceMode mode() const noexcept { return mode_; }
    [[nodiscard]] const auto& filtered_force() const noexcept { return f_filt_; }
    [[nodiscard]] const auto& displacement() const noexcept { return disp_; }

private:
    AdmittanceConfig config_;
    std::array<float, kDofCartesian> f_raw_offset_{};
    std::array<float, kDofCartesian> f_filt_{};
    std::array<float, kDofCartesian> disp_{};
    std::array<float, kDofCartesian> vel_{};
    std::array<float, kDofCartesian> tare_accum_{};
    uint32_t tare_counter_{0};
    AdmittanceMode mode_{AdmittanceMode::Idle};
};

} // namespace robotics::control
```
:::

## 3. Практичні аспекти інтеграції в польотний та робототехнічний стек

При інтеграції податливого контролера на мобільну платформу розробник стикається з низкою критичних факторів, що визначають стабільність роботи заліза в реальних польових умовах:

### Гравітаційна компенсація інструмента (Tool Gravity Compensation)
Силовий датчик на зап'ястку вимірює не лише зовнішню контактну силу, але й вагу закріпленого робочого органа (схоплювача, бура, камери). При зміні орієнтації інструмента в просторі проекція сили тяжіння на осі датчика безперервно змінюється. Якщо маса інструмента становить `0.8 кг`, поворот кисті на 90 градусів породжує хибну бічну силу `7.84 Н`. Без компенсації адмітансний контролер сприйме власну вагу інструмента як контакт зі стіною і почне нескінченно відхилятися убік. Перед подачею сигналу в адмітансний регулятор необхідно виконувати щотактове віднімання гравітаційної складової:
```text
F_ext = F_raw - R_sensor^T · [0, 0, -m_tool · g]^T
```
де `R_sensor` — матриця орієнтації датчика відносно горизонту, отримана з прямої кінематики маніпулятора та орієнтації бази від бортового IMU.

### Сингулярності та згасання найменших квадратів (Damped Least Squares)
Отримані декартові швидкості `v_cmd` транслюються у швидкості суглобів через псевдоінверсію якобіана `q' = J^dagger · v_cmd`. Поблизу сингулярних конфігурацій (повне випрямлення або граничне складання руки) детермінант матриці вироджується, і звичайна псевдоінверсія генерує нескінченні швидкості моторів. Щоб уникнути зриву приводів і механічного удару, застосовують регуляризовану інверсію Левенберга — Марквардта:
```text
J_dls = J^T · (J · J^T + lambda^2 · I)^(-1)
```
Коефіцієнт демпфування `lambda` автоматично масштабується залежно від показника маніпульованості `w = sqrt(det(J · J^T))`: коли рука перебуває у зручній робочій зоні (`w >> 0`), `lambda = 0`; при наближенні до сингулярності (`w -> 0`) `lambda` плавно зростає, жертвуючи точністю відпрацювання швидкості заради збереження плавності руху приводів.

### Синхронізація шини з приводами та бюджет затримок
Обчислення адмітансу з частотою 1 кГц не матимуть сенсу, якщо сервоприводи отримують команди через повільний або недетермінований інтерфейс (наприклад, звичайний UART на 50 Гц з непередбачуваними паузами ОС). Затримка передачі команди на 10 мс у поєднанні з жорстким металевим середовищем призводить до того, що команда «відступити назад» доходить до мотора вже після того, як сила реакції перевищила критичну межу. Зв'язок між обчислювальним вузлом і FOC-драйверами приводів має відбуватися через детерміновані шини CAN FD (швидкість 5–8 Мбіт/с) або EtherCAT із фіксованим циклом і джитером менше 50 мікросекунд.

### Детекція втрати контакту (Contact Slip Detection)
Якщо під час прикладання сили інструмент раптово зісковзує з деталі (наприклад, викрутка зривається зі шліца гвинта), виміряна сила різко обнуляється за кілька мікросекунд. У неякісно налаштованій системі це призводить до різкого «вистрілювання» інструмента вперед за рахунок накопиченої пружної енергії. Завдяки налаштуванню критичного демпфування віртуальної системи (`zeta = D_d / (2 · sqrt(M_d · K_d)) = 1.0`), координата інструмента плавно повертається до номінальної траєкторії без перерегулювання, коливань та ривків.
