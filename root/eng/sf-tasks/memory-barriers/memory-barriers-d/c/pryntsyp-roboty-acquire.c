// Застосування Acquire-Release у коді ядра Linux (C)
#include <linux/compiler.h>

// Потік 1: Виробник (CPU Core 0)
void producer(struct my_data *payload)
{
    payload->value = 42;
    payload->status = STATUS_READY;

    // Публікація прапорця з семантикою Release
    smp_store_release(&global_ready_flag, 1);
}

// Потік 2: Споживач (CPU Core 1)
void consumer(struct my_data *payload)
{
    // Перевірка прапорця з семантикою Acquire
    if (smp_load_acquire(&global_ready_flag) == 1) {
        // Гарантовано зчитає payload->value == 42!
        pr_info("Payload value: %d\n", payload->value);
    }
}
