#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
    const char *dev_name = (argc > 1) ? argv[1] : "10040000.bus-controller";
    char path[256];
    char buffer[512];
    FILE *f;

    snprintf(path, sizeof(path), "/sys/class/devfreq/%s/cur_freq", dev_name);
    f = fopen(path, "r");
    if (!f) {
        perror("Не вдалося відкрити cur_freq");
        return 1;
    }

    if (fgets(buffer, sizeof(buffer), f)) {
        unsigned long long freq = strtoull(buffer, NULL, 10);
        printf("Пристрій: %s\nПоточна частота: %.2f МГц\n", dev_name, (double)freq / 1e6);
    }
    fclose(f);

    snprintf(path, sizeof(path), "/sys/class/devfreq/%s/trans_stat", dev_name);
    f = fopen(path, "r");
    if (f) {
        printf("\n--- Статистика переходів частот ---\n");
        while (fgets(buffer, sizeof(buffer), f)) {
            printf("%s", buffer);
        }
        fclose(f);
    }

    return 0;
}
