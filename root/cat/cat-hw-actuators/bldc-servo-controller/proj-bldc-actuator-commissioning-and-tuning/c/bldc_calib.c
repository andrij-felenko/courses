#include "bldc_calib.h"
#include <string.h>

/* Математичні константи векторних перетворень */
#define INV_SQRT3       0.57735026919f   /* 1.0f / sqrtf(3.0f) */
#define SQRT3_DIV2      0.86602540378f   /* sqrtf(3.0f) / 2.0f */
#define TWO_PI          6.28318530718f   /* 2.0f * M_PI */

/* Кількість тактів витримки та замірів для кожної фази калібрування */
#define R_SETTLE_TICKS       400U        /* Витримка наростання струму R (40 мс при Ts=100мкс) */
#define R_SAMPLE_TICKS       400U        /* Тривалість усереднення струму R */
#define L_PULSE_CYCLES_COUNT 10U         /* Кількість циклів імпульсів для оцінки L */
#define ALIGN_HOLD_TICKS     4000U       /* Утримання ротора для вирівнювання нуля (400 мс) */
#define STEP_TEST_TICKS      200U        /* Тривалість сходинкового тесту (20 мс) */

/**
 * @brief Обгортання кута в діапазон [0, 2*PI)
 */
static inline float wrap_2pi(float angle) {
    float res = fmodf(angle, TWO_PI);
    if (res < 0.0f) {
        res += TWO_PI;
    }
    return res;
}

/**
 * @brief Обгортання кутової різниці в симетричний інтервал [-PI, PI)
 */
static inline float wrap_pm_pi(float angle) {
    while (angle > (float)M_PI) {
        angle -= TWO_PI;
    }
    while (angle < -(float)M_PI) {
        angle += TWO_PI;
    }
    return angle;
}

/**
 * @brief Амплітудно-інваріантне пряме перетворення Кларк (Ia, Ib, Ic -> I_alpha, I_beta)
 *
 * Припускається збалансована трифазна система без нульового проводу (Ia + Ib + Ic = 0).
 */
static inline void clarke_transform(float ia, float ib, float *i_alpha, float *i_beta) {
    *i_alpha = ia;
    *i_beta  = (ia + 2.0f * ib) * INV_SQRT3;
}

/**
 * @brief Пряме перетворення Парка (I_alpha, I_beta -> Id, Iq)
 */
static inline void park_transform(float i_alpha, float i_beta, float theta, float *id, float *iq) {
    float cos_th = cosf(theta);
    float sin_th = sinf(theta);
    *id =  i_alpha * cos_th + i_beta * sin_th;
    *iq = -i_alpha * sin_th + i_beta * cos_th;
}

/**
 * @brief Зворотне перетворення Парка (Vd, Vq -> V_alpha, V_beta)
 */
static inline void inv_park_transform(float vd, float vq, float theta, float *v_alpha, float *v_beta) {
    float cos_th = cosf(theta);
    float sin_th = sinf(theta);
    *v_alpha = vd * cos_th - vq * sin_th;
    *v_beta  = vd * sin_th + vq * cos_th;
}

/**
 * @brief Амплітудно-інваріантне зворотне перетворення Кларк (V_alpha, V_beta -> Va, Vb, Vc)
 */
static inline void inv_clarke_transform(float v_alpha, float v_beta, float *va, float *vb, float *vc) {
    *va = v_alpha;
    *vb = -0.5f * v_alpha + SQRT3_DIV2 * v_beta;
    *vc = -0.5f * v_alpha - SQRT3_DIV2 * v_beta;
}

/**
 * @brief Завдання вектора напруги Vd, Vq із захистом від перемодуляції інвертора
 */
