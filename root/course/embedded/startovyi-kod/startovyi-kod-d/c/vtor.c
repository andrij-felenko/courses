#include "mcu_regs.h"
#include "startup.h"

/* Перенесення таблиці векторів. Завантажувач лишає основній прошивці
   зсув у Flash, а RTOS часом тримає таблицю в RAM, щоб міняти обробники
   на льоту. Помилку повертаємо значенням: винятків тут іще немає. */
bool startup_relocate_vectors(const void *table_base)
{
    const uintptr_t base = (uintptr_t)table_base;

    /* VTOR просто ігнорує молодші біти адреси: незарівняна таблиця не
       дасть помилки — вона мовчки поїде на кілька сотень байтів нижче,
       і перше ж переривання піде за випадковою адресою. */
    if ((base & (VECTOR_TABLE_ALIGN - 1U)) != 0U) {
        return false;
    }

    SCB_VTOR = (uint32_t)base;

    /* dsb — дочекатися, поки запис дійде до шини; isb — перезапустити
       конвеєр, щоб наступне переривання читало вже нову таблицю. */
    __asm volatile("dsb 0xF" ::: "memory");
    __asm volatile("isb 0xF" ::: "memory");

    return SCB_VTOR == (uint32_t)base;
}
