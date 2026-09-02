#pragma once

#include <cstdint>
#include <expected>
#include <memory>

#include "sensor/i2c_bus.hpp"

namespace sensor {

/* Реалізація оголошена, але не визначена: заголовки мікросхеми лишаються
   в одному .cpp і не течуть у модулі застосунку навіть транзитивно. */
namespace detail {
class AdapterImpl;
}

/*
 * Адаптер над вендорським SDK.
 *
 * Реалізація схована за вказівником навмисно: вендорський дескриптор із
 * колбеками лежить у ній, тож заголовки мікросхеми не потрапляють у
 * жоден модуль застосунку — навіть транзитивно через цей файл.
 */
class SensorAdapter {
public:
    /* Єдиний спосіб побудови. Чип не відгукнувся — об'єкта не існує взагалі,
       а не існує в «недоініціалізованому» стані, який треба перевіряти. */
    static std::expected<SensorAdapter, SensorStatus> create(II2cBus& bus,
                                                             std::uint8_t i2c_addr);

    /* Деструктор кладе чип у сон; визначений у .cpp, бо Impl тут неповний. */
    ~SensorAdapter();

    /* Дескриптор SDK зберігає адресу реалізації. Копія отримала б чужий
       intf_ptr, який показує на можливо вже знищений об'єкт. */
    SensorAdapter(const SensorAdapter&) = delete;
    SensorAdapter& operator=(const SensorAdapter&) = delete;

    /* Переміщення безпечне: рухається лише вказівник, сама реалізація
       лишається за тією ж адресою, на яку показує intf_ptr. */
    SensorAdapter(SensorAdapter&&) noexcept;
    SensorAdapter& operator=(SensorAdapter&&) noexcept;

    /* Одне вимірювання на вимогу. */
    std::expected<EnvironmentReading, SensorStatus> read();

private:
    explicit SensorAdapter(std::unique_ptr<detail::AdapterImpl> impl) noexcept;

    std::unique_ptr<detail::AdapterImpl> impl_;
};

}  // namespace sensor
