#include "phase_selector.h"
#include <math.h>
#include <stddef.h>

/**
 * @brief Внутрішня функція безпечного вимкнення всіх контакторів (пауза розмикання)
 */
static void disconnect_all_contactors(phase_selector_t *ps) {
    if (ps->set_hardware_contactor != NULL) {
        ps->set_hardware_contactor(PHASE_L1, false);
        ps->set_hardware_contactor(PHASE_L2, false);
        ps->set_hardware_contactor(PHASE_L3, false);
    }
    ps->active_phase = PHASE_NONE;
}

/**
 * @brief Внутрішня функція увімкнення контактора конкретної фази із перевіркою блокування
 */
static void connect_contactor(phase_selector_t *ps, phase_id_t phase) {
    if (phase >= PHASE_COUNT) {
        disconnect_all_contactors(ps);
        return;
    }

    if (ps->set_hardware_contactor != NULL) {
        /* Апаратне/програмне взаємне блокування: вимикаємо інші перед увімкненням */
        for (uint8_t i = 0; i < PHASE_COUNT; i++) {
            if (i != (uint8_t)phase) {
                ps->set_hardware_contactor((phase_id_t)i, false);
            }
        }
        ps->set_hardware_contactor(phase, true);
    }
    ps->active_phase = phase;
}

/**
 * @brief Внутрішня оцінка відповідності напруги фази допустимому вікну з гістерезисом
 */
static void evaluate_phase_hysteresis(phase_selector_t *ps, phase_id_t phase) {
    if (phase >= PHASE_COUNT) return;

    float v = ps->rms_voltage[phase];
    bool currently_valid = ps->phase_valid[phase];

    float min_limit = ps->config.v_min_v;
    float max_limit = ps->config.v_max_v;
    float hyst = ps->config.v_hysteresis_v;

    if (currently_valid) {
        /* Фаза була нормою: знімаємо прапорець лише при виході за рамки з урахуванням гістерезису */
        if (v < (min_limit - hyst) || v > (max_limit + hyst)) {
            ps->phase_valid[phase] = false;
        }
    } else {
        /* Фаза була несправною: відновлюємо лише коли напруга строго у робочому вікні */
        if (v >= min_limit && v <= max_limit) {
            ps->phase_valid[phase] = true;
        }
    }
}

/**
 * @brief Пошук найкращої доступної фази з урахуванням пріоритету
 */
static phase_id_t select_best_available_phase(const phase_selector_t *ps) {
    /* 1. Перевірка пріоритетної фази */
    phase_id_t prio = ps->config.priority_phase;
    if (prio < PHASE_COUNT && ps->phase_valid[prio]) {
        return prio;
    }

    /* 2. Пошук першої придатної фази у порядку L1 -> L2 -> L3 */
    for (uint8_t i = 0; i < PHASE_COUNT; i++) {
        if (ps->phase_valid[i]) {
            return (phase_id_t)i;
        }
    }

    /* Жодна фаза не відповідає вимогам */
    return PHASE_NONE;
}

void phase_selector_init(phase_selector_t *ps,
                         const phase_selector_config_t *config,
                         contactor_control_fn hw_cb,
                         float v_ref,
                         uint32_t adc_max,
                         float divider_ratio) {
    if (ps == NULL || config == NULL) return;

    ps->config = *config;
    ps->set_hardware_contactor = hw_cb;
    ps->adc_v_ref = v_ref;
    ps->adc_max_value = adc_max;
    ps->voltage_divider_ratio = divider_ratio;

    for (uint8_t i = 0; i < PHASE_COUNT; i++) {
        ps->rms_voltage[i] = 0.0f;
        ps->phase_valid[i] = false;
    }

    ps->active_phase = PHASE_NONE;
    ps->target_phase = PHASE_NONE;
    ps->state = PHASE_STATE_INIT;
    ps->state_timer_ms = 0;

    disconnect_all_contactors(ps);
}

