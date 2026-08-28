#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define ADC_SAMPLE_RATE_HZ     8000
#define MAINS_FREQ_HZ          50
#define SAMPLES_PER_CYCLE      (ADC_SAMPLE_RATE_HZ / MAINS_FREQ_HZ) /* 160 відліків */
#define QUADRATURE_DELAY       (SAMPLES_PER_CYCLE / 4)             /* 40 відліків для 90° */
#define NVM_SECTOR_SLOTS       8
#define NVM_MAGIC_WORD         0x5A4D
#define ANTI_CREEP_POWER_MW    200   /* 0.2 Вт поріг чутливості */

/* Квадранти площини потужності за стандартом IEC 62053 */
typedef enum {
    QUADRANT_NONE = 0,
    QUADRANT_1_IMP_IND = 1, /* +P, +Q: Споживання активної, індуктивна реактивна */
    QUADRANT_2_EXP_IND = 2, /* -P, +Q: Генерація активної, індуктивна реактивна  */
    QUADRANT_3_EXP_CAP = 3, /* -P, -Q: Генерація активної, ємнісна реактивна     */
    QUADRANT_4_IMP_CAP = 4  /* +P, -Q: Споживання активної, ємнісна реактивна    */
} energy_quadrant_t;

/* 64-бітні накопичувачі енергії лічильника (в мікроджоулях та ват-годинах) */
typedef struct {
    uint64_t act_import_uj;   /* Активна імпорт (+P), мкДж */
    uint64_t act_export_uj;   /* Активна експорт (-P), мкДж */
    uint64_t react_ind_uj;    /* Реактивна індуктивна (+Q), мквар·с (мкДж) */
    uint64_t react_cap_uj;    /* Реактивна ємнісна (-Q), мквар·с (мкДж) */

    uint32_t act_import_wh;   /* Ват-години цілі імпорт */
    uint32_t act_export_wh;   /* Ват-години цілі експорт */
    uint32_t react_ind_varh;  /* Вар-години цілі індуктивні */
    uint32_t react_cap_varh;  /* Вар-години цілі ємнісні */
} energy_accumulators_t;

/* Слот енергонезалежного запису у Flash/EEPROM */
typedef struct {
    uint16_t magic;           /* NVM_MAGIC_WORD */
    uint16_t reserved;
    uint32_t seq_id;          /* Монотонний лічильник транзакцій */
    uint32_t act_import_wh;
    uint32_t act_export_wh;
    uint32_t react_ind_varh;
    uint32_t react_cap_varh;
    uint16_t crc16;
} nvm_slot_t;

/* Стан обчислювального конвеєра лічильника */
typedef struct {
    int32_t v_delay_buf[QUADRATURE_DELAY];
    uint32_t delay_idx;

    int64_t sum_v_sq;
    int64_t sum_i_sq;
    int64_t sum_p_inst;
    int64_t sum_q_inst;
    uint32_t sample_count;

    int32_t v_rms_mv;
    int32_t i_rms_ma;
    int32_t p_active_mw;
    int32_t q_reactive_mvar;
    energy_quadrant_t cur_quadrant;

    energy_accumulators_t accumulators;
    uint32_t nvm_last_saved_seq;
    nvm_slot_t flash_storage[NVM_SECTOR_SLOTS];
} energy_meter_engine_t;

