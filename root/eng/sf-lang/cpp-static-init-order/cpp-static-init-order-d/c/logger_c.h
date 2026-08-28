/* logger_c.h - класичний C-аналог з глобальним дескриптором */
#ifndef LOGGER_C_H
#define LOGGER_C_H

#include <stdio.h>
#include <stdbool.h>

typedef struct {
    const char* filename;
    bool is_open;
} CLogger;

extern CLogger g_c_logger;
void c_logger_init(const char* filename);
void c_logger_log(const char* message);

#endif
