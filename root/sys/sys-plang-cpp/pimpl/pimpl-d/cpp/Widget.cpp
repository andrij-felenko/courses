// Widget.cpp — закрита одиниця трансляції бібліотеки
#include "Widget.h"
#include <string>
#include <vector>
#include <iostream>
#include <openssl/ssl.h> // Важкі залежності підключаються ЛИШЕ тут!

struct Widget::Impl {
    std::string title_;
    std::vector<int> render_buffer_;
    SSL_CTX* ssl_context_{nullptr};

    void internal_layout() {
        // Внутрішня складна логіка
    }
};

Widget::Widget() : pImpl_(std::make_unique<Impl>()) {}

Widget::~Widget() = default; // Визначається тут, де тип Impl є повним!

Widget::Widget(Widget&&) noexcept = default;
Widget& Widget::operator=(Widget&&) noexcept = default;

Widget::Widget(const Widget& other) 
    : pImpl_(other.pImpl_ ? std::make_unique<Impl>(*other.pImpl_) : nullptr) {}

Widget& Widget::operator=(const Widget& other) {
    if (this != &other) {
        if (other.pImpl_) {
            pImpl_ = std::make_unique<Impl>(*other.pImpl_);
        } else {
            pImpl_.reset();
        }
    }
    return *this;
}

void Widget::set_title(std::string_view title) {
    pImpl_->title_ = title;
}

void Widget::draw() const {
    std::cout << "Rendering: " << pImpl_->title_ << '\n';
}
