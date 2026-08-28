template <typename T>
class optional_storage {
    alignas(T) std::byte data_[sizeof(T)];
    bool init_ = false;

public:
    constexpr T& value() & {
        if (!init_) throw std::bad_optional_access{};
        return *std::launder(reinterpret_cast<T*>(data_));
    }

    constexpr const T& value() const& {
        if (!init_) throw std::bad_optional_access{};
        return *std::launder(reinterpret_cast<const T*>(data_));
    }
};
