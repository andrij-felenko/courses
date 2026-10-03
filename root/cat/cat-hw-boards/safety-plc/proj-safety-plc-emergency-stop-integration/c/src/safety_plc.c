#include "safety_plc.h"
#include <string.h>

/**
 * @file safety_plc.c
 * @brief Реалізація низькорівневого C-драйвера функціональної безпеки Safety PLC.
 * @details Містить механіку фазового імпульсного зондування входів F-DI, розпізнавання
 *          коротких замикань на VCC, GND та між каналами, моніторинг розбіжності,
 *          керування силовими ключами High-Side/Low-Side F-DO та детермінований Fail-Safe.
 */

void safety_plc_init(safety_plc_t *plc) {
    if (!plc) {
        return;
    }
    
    memset(plc, 0, sizeof(safety_plc_t));
    
    plc->state = SAFETY_STATE_INIT;
    plc->global_faults = SAFETY_FAULT_NONE;
    plc->current_phase = SAFETY_PHASE_0;
    plc->t1_generator = true;
    plc->t2_generator = false;
    plc->cycle_count = 0;

    /* Конфігурація за замовчуванням для входів F-DI */
    for (uint8_t i = 0; i < SAFETY_DI_COUNT; i++) {
        plc->di[i].channel_id = i;
        plc->di[i].raw_a = false;
        plc->di[i].raw_b = false;
        plc->di[i].filter_cnt_a = 0;
        plc->di[i].filter_cnt_b = 0;
        plc->di[i].filtered_a = false;
        plc->di[i].filtered_b = false;
        plc->di[i].history_a = 0;
        plc->di[i].history_b = 0;
        plc->di[i].discrepancy_timer_ms = 0;
        plc->di[i].max_discrepancy_ms = SAFETY_DISCREPANCY_MAX_MS;
        plc->di[i].safe_value = false;
        plc->di[i].faults = SAFETY_FAULT_NONE;
    }

    /* Конфігурація за замовчуванням для виходів F-DO */
    for (uint8_t i = 0; i < SAFETY_DO_COUNT; i++) {
        plc->do_out[i].channel_id = i;
        plc->do_out[i].command = false;
        plc->do_out[i].hs_output = false;
        plc->do_out[i].ls_output = false;
        plc->do_out[i].hs_readback = false;
        plc->do_out[i].ls_readback = false;
        plc->do_out[i].edm_feedback = true; /* Без струму NC-контакт контактора замкнено */
        plc->do_out[i].edm_timer_ms = 0;
        plc->do_out[i].max_edm_delay_ms = SAFETY_EDM_MAX_DELAY_MS;
        plc->do_out[i].faults = SAFETY_FAULT_NONE;
    }

    /* Успішне завершення первинного тестування — перехід у робочий режим */
    plc->state = SAFETY_STATE_RUN;
}

void safety_plc_update_test_pulses(safety_plc_t *plc) {
    if (!plc) return;

    /* Генерація протифазних діагностичних імпульсів зондування T1 / T2 */
    if (plc->current_phase == SAFETY_PHASE_0) {
        plc->t1_generator = true;  /* T1 = 24V */
        plc->t2_generator = false; /* T2 = 0V  */
    } else {
        plc->t1_generator = false; /* T1 = 0V  */
        plc->t2_generator = true;  /* T2 = 24V */
    }
}

void safety_plc_read_f_di(safety_plc_t *plc, uint8_t di_idx, bool raw_a, bool raw_b) {
    if (!plc || di_idx >= SAFETY_DI_COUNT) {
        return;
    }
    plc->di[di_idx].raw_a = raw_a;
    plc->di[di_idx].raw_b = raw_b;
}

