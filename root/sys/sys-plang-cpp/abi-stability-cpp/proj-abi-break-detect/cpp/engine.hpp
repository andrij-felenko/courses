// engine.hpp — публічний заголовок бібліотеки з фіксованим ABI
#pragma once
#include <memory>
#include <string_view>

#if defined(_WIN32)
  #ifdef ENGINE_EXPORTS
    #define ENGINE_API __declspec(dllexport)
  #else
    #define ENGINE_API __declspec(dllimport)
  #endif
#else
  #define ENGINE_API __attribute__((visibility("default")))
#endif

namespace engine {
inline namespace v1 {

class ENGINE_API Engine {
public:
    Engine();
    ~Engine(); // Обов'язково неінлайновий деструктор!

    // Конструктори та оператори переміщення
    Engine(Engine&&) noexcept;
    Engine& operator=(Engine&&) noexcept;

    // Підтримка глибокого копіювання через фабричний метод клонування
    Engine(const Engine& other);
    Engine& operator=(const Engine& other);

    void initialize(std::string_view config_path);
    double execute_step(double delta_time);

private:
    struct EngineImpl;                 // Неповний тип (Forward declaration)
    std::unique_ptr<EngineImpl> impl_; // Фіксований розмір: рівно 8 байтів
};

} // namespace v1
} // namespace engine
