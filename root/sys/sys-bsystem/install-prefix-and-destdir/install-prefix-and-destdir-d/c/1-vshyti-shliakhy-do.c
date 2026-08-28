#include <stdio.h>
#include <libintl.h>
#include <locale.h>

#ifndef APP_DATADIR
#define APP_DATADIR "/usr/local/share/myapp"
#endif

#ifndef APP_LOCALEDIR
#define APP_LOCALEDIR "/usr/local/share/locale"
#endif

void init_resources(void) {
    setlocale(LC_ALL, "");
    bindtextdomain("myapp", APP_LOCALEDIR);
    textdomain("myapp");

    char config_path[512];
    snprintf(config_path, sizeof(config_path), "%s/config.default.json", APP_DATADIR);
    
    FILE* f = fopen(config_path, "r");
    if (!f) {
        perror("Не вдалося відкрити базову конфігурацію");
    } else {
        fclose(f);
    }
}
