// У заголовку engine.hpp
NetworkEngine(const NetworkEngine& other);
NetworkEngine& operator=(const NetworkEngine& other);

// У файлі реалізації engine.cpp
NetworkEngine::NetworkEngine(const NetworkEngine& other)
    : impl_(other.impl_ ? std::make_unique<Impl>(*other.impl_) : nullptr) {}

NetworkEngine& NetworkEngine::operator=(const NetworkEngine& other) {
    if (this != &other) {
        if (other.impl_) {
            impl_ = std::make_unique<Impl>(*other.impl_);
        } else {
            impl_.reset();
        }
    }
    return *this;
}
