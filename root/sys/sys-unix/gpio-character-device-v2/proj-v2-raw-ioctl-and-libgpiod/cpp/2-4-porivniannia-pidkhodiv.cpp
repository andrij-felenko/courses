// Ідіоматичний приклад C++20 з використанням сучасного libgpiod v2 C++ API (<gpiod.hpp>)
#include <iostream>
#include <chrono>
#include <cstdlib>
#include <gpiod.hpp>

int main() {
    try {
        // Відкриття контролера
        ::gpiod::chip chip("/dev/gpiochip0");

        // Налаштування для виходу (лінія 17)
        ::gpiod::line_settings out_settings;
        out_settings.set_direction(::gpiod::line::direction::OUTPUT);
        out_settings.set_bias(::gpiod::line::bias::PULL_UP);

        // Налаштування для вхідної лінії з подійним моніторингом (лінія 27)
        ::gpiod::line_settings in_settings;
        in_settings.set_direction(::gpiod::line::direction::INPUT);
        in_settings.set_edge_detection(::gpiod::line::edge::BOTH);
        in_settings.set_debounce_period(std::chrono::microseconds(5000));

        // Формування мапи конфігурації
        ::gpiod::line_config line_cfg;
        line_cfg.add_line_settings(17, out_settings);
        line_cfg.add_line_settings(27, in_settings);

        // Конфігурація запиту
        ::gpiod::request_config req_cfg;
        req_cfg.set_consumer("libgpiod-cxx-demo");

        // Захоплення ліній (повертає об'єкт line_request із керуванням RAII)
        auto request = chip.request_lines(req_cfg, line_cfg);

        std::cout << "C++ libgpiod v2: Встановлюємо HIGH на лінію 17...\n";
        request.set_value(17, ::gpiod::line::value::ACTIVE);

        // Буфер подій
        ::gpiod::edge_event_buffer event_buf(16);

        std::cout << "C++ libgpiod v2: Очікування подій на лінії 27...\n";
        if (request.wait_edge_events(std::chrono::seconds(10))) {
            request.read_edge_events(event_buf);
            for (const auto& event : event_buf) {
                std::cout << "Отримано подію! Timestamp: " << event.timestamp_ns() << " нс, "
                          << "Тип: " << (event.type() == ::gpiod::edge_event::type::RISING_EDGE ? "RISING" : "FALLING")
                          << ", Offset: " << event.line_offset() << '\n';
            }
        } else {
            std::cout << "Таймаут очікування події.\n";
        }

    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка gpiod::exception: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }

    // Автоматичне звільнення всіх ресурсів при виході з області видимості
    return EXIT_SUCCESS;
}
