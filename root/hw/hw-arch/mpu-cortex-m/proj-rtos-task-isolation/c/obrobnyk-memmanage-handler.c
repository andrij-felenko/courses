#include "core_cm4.h"

// зручні маски молодшого байта CFSR (це і є MMFSR)
#define MMFSR_IACCVIOL   (1u << 0)   // вибірка інструкції з XN-області
#define MMFSR_DACCVIOL   (1u << 1)   // читання/запис у заборонену область
#define MMFSR_MUNSTKERR  (1u << 3)   // помилка при діставанні кадру зі стека
#define MMFSR_MSTKERR    (1u << 4)   // помилка при укладанні кадру на стек
#define MMFSR_MMARVALID  (1u << 7)   // адреса в MMFAR достовірна

// Виклик із MemManage_Handler. Тут ми в привілейованому режимі,
// тож маємо доступ до системних регістрів SCB.
void mpu_fault_report(void)
{
    uint32_t mmfsr = SCB->CFSR & 0xFFu;       // молодший байт = MMFSR
    uint32_t addr  = (mmfsr & MMFSR_MMARVALID)
                   ?  SCB->MMFAR              // адреса злочину
                   :  0xFFFFFFFFu;            // недостовірна

    // на цьому місці зазвичай: залогувати addr/mmfsr,
    // прибити ЛИШЕ винну задачу й перемкнутися на наступну,
    // а не валити всю систему — у цьому і сенс ізоляції.

    if (mmfsr & MMFSR_DACCVIOL) {
        /* дике читання/запис за addr — знайдено винну інструкцію */
    }
    if (mmfsr & MMFSR_IACCVIOL) {
        /* спроба виконати дані/стек — зіпсований вказівник повернення */
    }
    if (mmfsr & (MMFSR_MSTKERR | MMFSR_MUNSTKERR)) {
        /* збій на кадрі винятку — найпевніше переповнення стека */
    }

    // очистити біти статусу (запис одиницею скидає їх — write-1-to-clear)
    SCB->CFSR = mmfsr;

    (void)addr;
}
