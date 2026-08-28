#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>

// 1. Schema-on-write: Пряме читання за зміщенням O(1)
typedef struct {
    uint32_t user_id;
    double balance;
    uint32_t created_at;
} account_record_t;

double read_balance_write(const account_record_t *rec) {
    return rec->balance; // 1 інструкція процесора
}

// 2. Schema-on-read: Текстовий парсинг рядка O(N)
double read_balance_read(const char *json_like_str) {
    const char *key = "\"balance\":";
    const char *pos = strstr(json_like_str, key);
    if (!pos) return 0.0;
    pos += strlen(key);
    return strtod(pos, NULL); // Лексичний розбір десяткового дробу
}
