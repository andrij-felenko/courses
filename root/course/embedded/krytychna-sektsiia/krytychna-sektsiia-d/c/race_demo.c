/*
 * Той самий стан чіпають фон і обробник переривання, захисту немає жодного.
 * Це вихідна вада, з якої починається стаття: у C один вираз, у ядрі — три
 * інструкції, і між ними процесор може піти в обробник.
 */
#include <stdint.h>

#include "demos.h"

/* STM32F4: TIM2 за адресою 0x40000000, регістр стану — зсув 0x10. */
#define TIM2_SR (*(volatile uint32_t *)0x40000010UL)
#define TIM_SR_UIF (1U << 0)

#define FLAG_FRAME_READY (1U << 3)

volatile uint32_t g_packet_counter = 0U;
volatile uint32_t g_device_flags = 0U;
volatile uint64_t g_timestamp_us = 0U; /* 64 біти на 32-бітному ядрі */

/* Що обробник насправді побачив у часовій мітці — сюди дивиться відлагодження. */
volatile uint64_t g_isr_timestamp_seen = 0U;

/* Фоновий потік (Thread Mode). */
void process_data(void)
{
    /* Один вираз у C — три інструкції ядра: LDR / ADDS / STR. */
    g_packet_counter++;

    /* Прапорець — те саме читання-зміна-запис, лише з ORR посередині. */
    g_device_flags |= FLAG_FRAME_READY;

    /* 64-бітне число ядро пише двома інструкціями STR. Переривання між ними
     * лишає в памʼяті половину старого значення й половину нового. */
    g_timestamp_us += 50U;
}

/* Обробник переривання таймера (Handler Mode) — той самий стан. */
void TIM2_IRQHandler(void)
{
    TIM2_SR = ~TIM_SR_UIF; /* зняти прапорець оновлення */

    /* Цей інкремент фон затре своїм STR, щойно повернеться з обробника. */
    g_packet_counter++;

    /* А сюди може приїхати «гібридна» мітка: старші 32 біти нові, молодші старі. */
    g_isr_timestamp_seen = g_timestamp_us;
}
