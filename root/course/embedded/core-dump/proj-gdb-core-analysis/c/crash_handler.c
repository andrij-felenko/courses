#include "crash_handler.h"
#include <string.h>

/* Виділений буфер аварійного дампа у спеціальній секції RAM, що не затирається при рестарті (noinit) */
#if defined(__GNUC__)
__attribute__((section(".noinit")))
#endif
static core_dump_data_t s_crash_dump;

/* Простий підрахунок CRC32 без виділення динамічної пам'яті в купі */
static uint32_t calculate_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (int j = 0; j < 8; ++j) {
            if (crc & 1) {
                crc = (crc >> 1) ^ 0xEDB88320;
            } else {
                crc = crc >> 1;
            }
        }
    }
    return ~crc;
}

void crash_handler_init(void) {
    /* Реєстрація або перевірка існуючого аварійного стану */
}

void crash_record_fatal(const char *task_name, const cpu_context_t *ctx, const uint32_t *stack_ptr) {
    /* Зупиняємо переривання — планувальник більше не працює */
    __asm volatile ("" : : : "memory");

    s_crash_dump.magic = CORE_DUMP_MAGIC;
    s_crash_dump.version = CORE_DUMP_VERSION;
    s_crash_dump.fault_address = ctx ? ctx->pc : 0;

    if (task_name) {
        strncpy(s_crash_dump.task_name, task_name, sizeof(s_crash_dump.task_name) - 1);
        s_crash_dump.task_name[sizeof(s_crash_dump.task_name) - 1] = '\0';
    } else {
        strcpy(s_crash_dump.task_name, "unknown");
    }

    if (ctx) {
        s_crash_dump.cpu = *ctx;
    }

    /* Копіюємо верхівку стека аварійної задачі для подальшого розмотування backtrace */
    s_crash_dump.stack_len = STACK_DUMP_SIZE_WORDS;
    if (stack_ptr) {
        for (size_t i = 0; i < STACK_DUMP_SIZE_WORDS; ++i) {
            s_crash_dump.stack_words[i] = stack_ptr[i];
        }
    }

    /* Обчислюємо контрольну суму після заповнення всіх полів (без поля crc32) */
    s_crash_dump.crc32 = 0;
    s_crash_dump.crc32 = calculate_crc32((const uint8_t *)&s_crash_dump, sizeof(core_dump_data_t));
}

bool crash_dump_is_valid(void) {
    if (s_crash_dump.magic != CORE_DUMP_MAGIC || s_crash_dump.version != CORE_DUMP_VERSION) {
        return false;
    }
    uint32_t stored_crc = s_crash_dump.crc32;
    s_crash_dump.crc32 = 0;
    uint32_t computed = calculate_crc32((const uint8_t *)&s_crash_dump, sizeof(core_dump_data_t));
    s_crash_dump.crc32 = stored_crc;
    return (stored_crc == computed);
}

const core_dump_data_t *crash_dump_get(void) {
    return &s_crash_dump;
}

void crash_dump_clear(void) {
    s_crash_dump.magic = 0;
    s_crash_dump.crc32 = 0;
}
