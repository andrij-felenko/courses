#include <gpiod.hpp>
#include <iostream>
#include <exception>

int main()
{
    try {
        // Відкриття чипа (RAII: автоматичне закриття у деструкторі)
        ::gpiod::chip chip("/dev/gpiochip1");

        // Налаштування для кнопки (Input, Pull-Up, 15 мс Debounce)
        ::gpiod::line_settings button_settings;
        button_settings.set_direction(::gpiod::line::direction::INPUT);
        button_settings.set_bias(::gpiod::line::bias::PULL_UP);
        button_settings.set_debounce_period(std::chrono::milliseconds(15));

        // Налаштування для світлодіода (Output, Inactive)
        ::gpiod::line_settings led_settings;
        led_settings.set_direction(::gpiod::line::direction::OUTPUT);
        led_settings.set_output_value(::gpiod::line::value::INACTIVE);

        // Конфігурація ліній
        ::gpiod::line_config line_cfg;
        line_cfg.add_line_settings(::gpiod::line::offset(12), button_settings);
        line_cfg.add_line_settings(::gpiod::line::offset(16), led_settings);

        ::gpiod::request_config req_cfg;
        req_cfg.set_consumer("button_led_cpp_app");

        // Виконання запиту (RAII handle)
        auto request = chip.request_lines(req_cfg, line_cfg);

        // Читання кнопки
        auto btn_val = request.get_value(::gpiod::line::offset(12));
        std::cout << "Стан кнопки (офсет 12): "
                  << (btn_val == ::gpiod::line::value::ACTIVE ? "НАТИСНУТО" : "ВІДПУЩЕНО")
                  << std::endl;

        // Перемикання світлодіода у логічний ACTIVE
        request.set_value(::gpiod::line::offset(16), ::gpiod::line::value::ACTIVE);

        // Запит та відкриті чипи звільняються автоматично при виході з скоупу
    }
    catch (const std::exception& e) {
        std::cerr << "Критична помилка GPIO: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
