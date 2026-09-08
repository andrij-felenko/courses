#include <stdio.h>
#include <stdint.h>
#include "crash_handler.h"

/* Обробник пакетів, що містить штучну помилку розіменування */
void trigger_null_dereference_bug(const uint8_t *packet, size_t len) {
    volatile uint32_t *bad_ptr = NULL;

    printf("[TASK] Обробка пакета (довжина: %zu байтів)...\n", len);
    if (len == 0) {
        printf("[TASK] Помилка: нульова довжина! Провокуємо збій розіменування NULL.\n");
        cpu_context_t simulated_ctx = {
            .r0 = (uint32_t)(uintptr_t)packet,
            .r1 = (uint32_t)len,
            .lr = 0x08001040,
            .pc = 0x080012BC,
            .psr = 0x01000000
        };
        uint32_t simulated_stack[STACK_DUMP_SIZE_WORDS] = {0x080012BC, 0x08001040, 0x20000420};
        crash_record_fatal("worker_task", &simulated_ctx, simulated_stack);
        *bad_ptr = 0xDEADBEEF; /* Апаратний HardFault якщо рестарт не стався */
    }
}

void worker_task(void *pvParameters) {
    (void)pvParameters;
    uint8_t dummy_data[4] = {0x01, 0x02, 0x03, 0x04};
    trigger_null_dereference_bug(dummy_data, 4);

    /* Тепер передаємо нульову довжину для провокації збою */
    trigger_null_dereference_bug(NULL, 0);
}

int main(void) {
    printf("=== Система стартувала ===\n");

    /* Перевіряємо, чи було попереднє перезавантаження спричинене збоєм */
    if (crash_dump_is_valid()) {
        const core_dump_data_t *dump = crash_dump_get();
        printf("[ДІАГНОСТИКА] Знайдено валідний core dump від попереднього збою!\n");
        printf("  Задача:       %s\n", dump->task_name);
        printf("  Адреса (PC):  0x%08X\n", dump->fault_address);
        printf("  Повернення LR:0x%08X\n", dump->cpu.lr);
        printf("  Контрольна сума CRC32: 0x%08X (OK)\n", dump->crc32);
        printf("[ДІАГНОСТИКА] Образ готовий для експорту в GDB через UART або збереження на Flash.\n");
        crash_dump_clear();
    } else {
        printf("[СТАРТ] Чистий запуск без збережених аварійних знімків.\n");
    }

    crash_handler_init();
    printf("[FreeRTOS] Створення задачі worker_task...\n");
    worker_task(NULL);

    return 0;
}
