// Widget.cpp
struct Widget::Impl {
    Widget* owner_; // Зворотний вказівник на зовнішній об'єкт
    int progress_{0};

    explicit Impl(Widget* owner) : owner_(owner) {}

    void on_network_data(int bytes) {
        progress_ += bytes;
        if (progress_ > 1000) {
            owner_->notify_ui(); // Виклик публічного методу зовнішнього класу
        }
    }
};

Widget::Widget() : pImpl_(std::make_unique<Impl>(this)) {}
