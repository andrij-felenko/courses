#include "silicon_rev.h"

#include "usart_regs.h"

uint16_t silicon_device_id(void)
{
    /* Одне читання IDCODE: регістр статичний, але лежить у просторі
     * налагоджувального блока, тож звертаємося до нього як до периферії. */
    return (uint16_t)(DBGMCU->IDCODE & 0x0FFFU);
}

silicon_rev_t silicon_revision(void)
{
    const uint32_t idcode = DBGMCU->IDCODE;

    if ((idcode & 0x0FFFU) != SILICON_EXPECTED_DEV_ID) {
        /* Прошивку залили не в той чип. REV_ID тут означає ревізію
         * чужої моделі, і зіставляти її з нашим Errata Sheet не можна. */
        return SILICON_REV_UNKNOWN;
    }

    switch (idcode >> 16) {
    case (uint32_t)SILICON_REV_A:
        return SILICON_REV_A;
    case (uint32_t)SILICON_REV_B:
        return SILICON_REV_B;
    default:
        /* Ревізія, якої не було на момент написання прошивки. Errata для
         * неї ми не читали, тому поводимося з нею як з невідомою. */
        return SILICON_REV_UNKNOWN;
    }
}

bool silicon_needs_te_workaround(silicon_rev_t rev)
{
    return rev != SILICON_REV_B;
}