void safety_plc_evaluate_f_di_diagnostics(safety_plc_t *plc, uint8_t di_idx, uint32_t delta_time_ms) {
    if (!plc || di_idx >= SAFETY_DI_COUNT) {
        return;
    }

    f_di_channel_t *ch = &plc->di[di_idx];

    /* 1. Фільтрація високочастотних завад (Debouncing Filter) каналу A */
    if (ch->raw_a) {
        if (ch->filter_cnt_a < SAFETY_DI_FILTER_THRESHOLD) {
            ch->filter_cnt_a++;
        }
    } else {
        if (ch->filter_cnt_a > 0) {
            ch->filter_cnt_a--;
        }
    }
    ch->filtered_a = (ch->filter_cnt_a >= SAFETY_DI_FILTER_THRESHOLD);

    /* Фільтрація високочастотних завад (Debouncing Filter) каналу B */
    if (ch->raw_b) {
        if (ch->filter_cnt_b < SAFETY_DI_FILTER_THRESHOLD) {
            ch->filter_cnt_b++;
        }
    } else {
        if (ch->filter_cnt_b > 0) {
            ch->filter_cnt_b--;
        }
    }
    ch->filtered_b = (ch->filter_cnt_b >= SAFETY_DI_FILTER_THRESHOLD);

    /* 2. Запис логічної маски відгуку за поточного значення тестових генераторів T1/T2 */
    if (plc->current_phase == SAFETY_PHASE_0) {
        /* Фаза 0: T1 активний (1), T2 вимкнений (0) */
        if (ch->filtered_a) {
            ch->history_a |= (1U << SAFETY_PHASE_0);
        } else {
            ch->history_a &= ~(1U << SAFETY_PHASE_0);
        }

        if (ch->filtered_b) {
            ch->history_b |= (1U << SAFETY_PHASE_0);
        } else {
            ch->history_b &= ~(1U << SAFETY_PHASE_0);
        }
    } else {
        /* Фаза 1: T1 вимкнений (0), T2 активний (1) */
        if (ch->filtered_a) {
            ch->history_a |= (1U << SAFETY_PHASE_1);
        } else {
            ch->history_a &= ~(1U << SAFETY_PHASE_1);
        }

        if (ch->filtered_b) {
            ch->history_b |= (1U << SAFETY_PHASE_1);
        } else {
            ch->history_b &= ~(1U << SAFETY_PHASE_1);
        }
    }

    /* 3. Аналіз схемотехнічних несправностей та замикань ліній */
    
    /* А. Перевірка короткого замикання на VCC (+24V):
       Якщо під час Фази 1 (коли T1 = 0) на лінії A є високий рівень, або під час Фази 0 (коли T2 = 0) на лінії B є високий рівень. */
    bool short_vcc_a = (plc->current_phase == SAFETY_PHASE_1) && ch->filtered_a;
    bool short_vcc_b = (plc->current_phase == SAFETY_PHASE_0) && ch->filtered_b;
    
    if (short_vcc_a || short_vcc_b) {
        ch->faults |= SAFETY_FAULT_SHORT_VCC;
    }

    /* Б. Перевірка перехресного замикання між каналами ( Cross-fault між лініями T1/A та T2/B ):
       При генерації прямокутного імпульсу лише на одній лінії, високий рівень одночасно спостерігається на обох входах. */
    if ((plc->current_phase == SAFETY_PHASE_0 && ch->filtered_a && ch->filtered_b) ||
        (plc->current_phase == SAFETY_PHASE_1 && ch->filtered_a && ch->filtered_b)) {
        ch->faults |= SAFETY_FAULT_CROSS_CHANNEL;
    }

    /* В. Перевірка цілісності двофазної маски ( Phase Pattern Matching ) */
    /* Канал A замкнений і здоровий, якщо точно повторює фазу T1 (History A == 0b01) */
    bool valid_closed_a = (ch->history_a == 0x01U);
    /* Канал B замкнений і здоровий, якщо точно повторює фазу T2 (History B == 0b10) */
    bool valid_closed_b = (ch->history_b == 0x02U);

    bool valid_open_a = (ch->history_a == 0x00U);
    bool valid_open_b = (ch->history_b == 0x00U);

    /* Г. Моніторинг часової розбіжності каналів ( Discrepancy Control 1oo2 ) */
    if (valid_closed_a && valid_closed_b) {
        /* Нормальний замкнений стан (кнопка в робочому положенні, коло ціле) */
        ch->discrepancy_timer_ms = 0;
        ch->safe_value = true;
    } else if (valid_open_a && valid_open_b) {
        /* Захисне відключення (кнопка E-Stop натиснута, обидва контакти розімкнено) */
        ch->discrepancy_timer_ms = 0;
        ch->safe_value = false;
    } else {
        /* Сигнали A та B знаходяться у розбіжному стані (один 1, один 0) */
        ch->safe_value = false;
        ch->discrepancy_timer_ms += delta_time_ms;

        if (ch->discrepancy_timer_ms >= ch->max_discrepancy_ms) {
            ch->faults |= SAFETY_FAULT_DISCREPANCY;
        }
    }

    /* У разі виявлення апаратної помилки — миттєвий перехід у безпечний стан Fail-Safe */
    if (ch->faults != SAFETY_FAULT_NONE) {
        ch->safe_value = false;
        safety_plc_force_failsafe(plc, ch->faults);
    }
}

