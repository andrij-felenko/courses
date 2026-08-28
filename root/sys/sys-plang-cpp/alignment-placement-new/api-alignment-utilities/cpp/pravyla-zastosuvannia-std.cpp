#include <new>
#include <cstdint>

struct ImmutableConfig {
    const int port;
    const char protocol;
};

void update_storage(ImmutableConfig* cfg) {
    // 1. Завершуємо час життя старого об'єкта
    cfg->~ImmutableConfig();
    
    // 2. Створюємо новий об'єкт на тому самому місці з новими const-значеннями
    ImmutableConfig* new_cfg = new (cfg) ImmutableConfig{8080, 'U'};
    
    // ПРЯМЕ використання старого cfg->port — це UB, бо компілятор пам'ятає старий const int
    // Правильний доступ:
    ImmutableConfig* valid_ptr = std::launder(cfg);
    // Тепер valid_ptr->port гарантовано поверне 8080
}
