#ifndef BLDC_CALIB_H
#define BLDC_CALIB_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846f
#endif

/**
 * @brief Стани скінченного автомата ініціалізації та калібрування BLDC привода
 */
typedef enum {
    BLDC_CALIB_STATE_IDLE = 0,          /**< Режим очікування / готовність до старту */
    BLDC_CALIB_STATE_MEASURE_R,         /**< Визначення фазного активного опору R імпульсом напруги */
    BLDC_CALIB_STATE_MEASURE_L,         /**< Визначення фазної індуктивності L за швидкістю наростання di/dt */
    BLDC_CALIB_STATE_CHECK_PHASE_POLES, /**< Обертання у відкритому контурі: перевірка фаз і підрахунок пар полюсів */
    BLDC_CALIB_STATE_ALIGN_ZERO,        /**< Утримання статичного вектора Id та калібрування нуля енкодера */
    BLDC_CALIB_STATE_CALC_GAINS,        /**< Аналітичний розрахунок коефіцієнтів Kp та Ki контуру струму */
    BLDC_CALIB_STATE_STEP_TEST,         /**< Сходинкове збурення струму для оцінки динаміки та перехідного процесу */
    BLDC_CALIB_STATE_COMPLETE,          /**< Автокалібрування успішно виконано, привід готовий до переходу в FOC */
    BLDC_CALIB_STATE_FAULT              /**< Аварійний стан при виявленні несправності */
} bldc_calib_state_t;

/**
 * @brief Коди помилок процедури автокалібрування
 */
typedef enum {
    BLDC_CALIB_ERR_NONE = 0,            /**< Помилок немає */
    BLDC_CALIB_ERR_OVERCURRENT,         /**< Перевищення гранично допустимого струму захисту */
    BLDC_CALIB_ERR_R_OUT_OF_RANGE,      /**< Опір виходить за допустимі межі (обрив фази або КЗ) */
    BLDC_CALIB_ERR_L_OUT_OF_RANGE,      /**< Індуктивність виходить за фізично допустимі межі */
    BLDC_CALIB_ERR_PHASE_INVERTED,      /**< Зворотний порядок чергування фаз (B і C переплутані) */
    BLDC_CALIB_ERR_POLE_PAIRS_MISMATCH, /**< Співвідношення кутів не дає цілого числа пар полюсів */
    BLDC_CALIB_ERR_ENCODER_NO_MOTION,   /**< Відсутній рух вала або енкодер не відповідає */
    BLDC_CALIB_ERR_STEP_UNSTABLE,       /**< Нестійкий перехідний процес або неприпустиме перерегулювання */
    BLDC_CALIB_ERR_TIMEOUT,             /**< Перевищено час очікування операції */
    BLDC_CALIB_ERR_INVALID_PARAM        /**< Некоректні вхідні конфігураційні параметри */
} bldc_calib_error_t;

/**
 * @brief Ідентифіковані параметри двигуна та давача кута
 */
typedef struct {
    float resistance_ohm;               /**< Фазний активний опір статора R (Ом) */
    float inductance_henry;             /**< Фазна індуктивність статора L (Гн) */
    uint16_t pole_pairs;                /**< Кількість пар полюсів ротора (p) */
    bool phase_reversed;                /**< Прапорець реверсу фаз (зворотна послідовність) */
    float encoder_offset_rad;           /**< Кутовий зсув електричного нуля енкодера (рад) */
} bldc_motor_params_t;

/**
 * @brief Розраховані коефіцієнти ПІ-регулятора контуру струму
 */
typedef struct {
    float kp;                           /**< Пропорційний коефіцієнт підсилення Kp (В/А) */
    float ki;                           /**< Неперервний інтегральний коефіцієнт Ki (В/(А·с)) */
    float ki_discrete;                  /**< Дискретний інтегральний коефіцієнт Ki_d = Ki * Ts (В/А) */
    float bandwidth_rad_s;              /**< Смуга пропускання контуру струму (рад/с) */
} bldc_current_pi_gains_t;

