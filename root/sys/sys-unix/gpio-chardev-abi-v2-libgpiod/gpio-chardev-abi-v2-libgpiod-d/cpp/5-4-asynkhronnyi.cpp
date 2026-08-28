#include <gpiod.hpp>
#include <iostream>
#include <chrono>

int main()
{
    try {
        ::gpiod::chip chip("/dev/gpiochip1");

        ::gpiod::line_settings settings;
        settings.set_direction(::gpiod::line::direction::INPUT);
        settings.set_edge_detection(::gpiod::line::edge::BOTH);

        ::gpiod::line_config line_cfg;
        line_cfg.add_line_settings(::gpiod::line::offset(7), settings);

        ::gpiod::request_config req_cfg;
        req_cfg.set_consumer("async_cpp_gpio_monitor");

        auto request = chip.request_lines(req_cfg, line_cfg);

        std::cout << "Очікування фронтів сигналів на офсеті 7 (C++)..." << std::endl;

        // Блокуюче очікування події з таймаутом 5 секунд
        bool has_event = request.wait_edge_events(std::chrono::seconds(5));

        if (has_event) {
            ::gpiod::edge_event_buffer buffer(1);
            int count = request.read_edge_events(buffer);
            if (count > 0) {
                const auto& event = buffer.get_event(0);
                std::cout << "Отримано фронт C++: "
                          << (event.type() == ::gpiod::edge_event::event_type::RISING_EDGE ? "RISING" : "FALLING")
                          << ", Timestamp: " << event.timestamp_ns() << " нс"
                          << std::endl;
            }
        }
    }
    catch (const std::exception& e) {
        std::cerr << "Помилка очікування події: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
