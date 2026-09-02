/* Правило зіставлення дня: поля «день місяця» (DOM) і «день тижня» (DOW)
   зв'язані не звичайним «І», а окремим правилом POSIX.1 та Vixie cron. */
#ifndef MINICRON_DAYMATCH_H
#define MINICRON_DAYMATCH_H

#include <stdbool.h>
#include <stdint.h>
#include <time.h>

/* Прапорці ФОРМИ полів — чи починається поле із зірочки. Саме форма, а не
   вміст маски, вирішує, за яким правилом зіставляти день. */
#define CRON_DOM_STAR 0x01u
#define CRON_DOW_STAR 0x02u

/* dom_mask — біти 1..31 (номер дня місяця), dow_mask — біти 0..6 (неділя == 0,
   сімку розбирач зводить до нуля ще на етапі побудови маски). */
bool cron_day_matches(uint32_t dom_mask, uint8_t dow_mask, unsigned flags,
                      const struct tm *tm_now);

/* Назва чинного правила — для діагностики й пояснень у журналі. */
const char *cron_day_rule_name(unsigned flags);

#endif /* MINICRON_DAYMATCH_H */
