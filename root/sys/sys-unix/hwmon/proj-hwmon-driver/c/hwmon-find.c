/* hwmon-find.c — знайти пристрій hwmon за вмістом name і прочитати temp1_input.
   Складання: cc -O2 -Wall -Wextra -o hwmon-find hwmon-find.c
   Запуск:    ./hwmon-find minisens */
#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int slurp(const char *path, char *buf, size_t n)
{
        FILE *f = fopen(path, "r");
        int ok;

        if (!f)
                return -1;
        ok = fgets(buf, (int)n, f) ? 0 : -1;
        fclose(f);
        if (ok == 0)
                buf[strcspn(buf, "\n")] = '\0';
        return ok;
}

int main(int argc, char **argv)
{
        const char *want = argc > 1 ? argv[1] : "minisens";
        char path[512], buf[64];
        struct dirent *e;
        DIR *d = opendir("/sys/class/hwmon");

        if (!d)
                return 1;

        while ((e = readdir(d))) {
                if (strncmp(e->d_name, "hwmon", 5))
                        continue;
                snprintf(path, sizeof(path), "/sys/class/hwmon/%s/name", e->d_name);
                if (slurp(path, buf, sizeof(buf)) || strcmp(buf, want))
                        continue;
                snprintf(path, sizeof(path), "/sys/class/hwmon/%s/temp1_input",
                         e->d_name);
                if (slurp(path, buf, sizeof(buf)))
                        continue;
                printf("%s: %.3f °C\n", e->d_name, atoi(buf) / 1000.0);
                closedir(d);
                return 0;
        }
        closedir(d);
        fprintf(stderr, "пристрій «%s» не знайдено\n", want);
        return 1;
}
