// cmd_names.c
#include "cmd.h"

#define X(code, id, name, handler)   [CMD_##id] = name,
static const char *const CMD_NAME[] = {
    CMD_TABLE(X)
};
#undef X

// Безпечний доступ: за межами таблиці або в «дірі» — читаємо NULL, не сміття.
const char *cmd_name(cmd_id_t id) {
    if ((unsigned)id >= (sizeof CMD_NAME / sizeof CMD_NAME[0]) || !CMD_NAME[id]) {
        return "UNKNOWN";
    }
    return CMD_NAME[id];
}
