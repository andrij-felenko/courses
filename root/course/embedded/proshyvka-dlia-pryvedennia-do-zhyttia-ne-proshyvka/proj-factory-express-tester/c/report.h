#ifndef FCT_REPORT_H
#define FCT_REPORT_H

#include <stdbool.h>
#include <stdint.h>

#include "fct.h"

/* Звіт складається в один статичний буфер і йде оператору конвеєра
 * через службовий порт одним рядком JSON. */

void report_begin(void);
void report_add(const char *name, const fct_verdict_t *v, uint32_t duration_us);
void report_finish(bool overall_pass, uint32_t total_us);

#endif /* FCT_REPORT_H */
