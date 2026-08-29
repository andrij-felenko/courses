#ifndef AT_CONFIG_H
#define AT_CONFIG_H

#include <stdint.h>

/* Розмір кільцевого буфера ОБОВ'ЯЗКОВО ступінь двійки: тоді загортання
   індексу — це одна побітова операція І, а не ділення за модулем. */
#define AT_RX_BUFFER_SIZE           512U
#define AT_RX_MASK                  (AT_RX_BUFFER_SIZE - 1U)

/* Стеля довжини одного рядка. Довший рядок вважається сміттям і викидається:
   без цієї стелі потік без '\r\n' зупинив би парсер назавжди. */
#define AT_MAX_LINE_SIZE            128U

#define AT_MAX_CMD_SIZE             96U
#define AT_MAX_PREFIX_SIZE          24U
#define AT_QUEUE_CAPACITY           8U
#define AT_MAX_URC_HANDLERS         8U

/* Неблокуюча витримка перед повторним надсиланням команди. */
#define AT_RETRY_DELAY_MS           100U

/* Символ запрошення на сирі дані (AT+QISEND, AT+CMGS). */
#define AT_PROMPT_CHAR              '>'

/* Скільки таймаутів поспіль ми терпимо, перш ніж вважати модуль завислим. */
#define AT_TIMEOUT_ESCALATION_LIMIT 3U

_Static_assert((AT_RX_BUFFER_SIZE & AT_RX_MASK) == 0U,
               "AT_RX_BUFFER_SIZE має бути ступенем двійки");
_Static_assert(AT_RX_BUFFER_SIZE <= 0x8000U,
               "індекси кільцевого буфера 16-бітові");
_Static_assert(AT_MAX_CMD_SIZE < AT_MAX_LINE_SIZE,
               "луна команди мусить уміщатися в рядок, інакше її не звірити");

#endif /* AT_CONFIG_H */
