// C-версія: зміна структури ламає зсуви у бінарнику
#include <stdint.h>

typedef struct {
    uint32_t id;
    uint32_t flags; // Вставка зміщує name з offset 4 на offset 8
    char name[64];
} UserRecord;

void process_user(const UserRecord* user);
