#pragma once

#include <memory>
#include <string>
#include <string_view>

namespace modern_system {

// Непрозорий клас-адаптер для роботи із застарілим рушієм
class LegacyEngineAdapter {
public:
    LegacyEngineAdapter();
    ~LegacyEngineAdapter();

    // Заборона копіювання через небезпеку дублювання вказівників (Rule of 5)
    LegacyEngineAdapter(const LegacyEngineAdapter&) = delete;
    LegacyEngineAdapter& operator=(const LegacyEngineAdapter&) = delete;

    // Дозвіл безпечного переміщення ресурсу
    LegacyEngineAdapter(LegacyEngineAdapter&&) noexcept;
    LegacyEngineAdapter& operator=(LegacyEngineAdapter&&) noexcept;

    // Публічний API для решти кодової бази
    [[nodiscard]] bool configure(std::string_view config_path);
    [[nodiscard]] std::string execute_query(std::string_view query);

private:
    // Структура реалізації ховається у файлі .cpp (PIMPL)
    struct Impl;
    std::unique_ptr<Impl> pimpl_;
};

} // namespace modern_system
