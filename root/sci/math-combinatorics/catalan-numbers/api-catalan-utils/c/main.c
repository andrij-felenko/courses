// main.c — Демонстрація процедурного C API
#include <stdio.h>
#include <stdlib.h>
#include "catalan_utils.h"

int main(void) {
    uint64_t val;
    catalan_status_t st = catalan_compute(10, &val);
    if (st == CATALAN_SUCCESS) {
        printf("Успіх: C_10 = %llu\n", (unsigned long long)val); // 16796
    } else {
        printf("Помилка обчислення: код %d\n", st);
    }

    const char* valid_seq = "((()()))";
    if (dyck_validate(valid_seq, 8)) {
        printf("Рядок %s є валідним шляхом Дюка.\n", valid_seq);
    }

    const char* invalid_seq = "())(";
    if (!dyck_validate(invalid_seq, 4)) {
        printf("Рядок %s некоректний (баланс від'ємний).\n", invalid_seq);
    }

    return 0;
}
