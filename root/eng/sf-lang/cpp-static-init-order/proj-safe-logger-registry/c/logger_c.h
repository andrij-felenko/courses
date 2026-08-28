/* logger_c.h - інтерфейс для мови C */
#ifndef LOGGER_C_H
#define LOGGER_C_H

#include <stdio.h>
#include <stdbool.h>

typedef struct {
    const char* prefix;
    bool ready;
} CLogger;

extern CLogger g_c_logger;
void c_logger_init(const char* prefix);
void c_logger_log(const char* msg);

#endif