/**
 * @brief Метрики якості перехідного процесу за сходинковим відгуком струму
 */
typedef struct {
    float target_current_a;             /**< Цільова амплітуда сходинки струму Id (А) */
    float peak_current_a;               /**< Максимальний піковий струм Id (А) */
    float overshoot_percent;            /**< Відносне динамічне перерегулювання (%) */
    float rise_time_ms;                 /**< Час наростання від 10% до 90% (мс) */
    float settling_time_ms;             /**< Час встановлення в коридор ±5% (мс) */
    bool stable;                        /**< Ознака задовільної стійкості перехідного процесу */
} bldc_step_metrics_t;

/**
 * @brief Конфігураційні налаштування процедури калібрування
 */
typedef struct {
    float v_bus;                        /**< Напруга ланки постійного струму інвертора (В) */
    float max_current_a;                /**< Максимальний безпечний струм калібрування (А) */
    float r_meas_voltage;               /**< Випробувальна постійна напруга вимірювання опору Vd (В) */
    float l_pulse_voltage;              /**< Амплітуда імпульсу вимірювання індуктивності (В) */
    float open_loop_voltage;            /**< Амплітуда напруги обертання у відкритому контурі (В) */
    float open_loop_speed_rad_s;        /**< Швидкість обертання поля у відкритому контурі (ел. рад/с) */
    float open_loop_elec_revs;          /**< Кількість електричних обертів для верифікації полюсів */
    float align_voltage;                /**< Напруга статичного вектора вирівнювання нуля енкодера (В) */
    float target_bandwidth_hz;          /**< Бажана смуга пропускання контуру струму (Гц) */
    float step_test_current;            /**< Амплітуда тестової сходинки струму Id (А) */
    float sample_time_s;                /**< Період виклику кроку калібрування Ts (с) */
} bldc_calib_cfg_t;

/**
 * @brief Апаратні функції зворотного виклику для взаємодії з периферією
 */
typedef struct {
    /** Завдання миттєвих напруг фаз Va, Vb, Vc на виході інвертора */
    void (*set_phase_voltages)(float va, float vb, float vc, void *user_data);
    /** Читання миттєвих струмів фаз Ia, Ib, Ic з АЦП шунтів */
    void (*get_phase_currents)(float *ia, float *ib, float *ic, void *user_data);
    /** Зчитування поточного механічного кута вала з енкодера (0 .. 2*PI рад) */
    float (*get_encoder_mech_rad)(void *user_data);
    /** Довільний вказівник користувача (контекст плати/драйвера) */
    void *user_data;
} bldc_calib_hw_ops_t;

/**
 * @brief Контекст скінченного автомата калібрування сервопривода
 */
