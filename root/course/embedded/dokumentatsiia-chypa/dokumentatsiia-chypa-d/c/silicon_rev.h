/* silicon_rev.h — ревізія кремнію та матриця застосовності еррати.
 *
 * Errata Sheet побудований як таблиця «дефект × ревізія»: рядок — вада,
 * стовпці — ревізії кристала, хрестик — «ця ревізія уражена». Прошивка,
 * яка хоче обходити ваду лише там, де вада є, мусить перенести цю таблицю
 * у код і зчитати власну ревізію з DBGMCU_IDCODE.
 */
#ifndef SILICON_REV_H
#define SILICON_REV_H

#include <stdbool.h>
#include <stdint.h>

/* DEV_ID сімейства STM32F405/407/415/417 (RM0090 §38.6.1) */
#define SILICON_DEV_ID_F40X 0x413U

/* Літерні позначення ревізій з розділу «Device identification» еррати ES0182.
 * Порядок елементів довільний — важливо лише, що кожна ревізія має свій
 * номер, за яким вона стоїть у масці застосовності. */
typedef enum {
    SILICON_REV_UNKNOWN = 0,
    SILICON_REV_A,
    SILICON_REV_Z,
    SILICON_REV_1,
    SILICON_REV_2,
    SILICON_REV_Y,
    SILICON_REV_3,
    SILICON_REV_COUNT
} silicon_rev_t;

/* Дефекти, які ця прошивка вміє обходити. Кожен — рядок таблиці еррати. */
typedef enum {
    /* ES0182 «Delay after an RCC peripheral clock enabling»: перше звернення
     * до регістра щойно затактованого блоку може не пройти. */
    ERRATUM_RCC_CLOCK_ENABLE_DELAY = 0,
    /* ES0182 «I2C analog filter may provide wrong value»: кінцевий автомат
     * I2C зависає з піднятим прапорцем BUSY, лінії лишаються притиснуті. */
    ERRATUM_I2C_BUSY_LOCK,
    ERRATUM_COUNT
} erratum_t;

typedef struct {
    uint16_t      dev_id;     /* DEV_ID [11:0]  — сімейство                */
    uint16_t      rev_id;     /* REV_ID [31:16] — сира ревізія             */
    silicon_rev_t rev;        /* розпізнана літера ревізії                 */
    bool          recognised; /* чи це справді очікуване сімейство         */
} silicon_info_t;

/* Читає IDCODE один раз і кешує результат: під час старту функцію смикають
 * з кількох модулів, а звернення до шини налагодження не безкоштовне. */
const silicon_info_t *silicon_info(void);

/* Назва ревізії для журналу чи налагоджувача. */
const char *silicon_rev_name(silicon_rev_t rev);

/* Головне питання до еррати: «а моя ревізія уражена?»
 * Нерозпізнаний кристал вважаємо ураженим — обхід коштує тактів,
 * пропущений обхід коштує зависання в полі. */
bool silicon_affected_by(erratum_t erratum);

/* Заголовок дефекту з еррати — щоб у журналі стояла не цифра, а посилання
 * на розділ документа, який можна відкрити й прочитати. */
const char *erratum_title(erratum_t erratum);

#endif /* SILICON_REV_H */
