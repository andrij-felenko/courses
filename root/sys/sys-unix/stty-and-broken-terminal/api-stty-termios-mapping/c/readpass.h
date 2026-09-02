#ifndef READPASS_H
#define READPASS_H

#include <stddef.h>
#include <sys/types.h>

/* Читає рядок із термінала з вимкненим відлунням (профіль `stty -echo`)
   і повертає відлуння назад за будь-якого виходу.
   Повертає довжину рядка або -1 (errno). */
ssize_t tty_read_password(int fd, const char *prompt, char *buf, size_t size);

#endif /* READPASS_H */