static void apply_dq_voltage(bldc_calib_ctx_t *ctx, float vd, float vq, float theta) {
    /* Максимальна амплітуда фазної напруги для просторово-векторної модуляції: Vbus / sqrt(3) */
    float v_max = ctx->cfg.v_bus * INV_SQRT3;
    float v_mag = sqrtf(vd * vd + vq * vq);

    if (v_mag > v_max && v_mag > 1e-6f) {
        float scale = v_max / v_mag;
        vd *= scale;
        vq *= scale;
    }

    float v_alpha, v_beta;
    inv_park_transform(vd, vq, theta, &v_alpha, &v_beta);

    float va, vb, vc;
    inv_clarke_transform(v_alpha, v_beta, &va, &vb, &vc);

    ctx->hw.set_phase_voltages(va, vb, vc, ctx->hw.user_data);
}

/**
 * @brief Зчитування фазних струмів та перетворення їх у систему координат ротора (Id, Iq)
 */
static void read_dq_currents(bldc_calib_ctx_t *ctx, float theta, float *id, float *iq) {
    float ia = 0.0f, ib = 0.0f, ic = 0.0f;
    ctx->hw.get_phase_currents(&ia, &ib, &ic, ctx->hw.user_data);

    float i_alpha, i_beta;
    clarke_transform(ia, ib, &i_alpha, &i_beta);
    park_transform(i_alpha, i_beta, theta, id, iq);
}

/**
 * @brief Перехід автомата в аварійний стан із негайним зняттям напруг
 */
static void set_fault(bldc_calib_ctx_t *ctx, bldc_calib_error_t err) {
    ctx->error = err;
    ctx->state = BLDC_CALIB_STATE_FAULT;
    apply_dq_voltage(ctx, 0.0f, 0.0f, 0.0f);
}

/**
 * @brief Безпечне перемикання стану автомата зі скиданням тактів
 */
static void set_state(bldc_calib_ctx_t *ctx, bldc_calib_state_t new_state) {
    ctx->state = new_state;
    ctx->state_tick = 0U;
    ctx->accum_current = 0.0f;
    ctx->accum_samples = 0U;
}

bool bldc_calib_init(bldc_calib_ctx_t *ctx, const bldc_calib_cfg_t *cfg, const bldc_calib_hw_ops_t *hw) {
    if (ctx == NULL || cfg == NULL || hw == NULL) {
        return false;
    }
    if (hw->set_phase_voltages == NULL || hw->get_phase_currents == NULL || hw->get_encoder_mech_rad == NULL) {
        return false;
    }
    if (cfg->v_bus <= 0.0f || cfg->max_current_a <= 0.0f || cfg->sample_time_s <= 0.0f ||
        cfg->target_bandwidth_hz <= 0.0f) {
        return false;
    }

    memset(ctx, 0, sizeof(*ctx));
    ctx->cfg = *cfg;
    ctx->hw = *hw;
    ctx->state = BLDC_CALIB_STATE_IDLE;
    ctx->error = BLDC_CALIB_ERR_NONE;

    return true;
}

bool bldc_calib_start(bldc_calib_ctx_t *ctx) {
    if (ctx == NULL) {
        return false;
    }
    if (ctx->state != BLDC_CALIB_STATE_IDLE && ctx->state != BLDC_CALIB_STATE_COMPLETE) {
        return false;
    }

    memset(&ctx->params, 0, sizeof(ctx->params));
    memset(&ctx->pi_gains, 0, sizeof(ctx->pi_gains));
    memset(&ctx->step_metrics, 0, sizeof(ctx->step_metrics));

    ctx->error = BLDC_CALIB_ERR_NONE;
    set_state(ctx, BLDC_CALIB_STATE_MEASURE_R);
    return true;
}

void bldc_calib_stop(bldc_calib_ctx_t *ctx) {
    if (ctx == NULL) {
        return;
    }
    apply_dq_voltage(ctx, 0.0f, 0.0f, 0.0f);
    if (ctx->state != BLDC_CALIB_STATE_FAULT) {
        ctx->state = BLDC_CALIB_STATE_IDLE;
    }
}

