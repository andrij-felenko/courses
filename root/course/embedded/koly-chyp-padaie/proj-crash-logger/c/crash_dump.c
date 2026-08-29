#include "crash_dump.h"

#include <stddef.h>
#include <string.h>

#include "stm32f4xx.h"

#define CRASH_MAGIC 0xDEADBEEFu
#define COUNTER_KEY 0xC0FFEE01u

// Обидві змінні лежать у .noinit (NOLOAD) — стартовий код їх не обнуляє, тож
// вміст переживає NVIC_SystemReset() і скидання по сторожовому таймеру.
__attribute__((section(".noinit"))) static crash_dump_t g_dump;
__attribute__((section(".noinit"))) static uint32_t g_counter;
__attribute__((section(".noinit"))) static uint32_t g_counter_key;

static uint32_t crc32(const uint8_t *data, uint32_t length)
{
    uint32_t crc = 0xFFFFFFFFu;
    for (uint32_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc & 1u) ? ((crc >> 1) ^ 0xEDB88320u) : (crc >> 1);
        }
    }
    return ~crc;
}

// Рахуємо все, крім самого поля crc, — тому воно й стоїть останнім у структурі.
static uint32_t dump_crc(const crash_dump_t *d)
{
    return crc32((const uint8_t *)d, (uint32_t)offsetof(crash_dump_t, crc));
}

uint32_t crash_dump_bump_counter(void)
{
    if (g_counter_key != COUNTER_KEY) {
        // Перший старт після подачі живлення: у RAM випадкове сміття.
        g_counter_key = COUNTER_KEY;
        g_counter = 0u;
    }
    g_counter += 1u;
    return g_counter;
}

void crash_dump_store(const cortex_frame_t *frame,
                      uint32_t exc_return,
                      fpu_frame_state_t fpu_state,
                      const uint32_t *fpu_block)
{
    // Пишемо поля напряму в .noinit, без проміжної копії на стеку: якщо аварія
    // сталася через переповнення стека, зайвих 120 байтів там просто немає.
    memset(&g_dump, 0, sizeof(g_dump));

    g_dump.magic = CRASH_MAGIC;
    g_dump.crash_count = crash_dump_bump_counter();
    g_dump.exc_return = exc_return;
    g_dump.fpu_state = (uint32_t)fpu_state;

    // Причину винятку кадр не містить — вона живе в регістрах стану ядра.
    g_dump.hfsr = SCB->HFSR;
    g_dump.cfsr = SCB->CFSR;
    g_dump.mmfar = SCB->MMFAR;
    g_dump.bfar = SCB->BFAR;
    g_dump.shcsr = SCB->SHCSR;

    // Обидва регістри — write-1-to-clear. Не погасивши їх, наступного разу
    // побачимо суміш старих і нових бітів і будемо шукати неіснуючу помилку.
    SCB->HFSR = g_dump.hfsr;
    SCB->CFSR = g_dump.cfsr;

    if (frame != NULL) {
        g_dump.frame = *frame;
    }

    if (fpu_state == FPU_FRAME_SAVED && fpu_block != NULL) {
        for (int i = 0; i < 16; ++i) {
            g_dump.s[i] = fpu_block[i];
        }
        g_dump.fpscr = fpu_block[16];
    }

    g_dump.crc = dump_crc(&g_dump);
}

bool crash_dump_take(crash_dump_t *out)
{
    if (g_dump.magic != CRASH_MAGIC) {
        return false;
    }
    if (dump_crc(&g_dump) != g_dump.crc) {
        // Сигнатура є, а CRC ні: RAM устигла зіпсуватися. Такий дамп друкувати
        // не можна — числа в ньому брехливі.
        g_dump.magic = 0u;
        return false;
    }

    *out = g_dump;
    g_dump.magic = 0u;
    return true;
}

uint32_t crash_dump_consecutive(void)
{
    return (g_counter_key == COUNTER_KEY) ? g_counter : 0u;
}

void crash_dump_clear_counter(void)
{
    g_counter_key = COUNTER_KEY;
    g_counter = 0u;
}
