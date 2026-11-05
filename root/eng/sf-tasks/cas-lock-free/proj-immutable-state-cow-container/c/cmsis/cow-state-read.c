#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// Розмір статичного пулу буферів для потрійної буферизації
#define STATE_POOL_SIZE 3

typedef struct {
    uint32_t sample_rate_hz;
    uint16_t gain_dB;
    uint16_t filter_cutoff_hz;
    uint32_t update_sequence;
} system_state_t;

static system_state_t g_state_pool[STATE_POOL_SIZE];
// Атомарне упаковане значення: старші 32 біти — generation, молодші 32 біти — index
static _Atomic uint64_t g_current_ref = 0;

// Читання стану (Wait-Free операція)
void cow_state_read(system_state_t *out_state) {
    // Атомарне завантаження з acquire-семантикою гарантує бачення полів
    uint64_t ref_val = __atomic_load_n(&g_current_ref, __ATOMIC_ACQUIRE);
    uint32_t active_idx = (uint32_t)(ref_val & 0xFFFFFFFFULL) % STATE_POOL_SIZE;

    // Зчитування з незмінного стабільного буфера
    *out_state = g_state_pool[active_idx];
}

// Оновлення стану (Lock-Free цикл оновлення)
bool cow_state_update(const system_state_t *new_config) {
    uint64_t current_ref = __atomic_load_n(&g_current_ref, __ATOMIC_RELAXED);
    
    for (uint32_t attempt = 0; attempt < 8; ++attempt) {
        uint32_t curr_idx = (uint32_t)(current_ref & 0xFFFFFFFFULL);
        uint32_t curr_gen = (uint32_t)(current_ref >> 32);

        // Вибір наступного вільного буфера у кільцевому пулі
        uint32_t next_idx = (curr_idx + 1) % STATE_POOL_SIZE;
        
        // Запис нових даних у буфер-чернетку
        g_state_pool[next_idx] = *new_config;
        g_state_pool[next_idx].update_sequence = curr_gen + 1;

        // Формування упакованого референсу з новим поколінням
        uint64_t new_ref = ((uint64_t)(curr_gen + 1) << 32) | next_idx;

        // Спроба атомарної підміни інструкцією CAS із release-семантикою
        if (__atomic_compare_exchange_n(&g_current_ref, &current_ref, new_ref,
                                        false, __ATOMIC_RELEASE, __ATOMIC_RELAXED)) {
            return true; // Стан успішно підменено
        }
    }
    return false; // Захисний вихід при високій конкуренції
}