void phase_selector_process_adc_buffer(phase_selector_t *ps,
                                         phase_id_t phase,
                                         const uint16_t *adc_samples,
                                         uint32_t sample_count,
                                         uint16_t zero_offset_adc) {
    if (ps == NULL || adc_samples == NULL || sample_count == 0 || phase >= PHASE_COUNT) {
        return;
    }

    double sum_squares = 0.0;
    float volts_per_lsb = ps->adc_v_ref / (float)ps->adc_max_value;

    for (uint32_t i = 0; i < sample_count; i++) {
        int32_t centered = (int32_t)adc_samples[i] - (int32_t)zero_offset_adc;
        float inst_voltage_sensor = (float)centered * volts_per_lsb;
        float inst_voltage_mains = inst_voltage_sensor * ps->voltage_divider_ratio;
        sum_squares += (double)(inst_voltage_mains * inst_voltage_mains);
    }

    float mean_square = (float)(sum_squares / (double)sample_count);
    ps->rms_voltage[phase] = sqrtf(mean_square);

    /* Оновлюємо стани гістерезису після кожного розрахунку RMS */
    evaluate_phase_hysteresis(ps, phase);
}

void phase_selector_process(phase_selector_t *ps, uint32_t current_time_ms) {
    if (ps == NULL) return;

    phase_id_t best_phase = select_best_available_phase(ps);

    switch (ps->state) {
        case PHASE_STATE_INIT:
            disconnect_all_contactors(ps);
            ps->state_timer_ms = current_time_ms;
            ps->state = PHASE_STATE_MONITORING;
            break;

        case PHASE_STATE_MONITORING:
            if (ps->active_phase == PHASE_NONE) {
                if (best_phase != PHASE_NONE) {
                    ps->target_phase = best_phase;
                    ps->state_timer_ms = current_time_ms;
                    ps->state = PHASE_STATE_CONNECTING;
                } else {
                    ps->state = PHASE_STATE_FAULT;
                }
            } else {
                /* Перевірка чи активна фаза досі придатна */
                if (!ps->phase_valid[ps->active_phase]) {
                    /* Активна фаза вийшла за межі допуску - негайно розмикаємо */
                    disconnect_all_contactors(ps);
                    ps->target_phase = best_phase;
                    ps->state_timer_ms = current_time_ms;
                    ps->state = PHASE_STATE_BREAK_PAUSE;
                } else if (best_phase != ps->active_phase && best_phase == ps->config.priority_phase) {
                    /* З'явилася пріоритетна фаза (L1): ініціюємо плановий перехід */
                    disconnect_all_contactors(ps);
                    ps->target_phase = best_phase;
                    ps->state_timer_ms = current_time_ms;
                    ps->state = PHASE_STATE_BREAK_PAUSE;
                }
            }
            break;

        case PHASE_STATE_BREAK_PAUSE:
            /* Переконуємось, що всі контактори вимкнені під час затримки розмикання */
            disconnect_all_contactors(ps);

            if ((current_time_ms - ps->state_timer_ms) >= ps->config.break_delay_ms) {
                if (ps->target_phase != PHASE_NONE && ps->phase_valid[ps->target_phase]) {
                    ps->state_timer_ms = current_time_ms;
                    ps->state = PHASE_STATE_CONNECTING;
                } else {
                    /* Цільова фаза за час паузи зіпсувалася: шукаємо нову альтернативу */
                    ps->target_phase = best_phase;
                    if (ps->target_phase == PHASE_NONE) {
                        ps->state = PHASE_STATE_FAULT;
                    }
                }
            }
            break;

        case PHASE_STATE_CONNECTING:
            /* Перевіряємо стабільність напруги цільової фази протягом часу затримки */
            if (ps->target_phase == PHASE_NONE || !ps->phase_valid[ps->target_phase]) {
                /* Цільова фаза втратила якість під час затримки */
                ps->target_phase = best_phase;
                ps->state_timer_ms = current_time_ms;
                ps->state = PHASE_STATE_BREAK_PAUSE;
                break;
            }

            if ((current_time_ms - ps->state_timer_ms) >= ps->config.connect_delay_ms) {
                connect_contactor(ps, ps->target_phase);
                ps->state = PHASE_STATE_MONITORING;
            }
            break;

        case PHASE_STATE_FAULT:
            disconnect_all_contactors(ps);
            if (best_phase != PHASE_NONE) {
                ps->target_phase = best_phase;
                ps->state_timer_ms = current_time_ms;
                ps->state = PHASE_STATE_CONNECTING;
            }
            break;

        default:
            ps->state = PHASE_STATE_INIT;
            break;
    }
}

phase_id_t phase_selector_get_active_phase(const phase_selector_t *ps) {
    return (ps != NULL) ? ps->active_phase : PHASE_NONE;
}

bool phase_selector_is_phase_valid(const phase_selector_t *ps, phase_id_t phase) {
    if (ps != NULL && phase < PHASE_COUNT) {
        return ps->phase_valid[phase];
    }
    return false;
}