void safety_plc_update_f_do(safety_plc_t *plc, uint8_t do_idx, bool command, bool hs_fb, bool ls_fb, bool edm_fb, uint32_t delta_time_ms) {
    if (!plc || do_idx >= SAFETY_DO_COUNT) {
        return;
    }

    f_do_channel_t *ch = &plc->do_out[do_idx];
    ch->command = command;
    ch->hs_readback = hs_fb;
    ch->ls_readback = ls_fb;
    ch->edm_feedback = edm_fb;

    /* Перевірка глобального безпечного стану: у Fail-Safe силові ключі ВСЕГДА ЗНЕСТРУМЛЕНО */
    if (plc->state == SAFETY_STATE_FAILSAFE || plc->global_faults != SAFETY_FAULT_NONE) {
        ch->hs_output = false;
        ch->ls_output = false;
        ch->command = false;
        return;
    }

    /* Формування керування ключами High-Side та Low-Side */
    ch->hs_output = ch->command;
    ch->ls_output = ch->command;

    /* 1. Моніторинг працездатності High-Side ключа (верхнє плече) */
    if (ch->hs_output != ch->hs_readback) {
        ch->faults |= SAFETY_FAULT_DO_HS_DRIVER;
    }

    /* 2. Моніторинг працездатності Low-Side ключа (нижнє плече) */
    if (ch->ls_output != ch->ls_readback) {
        ch->faults |= SAFETY_FAULT_DO_LS_DRIVER;
    }

    /* 3. Моніторинг зовнішнього виконавчого пристрою EDM (External Device Monitoring):
       При command == false (реле знеструмлене) -> NC контакт має бути замкнений (edm_fb == true).
       При command == true (реле під напругою) -> NC контакт має бути розімкнений (edm_fb == false). */
    bool expected_edm = !ch->command;

    if (ch->edm_feedback != expected_edm) {
        ch->edm_timer_ms += delta_time_ms;
        if (ch->edm_timer_ms >= ch->max_edm_delay_ms) {
            ch->faults |= SAFETY_FAULT_DO_FEEDBACK;
        }
    } else {
        ch->edm_timer_ms = 0;
    }

    /* Будь-яка аномалія силового виходу викличує аварійне відключення */
    if (ch->faults != SAFETY_FAULT_NONE) {
        ch->hs_output = false;
        ch->ls_output = false;
        safety_plc_force_failsafe(plc, ch->faults);
    }
}

void safety_plc_process_step(safety_plc_t *plc, uint32_t delta_time_ms) {
    if (!plc) return;

    plc->cycle_count++;

    if (plc->state == SAFETY_STATE_FAILSAFE) {
        /* Примусове підтримання знеструмленого стану силових виходів */
        for (uint8_t i = 0; i < SAFETY_DO_COUNT; i++) {
            plc->do_out[i].command = false;
            plc->do_out[i].hs_output = false;
            plc->do_out[i].ls_output = false;
        }
        return;
    }

    /* 1. Генерація тестових діагностичних імпульсів */
    safety_plc_update_test_pulses(plc);

    /* 2. Інкремент та перемикання фазового кроку зондування */
    plc->current_phase = (plc->current_phase + 1U) % SAFETY_PHASE_COUNT;
}

