// widget.hpp — публічний інтерфейс з ідіоматичною C++ інкапсуляцією
#pragma once
#include <memory>
#include <utility>

class Widget {
public:
    Widget(int x, int y);
    ~Widget();

    Widget(Widget&&) noexcept;
    Widget& operator=(Widget&&) noexcept;

    void set_position(int x, int y) noexcept;
    [[nodiscard]] std::pair<int, int> get_position() const noexcept;

private:
    struct Impl;
    std::unique_ptr<Impl> m_impl;
};
