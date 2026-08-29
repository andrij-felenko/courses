#ifndef FAULT_H
#define FAULT_H

#include <stdint.h>

/*
 * Базовий кадр, який апаратура ядра сама кладе на активний стек при вході
 * у виняток. Порядок полів заданий архітектурою, міняти не можна.
 */
typedef struct {
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r12;
    uint32_t lr;  /* адреса повернення з функції, що впала */
    uint32_t pc;  /* адреса інструкції аварії — головне число звіту */
    uint32_t psr;
} cortex_frame_t;

/* Який саме вектор спрацював; трамплін передає це третім аргументом. */
enum {
    FAULT_TAG_HARD      = 0,
    FAULT_TAG_MEMMANAGE = 1,
    FAULT_TAG_BUS       = 2,
    FAULT_TAG_USAGE     = 3
};

/*
 * Вмикає індивідуальні обробники MemManage/BusFault/UsageFault, пастки
 * ділення на нуль і невирівняного доступу, і вимикає буфер запису шини.
 * Викликати один раз на старті, до першого звертання до периферії.
 */
void fault_enable_all(void);

/* Друкує звіт про аварію: регістри кадру, HFSR/CFSR, адреси й підказку. */
void fault_report(uint32_t frame_sp, uint32_t exc_return, uint32_t tag);

#endif /* FAULT_H */
