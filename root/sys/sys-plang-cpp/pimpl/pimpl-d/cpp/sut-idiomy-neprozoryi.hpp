// Widget.h — відкритий заголовок, доступний клієнтам
#ifndef WIDGET_H
#define WIDGET_H

#include <memory>
#include <string_view>

class Widget {
public:
    Widget();
    ~Widget(); // Обов'язково оголошений у заголовку, але НЕ визначений!

    Widget(Widget&&) noexcept;
    Widget& operator=(Widget&&) noexcept;

    // Забороняємо або окремо реалізуємо копіювання
    Widget(const Widget&);
    Widget& operator=(const Widget&);

    void set_title(std::string_view title);
    void draw() const;

private:
    struct Impl;                  // Неповний тип (Incomplete Type)
    std::unique_ptr<Impl> pImpl_; // Єдине поле з даними: фіксовані 8 байтів
};

#endif // WIDGET_H
