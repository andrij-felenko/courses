#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define CRASH_DUMP_MAGIC    0xDEADBEEFU
#define RTT_BUFFER_SIZE     512U

/* Стан випробувального завантаження образу */
typedef enum {
    BOOT_STATE_NEW_CANDIDATE = 0,
    BOOT_STATE_SELF_TESTING,
    BOOT_STATE_CONFIRMED_STABLE,
    BOOT_STATE_ROLLBACK_REQUIRED
} trial_boot_state_t;

/* Структура аварійного знімка регістрів процесора (ARM Cortex-M) */
typedef struct {
    uint32_t magic;
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r12;
    uint32_t lr;
    uint32_t pc;
    uint32_t psr;
    uint32_t cfsr;  /* Configurable Fault Status Register */
    uint32_t hfsr;  /* HardFault Status Register */
    uint32_t mmar;  /* MemManage Fault Address Register */
    uint32_t bfar;  /* BusFault Address Register */
    uint32_t checksum;
} crash_dump_record_t;

/* Енергонезалежна структура журналу випробувального старту */
typedef struct {
    uint32_t            boot_magic;
    trial_boot_state_t  state;
    uint32_t            boot_attempts_left;
    uint32_t            target_slot_index;
    uint32_t            header_crc;
} trial_boot_meta_t;

/* Кільцевий буфер RTT для неблокуючого трасування */
typedef struct {
    char     buffer[RTT_BUFFER_SIZE];
    volatile uint32_t write_idx;
    volatile uint32_t read_idx;
} rtt_channel_t;

/* Глобальний буфер у пам'яті SRAM для вичитування апаратним зондом */
static rtt_channel_t g_rtt_channel = {{0}, 0, 0};

/* Проста цілочисельна контрольна сума для захисту структури дампа */
static uint32_t calculate_dump_checksum(const crash_dump_record_t *dump) {
    const uint32_t *words = (const uint32_t *)dump;
    uint32_t sum = 0;
    for (size_t i = 0; i < (sizeof(crash_dump_record_t) / sizeof(uint32_t)) - 1U; ++i) {
        sum ^= words[i];
    }
    return sum;
}

/* Обробник винятку HardFault для запису аварійного знімка в пам'ять */
void hard_fault_capture_c(const uint32_t *stack_frame, crash_dump_record_t *out_dump) {
    /* Регістри ядра SCB */
    volatile uint32_t *cfsr_reg = (volatile uint32_t *)0xE000ED28U;
    volatile uint32_t *hfsr_reg = (volatile uint32_t *)0xE000ED2CU;
    volatile uint32_t *mmar_reg = (volatile uint32_t *)0xE000ED34U;
    volatile uint32_t *bfar_reg = (volatile uint32_t *)0xE000ED38U;

    out_dump->magic = CRASH_DUMP_MAGIC;
    out_dump->r0   = stack_frame[0];
    out_dump->r1   = stack_frame[1];
    out_dump->r2   = stack_frame[2];
    out_dump->r3   = stack_frame[3];
    out_dump->r12  = stack_frame[4];
    out_dump->lr   = stack_frame[5];
    out_dump->pc   = stack_frame[6];
    out_dump->psr  = stack_frame[7];

    out_dump->cfsr = *cfsr_reg;
    out_dump->hfsr = *hfsr_reg;
    out_dump->mmar = *mmar_reg;
    out_dump->bfar = *bfar_reg;

    out_dump->checksum = calculate_dump_checksum(out_dump);
}

/* Неблокуючий запис діагностичного повідомлення в буфер RTT */
void rtt_write_string(const char *msg) {
    if (!msg) {
        return;
    }
    while (*msg != 0) {
        uint32_t next_idx = (g_rtt_channel.write_idx + 1U) % RTT_BUFFER_SIZE;
        if (next_idx != g_rtt_channel.read_idx) {
            g_rtt_channel.buffer[g_rtt_channel.write_idx] = *msg;
            g_rtt_channel.write_idx = next_idx;
        } else {
            break; /* Буфер переповнено, пропускаємо без затримки ядра */
        }
        msg++;
    }
}

/* Ініціалізація та валідація спроб випробувального старту */
bool trial_boot_evaluate_candidate(trial_boot_meta_t *meta) {
    if (meta->state == BOOT_STATE_CONFIRMED_STABLE) {
        return true; /* Образ уже перевірено і підтверджено */
    }

    if (meta->state == BOOT_STATE_NEW_CANDIDATE) {
        meta->state = BOOT_STATE_SELF_TESTING;
        meta->boot_attempts_left = 3U; /* Надаємо 3 спроби на старт */
        return true;
    }

    if (meta->state == BOOT_STATE_SELF_TESTING) {
        if (meta->boot_attempts_left > 1U) {
            meta->boot_attempts_left--;
            return true;
        }
        /* Спроби вичерпано через перезапуски Watchdog або крахи */
        meta->state = BOOT_STATE_ROLLBACK_REQUIRED;
        return false;
    }

    return false;
}

/* Підтвердження стабільності нової прошивки після успішних тестів */
void trial_boot_confirm_success(trial_boot_meta_t *meta) {
    meta->state = BOOT_STATE_CONFIRMED_STABLE;
    meta->boot_attempts_left = 0;
    rtt_write_string("[OTA] Прошивку успішно підтверджено як стабільну.");
}
