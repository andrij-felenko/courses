#define _POSIX_C_SOURCE 200809L

#include "trace.h"

#include <stdbool.h>
#include <time.h>

/* На платі це два записи в регістр порту, по кілька тактів кожен:
       GPIOB->BSRR = (1u << 7);         // фронт
       GPIOB->BSRR = (1u << (7 + 16));  // спад
   Пін навмисно смикають ДО й ПІСЛЯ всієї роботи такту, а не всередині: інакше
   виміряна ширина імпульсу перестане відповідати затримці, яку бачить мотор.
   На хості замість піна беремо монотонний годинник — той самий інтервал. */

static bool     s_armed;
static uint64_t s_rise_ns;
static uint32_t s_last_us;
static uint32_t s_worst_us;
static uint32_t s_count;

static uint64_t now_ns(void)
{
    struct timespec ts;

    if (clock_gettime(CLOCK_MONOTONIC, &ts) != 0)
        return 0;
    return (uint64_t)ts.tv_sec * 1000000000ull + (uint64_t)ts.tv_nsec;
}

void diag_pin_init(void)
{
    s_armed    = false;
    s_rise_ns  = 0;
    s_last_us  = 0;
    s_worst_us = 0;
    s_count    = 0;
}

void diag_pin_high(void)
{
    if (s_armed)
        return;      /* пін уже піднято — повторний фронт нічого не означає */
    s_rise_ns = now_ns();
    s_armed   = true;
}

void diag_pin_low(void)
{
    uint64_t delta;

    if (!s_armed)
        return;      /* спаду без фронту не буває: цього такту пілот нічого не робив */

    delta     = now_ns() - s_rise_ns;
    s_last_us = (uint32_t)((delta + 500ull) / 1000ull);
    if (s_last_us > s_worst_us)
        s_worst_us = s_last_us;
    s_count++;
    s_armed = false;
}

uint32_t diag_pulse_last_us(void)  { return s_last_us; }
uint32_t diag_pulse_worst_us(void) { return s_worst_us; }
uint32_t diag_pulse_count(void)    { return s_count; }