/* Розрахунок CRC16-CCITT */
static uint16_t calc_crc16(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (int b = 0; b < 8; ++b) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

/* Ініціалізація ядра вимірювання */
void energy_meter_init(energy_meter_engine_t *eng) {
    for (size_t i = 0; i < QUADRATURE_DELAY; ++i) {
        eng->v_delay_buf[i] = 0;
    }
    eng->delay_idx = 0;
    eng->sum_v_sq = 0;
    eng->sum_i_sq = 0;
    eng->sum_p_inst = 0;
    eng->sum_q_inst = 0;
    eng->sample_count = 0;
    eng->v_rms_mv = 0;
    eng->i_rms_ma = 0;
    eng->p_active_mw = 0;
    eng->q_reactive_mvar = 0;
    eng->cur_quadrant = QUADRANT_NONE;
    eng->nvm_last_saved_seq = 0;

    /* Скидання акумуляторів */
    eng->accumulators.act_import_uj = 0;
    eng->accumulators.act_export_uj = 0;
    eng->accumulators.react_ind_uj = 0;
    eng->accumulators.react_cap_uj = 0;
    eng->accumulators.act_import_wh = 0;
    eng->accumulators.act_export_wh = 0;
    eng->accumulators.react_ind_varh = 0;
    eng->accumulators.react_cap_varh = 0;

    /* Пошук останнього дійсного запису у Flash */
    uint32_t max_seq = 0;
    int best_slot = -1;
    for (int s = 0; s < NVM_SECTOR_SLOTS; ++s) {
        nvm_slot_t *slot = &eng->flash_storage[s];
        if (slot->magic == NVM_MAGIC_WORD) {
            uint16_t c = calc_crc16((const uint8_t *)slot, offsetof(nvm_slot_t, crc16));
            if (c == slot->crc16 && slot->seq_id > max_seq) {
                max_seq = slot->seq_id;
                best_slot = s;
            }
        }
    }

    if (best_slot >= 0) {
        nvm_slot_t *v = &eng->flash_storage[best_slot];
        eng->accumulators.act_import_wh = v->act_import_wh;
        eng->accumulators.act_export_wh = v->act_export_wh;
        eng->accumulators.react_ind_varh = v->react_ind_varh;
        eng->accumulators.react_cap_varh = v->react_cap_varh;
        eng->nvm_last_saved_seq = v->seq_id;
    }
}

/* Збереження поточного стану енергії у наступний слот NVM */
bool energy_meter_save_nvm(energy_meter_engine_t *eng) {
    uint32_t next_seq = eng->nvm_last_saved_seq + 1;
    uint32_t slot_idx = next_seq % NVM_SECTOR_SLOTS;
    nvm_slot_t *slot = &eng->flash_storage[slot_idx];

    slot->magic = NVM_MAGIC_WORD;
    slot->reserved = 0;
    slot->seq_id = next_seq;
    slot->act_import_wh = eng->accumulators.act_import_wh;
    slot->act_export_wh = eng->accumulators.act_export_wh;
    slot->react_ind_varh = eng->accumulators.react_ind_varh;
    slot->react_cap_varh = eng->accumulators.react_cap_varh;
    slot->crc16 = calc_crc16((const uint8_t *)slot, offsetof(nvm_slot_t, crc16));

    eng->nvm_last_saved_seq = next_seq;
    return true;
}

/* Обробка одного відліку АЦП (викликається з частотою 8 кГц) */
void energy_meter_process_sample(energy_meter_engine_t *eng, int32_t v_mv, int32_t i_ma) {
    /* 1. Квадратурна лінія затримки 90° для напруги */
    int32_t v_delayed = eng->v_delay_buf[eng->delay_idx];
    eng->v_delay_buf[eng->delay_idx] = v_mv;
    eng->delay_idx = (eng->delay_idx + 1) % QUADRATURE_DELAY;

    /* 2. Миттєві добутки (у мікроватах: мВ * мА = мкВт) */
    int64_t p_inst = (int64_t)v_mv * i_ma;
    int64_t q_inst = (int64_t)v_delayed * i_ma;

    eng->sum_v_sq += (int64_t)v_mv * v_mv;
    eng->sum_i_sq += (int64_t)i_ma * i_ma;
    eng->sum_p_inst += p_inst;
    eng->sum_q_inst += q_inst;
    eng->sample_count++;

    /* 3. Оновлення мікроджоульних акумуляторів кожні 125 мкс (1 Вт*с = 10^6 мкДж) */
    /* Елементарний квант енергії dE = P_inst * dt = (p_inst мкВт) / (8000 Гц) = мкДж / 8 */
    int64_t de_p_uj = p_inst / ADC_SAMPLE_RATE_HZ;
    int64_t de_q_uj = q_inst / ADC_SAMPLE_RATE_HZ;

    /* Anti-creep фільтр: не накопичуємо, якщо активна потужність нижче порогу */
    if (p_inst > (int64_t)ANTI_CREEP_POWER_MW * 1000) {
        eng->accumulators.act_import_uj += (uint64_t)de_p_uj;
    } else if (p_inst < -((int64_t)ANTI_CREEP_POWER_MW * 1000)) {
        eng->accumulators.act_export_uj += (uint64_t)(-de_p_uj);
    }

    if (q_inst > (int64_t)ANTI_CREEP_POWER_MW * 1000) {
        eng->accumulators.react_ind_uj += (uint64_t)de_q_uj;
    } else if (q_inst < -((int64_t)ANTI_CREEP_POWER_MW * 1000)) {
        eng->accumulators.react_cap_uj += (uint64_t)(-de_q_uj);
    }

    /* Перенесення 1 Вт·год = 3.6 * 10^9 мкДж у цілі лічильники */
    const uint64_t UJ_PER_WH = 3600000000ULL;
    if (eng->accumulators.act_import_uj >= UJ_PER_WH) {
        eng->accumulators.act_import_wh += (uint32_t)(eng->accumulators.act_import_uj / UJ_PER_WH);
        eng->accumulators.act_import_uj %= UJ_PER_WH;
    }
    if (eng->accumulators.act_export_uj >= UJ_PER_WH) {
        eng->accumulators.act_export_wh += (uint32_t)(eng->accumulators.act_export_uj / UJ_PER_WH);
        eng->accumulators.act_export_uj %= UJ_PER_WH;
    }
    if (eng->accumulators.react_ind_uj >= UJ_PER_WH) {
        eng->accumulators.react_ind_varh += (uint32_t)(eng->accumulators.react_ind_uj / UJ_PER_WH);
        eng->accumulators.react_ind_uj %= UJ_PER_WH;
    }
    if (eng->accumulators.react_cap_uj >= UJ_PER_WH) {
        eng->accumulators.react_cap_varh += (uint32_t)(eng->accumulators.react_cap_uj / UJ_PER_WH);
        eng->accumulators.react_cap_uj %= UJ_PER_WH;
    }

    /* 4. Завершення періоду мережі (160 відліків = 20 мс) */
    if (eng->sample_count >= SAMPLES_PER_CYCLE) {
        eng->p_active_mw = (int32_t)(eng->sum_p_inst / (int64_t)eng->sample_count / 1000);
        eng->q_reactive_mvar = (int32_t)(eng->sum_q_inst / (int64_t)eng->sample_count / 1000);

        /* Визначення квадранта */
        if (eng->p_active_mw >= 0 && eng->q_reactive_mvar >= 0) {
            eng->cur_quadrant = QUADRANT_1_IMP_IND;
        } else if (eng->p_active_mw < 0 && eng->q_reactive_mvar >= 0) {
            eng->cur_quadrant = QUADRANT_2_EXP_IND;
        } else if (eng->p_active_mw < 0 && eng->q_reactive_mvar < 0) {
            eng->cur_quadrant = QUADRANT_3_EXP_CAP;
        } else {
            eng->cur_quadrant = QUADRANT_4_IMP_CAP;
        }

        /* Скидання періодичних сум */
        eng->sum_v_sq = 0;
        eng->sum_i_sq = 0;
        eng->sum_p_inst = 0;
        eng->sum_q_inst = 0;
        eng->sample_count = 0;
    }
}
