/* rtc_wakeup.h — джерело пробудження за часом: RTC Wakeup Timer на LSE.
 * Роздільність 1/2048 с, стеля одного інтервалу — 32 секунди. */
#ifndef RTC_WAKEUP_H
#define RTC_WAKEUP_H

#include <stdint.h>
#include <stdbool.h>

#define RTC_WAKEUP_MAX_MS 31999u

void     rtc_wakeup_init(void);

/* Програмує таймер і повертає ФАКТИЧНИЙ інтервал: більше за стелю не буває,
 * тож довгий простій розбивається на кілька заходів у сон. */
uint32_t rtc_wakeup_arm(uint32_t ms);

void     rtc_wakeup_disarm(void);

/* Скільки минуло від моменту програмування — рахується по календарю RTC,
 * бо сам лічильник WUT назовні не читається. */
uint32_t rtc_wakeup_elapsed_ms(void);

bool     rtc_wakeup_expired(void);

#endif /* RTC_WAKEUP_H */
