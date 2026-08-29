/* main.c — прикладна програма, яка доводить, що середовище розгорнуте.

   Кожна змінна тут перевіряє свій крок стартового коду:
   g_boot_pattern лежить у .data — її значення могло взятися лише з Flash;
   g_zero_probe лежить у .bss — ненульовий байт означає, що занулення не
   відпрацювало; g_ctor_witness заповнює функція з .init_array. */

#include <stdint.h>
#include <stdlib.h>

#include "cortex_m.h"

/* .data: ініціалізоване значення, скопійоване з Flash у RAM. */
volatile uint32_t g_boot_pattern = 0xA5A5A5A5U;

/* .bss: місце, яке стартовий код мусив занулити. */
volatile uint8_t g_zero_probe[64];

/* Заповнюється обходом .init_array — тим самим механізмом, яким на C++
   виконуються конструктори глобальних об'єктів. */
volatile uint32_t g_ctor_witness;

__attribute__((constructor))
static void witness_ctor(void)
{
    g_ctor_witness = 0x00C0FFEEU;
}

/* Ознаки для налагоджувача. Під GDB достатньо `set var g_trigger_fault = 1`,
   щоб побачити роботу діагностичного обробника на живому збої. */
volatile int g_trigger_fault;
volatile uint32_t g_checks_failed;
volatile uint32_t g_heap_block_size;

/* Перевіряє все, що зробив стартовий код, і рахує невдачі. */
static uint32_t verify_environment(void)
{
    uint32_t failed = 0U;

    if (g_boot_pattern != 0xA5A5A5A5U) {
        failed |= 1U << 0;   /* .data не скопійовано з Flash */
    }

    for (unsigned i = 0; i < sizeof(g_zero_probe); ++i) {
        if (g_zero_probe[i] != 0U) {
            failed |= 1U << 1;   /* .bss не занулено */
            break;
        }
    }

    if (g_ctor_witness != 0x00C0FFEEU) {
        failed |= 1U << 2;   /* .init_array не пройдено */
    }

    if ((CM_REG32(SCB_CPACR) & SCB_CPACR_CP10_CP11_FULL) !=
        SCB_CPACR_CP10_CP11_FULL) {
        failed |= 1U << 3;   /* FPU лишився вимкненим */
    }

    /* Купа: якщо _sbrk працює, malloc віддасть блок, а free поверне його.
       Розмір беремо помітний, але явно менший за _Min_Heap_Size. */
    void *block = malloc(256);
    if (block == NULL) {
        failed |= 1U << 4;
    } else {
        g_heap_block_size = 256U;
        free(block);
    }

    return failed;
}

/* Ділення на нуль. Дільник volatile, інакше компілятор порахував би все на
   етапі збирання й ніякого винятку в прошивці не сталося б. */
static void divide_by_zero(void)
{
    volatile int divisor = 0;
    volatile int result = 1 / divisor;
    (void)result;
}

int main(void)
{
    g_checks_failed = verify_environment();

    /* Перша ж інструкція з рухомою комою перевіряє FPU не за регістром, а по
       ділу: при вимкненому CP10 тут був би UsageFault з ознакою NOCP. */
    volatile float x = 1.0f;
    x /= 3.0f;

    for (;;) {
        if (g_trigger_fault) {
            g_trigger_fault = 0;
            divide_by_zero();
        }
        cm_wfi();
    }
}
