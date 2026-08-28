#include <iostream>
#include <filesystem>
#include <fstream>
#include <libintl.h>
#include <locale.h>

#ifndef APP_DATADIR
#define APP_DATADIR "/usr/local/share/myapp"
#endif

#ifndef APP_LOCALEDIR
#define APP_LOCALEDIR "/usr/local/share/locale"
#endif

void init_resources() {
    namespace fs = std::filesystem;

    std::setlocale(LC_ALL, "");
    bindtextdomain("myapp", APP_LOCALEDIR);
    textdomain("myapp");

    const fs::path config_path = fs::path(APP_DATADIR) / "config.default.json";
    
    std::ifstream file(config_path);
    if (!file.is_open()) {
        std::cerr << "Не вдалося відкрити базову конфігурацію за шляхом: " 
                  << config_path << '\n';
    }
}