bldc_calib_state_t bldc_calib_step(bldc_calib_ctx_t *ctx) {
    if (ctx == NULL) {
        return BLDC_CALIB_STATE_FAULT;
    }

    switch (ctx->state) {
        case BLDC_CALIB_STATE_IDLE:
        case BLDC_CALIB_STATE_COMPLETE:
        case BLDC_CALIB_STATE_FAULT:
            /* Пасивні стани: напруга на виходах інвертора вимкнена */
            apply_dq_voltage(ctx, 0.0f, 0.0f, 0.0f);
            break;

        case BLDC_CALIB_STATE_MEASURE_R: {
            /*
             * Визначення активного фазного опору R:
             * Подаємо фіксовану постійну напругу Vd при theta = 0.
             * Струм зростає експоненціально: id(t) = (Vd / R) * (1 - exp(-t / tau_e)).
             * Перші R_SETTLE_TICKS очікуємо затухання перехідного процесу,
             * наступні R_SAMPLE_TICKS усереднюємо виміряний стаціонарний струм.
             */
            apply_dq_voltage(ctx, ctx->cfg.r_meas_voltage, 0.0f, 0.0f);

            float id, iq;
            read_dq_currents(ctx, 0.0f, &id, &iq);

            /* Захист від перевищення гранично допустимого струму */
            if (fabsf(id) > ctx->cfg.max_current_a || fabsf(iq) > ctx->cfg.max_current_a) {
                set_fault(ctx, BLDC_CALIB_ERR_OVERCURRENT);
                break;
            }

            if (ctx->state_tick >= R_SETTLE_TICKS &&
                ctx->state_tick < (R_SETTLE_TICKS + R_SAMPLE_TICKS)) {
                ctx->accum_current += id;
                ctx->accum_samples++;
            }

            ctx->state_tick++;

            if (ctx->state_tick >= (R_SETTLE_TICKS + R_SAMPLE_TICKS)) {
                if (ctx->accum_samples == 0U) {
                    set_fault(ctx, BLDC_CALIB_ERR_R_OUT_OF_RANGE);
                    break;
                }

                float i_steady = ctx->accum_current / (float)ctx->accum_samples;

                /* Струм повинен бути помітним над шумом АЦП, інакше обрив обмотки */
                if (i_steady < 0.02f) {
                    set_fault(ctx, BLDC_CALIB_ERR_R_OUT_OF_RANGE);
                    break;
                }

                /* Розрахунок фазного опору: R = Vd / Id */
                float r_est = ctx->cfg.r_meas_voltage / i_steady;

                /* Фізичні межі типових BLDC моторів (0.01 Ом .. 50.0 Ом) */
                if (r_est < 0.01f || r_est > 50.0f) {
                    set_fault(ctx, BLDC_CALIB_ERR_R_OUT_OF_RANGE);
                    break;
                }

                ctx->params.resistance_ohm = r_est;
                apply_dq_voltage(ctx, 0.0f, 0.0f, 0.0f);

                /* Скидання лічильників для вимірювання індуктивності L */
                ctx->l_accum_inductance = 0.0f;
                ctx->l_pulse_cycles = 0U;
                set_state(ctx, BLDC_CALIB_STATE_MEASURE_L);
            }
            break;
        }

        case BLDC_CALIB_STATE_MEASURE_L: {
            /*
             * Визначення фазної індуктивності L за швидкістю наростання di/dt:
             * V_L = L * (di/dt) + R * i  =>  L = (V_pulse - R * i_avg) * dt / delta_i.
             * Кожен цикл складається з 4 тактів (по 100 мкс):
             *  Такт 0: Vd = 0, зчитування базового струму i_base;
             *  Такт 1: Vd = +V_pulse, фіксація струму i_pos;
             *  Такт 2: Vd = -V_pulse, фіксація струму i_neg;
             *  Такт 3: Vd = 0, розрахунок L за різницею delta_i та акумуляція.
             */
            uint32_t step_in_cycle = ctx->state_tick % 4U;

            if (step_in_cycle == 0U) {
                apply_dq_voltage(ctx, 0.0f, 0.0f, 0.0f);
                float id, iq;
                read_dq_currents(ctx, 0.0f, &id, &iq);
                ctx->l_i_base = id;
            } else if (step_in_cycle == 1U) {
                apply_dq_voltage(ctx, ctx->cfg.l_pulse_voltage, 0.0f, 0.0f);
                float id, iq;
                read_dq_currents(ctx, 0.0f, &id, &iq);
                ctx->l_i_pos = id;
            } else if (step_in_cycle == 2U) {
                apply_dq_voltage(ctx, -ctx->cfg.l_pulse_voltage, 0.0f, 0.0f);
                float id, iq;
                read_dq_currents(ctx, 0.0f, &id, &iq);
                ctx->l_i_neg = id;
            } else {
                apply_dq_voltage(ctx, 0.0f, 0.0f, 0.0f);

                /* Двосторонній приріст струму для усунення постійного зсуву АЦП */
                float delta_i = ((ctx->l_i_pos - ctx->l_i_base) + (ctx->l_i_base - ctx->l_i_neg)) * 0.5f;

                if (delta_i > 0.001f) {
                    float v_eff = ctx->cfg.l_pulse_voltage -
                                  (ctx->params.resistance_ohm * (ctx->l_i_pos * 0.5f));
                    float l_sample = (v_eff * ctx->cfg.sample_time_s) / delta_i;

                    if (l_sample > 1.0e-6f && l_sample < 0.1f) {
                        ctx->l_accum_inductance += l_sample;
                        ctx->l_pulse_cycles++;
                    }
                }
            }

            ctx->state_tick++;

            if (ctx->l_pulse_cycles >= L_PULSE_CYCLES_COUNT) {
                float l_est = ctx->l_accum_inductance / (float)ctx->l_pulse_cycles;

                if (l_est < 1.0e-6f || l_est > 0.1f) {
                    set_fault(ctx, BLDC_CALIB_ERR_L_OUT_OF_RANGE);
                    break;
                }

                ctx->params.inductance_henry = l_est;
                apply_dq_voltage(ctx, 0.0f, 0.0f, 0.0f);

                /* Підготовка до тесту обертання у відкритому контурі */
                ctx->open_loop_angle_elec = 0.0f;
                ctx->open_loop_accum_mech = 0.0f;
                ctx->last_mech_angle = ctx->hw.get_encoder_mech_rad(ctx->hw.user_data);
                set_state(ctx, BLDC_CALIB_STATE_CHECK_PHASE_POLES);
            } else if (ctx->state_tick > (L_PULSE_CYCLES_COUNT * 8U)) {
                /* Таймаут, якщо імпульси не дають достатньої амплітуди delta_i */
                set_fault(ctx, BLDC_CALIB_ERR_L_OUT_OF_RANGE);
            }
            break;
        }

        case BLDC_CALIB_STATE_CHECK_PHASE_POLES: {
            /*
             * Тестове обертання у відкритому контурі:
             * Обертаємо вектор магнітного поля на фіксовану кількість електричних радіан.
             * Ротор захоплюється полем і повертається на механічний кут delta_theta_mech.
             * Чергування фаз: якщо механічний кут наростає разом з електричним — послідовність пряма;
             * якщо спадає — послідовність інвертована (фази переплутані).
             * Кількість пар полюсів: p = round(delta_theta_elec / |delta_theta_mech|).
             */
            float target_elec_revs = (ctx->cfg.open_loop_elec_revs > 0.0f) ?
                                      ctx->cfg.open_loop_elec_revs : 4.0f;
            float target_elec_rad = target_elec_revs * TWO_PI;

            ctx->open_loop_angle_elec += ctx->cfg.open_loop_speed_rad_s * ctx->cfg.sample_time_s;
            apply_dq_voltage(ctx, ctx->cfg.open_loop_voltage, 0.0f, ctx->open_loop_angle_elec);

            /* Зчитування механічного положення з енкодера та unwrap переходу через 2*PI */
            float current_mech = ctx->hw.get_encoder_mech_rad(ctx->hw.user_data);
            float delta_step = wrap_pm_pi(current_mech - ctx->last_mech_angle);
            ctx->open_loop_accum_mech += delta_step;
            ctx->last_mech_angle = current_mech;

            ctx->state_tick++;

            if (ctx->open_loop_angle_elec >= target_elec_rad) {
                apply_dq_voltage(ctx, 0.0f, 0.0f, 0.0f);

                /* Якщо ротор взагалі не зрушив з місця (заклинив або енкодер не рахує) */
                if (fabsf(ctx->open_loop_accum_mech) < 0.2f) {
                    set_fault(ctx, BLDC_CALIB_ERR_ENCODER_NO_MOTION);
                    break;
                }

                /* Перевірка чергування фаз за знаком переміщення */
                if (ctx->open_loop_accum_mech < 0.0f) {
                    ctx->params.phase_reversed = true;
                } else {
                    ctx->params.phase_reversed = false;
                }

                /* Підрахунок пар полюсів: співвідношення електричного та механічного кутів */
                float p_float = target_elec_rad / fabsf(ctx->open_loop_accum_mech);
                uint16_t p_int = (uint16_t)roundf(p_float);

                /* Перевірка близькості до цілого числа (допустиме відхилення ±0.25) */
                if (p_int < 1U || fabsf(p_float - (float)p_int) > 0.25f) {
                    set_fault(ctx, BLDC_CALIB_ERR_POLE_PAIRS_MISMATCH);
                    break;
                }

                ctx->params.pole_pairs = p_int;
                set_state(ctx, BLDC_CALIB_STATE_ALIGN_ZERO);
            }
            break;
        }

        case BLDC_CALIB_STATE_ALIGN_ZERO: {
            /*
             * Калібрування нуля енкодера:
             * Подаємо статичний вектор напруги Vd вздовж осі прямої складової (theta_e = 0).
             * Ротор притягується до осі фази A і затухає в положенні електричного нуля.
             * Після завершення затримки зчитуємо механічний кут theta_mech_align.
             * Електричний зсув нуля: theta_offset = p * theta_mech_align.
             */
            apply_dq_voltage(ctx, ctx->cfg.align_voltage, 0.0f, 0.0f);

            ctx->state_tick++;

            if (ctx->state_tick >= ALIGN_HOLD_TICKS) {
                float mech_align = ctx->hw.get_encoder_mech_rad(ctx->hw.user_data);
                float p = (float)ctx->params.pole_pairs;
                float offset;

                if (ctx->params.phase_reversed) {
                    offset = -p * mech_align;
                } else {
                    offset = p * mech_align;
                }

                ctx->params.encoder_offset_rad = wrap_2pi(offset);
                apply_dq_voltage(ctx, 0.0f, 0.0f, 0.0f);

                set_state(ctx, BLDC_CALIB_STATE_CALC_GAINS);
            }
            break;
        }

        case BLDC_CALIB_STATE_CALC_GAINS: {
            /*
             * Аналітичний розрахунок коефіцієнтів ПІ-регулятора струму:
             * За методом модульного технічного оптимуму нуль регулятора компенсує електричний
             * полюс обмотки (Ti = L / R):
             *  Kp = omega_c * L
             *  Ki = omega_c * R
             *  Ki_discrete = Ki * Ts = omega_c * R * Ts
             * Смуга пропускання обмежується запасом стійкості за частотою ШІМ (omega_c <= 1 / (3 * Ts)).
             */
            float target_omega_c = TWO_PI * ctx->cfg.target_bandwidth_hz;
            float max_stable_omega_c = 1.0f / (3.0f * ctx->cfg.sample_time_s);

            float omega_c = (target_omega_c < max_stable_omega_c) ? target_omega_c : max_stable_omega_c;

            float kp = omega_c * ctx->params.inductance_henry;
            float ki = omega_c * ctx->params.resistance_ohm;
            float ki_discrete = ki * ctx->cfg.sample_time_s;

            ctx->pi_gains.kp = kp;
            ctx->pi_gains.ki = ki;
            ctx->pi_gains.ki_discrete = ki_discrete;
            ctx->pi_gains.bandwidth_rad_s = omega_c;

            /* Ініціалізація змінних сходинкового збурення */
            ctx->pi_integral = 0.0f;
            ctx->step_peak_current = 0.0f;
            ctx->step_t10_ms = -1.0f;
            ctx->step_t90_ms = -1.0f;
            ctx->step_settle_candidate_ms = -1.0f;
            ctx->step_entered_corridor = false;

            set_state(ctx, BLDC_CALIB_STATE_STEP_TEST);
            break;
        }

        case BLDC_CALIB_STATE_STEP_TEST: {
            /*
             * Подача сходинкового сигналу струму Id_ref:
             * Ротор зафіксований на осі d (theta_e = 0), перевіряється реакція замкненого контуру струму.
             * Розраховується дискретний ПІ-алгоритм з обмеженням інтегратора (anti-windup clamping).
             * Вимірюються перерегулювання (overshoot), час наростання (rise time) і час встановлення.
             */
            float id, iq;
            read_dq_currents(ctx, 0.0f, &id, &iq);

            float i_target = ctx->cfg.step_test_current;
            float err = i_target - id;

            /* Інтегрування похибки */
            ctx->pi_integral += ctx->pi_gains.ki_discrete * err;

            /* Обмеження вихідної напруги за напругою шини живлення */
            float v_max = ctx->cfg.v_bus * INV_SQRT3;

            /* Анти-віндап обмеження інтегратора */
            if (ctx->pi_integral > v_max) {
                ctx->pi_integral = v_max;
            } else if (ctx->pi_integral < -v_max) {
                ctx->pi_integral = -v_max;
            }

            float vd = ctx->pi_gains.kp * err + ctx->pi_integral;
            if (vd > v_max) {
                vd = v_max;
            } else if (vd < -v_max) {
                vd = -v_max;
            }

            apply_dq_voltage(ctx, vd, 0.0f, 0.0f);

            /* Аналіз динаміки перехідного процесу */
            float t_ms = (float)ctx->state_tick * ctx->cfg.sample_time_s * 1000.0f;

            if (id > ctx->step_peak_current) {
                ctx->step_peak_current = id;
            }

            /* Фіксація часу наростання 10% -> 90% */
            if (id >= (0.10f * i_target) && ctx->step_t10_ms < 0.0f) {
                ctx->step_t10_ms = t_ms;
            }
            if (id >= (0.90f * i_target) && ctx->step_t90_ms < 0.0f) {
                ctx->step_t90_ms = t_ms;
            }

            /* Оцінка входження в коридор похибки ±5% від цільового струму */
            float corridor = 0.05f * i_target;
            if (fabsf(id - i_target) <= corridor) {
                if (!ctx->step_entered_corridor) {
                    ctx->step_settle_candidate_ms = t_ms;
                    ctx->step_entered_corridor = true;
                }
            } else {
                /* Якщо струм вийшов із коридору — скидаємо позначку встановлення */
                ctx->step_entered_corridor = false;
                ctx->step_settle_candidate_ms = -1.0f;
            }

            ctx->state_tick++;

            if (ctx->state_tick >= STEP_TEST_TICKS) {
                apply_dq_voltage(ctx, 0.0f, 0.0f, 0.0f);

                float overshoot = ((ctx->step_peak_current - i_target) / i_target) * 100.0f;
                if (overshoot < 0.0f) {
                    overshoot = 0.0f;
                }

                float rise_time = (ctx->step_t90_ms > 0.0f && ctx->step_t10_ms >= 0.0f) ?
                                  (ctx->step_t90_ms - ctx->step_t10_ms) : 0.0f;
                float settling_time = (ctx->step_entered_corridor && ctx->step_settle_candidate_ms >= 0.0f) ?
                                      ctx->step_settle_candidate_ms : 0.0f;

                /* Перевірка стабільності: перерегулювання не більше 25% і струм успішно встановився */
                if (overshoot > 25.0f || settling_time <= 0.0f) {
                    set_fault(ctx, BLDC_CALIB_ERR_STEP_UNSTABLE);
                    break;
                }

                ctx->step_metrics.target_current_a = i_target;
                ctx->step_metrics.peak_current_a = ctx->step_peak_current;
                ctx->step_metrics.overshoot_percent = overshoot;
                ctx->step_metrics.rise_time_ms = rise_time;
                ctx->step_metrics.settling_time_ms = settling_time;
                ctx->step_metrics.stable = true;

                set_state(ctx, BLDC_CALIB_STATE_COMPLETE);
            }
            break;
        }
    }

    return ctx->state;
}

