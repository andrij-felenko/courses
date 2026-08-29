#include "rcc.h"

#include "silicon_rev.h"
#include "stm32f4_regs.h"

/* Errata ES0182, «Delay after an RCC peripheral clock enabling».
 *
 * Симптом: запис у RCC_xxxENR доходить до периферійного блоку не миттєво —
 * між увімкненням тактування й появою тактів у блоці лежить кілька тактів
 * шини. Якщо наступною інструкцією ядро вже пише в регістр цього блоку,
 * запис губиться (а на читанні можна дістати BusFault).
 *
 * Офіційний обхід: після запису прочитати той самий регістр RCC назад.
 * Читання по шині AHB не завершиться, доки попередній запис не осяде, —
 * тож потрібна затримка виникає сама, без калібрування циклів.
 *
 * Питання ревізії тут перевіряється не заради економії двох тактів, а щоб
 * показати механізм: обхід прив'язаний до рядка таблиці еррати, і коли
 * виробник виправить дефект у новій ревізії, гілка згасне сама.
 */
static void enable_and_settle(volatile uint32_t *enr, uint32_t mask)
{
    *enr |= mask;

    if (silicon_affected_by(ERRATUM_RCC_CLOCK_ENABLE_DELAY)) {
        volatile uint32_t readback = *enr;
        (void)readback;
    }
}

void rcc_ahb1_enable(uint32_t mask)
{
    enable_and_settle(&RCC->AHB1ENR, mask);
}

void rcc_apb1_enable(uint32_t mask)
{
    enable_and_settle(&RCC->APB1ENR, mask);
}

void rcc_apb1_reset(uint32_t mask)
{
    /* Скидання — це імпульс, а не стан: біт треба виставити й зняти.
     * Між фронтами потрібне те саме холосте читання, інакше блок може
     * не встигнути побачити активний рівень. */
    RCC->APB1RSTR |= mask;

    volatile uint32_t readback = RCC->APB1RSTR;
    (void)readback;

    RCC->APB1RSTR &= ~mask;
}
