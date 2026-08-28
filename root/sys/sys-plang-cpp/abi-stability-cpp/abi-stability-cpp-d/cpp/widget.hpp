// widget.hpp — стабільний заголовок клієнта
#pragma once
#include <memory>

class Widget {
public:
    Widget();
    ~Widget(); // Обов'язково неінлайновий деструктор!

    Widget(Widget&&) noexcept;
    Widget& operator=(Widget&&) noexcept;

    void draw();

private:
    struct Impl;                  // Неповний тип (Forward declaration)
    std::unique_ptr<Impl> pimpl_; // Фіксований розмір: 8 байтів назавжди
};