bldc_calib_state_t bldc_calib_get_state(const bldc_calib_ctx_t *ctx) {
    return (ctx != NULL) ? ctx->state : BLDC_CALIB_STATE_FAULT;
}

bldc_calib_error_t bldc_calib_get_error(const bldc_calib_ctx_t *ctx) {
    return (ctx != NULL) ? ctx->error : BLDC_CALIB_ERR_INVALID_PARAM;
}

const char *bldc_calib_state_name(bldc_calib_state_t state) {
    switch (state) {
        case BLDC_CALIB_STATE_IDLE:          return "Очікування (IDLE)";
        case BLDC_CALIB_STATE_MEASURE_R:     return "Вимірювання опору обмотки R";
        case BLDC_CALIB_STATE_MEASURE_L:     return "Вимірювання індуктивності L";
        case BLDC_CALIB_STATE_CHECK_PHASE_POLES: return "Тестове обертання поля та полюси";
        case BLDC_CALIB_STATE_ALIGN_ZERO:    return "Вирівнювання нуля енкодера (вектор Id)";
        case BLDC_CALIB_STATE_CALC_GAINS:    return "Розрахунок коефіцієнтів Kp/Ki";
        case BLDC_CALIB_STATE_STEP_TEST:     return "Сходинковий тест перехідного процесу";
        case BLDC_CALIB_STATE_COMPLETE:      return "Калібрування завершено (FOC READY)";
        case BLDC_CALIB_STATE_FAULT:         return "Аварія калібрування (FAULT)";
        default:                             return "Невідомий стан";
    }
}

