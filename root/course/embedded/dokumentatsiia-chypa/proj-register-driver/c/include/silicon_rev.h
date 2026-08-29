/* Ревізія кремнію: що саме лежить на столі й які помилки в ньому лишилися.
 *
 * Errata Sheet прив'язує кожен апаратний дефект до ревізії. Прошивка, яка
 * прошивається в партію з різних ревізій (а так буває завжди, щойно виріб
 * пішов у серію), мусить питати про ревізію сам чип, а не покладатися на
 * те, що написали на корпусі.
 */
#ifndef SILICON_REV_H
#define SILICON_REV_H

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    SILICON_REV_UNKNOWN = 0x0000, /* IDCODE не збігся з очікуваним чипом */
    SILICON_REV_A       = 0x1000, /* Rev A — з дефектом TE, див. Errata  */
    SILICON_REV_B       = 0x2000  /* Rev B — дефект усунено в кремнії    */
} silicon_rev_t;

/* Модель чипа, під яку писана прошивка (DEV_ID у DBGMCU_IDCODE) */
#define SILICON_EXPECTED_DEV_ID 0x467U

/* Модель чипа з DBGMCU_IDCODE, біти [11:0] */
uint16_t silicon_device_id(void);

/* Ревізія кремнію з DBGMCU_IDCODE, біти [31:16].
 * Якщо DEV_ID не той, повертає SILICON_REV_UNKNOWN: значення REV_ID
 * чужого чипа нічого не означає й читати його як своє не можна. */
silicon_rev_t silicon_revision(void);

/* Чи потрібен обхід дефекту «перший стартовий біт після TE».
 *
 * Для невідомого кремнію відповідь «так»: обхід коштує одну транзакцію
 * читання на шині, а його відсутність — зіпсований перший байт кожної
 * сесії. У сумнівах платимо тактом, а не байтом. */
bool silicon_needs_te_workaround(silicon_rev_t rev);

#endif /* SILICON_REV_H */
