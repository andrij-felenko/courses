// cmd.h — похідні форми, усі згенеровані з cmd_table.h.
#ifndef CMD_H
#define CMD_H

#include "cmd_table.h"

// X бере поля (code, id) і будує рядок enum: CMD_##id = code,
#define X(code, id, name, handler)   CMD_##id = code,
typedef enum {
    CMD_TABLE(X)              // ← розгортається у весь перелік
} cmd_id_t;
#undef X                      // прибираємо X, щоб далі визначити інакше

#endif // CMD_H
