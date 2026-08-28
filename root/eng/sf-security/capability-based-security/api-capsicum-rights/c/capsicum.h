#include <sys/capsicum.h>
#include <stdbool.h>

/* Ініціалізація структури списком прав; список завершується 0 */
cap_rights_t *cap_rights_init(cap_rights_t *rights, ...);

/* Обмеження прав дескриптора fd вказаною маскою */
int cap_rights_limit(int fd, const cap_rights_t *rights);

/* Отримання поточної маски прав дескриптора */
int cap_rights_get(int fd, cap_rights_t *rights);

/* Перевірка, чи маска big містить усі права маски little */
bool cap_rights_contains(const cap_rights_t *big, const cap_rights_t *little);