const char *bldc_calib_error_name(bldc_calib_error_t error) {
    switch (error) {
        case BLDC_CALIB_ERR_NONE:            return "Помилок немає";
        case BLDC_CALIB_ERR_OVERCURRENT:     return "Аварійне перевантаження по струму";
        case BLDC_CALIB_ERR_R_OUT_OF_RANGE:  return "Опір поза діапазоном (обрив або КЗ)";
        case BLDC_CALIB_ERR_L_OUT_OF_RANGE:  return "Індуктивність поза діапазоном";
        case BLDC_CALIB_ERR_PHASE_INVERTED:  return "Зворотне чергування фаз";
        case BLDC_CALIB_ERR_POLE_PAIRS_MISMATCH: return "Помилка підрахунку пар полюсів";
        case BLDC_CALIB_ERR_ENCODER_NO_MOTION: return "Немає механічного обертання вала";
        case BLDC_CALIB_ERR_STEP_UNSTABLE:   return "Нестійкий перехідний процес струму";
        case BLDC_CALIB_ERR_TIMEOUT:         return "Таймаут процедури";
        case BLDC_CALIB_ERR_INVALID_PARAM:   return "Некоректні параметри конфігурації";
        default:                             return "Невідома помилка";
    }
}

float bldc_calib_electrical_angle(const bldc_calib_ctx_t *ctx, float mech_angle_rad) {
    if (ctx == NULL || ctx->state != BLDC_CALIB_STATE_COMPLETE) {
        return 0.0f;
    }

    float p = (float)ctx->params.pole_pairs;
    float theta_e;

    if (ctx->params.phase_reversed) {
        theta_e = -p * mech_angle_rad - ctx->params.encoder_offset_rad;
    } else {
        theta_e = p * mech_angle_rad - ctx->params.encoder_offset_rad;
    }

    return wrap_2pi(theta_e);
}
