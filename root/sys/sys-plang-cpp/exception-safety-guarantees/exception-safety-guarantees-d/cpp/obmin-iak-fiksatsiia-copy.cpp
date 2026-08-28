class Widget {
    std::unique_ptr<Impl>    impl_;
    std::vector<std::string> log_;
public:
    Widget(const Widget& other)
        : impl_(std::make_unique<Impl>(*other.impl_)), log_(other.log_) {}

    void swap(Widget& other) noexcept {
        impl_.swap(other.impl_);
        log_.swap(other.log_);
    }

    Widget& operator=(Widget other) {   // копію будують ДО входу сюди
        swap(other);
        return *this;
    }
};
