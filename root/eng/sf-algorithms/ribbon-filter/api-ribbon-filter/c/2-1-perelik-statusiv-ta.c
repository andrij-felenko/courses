#include <stdint.h>

typedef enum {
    RIBBON_OK                      =  0,  /* Успішне завершення операції */
    RIBBON_ERR_INVALID_ARGUMENT    = -1,  /* Некоректні параметри (нульовий вказівник, M < w) */
    RIBBON_ERR_UNRESOLVABLE_SYSTEM = -2,  /* Не вдалося розв'язати систему за ліміт спроб */
    RIBBON_ERR_OUT_OF_MEMORY       = -3,  /* Помилка виділення динамічної пам'яті */
    RIBBON_ERR_BUFFER_TOO_SMALL    = -4,  /* Буфер призначення замалий для серіалізації */
    RIBBON_ERR_CORRUPTED_DATA      = -5,  /* Пошкоджено магічне число або контрольну суму */
    RIBBON_ERR_UNSUPPORTED_VERSION = -6   /* Непідтримувана версія двійкового формату */
} RibbonStatus;
