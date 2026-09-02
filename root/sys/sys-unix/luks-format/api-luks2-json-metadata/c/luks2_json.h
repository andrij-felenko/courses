/* Перевірка текстових метаданих LUKS2: схема словників, перехресні посилання
 * та перекриття дискових областей. Розбір — libjson-c, тією ж бібліотекою
 * користується сама libcryptsetup.
 */
#ifndef LUKS2_JSON_H
#define LUKS2_JSON_H

#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

struct luks2_json_report {
    int errors;     /* через них ядро віддає -EINVAL і том не відкриється */
    int warnings;   /* підозріле, але формально дозволене */
};

/* Друкує підсумок графа у out, перевіряє інваріанти й повертає кількість помилок. */
int luks2_json_check(const char *json, size_t len, uint64_t hdr_size,
                     FILE *out, struct luks2_json_report *rep);

#endif /* LUKS2_JSON_H */
