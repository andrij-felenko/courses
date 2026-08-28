/* safe_logger_c.h - потокобезпечна реалізація на C через pthread_once */
#ifndef SAFE_LOGGER_C_H
#define SAFE_LOGGER_C_H

#include <stdio.h>
#include <pthread.h>

typedef struct {
    const char* prefix;
} SafeCLogger;

SafeCLogger* get_safe_c_logger(void);
void safe_c_logger_log(const char* msg);

#endif
