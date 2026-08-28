// database_safe.h
#ifndef DATABASE_SAFE_H
#define DATABASE_SAFE_H

typedef struct {
    int connection_id;
    int is_ready;
} Database;

Database* get_database(void);

#endif // DATABASE_SAFE_H

// database_safe.c
#include "database_safe.h"

Database* get_database(void) {
    static Database db = { .connection_id = 101, .is_ready = 1 };
    return &db;
}
