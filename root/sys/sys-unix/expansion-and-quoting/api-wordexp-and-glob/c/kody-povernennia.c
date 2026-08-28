#include <stdio.h>
#include <fnmatch.h>

int check_filename(const char *filename) {
    const char *pattern = "*.tar.gz";
    int flags = FNM_PATHNAME | FNM_PERIOD;

    if (fnmatch(pattern, filename, flags) == 0) {
        printf("Файл '%s' відповідає архіву tar.gz\n", filename);
        return 1;
    } else {
        printf("Файл '%s' НЕ відповідає масці\n", filename);
        return 0;
    }
}
