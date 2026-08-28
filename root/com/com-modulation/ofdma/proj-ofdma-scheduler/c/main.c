#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

#define NUM_USERS 4
#define NUM_RBS 25
#define NUM_SLOTS 1000
#define EWMA_WINDOW 200.0f

typedef struct {
    int id;
    char name[32];
    float channel_snr_base;      /* Середній SNR користувача (дБ) */
    float fade_frequency_param;  /* Параметр частотного завмирання */
    float avg_throughput;        /* Накопичена середня швидкість (біт/слот) */
    unsigned long total_bits;    /* Сумарно передано бітів */
    int rbs_allocated_total;     /* Сумарно виділено RB */
} User;

/* Розрахунок досяжної швидкості на одному RB за формулою Шеннона з урахуванням MCS */
static float calculate_rb_capacity_bits(float snr_db) {
    float snr_linear = powf(10.0f, snr_db / 10.0f);
    /* 1 RB = 12 піднесних * 14 символів = 168 елементів.
       Корисні дані ~ 140 RE (з урахуванням RS пілотів) */
    float spectral_efficiency = log2f(1.0f + snr_linear);
    /* Обмеження реальною MCS: QPSK 1/2 (1 біт/RE) до 1024-QAM 5/6 (8.3 біт/RE) */
    if (spectral_efficiency < 0.5f) return 0.0f;
    if (spectral_efficiency > 8.0f) spectral_efficiency = 8.0f;
    return spectral_efficiency * 140.0f;
}

/* Генерація частотно-вибіркового завмирання Релея на кожному RB */
static float generate_instantaneous_snr(const User *u, int rb_idx, int slot_idx) {
    float freq_phase = (float)rb_idx * u->fade_frequency_param;
    float time_phase = (float)slot_idx * 0.05f + (float)u->id;
    float fast_fading = sinf(freq_phase + time_phase) * 6.0f + 
                        cosf(freq_phase * 2.1f + time_phase * 1.7f) * 4.0f;
    return u->channel_snr_base + fast_fading;
}

int main(void) {
    User users[NUM_USERS] = {
        {0, "UE-A (Центр стільника)", 24.0f, 0.45f, 100.0f, 0, 0},
        {1, "UE-B (Середня зона)",     18.0f, 0.75f, 100.0f, 0, 0},
        {2, "UE-C (Край стільника)",   10.0f, 0.30f, 100.0f, 0, 0},
        {3, "UE-D (IoT термінал)",      6.0f, 0.90f, 100.0f, 0, 0}
    };

    printf("=== Симуляція 2D OFDMA Proportional Fair шедулера ===\n");
    printf("Кількість користувачів: %d, Ресурсних блоків (RB): %d, Слотів: %d\n\n",
           NUM_USERS, NUM_RBS, NUM_SLOTS);

    for (int slot = 0; slot < NUM_SLOTS; ++slot) {
        float slot_bits_per_user[NUM_USERS] = {0.0f};
        int slot_rbs_per_user[NUM_USERS] = {0};

        /* Для кожного ресурсного блоку шукаємо найкращого користувача за PF метрикою */
        for (int rb = 0; rb < NUM_RBS; ++rb) {
            int best_user_idx = -1;
            float best_pf_metric = -1.0f;
            float best_rate_bits = 0.0f;

            for (int u = 0; u < NUM_USERS; ++u) {
                float snr = generate_instantaneous_snr(&users[u], rb, slot);
                float achievable_rate = calculate_rb_capacity_bits(snr);
                
                /* Метрика Proportional Fair: R_ij / T_i */
                float pf_metric = achievable_rate / users[u].avg_throughput;

                if (pf_metric > best_pf_metric) {
                    best_pf_metric = pf_metric;
                    best_user_idx = u;
                    best_rate_bits = achievable_rate;
                }
            }

            if (best_user_idx >= 0) {
                slot_bits_per_user[best_user_idx] += best_rate_bits;
                slot_rbs_per_user[best_user_idx]++;
            }
        }

        /* Оновлення середньої швидкості EWMA та сумарної статистики */
        for (int u = 0; u < NUM_USERS; ++u) {
            users[u].total_bits += (unsigned long)slot_bits_per_user[u];
            users[u].rbs_allocated_total += slot_rbs_per_user[u];

            users[u].avg_throughput = (1.0f - (1.0f / EWMA_WINDOW)) * users[u].avg_throughput +
                                      (1.0f / EWMA_WINDOW) * slot_bits_per_user[u];
        }
    }

    /* Підсумковий звіт */
    unsigned long total_system_bits = 0;
    printf("%-26s | %-12s | %-12s | %-12s\n", "Користувач", "Виділено RB", "Всього Мбіт", "Швидкість (Мбіт/с)");
    printf("-------------------------------------------------------------------------\n");

    for (int u = 0; u < NUM_USERS; ++u) {
        float mbits = (float)users[u].total_bits / 1000000.0f;
        float mbps = (float)users[u].total_bits / ((float)NUM_SLOTS * 0.001f * 1000000.0f);
        total_system_bits += users[u].total_bits;

        printf("%-26s | %10d RB | %10.2f Мб | %10.2f Мбіт/с\n",
               users[u].name, users[u].rbs_allocated_total, mbits, mbps);
    }

    float system_mbps = (float)total_system_bits / ((float)NUM_SLOTS * 0.001f * 1000000.0f);
    printf("-------------------------------------------------------------------------\n");
    printf("Сумарна пропускна здатність 20 МГц сектору OFDMA PF: %.2f Мбіт/с\n", system_mbps);

    return 0;
}
