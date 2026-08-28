// nifty_logger.cpp
#include "nifty_logger.hpp"

alignas(NiftyLogger) char g_nifty_storage[sizeof(NiftyLogger)];
static int g_nifty_counter = 0;

NiftyInitializer::NiftyInitializer() {
    if (g_nifty_counter++ == 0) {
        // Перший .cpp модуль створює об'єкт через placement new
        new (g_nifty_storage) NiftyLogger();
        std::cout << "[NIFTY INIT] Системний журнал сконструйовано\n";
    }
}

NiftyInitializer::~NiftyInitializer() {
    if (--g_nifty_counter == 0) {
        // Останній .cpp модуль викликає деструктор
        reinterpret_cast<NiftyLogger*>(g_nifty_storage)->~NiftyLogger();
        std::cout << "[NIFTY DESTROY] Системний журнал коректно звільнено\n";
    }
}