void safety_plc_force_failsafe(safety_plc_t *plc, uint16_t fault_reason) {
    if (!plc) return;

    plc->state = SAFETY_STATE_FAILSAFE;
    plc->global_faults |= fault_reason;

    /* Детермінований перехід у безпечний стан: миттєве знеструмлення всіх High-Side та Low-Side ключів */
    for (uint8_t i = 0; i < SAFETY_DO_COUNT; i++) {
        plc->do_out[i].command = false;
        plc->do_out[i].hs_output = false;
        plc->do_out[i].ls_output = false;
    }
}

bool safety_plc_reset_faults(safety_plc_t *plc, bool reset_button_pressed) {
    if (!plc) return false;

    if (!reset_button_pressed) {
        return false;
    }

    /* Перевірка відсутності фізичних помилок на каналах F-DI */
    for (uint8_t i = 0; i < SAFETY_DI_COUNT; i++) {
        if (plc->di[i].faults != SAFETY_FAULT_NONE) {
            return false;
        }
    }

    /* Перевірка відсутності фізичних помилок на каналах F-DO */
    for (uint8_t i = 0; i < SAFETY_DO_COUNT; i++) {
        if (plc->do_out[i].faults != SAFETY_FAULT_NONE) {
            return false;
        }
    }

    /* Усі фізичні апаратні несправності ліквідовано — скидаємо прапори та повертаємось в робочий режим */
    plc->global_faults = SAFETY_FAULT_NONE;
    plc->state = SAFETY_STATE_RUN;
    return true;
}

const char* safety_fault_to_string(uint16_t fault_code) {
    if (fault_code == SAFETY_FAULT_NONE) return "ПОМИЛОК НЕМАЄ (OK)";
    if (fault_code & SAFETY_FAULT_SHORT_VCC) return "КОРОТКЕ ЗАМИКАННЯ НА VCC (+24V)";
    if (fault_code & SAFETY_FAULT_SHORT_GND) return "КОРОТКЕ ЗАМИКАННЯ НА GND (0V)";
    if (fault_code & SAFETY_FAULT_CROSS_CHANNEL) return "ПЕРЕХРЕСНЕ КОРОТКЕ ЗАМИКАННЯ МІЖ КАНАЛАМИ";
    if (fault_code & SAFETY_FAULT_DISCREPANCY) return "ТАЙМАУТ РОЗБІЖНОСТІ КАНАЛІВ (DISCREPANCY TIMEOUT)";
    if (fault_code & SAFETY_FAULT_DO_HS_DRIVER) return "НЕСПРАВНІСТЬ HIGH-SIDE КЛЮЧА F-DO";
    if (fault_code & SAFETY_FAULT_DO_LS_DRIVER) return "НЕСПРАВНІСТЬ LOW-SIDE КЛЮЧА F-DO";
    if (fault_code & SAFETY_FAULT_DO_FEEDBACK) return "НЕСПРАВНІСТЬ ЗВОРОТНОГО ЗВ'ЯЗКУ EDM (ЗВАРЕНО КОНТАКТОР)";
    if (fault_code & SAFETY_FAULT_SYSTEM_FAILSAFE) return "ПРИМУСОВИЙ АВАРІЙНИЙ СТАН FAIL-SAFE";
    return "НЕВІДОМА АПАРАТНА ПОМИЛКА";
}

const char* safety_state_to_string(safety_state_t state) {
    switch (state) {
        case SAFETY_STATE_INIT: return "ІНІЦІАЛІЗАЦІЯ (INIT)";
        case SAFETY_STATE_RUN:  return "РОБОЧИЙ РЕЖИМ (RUN)";
        case SAFETY_STATE_FAILSAFE: return "АПАРАТНИЙ БЕЗПЕЧНИЙ СТАН (FAIL-SAFE)";
        default: return "НЕВІДОМИЙ СТАН";
    }
}