typedef struct {
    bldc_calib_state_t state;           /**< Поточний стан автомата */
    bldc_calib_error_t error;           /**< Код останньої зафіксованої помилки */
    bldc_calib_cfg_t cfg;               /**< Налаштування та конфігураційні ліміти */
    bldc_calib_hw_ops_t hw;             /**< Апаратні інтерфейси драйвера */
    bldc_motor_params_t params;         /**< Ідентифіковані параметри двигуна */
    bldc_current_pi_gains_t pi_gains;   /**< Розраховані коефіцієнти регулятора струму */
    bldc_step_metrics_t step_metrics;   /**< Метрики якості перехідного процесу */

    /* Внутрішній стан та лічильники виконання */
    uint32_t state_tick;                /**< Лічильник викликів у поточному стані */
    float open_loop_angle_elec;         /**< Поточний електричний кут відкритого поля */
    float open_loop_accum_mech;         /**< Сумарне розгорнуте механічне переміщення вала */
    float last_mech_angle;              /**< Попередній механічний кут для операції unwrap */
    float accum_current;                /**< Акумулятор струму для фільтрації шумів АЦП */
    uint32_t accum_samples;             /**< Кількість зібраних вибірок струму */
    float pi_integral;                  /**< Інтегратор ПІ-регулятора тестової сходинки */

    /* Змінні вимірювання індуктивності L */
    float l_accum_inductance;           /**< Сума оцінок індуктивності за імпульсами */
    uint32_t l_pulse_cycles;            /**< Лічильник виконаних імпульсних циклів */
    float l_i_base;                     /**< Базовий струм до подачі імпульсу */
    float l_i_pos;                      /**< Струм на піку позитивного імпульсу */
    float l_i_neg;                      /**< Струм на піку негативного імпульсу */

    /* Змінні аналізу сходинкового збурення */
    float step_peak_current;            /**< Зафіксований піковий струм перехідного процесу */
    float step_t10_ms;                  /**< Момент досягнення 10% цільового струму */
    float step_t90_ms;                  /**< Момент досягнення 90% цільового струму */
    float step_settle_candidate_ms;     /**< Кандидат на час входження в 5% коридор */
    bool step_entered_corridor;         /**< Прапорець перебування всередині коридору */
} bldc_calib_ctx_t;

/**
 * @brief Ініціалізація структури автомата калібрування
 * @param ctx Вказівник на контекст автомата
 * @param cfg Конфігураційні параметри калібрування
 * @param hw Апаратні функції драйвера периферії
 * @return true, якщо параметри коректні; false за помилки валідації
 */
bool bldc_calib_init(bldc_calib_ctx_t *ctx, const bldc_calib_cfg_t *cfg, const bldc_calib_hw_ops_t *hw);

/**
 * @brief Запуск процедури калібрування
 * @param ctx Вказівник на контекст автомата
 * @return true за успішного переходу в стан вимірювання опору R
 */
bool bldc_calib_start(bldc_calib_ctx_t *ctx);

/**
 * @brief Примусова або аварійна зупинка автомата зі зняттям напруг інвертора
 * @param ctx Вказівник на контекст автомата
 */
void bldc_calib_stop(bldc_calib_ctx_t *ctx);

/**
 * @brief Періодичний крок виконання кінцевого автомата
 *
 * Викликається регулярно із фіксованим кроком sample_time_s із циклу
 * диспетчера або переривання таймера синхронізації ШІМ.
 *
 * @param ctx Вказівник на контекст автомата
 * @return Поточний стан автомата після виконання ітерації
 */
bldc_calib_state_t bldc_calib_step(bldc_calib_ctx_t *ctx);

/**
 * @brief Отримання поточного стану автомата
 */
bldc_calib_state_t bldc_calib_get_state(const bldc_calib_ctx_t *ctx);

/**
 * @brief Отримання коду останньої зафіксованої помилки
 */
bldc_calib_error_t bldc_calib_get_error(const bldc_calib_ctx_t *ctx);

/**
 * @brief Текстова назва стану автомата для діагностики та телеметрії
 */
const char *bldc_calib_state_name(bldc_calib_state_t state);

/**
 * @brief Текстовий опис коду помилки автомата
 */
const char *bldc_calib_error_name(bldc_calib_error_t error);

/**
 * @brief Розрахунок поточного електричного кута поля для FOC за механічним кутом
 *
 * Використовує ідентифіковані значення числа пар полюсів p, напрямку чергування
 * фаз та зміщення електричного нуля енкодера:
 * theta_e = wrap(p * theta_m - theta_offset).
 *
 * @param ctx Вказівник на контекст після успішного калібрування
 * @param mech_angle_rad Поточний механічний кут вала з енкодера (0 .. 2*PI рад)
 * @return Електричний кут у діапазоні [0, 2*PI)
 */
float bldc_calib_electrical_angle(const bldc_calib_ctx_t *ctx, float mech_angle_rad);

#endif /* BLDC_CALIB_H */
