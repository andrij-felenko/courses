#include <stdio.h>
#include <stdbool.h>
#include <stdatomic.h>

int main(void) {
    _Atomic long value = 10;
    long expected = 10;
    long desired = 20;

    // atomic_compare_exchange_strong приймає вказівник на expected.
    // Якщо value == expected, у value записується desired і повертається true.
    // Якщо value != expected, у expected копіюється поточне значення value і повертається false.
    bool success = atomic_compare_exchange_strong(&value, &expected, desired);

    if (success) {
        printf("CAS успішний! Нове значення value: %ld\n", atomic_load(&value));
    } else {
        printf("CAS невдалий. Значення у пам'яті: %ld, оновлено expected: %ld\n", 
               atomic_load(&value), expected);
    }

    return 0;
}
