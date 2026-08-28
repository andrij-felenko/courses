#include <stdio.h>
#include <stdlib.h>
#include "calc/math_ops.h"

#ifndef APP_DATADIR
#define APP_DATADIR "/usr/local/share/calcapp"
#endif

int main(int argc, char* argv[]) {
    char asset_path[512];
    snprintf(asset_path, sizeof(asset_path), "%s/operations.json", APP_DATADIR);

    FILE* f = fopen(asset_path, "r");
    if (!f) {
        fprintf(stderr, "Помилка: не знайдено файл конфігурації: %s\n", asset_path);
        return 1;
    }
    printf("Конфігурацію завантажено з: %s\n", asset_path);
    fclose(f);

    printf("Розрахунок: 12 + 30 = %d\n", calc_add(12, 30));
    return 0;
}
