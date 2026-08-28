/**
 * @file harness_tester.c
 * @brief Реалізація функцій матричного сканування та аналізу дефектів джгутів (C99).
 */

#include "harness_tester.h"
#include <string.h>

void harness_session_init(harness_session_t *session, uint8_t pin_count, const harness_hw_interface_t *hw)
{
    if (!session || !hw || pin_count > HARNESS_MAX_PINS) {
        return;
    }

    memset(session, 0, sizeof(harness_session_t));
    session->pin_count = pin_count;
    session->hw = *hw;
    session->max_defects = sizeof(session->defect_log) / sizeof(session->defect_log[0]);

    harness_matrix_clear(&session->ref_matrix, pin_count);
    harness_matrix_clear(&session->measured_matrix, pin_count);
}

void harness_matrix_clear(harness_matrix_t *mat, uint8_t pin_count)
{
    if (!mat) {
        return;
    }
    mat->pin_count = pin_count;
    for (uint8_t i = 0; i < HARNESS_MAX_PINS; ++i) {
        mat->rows[i] = 0ULL;
    }
}

bool harness_matrix_add_wire(harness_matrix_t *mat, uint8_t pin_a, uint8_t pin_b)
{
    if (!mat || pin_a >= mat->pin_count || pin_b >= mat->pin_count) {
        return false;
    }
    mat->rows[pin_a] |= (1ULL << pin_b);
    mat->rows[pin_b] |= (1ULL << pin_a);
    return true;
}

bool harness_scan_network(harness_session_t *session)
{
    if (!session || !session->hw.set_pin_mode_drive || !session->hw.read_pin_level) {
        return false;
    }

    const uint8_t n = session->pin_count;
    harness_matrix_clear(&session->measured_matrix, n);

    /* Усі піни переводяться в режим чутливого входу High-Z */
    for (uint8_t i = 0; i < n; ++i) {
        session->hw.set_pin_mode_sense(i);
    }

    /* Почергове сканування збудженням кожної тестової лінії */
    for (uint8_t drive_pin = 0; drive_pin < n; ++drive_pin) {
        session->hw.set_pin_mode_drive(drive_pin, true);
        session->hw.delay_us(5); /* Час стабілізації фронту напруги */

        for (uint8_t sense_pin = 0; sense_pin < n; ++sense_pin) {
            if (session->hw.read_pin_level(sense_pin)) {
                session->measured_matrix.rows[drive_pin] |= (1ULL << sense_pin);
            }
        }

        /* Повернення ведучого піна в безпечний стан High-Z */
        session->hw.set_pin_mode_sense(drive_pin);
    }

    return true;
}

bool harness_learn_golden_sample(harness_session_t *session)
{
    if (!harness_scan_network(session)) {
        return false;
    }
    memcpy(&session->ref_matrix, &session->measured_matrix, sizeof(harness_matrix_t));
    return true;
}

void harness_analyze_defects(harness_session_t *session, harness_test_summary_t *summary)
{
    if (!session || !summary) {
        return;
    }

    memset(summary, 0, sizeof(harness_test_summary_t));
    session->defect_count = 0;

    const uint8_t n = session->pin_count;
    const uint32_t t_start = session->hw.get_time_us ? session->hw.get_time_us() : 0;

    for (uint8_t i = 0; i < n; ++i) {
        for (uint8_t j = (uint8_t)(i + 1U); j < n; ++j) {
            const bool ref_conn = (session->ref_matrix.rows[i] & (1ULL << j)) != 0ULL;
            const bool meas_conn = (session->measured_matrix.rows[i] & (1ULL << j)) != 0ULL;

            if (ref_conn && !meas_conn) {
                summary->open_circuits++;
                summary->total_errors++;

                if (session->defect_count < session->max_defects) {
                    harness_defect_entry_t *entry = &session->defect_log[session->defect_count++];
                    entry->type = HARNESS_DEFECT_OPEN_CIRCUIT;
                    entry->pin_a = i;
                    entry->pin_b = j;
                    entry->glitch_duration_us = 0;
                }
            } else if (!ref_conn && meas_conn) {
                summary->short_circuits++;
                summary->total_errors++;

                if (session->defect_count < session->max_defects) {
                    harness_defect_entry_t *entry = &session->defect_log[session->defect_count++];
                    entry->type = HARNESS_DEFECT_SHORT_CIRCUIT;
                    entry->pin_a = i;
                    entry->pin_b = j;
                    entry->glitch_duration_us = 0;
                }
            }
        }
    }

    /* Аналіз на наявність переплутаних пінів (Miswired pins) */
    for (uint8_t i = 0; i < n; ++i) {
        uint8_t ref_target = 0xFF;
        uint8_t meas_target = 0xFF;

        for (uint8_t j = 0; j < n; ++j) {
            if (i != j) {
                if (session->ref_matrix.rows[i] & (1ULL << j)) {
                    ref_target = j;
                }
                if (session->measured_matrix.rows[i] & (1ULL << j)) {
                    meas_target = j;
                }
            }
        }

        if (ref_target != 0xFF && meas_target != 0xFF && ref_target != meas_target) {
            summary->miswires++;
            if (session->defect_count < session->max_defects) {
                harness_defect_entry_t *entry = &session->defect_log[session->defect_count++];
                entry->type = HARNESS_DEFECT_MISWIRED_PIN;
                entry->pin_a = i;
                entry->pin_b = meas_target;
                entry->glitch_duration_us = 0;
            }
        }
    }

    const uint32_t t_end = session->hw.get_time_us ? session->hw.get_time_us() : 0;
    summary->test_duration_us = t_end - t_start;
    summary->is_passed = (summary->total_errors == 0);
}

uint32_t harness_monitor_vibration_glitches(harness_session_t *session, uint32_t duration_ms)
{
    if (!session || !session->hw.get_time_us || !session->hw.read_pin_level) {
        return 0;
    }

    const uint8_t n = session->pin_count;
    const uint32_t start_us = session->hw.get_time_us();
    const uint32_t limit_us = duration_ms * 1000U;
    uint32_t glitches_found = 0;

    for (uint8_t i = 0; i < n; ++i) {
        session->hw.set_pin_mode_sense(i);
    }

    while ((session->hw.get_time_us() - start_us) < limit_us) {
        for (uint8_t i = 0; i < n; ++i) {
            session->hw.set_pin_mode_drive(i, true);
            session->hw.delay_us(2);

            for (uint8_t j = 0; j < n; ++j) {
                if (i != j && (session->ref_matrix.rows[i] & (1ULL << j))) {
                    if (!session->hw.read_pin_level(j)) {
                        const uint32_t g_start = session->hw.get_time_us();
                        while (!session->hw.read_pin_level(j) && (session->hw.get_time_us() - g_start < 5000U)) {
                            /* Очікування відновлення провідності */
                        }
                        const uint32_t g_dur = session->hw.get_time_us() - g_start;

                        if (session->defect_count < session->max_defects) {
                            harness_defect_entry_t *entry = &session->defect_log[session->defect_count++];
                            entry->type = HARNESS_DEFECT_INTERMITTENT_GLITCH;
                            entry->pin_a = i;
                            entry->pin_b = j;
                            entry->glitch_duration_us = (g_dur > 0) ? g_dur : 1U;
                        }
                        glitches_found++;
                    }
                }
            }
            session->hw.set_pin_mode_sense(i);
        }
    }

    return glitches_found;
}
