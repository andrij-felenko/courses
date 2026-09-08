#ifndef CRASH_HANDLER_H
#define CRASH_HANDLER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define CORE_DUMP_MAGIC       0x434F5245  /* "CORE" */
#define CORE_DUMP_VERSION     1
#define STACK_DUMP_SIZE_WORDS 128

/* Збережений контекст регістрів процесора (архітектура ARM Cortex-M / схожа модель) */
typedef struct {
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r12;
    uint32_t lr;  /* Link Register */
    uint32_t pc;  /* Program Counter (адреса збою) */
    uint32_t psr; /* Program Status Register */
} cpu_context_t;

/* Заголовок та образ аварійного дампа у пам'яті */
typedef struct {
    uint32_t magic;
    uint32_t version;
    uint32_t crc32;
    uint32_t fault_address;
    char task_name[16];
    cpu_context_t cpu;
    uint32_t stack_len;
    uint32_t stack_words[STACK_DUMP_SIZE_WORDS];
} core_dump_data_t;

void crash_handler_init(void);
void crash_record_fatal(const char *task_name, const cpu_context_t *ctx, const uint32_t *stack_ptr);
bool crash_dump_is_valid(void);
const core_dump_data_t *crash_dump_get(void);
void crash_dump_clear(void);

#endif /* CRASH_HANDLER_H */
