// plugin.cpp — Ідіоматична C++ реалізація плагіна з extern "C"
#include <iostream>
#include <string_view>

namespace {
    // Глобальний об'єкт: конструктор викликається при dlopen, деструктор — при dlclose
    struct PluginInitializer {
        PluginInitializer() {
            std::cout << "[Plugin C++] Ініціалізація модуля (RAII Init)...\n";
        }
        ~PluginInitializer() {
            std::cout << "[Plugin C++] Завершення роботи модуля (RAII Cleanup)...\n";
        }
    };

    PluginInitializer g_init;
}

extern "C" void plugin_process(const char* input) {
    std::cout << "[Plugin C++] Обробка вхідних даних: " << input << '\n';
}
