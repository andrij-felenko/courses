#ifndef AT_PORT_H
#define AT_PORT_H

#include <stdint.h>

/* Критична секція потрібна рівно в одному місці — навколо індексів черги
   команд. Кільцевий буфер прийому її не потребує взагалі: head пише лише
   DMA, tail — лише парсер, тож переривання там не вимикаються ніколи.

   А от у чергу команду кладе прикладний код, і робить це в тому числі з
   URC-колбеку або з переривання таймера. Індекси q_head/q_count не атомарні,
   тож їх правку треба захистити. */

#if defined(__ARM_ARCH) && !defined(AT_PORT_HOST)

static inline uint32_t at_port_enter_critical(void)
{
    uint32_t primask;
    __asm volatile ("mrs %0, primask" : "=r" (primask));
    __asm volatile ("cpsid i" ::: "memory");
    return primask;
}

static inline void at_port_exit_critical(uint32_t saved)
{
    /* Відновлюємо саме попередній стан, а не вмикаємо переривання наосліп:
       інакше вкладена критична секція розкриє зовнішню. */
    if ((saved & 1U) == 0U) {
        __asm volatile ("cpsie i" ::: "memory");
    }
}

#else /* хост-збірка симулятора: планувальника немає, вимикати нічого */

static inline uint32_t at_port_enter_critical(void) { return 0U; }
static inline void at_port_exit_critical(uint32_t saved) { (void)saved; }

#endif

#endif /* AT_PORT_H */
