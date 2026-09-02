#include "daymatch.h"

/* Зірочка не обмежує нічого: диз'юнкція з нею завжди давала б істину, і
   розклад «0 3 15 * *» спрацьовував би щодня. Тому правило обирається за
   формою полів:

     DOM або DOW записані зірочкою  →  кон'юнкція  (обидва обмеження разом)
     обидва поля задані явно        →  диз'юнкція  (досить одного збігу)

   Пастка «31 лютого» сюди не потрапляє сама собою: у лютому просто не буває
   дня з tm_mday == 31, тож біт 31 ніколи не перевіряється. */
bool cron_day_matches(uint32_t dom_mask, uint8_t dow_mask, unsigned flags,
                      const struct tm *tm_now)
{
    const int mday = tm_now->tm_mday;
    const int wday = tm_now->tm_wday;

    /* Календар від localtime_r() завжди в цих межах, але структуру нам міг
       підсунути й тест — краще відмовити, ніж зсунути маску за край. */
    if (mday < 1 || mday > 31 || wday < 0 || wday > 6) {
        return false;
    }

    const bool dom_hit = ((dom_mask >> mday) & 1u) != 0u;
    const bool dow_hit = ((dow_mask >> wday) & 1u) != 0u;

    if ((flags & (CRON_DOM_STAR | CRON_DOW_STAR)) != 0u) {
        return dom_hit && dow_hit;
    }
    return dom_hit || dow_hit;
}

const char *cron_day_rule_name(unsigned flags)
{
    if ((flags & (CRON_DOM_STAR | CRON_DOW_STAR)) != 0u) {
        return "кон'юнкція (DOM І DOW)";
    }
    return "диз'юнкція (DOM АБО DOW)";
}
