#include <stdint.h>
#include <string.h>

// Один запис журналу: короткий ключ + значення. У кінець дописуємо ТІЛЬКИ такі.
typedef struct {
    char    key[8];      // ім'я налаштування, напр. "volume"
    int32_t value;       // його значення
} Record;

#define CAP 256
static Record log[CAP];  // сам журнал (тут — у RAM; насправді був би Flash)
static int    count = 0; // скільки записів уже дописано (фронт запису)

// ЗАПИС = завжди в кінець. Старі записи про той самий ключ НЕ чіпаємо.
int log_put(const char *key, int32_t value) {
    if (count >= CAP) return -1;         // журнал повний → час ущільнювати
    strncpy(log[count].key, key, sizeof(log[count].key));
    log[count].value = value;
    count++;                             // фронт зсунувся на одну позицію вперед
    return 0;
}

// ЧИТАННЯ = знайти НАЙНОВІШИЙ запис із цим ключем: скануємо з КІНЦЯ назад.
int log_get(const char *key, int32_t *out) {
    for (int i = count - 1; i >= 0; i--) {   // від останнього до першого
        if (strncmp(log[i].key, key, sizeof(log[i].key)) == 0) {
            *out = log[i].value;             // перший знайдений з кінця — чинний
            return 0;
        }
    }
    return -1;                               // ключа взагалі немає
}
