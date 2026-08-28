#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define NUM_MCS 5
#define TARGET_BLER 0.10f
#define STEP_UP 0.10f   /* Крок підвищення порогової поправки при ACK */
#define STEP_DOWN 0.90f /* Крок зниження порогової поправки при NACK */

typedef struct {
    const char *name;
    float snr_threshold_db; /* Поріг SNR для BLER = 10% */
    float spectral_efficiency; /* біт/с/Гц */
} mcs_config_t;

static const mcs_config_t MCS_TABLE[NUM_MCS] = {
    {"QPSK 1/2",    2.5f,  1.0f},
    {"16-QAM 1/2",  7.3f,  2.0f},
    {"16-QAM 3/4", 10.5f,  3.0f},
    {"64-QAM 2/3", 14.3f,  4.0f},
    {"256-QAM 5/6",22.5f,  6.67f}
};

typedef struct {
    int current_mcs;
    float sinr_offset_db; /* Поправка зовнішньої петлі OLRC */
    float hysteresis_db;
} amc_controller_t;

void amc_init(amc_controller_t *amc, float hysteresis_db) {
    amc->current_mcs = 0; /* Стартуємо з найбезпечнішого QPSK 1/2 */
    amc->sinr_offset_db = 0.0f;
    amc->hysteresis_db = hysteresis_db;
}

/* Оновлення зовнішньої петлі на основі підтвердження ACK/NACK */
void amc_update_olrc(amc_controller_t *amc, bool is_ack) {
    if (is_ack) {
        /* При успіху повільно піднімаємо ефективне SINR */
        amc->sinr_offset_db += STEP_UP;
    } else {
        /* При помилці швидко опускаємо SINR, щоб скинути MCS */
        amc->sinr_offset_db -= STEP_DOWN;
    }
}

/* Оновлення внутрішньої петлі та вибір нового індексу MCS */
int amc_select_mcs(amc_controller_t *amc, float measured_sinr_db) {
    /* Ефективне SINR з урахуванням поправки OLRC */
    float eff_sinr = measured_sinr_db + amc->sinr_offset_db;
    int idx = amc->current_mcs;

    /* Перевірка на підвищення MCS (вгору з урахуванням гістерезису) */
    while (idx < NUM_MCS - 1) {
        if (eff_sinr >= MCS_TABLE[idx + 1].snr_threshold_db + amc->hysteresis_db) {
            idx++;
        } else {
            break;
        }
    }

    /* Перевірка на зниження MCS (вниз із запасом) */
    while (idx > 0) {
        if (eff_sinr < MCS_TABLE[idx].snr_threshold_db - amc->hysteresis_db) {
            idx--;
        } else {
            break;
        }
    }

    amc->current_mcs = idx;
    return idx;
}

int main(void) {
    amc_controller_t amc;
    amc_init(&amc, 1.2f); /* Гістерезис 1.2 дБ */

    float channel_sinr[] = {3.0f, 4.5f, 9.0f, 12.0f, 16.0f, 24.0f, 20.0f, 8.0f, 2.0f};
    size_t num_steps = sizeof(channel_sinr) / sizeof(channel_sinr[0]);

    printf("=== Симуляція адаптації лінку (C) ===\n");
    for (size_t i = 0; i < num_steps; i++) {
        float sinr = channel_sinr[i];
        int mcs = amc_select_mcs(&amc, sinr);

        /* Симулюємо результат: якщо SINR >= порогу — ACK, інакше NACK */
        bool ack = (sinr >= MCS_TABLE[mcs].snr_threshold_db);
        amc_update_olrc(&amc, ack);

        printf("Крок %2zu: SINR = %4.1f дБ -> MCS %d [%s] (η = %.2f, ACK = %s)\n",
               i, sinr, mcs, MCS_TABLE[mcs].name,
               MCS_TABLE[mcs].spectral_efficiency, ack ? "ТАК" : "НІ");
    }

    return 0;
}
